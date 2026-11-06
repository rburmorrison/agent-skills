"""Input field contracts for document variants and internal sequence geometry.

Fields describe the values consumed by each operation. JSON and mapping callers
remain subject to the renderer's existing runtime checks; these types do not
validate input or authorize executable custom content.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, TypedDict

if TYPE_CHECKING:
    from diagram_layout import GraphEdge, GraphNode, Point, PositionedLabel


class _DocumentTitle(TypedDict):
    title: str


class Document(_DocumentTitle, total=False):
    """A titled document with optional sections, assets, and presentation settings."""

    lang: str
    theme: str
    description: str
    brand: str
    lead: str
    intro: list[object]
    sections: list[Section]
    styles: list[str]
    scripts: list[str]


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


class CodeBlock(TextBlock, total=False):
    """Literal code with optional language and ID."""

    id: str
    language: str


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


class EquationBlock(TextBlock, total=False):
    """Equation text with optional accessible label and caption."""

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
    """Range or choice control fields with a visible label."""

    id: str
    min: float
    max: float
    value: float
    step: float
    options: list[ChoiceOption]


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


class ChoiceBlock(TypedDict):
    """Required options for a choice control."""

    options: list[ChoiceOption]
