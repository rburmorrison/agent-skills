"""Theme-set manifests, accent selection, and palette contrast rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

Pair = tuple[str, str]
"""Light and dark appearance values for one color token."""

MIN_CONTRAST = 4.5
"""Minimum WCAG contrast ratio for each pair in CONTRAST_PAIRS."""

CONTRAST_PAIRS = (
    ("accent", "bg"),
    ("accent", "paper"),
    ("accent", "wash"),
    ("button-ink", "accent"),
)
"""Foreground and background tokens the accent must keep legible in both appearances."""

FONT_FAMILIES = {"sans": "Explainer Sans", "mono": "Explainer Mono"}
"""CSS family names the shell uses for each manifest font role."""

_HEX = re.compile(r"#[0-9a-fA-F]{6}")
_SCRIPT = re.compile(r"[a-z][a-z0-9-]*\.js")
_APPEARANCES = ("light", "dark")


@dataclass(frozen=True, slots=True)
class FontFace:
    """One embedded font file and the license distributed with it."""

    role: str
    """Shell family role, a key of FONT_FAMILIES."""
    file: str
    """Font file name in the bundled fonts directory."""
    weight: str
    """CSS font-weight value or range the file provides."""
    license: str
    """License file name in the bundled fonts directory."""


@dataclass(frozen=True, slots=True)
class Theme:
    """A theme set's fonts, base palette, and accent presets."""

    name: str
    """Name documents use to select the set."""
    stylesheet: str
    """Stylesheet in the bundled themes directory for colors outside the paired
    tokens, such as shadows and the print palette, and set-specific styling."""
    fonts: tuple[FontFace, ...]
    """Embedded faces; the first sans face also supplies diagram text metrics."""
    script: str | None
    """Readable script in the bundled assets directory whose generated `.min.js`
    copy runs after the shell controller, or None when the set adds no behavior."""
    numbered: bool
    """Whether documents number sections, subsections, captioned tables, and figures."""
    tokens: Mapping[str, Pair]
    """Base color tokens, without the leading `--`; includes every CONTRAST_PAIRS token."""
    default_accent: str
    """Preset applied when a document selects no accent."""
    presets: Mapping[str, Mapping[str, Pair]]
    """Named accents, each a set of token overrides merged over the base tokens."""

    @property
    def metrics_font(self) -> FontFace:
        """The sans face used to measure diagram labels."""

        return next(face for face in self.fonts if face.role == "sans")


def parse_theme(name: str, data: object) -> Theme:
    """Interpret a decoded theme manifest.

    Args:
        name: Theme-set name, used in error messages.
        data: Decoded JSON manifest.

    Returns:
        The theme set the manifest declares.

    Raises:
        ValueError: A field is missing or malformed, a font role is unknown,
            the set has no sans face, a token checked by CONTRAST_PAIRS is
            missing, a preset overrides an undeclared token, or the default
            accent is not a preset.
    """

    # Read the top-level sections of the manifest.
    where = name + " theme"
    manifest = _mapping(data, where)
    accents = _mapping(manifest.get("accents"), where + " accents")
    stylesheet = _string(manifest.get("stylesheet"), where + " stylesheet")
    script = manifest.get("script")
    if script is not None and not (
        isinstance(script, str) and _SCRIPT.fullmatch(script)
    ):
        raise ValueError(where + " script must be a .js file name")
    numbered = manifest.get("numbered", False)
    if not isinstance(numbered, bool):
        raise ValueError(where + " numbered must be true or false")

    # Collect the embedded faces and require one sans face for metrics.
    fonts: list[FontFace] = []
    for index, value in enumerate(_list(manifest.get("fonts"), where + " fonts")):
        face = _mapping(value, f"{where} font {index}")
        fonts.append(
            FontFace(
                role=_string(face.get("role"), f"{where} font {index} role"),
                file=_string(face.get("file"), f"{where} font {index} file"),
                weight=_string(face.get("weight"), f"{where} font {index} weight"),
                license=_string(face.get("license"), f"{where} font {index} license"),
            )
        )
    if any(face.role not in FONT_FAMILIES for face in fonts):
        raise ValueError(where + " font roles must be " + ", ".join(FONT_FAMILIES))
    if not any(face.role == "sans" for face in fonts):
        raise ValueError(where + " needs a sans font")

    # Read the base palette, which must define every contrast-checked token.
    tokens = _tokens(manifest.get("tokens"), where + " tokens")
    missing = sorted({t for pair in CONTRAST_PAIRS for t in pair} - tokens.keys())
    if missing:
        raise ValueError(where + " tokens must include " + ", ".join(missing))

    # Read the presets, which may override only declared tokens.
    presets = {
        preset: _tokens(overrides, f"{where} accent {preset}")
        for preset, overrides in _mapping(
            accents.get("presets"), where + " accent presets"
        ).items()
    }
    if any(not overrides.keys() <= tokens.keys() for overrides in presets.values()):
        raise ValueError(where + " accent presets may override only its tokens")
    default = _string(accents.get("default"), where + " default accent")
    if default not in presets:
        raise ValueError(where + " default accent must be one of its presets")

    return Theme(
        name=name,
        stylesheet=stylesheet,
        fonts=tuple(fonts),
        script=script,
        numbered=numbered,
        tokens=tokens,
        default_accent=default,
        presets=presets,
    )


