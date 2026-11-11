# AGENTS.md

This repository is a collection of personal agent skills.

## Repository Rules

- After editing any readable JavaScript in `skills/documentation/visual-explainers/assets/`, run `just build-js` to regenerate the adjacent `.min.js` files and include those generated files with the source changes before committing. Edit the readable sources rather than the generated files; `just check` rejects stale or missing minified assets.
- When skills are added or modified, review README.md and update affected skill listings, purpose, scope, or usage instructions. Leave accurate entries unchanged; do not add fix-specific details or rewrite prose solely to produce a README diff. Before editing the README, read and apply this repository's documentation standards in [code-authoring](skills/engineering/code-authoring/SKILL.md), including when an installed copy is available.
