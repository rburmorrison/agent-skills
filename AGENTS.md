# AGENTS.md

This repository is a collection of personal agent skills.

## Repository Rules

- Edit the readable JavaScript in `skills/documentation/visual-explainers/assets/`, not the adjacent generated `.min.js` files, and commit the regenerated files together with the source changes; `just check` rejects stale or missing minified assets.
- When skills are added or modified, review README.md and update affected skill listings, purpose, scope, or usage instructions. Leave accurate entries unchanged, and do not add fix-specific details or rewrite prose solely to produce a README diff.

## Verification

```bash
# After editing JavaScript in skills/documentation/visual-explainers/assets/
just build-js

# After any change
just check
```
