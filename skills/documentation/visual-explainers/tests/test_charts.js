const assert = require('node:assert/strict');

// Record drawing calls as plain objects so chart kinds run without a browser.
function fakePlot(model, config, width = 640) {
  // Build a minimal element that supports the toolkit's append calls.
  const node = (tag, attrs = {}, text) => ({
    tag,
    attrs,
    text,
    children: [],
    append(...children) {
      this.children.push(...children);
    }
  });

  // Size the plot the way the browser controller does.
  const { height, left } = model.frame(config.kind);
  const m = { l: left, r: 18, t: 32, b: 54 };
  const drawn = [];
  const marks = [];
  const plot = {
    config,
    data: config.data,
    format: model.formats('en'),
    W: width,
    H: height,
    m,
    plotW: width - m.l - m.r,
    plotH: height - m.t - m.b,
    node,
    add: (tag, attrs, text) => {
      const element = node(tag, attrs, text);
      drawn.push(element);
      return element;
    },
    mark: (element, record) => {
      marks.push({ element, record });
      return element;
    },
    overlay: () => drawn.push(node('overlay'))
  };

  // Draw the kind and return everything it produced.
  model.kinds[config.kind].draw(plot);
  return { drawn, marks };
}

const CONFIGS = {
  line: { kind: 'line', xLabel: 'Time', yLabel: 'Latency', unit: 'ms', data: { categories: ['0', '10', '20'], series: [{ name: 'Base', values: [20, 35, 27] }, { name: 'New', values: [18, 24, 22] }] } },
  area: { kind: 'area', yMin: 10, data: { categories: ['a', 'b'], series: [{ name: 'A', values: [12, 18] }, { name: 'B', values: [15, 11] }] } },
  bar: { kind: 'bar', yLabel: 'Change', unit: 'items', data: { categories: ['A', 'An extremely long category label'], values: [12, -5] } },
  histogram: { kind: 'histogram', binUnit: 'ms', data: { bins: [{ low: 0, high: 10, count: 4 }, { low: 10, high: 20, count: 9 }] } },
  scatter: { kind: 'scatter', xLabel: 'Size', yLabel: 'Time', data: { points: [{ label: 'a', x: 1000, y: 5 }, { label: 'b', x: 1010, y: 6 }] } },
  donut: { kind: 'donut', unit: 'GB', data: { categories: ['Logs', 'Other'], values: [1, 3] } },
  heatmap: { kind: 'heatmap', unit: 'tasks', data: { rows: ['Mon', 'Tue'], columns: ['09', '10', '11'], values: [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]] } },
  box: { kind: 'box', data: { groups: [{ name: 'A', min: 10, q1: 20, median: 30, q3: 45, max: 70 }] } }
};

function checkScales({ niceStep, domain, baseline, ticks }) {
  // Round intervals to readable multiples.
  assert.equal(niceStep(0.3), 0.5);
  assert.equal(niceStep(7), 10);
  assert.equal(niceStep(120), 200);

  // Include zero for magnitude axes, and fit position axes to the data.
  assert.deepEqual(domain([20, 35]), [0, 40]);
  assert.deepEqual(domain([1000, 1010], { zero: false }), [995, 1015]);
  assert.deepEqual(domain([7], { zero: false }), [6, 8]);
  assert.deepEqual(domain([0, 0]), [0, 1.5]);
  assert.deepEqual(domain([20, 35], { min: 10, max: 50 }), [10, 50]);

  // Keep spans finite when values differ only by floating-point noise or sit at large magnitudes.
  for (const values of [[0.3, 0.1 + 0.2], [1e16, 1e16 + 2], [1700000000000, 1700000000000.0002]]) {
    const [low, high] = domain(values, { zero: false });
    assert.ok(Number.isFinite(low) && Number.isFinite(high) && high > low, String(values));
    assert.ok(ticks(low, high).length > 0, 'ticks for ' + values);
  }

  // Keep genuinely distinct large values apart, such as millisecond timestamps one second apart.
  const [tLow, tHigh] = domain([1700000000000, 1700000001000], { zero: false });
  assert.ok(tHigh - tLow < 10000, 'timestamp axis spans seconds, not years');

  // Keep a single explicit bound beyond the data from inverting the axis.
  const [raisedLow, raisedHigh] = domain([1, 5], { min: 10, zero: false });
  assert.equal(raisedLow, 10);
  assert.ok(raisedHigh > raisedLow);
  const [loweredLow, loweredHigh] = domain([20, 30], { max: 5 });
  assert.equal(loweredHigh, 5);
  assert.ok(loweredHigh > loweredLow);

  // Keep filled marks inside a raised or lowered axis.
  assert.equal(baseline(-5, 10), 0);
  assert.equal(baseline(50, 100), 50);
  assert.equal(baseline(-100, -20), -20);

  // Produce evenly spaced ticks without floating-point residue at zero.
  assert.deepEqual(ticks(0, 40), [0, 10, 20, 30, 40]);
  assert.deepEqual(ticks(-0.3, 0.3), [-0.2, 0, 0.2]);

  // Return no ticks for empty ranges, and stop even when the step is below float precision.
  assert.deepEqual(ticks(5, 5), []);
  assert.deepEqual(ticks(10, 6), []);
  assert.ok(ticks(1e16, 1e16 + 2).length <= 51);
}

