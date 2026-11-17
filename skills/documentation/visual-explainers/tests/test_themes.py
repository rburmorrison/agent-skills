"""Theme-set manifests, accent presets, and contrast rules."""

import json
import sys
import unittest
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render import THEMES
from themes import (
    contrast_failures,
    contrast_ratio,
    palette_css,
    parse_theme,
    resolve_palette,
)


def manifest(**changes: object) -> dict[str, object]:
    """Build a minimal valid manifest with selected top-level fields replaced."""

    base: dict[str, object] = {
        "stylesheet": "sample.css",
        "fonts": [
            {
                "role": "sans",
                "file": "Sans.ttf",
                "weight": "400",
                "license": "sans-OFL.txt",
            }
        ],
        "tokens": {
            "bg": ["#ffffff", "#000000"],
            "paper": ["#ffffff", "#000000"],
            "wash": ["#ffffff", "#000000"],
            "accent": ["#333333", "#dddddd"],
            "button-ink": ["#ffffff", "#000000"],
        },
        "accents": {"default": "ink", "presets": {"ink": {}}},
    }
    return {**base, **changes}


class ThemeTests(unittest.TestCase):
    def test_every_bundled_preset_keeps_the_accent_legible(self) -> None:
        for name, path in THEMES.items():
            # Load each bundled set through the same parser documents use.
            data = cast("object", json.loads(path.read_text(encoding="utf-8")))
            theme = parse_theme(name, data)

            # Verify each preset against the rule applied to custom pairs.
            for preset in theme.presets:
                with self.subTest(theme=name, preset=preset):
                    self.assertEqual(
                        [], contrast_failures(resolve_palette(theme, preset))
                    )

    def test_contrast_ratio_spans_identical_to_black_on_white(self) -> None:
        self.assertAlmostEqual(21, contrast_ratio("#000000", "#ffffff"))
        self.assertAlmostEqual(21, contrast_ratio("#FFFFFF", "#000000"))
        self.assertAlmostEqual(1, contrast_ratio("#777777", "#777777"))

    def test_palette_css_declares_tokens_and_paints_swatches_from_the_ground(
        self,
    ) -> None:
        # Render a two-token palette.
        css = palette_css(
            {"bg": ("#f7f7f5", "#121417"), "accent": ("#a14a1f", "#f0a477")}
        )

        # Verify the token rule and the swatches derived from the page ground.
        self.assertIn(
            "body{--bg:light-dark(#f7f7f5,#121417);--accent:light-dark(#a14a1f,#f0a477)}",
            css,
        )
        self.assertIn(
            ".theme-swatch-system{background:linear-gradient(90deg,#f7f7f5 50%,#121417 50%)}",
            css,
        )
        self.assertIn(".theme-swatch-dark{background:#121417}", css)

    def test_malformed_manifests_are_rejected(self) -> None:
        cases: list[tuple[dict[str, object], str]] = [
            ({"fonts": []}, "needs a sans font"),
            (
                {
                    "fonts": [
                        {
                            "role": "serif",
                            "file": "Serif.ttf",
                            "weight": "400",
                            "license": "serif-OFL.txt",
                        }
                    ]
                },
                "font roles must be sans, mono",
            ),
            ({"tokens": {"bg": ["#fff", "#000000"]}}, "tokens bg must be"),
            (
                {"accents": {"default": "rust", "presets": {"ink": {}}}},
                "default accent must be one of its presets",
            ),
            ({"stylesheet": ""}, "stylesheet must be a nonempty string"),
            ({"numbered": "yes"}, "numbered must be true or false"),
            ({"script": "../core.js"}, "script must be a .js file name"),
            ({"script": "hexfield.css"}, "script must be a .js file name"),
            (
                {"tokens": {"bg": ["#ffffff", "#000000"]}},
                "tokens must include accent, button-ink, paper, wash",
            ),
            (
                {
                    "accents": {
                        "default": "ink",
                        "presets": {"ink": {"acent": ["#a14a1f", "#f0a477"]}},
                    }
                },
                "presets may override only its tokens",
            ),
        ]

        # Parse each malformed variant of an otherwise valid manifest.
        for changes, message in cases:
            with (
                self.subTest(message=message),
                self.assertRaisesRegex(ValueError, message),
            ):
                _ = parse_theme("sample", manifest(**changes))

    def test_script_is_optional_and_names_a_bundled_source(self) -> None:
        self.assertIsNone(parse_theme("sample", manifest()).script)
        self.assertEqual(
            "hexfield.js",
            parse_theme("sample", manifest(script="hexfield.js")).script,
        )

    def test_presets_override_only_the_tokens_they_name(self) -> None:
        # Add a preset that changes the accent alone.
        theme = parse_theme(
            "sample",
            manifest(
                accents={
                    "default": "ink",
                    "presets": {"ink": {}, "rust": {"accent": ["#a14a1f", "#f0a477"]}},
                }
            ),
        )

        # Resolve the default and the alternate preset.
        default = resolve_palette(theme)
        rust = resolve_palette(theme, "rust")

        # Verify that only the accent differs between them.
        self.assertEqual(("#333333", "#dddddd"), default["accent"])
        self.assertEqual(("#a14a1f", "#f0a477"), rust["accent"])
        self.assertEqual({**default, "accent": rust["accent"]}, rust)


if __name__ == "__main__":
    _ = unittest.main()
