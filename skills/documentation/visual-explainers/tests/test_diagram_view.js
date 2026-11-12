const assert = require('node:assert/strict');

function checkDiagramView({ viewportSize, fitView, zoomView, constrainView, gestureFrame, gestureView }) {
  // Bound short and tall diagrams without magnifying small content to fill the panel.
  const small = { width: 200, height: 100 };
  assert.deepEqual(viewportSize(1000, small), { width: 1000, height: 180 });
  assert.deepEqual(fitView({ width: 1000, height: 180 }, small), { scale: 1, x: 400, y: 40 });
  const tall = { width: 800, height: 2400 };
  const tallPanel = viewportSize(600, tall);
  assert.equal(tallPanel.height, 480);
  const tallView = fitView(tallPanel, tall);
  assert.ok(tallView.x >= 20 && tallView.y >= 20);
  assert.ok(tallView.x + tall.width * tallView.scale <= tallPanel.width - 20);
  assert.ok(tallView.y + tall.height * tallView.scale <= tallPanel.height - 20);

  // Fit a wide graph inside a narrow panel with both edges visible.
  const content = { width: 1600, height: 600 };
  const panel = { width: 400, height: 300 };
  const fitted = fitView(panel, content);
  assert.equal(fitted.scale, 0.225);
  assert.equal(fitted.x, 20);
  assert.equal(fitted.y, 82.5);

  // Preserve the diagram coordinate under an interior pointer during zoom.
  const view = { scale: 1, x: -400, y: -100 };
  const anchor = { x: 180, y: 130 };
  const zoomed = zoomView(panel, content, view, 1.5, anchor);
  assert.equal((anchor.x - zoomed.x) / zoomed.scale, (anchor.x - view.x) / view.scale);
  assert.equal((anchor.y - zoomed.y) / zoomed.scale, (anchor.y - view.y) / view.scale);

  // Clamp zoom at Fit and 400% without accumulating drift at either limit.
  const minimum = zoomView(panel, content, fitted, 0.001, anchor);
  assert.deepEqual(minimum, fitted);
  const maximum = zoomView(panel, content, view, 1000, anchor);
  assert.equal(maximum.scale, 4);
  assert.deepEqual(zoomView(panel, content, maximum, 2, anchor), maximum);

  // Keep oversized content reachable at both extremes of a drag.
  const leftTop = constrainView(panel, content, { scale: 1, x: 1e6, y: 1e6 });
  const rightBottom = constrainView(panel, content, { scale: 1, x: -1e6, y: -1e6 });
  assert.deepEqual(leftTop, { scale: 1, x: 20, y: 20 });
  assert.deepEqual(rightBottom, { scale: 1, x: -1220, y: -320 });

  // Center fitted content even when a pan is requested far outside the panel.
  assert.deepEqual(constrainView(panel, content, { ...fitted, x: 999, y: -999 }), fitted);

  // Describe idle, single-touch, and two-touch frames while ignoring extra contacts.
  assert.equal(gestureFrame([]), null);
  assert.deepEqual(gestureFrame([{ x: 80, y: 100 }]), { x: 80, y: 100, distance: 1 });
  const start = gestureFrame([{ x: 130, y: 130 }, { x: 230, y: 130 }]);
  assert.deepEqual(start, { x: 180, y: 130, distance: 100 });
  assert.deepEqual(gestureFrame([{ x: 130, y: 130 }, { x: 230, y: 130 }, { x: 999, y: 999 }]), start);

  // Preserve the content under a pinch midpoint while that midpoint also moves.
  const end = { x: 200, y: 160, distance: 200 };
  const pinched = gestureView(panel, content, view, start, end);
  assert.equal(pinched.scale, 2);
  assert.equal((end.x - pinched.x) / pinched.scale, (start.x - view.x) / view.scale);
  assert.equal((end.y - pinched.y) / pinched.scale, (start.y - view.y) / view.scale);

  // Rebase a lifted or added finger at the current view without a visible jump.
  const remaining = gestureFrame([{ x: 200, y: 160 }]);
  assert.deepEqual(gestureView(panel, content, pinched, remaining, remaining), pinched);
  const added = gestureFrame([{ x: 200, y: 160 }, { x: 260, y: 160 }]);
  assert.deepEqual(gestureView(panel, content, pinched, added, added), pinched);
  assert.deepEqual(gestureView(panel, content, view,
    { x: 100, y: 100, distance: 1 }, { x: 120, y: 130, distance: 1 }),
    { scale: 1, x: -380, y: -70 });

  // Keep coincident touches finite and enforce the same Fit and 400% pinch limits.
  const coincident = gestureFrame([{ x: 180, y: 130 }, { x: 180, y: 130 }]);
  assert.equal(coincident.distance, 1);
  assert.deepEqual(gestureView(panel, content, view, coincident, coincident), view);
  assert.equal(gestureView(panel, content, view, start, { ...start, distance: 10000 }).scale, 4);
  assert.equal(gestureView(panel, content, view, start, { ...start, distance: 0.01 }).scale, fitted.scale);

}

// Exercise the same geometry contracts through source and the shipped generated module.
for (const name of ['diagrams.js', 'diagrams.min.js']) {
  checkDiagramView(require('../assets/' + name));
}
console.log('Diagram fit, mouse zoom, touch pan/pinch, gesture rebasing, and bounds passed across source and minified assets.');
