---
name: align-codebase
description: Align an existing codebase with the user's engineering conventions through a scoped, behavior-preserving refactor. Use only when explicitly requested.
---

# Align Codebase

Use this workflow only when the user explicitly invokes it or requests codebase alignment. It is not an automatic cleanup phase of ordinary feature or bug-fix work. Keep the work language-agnostic and use the project's supported language versions and conventions.

Use `plan-changes` and `implement-changes` for the shared planning, coding, testing, review, and handoff policies. Read their instructions when entering those phases; do not maintain a second set of coding rules here. If supporting guidance is unavailable, disclose it and proceed only where the supplied requirements and project guidance are sufficient.

## Assess and Plan

Inspect the requested scope, public entry points, callers, tests, and tooling. Establish current observable behavior and run relevant baseline checks. Distinguish pre-existing failures from regressions introduced by the refactor.

Identify concrete comprehension or maintenance problems: mixed responsibilities or I/O, domain values losing meaning across boundaries, unclear names, difficult logic grouping, misplaced modules, or tests that obscure their claimed behavior. Explain the benefit of each proposed change. Preserve cohesive code that already reads well; file coverage, function length, and helper counts are not goals.

Plan a few coherent changes using `plan-changes`. Specify the affected modules and contracts, compatibility constraints, behavior-preservation evidence, and exclusions. Preserve public APIs, imports, output, errors, ordering, persistence, and supported versions unless the user explicitly agrees to change them. Do not silently turn an apparent bug into a behavior change.

Resolve consequential questions one at a time before editing. Choose scope from the user's request and existing context; ask only when a consequential boundary remains unclear. A broad alignment request is not authorization for new features, dependency upgrades, or an unrelated rewrite.

Assess tooling against the existing project. Propose any stricter lint adoption or configuration migration during planning, including its cleanup scope. Do not apply a greenfield profile wholesale to an existing codebase or weaken checks to make a refactor pass. Relevant language profiles may inform an agreed tooling change.

Use existing behavior tests and add focused characterization only where a changed contract lacks useful coverage. Lock in observable behavior, not the current internal structure. Identify tests whose failure setup never reaches the claimed boundary.

## Execute the Agreed Alignment

Complete planning before edits. Respect planning-only requests. When implementation is already authorized and consequential decisions are settled, proceed without adding another approval checkpoint.

Use `implement-changes` for execution and review. If the user also explicitly requests `implement-verified-steps`, follow that cadence instead of stacking two review workflows. Do not activate that manual workflow merely because the refactor is large.

Keep changes tied to the agreed improvements. Preserve compatibility through existing interfaces or a small adapter when needed; avoid gratuitous abstraction or splitting. Compare verification results with the baseline and resolve introduced regressions.

For a roadblock requiring changed behavior or scope, finish useful independent work and report the incomplete portion using the shared blocker policy. In the final handoff, explain the useful structural changes, the contracts preserved, verification and any pre-existing failures affecting confidence, and only the most useful review locations. Do not produce an exhaustive inventory of untouched style issues.
