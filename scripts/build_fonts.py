"""Generate the committed WOFF2 fonts embedded by the visual explainer renderer.

The TrueType files remain the sources: the renderer reads their metrics with the
standard library, while generated documents embed the smaller WOFF2 copies.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

FONTS = (
    Path(__file__).resolve().parents[1]
    / "skills/documentation/visual-explainers/assets/fonts"
)


def compress(source: Path) -> bytes:
    """Convert one TrueType font to WOFF2 deterministically.

    Args:
        source: TrueType font file.

    Returns:
        WOFF2 bytes. The head table's modification time is preserved, so the
        same source and tool versions always produce the same output.
    """

    # Keep the source timestamp so regenerated output is byte-for-byte stable.
    font = TTFont(source, recalcTimestamp=False)
    font.flavor = "woff2"

    # Serialize the compressed font in memory.
    output = io.BytesIO()
    font.save(output)
    return output.getvalue()


def main() -> None:
    """Write the WOFF2 fonts, or report stale ones with --check."""

    # Parse the single mode flag.
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument(
        "--check",
        action="store_true",
        help="report stale or missing WOFF2 files without writing them",
    )
    check = bool(parser.parse_args().check)

    # Compare or write a generated font beside every TrueType source.
    outdated: list[str] = []
    for source in sorted(FONTS.glob("*.ttf")):
        target = source.with_suffix(".woff2")
        data = compress(source)
        if check:
            if not target.exists() or target.read_bytes() != data:
                outdated.append(target.name)
        else:
            _ = target.write_bytes(data)

    # Report the result in the same style as the JavaScript build.
    if outdated:
        print(
            "Outdated WOFF2 fonts: "
            + ", ".join(outdated)
            + ". Run `just build-fonts`.",
            file=sys.stderr,
        )
        sys.exit(1)
    print("WOFF2 fonts are up to date." if check else "Generated WOFF2 fonts.")


if __name__ == "__main__":
    main()
