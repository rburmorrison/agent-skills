const assert = require('node:assert/strict');

function checkHexfield({ FIELD, restWeight, hoverTarget, trailTarget, rippleStrength, sectionFills }) {
  // Show resting cells at full strength on each side and clear them toward the center.
  assert.equal(restWeight(0, 2000, 1000, 0), 1);
  assert.equal(restWeight(1000, 2000, 1000, 0), 1);
  assert.equal(restWeight(500, 2000, 1000, 0), 0);
  assert.equal(restWeight(1000 * FIELD.edge, 2000, 1000, 0), 0);
  assert.equal(restWeight(1000 * FIELD.plateau, 2000, 1000, 0), 1, 'The outer band holds full strength');
  assert.ok(restWeight(100, 2000, 1000, 0) > restWeight(200, 2000, 1000, 0));

  // Add a title band at the top that fades out by the hero's bottom.
  assert.equal(restWeight(500, 0, 1000, 600), FIELD.heroStrength);
  assert.equal(restWeight(500, 600, 1000, 600), 0);
  assert.ok(restWeight(500, 300, 1000, 600) > 0);
  assert.equal(restWeight(0, 0, 1000, 600), 1, 'The band never weakens the sides');

  // Ease hover strength from the pointer out to its reach.
  assert.equal(hoverTarget(0), 1);
  assert.equal(hoverTarget(FIELD.hover.reach), 0);
  assert.equal(hoverTarget(FIELD.hover.reach * 2), 0);
  assert.equal(hoverTarget(FIELD.hover.reach / 2), 0.25);

  // Light cells along a drag segment, including a zero-length press, and clamp to its ends.
  assert.equal(trailTarget(50, 0, [0, 0, 100, 0]), 1);
  assert.equal(trailTarget(50, FIELD.trail.width, [0, 0, 100, 0]), 0);
  assert.equal(trailTarget(0, 0, [0, 0, 0, 0]), 1);
  assert.equal(trailTarget(200, 0, [0, 0, 100, 0]), 0, 'Points past the end measure to the endpoint');

  // Move a ripple's bright band outward over time and end it after its life.
  const front = FIELD.ripple.speed * 0.5;
  assert.ok(rippleStrength(front, 0.5, false) > rippleStrength(0, 0.5, false));
  assert.ok(rippleStrength(0, 0, false) > 0.9);
  assert.equal(rippleStrength(front, FIELD.ripple.life, false), 0);

  // Replace motion with a short glow in place when the reader prefers reduced motion.
  assert.ok(rippleStrength(0, 0, true) > 0.9);
  assert.equal(rippleStrength(FIELD.ripple.glow, 0, true), 0);
  assert.equal(rippleStrength(front, 0.1, true), 0, 'A reduced ripple never travels');
  assert.equal(rippleStrength(0, FIELD.ripple.glowLife, true), 0);

  // Fill earlier sections, partly fill the highlighted one, and leave later ones empty.
  assert.deepEqual(sectionFills([0, 500, 1000], 2000, 750, 1, false), [1, 0.5, 0]);
  assert.deepEqual(sectionFills([0, 500, 1000], 2000, 400, 0, false), [0.8, 0, 0]);
  assert.deepEqual(sectionFills([0, 500, 1000], 2000, 1200, 2, false), [1, 1, 0.2]);

  // Complete every section at the page end, even ones the reading line never reached.
  assert.deepEqual(sectionFills([0, 500, 1000], 2000, 1200, 2, true), [1, 1, 1]);
  assert.deepEqual(sectionFills([0, 500, 1000], 2000, 600, 1, true), [1, 1, 1]);
  assert.deepEqual(sectionFills([0], 300, 0, 0, false), [0]);
}

// Exercise the same field rules through source and the shipped generated module.
for (const name of ['hexfield.js', 'hexfield.min.js']) {
  checkHexfield(require('../assets/' + name));
}
console.log('Hexfield resting strength, hover, trail, ripple, reduced motion, and section progress passed across source and minified assets.');
