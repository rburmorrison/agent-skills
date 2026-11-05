# Interactive Charts

A chart block accepts `type:"chart"`, `kind`, `title`, `data`, and optional `id`, `caption`, `xLabel`, `yLabel`, `unit`, `xUnit`, `binUnit`, `valueLabel`, `pointPrefix`, `yMin`, `yMax`, `selectedIndex`. Use camelCase exactly for chart option names. Match unit labels to the numbers; e.g. values already in milliseconds use `unit:"ms"`.

The renderer supplies axes, responsive labels, theme colors, exact-value inspection, keyboard navigation, and a View Data table. Do not draw your own tooltip or axes for these charts. Numeric values must be finite numbers, not strings. Label illustrative datasets as illustrative. There is no requirement to add a chart when the content does not benefit from one.

## Data Shapes

**Line / Area** — categorical or evenly spaced observations. Each series must match `categories` length. Negative values work. For irregular numeric x coordinates use scatter, or a custom numeric plot rather than presenting unequal intervals as equally spaced.

```json
{"type":"chart","kind":"line","id":"trend","title":"Response Time","xLabel":"Elapsed Time (s)","yLabel":"Latency (ms)","unit":"ms","caption":"Illustrative values.","data":{"categories":["0","10","20"],"series":[{"name":"Baseline","values":[20,35,27]},{"name":"Updated","values":[18,24,22]}]}}
```

Change `kind` to `area` for filled areas. Multiple areas overlap; they are **not stacked**. `selectedIndex` optionally highlights a particular observation; it is a sample index, not an x coordinate. Only use an exact matching sample for the current input; omit the highlight (set `-1`) between samples rather than presenting a nearby point as the current value. `pointPrefix` adds context before its category in the tooltip. Hovering the plot inspects the nearest x position and shows all series at that position.

**Bar** — compare categories, including signed values.

```json
{"type":"chart","kind":"bar","title":"Net Change","xLabel":"Stage","yLabel":"Change","unit":"items","data":{"categories":["A","B","C"],"values":[12,-5,8]}}
```

Keep category labels short; explain longer names in surrounding text or a table.

**Scatter** — numeric x/y observations, including negative coordinates. Each point needs a label.

```json
{"type":"chart","kind":"scatter","title":"Size and Duration","xLabel":"Size (KB)","yLabel":"Duration (ms)","xUnit":"KB","unit":"ms","data":{"points":[{"label":"Observation A","x":10,"y":45},{"label":"Observation B","x":30,"y":70}]}}
```

**Histogram** — contiguous, increasing, equal-width bins. The renderer plots frequencies, not probability densities. Compute bin counts from supplied observations, or clearly label sample data.

```json
{"type":"chart","kind":"histogram","title":"Duration Distribution","xLabel":"Duration (ms)","yLabel":"Count","binUnit":"ms","unit":"observations","data":{"bins":[{"low":0,"high":10,"count":4},{"low":10,"high":20,"count":9},{"low":20,"high":30,"count":2}]}}
```

**Donut** — parts of a meaningful whole; a few categories. Values must be nonnegative with a positive total. A bar chart is easier for precise category comparisons.

```json
{"type":"chart","kind":"donut","title":"Storage Allocation","valueLabel":"Storage","unit":"GB","data":{"categories":["Logs","Models","Other"],"values":[40,35,25]}}
```

**Heatmap** — nonnegative numeric matrix. Rows in `values` must match `rows`, and every matrix row must match `columns`. Zero-only matrices work. Hover/focus reveals exact values even when cells are too narrow to show numbers.

```json
{"type":"chart","kind":"heatmap","title":"Completions","xLabel":"Hour","yLabel":"Day","valueLabel":"Completed","unit":"tasks","data":{"rows":["Mon","Tue"],"columns":["09","10","11"],"values":[[2,6,4],[3,8,5]]}}
```

**Box** — five-number summaries. Supply true summaries, not uncomputed raw observations. This implementation uses minimum/maximum whiskers, not Tukey fences; there is no separate outlier series.

```json
{"type":"chart","kind":"box","title":"Duration by Group","xLabel":"Group","yLabel":"Duration (ms)","unit":"ms","caption":"Whiskers show the minimum and maximum.","data":{"groups":[{"name":"A","min":10,"q1":20,"median":30,"q3":45,"max":70},{"name":"B","min":15,"q1":25,"median":38,"q3":50,"max":90}]}}
```

## Live Updates

Give a chart an explicit ID, then update it from an embedded script:

```js
window.Explainer.chart('trend', {
  data: {categories: ['0','10','20'], series: [{name: 'Latency', values: [18,23,21]}]},
  selectedIndex: 1
});
```

Updates replace `data` as a whole. Use the same shape and finite numeric constraints as the original chart. Derive calculations, visible result text, and chart data from one state. Call your initial render after wiring inputs. No network, imports, or third-party runtime is needed.
