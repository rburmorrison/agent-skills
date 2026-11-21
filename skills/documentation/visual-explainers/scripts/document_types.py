"""Input field contracts for document variants and internal sequence geometry.

Fields describe the values consumed by each operation. check_fields validates
an input mapping's required fields, and its top-level list, object, and number
fields, against these declarations; the renderer checks nested values. The
types do not authorize executable custom content.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import TYPE_CHECKING, ForwardRef, TypedDict, cast

if TYPE_CHECKING:
    from diagram_layout import GraphEdge, GraphNode, Point, PositionedLabel

# Annotation names checked at runtime, with the accepted Python types and a reader-facing name.
# Strings, integers, and booleans stay unchecked: the renderer stringifies or tests their
# truthiness, so values such as a numeric title or "ordered": 1 have always rendered.
_RUNTIME_TYPES: dict[str, tuple[tuple[type, ...], str]] = {
    "float": ((int, float), "a finite number"),
    "list": ((list,), "a list"),
    "Mapping": ((Mapping,), "an object"),
}


def _expectation(annotation: str) -> tuple[tuple[type, ...], str] | None:
    """Resolve a field annotation to the runtime types it accepts.

    Args:
        annotation: Annotation source text, such as "float", "list[Metric]", or "str | int".

    Returns:
        Accepted types and a description, or None for annotations that are not
        checked at the top level, such as str, object, or another TypedDict.
    """

    # Combine union members, leaving the union unchecked if any member is.
    parts = [part.strip().split("[", 1)[0] for part in annotation.split("|")]
    resolved = [_RUNTIME_TYPES.get(part) for part in parts]
    if any(item is None for item in resolved):
        return None

    # Merge the accepted types and describe the alternatives in order.
    accepted = tuple(t for item in resolved if item for t in item[0])
    return accepted, " or ".join(item[1] for item in resolved if item)


def check_fields(values: object, spec: type, label: str) -> None:
    """Check a mapping's required fields and its list, object, and number fields.

    Args:
        values: Input value expected to be a mapping.
        spec: TypedDict declaring the fields.
        label: Reader-facing name of the value, such as "table block".

    Raises:
        ValueError: The value is not a mapping, a required field is missing,
            or a declared list, object, or number field has the wrong type or
            is not finite.
    """

    # Require a mapping before inspecting its fields.
    if not isinstance(values, Mapping):
        raise ValueError(f"{label} must be an object")

    fields = cast("Mapping[str, object]", values)
    annotations: dict[str, ForwardRef | str] = spec.__annotations__
    required: frozenset[str] = getattr(spec, "__required_keys__", frozenset())

    # Report the first missing required field in declaration order.
    for name in annotations:
        if name in required and name not in fields:
            raise ValueError(f"{label} requires field '{name}'")

    # Check each present field against its declared top-level type.
    for name, annotation in annotations.items():
        if name not in fields:
            continue
        source = (
            annotation.__forward_arg__
            if isinstance(annotation, ForwardRef)
            else str(annotation)
        )
        expectation = _expectation(source)
        value = fields[name]
        if expectation is None:
            continue

        # Treat booleans as distinct from numbers, as JSON does.
        accepted, description = expectation
        mistyped = not isinstance(value, accepted) or (
            isinstance(value, bool) and bool not in accepted
        )
        nonfinite = isinstance(value, float) and not math.isfinite(value)
        if mistyped or nonfinite:
            raise ValueError(f"{label} field '{name}' must be {description}")


class _DocumentTitle(TypedDict):
    title: str


class Document(_DocumentTitle, total=False):
    """A titled document with optional sections, assets, and presentation settings."""

    lang: str
    theme: str
    """Theme set selected at generation time; defaults to plain."""
    accent: str | AccentPair
    """Accent preset of the selected theme set, or a custom pair; defaults to the set's preset."""
    description: str
    brand: str
    lead: str
    intro: list[object]
    sections: list[Section]
    styles: list[str]
    scripts: list[str]


class AccentPair(TypedDict):
    """Custom accent colors that must keep 4.5:1 contrast with the theme's surfaces."""

    light: str
    """Light-appearance accent as `#rrggbb`."""
    dark: str
    """Dark-appearance accent as `#rrggbb`."""


