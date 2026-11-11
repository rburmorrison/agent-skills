"""Prepare numbered source and validated annotations without performing I/O."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from code_highlighting import HighlightedCode


RANGE_PALETTE_SIZE = 6


@dataclass(frozen=True)
class SourceRange:
    """Inclusive one-based source bounds identifying one referenced region."""

    start: int
    """First referenced source line."""
    end: int
    """Last referenced source line."""


@dataclass(frozen=True)
class CodeAnnotation:
    """Explanatory content located outside the copyable source."""

    text: str
    """Required nonblank text accepting the renderer's safe inline vocabulary."""
    title: str
    """Optional title accepting inline formatting; empty means no title."""
    lines: SourceRange | None = None
    """Referenced region independent of placement; None means a general note."""


@dataclass(frozen=True)
class PreparedCodeBlock:
    """Highlighted source and annotations grouped in stable input order."""

    source: HighlightedCode
    """Whole-source highlighting split into independently renderable lines."""
    annotations: dict[str | int, list[CodeAnnotation]]
    """Notes keyed by top, bottom, or a one-based source line to follow."""
    ranges: dict[SourceRange, int]
    """Unique regions mapped to indices in start-line order, with input-order ties."""
    line_ranges: tuple[tuple[int, ...], ...]
    """Range indices covering each source line in source order, earliest first."""


def _source_range(value: object, line_count: int, label: str) -> SourceRange:
    # Accept exactly one integer line or a two-integer inclusive range.
    if type(value) is int:
        bounds = [value, value]
    elif isinstance(value, list):
        values = cast("list[object]", value)
        if len(values) != 2 or any(type(bound) is not int for bound in values):
            raise ValueError(label + " lines must be an integer or [start, end]")
        bounds = cast("list[int]", values)
    else:
        raise ValueError(label + " lines must be an integer or [start, end]")

    # Reject reversed and out-of-range bounds instead of changing their meaning.
    start, end = bounds
    if not 1 <= start <= end <= line_count:
        raise ValueError(
            f"{label} lines must satisfy 1 <= start <= end <= {line_count}"
        )
    return SourceRange(start, end)


def _line_ranges(
    ranges: dict[SourceRange, int], line_count: int
) -> tuple[tuple[int, ...], ...]:
    # Index range boundaries once instead of rescanning every range for each line.
    starts: dict[int, list[int]] = {}
    ends: dict[int, list[int]] = {}
    for bounds, index in ranges.items():
        starts.setdefault(bounds.start, []).append(index)
        ends.setdefault(bounds.end + 1, []).append(index)

    # Keep active ranges in their start/input order as the source is traversed.
    active: dict[int, None] = {}
    result: list[tuple[int, ...]] = []
    for number in range(1, line_count + 1):
        for index in ends.get(number, []):
            del active[index]
        for index in starts.get(number, []):
            active[index] = None
        result.append(tuple(active))

    return tuple(result)


def prepare_code_block(
    source: HighlightedCode, annotations: object
) -> PreparedCodeBlock:
    """Validate and group annotations for already highlighted source.

    Args:
        source: Highlighted source with one or more addressable lines.
        annotations: JSON list of objects with required nonblank string text,
            optional string title, and position defaulting to top. Position is
            top, bottom, or an integer source line in 1..line_count. Booleans,
            unknown fields, and invalid field types are rejected. Optional lines
            is one integer or [start, end] within the source, independent of
            position; omission makes a general note.

    Returns:
        Numbered-line input and grouped notes; notes at each position retain
        their original list order. Identical referenced ranges share an index;
        indices follow start-line order with original input order breaking ties.
        Empty source has one addressable blank line.

    Raises:
        ValueError: Annotation input is malformed or its line is out of range.
    """
    # Require a list before validating individual notes.
    if not isinstance(annotations, list):
        raise ValueError("Code annotations must be a list")

    # Validate each complete annotation before adding it to its placement group.
    grouped: dict[str | int, list[CodeAnnotation]] = {}
    distinct_ranges: dict[SourceRange, None] = {}
    for index, raw in enumerate(cast("list[object]", annotations), 1):
        label = f"Code annotation {index}"
        if not isinstance(raw, dict):
            raise ValueError(label + " must be an object")
        fields = cast("dict[str, object]", raw)
        if fields.keys() - {"text", "title", "position", "lines"}:
            raise ValueError(label + " accepts only text, title, position, and lines")
        content = fields.get("text")
        title = fields.get("title", "")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(label + " text must be a nonblank string")
        if not isinstance(title, str):
            raise ValueError(label + " title must be a string")

        # Reject bad positions rather than silently moving a note to other code.
        position = fields.get("position", "top")
        if type(position) is int:
            if not 1 <= position <= len(source.lines):
                raise ValueError(
                    f"{label} position must be between 1 and {len(source.lines)}"
                )
        elif not isinstance(position, str) or position not in ("top", "bottom"):
            raise ValueError(label + " position must be top, bottom, or a source line")

        # Resolve referenced source separately from the note's display position.
        lines = (
            _source_range(fields["lines"], len(source.lines), label)
            if "lines" in fields
            else None
        )
        if lines is not None:
            distinct_ranges[lines] = None
        grouped.setdefault(position, []).append(CodeAnnotation(content, title, lines))

    # Assign stable source-order identities and record every overlapping range.
    ordered = sorted(distinct_ranges, key=lambda bounds: bounds.start)
    ranges = {bounds: index for index, bounds in enumerate(ordered)}
    return PreparedCodeBlock(
        source, grouped, ranges, _line_ranges(ranges, len(source.lines))
    )
