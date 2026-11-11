// Share pure heading-selection rules between the controller and its tests.
const ExplainerNavigation = (() => {
  /**
   * Select the active heading without reading or mutating the DOM.
   * @param {{id: string, top: number, order: number, visible?: boolean}[]} entries
   *   Heading IDs, viewport top positions, stable reading order, and visibility.
   * @param {object} position Scroll and selection state in CSS pixels.
   * @param {number} position.readingLine Viewport line used to track passed headings.
   * @param {number} position.scrollY Current document scroll position.
   * @param {number} position.maxScroll Maximum document scroll position.
   * @param {?string} [position.preferredId] Explicit navigation target to retain.
   * @param {?string} [position.currentId] Current heading used to resolve position ties.
   * @returns {?string} Selected visible heading ID, or null when none are visible.
   */
  function selectHeading(entries, { readingLine, scrollY, maxScroll, preferredId = null, currentId = null }) {
    // Collect visible headings in physical reading order.
    const visible = entries.filter(e => e.visible !== false).sort((a, b) => a.top - b.top || a.order - b.order);
    if (!visible.length)
      return null;

    // Retain an explicit navigation target while it remains visible.
    if (preferredId && visible.some(e => e.id === preferredId))
      return preferredId;

    // Select the final heading at the bottom of a scrollable document.
    if (maxScroll > 1 && scrollY >= maxScroll - 2)
      return visible.at(-1).id;

    // Find headings that have crossed the reading line.
    const passed = visible.filter(e => e.top <= readingLine + 2);
    if (!passed.length)
      return visible[0].id;

    // Keep coincident headings stable using the current selection.
    const lastTop = passed.at(-1).top;
    const tied = passed.filter(e => Math.abs(e.top - lastTop) <= 2);
    return (tied.find(e => e.id === currentId) || tied[0]).id;
  }
  return { selectHeading };
})();
if (typeof module !== 'undefined' && module.exports)
  module.exports = ExplainerNavigation;
