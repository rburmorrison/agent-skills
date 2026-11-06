# Document and Component Fields

Use JSON, not Python code. Strings inside `blocks` are paragraphs. All paths are relative to the input JSON. Objects below show the supported fields; optional fields are noted. Nested `blocks` use the same vocabulary.

## Document

Required: `title`. Optional: `brand` (short header name; defaults to title), `lead`, `description`, `theme` (theme set; currently only `plain`, the default), `lang` (default `en`), `intro` (blocks below the lead), `sections` (list of `{title, blocks, id?}`), `scripts` (local JS file paths), `styles` (local CSS file paths). All asset paths must be relative and remain within the JSON directory after resolving symlinks. `html` blocks and nonempty `scripts`/`styles` require the operator's `--trusted-custom` option; see [custom.md](custom.md).

The shell creates H1. Sections create H2 and ToC entries. You choose all section names and ordering. Heading blocks create H3/H4; H3 joins the ToC except inside tabs. Component titles are labels, not extra sections. On mobile the header stays sticky and its contents icon opens a vertical drawer. Selecting a heading closes the drawer and scrolls smoothly to it below the header. The selected link stays highlighted during navigation, including near the end of the document. Manual scrolling resumes section tracking; reduced-motion preferences disable animation. No footer or source section is forced. Use paragraphs/links or a section when sources are useful.

## Theme Sets

`theme` selects one supported set at generation time, for example `"theme": "plain"`. Only `plain` is currently supported. Each output embeds just that set’s paired light/dark palettes; the reader cannot switch sets. The header menu always starts in System and offers only System, Light, and Dark. System follows the reader’s OS/browser appearance preference live; choosing Light or Dark fixes the appearance until System is selected again.

To add a supported set, place its paired color tokens and menu swatches in `assets/themes/<name>.css` and register its path in `THEMES` in `scripts/render.py`. Use `assets/themes/plain.css` as the token contract: its `light-dark()` values resolve through the shell’s selected color scheme. Keep set-specific styling in that asset so it is embedded only when selected. The shared shell owns layout, appearance switching, and print behavior.

## Inline Text

Paragraphs, table cells, captions, labels, and list items accept `**bold**`, `*emphasis*`, backtick-delimited inline code, and `[label](https://url)`. Literal HTML is escaped. Inline formatting is deliberately simple and does not nest. Write multiline code in a code block. Use an `equation` block for formulas and an `html` block for complex links, SVG, or other markup. Links can be `https:`, `http:`, `mailto:`, or fragment anchors.

## Writing and Layout

```json
{"type":"text","text":"A paragraph."}
{"type":"heading","level":3,"text":"A Subheading"}
{"type":"list","ordered":false,"items":["First item","Second item"]}
{"type":"equation","text":"T = n × t","label":"Total time equals count times time per item","caption":"Optional explanation."}
{"type":"card","title":"Optional Title","icon":"optional-icon-name","blocks":["Content."]}
{"type":"columns","columns":[["Left content."],["Right content."]]}
{"type":"metrics","items":[{"value":"42 ms","label":"Median Latency","detail":"Optional context","icon":"clock"}]}
{"type":"timeline","items":[{"label":"Optional time or phase","title":"Event","text":"What happens."}]}
```

`heading.level` is 3 or 4, default 3. `columns` accepts 1–3 lists of blocks and stacks when its container is narrow. `card.title` and `card.icon` are optional. Metrics are for meaningful figures, not invented decoration.

## Math Formulas

Use `equation.text` for simple Unicode formulas. For typeset fractions, roots, scripts, sums, integrals, or matrices, supply `mathml` instead of `text` and a nonempty, plain-language `label`. Both forms accept an optional `caption` with inline formatting. MathML uses the browser's native math rendering, works offline, and needs no `--trusted-custom` option. TeX/LaTeX strings and inline math delimiters are not interpreted.

```json
{"type":"equation","mathml":"<math><mi>x</mi><mo>=</mo><mfrac><mrow><mo>−</mo><mi>b</mi><mo>±</mo><msqrt><mrow><msup><mi>b</mi><mn>2</mn></msup><mo>−</mo><mn>4</mn><mi>a</mi><mi>c</mi></mrow></msqrt></mrow><mrow><mn>2</mn><mi>a</mi></mrow></mfrac></math>","label":"x equals negative b plus or minus the square root of b squared minus four a c, all divided by two a","caption":"The quadratic formula."}
```

