"""Document output and rejection contracts across renderer variants."""

import base64
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, cast
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from diagram_layout import FontMetrics
from render import (
    ASSETS,
    THEMES,
    Renderer,
    check_html,
    validate_bounds,
    validate_chart,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class RenderTests(unittest.TestCase):
    def test_generated_scripts_are_embedded_with_charts_only_when_needed(self) -> None:
        # Read the generated assets that ship with the standalone skill.
        navigation = (ASSETS / "navigation.min.js").read_text(encoding="utf-8")
        core = (ASSETS / "core.min.js").read_text(encoding="utf-8")
        charts = (ASSETS / "charts.min.js").read_text(encoding="utf-8")

        # Build ordinary content without the optional chart runtime.
        ordinary = Renderer({"title": "Compact Assets"}, FIXTURES).render()

        # Verify that the generated navigation and controls are embedded directly.
        self.assertIn(navigation, ordinary)
        self.assertIn(core, ordinary)
        self.assertNotIn(charts, ordinary)
        self.assertNotIn("// Bind each range control", ordinary)

        # Build chart content through the same document entry point.
        chart: dict[str, object] = {
            "type": "chart",
            "kind": "bar",
            "title": "Values",
            "data": {"categories": ["One"], "values": [1]},
        }
        with_chart = Renderer(
            {"title": "Compact Charts", "intro": [chart]}, FIXTURES
        ).render()

        # Verify that chart documents also include the generated chart runtime.
        self.assertIn(charts, with_chart)
        self.assertIn(navigation, with_chart)
        self.assertIn(core, with_chart)
        self.assertEqual([], check_html(with_chart))

    def test_svg_diagrams_offer_controls_with_a_scrollable_fallback(self) -> None:
        # Render each diagram kind through the document entry point.
        variants: list[dict[str, object]] = [
            {"type": "diagram", "kind": "flow", "nodes": [{"label": "Start"}]},
            {
                "type": "diagram",
                "kind": "graph",
                "nodes": [{"id": "start", "label": "Start"}],
            },
            {
                "type": "diagram",
                "kind": "sequence",
                "actors": ["Caller", "Service"],
                "messages": [],
            },
        ]
        controller = (ASSETS / "diagrams.min.js").read_text(encoding="utf-8")

        for diagram in variants:
            with self.subTest(kind=diagram["kind"]):
                output = Renderer(
                    {"title": "Diagram Controls", "intro": [diagram]}, FIXTURES
                ).render()

                # Keep each figure offline and its ordinary scrollable container intact.
                self.assertEqual([], check_html(output))
                self.assertIn('class="diagram-scroll"', output)
                self.assertNotIn('class="diagram-scroll diagram-panzoom"', output)

                # Offer hidden controls and the enhancement runtime only for SVG diagrams.
                if diagram["kind"] == "flow":
                    self.assertNotIn(controller, output)
                    self.assertNotIn("data-diagram-viewport data-diagram-help=", output)
                    continue

                self.assertIn(controller, output)
                self.assertIn('class="diagram-tools" hidden', output)
                self.assertIn("data-diagram-viewport data-diagram-help=", output)
                self.assertNotIn('class="diagram-controls-toggle"', output)
                self.assertIn('class="diagram-zoom" role="group"', output)
                self.assertIn("one finger pans and two fingers pinch", output)
                self.assertIn('aria-label="Zoom Out"', output)
                self.assertIn('aria-label="Zoom In"', output)
                self.assertIn('aria-label="Fit to View" title="Fit to View"', output)
                self.assertIn("icon-expand", output)

    def test_plain_theme_defaults_to_system_with_only_appearance_choices(self) -> None:
        # Build a document using the default theme settings.
        output = Renderer({"title": "Appearance"}, FIXTURES).render()

        # Verify the system appearance and the three supported menu choices.
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
        # Render default and explicitly selected plain themes.
        default = Renderer({"title": "Appearance"}, FIXTURES).render()
        explicit = Renderer(
            {"title": "Appearance", "theme": "plain"}, FIXTURES
        ).render()

        # Verify that explicit theme selection leaves output unchanged.
        self.assertEqual(default, explicit)

    def test_output_embeds_only_the_selected_theme_set(self) -> None:
        # Derive a distinguishable set from the bundled plain manifest.
        plain = cast(
            "dict[str, object]",
            json.loads(THEMES["plain"].read_text(encoding="utf-8")),
        )
        tokens = cast("dict[str, list[str]]", plain["tokens"])
        warm = {**plain, "tokens": {**tokens, "bg": ["#fff0ed", "#211b18"]}}

        # Register the disposable set and render both selections.
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "warm.json"
            _ = manifest.write_text(json.dumps(warm), encoding="utf-8")
            with patch.dict(THEMES, {"warm": manifest}):
                default = Renderer({"title": "Appearance"}, FIXTURES).render()
                alternate = Renderer(
                    {"title": "Appearance", "theme": "warm"}, FIXTURES
                ).render()

        # Verify that each document carries only its own palette.
        self.assertIn("--bg:light-dark(#fafafa,#181818)", default)
        self.assertNotIn("#fff0ed", default)
        self.assertIn("--bg:light-dark(#fff0ed,#211b18)", alternate)
        self.assertNotIn("#fafafa", alternate)
        self.assertIn('<body data-theme="warm" data-appearance="system">', alternate)

    def test_report_theme_embeds_only_its_fonts_licenses_and_styles(self) -> None:
        # Render the same content in both bundled sets.
        plain = Renderer({"title": "Fonts"}, FIXTURES).render()
        report = Renderer({"title": "Fonts", "theme": "report"}, FIXTURES).render()

        # Encode the leading bytes of each generated WOFF2 font as embedded data.
        fonts = {
            name: base64.b64encode(
                (ASSETS / "fonts" / name).with_suffix(".woff2").read_bytes()[:3000]
            ).decode()
            for name in [
                "Manrope.ttf",
                "JetBrainsMono.ttf",
                "IBMPlexSans.ttf",
                "IBMPlexMono-Regular.ttf",
                "IBMPlexMono-Medium.ttf",
            ]
        }
        report_css = (ASSETS / "themes" / "report.css").read_text(encoding="utf-8")

        # Verify that plain keeps its own fonts and licenses and no report styles.
        self.assertIn(fonts["Manrope.ttf"], plain)
        self.assertIn(fonts["JetBrainsMono.ttf"], plain)
        self.assertNotIn(fonts["IBMPlexSans.ttf"], plain)
        self.assertNotIn("ibmplexsans-OFL.txt", plain)
        self.assertNotIn(report_css, plain)

        # Verify that report swaps in IBM Plex, its licenses, and its stylesheet.
        for name in [
            "IBMPlexSans.ttf",
            "IBMPlexMono-Regular.ttf",
            "IBMPlexMono-Medium.ttf",
        ]:
            self.assertIn(fonts[name], report)
        self.assertNotIn(fonts["Manrope.ttf"], report)
        self.assertIn("ibmplexsans-OFL.txt", report)
        self.assertIn("ibmplexmono-OFL.txt", report)
        self.assertNotIn("manrope-OFL.txt", report)
        self.assertIn(report_css, report)
        self.assertIn('<body data-theme="report" data-appearance="system">', report)

    def test_accent_presets_and_custom_pairs_set_the_accent_token(self) -> None:
        # Render the default, each report preset, and a custom pair.
        def render(accent: object = None) -> str:
            document: dict[str, object] = {"title": "Accent", "theme": "report"}
            if accent is not None:
                document["accent"] = accent
            return Renderer(document, FIXTURES).render()

        default = render()
        rust = render("rust")
        blue = render("blue")
        custom = render({"light": "#5C6420", "dark": "#c2c97a"})

        # Verify that the default is the blue preset and rust differs from it.
        self.assertEqual(default, blue)
        self.assertIn("--accent:light-dark(#a14a1f,#f0a477)", rust)
        self.assertIn("--accent:light-dark(#1f4f8f,#8db4ec)", blue)
        self.assertIn("--chart-secondary:light-dark(#c0622a,#eba06a)", blue)
        self.assertNotIn("#a14a1f", blue)

        # Verify that a custom pair replaces only the accent, normalized to lowercase.
        self.assertIn("--accent:light-dark(#5c6420,#c2c97a)", custom)
        self.assertIn("--chart-secondary:light-dark(#c0622a,#eba06a)", custom)

    def test_invalid_accents_are_rejected(self) -> None:
        for accent, message in [
            ("green", "accent must be blue, rust, or"),
            ("graphite", "accent must be blue, rust, or"),
            ({"light": "#fff", "dark": "#000000"}, "accent must be"),
            ({"light": "#5c6420"}, "accent must be"),
            (
                {"light": "#5c6420", "dark": "#c2c97a", "chart": "#000000"},
                "accent must be",
            ),
            (
                {"light": "#eeeeee", "dark": "#c2c97a"},
                "too little contrast: accent on bg in light",
            ),
            (
                {"light": "#5c6420", "dark": "#303030"},
                "too little contrast: accent on bg in dark",
            ),
            (
                {"light": "#717171", "dark": "#c2c97a"},
                "too little contrast: accent on wash in light",
            ),
        ]:
            with (
                self.subTest(accent=accent),
                self.assertRaisesRegex(ValueError, re.escape(message)),
            ):
                _ = Renderer(
                    {"title": "Accent", "theme": "report", "accent": accent}, FIXTURES
                ).render()

    def test_report_numbers_are_fixed_in_document_order(self) -> None:
        # Mix numbered items with an intro heading, a closed disclosure, and tabs.
        caption = "Shown"
        document: dict[str, object] = {
            "title": "Numbering",
            "theme": "report",
            "intro": [{"type": "heading", "text": "Intro Heading"}],
            "sections": [
                {
                    "title": "First",
                    "blocks": [
                        {"type": "heading", "text": "Alpha"},
                        {
                            "type": "disclosure",
                            "title": "Closed",
                            "blocks": [
                                {"type": "heading", "text": "Hidden"},
                                {
                                    "type": "table",
                                    "headers": ["A"],
                                    "rows": [["1"]],
                                    "caption": caption,
                                },
                            ],
                        },
                        {
                            "type": "tabs",
                            "tabs": [
                                {
                                    "title": "One",
                                    "blocks": [{"type": "heading", "text": "In Tab"}],
                                },
                                {
                                    "title": "Two",
                                    "blocks": [
                                        {
                                            "type": "table",
                                            "headers": ["A"],
                                            "rows": [["1"]],
                                            "caption": caption,
                                        }
                                    ],
                                },
                            ],
                        },
                        {"type": "heading", "text": "Beta"},
                        {"type": "heading", "level": 4, "text": "Minor"},
                    ],
                },
                {
                    "title": "Second",
                    "blocks": [
                        {"type": "table", "headers": ["A"], "rows": [["1"]]},
                        {"type": "equation", "text": "a + b", "caption": caption},
                        {
                            "type": "diagram",
                            "kind": "flow",
                            "nodes": [{"label": "Step"}],
                            "caption": caption,
                        },
                        {"type": "heading", "text": "Gamma"},
                    ],
                },
            ],
        }

        # Render the report document and the same content in plain.
        report = Renderer(document, FIXTURES).render()
        plain = Renderer({**document, "theme": "plain"}, FIXTURES).render()

        # Verify headings: intro and tab headings and H4 stay unnumbered, and a
        # heading inside a closed disclosure keeps its place in the sequence.
        self.assertEqual(
            ["1", "1.1", "1.2", "1.3", "2", "2.1"],
            re.findall(r'<h[23] id="[^"]+" data-number="([0-9.]+)"', report),
        )
        self.assertEqual(2, len(re.findall(r'<h3 id="[^"]+">', report)))
        self.assertNotIn('data-number="0', report)

        # Verify captions: captioned tables count across panels; equations do not.
        self.assertEqual(
            ["1", "2"],
            re.findall(r'<caption class="table-caption" data-number="(\d+)">', report),
        )
        self.assertEqual(
            ["1"], re.findall(r'<figcaption[^>]* data-number="(\d+)"', report)
        )

        # Verify that a set without numbering emits no numbers.
        self.assertNotIn("data-number=", plain)

    def test_diagram_labels_are_measured_with_the_theme_font(self) -> None:
        # Measure one label with each set's diagram metrics.
        label = "Acknowledge the durable commit"
        plain = Renderer({"title": "Metrics"}, FIXTURES).diagram_metrics()
        report = Renderer(
            {"title": "Metrics", "theme": "report"}, FIXTURES
        ).diagram_metrics()

        # Verify that the report set measures with IBM Plex Sans.
        expected = FontMetrics(ASSETS / "fonts" / "IBMPlexSans.ttf").width(label, 14)
        self.assertEqual(expected, report.width(label, 14))
        self.assertNotEqual(plain.width(label, 14), report.width(label, 14))

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
            with (
                self.subTest(theme=theme),
                self.assertRaisesRegex(ValueError, "theme must be plain, report"),
            ):
                _ = Renderer({"title": "Appearance", "theme": theme}, FIXTURES).render()

    def test_all_block_and_chart_variants_build_one_offline_document(self) -> None:
        # Read the fixture covering every block and chart variant.
        document = cast(
            "Mapping[str, object]",
            json.loads((FIXTURES / "all_blocks.json").read_text(encoding="utf-8")),
        )

        # Render the fixture through the document entry point.
        output = Renderer(document, FIXTURES).render()

        # Verify offline structure and representative generated components.
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
        # Create one renderer to retain ID state across blocks.
        renderer = Renderer({"title": "IDs"}, FIXTURES)

        # Render code and tabs in encounter order.
        code = renderer.block({"type": "code", "text": "first"})
        tabs = renderer.block(
            {"type": "tabs", "tabs": [{"title": "One", "blocks": ["Body"]}]}
        )

        # Verify generated IDs and paired tab-panel reservations.
        self.assertIn('id="ve-1"', code)
        self.assertIn('id="ve-2-tab-0"', tabs)
        self.assertIn('id="ve-2-panel-0"', tabs)

        # Reject reuse of an earlier block ID.
        with self.assertRaisesRegex(ValueError, "Duplicate/reserved ID: ve-1"):
            _ = renderer.block({"type": "code", "id": "ve-1", "text": "second"})

    def test_existing_public_keyword_parameters_remain_supported(self) -> None:
        # Configure the renderer with the supported string base path.
        renderer = Renderer({"title": "Keywords"}, str(FIXTURES))

        # Exercise the existing block and diagram keyword parameters.
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

        # Exercise chart rendering and validation with their existing keywords.
        data = {"categories": ["A"], "values": [1]}
        self.assertIn(
            'class="chart visual"',
            renderer.chart(b={"kind": "bar", "title": "Values", "data": data}),
        )
        validate_chart(kind="bar", d=data)

    def test_unknown_blocks_keep_their_error(self) -> None:
        # Configure an ordinary document renderer.
        renderer = Renderer({"title": "Invalid"}, FIXTURES)

        # Reject non-block values and unknown block variants.
        blocks: list[object] = [
            None,
            7,
            {},
            {"type": "missing"},
            {"type": ["x"]},
            {"type": {}},
        ]
        for block in blocks:
            with (
                self.subTest(block=block),
                self.assertRaisesRegex(ValueError, "Unknown block type:"),
            ):
                _ = renderer.block(block)

    def test_invalid_chart_data_reaches_each_shape_boundary(self) -> None:
        # Pair invalid chart shapes and numbers with their expected diagnostics.
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

        # Verify that each chart variant reaches its intended validation boundary.
        for kind, data, message in cases:
            with (
                self.subTest(kind=kind, data=data),
                self.assertRaisesRegex(ValueError, message),
            ):
                validate_chart(kind, data)

    def test_axis_bounds_must_be_ordered_finite_numbers(self) -> None:
        # Pair invalid bound combinations with their expected diagnostics.
        cases: list[tuple[str, Mapping[str, object], str]] = [
            ("line", {"xMin": 0}, "apply only to scatter"),
            ("scatter", {"xMin": "0"}, "xMin and xMax must be finite numbers"),
            ("bar", {"yMax": float("nan")}, "yMin and yMax must be finite numbers"),
            ("scatter", {"xMin": 5, "xMax": 5}, "xMin must be less than xMax"),
            ("box", {"yMin": 10, "yMax": 2}, "yMin must be less than yMax"),
        ]

        # Verify that each invalid combination is rejected.
        for kind, options, message in cases:
            with (
                self.subTest(kind=kind, options=options),
                self.assertRaisesRegex(ValueError, message),
            ):
                validate_bounds(kind, options)

        # Accept one-sided and ordered bounds, including scatter x bounds.
        validate_bounds("scatter", {"xMin": 1000, "xMax": 1010, "yMin": 0})
        validate_bounds("line", {"yMax": 100})

    def test_documents_and_blocks_report_missing_and_mistyped_fields(self) -> None:
        # Pair malformed documents with the field-level diagnostics they produce.
        cases: list[tuple[Mapping[str, object], str]] = [
            ({}, "document requires field 'title'"),
            (
                {"title": "T", "intro": [{"type": "range", "label": "N", "min": "1"}]},
                "range block field 'min' must be a finite number",
            ),
            (
                {"title": "T", "sections": [{"blocks": []}]},
                "section requires field 'title'",
            ),
            (
                {"title": "T", "intro": [{"type": "table", "headers": ["A"]}]},
                "table block requires field 'rows'",
            ),
            (
                {"title": "T", "intro": [{"type": "list", "items": "one"}]},
                "list block field 'items' must be a list",
            ),
            (
                {"title": "T", "intro": [{"type": "choice", "label": "Pick"}]},
                "choice block requires field 'options'",
            ),
            (
                {
                    "title": "T",
                    "intro": [{"type": "diagram", "kind": "sequence", "actors": []}],
                },
                "sequence diagram requires field 'messages'",
            ),
            (
                {
                    "title": "T",
                    "intro": [
                        {"type": "chart", "kind": "bar", "title": "C", "data": []}
                    ],
                },
                "chart block field 'data' must be an object",
            ),
        ]

        # Verify that each malformed input stops with its diagnostic.
        for document, message in cases:
            with (
                self.subTest(document=document),
                self.assertRaisesRegex(ValueError, re.escape(message)),
            ):
                _ = Renderer(document, FIXTURES).render()

    def test_scalar_fields_keep_accepting_values_that_always_rendered(self) -> None:
        # Compose a document using numeric titles and integer flags.
        document: Mapping[str, object] = {
            "title": 2024,
            "brand": 7,
            "sections": [
                {
                    "title": 2025,
                    "blocks": [
                        {"type": "list", "ordered": 1, "items": ["a"]},
                        {"type": "disclosure", "title": 3, "open": 1, "blocks": ["b"]},
                        {
                            "type": "chart",
                            "kind": "line",
                            "title": 4,
                            "selectedIndex": 0.0,
                            "data": {
                                "categories": ["x"],
                                "series": [{"name": "S", "values": [1]}],
                            },
                        },
                    ],
                }
            ],
        }

        # Build it as earlier releases did.
        output = Renderer(document, FIXTURES).render()
        self.assertIn(">2025</h2>", output)


if __name__ == "__main__":
    _ = unittest.main()
