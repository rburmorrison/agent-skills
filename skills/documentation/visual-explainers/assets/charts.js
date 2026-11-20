// Plot offline SVG charts with shared exact-value inspection.

// Keep chart scales, tables, drawing rules, and navigation free of the DOM so they can be verified directly.
const ExplainerChartModel = (() => {
  const PALETTE = [
    'var(--accent)',
    'var(--chart-secondary)',
    'var(--chart-third)',
    'var(--chart-fourth)',
    'var(--chart-fifth)'
  ];
  const DEFAULT_FRAME = { height: 320, left: 54 };
  const color = i => PALETTE[i % PALETTE.length];

  /**
   * Build the number formatters used by every chart in one document.
   * @param {string} locale BCP 47 language tag accepted by Intl.
   * @returns {{value: Function, axis: Function, range: Function, share: Function, unit: Function}}
   *   Exact values, tick labels (scientific when shorter), intervals, one-decimal percentages, and values with an optional unit.
   */
  function formats(locale) {
    const number = new Intl.NumberFormat(locale, { maximumSignificantDigits: 17 });
    const percent = new Intl.NumberFormat(locale, { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 });
    const scientific = new Intl.NumberFormat(locale, { notation: 'scientific', maximumSignificantDigits: 8 });
    const value = n => typeof n === 'number' ? number.format(n) : String(n);
    return {
      value,
      axis(n) {
        // Remove floating-point residue, then prefer scientific notation only when it is shorter.
        const rounded = Number(n.toPrecision(8));
        const ordinary = value(rounded);
        const compact = scientific.format(rounded);
        return compact.length < ordinary.length ? compact : ordinary;
      },
      range: (low, high) => value(low) + '–' + value(high),
      share: fraction => percent.format(fraction),
      unit: (n, unit) => value(n) + (unit ? ' ' + unit : '')
    };
  }

  /**
   * Round an interval up to a readable 1, 2, 5, or 10 multiple of its magnitude.
   * @param {number} value Positive interval.
   * @returns {number} Readable interval no smaller than value.
   */
  function niceStep(value) {
    // Normalize the requested interval to its decimal magnitude.
    const power = 10 ** Math.floor(Math.log10(Math.max(value, 1e-9)));
    const f = value / power;

    // Choose a readable one, two, five, or ten interval.
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * power;
  }

  /**
   * Choose a padded, rounded axis range for plotted values.
   * @param {number[]} values Finite plotted values; at least one.
   * @param {{min?: number, max?: number, zero?: boolean}} [options] Explicit bounds, and
   *   whether the range must include zero because marks encode magnitude from a baseline.
   * @returns {[number, number]} Lower and upper axis bounds, lower first. A single explicit
   *   bound on the far side of the data keeps the fitted span instead of inverting the axis.
   */
  function domain(values, { min, max, zero = true } = {}) {
    // Fit the values, including zero when marks encode magnitude from a baseline.
    let lo = Math.min(...values);
    let hi = Math.max(...values);
    if (zero) {
      lo = Math.min(0, lo);
      hi = Math.max(0, hi);
    }

    // Treat a span lost in floating-point precision as a single value, and widen it so it stays visible.
    if (hi - lo <= Math.max(Math.abs(lo), Math.abs(hi)) * Number.EPSILON * 64) {
      const center = (lo + hi) / 2;
      const half = zero ? 0 : Math.abs(center) * .1 || .5;
      lo = zero ? lo : center - half;
      hi = zero ? hi + 1 : center + half;
    }

    // Pad the domain, keeping zero as a natural boundary when it is included.
    const pad = (hi - lo) * .06;
    if (!zero || lo < 0)
      lo -= pad;
    if (!zero || hi > 0)
      hi += pad;

    // Round domain bounds unless the configuration supplies explicit limits.
    const step = niceStep((hi - lo) / 4);
    const span = Math.ceil(hi / step) * step - Math.floor(lo / step) * step;
    let low = min ?? Math.floor(lo / step) * step;
    let high = max ?? Math.ceil(hi / step) * step;

    // Keep an explicit bound beyond the data from inverting the axis.
    if (!(high > low)) {
      if (max === undefined)
        high = low + span;
      else
        low = high - span;
    }
    return [low, high];
  }

  /**
   * Anchor filled marks at zero, or at the nearest plotted edge when zero is outside the domain.
   * @param {number} min Lower axis bound.
   * @param {number} max Upper axis bound.
   * @returns {number} Baseline value within the domain.
   */
  function baseline(min, max) {
    return Math.min(max, Math.max(min, 0));
  }

  /**
   * List readable tick values across an axis.
   * @param {number} min Lower axis bound.
   * @param {number} max Upper axis bound, greater than min.
   * @returns {number[]} Ascending ticks within the bounds, at most 51, with floating-point residue
   *   near zero removed; empty when max is not greater than min.
   */
  function ticks(min, max) {
    // Choose a readable tick interval, and draw none for an empty or invalid range.
    const step = niceStep((max - min) / 5);
    if (!(max > min) || !(step > 0) || !Number.isFinite(step))
      return [];

    // Enumerate by index, so precision loss at large magnitudes cannot stall the loop,
    // and normalize near-zero floating-point residue.
    const first = Math.ceil(min / step) * step;
    const out = [];
    for (let i = 0; i <= 50; i++) {
      const v = first + i * step;
      if (v > max + step * .001)
        break;
      out.push(Math.abs(v) < step * .001 ? 0 : v);
    }
    return out;
  }

  /**
   * Fit a category label beneath a mark using approximate character widths.
   * @param {*} label Category label.
   * @param {number} width Available width in SVG units.
   * @returns {string[]} The whole label as one line when it fits; otherwise at most two
   *   wrapped lines, with an ellipsis on any line that still overflows.
   */
  function wrapLabel(label, width) {
    // Use a single line when the category label fits.
    const text = String(label);
    const size = Math.max(3, Math.floor((width - 8) / 6.6));
    if (text.length <= size)
      return [text];

    // Wrap longer labels at word boundaries.
    const lines = [];
    let line = '';
    for (const word of text.split(/\s+/)) {
      if ((line + ' ' + word).trim().length > size && line) {
        lines.push(line);
        line = word;
      }
      else
        line = (line + ' ' + word).trim();
    }
    if (line)
      lines.push(line);

    // Split an overlong unbroken label across two lines.
    if (lines.length === 1) {
      const [word] = lines;
      lines.splice(0, 1, word.slice(0, size), word.slice(size));
    }

    // Keep two lines and mark any remaining overflow.
    return lines.slice(0, 2).map(l => l.length > size ? l.slice(0, Math.max(1, size - 1)) + '…' : l);
  }

  /**
   * Choose the mark a navigation key moves to.
   * @param {string} key KeyboardEvent key value.
   * @param {number} index Current mark index.
   * @param {number} count Number of marks, greater than zero.
   * @param {number} [stride] Marks per grid row; vertical arrows move by rows when supplied.
   * @returns {?number} Next mark index, wrapping at the ends, or null for non-navigation keys.
   */
  function nextIndex(key, index, count, stride) {
    if (stride && (key === 'ArrowDown' || key === 'ArrowUp'))
      return (index + (key === 'ArrowDown' ? stride : count - stride)) % count;
    if (key === 'ArrowRight' || key === 'ArrowDown')
      return (index + 1) % count;
    if (key === 'ArrowLeft' || key === 'ArrowUp')
      return (index + count - 1) % count;
    if (key === 'Home')
      return 0;
    if (key === 'End')
      return count - 1;
    return null;
  }

  /**
   * Find the mark closest to a plot position.
   * @param {{x: number, y: number}[]} records Mark positions in SVG units.
   * @param {{x: number, y: number}} point Position in SVG units.
   * @param {'x'|'xy'} mode Compare horizontal distance only, or Euclidean distance.
   * @returns {number} Index of the first nearest record, or -1 when there are none.
   */
  function nearestIndex(records, point, mode) {
    let best = -1;
    let distance = Infinity;
    records.forEach((r, i) => {
      const d = mode === 'xy' ? Math.hypot(point.x - r.x, point.y - r.y) : Math.abs(point.x - r.x);
      if (d < distance) {
        distance = d;
        best = i;
      }
    });
    return best;
  }

  // Drawing helpers shared by chart kinds. Each receives the plot toolkit described on `kinds`.
  function valueAxis(plot, min, max) {
    // Draw horizontal grid lines with their numeric labels.
    const { config, W, H, m, plotH } = plot;
    for (const value of ticks(min, max)) {
      const y = H - m.b - plotH * (value - min) / (max - min);
      plot.add('path', { d: `M${m.l} ${y}H${W - m.r}`, class: 'chart-grid' });
      plot.add('text', { x: m.l - 10, y: y + 4, 'text-anchor': 'end', class: 'chart-axis' }, plot.format.axis(value));
    }

    // Place the configured axis titles outside the plot.
    if (config.yLabel)
      plot.add('text', { x: m.l, y: 16, class: 'chart-axis-title' }, config.yLabel);
    xTitle(plot);
  }

  function xTitle(plot) {
    const { config, W, H, m } = plot;
    if (config.xLabel)
      plot.add('text', { x: (m.l + W - m.r) / 2, y: H - 5, 'text-anchor': 'middle', class: 'chart-axis-title' }, config.xLabel);
  }

  function axisLabel(plot, label, x, y = plot.H - plot.m.b + 22) {
    plot.add('text', { x, y, 'text-anchor': 'middle', class: 'chart-axis' }, label);
  }

  function categoryLabel(plot, label, x, width) {
    // Draw a fitting label directly.
    const lines = wrapLabel(label, width);
    const y = plot.H - plot.m.b + 20;
    if (lines.length === 1) {
      axisLabel(plot, lines[0], x, y);
      return;
    }

    // Draw wrapped lines while retaining the full label as the element title.
    const text = plot.add('text', { x, y, 'text-anchor': 'middle', class: 'chart-axis' });
    text.append(plot.node('title', {}, String(label)));
    lines.forEach((line, i) => text.append(plot.node('tspan', { x, dy: i ? 14 : 0 }, line)));
  }

  function plotHit(plot) {
    // Reserve a transparent target so the whole plot area reports pointer positions.
    const { m, plotW, plotH } = plot;
    plot.add('rect', { x: m.l, y: m.t, width: plotW, height: plotH, class: 'chart-hit', 'data-plot-hit': 'true' });
  }

  function seriesKind(filled) {
    return {
      nearest: 'x',
      yDomain: config => domain(config.data.series.flatMap(s => s.values), { min: config.yMin, max: config.yMax }),
      table: config => ({
        headers: [config.xLabel || 'Category', ...config.data.series.map(s => s.name)],
        rows: config.data.categories.map((c, i) => [c, ...config.data.series.map(s => s.values[i])])
      }),
      legend: config => ({
        entries: config.data.series.length > 1 ? config.data.series.map((s, i) => ({ name: s.name, color: color(i), dashed: i === 1 })) : []
      }),
      draw(plot) {
        // Map series categories and values into plot coordinates.
        const { config, data, H, m, plotW, plotH, format } = plot;
        const n = data.categories.length;
        const [min, max] = kinds[config.kind].yDomain(config);
        const x = i => m.l + (n === 1 ? plotW / 2 : plotW * i / (n - 1));
        const y = v => H - m.b - plotH * (v - min) / (max - min);
        valueAxis(plot, min, max);

        // Thin category labels to the available horizontal space.
        const widest = Math.max(...data.categories.map(v => String(v).length));
        const slots = Math.max(2, Math.min(n, Math.floor(plotW / (widest * 6.8 + 18))));
        const shown = new Set(Array.from({ length: slots }, (_, i) => Math.round(i * (n - 1) / (slots - 1))));
        data.categories.forEach((v, i) => {
          if (shown.has(i))
            axisLabel(plot, v, x(i));
        });
        plotHit(plot);

        // Draw series paths, and area fills down to the baseline beneath them.
        const base = y(baseline(min, max));
        data.series.forEach((s, j) => {
          const path = s.values.map((v, i) => (i ? 'L' : 'M') + x(i) + ' ' + y(v)).join(' ');
          if (filled)
            plot.add('path', { d: path + `L${x(n - 1)} ${base}L${x(0)} ${base}Z`, class: 'chart-area', fill: color(j) });
          plot.add('path', { d: path, class: j === 1 ? 'chart-line dashed' : 'chart-line', stroke: color(j) });
        });

        // Register one inspection mark per category with all series values.
        data.categories.forEach((label, i) => {
          const position = { x: x(i), y: y(data.series[0].values[i]) };
          plot.mark(plot.node('circle', { cx: position.x, cy: position.y, r: 4, class: 'chart-point' }), {
            title: (config.pointPrefix || '') + label,
            rows: data.series.map(s => [s.name, format.unit(s.values[i], config.unit)]),
            ...position
          });
        });

        // Add the crosshair and selection overlays above the series.
        plot.overlay();
      }
    };
  }

  function barKind(histogram) {
    const values = data => histogram ? data.bins.map(b => b.count) : data.values;
    return {
      yDomain: config => domain(values(config.data), { min: config.yMin, max: config.yMax }),
      table: (config, format) => histogram
        ? {
          headers: ['Interval (' + (config.binUnit || 'units') + ')', config.yLabel || 'Count'],
          rows: config.data.bins.map(b => [format.range(b.low, b.high), b.count])
        }
        : {
          headers: ['Category', config.yLabel || config.unit || 'Value'],
          rows: config.data.categories.map((c, i) => [c, config.data.values[i]])
        },
      legend: () => ({ entries: [] }),
      draw(plot) {
        // Map bar values or histogram counts onto a shared numeric axis.
        const { config, data, H, m, plotW, plotH, format } = plot;
        const heights = values(data);
        const n = heights.length;
        const [min, max] = kinds[config.kind].yDomain(config);
        const step = plotW / n;
        const yAt = v => H - m.b - plotH * (v - min) / (max - min);
        const zero = yAt(baseline(min, max));
        valueAxis(plot, min, max);

        heights.forEach((v, i) => {
          // Draw each value as an inspectable bar or bin.
          const x = m.l + i * step + (histogram ? 1 : step * .17);
          const width = histogram ? step - 2 : step * .66;
          const y = Math.min(zero, yAt(v));
          const label = histogram
            ? format.range(data.bins[i].low, data.bins[i].high) + (config.binUnit ? ' ' + config.binUnit : '')
            : data.categories[i];
          plot.mark(plot.node('rect', { x, y, width: Math.max(1, width), height: Math.abs(yAt(v) - zero), rx: histogram ? 1 : 4, class: 'chart-bar' }), {
            title: label,
            rows: [[config.yLabel || 'Value', format.unit(v, config.unit)]],
            x: x + width / 2,
            y
          });

          // Label bin boundaries, thinning alternate edges on narrow charts, or wrap the category text.
          if (!histogram)
            categoryLabel(plot, label, x + width / 2, step);
          else {
            if (i === 0)
              axisLabel(plot, format.axis(data.bins[i].low), m.l);
            if (plot.W > 450 || i % 2 === 1 || i === n - 1)
              axisLabel(plot, format.axis(data.bins[i].high), m.l + (i + 1) * step);
          }
        });
      }
    };
  }

  /**
   * Chart kinds keyed by the renderer's `kind` value. Each declaration owns:
   * - `table(config, format)`: headers and raw rows for the accessible data table;
   * - `legend(config, format)`: swatch entries and an optional intensity `scale` maximum;
   * - `draw(plot)`: marks drawn through the plot toolkit, which supplies `config`, `data`,
   *   `format`, `W`, `H`, margins `m`, `plotW`, `plotH`, `node(tag, attrs, text)` to create,
   *   `add(tag, attrs, text)` to create and append, `mark(element, record)` to append an
   *   inspectable mark, and `overlay()` for series crosshairs;
   * - optional `frame` height and left margin, `nearest` pointer mode, grid `stride(config)`,
   *   and `yDomain(config)` bounds for a numeric value axis.
   */
  const kinds = {
    line: seriesKind(false),
    area: seriesKind(true),
    bar: barKind(false),
    histogram: barKind(true),
    scatter: {
      nearest: 'xy',
      yDomain: config => domain(config.data.points.map(p => p.y), { min: config.yMin, max: config.yMax, zero: false }),
      table: config => ({
        headers: ['Observation', config.xLabel, config.yLabel],
        rows: config.data.points.map(p => [p.label, p.x, p.y])
      }),
      legend: () => ({ entries: [] }),
      draw(plot) {
        // Fit both axes to the observations, since scatter marks encode position rather than magnitude.
        const { config, data, H, m, plotW, plotH, format } = plot;
        const [xmin, xmax] = domain(data.points.map(p => p.x), { min: config.xMin, max: config.xMax, zero: false });
        const [ymin, ymax] = kinds.scatter.yDomain(config);
        const x = v => m.l + plotW * (v - xmin) / (xmax - xmin);
        const y = v => H - m.b - plotH * (v - ymin) / (ymax - ymin);
        valueAxis(plot, ymin, ymax);
        for (const v of ticks(xmin, xmax))
          axisLabel(plot, format.axis(v), x(v));
        plotHit(plot);

        // Draw an inspectable mark for each observation.
        data.points.forEach(p => {
          const position = { x: x(p.x), y: y(p.y) };
          plot.mark(plot.node('circle', { cx: position.x, cy: position.y, r: 5, class: 'chart-dot' }), {
            title: p.label,
            rows: [[config.xLabel, format.unit(p.x, config.xUnit)], [config.yLabel, format.unit(p.y, config.unit)]],
            ...position
          });
        });
      }
    },
    donut: {
      table: config => ({
        headers: ['Category', config.yLabel || config.unit || 'Value'],
        rows: config.data.categories.map((c, i) => [c, config.data.values[i]])
      }),
      legend: config => ({ entries: config.data.categories.map((name, i) => ({ name, color: color(i) })) }),
      draw(plot) {
        // Measure the total and establish the ring geometry.
        const { config, data, W, H, format } = plot;
        const total = data.values.reduce((a, b) => a + b, 0);
        const cx = W / 2;
        const cy = H / 2 - 8;
        const outer = 101;
        const inner = 62;
        const at = (radius, a) => [cx + Math.cos(a) * radius, cy + Math.sin(a) * radius];
        let angle = -Math.PI / 2;

        // Draw inspectable ring segments in category order.
        data.values.forEach((v, i) => {
          const end = angle + Math.min(v / total * Math.PI * 2, Math.PI * 2 - 0.00001);
          const large = end - angle > Math.PI ? 1 : 0;
          const d = `M${at(outer, angle)}A${outer} ${outer} 0 ${large} 1 ${at(outer, end)}L${at(inner, end)}A${inner} ${inner} 0 ${large} 0 ${at(inner, angle)}Z`;
          const [x, y] = at((outer + inner) / 2, (angle + end) / 2);
          plot.mark(plot.node('path', { d, class: 'chart-slice', fill: color(i) }), {
            title: data.categories[i],
            rows: [[config.valueLabel || config.yLabel || 'Value', format.unit(v, config.unit)], ['Share', format.share(v / total)]],
            x,
            y
          });
          angle = end;
        });

        // Label the center of the ring with its total and unit.
        plot.add('text', { x: cx, y: cy - 2, 'text-anchor': 'middle', class: 'chart-total' }, format.value(total));
        plot.add('text', { x: cx, y: cy + 22, 'text-anchor': 'middle', class: 'chart-axis' }, config.unit ? config.unit + ' Total' : 'Total');
      }
    },
    heatmap: {
      frame: { height: 310, left: 92 },
      stride: config => config.data.columns.length,
      table: config => ({
        headers: [config.yLabel || 'Row', ...config.data.columns],
        rows: config.data.rows.map((r, i) => [r, ...config.data.values[i]])
      }),
      legend: config => ({ entries: [], scale: Math.max(...config.data.values.flat()) }),
      draw(plot) {
        // Measure the cell grid and scale intensity to the largest value.
        const { config, data, W, m, plotW, plotH, format } = plot;
        const max = Math.max(...data.values.flat());
        const intensity = v => max > 0 ? v / max : 0;
        const cw = plotW / data.columns.length;
        const ch = plotH / data.rows.length;

        data.rows.forEach((row, ri) => {
          // Label the row, abbreviating on narrow charts.
          plot.add('text', { x: m.l - 9, y: m.t + (ri + .5) * ch + 4, 'text-anchor': 'end', class: 'chart-axis' }, W < 450 ? row.slice(0, 3) : row);

          data.columns.forEach((col, ci) => {
            // Draw cell intensity and register its exact-value inspection.
            const v = data.values[ri][ci];
            const x = m.l + ci * cw + 2;
            const y = m.t + ri * ch + 2;
            const center = { x: x + cw / 2 - 2, y: y + ch / 2 - 2 };
            plot.mark(plot.node('rect', { x, y, width: Math.max(1, cw - 4), height: ch - 4, rx: 3, class: 'chart-cell', opacity: .12 + .82 * intensity(v) }), {
              title: row + ' · ' + col,
              rows: [[config.valueLabel || 'Value', format.unit(v, config.unit)]],
              ...center
            });

            // Overlay values only when the cell is wide enough, inverting text on intense cells.
            if (cw > 48)
              plot.add('text', { x: center.x, y: center.y + 4, 'text-anchor': 'middle', class: intensity(v) > .5 ? 'chart-cell-value intense' : 'chart-cell-value' }, format.value(v));
          });
        });

        // Label columns, thinning alternate labels on narrow charts.
        data.columns.forEach((col, i) => {
          if (W >= 450 || i % 2 === 0)
            axisLabel(plot, col, m.l + (i + .5) * cw);
        });
        xTitle(plot);
      }
    },
    box: {
      yDomain: config => domain(config.data.groups.flatMap(g => [g.min, g.max]), { min: config.yMin, max: config.yMax }),
      table: config => ({
        headers: ['Group', 'Min', 'Q1', 'Median', 'Q3', 'Max'],
        rows: config.data.groups.map(g => [g.name, g.min, g.q1, g.median, g.q3, g.max])
      }),
      legend: () => ({ entries: [] }),
      draw(plot) {
        // Map five-number summaries onto a shared numeric axis.
        const { config, data, H, m, plotW, plotH, format } = plot;
        const [min, max] = kinds.box.yDomain(config);
        const y = v => H - m.b - plotH * (v - min) / (max - min);
        const step = plotW / data.groups.length;
        valueAxis(plot, min, max);

        data.groups.forEach((g, i) => {
          // Draw each inspectable box with its whiskers and median.
          const x = m.l + (i + .5) * step;
          const bw = Math.min(64, step * .58);
          const group = plot.node('g');
          group.append(
            plot.node('rect', { x: x - bw / 2 - 6, y: y(g.max) - 5, width: bw + 12, height: y(g.min) - y(g.max) + 10, class: 'chart-hit' }),
            plot.node('path', { d: `M${x} ${y(g.max)}V${y(g.min)}M${x - bw * .3} ${y(g.max)}H${x + bw * .3}M${x - bw * .3} ${y(g.min)}H${x + bw * .3}`, class: 'chart-whisker' }),
            plot.node('rect', { x: x - bw / 2, y: y(g.q3), width: bw, height: y(g.q1) - y(g.q3), rx: 3, class: 'chart-box' }),
            plot.node('path', { d: `M${x - bw / 2} ${y(g.median)}H${x + bw / 2}`, class: 'chart-median' })
          );
          plot.mark(group, {
            title: g.name,
            rows: [
              ['Minimum', format.unit(g.min, config.unit)],
              ['Q1', format.unit(g.q1, config.unit)],
              ['Median', format.unit(g.median, config.unit)],
              ['Q3', format.unit(g.q3, config.unit)],
              ['Maximum', format.unit(g.max, config.unit)]
            ],
            x,
            y: y(g.median)
          });

          // Label the group beneath its box.
          axisLabel(plot, g.name, x);
        });
      }
    }
  };

  /**
   * Resolve a chart's frame size from its kind.
   * @param {string} kind Key of `kinds`.
   * @returns {{height: number, left: number}} SVG height and left margin in SVG units.
   */
  function frame(kind) {
    return { ...DEFAULT_FRAME, ...kinds[kind].frame };
  }

  /**
   * List the formatted labels of a chart's numeric value axis.
   * @param {object} config Chart configuration with a `kind` key of `kinds`.
   * @param {{axis: Function}} format Formatters from `formats`.
   * @returns {string[]} Tick labels in drawing order; empty when the kind has no value axis.
   */
  function valueAxisLabels(config, format) {
    const kind = kinds[config.kind];
    return kind.yDomain ? ticks(...kind.yDomain(config)).map(format.axis) : [];
  }

  return { formats, niceStep, domain, baseline, ticks, wrapLabel, nextIndex, nearestIndex, kinds, frame, valueAxisLabels };
})();

