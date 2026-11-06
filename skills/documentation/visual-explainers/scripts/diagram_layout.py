"""Deterministic diagram geometry, measured with the bundled offline font."""

from __future__ import annotations

import bisect
import struct
from typing import TYPE_CHECKING, Tuple, TypedDict

if TYPE_CHECKING:
    from pathlib import Path

Point = Tuple[float, float]


class GraphNode(TypedDict):
    """A graph node's identifier and display label."""

    id: str
    label: str


_GraphEdgeEndpoints = TypedDict("_GraphEdgeEndpoints", {"from": str, "to": str})


class GraphEdge(_GraphEdgeEndpoints, total=False):
    """Directed endpoints with an optional display label."""

    label: str


class LabelGeometry(TypedDict):
    """Measured label lines, padded dimensions, and font size."""

    lines: list[str]
    width: float
    height: float
    size: float


class PositionedLabel(LabelGeometry):
    """A measured label placed at its upper left corner."""

    x: float
    y: float


class PlacedNode(TypedDict):
    """Node bounds and wrapped label lines in diagram coordinates."""

    id: str
    x: float
    y: float
    width: float
    height: float
    lines: list[str]


class EdgeRoute(TypedDict):
    """An orthogonal path and its optional positioned label."""

    points: list[Point]
    label: PositionedLabel | None
    edge: GraphEdge


class GraphLayout(TypedDict):
    """Placed nodes and routes inside the diagram's outer bounds."""

    nodes: list[PlacedNode]
    edges: list[EdgeRoute]
    width: float
    height: float


class FontMetrics:
    """Measure text using a TrueType font with a Unicode format 4 or 12 cmap."""

    def __init__(self, path: Path) -> None:
        """Load glyph advances and the preferred Unicode character map.

        Args:
            path: TrueType font containing head, hhea, hmtx, and cmap tables.

        Raises:
            OSError: The font cannot be read.
            KeyError: A required table is absent.
            ValueError: No supported Unicode character map is present.
            struct.error: Font tables are truncated or malformed.
        """
        self.data: bytes = path.read_bytes()
        tables: dict[bytes, int] = {}
        for i in range(self.u16(4)):
            pos = 12 + i * 16
            tables[self.data[pos : pos + 4]] = self.u32(pos + 8)
        self.units: int = self.u16(tables[b"head"] + 18)
        count = self.u16(tables[b"hhea"] + 34)
        self.advances: list[int] = [
            self.u16(tables[b"hmtx"] + i * 4) for i in range(count)
        ]
        cmap = tables[b"cmap"]
        candidates: list[tuple[bool, bool, int, int]] = []
        for i in range(self.u16(cmap + 2)):
            pos = cmap + 4 + i * 8
            platform, encoding = self.u16(pos), self.u16(pos + 2)
            sub = cmap + self.u32(pos + 4)
            fmt = self.u16(sub)
            if platform in (0, 3) and fmt in (4, 12):
                candidates.append((fmt == 12, platform == 3, encoding, sub))
        if not candidates:
            raise ValueError("Bundled font has no supported Unicode character map")
        self.cmap: int = max(candidates)[-1]
        self.format: int = self.u16(self.cmap)
        if self.format == 12:
            self.groups: list[tuple[int, int, int]] = [
                struct.unpack_from(">III", self.data, self.cmap + 16 + i * 12)
                for i in range(self.u32(self.cmap + 12))
            ]
            self.ends: list[int] = [g[1] for g in self.groups]
        else:
            self.segments: int = self.u16(self.cmap + 6) // 2
            self.end_offset: int = self.cmap + 14
            self.start_offset: int = self.end_offset + self.segments * 2 + 2
            self.delta_offset: int = self.start_offset + self.segments * 2
            self.range_offset: int = self.delta_offset + self.segments * 2
            self.ends = [
                self.u16(self.end_offset + i * 2) for i in range(self.segments)
            ]

    def u16(self, offset: int) -> int:
        return struct.unpack_from(">H", self.data, offset)[0]

    def u32(self, offset: int) -> int:
        return struct.unpack_from(">I", self.data, offset)[0]

    def glyph(self, character: str) -> int:
        code = ord(character)
        i = bisect.bisect_left(self.ends, code)
        if i == len(self.ends):
            return 0
        if self.format == 12:
            start, end, glyph = self.groups[i]
            return glyph + code - start if start <= code <= end else 0
        start = self.u16(self.start_offset + i * 2)
        if code < start:
            return 0
        delta = self.u16(self.delta_offset + i * 2)
        offset = self.u16(self.range_offset + i * 2)
        if not offset:
            return (code + delta) & 0xFFFF
        glyph = self.u16(self.range_offset + i * 2 + offset + (code - start) * 2)
        return (glyph + delta) & 0xFFFF if glyph else 0

    def width(self, text: object, size: float) -> float:
        """Measure the advance width of the string representation of a value.

        Args:
            text: Value to stringify and measure; no shaping is performed.
            size: Font size in diagram units.

        Returns:
            Summed glyph advances, using one em for missing non-ASCII glyphs.
        """
        return (
            sum(
                self.units
                if not self.glyph(c) and ord(c) > 127
                else self.advances[min(self.glyph(c), len(self.advances) - 1)]
                for c in str(text)
            )
            * size
            / self.units
        )

    def wrap(self, text: object, size: float, width: float) -> list[str]:
        """Wrap a value's text into measured lines, splitting long identifiers.

        Args:
            text: Value to stringify; whitespace is normalized between words.
            size: Font size in diagram units.
            width: Maximum line width; a single glyph may exceed this value.

        Returns:
            At least one line, including an empty line for empty text.
        """
        lines: list[str] = []
        line = ""
        for token in str(text).split():
            word = token
            candidate = (line + " " + word).strip()
            if line and self.width(candidate, size) > width:
                lines.append(line)
                line = ""
            # Long identifiers must fit their reserved label lane too.
            while self.width(word, size) > width and len(word) > 1:
                cut = 1
                while cut < len(word) and self.width(word[: cut + 1], size) <= width:
                    cut += 1
                lines.append(word[:cut])
                word = word[cut:]
            line = (line + " " + word).strip()
        if line:
            lines.append(line)
        return lines or [""]


