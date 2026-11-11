const assert = require('node:assert/strict');
const entries = (rows) => rows.map(([id, top, visible = true], order) => ({
  id,
  top,
  visible,
  order
}));
const position = {
  readingLine: 84,
  scrollY: 100,
  maxScroll: 1000
};

function checkNavigation(selectHeading) {
  // Keep the clicked target when scrolling clamps at the document end.
  assert.equal(
    selectHeading(
      entries([['intro', -300], ['errors', 420], ['references', 650]]),
      {
        ...position,
        scrollY: 549,
        maxScroll: 549,
        preferredId: 'errors'
      }
    ),
    'errors',
    'A clamped click must retain its actual target'
  );

  // Activate the final heading after manual scrolling reaches the end.
  assert.equal(
    selectHeading(
      entries([['intro', -300], ['errors', 420], ['references', 650]]),
      {
        ...position,
        scrollY: 549,
        maxScroll: 549
      }
    ),
    'references',
    'Manual scrolling to the end activates the last visible heading'
  );

  // Keep the first heading active when the document fits the viewport.
  assert.equal(
    selectHeading(entries([['intro', 200], ['summary', 500]]), {
      ...position,
      scrollY: 0,
      maxScroll: 0
    }),
    'intro',
    'A document fitting the viewport must not default to the last heading'
  );

  // Exclude hidden headings from scroll tracking.
  assert.equal(
    selectHeading(entries([['intro', -100], ['hidden', 0, false], ['later', 500]]), position),
    'intro',
    'Hidden headings cannot steal the active state'
  );

  // Preserve the clicked heading when columns share a position.
  assert.equal(
    selectHeading(entries([['left', 84], ['right', 84]]), { ...position, preferredId: 'left' }),
    'left',
    'Coincident columns retain the clicked heading'
  );

  // Retain the current heading when aligned columns would otherwise tie.
  assert.equal(
    selectHeading(entries([['left', 84], ['right', 84]]), { ...position, currentId: 'left' }),
    'left',
    'Tracking should not flicker between aligned headings'
  );

  // Use reading order as the fallback for aligned headings.
  assert.equal(
    selectHeading(entries([['left', 84], ['right', 84]]), position),
    'left',
    'Aligned headings have a stable first-reading-order fallback'
  );

  // Track physical heading positions across columns.
  assert.equal(
    selectHeading(entries([['first-column-low', 40], ['second-column-high', -100], ['next', 300]]), position),
    'first-column-low',
    'Use physical heading positions rather than DOM iteration order'
  );

  // Allow fractional positions at the reading line.
  assert.equal(
    selectHeading(entries([['parent', -20], ['child', 83.5], ['later', 400]]), position),
    'child',
    'The reading line tolerates fractional CSS positions'
  );

  // Return no selection when every heading is hidden.
  assert.equal(selectHeading(entries([['hidden', 0, false]]), position), null);

  // Return no selection for an empty heading list.
  assert.equal(selectHeading([], position), null);
}

// Exercise the same selection scenarios through readable and generated modules.
for (const name of ['navigation.js', 'navigation.min.js']) {
  const { selectHeading } = require('../assets/' + name);
  checkNavigation(selectHeading);
}
console.log('22 navigation selection checks passed across source and minified assets.');
