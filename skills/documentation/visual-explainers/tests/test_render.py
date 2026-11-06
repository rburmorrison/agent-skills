"""Document output and rejection contracts across renderer variants."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Mapping, cast
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render import THEMES, Renderer, check_html, validate_chart

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class RenderTests(unittest.TestCase):
    def test_plain_theme_defaults_to_system_with_only_appearance_choices(self) -> None:
        output = Renderer({"title": "Appearance"}, FIXTURES).render()

        self.assertIn('<body data-theme="plain" data-appearance="system">', output)
        self.assertEqual(
            ["system"],
            re.findall(r'data-appearance-value="([a-z]+)" aria-checked="true"', output),
        )
        self.assertEqual(
            ["system", "light", "dark"],
            re.findall(r'data-appearance-value="([a-z]+)"', output),
        )

    def test_explicit_theme_matches_the_default_output(self) -> None:
        default = Renderer({"title": "Appearance"}, FIXTURES).render()
        explicit = Renderer(
            {"title": "Appearance", "theme": "plain"}, FIXTURES
        ).render()

        self.assertEqual(default, explicit)

    def test_output_embeds_only_the_selected_theme_set(self) -> None:
        plain_css = THEMES["plain"].read_text(encoding="utf-8")
        warm_css = "body{--bg:light-dark(#fff0ed,#211b18)}"
        with tempfile.TemporaryDirectory() as directory:
            warm = Path(directory) / "warm.css"
            _ = warm.write_text(warm_css, encoding="utf-8")
            with patch.dict(THEMES, {"warm": warm}):
                plain = Renderer({"title": "Appearance"}, FIXTURES).render()
                alternate = Renderer(
                    {"title": "Appearance", "theme": "warm"}, FIXTURES
                ).render()

        self.assertIn(plain_css, plain)
        self.assertNotIn(warm_css, plain)
        self.assertIn(warm_css, alternate)
        self.assertNotIn(plain_css, alternate)
        self.assertIn('<body data-theme="warm" data-appearance="system">', alternate)

    def test_removed_palettes_and_unknown_theme_sets_are_rejected(self) -> None:
        for theme in [
            "violet",
            "slate",
            "blue",
            "night",
            "system",
            "light",
            "dark",
            "unknown",
        ]:
            with self.subTest(theme=theme), self.assertRaisesRegex(
                ValueError, "theme must be plain"
            ):
                _ = Renderer({"title": "Appearance", "theme": theme}, FIXTURES).render()

    def test_all_block_and_chart_variants_build_one_offline_document(self) -> None:
        document = cast(
            "Mapping[str, object]",
            json.loads((FIXTURES / "all_blocks.json").read_text(encoding="utf-8")),
        )

        output = Renderer(document, FIXTURES).render()

        self.assertEqual([], check_html(output))
        self.assertEqual(8, output.count('class="chart visual"'))
        self.assertEqual(3, output.count('<figure class="visual">'))
        self.assertIn("<h1>Characterization</h1>", output)
        self.assertIn('class="tab-panel content-stack"', output)
        self.assertIn('class="timeline-item"', output)
        self.assertIn("<strong>world</strong>", output)
        self.assertIn('type="range"', output)
        self.assertIn('<select id="', output)

    def test_block_ids_keep_order_and_reject_collisions(self) -> None:
        renderer = Renderer({"title": "IDs"}, FIXTURES)

        code = renderer.block({"type": "code", "text": "first"})
        tabs = renderer.block(
            {"type": "tabs", "tabs": [{"title": "One", "blocks": ["Body"]}]}
        )

        self.assertIn('id="ve-1"', code)
        self.assertIn('id="ve-2-tab-0"', tabs)
        self.assertIn('id="ve-2-panel-0"', tabs)
        with self.assertRaisesRegex(ValueError, "Duplicate/reserved ID: ve-1"):
            _ = renderer.block({"type": "code", "id": "ve-1", "text": "second"})

    def test_existing_public_keyword_parameters_remain_supported(self) -> None:
        renderer = Renderer({"title": "Keywords"}, str(FIXTURES))

        self.assertEqual("<p>hello</p>", renderer.block(b="hello"))
        self.assertIn(
            'class="flow"', renderer.diagram(b={"nodes": [{"label": "Start"}]})
        )
        self.assertIn(
            'class="graph-svg"',
            renderer.graph_diagram(b={"nodes": [{"id": "a", "label": "A"}]}),
        )
        self.assertIn(
            'class="sequence-svg"',
            renderer.sequence_diagram(b={"actors": ["A", "B"], "messages": []}),
        )
        data = {"categories": ["A"], "values": [1]}
        self.assertIn(
            'class="chart visual"',
            renderer.chart(b={"kind": "bar", "title": "Values", "data": data}),
        )
        validate_chart(kind="bar", d=data)

    def test_unknown_blocks_keep_their_error(self) -> None:
        renderer = Renderer({"title": "Invalid"}, FIXTURES)
        for block in [None, 7, {}, {"type": "missing"}]:
            with self.subTest(block=block), self.assertRaisesRegex(
                ValueError, "Unknown block type:"
            ):
                _ = renderer.block(block)

    def test_invalid_chart_data_reaches_each_shape_boundary(self) -> None:
        cases: list[tuple[str, Mapping[str, object], str]] = [
            ("line", {"categories": [], "series": []}, "needs categories and series"),
            (
                "area",
                {"categories": ["A"], "series": [{"name": "X", "values": [1, 2]}]},
                "Every series must match categories length",
            ),
            (
                "bar",
                {"categories": ["A"], "values": []},
                "categories and values must match",
            ),
            ("bar", {"categories": ["A"], "values": [True]}, "finite numbers"),
            ("donut", {"categories": ["A"], "values": [0]}, "positive total"),
            ("scatter", {"points": [{"x": float("inf"), "y": 1}]}, "finite numbers"),
            (
                "histogram",
                {
                    "bins": [
                        {"low": 0, "high": 1, "count": 1},
                        {"low": 2, "high": 3, "count": 1},
                    ]
                },
                "increasing, contiguous, equal width",
            ),
            (
                "histogram",
                {
                    "bins": [
                        {"low": 0, "high": 1, "count": 1},
                        {"low": 1, "high": 3, "count": 1},
                    ]
                },
                "Histogram bins must be equal width",
            ),
            (
                "heatmap",
                {"rows": ["A"], "columns": ["B"], "values": [[1, 2]]},
                "matrix must match labels",
            ),
            (
                "box",
                {"groups": [{"min": 0, "q1": 3, "median": 2, "q3": 4, "max": 5}]},
                "min <= q1 <= median <= q3 <= max",
            ),
        ]
        for kind, data, message in cases:
            with self.subTest(kind=kind, data=data), self.assertRaisesRegex(
                ValueError, message
            ):
                validate_chart(kind, data)


if __name__ == "__main__":
    _ = unittest.main()
