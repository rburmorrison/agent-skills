# AGENTS.md

<One sentence describing what this repository is.>

## Repository Rules

- Add, remove, and upgrade dependencies with <the project's package-manager commands, such as `uv add` and `uv remove`>, not by hand-editing manifests or lockfiles.
- Keep core logic and decisions pure over ordinary values, with I/O and state changes at the edges.
- Prefer concrete named types and explicit variants over positional tuples, untyped maps, or magic strings, and use full-word domain names (with units where they matter).
- Break dense or nested expressions into named intermediate variables so each step is clear in review.
- Separate distinct logical stages with blank lines.
- Comment only non-obvious constraints, ordering, or surprises—never narrate what the code already says—and update stale comments when behavior changes.

## Verification

```bash
# After any change
<project verification commands>
```