// Expose the model to tests, and bind charts when running in a document.
if (typeof module !== 'undefined' && module.exports)
  module.exports = ExplainerChartModel;
if (typeof document !== 'undefined')
  (() => {
    const { formats, kinds, frame, valueAxisLabels, nextIndex, nearestIndex } = ExplainerChartModel;
    const SVG_NAMESPACE = 'http://www.w3.org/2000/svg';
    const format = formats(documentLocale());
    const instances = new Map();

    function documentLocale() {
      // Format numbers for the document language, falling back when the tag is invalid.
      try {
        return Intl.getCanonicalLocales(document.documentElement.lang || 'en')[0];
      }
      catch {
        return 'en';
      }
    }

    function svgNode(tag, attrs = {}, text) {
      // Create an SVG element and apply its attributes.
      const element = document.createElementNS(SVG_NAMESPACE, tag);
      Object.entries(attrs).forEach(([k, v]) => element.setAttribute(k, String(v)));

      // Populate optional literal text without interpreting markup.
      if (text !== undefined)
        element.textContent = text;
      return element;
    }

    function htmlNode(tag, cls, text) {
      // Create an HTML element and apply its presentation class.
      const element = document.createElement(tag);
      if (cls)
        element.className = cls;

      // Populate optional literal text without interpreting markup.
      if (text !== undefined)
        element.textContent = text;
      return element;
    }

    function summary(record) {
      return record.title + ' — ' + record.rows.map(([k, v]) => k + ': ' + v).join('; ');
    }

    function renderData(state) {
      // Rebuild the legend swatches and any intensity scale for the current data.
      const kind = kinds[state.config.kind];
      const legend = kind.legend(state.config, format);
      const swatches = legend.entries.map(entry => {
        const swatch = htmlNode('i', entry.dashed ? 'dashed' : '');
        swatch.style.setProperty('--legend-color', entry.color);
        swatch.setAttribute('aria-hidden', 'true');
        const span = htmlNode('span');
        span.append(swatch, document.createTextNode(entry.name));
        return span;
      });
      if (legend.scale !== undefined) {
        const scale = htmlNode('span', 'heatmap-scale');
        scale.append(htmlNode('span', '', '0'), htmlNode('i', ''), htmlNode('span', '', format.unit(legend.scale, state.config.unit)));
        swatches.push(scale);
      }
      state.root.querySelector('.chart-legend').replaceChildren(...swatches);

      // Rebuild the accessible data table in original row order.
      const data = kind.table(state.config, format);
      const head = htmlNode('tr');
      data.headers.forEach(h => {
        const th = htmlNode('th', '', h);
        th.scope = 'col';
        head.append(th);
      });
      const body = htmlNode('tbody');
      data.rows.forEach(row => {
        const tr = htmlNode('tr');
        row.forEach(v => tr.append(htmlNode('td', '', format.value(v))));
        body.append(tr);
      });
      const thead = htmlNode('thead');
      thead.append(head);
      const table = htmlNode('table');
      table.append(thead, body);
      state.root.querySelector('.chart-data .table-wrap').replaceChildren(table);
    }

    function mark(state, element, record) {
      // Assign the mark its record index and accessible interaction attributes.
      const i = state.records.length;
      element.setAttribute('data-mark', i);
      element.setAttribute('tabindex', i === 0 ? '0' : '-1');
      element.setAttribute('role', 'button');
      element.setAttribute('aria-label', record.title + '. ' + record.rows.map(([k, v]) => k + ': ' + v).join('; '));

      // Retain the mark with its inspection values and coordinates.
      state.records.push({ ...record, element });
      return element;
    }

    function axisLabelWidth(state, config) {
      // Measure value-axis labels in the font the SVG axis text inherits.
      const labels = valueAxisLabels(config, format);
      const context = labels.length ? document.createElement('canvas').getContext('2d') : null;
      if (!context)
        return 0;
      context.font = '12px ' + getComputedStyle(state.canvas).fontFamily;
      return Math.ceil(Math.max(...labels.map(label => context.measureText(label).width)));
    }

    function draw(state) {
      // Size the SVG to the canvas width and the kind's frame.
      const config = state.config;
      const { height, left } = frame(config.kind);
      const W = Math.max(280, Math.round(state.canvas.clientWidth));
      const H = height;
      const m = { l: Math.max(left, axisLabelWidth(state, config) + 10), r: 18, t: 32, b: 54 };
      const svg = svgNode('svg', { viewBox: `0 0 ${W} ${H}`, role: 'group', 'aria-label': config.title });
      svg.append(svgNode('title', {}, config.title));

      // Reset interaction state before rebuilding chart marks.
      state.records = [];
      state.svg = svg;
      state.dim = { W, H, m };
      state.crosshair = null;
      state.selection = null;
      state.tip.hidden = true;

      // Draw the kind's marks through the plot toolkit.
      kinds[config.kind].draw({
        config,
        data: config.data,
        format,
        W,
        H,
        m,
        plotW: W - m.l - m.r,
        plotH: H - m.t - m.b,
        node: svgNode,
        add: (tag, attrs, text) => svg.appendChild(svgNode(tag, attrs, text)),
        mark: (element, record) => svg.appendChild(mark(state, element, record)),
        overlay() {
          state.crosshair = svgNode('path', { class: 'chart-crosshair', visibility: 'hidden' });
          state.selection = svgNode('circle', { r: 6, class: 'chart-selection', visibility: 'hidden' });
          svg.append(state.crosshair, state.selection);
        }
      });
      state.canvas.replaceChildren(svg);

      // Restore the initial summary and any configured selection.
      const initial = state.records[Math.min(config.selectedIndex ?? 0, state.records.length - 1)];
      if (initial)
        state.status.textContent = summary(initial);
      if (config.selectedIndex !== undefined && state.records[config.selectedIndex])
        highlight(state, config.selectedIndex);
    }

    function highlight(state, index) {
      // Highlight only the selected mark.
      state.records.forEach((record, i) => record.element.classList.toggle('is-active', i === index));
      const record = state.records[index];
      if (!record)
        return;

      // Align series overlays with the selected record.
      if (state.crosshair) {
        const { H, m } = state.dim;
        state.crosshair.setAttribute('d', `M${record.x} ${m.t}V${H - m.b}`);
        state.crosshair.setAttribute('visibility', 'visible');
        state.selection.setAttribute('cx', record.x);
        state.selection.setAttribute('cy', record.y);
        state.selection.setAttribute('visibility', 'visible');
      }
    }

    function show(state, index, event) {
      // Ignore missing records before changing inspection state.
      const record = state.records[index];
      if (!record)
        return;

      // Publish the active record and its accessible summary.
      highlight(state, index);
      state.status.textContent = summary(record);

      // Populate the tooltip with the record title and exact values.
      const title = htmlNode('strong', '', record.title);
      const dl = htmlNode('dl');
      record.rows.forEach(([k, v]) => dl.append(htmlNode('dt', '', k), htmlNode('dd', '', v)));
      state.tip.replaceChildren(title, dl);
      state.tip.hidden = false;

      // Position the tooltip near the pointer or focused mark.
      const root = state.root.getBoundingClientRect();
      const box = state.svg.getBoundingClientRect();
      const markY = box.top - root.top + record.y / state.dim.H * box.height;
      let x = event ? event.clientX - root.left + 14 : box.left - root.left + record.x / state.dim.W * box.width + 14;
      let y = event ? event.clientY - root.top + 14 : markY - state.tip.offsetHeight - 12;

      // Clamp the tooltip to the chart and viewport bounds, flipping above when it would overflow below.
      x = Math.max(8, Math.min(x, state.root.clientWidth - state.tip.offsetWidth - 8));
      const bottom = Math.min(state.root.clientHeight - 8, innerHeight - root.top - 8);
      if (y + state.tip.offsetHeight > bottom)
        y = (event ? event.clientY - root.top : markY) - state.tip.offsetHeight - 12;
      y = Math.max(8, Math.min(y, bottom - state.tip.offsetHeight));
      state.tip.style.left = x + 'px';
      state.tip.style.top = y + 'px';
    }

    function hide(state) {
      // Hide transient inspection and clear active mark styles.
      state.tip.hidden = true;
      state.records.forEach(record => record.element.classList.remove('is-active'));

      // Restore a configured selection or hide transient series overlays.
      if (state.crosshair) {
        if (state.config.selectedIndex !== undefined)
          highlight(state, state.config.selectedIndex);
        else {
          state.crosshair.setAttribute('visibility', 'hidden');
          state.selection.setAttribute('visibility', 'hidden');
        }
      }
    }

    function bind(root) {
      // Read the embedded configuration and register this chart instance.
      const state = {
        root,
        config: JSON.parse(root.dataset.chart),
        canvas: root.querySelector('.chart-canvas'),
        tip: root.querySelector('.chart-tooltip'),
        status: root.querySelector('.chart-status')
      };
      instances.set(state.config.id, state);
      renderData(state);
      draw(state);

      function inspect(e) {
        // Inspect a directly targeted mark when available.
        const el = e.target.closest?.('[data-mark]');
        if (el) {
          show(state, +el.dataset.mark, e);
          return;
        }

        // Restrict nearest-point inspection to kinds that declare it.
        const mode = kinds[state.config.kind].nearest;
        if (!mode)
          return;

        // Translate pointer coordinates into plot coordinates and reject outside hits.
        const b = state.svg.getBoundingClientRect();
        const { W, H, m } = state.dim;
        const point = { x: (e.clientX - b.left) / b.width * W, y: (e.clientY - b.top) / b.height * H };
        if (point.x < m.l || point.x > W - m.r || point.y < m.t || point.y > H - m.b) {
          hide(state);
          return;
        }

        // Show the nearest record using the pointer position.
        show(state, nearestIndex(state.records, point, mode), e);
      }

      // Bind pointer and focus inspection to the canvas.
      state.canvas.addEventListener('pointermove', inspect);
      state.canvas.addEventListener('click', inspect);
      state.canvas.addEventListener('pointerleave', () => {
        const a = document.activeElement;
        if (state.canvas.contains(a) && a.hasAttribute('data-mark'))
          show(state, +a.dataset.mark);
        else
          hide(state);
      });
      state.canvas.addEventListener('focusin', e => {
        if (e.target.hasAttribute('data-mark'))
          show(state, +e.target.dataset.mark);
      });
      state.canvas.addEventListener('focusout', e => {
        if (!state.canvas.contains(e.relatedTarget))
          hide(state);
      });

      state.canvas.addEventListener('keydown', e => {
        // Handle keys only on chart marks.
        const el = e.target.closest?.('[data-mark]');
        if (!el)
          return;

        // Dismiss or explicitly inspect the focused mark.
        const index = +el.dataset.mark;
        if (e.key === 'Escape') {
          hide(state);
          return;
        }
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          show(state, index);
          return;
        }

        // Move the keyboard tab stop and focus using the kind's grid stride.
        const next = nextIndex(e.key, index, state.records.length, kinds[state.config.kind].stride?.(state.config));
        if (next === null)
          return;
        e.preventDefault();
        state.records.forEach(r => r.element.setAttribute('tabindex', '-1'));
        state.records[next].element.setAttribute('tabindex', '0');
        state.records[next].element.focus();
      });

      // Redraw marks once per animation frame after width changes; the legend and table do not depend on width.
      let width = state.canvas.clientWidth;
      let scheduled = false;
      new ResizeObserver(() => {
        const next = state.canvas.clientWidth;
        if (Math.abs(next - width) < 1 || scheduled)
          return;
        width = next;
        scheduled = true;
        requestAnimationFrame(() => {
          scheduled = false;
          draw(state);
        });
      }).observe(state.canvas);
    }

    document.querySelectorAll('[data-chart]').forEach(bind);
    window.ExplainerCharts = {
      /**
       * Apply a shallow configuration patch and redraw an existing chart.
       * @param {string} id Generated chart ID; unknown IDs are ignored.
       * @param {object} patch Fields compatible with the existing chart kind and data.
       *   Values must satisfy the renderer's chart contract; patches are not validated here.
       */
      update(id, patch) {
        // Ignore updates for unknown chart instances.
        const state = instances.get(id);
        if (!state)
          return;

        // Apply the configuration patch and rebuild the chart and its data views.
        Object.assign(state.config, patch);
        renderData(state);
        draw(state);
      }
    };
  })();
