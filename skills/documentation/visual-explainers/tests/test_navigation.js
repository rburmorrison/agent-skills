const assert=require('node:assert/strict');
const {selectHeading}=require('../assets/navigation.js');
const entries=(rows)=>rows.map(([id,top,visible=true],order)=>({id,top,visible,order}));
const position={readingLine:84,scrollY:100,maxScroll:1000};

assert.equal(selectHeading(entries([['intro',-300],['errors',420],['references',650]]),{...position,scrollY:549,maxScroll:549,preferredId:'errors'}),'errors','A clamped click must retain its actual target');
assert.equal(selectHeading(entries([['intro',-300],['errors',420],['references',650]]),{...position,scrollY:549,maxScroll:549}),'references','Manual scrolling to the end activates the last visible heading');
assert.equal(selectHeading(entries([['intro',200],['summary',500]]),{...position,scrollY:0,maxScroll:0}),'intro','A document fitting the viewport must not default to the last heading');
assert.equal(selectHeading(entries([['intro',-100],['hidden',0,false],['later',500]]),position),'intro','Hidden headings cannot steal the active state');
assert.equal(selectHeading(entries([['left',84],['right',84]]),{...position,preferredId:'left'}),'left','Coincident columns retain the clicked heading');
assert.equal(selectHeading(entries([['left',84],['right',84]]),{...position,currentId:'left'}),'left','Tracking should not flicker between aligned headings');
assert.equal(selectHeading(entries([['left',84],['right',84]]),position),'left','Aligned headings have a stable first-reading-order fallback');
assert.equal(selectHeading(entries([['first-column-low',40],['second-column-high',-100],['next',300]]),position),'first-column-low','Use physical heading positions rather than DOM iteration order');
assert.equal(selectHeading(entries([['parent',-20],['child',83.5],['later',400]]),position),'child','The reading line tolerates fractional CSS positions');
assert.equal(selectHeading(entries([['hidden',0,false]]),position),null);
assert.equal(selectHeading([],position),null);
console.log('11 navigation selection checks passed.');
