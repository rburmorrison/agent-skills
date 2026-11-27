# AGENTS.md

<One sentence describing what this repository is.>

## Repository Rules

- Add, remove, and upgrade dependencies with <the project's package-manager commands, such as `uv add` and `uv remove`>, not by hand-editing manifests or lockfiles.
- Keep core logic and decisions pure over ordinary values, with I/O and state changes at the edges.
- Use descriptive, full-word names from the problem domain (including units where they matter) instead of abbreviations, and prefer concrete named types and explicit variants over positional tuples, untyped maps, magic strings, or catch-all types.
- Break dense logic into named intermediate variables and short, named stage helpers so each step explains what the data represents instead of packing multiple concepts into a few lines.
- Separate distinct logical stages with blank lines. Comment only non-obvious constraints, ordering, or surprises rather than what the code already says, and update stale comments when behavior changes.

## Verification

```bash
# After any change
<project verification commands>
```
