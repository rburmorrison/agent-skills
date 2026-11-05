# Diagrams

Choose a built-in layout when it expresses the relationship. Choose custom SVG/HTML for specialized geometry or a dense network. Built-ins provide themed containers and labels. `title` and `caption` are optional. Keep labels short enough to read; put detail in surrounding prose.

## Flow

Ordered stages. Cards share an aligned row when every stage and connector fits. Otherwise they stack with centered SVG arrows; stages never wrap into disconnected rows. Each node has `label`, optional `text`, optional `icon` from [icons.md](icons.md).

```json
{"type":"diagram","kind":"flow","title":"Processing Stages","nodes":[{"label":"Read","text":"Load the input.","icon":"document"},{"label":"Transform","text":"Apply the rule.","icon":"transformation"},{"label":"Return","text":"Produce the result.","icon":"output"}]}
```

## Sequence

Messages between 2–6 named actors. `from` and `to` are zero-based actor indices. Messages appear top to bottom; short labels sit above directional arrows. Self-messages are supported. Measured labels sit above their arrows, including self-message loops. On narrow screens this component scrolls horizontally, retaining legible type.

```json
{"type":"diagram","kind":"sequence","title":"Request and Response","actors":["Client","Service","Store"],"messages":[{"from":0,"to":1,"label":"Request"},{"from":1,"to":2,"label":"Read"},{"from":2,"to":1,"label":"Data"},{"from":1,"to":0,"label":"Response"}]}
```

## Directed Graph

A small directed **acyclic** graph. The builder lays out layers left to right, measures labels using the bundled font, and reserves separate gutters for connections. Links that skip layers route above the blocks. Connection labels wrap within reserved lanes and remain visible. Nodes have unique `id` and `label`. Edges have `from`, `to`, optional short `label`. Cycles are rejected; sequence diagrams or a custom visual are better for feedback loops. Graphs scroll inside their container when extra width is needed to retain readable labels. For dense crossing edges or specialized layouts, author a custom SVG rather than squeezing a diagram into this layout.

```json
{"type":"diagram","kind":"graph","title":"Dependencies","nodes":[{"id":"app","label":"Application"},{"id":"api","label":"API Client"},{"id":"store","label":"Local Store"}],"edges":[{"from":"app","to":"api","label":"calls"},{"from":"app","to":"store","label":"reads"}]}
```

Diagrams should express actual relationships. Do not use a sequence of boxes to decorate prose that has no sequence, and do not imply causal arrows for mere association. Validate labels, arrow directions, and what the diagram leaves out against the explanation.
