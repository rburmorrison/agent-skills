"""Deterministic diagram geometry, measured with the bundled offline font."""
import bisect
import struct


class FontMetrics:
    def __init__(self, path):
        self.data = path.read_bytes()
        tables = {}
        for i in range(self.u16(4)):
            pos = 12 + i * 16
            tables[self.data[pos:pos + 4]] = self.u32(pos + 8)
        self.units = self.u16(tables[b'head'] + 18)
        count = self.u16(tables[b'hhea'] + 34)
        self.advances = [self.u16(tables[b'hmtx'] + i * 4) for i in range(count)]
        cmap = tables[b'cmap']
        candidates = []
        for i in range(self.u16(cmap + 2)):
            pos = cmap + 4 + i * 8
            platform, encoding = self.u16(pos), self.u16(pos + 2)
            sub = cmap + self.u32(pos + 4)
            fmt = self.u16(sub)
            if platform in (0, 3) and fmt in (4, 12):
                candidates.append((fmt == 12, platform == 3, encoding, sub))
        if not candidates:
            raise ValueError('Bundled font has no supported Unicode character map')
        self.cmap = max(candidates)[-1]
        self.format = self.u16(self.cmap)
        if self.format == 12:
            self.groups = [struct.unpack_from('>III', self.data, self.cmap + 16 + i * 12)
                           for i in range(self.u32(self.cmap + 12))]
            self.ends = [g[1] for g in self.groups]
        else:
            self.segments = self.u16(self.cmap + 6) // 2
            self.end_offset = self.cmap + 14
            self.start_offset = self.end_offset + self.segments * 2 + 2
            self.delta_offset = self.start_offset + self.segments * 2
            self.range_offset = self.delta_offset + self.segments * 2
            self.ends = [self.u16(self.end_offset + i * 2) for i in range(self.segments)]

    def u16(self, offset):
        return struct.unpack_from('>H', self.data, offset)[0]

    def u32(self, offset):
        return struct.unpack_from('>I', self.data, offset)[0]

    def glyph(self, character):
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
            return (code + delta) & 0xffff
        glyph = self.u16(self.range_offset + i * 2 + offset + (code - start) * 2)
        return (glyph + delta) & 0xffff if glyph else 0

    def width(self, text, size):
        return sum(self.units if not self.glyph(c) and ord(c)>127 else
                   self.advances[min(self.glyph(c), len(self.advances) - 1)]
                   for c in str(text)) * size / self.units

    def wrap(self, text, size, width):
        lines, line = [], ''
        for word in str(text).split():
            candidate = (line + ' ' + word).strip()
            if line and self.width(candidate, size) > width:
                lines.append(line)
                line = ''
            # Long identifiers must fit their reserved label lane too.
            while self.width(word, size) > width and len(word) > 1:
                cut = 1
                while cut < len(word) and self.width(word[:cut + 1], size) <= width:
                    cut += 1
                lines.append(word[:cut])
                word = word[cut:]
            line = (line + ' ' + word).strip()
        if line:
            lines.append(line)
        return lines or ['']


def label_geometry(text, metrics, max_width=180, size=13):
    lines = metrics.wrap(text, size, max_width)
    return dict(lines=lines, width=max(metrics.width(s, size) for s in lines) + 16,
                height=len(lines) * 18 + 8, size=size)


