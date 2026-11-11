const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const headings = $$('main h2,main h3').filter(h => !h.classList.contains('component-title') && !h.closest('[role="tabpanel"]'));
const nav = $('nav');
headings.forEach((h, i) => {
  // Ensure each contents entry has an addressable heading.
  if (!h.id)
    h.id = 'section-' + i;

  // Append a link with the heading text and nesting style.
  let a = document.createElement('a');
  a.href = '#' + encodeURIComponent(h.id);
  a.dataset.headingId = h.id;
  a.textContent = h.textContent;
  if (h.tagName === 'H3')
    a.className = 'sub';
  nav.append(a);
});
let headerOffset = 95;
let tocNavigation = null;
let currentHeadingId = null;
let spyScheduled = false;

function measureHeader() {
  // Measure the sticky header and the reading offset.
  const header = $('header');
  const height = header.getBoundingClientRect().height;
  headerOffset = getComputedStyle(header).position === 'sticky' ? height + 20 : 20;

  // Publish the dimensions for layout and anchor positioning.
  document.documentElement.style.setProperty('--header-offset', headerOffset + 'px');
  document.documentElement.style.setProperty('--header-height', height + 'px');
}

function headingVisible(h) {
  return !h.closest('details:not([open]),[hidden]') && h.getClientRects().length > 0 && getComputedStyle(h).visibility !== 'hidden';
}

function spy() {
  // Read the scroll position and discard stale navigation preferences.
  const y = scrollY;
  const maxScroll = Math.max(0, document.documentElement.scrollHeight - innerHeight);
  if (tocNavigation && (!headingVisible(tocNavigation.target) || (!tocNavigation.moving && Math.abs(y - tocNavigation.landedY) > 1)))
    tocNavigation = null;

  // Select the active heading from its physical position.
  currentHeadingId = ExplainerNavigation.selectHeading(
    headings.map((h, order) => ({
      id: h.id,
      order,
      top: h.getBoundingClientRect().top,
      visible: headingVisible(h)
    })),
    {
      readingLine: headerOffset,
      scrollY: y,
      maxScroll,
      preferredId: tocNavigation?.target.id,
      currentId: currentHeadingId
    }
  );

  // Publish the active link and reading progress.
  $$('nav a').forEach(a => {
    if (a.dataset.headingId === currentHeadingId)
      a.setAttribute('aria-current', 'location');
    else
      a.removeAttribute('aria-current');
  });
  $('.progress').style.width = (maxScroll > 0 ? Math.min(100, y / maxScroll * 100) : 0) + '%';
}

function scheduleSpy() {
  // Skip work already scheduled for the next frame.
  if (spyScheduled)
    return;

  // Coalesce scroll updates into one animation frame.
  spyScheduled = true;
  requestAnimationFrame(() => {
    spyScheduled = false;
    spy();
  });
}

function stopTocMotion() {
  // Ignore cancellation when no contents navigation is moving.
  if (!tocNavigation?.moving)
    return;

  // Stop the current scroll and schedule a fresh heading selection.
  tocNavigation = null;
  window.scrollTo({ top: scrollY, behavior: 'instant' });
  scheduleSpy();
}

