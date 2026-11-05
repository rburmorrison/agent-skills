# Custom Visuals and Interactions

Use a custom HTML/SVG/canvas fragment when the built-in components cannot explain the subject. Keep the standard document shell, spacing, typography, and tokens. No required framework. The builder embeds local files verbatim; custom code must be self-contained.

Document fields:

```json
{
  "title":"Your Subject",
  "styles":["visual.css"],
  "scripts":["visual.js"],
  "sections":[{"title":"Explore the Relationship","blocks":[
    {"type":"range","id":"count","label":"Item Count","min":1,"max":10,"value":3},
    {"type":"html","file":"visual.html"}
  ]}]
}
```

`html` also accepts an `html` string instead of `file`. Fragments go inside main; do not supply `doctype`, `html`, `head`, `body`, an H1, or a second navigation shell. Scripts load after the components and `window.Explainer` API are ready. Each script file runs in its own function scope. Use `document.getElementById`/scoped selectors to find your elements. No script imports, CDNs, network requests, or sibling file fetches at runtime. Supply all data in the fragment/script or chart config.

Example fragment:

```html
<div class="visual custom-visual"><div class="visual-body">
  <svg viewBox="0 0 500 100" role="img" aria-label="Item count">
    <rect id="count-bar" x="10" y="20" width="144" height="36" rx="5" fill="var(--accent)"/>
  </svg>
  <p id="count-result" aria-live="polite">3 items</p>
</div></div>
```

Example script:

```js
const input = document.getElementById('count');
function render() {
  const value = Number(input.value);
  document.getElementById('count-bar').setAttribute('width', value * 48);
  document.getElementById('count-result').textContent = value + ' items';
}
input.addEventListener('input', render);
render();
```

For a supported plot shape use a chart block, not custom chart markup. For an unsupported plot shape, provide exact-value tooltips on hover/tap, keyboard-focus inspection, and an accessible data/text equivalent. A visualization responding to a slider still needs inspection of its plotted marks.

Every control should visibly change the relevant result; use one state to derive all labels, calculations, and charts. For standard chart updates call `window.Explainer.chart(id, {data: ...})`; see [charts.md](charts.md). This API is available when at least one chart is present.

## Styling and Accessibility

Use tokens `--bg`, `--paper`, `--ink`, `--muted`, `--accent`, `--line`, `--wash`, `--table-head`, and `--radius-media`. Available classes include `.visual`, `.visual-label`, `.visual-body`, `.controls`, `.control-group`, `.metric`, `.caption`, `.card`, `.two`, and `.sr-only`. Use `currentColor` for icons. SVG text inherits the embedded document font. Use `viewBox`, padding for labels, and responsive widths. Keep label/connector geometry clear at narrow widths; use a horizontally scrollable container when genuine diagram complexity requires it.

Controls need visible labels, native keyboard behavior or equivalent key handling, and focus indication. SVG/canvas visuals need descriptive accessible text and a nearby textual result or data table where the information is otherwise inaccessible. Honor `prefers-reduced-motion`; avoid animation unrelated to the explanation. Test all four themes if custom colors are used.

For custom icons, embed an existing file from `assets/icons/NAME.svg`; its viewBox is 24×24 and stroke width 1.75. Do not turn the icon gallery into article content unless the user asks for it.

Use custom CSS sparingly. Images inside custom fragments using local `src` are embedded relative to the document JSON. Other custom resources must already be data URIs or inline; the checker rejects external asset references. Local font files and licenses are already bundled by the builder, including in exported HTML.
