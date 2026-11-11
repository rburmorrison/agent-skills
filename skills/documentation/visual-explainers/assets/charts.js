// Render offline SVG charts with shared exact-value inspection.
(() => {
  const svgNamespace = 'http://www.w3.org/2000/svg';
  const instances = new Map();
  const palette = [
    'var(--accent)',
    'var(--chart-secondary)',
    'var(--chart-third)',
    'var(--chart-fourth)',
    'var(--chart-fifth)'
  ];
  const formatValue = n => typeof n === 'number' && Number.isInteger(n) ? new Intl.NumberFormat('en-US').format(n) : String(n);
  const formatAxisValue = n => formatValue(Number(n.toPrecision(8)));
  const color = i => palette[i % palette.length];

  function svgNode(tag, attrs = {}, text) {
    // Create an SVG element and apply its attributes.
    const element = document.createElementNS(svgNamespace, tag);
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

  function numberUnit(n, unit) {
    return formatValue(n) + (unit ? ' ' + unit : '');
  }

  function dataRows(config) {
    const data = config.data;
    if (config.kind === 'line' || config.kind === 'area')
      return { headers: [config.xLabel || 'Category', ...data.series.map(s => s.name)], rows: data.categories.map((n, i) => [n, ...data.series.map(s => s.values[i])]) };
    if (config.kind === 'bar' || config.kind === 'donut')
      return { headers: ['Category', config.yLabel || config.unit || 'Value'], rows: data.categories.map((n, i) => [n, data.values[i]]) };
    if (config.kind === 'scatter')
      return { headers: ['Observation', config.xLabel, config.yLabel], rows: data.points.map(p => [p.label, p.x, p.y]) };
    if (config.kind === 'histogram')
      return { headers: ['Interval (' + (config.binUnit || 'units') + ')', config.yLabel || 'Count'], rows: data.bins.map(b => [b.low + '–' + b.high, b.count]) };
    if (config.kind === 'heatmap')
      return { headers: [config.yLabel || 'Row', ...data.columns], rows: data.rows.map((r, i) => [r, ...data.values[i]]) };
    if (config.kind === 'box')
      return {
        headers: [
          'Group',
          'Min',
          'Q1',
          'Median',
          'Q3',
          'Max'
        ], rows: data.groups.map(g => [
          g.name,
          g.min,
          g.q1,
          g.median,
          g.q3,
          g.max
        ])
      };
  }

  function table(state) {
    // Build the accessible data-table structure.
    const t = dataRows(state.config);
    const el = htmlNode('table');
    const head = htmlNode('thead');
    const tr = htmlNode('tr');
    const body = htmlNode('tbody');

    // Render column headings before the data rows.
    t.headers.forEach(h => {
      const th = htmlNode('th', '', h);
      th.scope = 'col';
      tr.append(th);
    });
    head.append(tr);

    // Render values in their original row order.
    t.rows.forEach(row => {
      const r = htmlNode('tr');
      row.forEach(v => r.append(htmlNode('td', '', formatValue(v))));
      body.append(r);
    });

    // Replace the chart data view with the completed table.
    el.append(head, body);
    state.root.querySelector('.chart-data .table-wrap').replaceChildren(el);
  }

  function legend(state, entries) {
    // Clear the previous legend before rebuilding its entries.
    const l = state.root.querySelector('.chart-legend');
    l.replaceChildren();

    // Pair each series label with its corresponding visual swatch.
    entries.forEach((name, i) => {
      const span = htmlNode('span');
      const swatch = htmlNode('i', state.config.kind === 'line' && i === 1 ? 'dashed' : '');
      swatch.style.setProperty('--legend-color', color(i));
      swatch.setAttribute('aria-hidden', 'true');
      span.append(swatch, document.createTextNode(name));
      l.append(span);
    });
  }

  function niceStep(value) {
    // Normalize the requested interval to its decimal magnitude.
    const power = 10 ** Math.floor(Math.log10(Math.max(value, 1e-9)));
    const f = value / power;

    // Choose a readable one, two, five, or ten interval.
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * power;
  }

  function domain(values, config = {}) {
    // Include zero and avoid an empty numeric domain.
    let lo = Math.min(0, ...values);
    let hi = Math.max(0, ...values);
    if (lo === hi)
      hi = lo + 1;

    // Pad the domain while retaining zero as a natural boundary.
    const pad = (hi - lo) * .06;
    lo = lo < 0 ? lo - pad : lo;
    hi = hi > 0 ? hi + pad : hi;

    // Round domain bounds unless the configuration supplies explicit limits.
    const step = niceStep((hi - lo) / 4);
    return [config.yMin ?? Math.floor(lo / step) * step, config.yMax ?? Math.ceil(hi / step) * step];
  }

  function ticks(min, max) {
    // Choose a readable tick interval.
    const step = niceStep((max - min) / 5);
    const out = [];

    // Enumerate ticks and normalize near-zero floating-point residue.
    for (let v = Math.ceil(min / step) * step;v <= max + step * .001;v += step)
      out.push(Math.abs(v) < step * .001 ? 0 : v);
    return out;
  }

  function yAxis(svg, config, W, H, m, max, min = 0) {
    // Draw horizontal grid lines with their numeric labels.
    for (const value of ticks(min, max)) {
      const y = H - m.b - (H - m.b - m.t) * (value - min) / (max - min);
      svg.append(
        svgNode('path', { d: `M${m.l} ${y}H${W - m.r}`, class: 'chart-grid' }),
        svgNode(
          'text',
          {
            x: m.l - 10,
            y: y + 4,
            'text-anchor': 'end',
            class: 'chart-axis'
          },
          formatAxisValue(value)
        )
      );
    }

    // Place the configured axis titles outside the plot.
    if (config.yLabel)
      svg.append(svgNode('text', {
        x: m.l,
        y: 16,
        class: 'chart-axis-title'
      }, config.yLabel));
    if (config.xLabel)
      svg.append(svgNode(
        'text',
        {
          x: (m.l + W - m.r) / 2,
          y: H - 5,
          'text-anchor': 'middle',
          class: 'chart-axis-title'
        },
        config.xLabel
      ));
  }

  function labelX(svg, label, x, y) {
    svg.append(svgNode('text', {
      x,
      y,
      'text-anchor': 'middle',
      class: 'chart-axis'
    }, label));
  }

  function barLabel(svg, label, x, y, width) {
    // Use a single line when the category label fits.
    const text = String(label);
    const size = Math.max(3, Math.floor((width - 8) / 6.6));
    if (text.length <= size) {
      labelX(svg, text, x, y);
      return;
    }

    // Wrap longer labels into approximate character-width lines.
    const words = text.split(/\s+/);
    const lines = [];
    let line = '';
    for (const word of words) {
      if ((line + ' ' + word).trim().length > size && line) {
        lines.push(line);
        line = word;
      }
      else
        line = (line + ' ' + word).trim();
    }
    if (line)
      lines.push(line);

    // Split an overlong unbroken label before drawing two lines.
    if (lines.length === 1 && text.length > size) {
      lines[0] = text.slice(0, size);
      lines[1] = text.slice(size);
    }

    // Draw at most two lines while retaining the full label in its title.
    const el = svgNode('text', {
      x,
      y,
      'text-anchor': 'middle',
      class: 'chart-axis'
    });
    el.append(svgNode('title', {}, text));
    lines.slice(0, 2).forEach((l, i) => el.append(svgNode('tspan', { x, dy: i ? 14 : 0 }, l.length > size ? l.slice(0, Math.max(1, size - 1)) + '…' : l)));
    svg.append(el);
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

  function render(state) {
    // Measure the canvas and create the chart SVG.
    const config = state.config;
    const data = config.data;
    const host = state.canvas;
    const W = Math.max(280, Math.round(host.clientWidth));
    const H = config.kind === 'heatmap' ? 310 : 320;
    const m = {
      l: config.kind === 'heatmap' ? 92 : 54,
      r: 18,
      t: 32,
      b: 54
    };
    const svg = svgNode('svg', {
      viewBox: `0 0 ${W} ${H}`,
      role: 'group',
      'aria-label': config.title
    });
    svg.append(svgNode('title', {}, config.title));

    // Reset interaction state before rebuilding chart marks.
    state.records = [];
    state.svg = svg;
    state.dim = {
      W,
      H,
      m
    };
    state.crosshair = null;
    state.selection = null;
    state.active = -1;
    state.tip.hidden = true;

    // Calculate the usable plot area and select the chart variant.
    const plotW = W - m.l - m.r;
    const plotH = H - m.t - m.b;
    const series = config.kind === 'line' || config.kind === 'area';
    if (series) {
      // Map series categories and values into plot coordinates.
      const n = data.categories.length;
      const [min, max] = domain(data.series.flatMap(s => s.values), config);
      const x = i => m.l + (n === 1 ? plotW / 2 : plotW * i / (n - 1));
      const y = v => H - m.b - plotH * (v - min) / (max - min);
      yAxis(svg, config, W, H, m, max, min);
      legend(state, data.series.length > 1 ? data.series.map(s => s.name) : []);

      // Thin category labels to the available horizontal space.
      const slots = Math.max(2, Math.min(n, Math.floor(plotW / (Math.max(...data.categories.map(v => String(v).length)) * 6.8 + 18))));
      const shown = new Set(Array.from({ length: slots }, (_, i) => Math.round(i * (n - 1) / (slots - 1))));
      data.categories.forEach((v, i) => {
        if (shown.has(i))
          labelX(svg, v, x(i), H - m.b + 22);
      });

      // Reserve a transparent hit target for nearest-point inspection.
      const hit = svgNode(
        'rect',
        {
          x: m.l,
          y: m.t,
          width: plotW,
          height: plotH,
          fill: 'transparent',
          'data-plot-hit': 'true'
        }
      );
      svg.append(hit);

      // Draw series paths and optional area fills beneath the marks.
      data.series.forEach((s, j) => {
        const points = s.values.map((v, i) => [x(i), y(v)]);
        const path = points.map((p, i) => (i ? 'L' : 'M') + p.join(' ')).join(' ');
        if (config.kind === 'area')
          svg.append(svgNode(
            'path',
            {
              d: path + `L${x(n - 1)} ${y(0)}L${x(0)} ${y(0)}Z`,
              fill: color(j),
              opacity: .16,
              'pointer-events': 'none'
            }
          ));
        svg.append(svgNode(
          'path',
          {
            d: path,
            class: 'chart-line',
            stroke: color(j),
            'stroke-dasharray': j === 1 ? '6 4' : 'none',
            'pointer-events': 'none'
          }
        ));
      });

      // Register one inspection mark per category with all series values.
      data.categories.forEach((label, i) => {
        const el = svgNode(
          'circle',
          {
            cx: x(i),
            cy: y(data.series[0].values[i]),
            r: 4,
            fill: color(0),
            stroke: 'var(--paper)',
            'stroke-width': 1.5
          }
        );
        svg.append(mark(
          state,
          el,
          {
            title: (config.pointPrefix || '') + label,
            rows: data.series.map(s => [s.name, numberUnit(s.values[i], config.unit)]),
            x: x(i),
            y: y(data.series[0].values[i])
          }
        ));
      });

      // Create the crosshair and selection overlays above the series.
      state.crosshair = svgNode('path', { class: 'chart-crosshair', visibility: 'hidden' });
      state.selection = svgNode('circle', {
        r: 6,
        class: 'chart-selection',
        visibility: 'hidden'
      });
      svg.append(state.crosshair, state.selection);
    }
    else if (config.kind === 'bar' || config.kind === 'histogram') {
      // Map bar values or histogram counts onto a shared numeric axis.
      const hist = config.kind === 'histogram';
      const values = hist ? data.bins.map(b => b.count) : data.values;
      const n = values.length;
      const [min, max] = domain(values, config);
      const step = plotW / n;
      const yAt = v => H - m.b - plotH * (v - min) / (max - min);
      const zero = yAt(0);
      yAxis(svg, config, W, H, m, max, min);
      legend(state, []);

      // Draw each value as an inspectable bar or bin.
      values.forEach((v, i) => {
        const x = m.l + i * step + (hist ? 1 : step * .17);
        const width = hist ? step - 2 : step * .66;
        const y = Math.min(zero, yAt(v));
        const label = hist ? `${data.bins[i].low}–${data.bins[i].high} ${config.binUnit || ''}` : data.categories[i];
        const el = svgNode(
          'rect',
          {
            x,
            y,
            width: Math.max(1, width),
            height: Math.abs(yAt(v) - zero),
            rx: hist ? 1 : 4,
            fill: 'var(--accent)',
            opacity: .86
          }
        );
        svg.append(mark(
          state,
          el,
          {
            title: label,
            rows: [[config.yLabel || 'Value', numberUnit(v, config.unit)]],
            x: x + width / 2,
            y
          }
        ));

        // Label bin boundaries or wrap the category text below the mark.
        if (hist) {
          if (i === 0)
            labelX(svg, data.bins[i].low, m.l, H - m.b + 22);
          if (W > 450 || i % 2 === 1 || i === n - 1)
            labelX(svg, data.bins[i].high, m.l + (i + 1) * step, H - m.b + 22);
        }
        else {
          barLabel(svg, label, x + width / 2, H - m.b + 20, step);
        }
      });
    }
    else if (config.kind === 'scatter') {
      // Map both scatter coordinates onto numeric axes.
      const [xmin, xmax] = domain(data.points.map(p => p.x));
      const [ymin, ymax] = domain(data.points.map(p => p.y), config);
      yAxis(svg, config, W, H, m, ymax, ymin);
      legend(state, []);
      for (const v of ticks(xmin, xmax))
        labelX(svg, formatAxisValue(v), m.l + plotW * (v - xmin) / (xmax - xmin), H - m.b + 22);
      svg.append(svgNode(
        'rect',
        {
          x: m.l,
          y: m.t,
          width: plotW,
          height: plotH,
          fill: 'transparent',
          'data-plot-hit': 'true'
        }
      ));

      // Draw an inspectable mark for each scatter observation.
      data.points.forEach(p => {
        const x = m.l + plotW * (p.x - xmin) / (xmax - xmin);
        const y = H - m.b - plotH * (p.y - ymin) / (ymax - ymin);
        const el = svgNode('circle', {
          cx: x,
          cy: y,
          r: 5,
          fill: 'var(--accent)',
          opacity: .85
        });
        svg.append(mark(
          state,
          el,
          {
            title: p.label,
            rows: [[config.xLabel, numberUnit(p.x, config.xUnit)], [config.yLabel, numberUnit(p.y, config.unit)]],
            x,
            y
          }
        ));
      });
    }
    else if (config.kind === 'donut') {
      // Measure the donut total and establish its ring coordinates.
      const total = data.values.reduce((a, b) => a + b, 0);
      const cx = W / 2;
      const cy = H / 2 - 8;
      const r = 101;
      const inner = 62;
      let angle = -Math.PI / 2;
      legend(state, data.categories);
      const at = (radius, a) => [cx + Math.cos(a) * radius, cy + Math.sin(a) * radius];

      // Draw inspectable ring segments in category order.
      data.values.forEach((v, i) => {
        const end = angle + Math.min(v / total * Math.PI * 2, Math.PI * 2 - 0.00001);
        const large = end - angle > Math.PI ? 1 : 0;
        const p1 = at(r, angle);
        const p2 = at(r, end);
        const p3 = at(inner, end);
        const p4 = at(inner, angle);
        const path = `M${p1}A${r} ${r} 0 ${large} 1 ${p2}L${p3}A${inner} ${inner} 0 ${large} 0 ${p4}Z`;
        const mid = (angle + end) / 2;
        const pos = at((r + inner) / 2, mid);
        const el = svgNode(
          'path',
          {
            d: path,
            fill: color(i),
            stroke: 'var(--paper)',
            'stroke-width': 3
          }
        );
        svg.append(mark(
          state,
          el,
          {
            title: data.categories[i],
            rows: [[config.valueLabel || config.yLabel || 'Value', numberUnit(v, config.unit)], ['Share', (v / total * 100).toFixed(1) + '%']],
            x: pos[0],
            y: pos[1]
          }
        ));
        angle = end;
      });

      // Label the center of the donut with its total and unit.
      svg.append(
        svgNode(
          'text',
          {
            x: cx,
            y: cy - 2,
            'text-anchor': 'middle',
            fill: 'var(--ink)',
            'font-size': 26,
            'font-weight': 700
          },
          formatValue(total)
        ),
        svgNode(
          'text',
          {
            x: cx,
            y: cy + 22,
            'text-anchor': 'middle',
            class: 'chart-axis'
          },
          config.unit + ' Total'
        )
      );
    }
    else if (config.kind === 'heatmap') {
      // Measure the heatmap cell grid and its value range.
      const rows = data.rows.length;
      const cols = data.columns.length;
      const max = Math.max(1, ...data.values.flat());
      const cw = plotW / cols;
      const ch = plotH / rows;
      legend(state, []);

      // Draw a value-intensity legend for the heatmap.
      const scale = htmlNode('span', 'heatmap-scale');
      scale.append(
        htmlNode('span', '', '0'),
        htmlNode('i', ''),
        htmlNode('span', '', numberUnit(Math.max(...data.values.flat()), config.unit))
      );
      state.root.querySelector('.chart-legend').append(scale);

      // Draw each heatmap row label before its inspectable cells.
      data.rows.forEach((row, ri) => {
        svg.append(svgNode(
          'text',
          {
            x: m.l - 9,
            y: m.t + (ri + .5) * ch + 4,
            'text-anchor': 'end',
            class: 'chart-axis'
          },
          W < 450 ? row.slice(0, 3) : row
        ));

        // Draw cell intensity and register its exact-value inspection.
        data.columns.forEach((col, ci) => {
          const v = data.values[ri][ci];
          const x = m.l + ci * cw + 2;
          const y = m.t + ri * ch + 2;
          const el = svgNode(
            'rect',
            {
              x,
              y,
              width: Math.max(1, cw - 4),
              height: ch - 4,
              rx: 3,
              fill: 'var(--accent)',
              opacity: .12 + .82 * v / max
            }
          );
          svg.append(mark(
            state,
            el,
            {
              title: row + ' · ' + col,
              rows: [[config.valueLabel || 'Value', numberUnit(v, config.unit)]],
              x: x + cw / 2 - 2,
              y: y + ch / 2 - 2
            }
          ));

          // Overlay values only when the cell is wide enough.
          if (cw > 48)
            svg.append(svgNode(
              'text',
              {
                x: x + cw / 2 - 2,
                y: y + ch / 2 + 2,
                'text-anchor': 'middle',
                fill: 'var(--ink)',
                'font-size': 11,
                'pointer-events': 'none'
              },
              v
            ));
        });
      });

      // Thin column labels and add the heatmap axis title.
      data.columns.forEach((col, i) => {
        if (W >= 450 || i % 2 === 0)
          labelX(svg, col, m.l + (i + .5) * cw, H - m.b + 22);
      });
      svg.append(svgNode(
        'text',
        {
          x: (m.l + W - m.r) / 2,
          y: H - 5,
          'text-anchor': 'middle',
          class: 'chart-axis-title'
        },
        config.xLabel
      ));
    }
    else if (config.kind === 'box') {
      // Map five-number summaries onto a shared numeric axis.
      const [min, max] = domain(data.groups.flatMap(g => [g.min, g.max]), config);
      const y = v => H - m.b - plotH * (v - min) / (max - min);
      const step = plotW / data.groups.length;
      legend(state, []);
      yAxis(svg, config, W, H, m, max, min);

      // Draw each inspectable box, whiskers, and median.
      data.groups.forEach((g, i) => {
        const x = m.l + (i + .5) * step;
        const bw = Math.min(64, step * .58);
        const el = svgNode('g');
        el.append(
          svgNode(
            'rect',
            {
              x: x - bw / 2 - 6,
              y: y(g.max) - 5,
              width: bw + 12,
              height: y(g.min) - y(g.max) + 10,
              fill: 'transparent'
            }
          ),
          svgNode(
            'path',
            {
              d: `M${x} ${y(g.max)}V${y(g.min)}M${x - bw * .3} ${y(g.max)}H${x + bw * .3}M${x - bw * .3} ${y(g.min)}H${x + bw * .3}`,
              stroke: 'var(--accent)',
              'stroke-width': 2,
              fill: 'none'
            }
          ),
          svgNode(
            'rect',
            {
              x: x - bw / 2,
              y: y(g.q3),
              width: bw,
              height: y(g.q1) - y(g.q3),
              fill: 'var(--wash)',
              stroke: 'var(--accent)',
              'stroke-width': 2,
              rx: 3
            }
          ),
          svgNode('path', {
            d: `M${x - bw / 2} ${y(g.median)}H${x + bw / 2}`,
            stroke: 'var(--accent)',
            'stroke-width': 3
          })
        );
        svg.append(mark(
          state,
          el,
          {
            title: g.name,
            rows: [
              ['Minimum', numberUnit(g.min, config.unit)],
              ['Q1', numberUnit(g.q1, config.unit)],
              ['Median', numberUnit(g.median, config.unit)],
              ['Q3', numberUnit(g.q3, config.unit)],
              ['Maximum', numberUnit(g.max, config.unit)]
            ],
            x,
            y: y(g.median)
          }
        ));

        // Label the group beneath its box.
        labelX(svg, g.name, x, H - m.b + 22);
      });
    }

    // Publish the completed SVG and accessible data table.
    host.replaceChildren(svg);
    table(state);

    // Restore the initial summary and any configured selection.
    const initial = state.records[Math.min(config.selectedIndex ?? 0, state.records.length - 1)];
    if (initial)
      state.status.textContent = summary(initial);
    if (config.selectedIndex !== undefined && state.records[config.selectedIndex])
      highlight(state, config.selectedIndex);
  }

  function summary(record) {
    return record.title + ' — ' + record.rows.map(([k, v]) => k + ': ' + v).join('; ');
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
    state.active = index;
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
    let x;
    let y;
    if (event) {
      x = event.clientX - root.left + 14;
      y = event.clientY - root.top + 14;
    }
    else {
      x = box.left - root.left + record.x / state.dim.W * box.width + 14;
      y = box.top - root.top + record.y / state.dim.H * box.height - state.tip.offsetHeight - 12;
    }

    // Clamp the tooltip to the chart and viewport bounds.
    x = Math.max(8, Math.min(x, state.root.clientWidth - state.tip.offsetWidth - 8));
    const bottom = Math.min(state.root.clientHeight - 8, innerHeight - root.top - 8);
    if (y + state.tip.offsetHeight > bottom)
      y = (event ? event.clientY - root.top : box.top - root.top + record.y / state.dim.H * box.height) - state.tip.offsetHeight - 12;
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
  document.querySelectorAll('[data-chart]').forEach(root => {
    // Read the embedded configuration and register this chart instance.
    const state = {
      root,
      config: JSON.parse(root.dataset.chart),
      canvas: root.querySelector('.chart-canvas'),
      tip: root.querySelector('.chart-tooltip'),
      status: root.querySelector('.chart-status')
    };
    instances.set(state.config.id, state);
    render(state);

    function inspect(e) {
      // Inspect a directly targeted mark when available.
      const el = e.target.closest?.('[data-mark]');
      if (el) {
        show(state, +el.dataset.mark, e);
        return;
      }

      // Restrict nearest-point inspection to supported chart kinds.
      if (!['line', 'area', 'scatter'].includes(state.config.kind))
        return;

      // Translate pointer coordinates into plot coordinates and reject outside hits.
      const b = state.svg.getBoundingClientRect();
      const { W, H, m } = state.dim;
      const x = (e.clientX - b.left) / b.width * W;
      const y = (e.clientY - b.top) / b.height * H;
      if (x < m.l || x > W - m.r || y < m.t || y > H - m.b) {
        hide(state);
        return;
      }

      // Find the nearest record by horizontal or Euclidean distance.
      let best = 0;
      let dist = Infinity;
      state.records.forEach((r, i) => {
        const n = state.config.kind === 'scatter' ? Math.hypot(x - r.x, y - r.y) : Math.abs(x - r.x);
        if (n < dist) {
          dist = n;
          best = i;
        }
      });

      // Show the nearest record using the pointer position.
      show(state, best, e);
    }

    // Bind pointer and focus inspection to the canvas.
    state.canvas.addEventListener('pointermove', inspect);
    state.canvas.addEventListener('click', inspect);
    state.canvas.addEventListener(
      'pointerleave',
      () => {
        const a = document.activeElement;
        if (state.canvas.contains(a) && a.hasAttribute('data-mark'))
          show(state, +a.dataset.mark);
        else
          hide(state);
      }
    );
    state.canvas.addEventListener(
      'focusin',
      e => {
        if (e.target.hasAttribute('data-mark'))
          show(state, +e.target.dataset.mark);
      }
    );
    state.canvas.addEventListener(
      'focusout',
      e => {
        if (!state.canvas.contains(e.relatedTarget))
          hide(state);
      }
    );

    // Support keyboard movement and explicit inspection of chart marks.
    state.canvas.addEventListener(
      'keydown',
      e => {
        // Inspect a directly targeted mark when available.
        const el = e.target.closest?.('[data-mark]');
        if (!el)
          return;

        // Select the next record using chart-specific keyboard rules.
        let i = +el.dataset.mark;
        let n = state.records.length;
        if (state.config.kind === 'heatmap' && ['ArrowDown', 'ArrowUp'].includes(e.key)) {
          const stride = state.config.data.columns.length;
          i = (i + (e.key === 'ArrowDown' ? stride : n - stride)) % n;
        }
        else if (['ArrowRight', 'ArrowDown'].includes(e.key))
          i = (i + 1) % n;
        else if (['ArrowLeft', 'ArrowUp'].includes(e.key))
          i = (i + n - 1) % n;
        else if (e.key === 'Home')
          i = 0;
        else if (e.key === 'End')
          i = n - 1;
        else if (e.key === 'Escape') {
          hide(state);
          return;
        }
        else if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          show(state, i);
          return;
        }
        else
          return;

        // Move the keyboard tab stop and focus to the selected mark.
        e.preventDefault();
        state.records.forEach(r => r.element.setAttribute('tabindex', '-1'));
        state.records[i].element.setAttribute('tabindex', '0');
        state.records[i].element.focus();
      }
    );

    // Coalesce width changes into one chart render per animation frame.
    let width = state.canvas.clientWidth;
    let scheduled = false;
    new ResizeObserver(() => {
      // Ignore negligible width changes before scheduling a render.
      const next = state.canvas.clientWidth;
      if (Math.abs(next - width) < 1)
        return;

      // Remember the new width and schedule the pending render once.
      width = next;
      if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(() => {
          scheduled = false;
          render(state);
        });
      }
    }).observe(state.canvas);
  });
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

      // Apply the configuration patch and rebuild the chart.
      Object.assign(state.config, patch);
      render(state);
    }
  };
})();
