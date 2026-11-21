"""Align two source versions into diff hunks without performing I/O."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import groupby, zip_longest
from typing import cast

from code_blocks import SourceRange, source_range

DEFAULT_CONTEXT = 3
SIDES = ("before", "after")


@dataclass(frozen=True)
class DiffRow:
    """One side-by-side row of zero-based line indices into each version."""

    before: int | None
    """Line in the earlier version; None when this row has no earlier line."""
    after: int | None
    """Line in the later version; None when this row has no later line."""
    changed: bool
    """False for a line present in both versions; True for a removal or addition."""


@dataclass(frozen=True)
class DiffHunk:
    """Adjacent changes with their surrounding unchanged lines."""

    hidden: int
    """Unchanged lines omitted between the previous hunk, or the start, and this one."""
    rows: tuple[DiffRow, ...]
    """Side-by-side rows in source order; a replacement pairs lines by position."""


@dataclass(frozen=True)
class DiffNote:
    """Explanatory content shown between diff rows."""

    text: str
    """Required nonblank text accepting the renderer's safe inline vocabulary."""
    title: str
    """Optional title accepting inline formatting; empty means no title."""
    side: int | None = None
    """Version the lines belong to, 0 earlier or 1 later; None for a general note."""
    lines: SourceRange | None = None
    """Referenced lines in that version's numbering; None for a general note."""


@dataclass(frozen=True)
class PreparedDiff:
    """Hunks covering every difference between two versions, with their notes."""

    hunks: tuple[DiffHunk, ...]
    """One or more hunks in source order."""
    starts: tuple[int, int]
    """Number of the first line of the earlier and later version."""
    notes: dict[str | tuple[int, int], list[DiffNote]]
    """Notes keyed by top, bottom, or the (version, zero-based line) to follow."""
    trailing: int
    """Unchanged lines omitted after the last hunk."""
    deletions: int
    """Lines present only in the earlier version."""
    insertions: int
    """Lines present only in the later version."""


def source_lines(text: str) -> list[str]:
    """Split source into lines the way highlighted code numbers them.

    Args:
        text: Literal source using LF, CRLF, or CR line endings.

    Returns:
        Line contents without endings. A final ending adds no extra line, and
        empty source has no lines.
    """
    lines = re.split(r"\r\n|\r|\n", text)
    if not lines[-1]:
        _ = lines.pop()
    return lines


def _notes(
    annotations: object,
    hunks: list[DiffHunk],
    starts: tuple[int, int],
    counts: tuple[int, int],
) -> dict[str | tuple[int, int], list[DiffNote]]:
    # Require a list before validating individual notes.
    if not isinstance(annotations, list):
        raise ValueError("Diff annotations must be a list")

    # Record which lines of each version the hunks actually show.
    shown = (
        {row.before for hunk in hunks for row in hunk.rows},
        {row.after for hunk in hunks for row in hunk.rows},
    )

    # Validate each complete annotation before adding it to its placement group.
    grouped: dict[str | tuple[int, int], list[DiffNote]] = {}
    for index, raw in enumerate(cast("list[object]", annotations), 1):
        label = f"Diff annotation {index}"
        if not isinstance(raw, dict):
            raise ValueError(label + " must be an object")
        fields = cast("dict[str, object]", raw)
        if fields.keys() - {"text", "title", "position", "lines", "side"}:
            raise ValueError(
                label + " accepts only text, title, position, lines, and side"
            )
        content = fields.get("text")
        title = fields.get("title", "")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(label + " text must be a nonblank string")
        if not isinstance(title, str):
            raise ValueError(label + " title must be a string")
        position = fields.get("position")
        if position is not None and position not in ("top", "bottom"):
            raise ValueError(label + " position must be top or bottom")

        # Keep a note without referenced lines as a general note.
        if "lines" not in fields:
            if "side" in fields:
                raise ValueError(label + " side applies only with lines")
            grouped.setdefault(position or "top", []).append(DiffNote(content, title))
            continue

        # Resolve the referenced lines in the chosen version's own numbering.
        side_name = fields.get("side", "after")
        if side_name not in SIDES:
            raise ValueError(label + " side must be before or after")
        side = SIDES.index(cast("str", side_name))
        first = starts[side]
        lines = source_range(fields["lines"], first, first + counts[side] - 1, label)

        # Reject a note whose anchor line is collapsed instead of moving it.
        last_index = lines.end - first
        if position is None and last_index not in shown[side]:
            raise ValueError(
                f"{label} line {lines.end} is collapsed as unchanged; raise context to show it, or set position"
            )
        key = position or (side, last_index)
        grouped.setdefault(key, []).append(DiffNote(content, title, side, lines))

    return grouped