function checkFormatting({ formats }) {
  // Format exact values, intervals, and shares for the document language.
  const en = formats('en');
  const de = formats('de');
  assert.equal(en.value(1234.5), '1,234.5');
  assert.equal(de.value(1234.5), '1.234,5');
  assert.equal(en.value(0.1 + 0.2), '0.30000000000000004');
  assert.equal(en.value('Label'), 'Label');
  assert.equal(en.range(0.5, 1.5), '0.5–1.5');
  assert.equal(en.share(1 / 3), '33.3%');
  assert.equal(en.unit(1200, 'ms'), '1,200 ms');
  assert.equal(en.unit(3, ''), '3');
  assert.equal(en.axis(0.1 + 0.2), '0.3');
}

function checkLabels({ wrapLabel }) {
  // Keep short labels whole, wrap at words, and split or truncate what cannot fit.
  assert.deepEqual(wrapLabel('Short', 120), ['Short']);
  assert.deepEqual(wrapLabel('Two words', 50), ['Two', 'words']);
  assert.deepEqual(wrapLabel('Supercalifragilistic', 60), ['Superca', 'lifrag…']);
  assert.deepEqual(wrapLabel('one two three four five six', 50), ['one', 'two']);
}

function checkNavigation({ nextIndex, nearestIndex }) {
  // Move through marks with wrapping, endpoints, and grid rows.
  assert.equal(nextIndex('ArrowRight', 4, 5), 0);
  assert.equal(nextIndex('ArrowLeft', 0, 5), 4);
  assert.equal(nextIndex('ArrowDown', 1, 6), 2);
  assert.equal(nextIndex('ArrowDown', 1, 6, 3), 4);
  assert.equal(nextIndex('ArrowUp', 1, 6, 3), 4);
  assert.equal(nextIndex('Home', 3, 6), 0);
  assert.equal(nextIndex('End', 3, 6), 5);
  assert.equal(nextIndex('a', 3, 6), null);

  // Pick the nearest mark horizontally for series and in two dimensions for scatter plots.
  const records = [{ x: 0, y: 0 }, { x: 10, y: 100 }, { x: 12, y: 0 }];
  assert.equal(nearestIndex(records, { x: 10, y: 0 }, 'x'), 1);
  assert.equal(nearestIndex(records, { x: 10, y: 0 }, 'xy'), 2);
  assert.equal(nearestIndex([], { x: 0, y: 0 }, 'x'), -1);
}

