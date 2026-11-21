"""Source-line, annotation placement, and input-rejection contracts."""

import html
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from code_blocks import prepare_code_block
from code_highlighting import highlight_code
from render import Renderer


class CodeBlockTests(unittest.TestCase):
    def test_notes_follow_source_positions_and_keep_same_position_order(self) -> None:
        # Mix input positions to distinguish source order from annotation order.
        output = Renderer({"title": "Notes"}, Path.cwd()).block(
            {
                "type": "code",
                "language": "Rust",
                "text": "fn main() {\n}\n",
                "annotations": [
                    {"position": "bottom", "text": "Bottom"},
                    {"position": 1, "text": "First"},
                    {"title": "<Source>", "text": "**Top** with `code`"},
                    {"position": 1, "text": "Second"},
                    {"position": 2, "text": "Last line"},
                ],
            }
        )

        # Parse only renderer-produced markup to inspect rendered reading order.
        root = ET.fromstring(output)  # noqa: S314 — renderer escapes all input markup.
        content = root.findall("code")[0]
        events = [
            (element.get("class"), "".join(element.itertext())) for element in content
        ]
        self.assertEqual(
            events,
            [
                ("code-annotation", "<Source>Top with code"),
                ("code-line", "1fn main() {"),
                ("code-annotation", "First"),
                ("code-annotation", "Second"),
                ("code-line", "2}"),
                ("code-annotation", "Last line"),
                ("code-annotation", "Bottom"),
            ],
        )
        self.assertIsNone(content.find(".//Source"))
        self.assertIsNotNone(content.find(".//strong"))

    def test_highlighting_retains_multiline_context_and_original_endings(self) -> None:
        # Use a multiline string whose middle line resembles executable code.
        source = 'value = """first\r\nreturn 42\rlast"""\n\n'
        result = highlight_code(source, "Python")

        # Reconstruct literal source from balanced line markup and separate endings.
        reconstructed = "".join(
            html.unescape(re.sub(r"</?span[^>]*>", "", line.markup)) + line.ending
            for line in result.lines
        )
        self.assertEqual(source, reconstructed)
        self.assertEqual(["\r\n", "\r", "\n", "\n"], [x.ending for x in result.lines])
        self.assertIn('class="syn-string">return 42</span>', result.lines[1].markup)
        self.assertNotIn("syn-keyword", result.lines[1].markup)

    def test_blank_and_terminated_lines_have_stable_numbers(self) -> None:
        # Count actual source lines, with one addressable row for empty input.
        for source, count in [
            ("", 1),
            ("\n", 1),
            ("a\n", 1),
            ("a\n\n", 2),
            ("a\rb", 2),
        ]:
            with self.subTest(source=source):
                result = prepare_code_block(
                    highlight_code(source, ""), [{"position": count, "text": "End"}]
                )
                self.assertEqual(count, len(result.source.lines))
                self.assertEqual("End", result.annotations[count][0].text)

    def test_large_gutter_and_copyable_rows_preserve_exact_source(self) -> None:
        # Include four-digit numbering and mixed line endings in a large block.
        source = "\t<&>\r\n" * 999 + "last\r"
        output = Renderer({"title": "Large"}, Path.cwd()).block(
            {"type": "code", "text": source}
        )

        # Recover source from the same row fields used by the browser copy control.
        root = ET.fromstring(output)  # noqa: S314 — renderer escapes all input markup.
        content = root.findall("code")[0]
        self.assertEqual("--code-digits:4", content.get("style"))
        rows = content.findall("span[@class='code-line']")
        self.assertEqual(1000, len(rows))
        recovered = "".join(
            "".join(row.findall("span[@class='code-line-text']")[0].itertext())
            + row.attrib["data-ending"]
            for row in rows
        )
        self.assertEqual(source, recovered)

    def test_start_renumbers_rows_positions_and_referenced_lines(self) -> None:
        # Number a three-line excerpt as lines 98 to 100 of its file.
        output = Renderer({"title": "Excerpt"}, Path.cwd()).block(
            {
                "type": "code",
                "text": "a\nb\nc\n",
                "start": 98,
                "annotations": [
                    {"position": 99, "lines": [99, 100], "text": "Note"},
                ],
            }
        )

        # Show file numbers in the gutter, the note's badge, and the range data.
        root = ET.fromstring(output)  # noqa: S314 — renderer escapes all input markup.
        content = root.findall("code")[0]
        self.assertEqual("--code-digits:3", content.get("style"))
        self.assertEqual(
            [
                ("code-line", "98a"),
                ("code-line", "99b"),
                ("code-annotation", "Lines 99\u2013100Note"),
                ("code-line", "100c"),
            ],
            [(row.get("class"), "".join(row.itertext())) for row in content],
        )
        note = content.findall("span[@class='code-annotation']")[0]
        self.assertEqual(
            ("99", "100"),
            (note.attrib["data-range-start"], note.attrib["data-range-end"]),
        )
        self.assertEqual(
            ["98", "99", "100"],
            [row.attrib["data-source-line"] for row in content if row is not note],
        )

    def test_start_bounds_annotations_and_rejects_invalid_values(self) -> None:
        # Reject lines numbered as if the excerpt still began at one.
        source = highlight_code("a\nb", "")
        for annotation, message in [
            ({"text": "n", "position": 1}, "between 40 and 41"),
            ({"text": "n", "lines": [1, 2]}, "40 <= start <= end <= 41"),
        ]:
            with (
                self.subTest(annotation=annotation),
                self.assertRaisesRegex(ValueError, message),
            ):
                _ = prepare_code_block(source, [annotation], 40)

        # Reject starts that cannot number a first line.
        for start in [0, -3, True, 1.0, "2", None]:
            with (
                self.subTest(start=start),
                self.assertRaisesRegex(ValueError, "start must be an integer >= 1"),
            ):
                _ = prepare_code_block(source, [], start)

    def test_ranges_share_identities_and_keep_every_overlap(self) -> None:
        # Mix placement and range order, including an identical repeated range.
        result = prepare_code_block(
            highlight_code("a\nb\nc\nd", ""),
            [
                {"text": "later", "lines": [2, 4]},
                {"text": "early", "position": "bottom", "lines": [1, 3]},
                {"text": "same", "lines": [2, 4]},
                {"text": "single", "lines": 2},
                {"text": "general"},
            ],
        )

        # Preserve all distinct overlapping identities in source/input order.
        self.assertEqual(((0,), (0, 1, 2), (0, 1), (1,)), result.line_ranges)
        self.assertEqual(3, len(result.ranges))
        self.assertEqual(
            result.annotations["top"][0].lines, result.annotations["top"][1].lines
        )
        self.assertIsNone(result.annotations["top"][-1].lines)

    def test_invalid_reference_bounds_stop_rendering(self) -> None:
        # Reject ambiguous values and references outside the source.
        for bounds in [
            True,
            1.5,
            "1",
            None,
            [],
            [1],
            [1, 2, 3],
            [True, 2],
            [1, "2"],
            0,
            3,
            [2, 1],
            [1, 3],
        ]:
            with (
                self.subTest(bounds=bounds),
                self.assertRaisesRegex(ValueError, "lines must"),
            ):
                _ = prepare_code_block(
                    highlight_code("a\nb", ""), [{"text": "note", "lines": bounds}]
                )

    def test_malformed_annotations_fail_instead_of_moving_notes(self) -> None:
        # Reject out-of-range lines, booleans, fractional positions, and bad fields.
        cases: list[tuple[object, str]] = [
            (None, "must be a list"),
            ({}, "must be a list"),
            (["note"], "must be an object"),
            ([{}], "text must be a nonblank string"),
            ([{"text": " "}], "text must be a nonblank string"),
            ([{"text": "Note", "title": None}], "title must be a string"),
            ([{"text": "Note", "position": 0}], "between 1 and 2"),
            ([{"text": "Note", "position": 3}], "between 1 and 2"),
            ([{"text": "Note", "position": True}], "position must be"),
            ([{"text": "Note", "position": 1.5}], "position must be"),
            ([{"text": "Note", "position": "1"}], "position must be"),
            ([{"text": "Note", "line": 1}], "accepts only"),
        ]

        # Check errors at the renderer boundary used by document generation.
        for annotations, message in cases:
            with (
                self.subTest(annotations=annotations),
                self.assertRaisesRegex(ValueError, message),
            ):
                _ = Renderer({"title": "Invalid"}, Path.cwd()).block(
                    {
                        "type": "code",
                        "text": "first\nsecond",
                        "annotations": annotations,
                    }
                )


if __name__ == "__main__":
    _ = unittest.main()