def prepare_diff(
    before: object,
    after: object,
    context: object = DEFAULT_CONTEXT,
    annotations: object = None,
    starts: tuple[object, object] = (1, 1),
) -> PreparedDiff:
    """Compare two versions line by line and group their differences.

    Args:
        before: Earlier source as a string; empty for a newly added file.
        after: Later source as a string; empty for a removed file.
        context: Non-negative integer count of unchanged lines kept around
            each change. Booleans are rejected.
        annotations: None, or a JSON list of objects with required nonblank
            string text and optional string title. Optional lines is one
            integer or [start, end] in the numbering of the version named by
            side, before or after (the default). Optional position is top or
            bottom. A note with lines and no position follows its last line,
            which must be shown; a note without lines defaults to top.
            Unknown fields, and side without lines, are rejected.
        starts: Integer number, at least 1, of the first line of the earlier
            and of the later version. Booleans are rejected.

    Returns:
        Hunks in source order. Lines compare by content, ignoring their line
        endings. Changes whose context overlaps or touches share one hunk.
        Notes at each placement retain their original list order.

    Raises:
        ValueError: A version is not a string, context or a start is not a
            valid integer, the versions have identical lines, or an annotation
            is malformed, out of range, or anchored to a collapsed line.
    """
    # Reject mistyped input instead of comparing its string form.
    if not isinstance(before, str) or not isinstance(after, str):
        raise ValueError("Diff before and after must be strings")
    if type(context) is not int or context < 0:
        raise ValueError("Diff context must be a non-negative integer")
    if any(type(start) is not int or start < 1 for start in starts):
        raise ValueError("Diff before_start and after_start must be integers >= 1")
    numbering = cast("tuple[int, int]", starts)

    # Require a difference so the block always has a change to show.
    old, new = source_lines(before), source_lines(after)
    if old == new:
        raise ValueError("Diff before and after have identical lines")

    # Group every change with the requested unchanged lines around it.
    matcher = SequenceMatcher(None, old, new, autojunk=False)
    hunks: list[DiffHunk] = []
    previous_end = 0
    for group in matcher.get_grouped_opcodes(context):
        # Pair matching lines, and pair replaced lines by position within the change.
        rows: list[DiffRow] = []
        for tag, old_start, old_end, new_start, new_end in group:
            rows.extend(
                DiffRow(old_index, new_index, tag != "equal")
                for old_index, new_index in zip_longest(
                    range(old_start, old_end), range(new_start, new_end)
                )
            )

        hunks.append(DiffHunk(group[0][1] - previous_end, tuple(rows)))
        previous_end = group[-1][2]

    changed = [row for hunk in hunks for row in hunk.rows if row.changed]
    notes = _notes(
        [] if annotations is None else annotations,
        hunks,
        numbering,
        (len(old), len(new)),
    )
    return PreparedDiff(
        tuple(hunks),
        numbering,
        notes,
        len(old) - previous_end,
        sum(row.before is not None for row in changed),
        sum(row.after is not None for row in changed),
    )


def unified_rows(rows: tuple[DiffRow, ...]) -> tuple[DiffRow, ...]:
    """Reorder side-by-side rows into single-column reading order.

    Args:
        rows: Rows of one hunk, as produced by prepare_diff.

    Returns:
        Unchanged rows as given. Each run of changed rows becomes its removals
        followed by its additions, with one line per row.
    """
    result: list[DiffRow] = []
    for changed, run in groupby(rows, key=lambda row: row.changed):
        group = tuple(run)
        if not changed:
            result.extend(group)
            continue

        # List every removal in a change before any of its additions.
        result.extend(
            DiffRow(row.before, None, True) for row in group if row.before is not None
        )
        result.extend(
            DiffRow(None, row.after, True) for row in group if row.after is not None
        )

    return tuple(result)