Supply one `<math>` root, with no namespace or `xmlns="http://www.w3.org/1998/Math/MathML"`; display mode is always block. Use Unicode symbols (`∑`, `∫`, `∞`, `≤`) or numeric references such as `&#x2211;`, rather than named entities such as `&sum;`. Text and attribute values are escaped on output. Unsupported markup is rejected, including HTML, links, event handlers, styles, declarations, comments, and processing instructions.

Supported presentation elements: `mrow`, `mi`, `mn`, `mo`, `mtext`, `ms`, `mspace`, `mfrac`, `msqrt`, `mroot`, `msub`, `msup`, `msubsup`, `munder`, `mover`, `munderover`, `mmultiscripts`, `mprescripts`, `none`, `mtable`, `mtr`, `mtd`, `mstyle`, `mphantom`. Group multi-part numerators, denominators, and script operands in `mrow`. Use `munderover` for sum limits and `mtable`/`mtr`/`mtd` for matrices. Explicit `<mo>` parentheses work as matrix delimiters.

Supported presentation attributes: `displaystyle`, `scriptlevel`, `mathvariant`, `stretchy`, `symmetric`, `largeop`, `movablelimits`, `fence`, `separator`, `form`, `accent`, `accentunder`, `columnalign`, `rowalign`, `columnspan`, `rowspan`. A root `display="block"` is also accepted. Keep nesting within 64 levels. The builder checks the vocabulary, not mathematical correctness or operand counts; verify the notation in the browser. See [MathML Core](https://www.w3.org/TR/mathml-core/) for element semantics.

## Information

```json
{"type":"alert","kind":"note","text":"Relevant information."}
{"type":"code","language":"Shell","text":"printf 'hello\\n'"}
{"type":"table","headers":["State","Meaning"],"rows":[["A","Explanation"],["B","Explanation"]],"caption":"Optional caption."}
{"type":"disclosure","title":"A Useful Question","open":false,"blocks":["The answer."]}
```

Alerts accept `kind`: `note`, `tip`, `important`, `warning`, `caution`. Instead of `text`, an alert can use `blocks`; `title` overrides its default variant label. Do not choose a severe variant for visual variety. Code `language` labels the block; it does not invoke syntax highlighting or execute code. Optional `id` lets a custom script update the code element with `textContent`. Rows must have exactly as many cells as headers. Tables scroll within their rounded container when needed. Disclosures have a plain summary and a padded, tinted body.

## Images

```json
{"type":"image","file":"assets/example.png","alt":"What the image shows","caption":"Optional subject caption."}
```

The builder embeds file bytes as a data URI. PNG, JPEG, GIF, WebP, and SVG work through browser image support. A `src` containing a complete `data:image/...` URI can replace `file`. HTTP URLs and sibling image files are not left in exported HTML. Rounded corners, centered captions, and the enlarge dialog are automatic. Do not put buttons or links around image blocks yourself.

## Interactions

```json
{"type":"tabs","label":"Comparison","tabs":[
  {"title":"Before","blocks":["Earlier behavior."]},
  {"title":"After","blocks":["Changed behavior."]}
]}
{"type":"range","id":"amount","label":"Amount","min":0,"max":20,"step":1,"value":5}
{"type":"choice","id":"mode","label":"Mode","value":"a","options":[{"value":"a","label":"First"},{"value":"b","label":"Second"}]}
```

Tabs work without custom JS and support arrows/Home/End. Disclosures use native details controls. A range control updates its numeric output automatically; its output ID is `<id>-value`. Range/choice controls need a custom script to change any simulation, chart, or calculated result. Do not add an inert control. Custom files are described in [custom.md](custom.md).

## Diagrams, Charts, and Custom Visuals

Use [diagrams.md](diagrams.md) for `diagram`, [charts.md](charts.md) for `chart`, and [custom.md](custom.md) for `html`, `scripts`, and `styles`. Use [icons.md](icons.md) to select valid icon names for cards, flow nodes, or metrics.

IDs are optional except when custom code refers to a component. Supply an ID starting with a letter and containing only letters, digits, hyphens, and underscores. IDs must be unique. The builder reserves shell IDs and generates the rest.

Paragraphs and headings fill their containing column. The page expands to the available viewport width with the shell’s normal side padding; hiding the contents expands the main column.
