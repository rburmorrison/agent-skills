// Hexfield theme set: a pointer-responsive hex field behind the page and a sectioned
// reading-progress bar. Field math stays independent of the DOM so it can be verified directly.
const ExplainerHexfield = (() => {
  const FIELD = {
    // Cell spacing and drawn radius, which leaves a thin gap between neighbors.
    spacing: 28,
    radius: 26,

    // Resting cells hold full strength over the outer fraction of the page width on each
    // side, then fade out by the edge fraction.
    plateau: 0.06,
    edge: 0.26,

    // Resting cells also fill a band behind the title that fades out downward.
    heroStrength: 0.75,

    // Effects keep this share of their strength where resting cells are clear,
    // so the pointer stays visible behind the text column without crowding it.
    reveal: 0.35,

    hover: { reach: 150, attack: 0.06, release: 0.45, line: 0.28, fill: 0.04 },
    trail: { width: 64, fade: 0.9, line: 0.36, fill: 0.08 },
    push: { reach: 130, distance: 5, spring: 0.12 },
    ripple: { speed: 520, band: 34, life: 1.6, glow: 70, glowLife: 0.5, line: 0.45, fill: 0.06 },

    // Energetic cells shrink slightly, and no effect line exceeds this opacity.
    shrink: 0.07,
    maxLine: 0.6
  };

  /**
   * Ease a value from 0 to 1 between two edges.
   * @param {number} start Input where the result is 0.
   * @param {number} end Input where the result is 1; differs from start.
   * @param {number} value Input to ease.
   * @returns {number} Smoothstep of value, clamped to 0–1.
   */
  function smoothstep(start, end, value) {
    const t = Math.min(1, Math.max(0, (value - start) / (end - start)));
    return t * t * (3 - 2 * t);
  }

  /**
   * Weight a resting cell by its distance from the page sides and the title band.
   * @param {number} x Cell center from the page's left edge, in CSS pixels.
   * @param {number} y Cell center from the document top, in CSS pixels.
   * @param {number} width Page width in CSS pixels, greater than zero.
   * @param {number} heroBottom Document offset where the title band has faded out; 0 for none.
   * @returns {number} Resting strength from 0 (clear) to 1 (full).
   */
  function restWeight(x, y, width, heroBottom) {
    // Hold the sides at full strength near each edge, then fade them clear toward the center.
    const fromSide = Math.max(0, Math.min(x, width - x) / width);
    const side = Math.pow(1 - smoothstep(FIELD.plateau, FIELD.edge, fromSide), 1.3);

    // Add the title band, which begins fading a fifth of the way down.
    const band = heroBottom > 0
      ? FIELD.heroStrength * (1 - smoothstep(heroBottom * 0.2, heroBottom, y))
      : 0;

    return Math.max(side, band);
  }

  /**
   * Measure the strength a pointer lends a cell within hover reach.
   * @param {number} distance Distance from cell center to pointer, in CSS pixels.
   * @returns {number} 1 under the pointer, easing to 0 at the reach.
   */
  function hoverTarget(distance) {
    const q = Math.max(0, 1 - distance / FIELD.hover.reach);
    return q * q;
  }

  /**
   * Measure a cell's closeness to the latest drag segment.
   * @param {number} px Cell center x.
   * @param {number} py Cell center y.
   * @param {number[]} segment Drag segment as [ax, ay, bx, by], in the same coordinates.
   * @returns {number} 1 on the segment, easing to 0 at the trail width.
   */
  function trailTarget(px, py, segment) {
    // Project the cell onto the segment, clamped to its endpoints.
    const [ax, ay, bx, by] = segment;
    const vx = bx - ax;
    const vy = by - ay;
    const length = vx * vx + vy * vy;
    const u = length > 0 ? Math.max(0, Math.min(1, ((px - ax) * vx + (py - ay) * vy) / length)) : 0;

    // Ease the distance to that point across the trail width.
    const q = Math.max(0, 1 - Math.hypot(ax + vx * u - px, ay + vy * u - py) / FIELD.trail.width);
    return q * q;
  }

  /**
   * Measure how strongly a ripple lights a cell at a moment in its life.
   * @param {number} distance Distance from the press to the cell, in CSS pixels.
   * @param {number} age Seconds since the press, at least 0.
   * @param {boolean} reduced Whether the reader prefers reduced motion.
   * @returns {number} Strength from 0 to 1; a reduced ripple is a brief glow in place.
   */
  function rippleStrength(distance, age, reduced) {
    const r = FIELD.ripple;

    // Glow around the press without motion when the reader prefers it.
    if (reduced)
      return age < r.glowLife && distance < r.glow ? (1 - distance / r.glow) * (1 - age / r.glowLife) : 0;

    // Light a band at the expanding front that weakens with age and distance.
    if (age >= r.life)
      return 0;
    const band = (distance - age * r.speed) / r.band;
    const fade = 1 - age / r.life;
    return Math.exp(-band * band) * fade * fade * Math.max(0.25, 1 - distance / 900);
  }

  /**
   * Fill one progress segment per page section, agreeing with the highlighted contents entry.
   * @param {number[]} starts Ascending document offsets where each section begins; the first is 0.
   * @param {number} total Document height, greater than the last start.
   * @param {number} position Document offset of the reading line.
   * @param {number} current Index of the section being read.
   * @param {boolean} atEnd Whether the page is scrolled to its end, or cannot scroll.
   * @returns {number[]} Fill from 0 to 1 for each section: earlier sections are full, later
   *   ones empty, and the current one fills as the reading line crosses it. Every section
   *   is full at the end, since the reading line may never reach the last ones.
   */
  function sectionFills(starts, total, position, current, atEnd) {
    return starts.map((start, index) => {
      if (atEnd || index < current)
        return 1;
      if (index > current)
        return 0;

      // Fill the current section by how far the reading line has crossed it.
      const end = index + 1 < starts.length ? starts[index + 1] : total;
      return end > start ? Math.min(1, Math.max(0, (position - start) / (end - start))) : 1;
    });
  }

  /**
   * Draw the field behind the page and the sectioned progress bar in the header.
   * @param {Document} document Rendered explainer document using the hexfield theme set.
   */
  function bind(document) {
    const view = document.defaultView;
    const root = document.documentElement;
    const body = document.body;
    const reducedMotion = view.matchMedia('(prefers-reduced-motion:reduce)');
    const darkScheme = view.matchMedia('(prefers-color-scheme:dark)');

    // Add the canvas behind every page element and the bar inside the sticky header.
    const canvas = document.createElement('canvas');
    canvas.className = 'hexfield-canvas';
    canvas.setAttribute('aria-hidden', 'true');
    body.prepend(canvas);
    const context = canvas.getContext('2d');
    const bar = document.createElement('div');
    bar.className = 'hexfield-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.querySelector('header').append(bar);

    const dx = Math.sqrt(3) * FIELD.spacing;
    const dy = 1.5 * FIELD.spacing;
    const hexagon = [0, 1, 2, 3, 4, 5].map(i => {
      const angle = Math.PI / 180 * (60 * i - 90);
      return [Math.cos(angle), Math.sin(angle)];
    });
    let page = { width: 1, height: 1, columns: 0, rows: 0, heroBottom: 0 };
    let cells = null;
    let colors = null;
    let sectionElements = [];
    let sections = [];
    let segments = [];
    const pointer = { clientX: 0, clientY: 0, inside: false, down: false, previous: null };
    let ripples = [];
    let frame = 0;
    let lastTime = 0;

    function readColors() {
      // Resolve the stylesheet's line color (with its resting opacity) and the accent
      // through computed styles, which apply the current appearance's light-dark() value.
      const style = view.getComputedStyle(canvas);
      const channels = value => (value.match(/[\d.]+/g) || []).map(Number);
      const [r, g, b, a = 1] = channels(style.color);
      const accent = channels(style.caretColor).slice(0, 3);
      const dark = view.getComputedStyle(root).colorScheme.includes('dark');

      // Pale pages swallow thin accent lines, so the light appearance draws effects harder.
      colors = {
        line: `${r},${g},${b}`,
        rest: a,
        accent: accent.join(','),
        strength: dark ? 1 : 1.15,
        fill: dark ? 1 : 1.8
      };
    }

    function layout() {
      // Measure the page, the title band, and each section's starting offset.
      const width = root.clientWidth;
      const height = Math.max(root.scrollHeight, view.innerHeight);
      const hero = document.querySelector('main > .hero');
      const heroBottom = hero ? hero.getBoundingClientRect().bottom + view.scrollY + 60 : 0;
      sectionElements = [...document.querySelectorAll('main > section')];
      sections = sectionElements.map((section, index) =>
        index === 0 ? 0 : section.getBoundingClientRect().top + view.scrollY);

      // Rebuild cell state only when the field's extent changes, so effects survive scrolling.
      if (width !== page.width || height !== page.height || heroBottom !== page.heroBottom || !cells) {
        const columns = Math.ceil((width + dx) / dx) + 2;
        const rows = Math.ceil((height + FIELD.spacing) / dy) + 2;
        page = { width, height, columns, rows, heroBottom };
        const size = columns * rows;
        cells = { rest: new Float32Array(size), hover: new Float32Array(size), trail: new Float32Array(size),
          ox: new Float32Array(size), oy: new Float32Array(size) };
        for (let row = 0; row < rows; row++)
          for (let column = 0; column < columns; column++) {
            const [x, y] = center(row, column);
            cells.rest[row * columns + column] = restWeight(x, y, width, heroBottom);
          }
      }

      // Size the canvas to the viewport at the display's pixel density.
      const ratio = Math.min(view.devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(view.innerHeight * ratio);

      // Give the progress bar one segment per section, weighted by its share of the page.
      if (segments.length !== sections.length) {
        bar.replaceChildren(...sections.map(() => {
          const segment = document.createElement('span');
          segment.append(document.createElement('i'));
          return segment;
        }));
        segments = [...bar.children];
      }
      segments.forEach((segment, index) => {
        const end = index + 1 < sections.length ? sections[index + 1] : height;
        segment.style.flexGrow = String(Math.max(1, Math.round(end - sections[index])));
      });
    }

    function center(row, column) {
      // Offset odd rows by half a cell; row and column 0 sit one cell beyond the top-left edge.
      const r = row - 1;
      return [(column - 1) * dx + (r & 1 ? dx / 2 : 0), r * dy];
    }

    function visibleRows() {
      // Cover the viewport plus one cell of overhang above and below.
      const top = view.scrollY;
      return [
        Math.max(0, Math.floor((top - FIELD.spacing) / dy) + 1),
        Math.min(page.rows - 1, Math.ceil((top + view.innerHeight + FIELD.spacing) / dy) + 1)
      ];
    }

    function isEmptySpace(target) {
      // Only the page ground starts effects, so text selection, links, and controls behave as usual.
      return target === body || target === root || target === canvas ||
        (target instanceof view.Element && target.matches('.layout, main, main > section, .content-stack, .contents-slot, aside'));
    }

    function step(time) {
      frame = 0;
      const seconds = Math.min(0.05, Math.max(0, (time - lastTime) / 1000));
      lastTime = time;

      // Locate the pointer in document coordinates and extend any drag segment.
      const px = pointer.clientX;
      const py = pointer.clientY + view.scrollY;
      let segment = null;
      if (pointer.down && pointer.inside) {
        const from = pointer.previous || [px, py];
        segment = [from[0], from[1], px, py];
        pointer.previous = [px, py];
      }

      // Precompute this frame's easing rates from the elapsed time.
      const attack = 1 - Math.exp(-seconds / FIELD.hover.attack);
      const release = 1 - Math.exp(-seconds / FIELD.hover.release);
      const fade = Math.exp(-seconds / FIELD.trail.fade);
      const spring = 1 - Math.exp(-seconds / FIELD.push.spring);
      const reduced = reducedMotion.matches;
      const now = time / 1000;
      ripples = ripples.filter(r => now - r.time < (reduced ? FIELD.ripple.glowLife : FIELD.ripple.life));

      // Advance hover, trail, and push for visible cells, noting whether anything still moves.
      let moving = ripples.length > 0 || pointer.down;
      const [firstRow, lastRow] = visibleRows();
      for (let row = firstRow; row <= lastRow; row++)
        for (let column = 0; column < page.columns; column++) {
          const index = row * page.columns + column;
          const [x, y] = center(row, column);

          const target = pointer.inside ? hoverTarget(Math.hypot(x - px, y - py)) : 0;
          cells.hover[index] += (target - cells.hover[index]) * (target > cells.hover[index] ? attack : release);

          cells.trail[index] *= fade;
          let pushX = 0;
          let pushY = 0;
          if (segment) {
            cells.trail[index] = Math.max(cells.trail[index], trailTarget(x, y, segment));
            const distance = Math.hypot(x - px, y - py);
            if (!reduced && distance > 0.01 && distance < FIELD.push.reach) {
              const q = 1 - distance / FIELD.push.reach;
              pushX = (x - px) / distance * q * q * FIELD.push.distance;
              pushY = (y - py) / distance * q * q * FIELD.push.distance;
            }
          }
          cells.ox[index] += (pushX - cells.ox[index]) * spring;
          cells.oy[index] += (pushY - cells.oy[index]) * spring;

          if (cells.hover[index] > 0.003 || cells.trail[index] > 0.003 ||
            Math.abs(cells.ox[index]) > 0.05 || Math.abs(cells.oy[index]) > 0.05)
            moving = true;
        }

      // Paint after the shell's contents spy has run this frame, and keep animating only
      // while an effect is still settling.
      updateProgress();
      paint(firstRow, lastRow, now, reduced);
      if (moving)
        wake();
    }

    function paint(firstRow, lastRow, now, reduced) {
      // Draw in document coordinates shifted by the scroll offset.
      const ratio = canvas.width / page.width;
      const snap = value => (Math.round(value * ratio - 0.5) + 0.5) / ratio;
      context.setTransform(ratio, 0, 0, ratio, 0, -view.scrollY * ratio);
      context.clearRect(0, view.scrollY, page.width, view.innerHeight);
      context.lineWidth = 1;
      context.lineJoin = 'round';

      for (let row = firstRow; row <= lastRow; row++)
        for (let column = 0; column < page.columns; column++) {
          const index = row * page.columns + column;
          const [x, y] = center(row, column);

          // Combine the cell's hover, trail, and strongest ripple.
          let ripple = 0;
          for (const r of ripples)
            ripple = Math.max(ripple, rippleStrength(Math.hypot(x - r.x, y - r.y), now - r.time, reduced));
          const energy = Math.min(1, cells.hover[index] * 0.9 + cells.trail[index] + ripple);
          const restLine = colors.rest * cells.rest[index];
          if (restLine < 0.002 && energy < 0.003)
            continue;

          // Show effects more quietly where resting cells are clear.
          const reveal = (FIELD.reveal + (1 - FIELD.reveal) * cells.rest[index]) * colors.strength;
          const line = Math.min(FIELD.maxLine, (cells.hover[index] * FIELD.hover.line +
            cells.trail[index] * FIELD.trail.line + ripple * FIELD.ripple.line) * reveal);
          const fill = (cells.hover[index] * FIELD.hover.fill + cells.trail[index] * FIELD.trail.fill +
            ripple * FIELD.ripple.fill) * reveal * colors.fill;

          // Trace the shrunken, pushed hexagon with its corners on device-pixel centers, so the
          // 1px vertical sides draw crisp instead of as two half-strength columns.
          const radius = FIELD.radius * (1 - FIELD.shrink * energy);
          const cx = x + cells.ox[index];
          const cy = y + cells.oy[index];
          context.beginPath();
          hexagon.forEach(([hx, hy], k) => {
            const px = snap(cx + hx * radius);
            const py = snap(cy + hy * radius - view.scrollY) + view.scrollY;
            if (k)
              context.lineTo(px, py);
            else
              context.moveTo(px, py);
          });
          context.closePath();
          if (fill > 0.002) {
            context.fillStyle = `rgba(${colors.accent},${fill.toFixed(3)})`;
            context.fill();
          }
          if (restLine > 0.002) {
            context.strokeStyle = `rgba(${colors.line},${restLine.toFixed(3)})`;
            context.stroke();
          }
          if (line > 0.003) {
            context.strokeStyle = `rgba(${colors.accent},${line.toFixed(3)})`;
            context.stroke();
          }
        }
    }

    function updateProgress() {
      // Read at a line just below the header and follow the section the contents list highlights.
      const line = view.scrollY + document.querySelector('header').getBoundingClientRect().bottom + 30;
      const heading = document.getElementById(document.querySelector('nav a[aria-current]')?.dataset.headingId);
      const current = Math.max(0, sectionElements.indexOf(heading?.closest('main > section')));
      const atEnd = view.scrollY >= page.height - view.innerHeight - 2;
      const fills = sectionFills(sections, page.height, line, current, atEnd);

      // Mark the section being read so its leading edge can be emphasized.
      segments.forEach((segment, index) => {
        segment.firstChild.style.width = (fills[index] * 100).toFixed(2) + '%';
        segment.classList.toggle('is-current', fills[index] > 0 && fills[index] < 1);
      });
    }

    function wake() {
      // Coalesce work into the next animation frame.
      if (!frame)
        frame = view.requestAnimationFrame(time => {
          if (!lastTime)
            lastTime = time;
          step(time);
        });
    }

    function refresh() {
      // Remeasure, then repaint the field and progress for the new geometry.
      layout();
      wake();
    }

    // Follow the pointer over the whole page; touch input only taps, since dragging scrolls.
    document.addEventListener('pointermove', event => {
      if (event.pointerType === 'touch')
        return;
      pointer.clientX = event.clientX;
      pointer.clientY = event.clientY;
      pointer.inside = true;
      wake();
    }, { passive: true });
    document.addEventListener('pointerdown', event => {
      if (event.button !== 0 || !isEmptySpace(event.target))
        return;

      // Send a ripple from the press, and start a drag trail for mouse and pen.
      ripples.push({ x: event.clientX, y: event.clientY + view.scrollY, time: performance.now() / 1000 });
      if (ripples.length > 6)
        ripples.shift();
      if (event.pointerType !== 'touch') {
        pointer.clientX = event.clientX;
        pointer.clientY = event.clientY;
        pointer.inside = true;
        pointer.down = true;
        pointer.previous = null;

        // Keep a drag across empty space from starting a text selection.
        event.preventDefault();
      }
      wake();
    });
    const release = () => {
      pointer.down = false;
      pointer.previous = null;
    };
    view.addEventListener('pointerup', release);
    view.addEventListener('pointercancel', release);
    root.addEventListener('pointerleave', () => {
      release();
      pointer.inside = false;
      wake();
    });
    view.addEventListener('blur', () => {
      release();
      pointer.inside = false;
      wake();
    });

    // Repaint on scroll, and remeasure when the page or appearance changes.
    view.addEventListener('scroll', wake, { passive: true });
    new view.ResizeObserver(refresh).observe(body);
    const recolor = () => {
      readColors();
      wake();
    };
    new view.MutationObserver(recolor).observe(body, { attributes: true, attributeFilter: ['data-appearance'] });

    // Follow the contents list, whose highlighted entry can change after this frame ran.
    new view.MutationObserver(wake).observe(document.querySelector('nav'),
      { subtree: true, attributes: true, attributeFilter: ['aria-current'] });
    darkScheme.addEventListener('change', recolor);

    readColors();
    refresh();
  }

  return { FIELD, restWeight, hoverTarget, trailTarget, rippleStrength, sectionFills, bind };
})();

// Expose the pure operations to tests and enhance the rendered document.
if (typeof module !== 'undefined' && module.exports)
  module.exports = ExplainerHexfield;
if (typeof document !== 'undefined')
  ExplainerHexfield.bind(document);