def label_geometry(
    text: object, metrics: FontMetrics, max_width: float = 180, size: float = 13
) -> LabelGeometry:
    """Measure wrapped label lines and their padded dimensions.

    Args:
        text: Label value to stringify and wrap.
        metrics: Font used to measure each line.
        max_width: Maximum text width before horizontal padding.
        size: Font size in diagram units.

    Returns:
        Lines, dimensions including padding, and the font size used.
    """
    lines = metrics.wrap(text, size, max_width)
    return {
        "lines": lines,
        "width": max(metrics.width(s, size) for s in lines) + 16,
        "height": len(lines) * 18 + 8,
        "size": size,
    }


def _graph_layers(
    nodes: list[GraphNode], edges: list[GraphEdge]
) -> tuple[dict[str, int], dict[str, list[int]], dict[str, list[int]]]:
    ids = [node["id"] for node in nodes]
    if not nodes or len(set(ids)) != len(ids):
        raise ValueError("Graph requires unique node IDs")
    incoming: dict[str, list[int]] = {ident: [] for ident in ids}
    outgoing: dict[str, list[int]] = {ident: [] for ident in ids}
    layers: dict[str, int] = {}
    for i, edge in enumerate(edges):
        if edge["from"] not in incoming or edge["to"] not in incoming:
            raise ValueError("Graph edge refers to unknown node")
        incoming[edge["to"]].append(i)
        outgoing[edge["from"]].append(i)
    pending = set(ids)
    while pending:
        ready = [
            ident
            for ident in ids
            if ident in pending
            and all(edges[i]["from"] in layers for i in incoming[ident])
        ]
        if not ready:
            raise ValueError(
                "Graph must be acyclic; use sequence or custom HTML/SVG for cycles"
            )
        for ident in ready:
            layers[ident] = max(
                [layers[edges[i]["from"]] + 1 for i in incoming[ident]] or [0]
            )
            pending.remove(ident)
    return layers, incoming, outgoing