def layout_graph(nodes, edges, metrics):
    ids = [node['id'] for node in nodes]
    if not nodes or len(set(ids)) != len(ids):
        raise ValueError('Graph requires unique node IDs')
    incoming = {ident: [] for ident in ids}
    outgoing = {ident: [] for ident in ids}
    layers = {}
    for i, edge in enumerate(edges):
        if edge['from'] not in incoming or edge['to'] not in incoming:
            raise ValueError('Graph edge refers to unknown node')
        incoming[edge['to']].append(i)
        outgoing[edge['from']].append(i)
    pending = set(ids)
    while pending:
        ready = [ident for ident in ids if ident in pending and
                 all(edges[i]['from'] in layers for i in incoming[ident])]
        if not ready:
            raise ValueError('Graph must be acyclic; use sequence or custom HTML/SVG for cycles')
        for ident in ready:
            layers[ident] = max([layers[edges[i]['from']] + 1 for i in incoming[ident]] or [0])
            pending.remove(ident)
    depth = max(layers.values()) + 1
    labels = [label_geometry(e['label'], metrics, 132 if layers[e['to']]==layers[e['from']]+1 else 260, 14) if e.get('label') else None for e in edges]
    adjacent = {i: [] for i in range(depth - 1)}
    skipped = []
    for i, edge in enumerate(edges):
        a, b = layers[edge['from']], layers[edge['to']]
        if b == a + 1:
            adjacent[a].append(i)
        else:
            skipped.append(i)
    side_band = 14 + len(edges) * 3
    gaps = [max(72, max([labels[i]['width'] for i in adjacent[l] if labels[i]] or [0])
                + side_band * 2 + 16) for l in range(depth - 1)]
    node_w = max(132, min(176, max(metrics.width(n['label'],14)+28 for n in nodes)))
    node_h, margin = 76, 24
    xs = [margin]
    for gap in gaps:
        xs.append(xs[-1] + node_w + gap)
    top_tracks, top = {}, 20
    for i in skipped:
        height = labels[i]['height'] if labels[i] else 0
        top_tracks[i] = top + height + 8
        top += height + 26
    top += 20
    lane_pitch = max([lab['height'] + 24 for lab in labels if lab] or [52])
    body_h = max(max(list(layers.values()).count(l) for l in range(depth)) * 110,
                 max([len(v) for v in adjacent.values()] or [0]) * lane_pitch + 44)
    placed, rows = {}, {}
    for node in nodes:
        ident = node['id']; layer = layers[ident]
        row = rows.get(layer, 0); rows[layer] = row + 1
        count = list(layers.values()).count(layer)
        lines = metrics.wrap(node['label'], 14, node_w - 24)
        if len(lines) > 3:
            raise ValueError('Graph labels must fit three short lines; move detail into surrounding prose')
        placed[ident] = dict(id=ident, x=xs[layer], y=top + (row + .5) * body_h / count - node_h / 2,
                             width=node_w, height=node_h, lines=lines)

    def port(node, index, group, right):
        rank = group.index(index)
        adjacent_ports = [i for i in group if layers[edges[i]['to']]==layers[edges[i]['from']]+1]
        if len(adjacent_ports)==1 and index in adjacent_ports:
            y=node['y']+node_h/2
        elif len(group)==2 and len(adjacent_ports)==1:
            y=node['y']+node_h*.75
        else:
            y=node['y']+18+(rank+1)*(node_h-36)/(len(group)+1)
        return (node['x'] + (node_w if right else 0), y)

    routes = []
    for i, edge in enumerate(edges):
        source, target = placed[edge['from']], placed[edge['to']]
        start = port(source, i, outgoing[edge['from']], True)
        end = port(target, i, incoming[edge['to']], False)
        # All vertical segments live in gutters, never in a node column.
        exit_x = start[0] + 10 + i * 3
        entry_x = end[0] - 10 - i * 3
        if i in top_tracks:
            lane_y = top_tracks[i]
        else:
            group = adjacent[layers[edge['from']]]
            lane_y = (start[1]+end[1])/2 if len(group)==1 else top + 32 + group.index(i) * lane_pitch + lane_pitch / 2
        points = [start, (exit_x, start[1]), (exit_x, lane_y),
                  (entry_x, lane_y), (entry_x, end[1]), end]
        label = None
        if labels[i]:
            label = dict(labels[i], x=(exit_x + entry_x) / 2 - labels[i]['width'] / 2,
                         y=lane_y - labels[i]['height'] - 7)
        routes.append(dict(points=points, label=label, edge=edge))
    return dict(nodes=list(placed.values()), edges=routes,
                width=xs[-1] + node_w + margin, height=top + body_h + 24)


def rounded_path(points, radius=7):
    def point(p):
        return f'{p[0]:.2f} {p[1]:.2f}'
    # Remove coincident segments before rounding corners.
    clean = [points[0]]
    for p in points[1:]:
        if p != clean[-1]:
            clean.append(p)
    result = 'M' + point(clean[0])
    for i in range(1, len(clean) - 1):
        a, b, c = clean[i - 1:i + 2]
        ab = abs(a[0] - b[0]) + abs(a[1] - b[1])
        bc = abs(b[0] - c[0]) + abs(b[1] - c[1])
        distance = min(radius, ab / 2, bc / 2)
        before = (b[0] + (a[0] - b[0]) * distance / ab,
                  b[1] + (a[1] - b[1]) * distance / ab)
        after = (b[0] + (c[0] - b[0]) * distance / bc,
                 b[1] + (c[1] - b[1]) * distance / bc)
        result += 'L' + point(before) + 'Q' + point(b) + ' ' + point(after)
    return result + 'L' + point(clean[-1])
