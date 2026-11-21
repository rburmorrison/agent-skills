# Document and Component Fields

Use JSON, not Python code. Strings inside `blocks` are paragraphs. All paths are relative to the input JSON. Objects below show the supported fields; optional fields are noted. Nested `blocks` use the same vocabulary.

## Document

Required: `title`. Optional: `brand` (short header name; defaults to title), `lead`, `description`, `theme` (theme set: `plain`, the default, `report`, or `hexfield`), `accent` (preset name or custom pair; see [Theme Sets](#theme-sets)), `lang` (default `en`), `intro` (blocks below the lead), `sections` (list of `{title, blocks, id?}`), `scripts` (local JS file paths), `styles` (local CSS file paths). All asset paths must be relative and remain within the JSON directory after resolving symlinks. `html` blocks and nonempty `scripts`/`styles` require the operator's `--trusted-custom` option; see [custom.md](custom.md).

The shell creates H1. Sections create H2 and ToC entries. You choose all section names and ordering. Heading blocks create H3/H4; H3 joins the ToC except inside tabs. Component titles are labels, not extra sections. No footer or source section is forced. Use paragraphs/links or a section when sources are useful.

## Theme Sets

`theme` selects one supported set at generation time, for example `"theme": "report"`. `plain` is the default; `report` numbers sections, H3 subsections outside the intro and tabs, their contents entries, captioned tables, and captioned image, chart, and diagram figures, and uses IBM Plex fonts; `hexfield` uses Inter, frosted panels, and a hex field behind the page that reacts to hovering, dragging, and clicking empty space. Each output embeds just that set’s fonts and paired light/dark palettes; the reader cannot switch sets.

`accent` picks one of the set’s presets, for example `"accent": "rust"`; `report` offers `blue` (the default) and `rust`, `plain` offers only `graphite`, its gray default, and `hexfield` offers only `blue`. A preset can also adjust related tokens such as chart series colors. For another color, supply `{"light": "#rrggbb", "dark": "#rrggbb"}`; it replaces only the accent, and the builder rejects it unless the accent keeps 4.5:1 contrast with the page, panel, and wash grounds and with button text in both appearances.

To add a supported set, write a manifest at `assets/themes/<name>.json` and register its path in `THEMES` in `scripts/render.py`. The manifest lists its `fonts` (role `sans` or `mono`, TrueType file, CSS weight, and license file; run `just build-fonts` to generate the embedded WOFF2 copy), its `tokens` as `[light, dark]` colors, its `accents` (`default` and named `presets` of token overrides), a `stylesheet` in `assets/themes/`, an optional `script` naming a readable `.js` file in `assets/` (add it to `SOURCE_NAMES` in `scripts/build-javascript.mjs`; the builder embeds its generated `.min.js` after the shell controller), and optional `"numbered": true`, which makes the builder emit fixed `data-number` attributes on those headings and captions for the stylesheet to display. Use `assets/themes/plain.json` and `plain.css` as the contract: the builder emits each token through `light-dark()` for the shell’s selected color scheme and derives the menu swatches from `bg`, and the stylesheet supplies shadow and backdrop colors, the print palette, and set-specific styling, embedded only when selected. The shared shell owns layout, appearance switching, and print behavior.

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
{"type":"diff","language":"Python","before":"x = 1\n","after":"x = 2\n"}
{"type":"table","headers":["State","Meaning"],"rows":[["A","Explanation"],["B","Explanation"]],"caption":"Optional caption."}
{"type":"disclosure","title":"A Useful Question","open":false,"blocks":["The answer."]}
```

Alerts accept `kind`: `note`, `tip`, `important`, `warning`, `caution`. Instead of `text`, an alert can use `blocks`; `title` overrides its default variant label. Do not choose a severe variant for visual variety. Rows must have exactly as many cells as headers. Tables scroll within their rounded container when needed. Disclosures have a plain summary and a padded, tinted body.

### Code Blocks

Code `language` labels the block and selects syntax highlighting during generation; it does not execute code. Use a recognized Pygments name or alias, such as `"Rust"` or `"rust"`; matching is case-insensitive. Missing or unknown languages render as plain text. Keep descriptions such as “Actual Source” in `annotations`, outside `language`: `"Rust · Actual Source"` is not a recognized language.

Code blocks are numbered by source line, including blank lines, not by wrapped rows. Copy copies only the source, not numbers or annotations.

Use the optional `annotations` list for full-width explanatory notes. Each object requires a nonblank string `text` and accepts an optional string `title`; both use the existing safe inline formatting. `position` defaults to `"top"`, accepts `"bottom"`, or takes a positive integer meaning **after that source line**. Multiple notes at the same position keep their list order. Invalid fields, types, positions, or line numbers stop generation with an error; correct them rather than moving the note silently. Choose notes and positions that help explain the source; no annotation is required.

Add `lines` to identify the source a note explains: an integer for one line or `[start, end]` for an inclusive range. This is independent of `position`; omitting it leaves a neutral general note. Bounds must be integers within the source, with start no greater than end; invalid bounds stop generation. Referenced notes show a line badge and matching source shading. Overlapping ranges are supported.

```json
{
  "type": "code",
  "language": "Rust",
  "text": "fn total(values: &[i32]) -> i32 {\n    values.iter().sum()\n}",
  "annotations": [
    {"title": "Actual Source", "text": "Adds the values in a borrowed slice."},
    {"position": 2, "lines": 2, "text": "`sum()` returns zero when the iterator is empty."},
    {"position": "bottom", "lines": [1, 3], "title": "Result", "text": "The input slice is left unchanged."}
  ]
}
```

Optional `id` identifies the code container. A custom script can replace its contents with `textContent`; the replacement is plain text without highlighting, numbers, or annotations, and Copy uses that replacement text.

### Diff Blocks

A `diff` block compares two versions of one source. Supply the earlier text as `before` and the later text as `after`; the builder computes the line differences, so do not write `+` or `-` markers or a patch yourself. Take both versions from the real source, such as `git show <commit>:<path>`. Use an empty string for the missing side of an added or removed file. Identical versions stop generation with an error.

The reader switches between a unified layout and a side-by-side split layout, and switching one diff switches every diff in the document; a container too narrow for two columns shows the unified layout without the switch. Both layouts keep syntax highlighting, mark removed and added lines with a sign as well as color, and show the count of added and removed lines.

```json
{
  "type": "diff",
  "language": "Python",
  "title": "orders/totals.py",
  "view": "split",
  "context": 3,
  "before_start": 40,
  "after_start": 42,
  "before": "def total(items):\n    return sum(items)\n",
  "after": "def total(items, discount=0):\n    return sum(items) - discount\n"
}
```

Only `before` and `after` are required. `language` selects highlighting as it does for code blocks. `title` labels the bar, typically with the file path, and defaults to the language. `view` sets the initial layout, `"unified"` (the default) or `"split"`. Use the same `view` for every diff in a document, since the reader's switch applies to all of them. `context` is the number of unchanged lines kept around each change, default 3; longer unchanged runs collapse into a row stating how many lines were omitted, so whole functions or files can be supplied. When the versions are excerpts, set `before_start` and `after_start` to the file line number of each excerpt's first line; both default to 1. Lines compare by content, ignoring line-ending differences. An invalid `view`, `context`, or start line stops generation.

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

Paragraphs and headings fill their containing column.