class _SectionContent(TypedDict):
    title: str
    blocks: list[object]


class Section(_SectionContent, total=False):
    """Section heading and blocks, with an optional explicit heading ID."""

    id: str


class TextBlock(TypedDict):
    """Inline text content."""

    text: object


class HeadingBlock(TextBlock, total=False):
    """Text with an optional nested heading level."""

    level: int


class _ListItems(TypedDict):
    items: list[object]


class ListBlock(_ListItems, total=False):
    """Items with an optional ordered-list presentation."""

    ordered: bool


class AlertBlock(TypedDict, total=False):
    """Alert styling and either nested blocks or text content."""

    kind: str
    title: str
    text: object
    blocks: list[object]


class _CodeAnnotationText(TypedDict):
    text: str
    """Nonblank explanatory text accepting safe inline formatting."""


class CodeAnnotation(_CodeAnnotationText, total=False):
    """One note positioned outside the copyable source."""

    title: str
    """Optional title accepting safe inline formatting."""
    lines: int | list[int]
    """One numbered line or inclusive [start, end]; independent of position, omitted for general notes."""
    position: str | int
    """Top (default), bottom, or a numbered source line to follow."""


class CodeBlock(TextBlock, total=False):
    """Numbered literal code with optional language, title, annotations, and ID."""

    id: str
    language: str
    title: str
    """Bar label, such as a file path; defaults to the language."""
    start: int
    """Number of the first source line; defaults to 1."""
    annotations: list[CodeAnnotation]
    """Notes in input order within each placement; invalid input is rejected."""


class DiffAnnotation(_CodeAnnotationText, total=False):
    """One note shown between diff rows."""

    title: str
    """Optional title accepting safe inline formatting."""
    lines: int | list[int]
    """One numbered line or inclusive [start, end] of the version named by side."""
    side: str
    """Version the lines belong to: before or after (default)."""
    position: str
    """Top or bottom; defaults to after the last referenced line, or top without lines."""


class _DiffVersions(TypedDict):
    before: str
    """Earlier source; empty for a newly added file."""
    after: str
    """Later source; empty for a removed file."""


class DiffBlock(_DiffVersions, total=False):
    """Two versions of one source compared line by line, with a layout toggle."""

    id: str
    language: str
    """Bundled lexer name or alias used to highlight both versions."""
    title: str
    """Bar label, such as a file path; defaults to the language."""
    view: str
    """Initial layout: unified (default) or split."""
    context: int
    """Unchanged lines kept around each change; defaults to 3."""
    before_start: int
    """Line number of the first earlier line; defaults to 1."""
    after_start: int
    """Line number of the first later line; defaults to 1."""
    annotations: list[DiffAnnotation]
    """Notes in input order within each placement; invalid input is rejected."""


class _TableContent(TypedDict):
    headers: list[object]
    rows: list[list[object]]


class TableBlock(_TableContent, total=False):
    """Headers and equally sized rows, with an optional caption."""

    caption: object


class ImageBlock(TypedDict, total=False):
    """An accessible image source or local file and optional caption."""

    alt: str
    src: str
    file: str
    caption: object


class DisclosureBlock(_SectionContent, total=False):
    """Titled expandable blocks with an optional initial open state."""

    open: bool


class ColumnsBlock(TypedDict):
    """One to three columns containing nested blocks."""

    columns: list[list[object]]


class _BlocksContent(TypedDict):
    blocks: list[object]


class CardBlock(_BlocksContent, total=False):
    """Nested blocks with an optional title and icon."""

    title: object
    icon: str


class _MetricContent(TypedDict):
    value: object
    label: object


class Metric(_MetricContent, total=False):
    """A display value and label, with optional icon and detail."""

    icon: str
    detail: object


class MetricsBlock(TypedDict):
    """A collection of display metrics."""

    items: list[Metric]


class _TabsContent(TypedDict):
    tabs: list[_SectionContent]


class TabsBlock(_TabsContent, total=False):
    """Nonempty titled panels with optional group label and ID."""

    id: str
    label: str


class _TimelineContent(TypedDict):
    title: object
    text: object


