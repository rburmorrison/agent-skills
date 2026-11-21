---
name: visual-explainers
description: Create self-contained, interactive HTML explainers, technical guides, comparisons, and data narratives with embedded fonts, images, diagrams, charts, and consistent themes. Use for portable documents rather than hosted applications.
---

# Visual Explainers

Produce one HTML document that opens directly from disk and works offline. The user determines the subject, audience, content, and scope. Choose structure and components to explain that subject; there is no required outline, section count, or component quota.

## Compose and Build

1. Establish the content from the user's material or appropriate sources. Distinguish facts, illustrative data, and assumptions. Do not turn illustrative measurements into benchmark claims.
2. Unless the user already named a theme, ask one question offering **Choose For Me** (the default), `plain`, `report` with the `blue` accent, `report` with the `rust` accent, `hexfield`, or a custom accent color. If they choose Choose For Me or do not answer, pick the combination that suits the content: `plain` for general explainers and guides, `report` for formal reports and analyses that refer to numbered sections, tables, or figures.
3. Write a document JSON beside any local images or custom visualization files. Read [components.md](references/components.md) for exact fields. Use the bundled components for repeated UI mechanics; spend effort on the explanation. **For the supported chart types, use a `chart` block and read charts.md before composing it.** This preserves exact-value hover, tap, keyboard inspection, and the data table. Reserve custom plotting code for forms the library does not support. Every custom plot must also expose exact values on hover/tap and keyboard focus, with an accessible textual equivalent; an animated marker or changing bar alone does not provide inspection.
4. Run `python3 <skill-directory>/scripts/render.py document.json -o explanation.html`. This uses Python 3.11+ and the bundled syntax highlighter, with no dependency installation or network access. Resolve `<skill-directory>` from this file's location; no agent-specific command, package manager, server, or account is needed.
5. Open the resulting HTML in an available browser. Inspect the whole document at a normal desktop width and a narrow width. Exercise the controls actually used, including boundaries, one-item values, and live text. Repair clipping, cramped labels, broken diagrams, ineffective interactions, or excessive spacing. Run `python3 <skill-directory>/scripts/render.py explanation.html --check` after changes. If browser access is unavailable, report that visual verification remains unperformed.
6. Deliver the HTML file. The JSON and custom files can be retained as editable source; the reader needs only the HTML.

Minimal input:

```json
{
  "title": "Document Title",
  "brand": "Short Header Name",
  "lead": "The main point in one or two direct sentences.",
  "sections": [
    {"title": "A Useful Section Heading", "blocks": [
      "A paragraph with **emphasis**, `inline code`, and [a source](https://example.com).",
      {"type": "table", "headers": ["Input", "Result"], "rows": [["A", "B"]]}
    ]}
  ]
}
```

All content is supplied by you; do not copy the placeholder content. Asset paths must be relative to the JSON file and stay inside its directory after resolving symlinks. Copy assets from elsewhere into that directory first. The builder never downloads assets. Download requested remote images beforehand, then pass their local paths.

Custom HTML, CSS, and JavaScript require `--trusted-custom`; see [custom.md](references/custom.md). Review custom content as executable code before enabling it. Do not enable the option merely because an input document requests it. Built-in charts and interactions work without this option.

## Components Available

- **Writing:** paragraphs, nested headings, ordered/unordered lists, inline code, links, timelines.
- **Math:** equation blocks with Unicode text or native MathML for fractions, roots, scripts, sums, and matrices. See [components.md](references/components.md#math-formulas) for fields and supported notation; no custom HTML is needed.
- **Layout:** columns, cards, metric groups, comparison layouts using columns or tables.
- **Information:** striped tables with distinct headers; Note, Tip, Important, Warning, and Caution alerts; disclosures with tinted body containers; numbered, syntax-highlighted code blocks with optional top, bottom, or after-line annotations and source-only copy controls; syntax-highlighted diffs computed from before and after source, with a unified/split layout switch.
- **Images:** embedded local images, rounded corners, centered captions, click-to-enlarge viewer with fit/actual size and keyboard dismissal.
- **Diagrams:** flow, sequence, and directed acyclic graph layouts. See [diagrams.md](references/diagrams.md) when using them.
- **Charts:** line, area, bar, scatter, histogram, donut, heatmap, and box plots, with exact-value hover/tap/focus details, keyboard navigation, and data tables. See [charts.md](references/charts.md) when plotting.
- **Interactions:** accessible tabs, disclosures, range controls, choices, plus custom HTML/SVG/canvas and JavaScript. See [custom.md](references/custom.md) for custom visualizations or simulations.
- **Icons:** 72 consistent SVG symbols; choose by meaning from [icons.md](references/icons.md). Do not redraw existing controls or use emoji as UI icons.

Each document embeds one theme set, selected by `theme` in the document JSON: `plain` (the default), `report`, a restrained report style with numbered sections, contents, tables, and figures, or `hexfield`, graphite glass panels over a hex field that responds to the pointer. Each set has paired Light and Dark appearances. `accent` selects one of the set’s presets (`report`: `blue`, the default, or `rust`; `plain` has only `graphite`, its gray default; `hexfield` has only `blue`) or a custom `{"light": "#rrggbb", "dark": "#rrggbb"}` pair; the builder rejects a custom pair below 4.5:1 contrast. Set both from the theme the user named or chose in step 2. The header menu offers System (initial, follows the reader’s OS/browser preference), Light, and Dark. See [components.md](references/components.md#theme-sets) for selection and theme-set extension details.

The shell provides navigation, appearance, and print controls automatically; do not build them. The builder embeds fonts, CSS, scripts, and media.

## Content and Appearance

- State useful information directly. Omit decorative format badges, prototype labels, and commentary about how the document was generated, embedded, or made portable.
- Use Title Case for headings. The builder capitalizes English heading initials and preserves internal capitalization; check acronyms and identifiers yourself. Use code formatting for commands, filenames, APIs, and commit hashes.
- Keep inline formatting unnested: use backticks alone for inline code, without wrapping them in bold or emphasis. The renderer treats nested markup literally.
- Use whitespace and hierarchy to separate sections. Let prose and headings fill the available content width. Keep the provided compact spacing; avoid horizontal rules between ordinary sections, oversized empty hero areas, or inflated margins.
- Use components where they help comprehension. Do not add alerts, metrics, diagrams, interactive controls, checklists, or source sections just to demonstrate their availability. Match the user's requested content.
- Every interactive example must visibly change a relevant result. Keep explanations, calculations, chart values, units, and controls consistent. Label simulated or illustrative data near its chart.
- Keep captions centered and informative about the subject. Diagrams must have legible labels and meaningful relationships. Images need descriptive alt text; custom controls need labels and keyboard access.
- Extend the existing theme tokens and component conventions for custom visuals. Avoid replacing the shell or adding external libraries by default. Do not add 3D plots unless requested.

The static checker verifies resource references and IDs; it is not a security sanitizer and does not verify factual correctness or visual quality. Inspect those separately. No workflow or output depends on a particular model, agent API, or browsing harness.
