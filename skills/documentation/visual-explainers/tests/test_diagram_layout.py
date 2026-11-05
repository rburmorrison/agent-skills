"""Geometry contracts for the actual offline diagram builder."""
import random
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from diagram_layout import FontMetrics, layout_graph, rounded_path


def overlaps(a, b):
    return (a['x'] < b['x'] + b['width'] - .001 and
            b['x'] < a['x'] + a['width'] - .001 and
            a['y'] < b['y'] + b['height'] - .001 and
            b['y'] < a['y'] + a['height'] - .001)


def segment_enters_node(a, b, node):
    left, right = node['x'] + .001, node['x'] + node['width'] - .001
    top, bottom = node['y'] + .001, node['y'] + node['height'] - .001
    if a[0] == b[0]:
        return left < a[0] < right and max(min(a[1], b[1]), top) < min(max(a[1], b[1]), bottom)
    if a[1] == b[1]:
        return top < a[1] < bottom and max(min(a[0], b[0]), left) < min(max(a[0], b[0]), right)
    raise AssertionError('A routed segment is not orthogonal')


class DiagramGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.font = FontMetrics(SKILL / 'assets/fonts/Manrope.ttf')

    def assert_clear(self, nodes, edges):
        layout = layout_graph(nodes, edges, self.font)
        labels = [r['label'] for r in layout['edges'] if r['label']]
        for label in labels:
            self.assertTrue(0 <= label['x'] < label['x'] + label['width'] <= layout['width'])
            self.assertTrue(0 <= label['y'] < label['y'] + label['height'] <= layout['height'])
            for node in layout['nodes']:
                self.assertFalse(overlaps(label, node), (label, node))
            for line in label['lines']:
                self.assertLessEqual(self.font.width(line, label['size']), label['width'] - 15.9)
        for i, label in enumerate(labels):
            for other in labels[i + 1:]:
                self.assertFalse(overlaps(label, other), (label, other))
        for route in layout['edges']:
            self.assertTrue(rounded_path(route['points']).startswith('M'))
            for a, b in zip(route['points'], route['points'][1:]):
                for node in layout['nodes']:
                    self.assertFalse(segment_enters_node(a, b, node), (route, node))
        return layout

    def test_connection_error_bypasses_middle_node(self):
        nodes = [dict(id=i, label=i.title()) for i in ('request', 'validate', 'result')]
        edges = [{'from': 'request', 'to': 'validate', 'label': 'Ready'},
                 {'from': 'validate', 'to': 'result', 'label': 'Valid'},
                 {'from': 'request', 'to': 'result', 'label': 'Connection error'}]
        layout = self.assert_clear(nodes, edges)
        for route in layout['edges'][:2]:
            self.assertEqual(1,len({point[1] for point in route['points']}),'Single adjacent connections should align with node centers')
        bypass = layout['edges'][2]
        self.assertLess(bypass['label']['y'] + bypass['label']['height'], min(n['y'] for n in layout['nodes']))

    def test_asymmetric_branching_and_long_identifiers(self):
        nodes = [dict(id=str(i), label='Stage ' + str(i)) for i in range(7)]
        edges = [{'from': str(a), 'to': str(b), 'label': label} for a, b, label in [
            (0, 1, 'Request payload'), (0, 2, 'Authentication'),
            (0, 3, 'ConnectionErrorWithoutWhitespace' * 2),
            (1, 4, 'Successful validation'), (2, 4, 'Identity accepted'),
            (3, 5, 'Upstream unavailable'), (4, 6, 'Response'), (0, 6, 'Connection error: request timed out')]]
        self.assert_clear(nodes, edges)

    def test_many_small_dags_keep_labels_and_paths_outside_nodes(self):
        randomizer = random.Random(17)
        for count in range(2, 10):
            for case in range(8):
                nodes = [dict(id=str(i), label='Stage ' + str(i)) for i in range(count)]
                edges = [{'from': str(i), 'to': str(i + 1), 'label': 'Continue'} for i in range(count - 1)]
                edges += [{'from': str(a), 'to': str(b), 'label': 'Connection error ' + str(a)}
                          for a in range(count) for b in range(a + 2, count) if randomizer.random() < .3]
                with self.subTest(nodes=count, case=case):
                    self.assert_clear(nodes, edges)

    def test_cycles_and_unknown_nodes_are_rejected(self):
        nodes = [dict(id='a', label='A'), dict(id='b', label='B')]
        for edges in [[{'from':'a','to':'b'}, {'from':'b','to':'a'}], [{'from':'a','to':'missing'}]]:
            with self.assertRaises(ValueError):
                layout_graph(nodes, edges, self.font)

    def test_font_metrics_wrap_wide_and_unicode_labels(self):
        for text in ['WWW Connection Error WWW', 'ConnectionErrorWithoutWhitespace', '连接错误：请求超时', 'Διαδρομή σφάλματος']:
            lines = self.font.wrap(text, 13, 120)
            self.assertEqual(''.join(text.split()), ''.join(''.join(lines).split()))
            for line in lines:
                self.assertLessEqual(self.font.width(line, 13), 120)


if __name__ == '__main__':
    unittest.main()