function navigateToHeading(target) {
  // Track this contents navigation request.
  const state = {
    target,
    moving: true,
    landedY: null
  };
  tocNavigation = state;

  // Reveal collapsed ancestors before measuring the destination.
  for (let parent = target.parentElement; parent;parent = parent.parentElement) {
    if (parent.tagName === 'DETAILS')
      parent.open = true;
  }

  // Close the mobile drawer and focus the destination without scrolling.
  if (mobileContents.matches)
    closeContents(false);
  measureHeader();
  target.tabIndex = -1;
  target.focus({ preventScroll: true });

  // Update the address when history access is available.
  const hash = '#' + encodeURIComponent(target.id);
  if (location.hash !== hash) {
    try {
      history.pushState(null, '', hash);
    }
    catch {
      // Keep scrolling available when history updates are unavailable.
    }
  }

  // Clamp the scroll destination and honor reduced-motion preferences.
  const destination = () => Math.max(
    0,
    Math.min(
      target.getBoundingClientRect().top + scrollY - headerOffset,
      Math.max(0, document.documentElement.scrollHeight - innerHeight)
    )
  );
  let top = destination();
  const behavior = matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth';
  spy();
  window.scrollTo({ top, behavior });

  // Track animation progress until scrolling settles or times out.
  let previous = scrollY;
  let quiet = 0;
  const started = performance.now();

  function settled() {
    // Stop tracking when another navigation replaces this request.
    if (tocNavigation !== state)
      return;

    // Retarget the animation when layout changes move the heading.
    const shifted = destination();
    if (Math.abs(shifted - top) > 2) {
      top = shifted;
      quiet = 0;
      window.scrollTo({ top, behavior });
    }

    // Detect arrival, quiet scrolling, or the maximum tracking duration.
    const y = scrollY;
    quiet = Math.abs(y - previous) < .5 ? quiet + 1 : 0;
    previous = y;
    if (Math.abs(y - top) <= 1 || (quiet >= 4 && performance.now() - started > 200) || performance.now() - started > 4000) {
      state.moving = false;
      state.landedY = y;
      spy();
      return;
    }

    // Continue tracking the unfinished navigation on the next frame.
    requestAnimationFrame(settled);
  }
  requestAnimationFrame(settled);
}
addEventListener('scroll', scheduleSpy, { passive: true });
addEventListener(
  'resize',
  () => {
    // Discard the preferred heading after a settled navigation.
    if (!tocNavigation?.moving)
      tocNavigation = null;

    // Refresh header measurements and schedule heading tracking.
    measureHeader();
    scheduleSpy();
  }
);

function manualScrollIntent(e) {
  // Ignore scroll intent originating inside interactive panels or inputs.
  if (e.target.closest?.('aside,dialog,input,textarea,select,[contenteditable="true"]'))
    return;

  // Cancel the contents animation for manual page scrolling.
  stopTocMotion();
}
addEventListener('wheel', manualScrollIntent, { passive: true });
addEventListener('touchstart', manualScrollIntent, { passive: true });
addEventListener(
  'keydown',
  e => {
    if ([
      'ArrowUp',
      'ArrowDown',
      'PageUp',
      'PageDown',
      'Home',
      'End',
      ' '
    ].includes(e.key) && !e.target.closest?.('button'))
      manualScrollIntent(e);
  }
);
addEventListener(
  'pointerdown',
  e => {
    if (!e.target.closest?.('header,aside,dialog'))
      stopTocMotion();
  },
  { passive: true }
);

function restoreHashSelection() {
  // Resolve the fragment while tolerating malformed URL escapes.
  let target;
  try {
    target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
  }
  catch {
    return;
  }

  // Retain an eligible fragment target and refresh the selected heading.
  if (target && headings.includes(target) && headingVisible(target))
    tocNavigation = {
      target,
      moving: false,
      landedY: scrollY
    };
  spy();
}
addEventListener('popstate', () => {
  tocNavigation = null;
  scheduleSpy();
});
addEventListener('hashchange', () => requestAnimationFrame(restoreHashSelection));
addEventListener('load', () => {
  if (!tocNavigation)
    restoreHashSelection();
});
measureHeader();
spy();
const contents = $('#contents');
const contentsToggle = $('#toc-toggle');
const mobileContents = matchMedia('(max-width:850px)');
let desktopContentsOpen = true;
let mobileContentsOpen = false;
let contentsOverflow = null;