function checkKinds(model) {
  const format = model.formats('en');

  // Every kind declares its table, legend, and drawing in one place.
  for (const [kind, config] of Object.entries(CONFIGS)) {
    const declaration = model.kinds[kind];
    assert.equal(typeof declaration.table, 'function', kind);
    assert.equal(typeof declaration.legend, 'function', kind);
    assert.equal(typeof declaration.draw, 'function', kind);

    // Each data-table row has one cell per header.
    const table = declaration.table(config, format);
    table.rows.forEach(row => assert.equal(row.length, table.headers.length, kind));
  }

  // Series charts mark one point per category, dash the second series, and overlay a crosshair.
  for (const kind of ['line', 'area']) {
    const { drawn, marks } = fakePlot(model, CONFIGS[kind]);
    assert.equal(marks.length, CONFIGS[kind].data.categories.length);
    assert.ok(drawn.some(e => e.attrs?.class === 'chart-line dashed'));
    assert.ok(drawn.some(e => e.tag === 'overlay'));
    assert.deepEqual(model.kinds[kind].legend(CONFIGS[kind]).entries.map(e => Boolean(e.dashed)), [false, true]);
  }

  // Area fills close at the raised axis rather than at y = 0 below the plot.
  const area = fakePlot(model, CONFIGS.area).drawn.find(e => e.attrs.class === 'chart-area');
  assert.match(area.attrs.d, /L\S+ 266L\S+ 266Z$/);

  // Bars and bins mark each value; long categories wrap with the full label kept as a title.
  const bars = fakePlot(model, CONFIGS.bar, 300);
  assert.equal(bars.marks.length, 2);
  assert.ok(bars.drawn.some(e => e.children.some(c => c.tag === 'title')));
  assert.equal(fakePlot(model, CONFIGS.histogram).marks[1].record.title, '10–20 ms');

  // Scatter plots fit clustered points across the plot instead of pinning them to one edge.
  const scatter = fakePlot(model, CONFIGS.scatter);
  const xs = scatter.marks.map(mk => mk.record.x);
  assert.ok(xs[1] - xs[0] > 200, 'clustered scatter points spread across the plot');
  assert.equal(model.kinds.scatter.nearest, 'xy');

  // Near-equal observations still map to finite coordinates.
  const noisy = fakePlot(model, { kind: 'scatter', xLabel: 'X', yLabel: 'Y', data: { points: [{ label: 'a', x: 1, y: 0.3 }, { label: 'b', x: 2, y: 0.1 + 0.2 }] } });
  noisy.marks.forEach(mk => assert.ok(Number.isFinite(mk.record.x) && Number.isFinite(mk.record.y)));
  noisy.drawn.filter(e => e.tag === 'text').forEach(e => assert.ok(Number.isFinite(Number(e.attrs.y)), 'finite label position'));

  // Donut segments report locale-formatted shares and label the total with its unit.
  const donut = fakePlot(model, CONFIGS.donut);
  assert.deepEqual(donut.marks.map(mk => mk.record.rows[1][1]), ['25.0%', '75.0%']);
  assert.ok(donut.drawn.some(e => e.text === 'GB Total'));
  assert.ok(fakePlot(model, { ...CONFIGS.donut, unit: '' }).drawn.some(e => e.text === 'Total'));

  // Heatmaps use their own frame, move by rows, scale to the data maximum, and invert intense labels.
  assert.deepEqual(model.frame('heatmap'), { height: 310, left: 92 });
  assert.equal(model.kinds.heatmap.stride(CONFIGS.heatmap), 3);
  assert.equal(model.kinds.heatmap.legend(CONFIGS.heatmap).scale, 0.6);
  const heat = fakePlot(model, CONFIGS.heatmap);
  assert.equal(heat.marks.length, 6);
  assert.equal(Number(heat.marks[5].element.attrs.opacity).toFixed(2), '0.94');
  assert.equal(heat.drawn.filter(e => e.attrs.class === 'chart-cell-value intense').length, 3);
  assert.ok(!heat.drawn.some(e => e.attrs.class === 'chart-axis-title'), 'no empty axis title without xLabel');

  // Box plots mark one group with its five-number summary.
  const box = fakePlot(model, CONFIGS.box);
  assert.equal(box.marks.length, 1);
  assert.equal(box.marks[0].record.rows.length, 5);
  assert.equal(box.marks[0].element.children.length, 4);
}

// Exercise the same contracts through source and the shipped generated module.
for (const name of ['charts.js', 'charts.min.js']) {
  const model = require('../assets/' + name);
  checkScales(model);
  checkFormatting(model);
  checkLabels(model);
  checkNavigation(model);
  checkKinds(model);
}
console.log('Chart scales, formatting, labels, navigation, and every kind\'s drawing passed across source and minified assets.');
