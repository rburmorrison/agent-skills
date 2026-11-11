"""Geometry contracts for the actual offline diagram builder."""

from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from diagram_layout import (
    FontMetrics,
    GraphEdge,
    GraphLayout,
    GraphNode,
    PlacedNode,
    Point,
    layout_graph,
    rounded_path,
)

SKILL = Path(__file__).resolve().parents[1]


class Bounds(TypedDict):
    x: float
    y: float
    width: float
    height: float


def overlaps(a: Bounds, b: Bounds) -> bool:
    return (
        a["x"] < b["x"] + b["width"] - 0.001
        and b["x"] < a["x"] + a["width"] - 0.001
        and a["y"] < b["y"] + b["height"] - 0.001
        and b["y"] < a["y"] + a["height"] - 0.001
    )


def segment_enters_node(a: Point, b: Point, node: PlacedNode) -> bool:
    # Inset the node bounds to allow routes along its border.
    left, right = node["x"] + 0.001, node["x"] + node["width"] - 0.001
    top, bottom = node["y"] + 0.001, node["y"] + node["height"] - 0.001

    # Check intersections for vertical and horizontal segments.
    if a[0] == b[0]:
        return left < a[0] < right and max(min(a[1], b[1]), top) < min(
            max(a[1], b[1]), bottom
        )

    if a[1] == b[1]:
        return top < a[1] < bottom and max(min(a[0], b[0]), left) < min(
            max(a[0], b[0]), right
        )

    # Reject diagonal routes because the geometry contract is orthogonal.
    raise AssertionError("A routed segment is not orthogonal")


class DiagramGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.font: FontMetrics = FontMetrics(SKILL / "assets/fonts/Manrope.ttf")

    def assert_clear(
        self, nodes: list[GraphNode], edges: list[GraphEdge]
    ) -> GraphLayout:
        # Lay out the graph and collect its measured edge labels.
        layout = layout_graph(nodes, edges, self.font)
        labels = [r["label"] for r in layout["edges"] if r["label"]]

        # Verify label bounds, node clearance, and measured text widths.
        for label in labels:
            self.assertTrue(
                0 <= label["x"] < label["x"] + label["width"] <= layout["width"]
            )
            self.assertTrue(
                0 <= label["y"] < label["y"] + label["height"] <= layout["height"]
            )

            # Verify that the label clears every node.
            for node in layout["nodes"]:
                self.assertFalse(overlaps(label, node), (label, node))

            # Verify each wrapped line fits inside the padded label.
            for line in label["lines"]:
                self.assertLessEqual(
                    self.font.width(line, label["size"]), label["width"] - 15.9
                )

        # Verify that edge labels do not overlap one another.
        for i, label in enumerate(labels):
            for other in labels[i + 1 :]:
                self.assertFalse(overlaps(label, other), (label, other))

        # Verify path serialization and route clearance from every node.
        for route in layout["edges"]:
            self.assertTrue(rounded_path(route["points"]).startswith("M"))

            # Verify that each orthogonal route segment clears every node.
            for a, b in zip(route["points"], route["points"][1:]):
                for node in layout["nodes"]:
                    self.assertFalse(segment_enters_node(a, b, node), (route, node))

        return layout

    def test_connection_error_bypasses_middle_node(self) -> None:
        # Compose adjacent connections and a labeled bypass edge.
        nodes: list[GraphNode] = [
            {"id": i, "label": i.title()} for i in ("request", "validate", "result")
        ]
        edges: list[GraphEdge] = [
            {"from": "request", "to": "validate", "label": "Ready"},
            {"from": "validate", "to": "result", "label": "Valid"},
            {"from": "request", "to": "result", "label": "Connection error"},
        ]

        # Lay out the graph and verify shared clearance invariants.
        layout = self.assert_clear(nodes, edges)

        # Verify that single adjacent connections align with node centers.
        for route in layout["edges"][:2]:
            self.assertEqual(
                1,
                len({point[1] for point in route["points"]}),
                "Single adjacent connections should align with node centers",
            )

        # Verify that the bypass label stays above all graph nodes.
        bypass = layout["edges"][2]
        label = bypass["label"]
        if label is None:
            self.fail("The labeled bypass must retain its measured label")

        self.assertLess(
            label["y"] + label["height"],
            min(n["y"] for n in layout["nodes"]),
        )

    def test_asymmetric_branching_and_long_identifiers(self) -> None:
        # Compose asymmetric branches with long and unbroken labels.
        nodes: list[GraphNode] = [
            {"id": str(i), "label": "Stage " + str(i)} for i in range(7)
        ]
        edges: list[GraphEdge] = [
            {"from": str(a), "to": str(b), "label": label}
            for a, b, label in [
                (0, 1, "Request payload"),
                (0, 2, "Authentication"),
                (0, 3, "ConnectionErrorWithoutWhitespace" * 2),
                (1, 4, "Successful validation"),
                (2, 4, "Identity accepted"),
                (3, 5, "Upstream unavailable"),
                (4, 6, "Response"),
                (0, 6, "Connection error: request timed out"),
            ]
        ]

        # Verify that measured labels and routes retain their reserved space.
        _ = self.assert_clear(nodes, edges)

    def test_many_small_dags_keep_labels_and_paths_outside_nodes(self) -> None:
        # Seed graph generation for reproducible geometry coverage.
        randomizer = random.Random(17)

        # Exercise multiple graph sizes and branching patterns.
        for count in range(2, 10):
            for case in range(8):
                # Create an adjacent chain for this graph size.
                nodes: list[GraphNode] = [
                    {"id": str(i), "label": "Stage " + str(i)} for i in range(count)
                ]
                edges: list[GraphEdge] = [
                    {"from": str(i), "to": str(i + 1), "label": "Continue"}
                    for i in range(count - 1)
                ]

                # Add reproducible bypass edges with measured labels.
                skipped_edges: list[GraphEdge] = [
                    {
                        "from": str(a),
                        "to": str(b),
                        "label": "Connection error " + str(a),
                    }
                    for a in range(count)
                    for b in range(a + 2, count)
                    if randomizer.random() < 0.3
                ]
                edges.extend(skipped_edges)

                # Verify clearance for the complete generated graph.
                with self.subTest(nodes=count, case=case):
                    _ = self.assert_clear(nodes, edges)

    def test_cycles_and_unknown_nodes_are_rejected(self) -> None:
        # Compose a cycle and an edge with an unknown endpoint.
        nodes: list[GraphNode] = [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}]
        invalid_edges: list[list[GraphEdge]] = [
            [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}],
            [{"from": "a", "to": "missing"}],
        ]

        # Verify that neither invalid graph can be laid out.
        for edges in invalid_edges:
            with self.assertRaises(ValueError):
                _ = layout_graph(nodes, edges, self.font)

    def test_font_metrics_wrap_wide_and_unicode_labels(self) -> None:
        for text in [
            "WWW Connection Error WWW",
            "ConnectionErrorWithoutWhitespace",
            "连接错误\uff1a请求超时",
            "Διαδρομή σφάλματος",
        ]:
            # Wrap the label using the bundled font metrics.
            lines = self.font.wrap(text, 13, 120)

            # Verify that wrapping preserves text and respects the line width.
            self.assertEqual("".join(text.split()), "".join("".join(lines).split()))

            for line in lines:
                self.assertLessEqual(self.font.width(line, 13), 120)


if __name__ == "__main__":
    _ = unittest.main()
