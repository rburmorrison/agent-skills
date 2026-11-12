// Keep diagram framing independent of the DOM so geometry can be verified directly.
const ExplainerDiagrams = (() => {
  const PADDING = 20;
  const MAX_SCALE = 4;

  /**
   * Bound a diagram panel to 180–480 CSS pixels in height.
   * @param {number} width Available panel width in CSS pixels, greater than zero.
   * @param {{width:number,height:number}} content Positive authored SVG dimensions.
   * @returns {{width:number,height:number}} Panel dimensions fitting width first.
   */
  function viewportSize(width, content) {
    const scale = Math.min(1, Math.max(1, width - PADDING * 2) / content.width);
    return { width, height: Math.max(180, Math.min(480, content.height * scale + PADDING * 2)) };
  }

  /**
   * Center small content and keep larger content reachable at both pan boundaries.
   * @param {{width:number,height:number}} viewport Positive panel dimensions.
   * @param {{width:number,height:number}} content Positive authored SVG dimensions.
   * @param {{scale:number,x:number,y:number}} view Positive scale and pixel offsets.
   * @returns {{scale:number,x:number,y:number}} View with constrained offsets.
   */
  function constrainView(viewport, content, view) {
    // Center each fitted axis or clamp its oversized content to the panel edges.
    const offset = (available, size, value) => size <= available - PADDING * 2
      ? (available - size) / 2
      : Math.min(PADDING, Math.max(available - PADDING - size, value));

    return {
      scale: view.scale,
      x: offset(viewport.width, content.width * view.scale, view.x),
      y: offset(viewport.height, content.height * view.scale, view.y)
    };
  }

  /**
   * Fit an entire diagram without enlarging its authored dimensions.
   * @param {{width:number,height:number}} viewport Positive panel dimensions.
   * @param {{width:number,height:number}} content Positive authored SVG dimensions.
   * @returns {{scale:number,x:number,y:number}} Centered fitted view.
   */
  function fitView(viewport, content) {
    // Choose the largest scale that keeps the complete diagram visible.
    const scale = Math.min(1,
      Math.max(1, viewport.width - PADDING * 2) / content.width,
      Math.max(1, viewport.height - PADDING * 2) / content.height);

    // Center the fitted content along both axes.
    return constrainView(viewport, content, { scale, x: 0, y: 0 });
  }

  /**
   * Describe the center and span of the first two active pointers.
   * @param {{x:number,y:number}[]} points Ordered panel-local CSS pixel positions.
   * @returns {?{x:number,y:number,distance:number}} Null for no pointers; otherwise
   *   one pointer's position or two pointers' midpoint, with a span of at least 1px.
   */
  function gestureFrame(points) {
    // Handle idle and single-pointer gestures without introducing a zoom factor.
    if (!points.length)
      return null;
    const [first, second] = points;
    if (!second)
      return { ...first, distance: 1 };

    // Anchor a pinch at its midpoint and avoid division by a coincident touch pair.
    return {
      x: (first.x + second.x) / 2,
      y: (first.y + second.y) / 2,
      distance: Math.max(1, Math.hypot(second.x - first.x, second.y - first.y))
    };
  }

  /**
   * Move a gesture's content anchor while scaling between Fit and 400%.
   * @param {{width:number,height:number}} viewport Positive panel dimensions.
   * @param {{width:number,height:number}} content Positive authored SVG dimensions.
   * @param {{scale:number,x:number,y:number}} view View at the gesture's start.
   * @param {{x:number,y:number,distance:number}} from Starting center and positive span.
   * @param {{x:number,y:number,distance:number}} to Current center and positive span.
   * @returns {{scale:number,x:number,y:number}} Anchored, constrained gesture view.
   */
  function gestureView(viewport, content, view, from, to) {
    // Clamp the scale before anchoring to avoid drift at the zoom limits.
    const minimum = fitView(viewport, content).scale;
    const scale = Math.min(MAX_SCALE, Math.max(minimum, view.scale * to.distance / from.distance));
    const ratio = scale / view.scale;

    // Preserve the content point under the moving center unless a pan boundary intervenes.
    return constrainView(viewport, content, {
      scale,
      x: to.x - (from.x - view.x) * ratio,
      y: to.y - (from.y - view.y) * ratio
    });
  }

  /**
   * Zoom around a panel-local point, bounded by Fit and 400% authored scale.
   * @param {{width:number,height:number}} viewport Positive panel dimensions.
   * @param {{width:number,height:number}} content Positive authored SVG dimensions.
   * @param {{scale:number,x:number,y:number}} view Current view.
   * @param {number} factor Positive zoom multiplier.
   * @param {{x:number,y:number}} anchor Panel-local pointer or center in CSS pixels.
   * @returns {{scale:number,x:number,y:number}} Anchored, constrained view.
   */
  function zoomView(viewport, content, view, factor, anchor) {
    return gestureView(viewport, content, view,
      { ...anchor, distance: 1 }, { ...anchor, distance: factor });
  }

  /**
   * Enhance one SVG panel; hidden panels initialize when they acquire a width.
   * @param {HTMLElement} viewport Renderer-marked panel containing one diagram SVG.
   * @returns {void} No result; updates this panel and its figure's control header.
   */
  function bind(viewport) {
    // Retain the existing scrollable fallback when enhancement cannot initialize.
    const svg = viewport.querySelector('.graph-svg,.sequence-svg');
    const toolbar = viewport.parentElement.querySelector(':scope > .diagram-header > .diagram-tools');
    if (!svg || !toolbar?.classList.contains('diagram-tools') || typeof ResizeObserver === 'undefined')
      return;
    const box = svg.viewBox.baseVal;
    const width = parseFloat(getComputedStyle(svg).getPropertyValue('--diagram-min-width'));
    if (!(width > 0 && box.width > 0 && box.height > 0))
      return;

    // Keep authored geometry separate from the mutable view and pointer state.
    const content = { width, height: width * box.height / box.width };
    const output = toolbar.querySelector('output');
    const zoomOut = toolbar.querySelector('[data-diagram-action="out"]');
    const zoomIn = toolbar.querySelector('[data-diagram-action="in"]');
    let panel = null;
    let view = null;
    let fitted = true;
    let drag = null;
    const pointers = new Map();

    function paint() {
      // Apply the view without changing the SVG's layout dimensions.
      svg.style.transform = `translate(${view.x}px,${view.y}px) scale(${view.scale})`;
      output.value = `${Math.round(view.scale * 100)}%`;

      // Reflect the zoom bounds in the native controls.
      zoomOut.disabled = view.scale <= fitView(panel, content).scale + 0.000001;
      zoomIn.disabled = view.scale >= MAX_SCALE - 0.000001;
    }

    function refresh() {
      // Ignore hidden panels and unchanged widths, including observer height callbacks.
      const width = viewport.clientWidth;
      if (!width || (panel && panel.width === width))
        return;

      // End gestures before changing their panel-local coordinate system.
      clearGesture();

      // Measure the bounded viewport independently of the current zoom.
      const previous = panel;
      panel = viewportSize(width, content);
      viewport.style.height = `${panel.height}px`;

      // Fit initially or preserve manual framing around the panel's center on resize.
      if (fitted || !view)
        view = fitView(panel, content);
      else {
        const scale = Math.max(fitView(panel, content).scale, view.scale);
        view = constrainView(panel, content, {
          scale,
          x: panel.width / 2 - (previous.width / 2 - view.x) * scale / view.scale,
          y: panel.height / 2 - (previous.height / 2 - view.y) * scale / view.scale
        });
      }

      // Reveal the controls only after the fitted transform is ready.
      viewport.classList.add('diagram-panzoom');
      viewport.tabIndex = 0;
      viewport.setAttribute('role', 'group');
      viewport.setAttribute('aria-label', `${svg.getAttribute('aria-label')} viewer`);
      viewport.setAttribute('aria-describedby', viewport.dataset.diagramHelp);
      toolbar.hidden = false;
      toolbar.parentElement.hidden = false;
      paint();
    }

    function fit() {
      // Ignore panels that have not acquired layout dimensions.
      if (!panel)
        return;

      // End gestures before replacing their initial view.
      clearGesture();

      // Restore automatic fitting and center the complete diagram.
      fitted = true;
      view = fitView(panel, content);
      paint();
    }

    function zoom(factor, anchor = { x: panel.width / 2, y: panel.height / 2 }) {
      // End pointer gestures before applying a toolbar or wheel command.
      clearGesture();

      // Apply bounded zoom and resume fitting when the minimum scale is reached.
      view = zoomView(panel, content, view, factor, anchor);
      fitted = view.scale <= fitView(panel, content).scale + 0.000001;

      // Publish the updated framing and control limits.
      paint();
    }

    function rebaseGesture() {
      // Snapshot the current view whenever the active pointer set changes.
      const frame = gestureFrame([...pointers.values()]);
      drag = frame ? { view, frame } : null;

      // Reflect whether any pointer remains active.
      viewport.classList.toggle('is-panning', Boolean(drag));
    }

    function clearGesture() {
      // Forget active pointers before releasing capture can send lost-capture events.
      const captured = [...pointers.keys()];
      pointers.clear();
      drag = null;
      viewport.classList.remove('is-panning');

      // Release every pointer retained by the completed or interrupted gesture.
      for (const id of captured) {
        if (viewport.hasPointerCapture(id))
          viewport.releasePointerCapture(id);
      }
    }

    function endPointer(event) {
      // Ignore pointers that do not belong to this panel's gesture.
      if (!pointers.has(event.pointerId))
        return;

      // Rebase before release so lifting one finger cannot jump the remaining drag.
      pointers.delete(event.pointerId);
      rebaseGesture();
      if (viewport.hasPointerCapture(event.pointerId))
        viewport.releasePointerCapture(event.pointerId);
    }

    function pointerPosition(event) {
      const bounds = viewport.getBoundingClientRect();
      return { x: event.clientX - bounds.left, y: event.clientY - bounds.top };
    }

    // Bind toolbar actions without moving focus away from the pressed control.
    zoomOut.addEventListener('click', () => zoom(1 / 1.25));
    zoomIn.addEventListener('click', () => zoom(1.25));
    toolbar.querySelector('[data-diagram-action="fit"]').addEventListener('click', fit);

    // Consume only modifier-assisted wheel zoom; leave ordinary page scrolling alone.
    viewport.addEventListener('wheel', event => {
      if (!(event.ctrlKey || event.metaKey) || !view || !event.deltaY)
        return;

      // Zoom at the pointer using panel-local coordinates and pixel-normalized deltas.
      event.preventDefault();
      const bounds = viewport.getBoundingClientRect();
      const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? panel.height : 1);
      zoom(Math.exp(-Math.max(-200, Math.min(200, delta)) * 0.002), {
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top
      });
    }, { passive: false });

    // Capture mouse, pen, or multiple touches inside the diagram only.
    viewport.addEventListener('pointerdown', event => {
      // Accept secondary touches but keep mouse and pen drags on their primary pointer.
      if (!view || event.button !== 0 || (event.pointerType !== 'touch' && !event.isPrimary))
        return;

      // Retain each contact and rebase without changing the visible diagram.
      event.preventDefault();
      viewport.focus({ preventScroll: true });
      pointers.set(event.pointerId, pointerPosition(event));
      viewport.setPointerCapture(event.pointerId);
      rebaseGesture();
    });
    viewport.addEventListener('pointermove', event => {
      // Ignore movement from pointers that did not start this gesture.
      if (!drag || !pointers.has(event.pointerId))
        return;

      // Pan or pinch from the current pointer set's starting frame.
      pointers.set(event.pointerId, pointerPosition(event));
      view = gestureView(panel, content, drag.view, drag.frame, gestureFrame([...pointers.values()]));
      fitted = view.scale <= fitView(panel, content).scale + 0.000001;

      // Publish the gesture without resizing the panel or the document.
      paint();
    });
    for (const event of ['pointerup', 'pointercancel', 'lostpointercapture'])
      viewport.addEventListener(event, endPointer);

    // Provide keyboard access without handling shortcuts aimed at toolbar controls.
    viewport.addEventListener('keydown', event => {
      // Ignore shortcuts that belong to other controls or browser commands.
      if (!view || event.target !== viewport || event.ctrlKey || event.metaKey || event.altKey)
        return;

      // Resolve fit and zoom shortcuts before directional panning.
      if (event.key === 'Home')
        fit();
      else if (event.key === '+' || event.key === '=')
        zoom(1.25);
      else if (event.key === '-' || event.key === '−')
        zoom(1 / 1.25);
      else {
        const directions = { ArrowLeft: [40, 0], ArrowRight: [-40, 0], ArrowUp: [0, 40], ArrowDown: [0, -40] };
        const direction = directions[event.key];
        if (!direction)
          return;

        // End pointer gestures before applying a keyboard pan.
        clearGesture();

        // Move the diagram in the requested viewing direction and repaint.
        view = constrainView(panel, content, { scale: view.scale, x: view.x + direction[0], y: view.y + direction[1] });
        paint();
      }

      // Keep recognized diagram shortcuts from also scrolling the document.
      event.preventDefault();
    });

    // Recompute fitted or manual framing when a panel becomes visible or resizes.
    const observer = new ResizeObserver(refresh);
    observer.observe(viewport);
    refresh();
  }

  return { viewportSize, constrainView, fitView, gestureFrame, gestureView, zoomView, bind };
})();

// Expose the pure operations to tests and enhance renderer-marked browser panels.
if (typeof module !== 'undefined' && module.exports)
  module.exports = ExplainerDiagrams;
if (typeof document !== 'undefined')
  document.querySelectorAll('[data-diagram-viewport]').forEach(ExplainerDiagrams.bind);
