"""Diff alignment, layout, and input-rejection contracts."""

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from diff_blocks import DiffRow, prepare_diff, unified_rows
from render import Renderer


def _rendered(block: dict[str, object]) -> ET.Element:
    # Parse only renderer-produced markup to inspect the rendered structure.
    output = Renderer({"title": "Diff"}, Path.cwd()).block({"type": "diff", **block})
    return ET.fromstring(output)  # noqa: S314 — renderer escapes all input markup.


def _texts(parent: ET.Element, name: str) -> list[str]:
    return [
        "".join(element.itertext())
        for element in parent.iter("span")
        if element.get("class") == name
    ]


class DiffBlockTests(unittest.TestCase):
    def test_replacements_pair_by_position_and_unify_removals_first(self) -> None:
        # Replace two lines with three between unchanged neighbors.
        prepared = prepare_diff("a\nb\nc\nz\n", "a\nx\ny\nw\nz\n")

        # Pair replaced lines side by side and leave the surplus addition unpaired.
        rows = prepared.hunks[0].rows
        self.assertEqual(
            (
                DiffRow(0, 0, False),
                DiffRow(1, 1, True),
                DiffRow(2, 2, True),
                DiffRow(None, 3, True),
                DiffRow(3, 4, False),
            ),
            rows,
        )
        self.assertEqual((2, 3), (prepared.deletions, prepared.insertions))

        # Read every removal of the change before any of its additions.
        self.assertEqual(
            (
                DiffRow(0, 0, False),
                DiffRow(1, None, True),
                DiffRow(2, None, True),
                DiffRow(None, 1, True),
                DiffRow(None, 2, True),
                DiffRow(None, 3, True),
                DiffRow(3, 4, False),
            ),
            unified_rows(rows),
        )

    def test_context_limits_hunks_and_counts_omitted_lines(self) -> None:
        # Change the second and last lines of a ten-line source.
        before = "".join(f"line {number}\n" for number in range(1, 11))
        after = before.replace("line 2\n", "two\n").replace("line 10\n", "ten\n")

        # Keep one unchanged line around each change and count the rest.
        prepared = prepare_diff(before, after, 1)
        self.assertEqual([0, 5], [hunk.hidden for hunk in prepared.hunks])
        self.assertEqual(0, prepared.trailing)
        self.assertEqual([3, 2], [len(hunk.rows) for hunk in prepared.hunks])

        # Show no unchanged lines when no context is requested.
        bare = prepare_diff(before, after, 0)
        self.assertEqual([1, 7], [hunk.hidden for hunk in bare.hunks])
        self.assertTrue(all(row.changed for hunk in bare.hunks for row in hunk.rows))

        # Count unchanged lines left after the final hunk.
        self.assertEqual(8, prepare_diff(before, "two\n" + before[7:], 1).trailing)

    def test_added_and_removed_files_have_one_sided_rows(self) -> None:
        # Compare against empty source in each direction.
        added = prepare_diff("", "a\nb\n")
        removed = prepare_diff("a\nb\n", "")

        self.assertEqual(
            (DiffRow(None, 0, True), DiffRow(None, 1, True)), added.hunks[0].rows
        )
        self.assertEqual((2, 0), (removed.deletions, removed.insertions))

    def test_both_layouts_render_numbered_highlighted_source(self) -> None:
        # Offset each version's numbering as an excerpt from a larger file.
        root = _rendered(
            {
                "language": "Python",
                "title": "<app>.py",
                "view": "split",
                "before": "x = 1\nreturn x\n",
                "after": "x = 2\nreturn x\n",
                "before_start": 99,
                "after_start": 120,
            }
        )

        # Start in the requested layout with matching toggle state.
        self.assertEqual("split", root.get("data-diff-view"))
        self.assertEqual(
            [("unified", "false"), ("split", "true")],
            [
                (button.attrib["data-diff-choice"], button.attrib["aria-pressed"])
                for button in root.iter("button")
            ],
        )
        self.assertEqual("<app>.py", next(root.iter("span")).findtext("span"))

        # Read the unified layout as removal, addition, then shared context.
        unified, split = root.findall("code")
        self.assertEqual("--code-digits:3", unified.get("style"))
        self.assertEqual(
            ["delete", "insert", "context"],
            [row.attrib["data-diff"] for row in unified],
        )
        self.assertEqual(
            ["99", "", "", "120", "100", "121"], _texts(unified, "diff-number")
        )
        self.assertEqual(["x = 1", "x = 2", "return x"], _texts(unified, "diff-text"))
        self.assertIn("syn-keyword", ET.tostring(unified, encoding="unicode"))

        # Place the same lines side by side with one number per version.
        self.assertEqual(
            [["delete", "insert"], ["context", "context"]],
            [[side.attrib["data-diff"] for side in pair] for pair in split],
        )
        self.assertEqual(["99", "120", "100", "121"], _texts(split, "diff-number"))

    def test_omitted_lines_are_named_between_hunks(self) -> None:
        # Leave unchanged source before, between, and after two changes.
        before = "".join(f"{number}\n" for number in range(1, 13))
        after = before.replace("3\n", "c\n").replace("9\n", "i\n")
        root = _rendered({"before": before, "after": after, "context": 1})

        # Repeat the same separators in both layouts.
        for content in root.findall("code"):
            self.assertEqual(
                ["1 unchanged line", "3 unchanged lines", "2 unchanged lines"],
                _texts(content, "diff-gap"),
            )

    def test_notes_follow_their_lines_in_both_layouts(self) -> None:
        # Annotate a removed line, a replacement range, and the diff as a whole.
        root = _rendered(
            {
                "before": "keep\nold\ngone\n",
                "after": "keep\nnew\nadded\n",
                "before_start": 10,
                "after_start": 20,
                "annotations": [
                    {"position": "bottom", "text": "Last"},
                    {"lines": 12, "side": "before", "text": "Why it went"},
                    {"lines": [21, 22], "title": "<T>", "text": "**Both** lines"},
                    {"text": "Overview"},
                ],
            }
        )

        # Place each note after its last line, wherever the layout puts that line.
        unified, split = (
            [
                "".join(row.itertext())
                for row in content
                if "code-annotation" in row.attrib["class"]
                or row.attrib["class"] in ("diff-line", "diff-pair")
            ]
            for content in root.findall("code")
        )
        self.assertEqual(
            [
                "Overview",
                "1020keep",
                "11\u2212Removedold",
                "12\u2212Removedgone",
                "Old line 12Why it went",
                "21+Addednew",
                "22+Addedadded",
                "New lines 21\u201322<T>Both lines",
                "Last",
            ],
            unified,
        )
        self.assertEqual(
            [
                "Overview",
                "10keep20keep",
                "11\u2212Removedold21+Addednew",
                "12\u2212Removedgone22+Addedadded",
                "Old line 12Why it went",
                "New lines 21\u201322<T>Both lines",
                "Last",
            ],
            split,
        )

        # Mark which version a referenced note explains, and escape its title.
        notes = [row for row in root.findall("code")[0] if row.get("role") == "note"]
        self.assertEqual(
            [None, "before", "after", None],
            [note.get("data-diff-note") for note in notes],
        )
        self.assertIsNone(root.find(".//T"))
        self.assertIsNotNone(root.find(".//strong"))

    def test_notes_on_collapsed_lines_need_an_explicit_position(self) -> None:
        # Leave line 1 outside the single line of context around the change.
        before = "".join(f"{number}\n" for number in range(1, 9))
        block: dict[str, object] = {
            "before": before,
            "after": before.replace("8\n", "eight\n"),
            "context": 1,
        }

        # Refuse to move a note away from the line it names.
        with self.assertRaisesRegex(ValueError, "line 1 is collapsed"):
            _ = _rendered(block | {"annotations": [{"lines": 1, "text": "n"}]})

        # Accept the same reference once the author chooses where it goes.
        root = _rendered(
            block | {"annotations": [{"lines": 1, "position": "top", "text": "n"}]}
        )
        self.assertEqual(
            ["New line 1"], _texts(root.findall("code")[0], "code-range-label")
        )

    def test_malformed_diff_annotations_stop_rendering(self) -> None:
        # Pair each invalid annotation list with the diagnostic it produces.
        cases: list[tuple[object, str]] = [
            ({}, "must be a list"),
            (["note"], "must be an object"),
            ([{}], "text must be a nonblank string"),
            ([{"text": " "}], "text must be a nonblank string"),
            ([{"text": "n", "title": 1}], "title must be a string"),
            ([{"text": "n", "position": 2}], "position must be top or bottom"),
            ([{"text": "n", "side": "before"}], "side applies only with lines"),
            ([{"text": "n", "lines": 1, "side": "old"}], "side must be before or"),
            ([{"text": "n", "lines": 3}], "1 <= start <= end <= 2"),
            ([{"text": "n", "lines": [2, 1]}], "lines must"),
            ([{"text": "n", "lines": True}], "lines must"),
            ([{"text": "n", "line": 1}], "accepts only"),
        ]

        for annotations, message in cases:
            with (
                self.subTest(annotations=annotations),
                self.assertRaisesRegex(ValueError, message),
            ):
                _ = _rendered(
                    {"before": "a\nb\n", "after": "a\nc\n", "annotations": annotations}
                )

    def test_malformed_diffs_stop_rendering(self) -> None:
        # Pair each invalid field with the diagnostic it produces.
        valid: dict[str, object] = {"before": "a\n", "after": "b\n"}
        cases: list[tuple[dict[str, object], str]] = [
            ({"before": 1}, "must be strings"),
            ({"after": None}, "must be strings"),
            ({"after": "a\n"}, "identical lines"),
            ({"after": "a\r\n"}, "identical lines"),
            ({"context": -1}, "non-negative integer"),
            ({"context": True}, "non-negative integer"),
            ({"context": 1.5}, "non-negative integer"),
            ({"view": "side"}, "unified or split"),
            ({"before_start": 0}, "integers >= 1"),
            ({"after_start": True}, "integers >= 1"),
        ]

        # Check errors at the renderer boundary used by document generation.
        for fields, message in cases:
            with (
                self.subTest(fields=fields),
                self.assertRaisesRegex(ValueError, message),
            ):
                _ = _rendered(valid | fields)

        # Require both versions rather than treating an absent one as empty.
        with self.assertRaisesRegex(ValueError, "requires field 'after'"):
            _ = _rendered({"before": "a\n"})


if __name__ == "__main__":
    _ = unittest.main()