def resolve_palette(theme: Theme, accent: object = None) -> dict[str, Pair]:
    """Apply a document's accent selection to a theme's base palette.

    Args:
        theme: Selected theme set.
        accent: None for the default preset, a preset name, or a mapping with
            exactly `light` and `dark` `#rrggbb` colors for a custom accent.

    Returns:
        Every color token of the theme with the accent applied.

    Raises:
        ValueError: The accent is not a preset or a well-formed custom pair, or
            a custom pair falls below MIN_CONTRAST for a pair in CONTRAST_PAIRS.
    """

    # Select the overrides for a preset or a well-formed custom pair.
    custom = _custom_accent(accent)
    if accent is None:
        overrides = theme.presets[theme.default_accent]
    elif isinstance(accent, str) and accent in theme.presets:
        overrides = theme.presets[accent]
    elif custom is not None:
        overrides = {"accent": custom}
    else:
        raise ValueError(
            "accent must be "
            + ", ".join(theme.presets)
            + ', or {"light": "#rrggbb", "dark": "#rrggbb"}'
        )

    # Merge the overrides over the base palette.
    palette = {**theme.tokens, **overrides}

    # Reject custom colors that would leave links, numbers, or buttons illegible.
    if custom is not None and (failures := contrast_failures(palette)):
        raise ValueError("accent has too little contrast: " + "; ".join(failures))

    return palette


def contrast_failures(palette: Mapping[str, Pair]) -> list[str]:
    """Describe each CONTRAST_PAIRS check a palette fails.

    Args:
        palette: Color tokens that include every token named in CONTRAST_PAIRS.

    Returns:
        One message per failing pair and appearance, empty when all pass.
    """

    return [
        f"{fg} on {bg} in {appearance} is {ratio:.2f}:1, below {MIN_CONTRAST}:1"
        for fg, bg in CONTRAST_PAIRS
        for index, appearance in enumerate(_APPEARANCES)
        if (ratio := contrast_ratio(palette[fg][index], palette[bg][index]))
        < MIN_CONTRAST
    ]


def contrast_ratio(first: str, second: str) -> float:
    """Compute the WCAG 2 contrast ratio of two `#rrggbb` colors.

    Args:
        first: One color.
        second: The other color; order does not matter.

    Returns:
        A ratio from 1 to 21.
    """

    # Order the relative luminances so the ratio is at least one.
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)

    return (high + 0.05) / (low + 0.05)


def palette_css(palette: Mapping[str, Pair]) -> str:
    """Render color tokens and the appearance-menu swatches as CSS.

    Args:
        palette: Color tokens, including `bg`, without the leading `--`.

    Returns:
        A body rule of `light-dark()` custom properties and swatch rules.
    """

    # Declare each token for the shell's selected color scheme.
    tokens = ";".join(
        f"--{token}:light-dark({light},{dark})"
        for token, (light, dark) in palette.items()
    )

    # Paint the menu swatches from the page ground of each appearance.
    light, dark = palette["bg"]

    return (
        "body{"
        + tokens
        + "}\n"
        + f".theme-swatch-system{{background:linear-gradient(90deg,{light} 50%,{dark} 50%)}}"
        + f".theme-swatch-light{{background:{light}}}"
        + f".theme-swatch-dark{{background:{dark}}}"
    )


def _custom_accent(accent: object) -> Pair | None:
    # Accept only a mapping of exactly two hex colors named by appearance.
    if not isinstance(accent, dict):
        return None
    fields = cast("dict[object, object]", accent)
    light, dark = fields.get("light"), fields.get("dark")
    if (
        len(fields) != len(_APPEARANCES)
        or not isinstance(light, str)
        or not isinstance(dark, str)
        or not _HEX.fullmatch(light)
        or not _HEX.fullmatch(dark)
    ):
        return None

    return light.lower(), dark.lower()


def _luminance(color: str) -> float:
    # Linearize each sRGB channel before weighting it.
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    red, green, blue = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]

    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _tokens(value: object, where: str) -> dict[str, Pair]:
    # Require each token to hold one hex color per appearance.
    tokens: dict[str, Pair] = {}
    for token, pair in _mapping(value, where).items():
        colors = _list(pair, f"{where} {token}")
        if len(colors) != len(_APPEARANCES) or not all(
            isinstance(c, str) and _HEX.fullmatch(c) for c in colors
        ):
            raise ValueError(f"{where} {token} must be [light, dark] #rrggbb colors")
        tokens[token] = (cast("str", colors[0]), cast("str", colors[1]))

    return tokens


def _mapping(value: object, where: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(where + " must be an object")
    return cast("dict[str, object]", value)


def _list(value: object, where: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(where + " must be a list")
    return cast("list[object]", value)


def _string(value: object, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(where + " must be a nonempty string")
    return value
