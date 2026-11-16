"""Icon catalog consistency across bundled files and the agent reference."""

import json
import re
import unittest
from pathlib import Path
from typing import TypedDict, cast

SKILL = Path(__file__).resolve().parents[1]
ICONS = SKILL / "assets" / "icons"


class Icon(TypedDict):
    name: str
    family: str
    purpose: str
    file: str


class Catalog(TypedDict):
    grid: int
    stroke_width: float
    stroke_linecap: str
    stroke_linejoin: str
    icons: list[Icon]


def load_catalog() -> Catalog:
    return cast(
        "Catalog", json.loads((ICONS / "catalog.json").read_text(encoding="utf-8"))
    )


class IconCatalogTests(unittest.TestCase):
    def test_catalog_files_and_reference_list_the_same_icons(self) -> None:
        # Read the catalog, the bundled SVG files, and the reference's grouped entries.
        catalog = load_catalog()
        files = {path.stem for path in ICONS.glob("*.svg")}
        reference: dict[str, tuple[str, str]] = {}
        family = ""
        for line in (
            (SKILL / "references" / "icons.md").read_text(encoding="utf-8").splitlines()
        ):
            if line.startswith("## "):
                family = line[3:]
            elif match := re.fullmatch(r"- `([a-z0-9-]+)`: (.+)\.", line):
                reference[match[1]] = (family, match[2])

        # Every catalog entry names an existing file and matches its reference family and purpose.
        names = {icon["name"] for icon in catalog["icons"]}
        self.assertEqual(names, files)
        self.assertEqual(names, set(reference))
        for icon in catalog["icons"]:
            with self.subTest(icon=icon["name"]):
                self.assertEqual(icon["file"], icon["name"] + ".svg")
                self.assertEqual(
                    (icon["family"], icon["purpose"]), reference[icon["name"]]
                )

    def test_icons_share_the_catalog_drawing_conventions(self) -> None:
        # Each SVG uses the catalog's grid and stroke settings.
        catalog = load_catalog()
        grid = catalog["grid"]
        for path in sorted(ICONS.glob("*.svg")):
            with self.subTest(icon=path.stem):
                svg = path.read_text(encoding="utf-8")
                self.assertIn(f'viewBox="0 0 {grid} {grid}"', svg)
                self.assertIn(f'stroke-width="{catalog["stroke_width"]}"', svg)
                self.assertIn(f'stroke-linecap="{catalog["stroke_linecap"]}"', svg)
                self.assertIn(f'stroke-linejoin="{catalog["stroke_linejoin"]}"', svg)


if __name__ == "__main__":
    _ = unittest.main()