def layout_graph(
    nodes: list[GraphNode], edges: list[GraphEdge], metrics: FontMetrics
) -> GraphLayout:
    """Place a directed acyclic graph with orthogonal routes and label lanes.

    Args:
        nodes: Nonempty list with unique IDs and short display labels.
        edges: Directed endpoints referring to those IDs, with optional labels.
        metrics: Font used to measure node and edge labels.

    Returns:
        Diagram bounds, placed nodes in input order, and routes in edge order.

    Raises:
        ValueError: IDs are duplicated, endpoints are unknown, the graph is
            empty or cyclic, or a node label needs more than three lines.
    """
    layers, incoming, outgoing = _graph_layers(nodes, edges)
    depth = max(layers.values()) + 1
    labels: list[LabelGeometry | None] = [
        label_geometry(
            e.get("label"),
            metrics,
            132 if layers[e["to"]] == layers[e["from"]] + 1 else 260,
            14,
        )
        if e.get("label")
        else None
        for e in edges
    ]
    adjacent: dict[int, list[int]] = {i: [] for i in range(depth - 1)}
    skipped: list[int] = []
    for i, edge in enumerate(edges):
        a, b = layers[edge["from"]], layers[edge["to"]]
        if b == a + 1:
            adjacent[a].append(i)
        else:
            skipped.append(i)
    side_band = 14 + len(edges) * 3
    gaps = [
        max(
            72,
            max(
                [label["width"] for i in adjacent[layer] if (label := labels[i])] or [0]
            )
            + side_band * 2
            + 16,
        )
        for layer in range(depth - 1)
    ]
    node_w = max(132, min(176, max(metrics.width(n["label"], 14) + 28 for n in nodes)))
    node_h, margin = 76, 24
    xs: list[float] = [margin]
    for gap in gaps:
        xs.append(xs[-1] + node_w + gap)
    top_tracks: dict[int, float] = {}
    top: float = 20
    for i in skipped:
        label = labels[i]
        height = label["height"] if label else 0
        top_tracks[i] = top + height + 8
        top += height + 26
    top += 20
    lane_pitch = max([lab["height"] + 24 for lab in labels if lab] or [52])
    body_h = max(
        max(list(layers.values()).count(layer) for layer in range(depth)) * 110,
        max([len(v) for v in adjacent.values()] or [0]) * lane_pitch + 44,
    )
    placed: dict[str, PlacedNode] = {}
    rows: dict[int, int] = {}
    for node in nodes:
        ident = node["id"]
        layer = layers[ident]
        row = rows.get(layer, 0)
        rows[layer] = row + 1
        count = list(layers.values()).count(layer)
        lines = metrics.wrap(node.get("label"), 14, node_w - 24)
        if len(lines) > 3:
            raise ValueError(
                "Graph labels must fit three short lines; move detail into surrounding prose"
            )
        placed[ident] = {
            "id": ident,
            "x": xs[layer],
            "y": top + (row + 0.5) * body_h / count - node_h / 2,
            "width": node_w,
            "height": node_h,
            "lines": lines,
        }

    def port(node: PlacedNode, index: int, group: list[int], right: bool) -> Point:
        rank = group.index(index)
        adjacent_ports = [
            i for i in group if layers[edges[i]["to"]] == layers[edges[i]["from"]] + 1
        ]
        if len(adjacent_ports) == 1 and index in adjacent_ports:
            y = node["y"] + node_h / 2
        elif len(group) == 2 and len(adjacent_ports) == 1:
            y = node["y"] + node_h * 0.75
        else:
            y = node["y"] + 18 + (rank + 1) * (node_h - 36) / (len(group) + 1)
        return (node["x"] + (node_w if right else 0), y)

    routes: list[EdgeRoute] = []
    for i, edge in enumerate(edges):
        source, target = placed[edge["from"]], placed[edge["to"]]
        start = port(source, i, outgoing[edge["from"]], True)
        end = port(target, i, incoming[edge["to"]], False)
        # All vertical segments live in gutters, never in a node column.
        exit_x = start[0] + 10 + i * 3
        entry_x = end[0] - 10 - i * 3
        if i in top_tracks:
            lane_y = top_tracks[i]
        else:
            group = adjacent[layers[edge["from"]]]
            lane_y = (
                (start[1] + end[1]) / 2
                if len(group) == 1
                else top + 32 + group.index(i) * lane_pitch + lane_pitch / 2
            )
        points = [
            start,
            (exit_x, start[1]),
            (exit_x, lane_y),
            (entry_x, lane_y),
            (entry_x, end[1]),
            end,
        ]
        measured_label = labels[i]
        positioned_label: PositionedLabel | None = None
        if measured_label:
            positioned_label = {
                **measured_label,
                "x": (exit_x + entry_x) / 2 - measured_label["width"] / 2,
                "y": lane_y - measured_label["height"] - 7,
            }
        routes.append({"points": points, "label": positioned_label, "edge": edge})
    return {
        "nodes": list(placed.values()),
        "edges": routes,
        "width": xs[-1] + node_w + margin,
        "height": top + body_h + 24,
    }


def rounded_path(points: list[Point], radius: float = 7) -> str:
    """Convert orthogonal route points into a rounded SVG path.

    Args:
        points: Nonempty route; consecutive duplicate points are removed.
        radius: Maximum corner radius, limited by adjacent segment lengths.

    Returns:
        SVG path data with coordinates rounded to two decimal places.
    """

    def point(p: Point) -> str:
        return f"{p[0]:.2f} {p[1]:.2f}"

    # Remove coincident segments before rounding corners.
    clean = [points[0]]
    for p in points[1:]:
        if p != clean[-1]:
            clean.append(p)
    result = "M" + point(clean[0])
    for i in range(1, len(clean) - 1):
        a, b, c = clean[i - 1 : i + 2]
        ab = abs(a[0] - b[0]) + abs(a[1] - b[1])
        bc = abs(b[0] - c[0]) + abs(b[1] - c[1])
        distance = min(radius, ab / 2, bc / 2)
        before = (
            b[0] + (a[0] - b[0]) * distance / ab,
            b[1] + (a[1] - b[1]) * distance / ab,
        )
        after = (
            b[0] + (c[0] - b[0]) * distance / bc,
            b[1] + (c[1] - b[1]) * distance / bc,
        )
        result += "L" + point(before) + "Q" + point(b) + " " + point(after)
    return result + "L" + point(clean[-1])