class TimelineItem(_TimelineContent, total=False):
    """An event title and text, with an optional time label."""

    label: object


class TimelineBlock(TypedDict):
    """Timeline events in display order."""

    items: list[TimelineItem]


class EquationBlock(TypedDict, total=False):
    """Exactly one of text or MathML; MathML requires a nonempty string label."""

    text: object
    mathml: str
    label: object
    caption: object


class ChoiceOption(TypedDict):
    """A selectable value and its display label."""

    value: object
    label: object


class _ControlContent(TypedDict):
    type: str
    label: object


class ControlBlock(_ControlContent, total=False):
    """Fields shared by range and choice controls."""

    id: str


class RangeBlock(ControlBlock, total=False):
    """A numeric slider; bounds default to 0 through 100 and step to 1."""

    min: float
    max: float
    value: float
    step: float


class _ChoiceOptions(TypedDict):
    options: list[ChoiceOption]


class ChoiceBlock(_ChoiceOptions, ControlBlock, total=False):
    """A select control whose value matches one option's value."""

    value: object


class HtmlBlock(TypedDict, total=False):
    """Custom markup from a local file or inline HTML."""

    file: str
    html: str


class Diagram(TypedDict, total=False):
    """Shared diagram presentation options."""

    kind: str
    title: str
    caption: object


class _FlowNodeLabel(TypedDict):
    label: object


class FlowNode(_FlowNodeLabel, total=False):
    """A labeled flow step with optional icon and description."""

    icon: str
    text: object


class FlowDiagram(Diagram):
    """Ordered nodes in a flow diagram."""

    nodes: list[FlowNode]


class _GraphNodes(TypedDict):
    nodes: list[GraphNode]


class GraphDiagram(_GraphNodes, total=False):
    """Directed graph nodes, edges, and optional title."""

    title: str
    edges: list[GraphEdge]


SequenceMessage = TypedDict("SequenceMessage", {"from": int, "to": int, "label": str})


class _SequenceContent(TypedDict):
    actors: list[str]
    messages: list[SequenceMessage]


class SequenceDiagram(_SequenceContent, total=False):
    """Actors and ordered messages with an optional title."""

    title: str


class SequenceRow(TypedDict):
    """A positioned message label and its arrow route."""

    label: PositionedLabel
    points: list[Point]


class _ChartContent(TypedDict):
    kind: str
    title: str
    data: Mapping[str, object]


class Chart(_ChartContent, total=False):
    """A chart kind, title, data, and optional display settings."""

    id: str
    caption: object
    xLabel: str
    yLabel: str
    unit: str
    xUnit: str
    binUnit: str
    xMax: float
    xMin: float
    yMax: float
    yMin: float
    pointPrefix: str
    selectedIndex: int
    valueLabel: str


class Series(TypedDict):
    """A named numeric series aligned with category labels."""

    name: str
    values: list[float]


class SeriesData(TypedDict):
    """Category labels and corresponding named numeric series."""

    categories: list[str]
    series: list[Series]


class CategoryData(TypedDict):
    """Category labels with a corresponding numeric value for each."""

    categories: list[str]
    values: list[float]


class ScatterPoint(TypedDict):
    """A labeled observation with numeric coordinates."""

    x: float
    y: float
    label: str


class ScatterData(TypedDict):
    """Scatter observations in display order."""

    points: list[ScatterPoint]


class HistogramBin(TypedDict):
    """A numeric interval and its observation count."""

    low: float
    high: float
    count: float


class HistogramData(TypedDict):
    """Ordered bins for a contiguous, equal-width histogram."""

    bins: list[HistogramBin]


class HeatmapData(TypedDict):
    """Row and column labels with their numeric matrix."""

    rows: list[str]
    columns: list[str]
    values: list[list[float]]


class BoxGroup(TypedDict):
    """A named five-number summary."""

    name: str
    min: float
    q1: float
    median: float
    q3: float
    max: float


class BoxData(TypedDict):
    """Five-number summaries in display order."""

    groups: list[BoxGroup]


class FileAsset(TypedDict):
    """A required local file reference."""

    file: str


class InlineHtml(TypedDict):
    """Required inline custom markup."""

    html: str