function syncContents(restore = false) {
  // Resolve the current drawer or sidebar state.
  const mobile = mobileContents.matches;
  const open = mobile ? mobileContentsOpen : desktopContentsOpen;

  // Synchronize visibility, accessibility state, and background interaction.
  document.body.classList.toggle('contents-hidden', !desktopContentsOpen);
  document.body.classList.toggle('contents-open', mobile && open);
  contents.inert = !open;
  contents.setAttribute('aria-hidden', String(!open));
  contentsToggle.setAttribute('aria-expanded', String(open));
  contentsToggle.setAttribute('aria-label', open ? 'Hide Contents' : 'Show Contents');
  contentsToggle.title = open ? 'Hide Contents' : 'Show Contents';
  $('main').inert = mobile && open;
  $('.tools').inert = mobile && open;

  // Expose the mobile contents panel as a modal dialog.
  if (mobile) {
    contents.setAttribute('role', 'dialog');
    contents.setAttribute('aria-modal', 'true');
  }
  else {
    contents.removeAttribute('role');
    contents.removeAttribute('aria-modal');
  }

  // Lock page scrolling only while the mobile drawer is open.
  if (mobile && open) {
    if (contentsOverflow === null)
      contentsOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
  }
  else if (contentsOverflow !== null) {
    document.documentElement.style.overflow = contentsOverflow;
    contentsOverflow = null;
  }

  // Restore focus when requested and refresh heading measurements.
  if (restore)
    contentsToggle.focus({ preventScroll: true });
  measureHeader();
  spy();
}

function closeContents(restore = true) {
  // Close the mobile drawer and synchronize its visible state.
  mobileContentsOpen = false;
  syncContents(restore);
}
contentsToggle.addEventListener(
  'click',
  () => {
    if (mobileContents.matches) {
      // Toggle the mobile drawer after stopping contents navigation.
      stopTocMotion();
      mobileContentsOpen = !mobileContentsOpen;
      syncContents(!mobileContentsOpen);

      // Focus and reveal the active contents item when opening the drawer.
      if (mobileContentsOpen) {
        const active = nav.querySelector('[aria-current]') || $('.contents-close');
        active.focus({ preventScroll: true });

        // Scroll the focused entry into the drawer viewport.
        const item = active.getBoundingClientRect();
        const panel = contents.getBoundingClientRect();
        if (item.bottom > panel.bottom - 16)
          contents.scrollTop += item.bottom - panel.bottom + 16;
        else if (item.top < panel.top + 16)
          contents.scrollTop -= panel.top + 16 - item.top;
      }
    }
    else {
      desktopContentsOpen = !desktopContentsOpen;
      syncContents();
    }
  }
);
$('.contents-close').addEventListener('click', () => closeContents());
$('.contents-backdrop').addEventListener('click', () => closeContents());
contents.addEventListener(
  'keydown',
  e => {
    // Handle modal keyboard controls only while the mobile drawer is open.
    if (!mobileContents.matches || !mobileContentsOpen)
      return;

    // Dismiss the drawer on Escape.
    if (e.key === 'Escape') {
      e.preventDefault();
      closeContents();
      return;
    }

    // Wrap keyboard focus within the mobile drawer.
    if (e.key === 'Tab') {
      const stops = [...contents.querySelectorAll('button,a[href]')];
      const first = stops[0];
      const last = stops.at(-1);
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
      else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }
);
nav.addEventListener(
  'click',
  e => {
    // Accept ordinary primary-button contents links.
    const link = e.target.closest('a');
    if (!link || e.button > 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey)
      return;

    // Resolve the destination before replacing native anchor navigation.
    const target = document.getElementById(link.dataset.headingId);
    if (!target)
      return;

    // Navigate with heading tracking and focus restoration.
    e.preventDefault();
    navigateToHeading(target);
  }
);
mobileContents.addEventListener(
  'change',
  () => {
    // Remember whether focus needs restoring across the breakpoint.
    const hadFocus = contents.contains(document.activeElement);

    // Close the mobile drawer and synchronize the new layout.
    mobileContentsOpen = false;
    syncContents(hadFocus && (mobileContents.matches || !desktopContentsOpen));
  }
);
syncContents();
$('.layout').addEventListener('transitionend', spy);
$$('details').forEach(d => d.addEventListener('toggle', spy));
const appearanceToggle = $('#theme-toggle');
const appearanceMenu = $('#theme-menu');
const appearanceOptions = $$('[data-appearance-value]');

function syncAppearance() {
  appearanceOptions.forEach(b => b.setAttribute('aria-checked', String(b.dataset.appearanceValue === document.body.dataset.appearance)));
}

function closeAppearance(restore = false) {
  // Hide the appearance menu and synchronize its toggle.
  appearanceMenu.hidden = true;
  appearanceToggle.setAttribute('aria-expanded', 'false');

  // Restore keyboard focus to the appearance toggle when requested.
  if (restore)
    appearanceToggle.focus();
}

function openAppearance(last = false) {
  // Show the appearance menu and synchronize its toggle.
  appearanceMenu.hidden = false;
  appearanceToggle.setAttribute('aria-expanded', 'true');

  // Focus the selected appearance or the requested last option.
  const current = appearanceOptions.find(b => b.getAttribute('aria-checked') === 'true');
  (last ? appearanceOptions.at(-1) : current || appearanceOptions[0]).focus();
}
appearanceToggle.addEventListener('click', () => appearanceMenu.hidden ? openAppearance() : closeAppearance(true));
appearanceToggle.addEventListener(
  'keydown',
  e => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      openAppearance(e.key === 'ArrowUp');
    }
    else if (e.key === 'Escape')
      closeAppearance(true);
  }
);
appearanceMenu.addEventListener(
  'keydown',
  e => {
    // Choose the destination option or handle menu dismissal.
    let i = appearanceOptions.indexOf(document.activeElement);
    if (e.key === 'ArrowDown')
      i = (i + 1) % appearanceOptions.length;
    else if (e.key === 'ArrowUp')
      i = (i + appearanceOptions.length - 1) % appearanceOptions.length;
    else if (e.key === 'Home')
      i = 0;
    else if (e.key === 'End')
      i = appearanceOptions.length - 1;
    else if (e.key === 'Escape') {
      e.preventDefault();
      closeAppearance(true);
      return;
    }
    else if (e.key === 'Tab') {
      closeAppearance(true);
      return;
    }
    else
      return;

    // Move focus to the chosen appearance option.
    e.preventDefault();
    appearanceOptions[i].focus();
  }
);
appearanceOptions.forEach(b => b.addEventListener(
  'click',
  () => {
    // Apply the selected appearance and update menu selection.
    document.body.dataset.appearance = b.dataset.appearanceValue;
    syncAppearance();

    // Dismiss the menu and return focus to its toggle.
    closeAppearance(true);
  }
));
document.addEventListener(
  'pointerdown',
  e => {
    if (!e.target.closest('.theme-control'))
      closeAppearance();
  }
);
document.addEventListener(
  'focusin',
  e => {
    if (!appearanceMenu.hidden && !e.target.closest('.theme-control'))
      closeAppearance();
  }
);
syncAppearance();
const images = $$('main img');
if (images.length) {
  // Create the shared image-preview dialog.
  const viewer = document.createElement('dialog');
  viewer.className = 'image-viewer';
  viewer.setAttribute('aria-label', 'Enlarged Image');
  viewer.innerHTML = '<div class="image-viewer-bar"><span>Image Preview</span><div><button class="image-size" type="button" aria-pressed="false">Actual Size</button><button class="image-close" type="button" aria-label="Close Image"></button></div></div><div class="image-viewer-stage"><img alt=""></div><p class="image-viewer-caption"></p>';
  viewer.querySelector('.image-close').innerHTML = "<svg class=\"icon\" viewBox=\"0 0 24 24\" aria-hidden=\"true\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.75\"><path d=\"m6 6 12 12M18 6 6 18\"/></svg>";
  document.body.append(viewer);

  // Track preview controls and the state restored on close.
  const preview = viewer.querySelector('img');
  const size = viewer.querySelector('.image-size');
  let opener = null;
  let previousOverflow = '';

  // Wrap each document image in an accessible preview trigger.
  images.forEach(img => {
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'image-trigger';
    trigger.setAttribute('aria-label', 'Enlarge Image: ' + (img.alt || 'Image'));
    trigger.setAttribute('aria-haspopup', 'dialog');
    img.before(trigger);
    trigger.append(img);

    // Open the shared preview with this image and its caption.
    trigger.addEventListener(
      'click',
      () => {
        opener = trigger;
        preview.src = img.currentSrc || img.src;
        preview.alt = img.alt;
        viewer.querySelector('.image-viewer-caption').textContent = img.closest('figure')?.querySelector('figcaption')?.textContent || '';

        // Reset image sizing before displaying the preview.
        viewer.classList.remove('actual-size');
        size.textContent = 'Actual Size';
        size.setAttribute('aria-pressed', 'false');

        // Lock background scrolling and show the modal preview.
        previousOverflow = document.documentElement.style.overflow;
        document.documentElement.style.overflow = 'hidden';
        viewer.showModal();
      }
    );
  });

  // Toggle preview sizing and publish the selected mode.
  size.addEventListener(
    'click',
    () => {
      const actual = viewer.classList.toggle('actual-size');
      size.textContent = actual ? 'Fit to Screen' : 'Actual Size';
      size.setAttribute('aria-pressed', String(actual));
    }
  );

  // Close the preview from its button or an outside click.
  viewer.querySelector('.image-close').addEventListener('click', () => viewer.close());
  viewer.addEventListener(
    'click',
    e => {
      const r = viewer.getBoundingClientRect();
      if (e.target === viewer && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom))
        viewer.close();
    }
  );

  // Restore background scrolling and focus after the preview closes.
  viewer.addEventListener(
    'close',
    () => {
      document.documentElement.style.overflow = previousOverflow;
      opener?.focus({ preventScroll: true });
    }
  );
}
$$('[data-copy]').forEach(b => b.addEventListener(
  'click',
  async () => {
    // Copy the selected code block to the clipboard when available.
    const code = document.getElementById(b.dataset.copy);
    try {
      await navigator.clipboard.writeText(code.textContent);
      b.textContent = 'Copied';
    }
    catch {
      // Select the code for manual copying when clipboard access fails.
      const r = document.createRange();
      r.selectNodeContents(code);
      const s = getSelection();
      s.removeAllRanges();
      s.addRange(r);
      b.textContent = 'Selected; press Ctrl/Cmd+C';
    }

    // Restore the copy button label after its feedback interval.
    setTimeout(() => b.textContent = 'Copy', 2600);
  }
));
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
document.querySelectorAll('.tabs').forEach(group => {
  // Collect only the tabs owned by this group.
  const tabs = [...group.querySelectorAll(':scope > .tab-list > [role="tab"]')];

  function choose(button) {
    // Synchronize selection, keyboard access, and panel visibility.
    tabs.forEach(t => {
      const active = t === button;
      t.setAttribute('aria-selected', String(active));
      t.tabIndex = active ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !active;
    });

    // Refresh charts and layout after revealing the selected panel.
    window.dispatchEvent(new Event('resize'));
  }

  // Bind pointer activation and roving keyboard focus for each tab.
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => choose(t));
    t.addEventListener(
      'keydown',
      e => {
        // Choose the adjacent or endpoint tab for supported keys.
        let next;
        if (e.key === 'ArrowRight')
          next = (i + 1) % tabs.length;
        else if (e.key === 'ArrowLeft')
          next = (i + tabs.length - 1) % tabs.length;
        else if (e.key === 'Home')
          next = 0;
        else if (e.key === 'End')
          next = tabs.length - 1;
        else
          return;

        // Activate and focus the chosen tab.
        e.preventDefault();
        choose(tabs[next]);
        tabs[next].focus();
      }
    );
  });
});
window.Explainer = {
  /**
   * Forward a chart update to the optional bundled chart controller.
   * @param {string} id Generated chart ID; unknown IDs are ignored.
   * @param {object} patch Shallow configuration fields satisfying the chart data contract.
   */
  chart: (id, patch) => window.ExplainerCharts?.update(id, patch)
};

// Bind each range control to its adjacent live-value output.
document.querySelectorAll('input[type="range"]').forEach(range =>
  range.addEventListener("input", () => {
    // Locate the live-value output associated with this range.
    const output = document.getElementById(range.id + "-value");

    // Publish the current value when the output is present.
    if (output) output.value = range.value;
  })
);
