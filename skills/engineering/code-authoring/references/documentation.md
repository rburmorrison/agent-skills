# Documentation

Code changes allow useful inline implementation comments and source API doc comments/docstrings for affected code without listing each in the plan. Usage documentation requires a bounded documentation map. This reference owns the scope rules, the map format, the writing standards, and the final accuracy check; planning, authoring, and review each apply the part that fits their role.

## Documentation Scope

Usage documentation—READMEs, guides, standalone reference material, built-in help, and user examples—requires a bounded documentation map: exact location, existing inaccurate claim and correction or explicitly requested addition, and verification. Correct claims at their existing level of detail; leave accurate content unchanged. An omitted map permits no usage-documentation edits. A direct, explicit documentation request supplies scope and may use a brief plan.

New documents, sections, examples, or previously undocumented facts require an explicit user request or confirmation recorded in the plan, even inside an existing passage. Do not infer permission from code requirements, general plan approval, or your judgment that an addition would help. An accuracy inspection, reviewer finding, or documentation lint does not expand scope. For an unplanned edit, leave the material unchanged and use the immediate-question procedure under Roadblocks and Handoff in `code-authoring`.

### Documentation Map Entries

Each entry names the planned edit's path and section or symbol, the existing claim made inaccurate by the change, the required correction, and its verification. Listing a file or saying "update documentation" is not sufficient scope. By default, plan only accuracy fixes. The planner may ask whether the user wants a specific addition and explain why, but must wait for confirmation before including it, then record that authorization in the map. If no edits are needed or requested, the plan states "No usage-documentation edits planned." The implementer must not edit usage documentation outside the map; a newly discovered need requires a confirmed plan amendment.

Plan a final accuracy inspection, including related documentation outside the edit map; inspection does not authorize unplanned edits. Surface project requirements that would need additions beyond the requested scope.

## Document Interfaces and Decisions

Apply these standards to source API doc comments/docstrings and authorized standalone interface documentation. Inspect the affected code, callers, existing documentation, and tooling before promising a contract.

Interfaces intended for other components, including within the project, are the boundary for caller-facing contracts. Include types and relevant members, not just functions. Visibility keywords, underscores, and module names are evidence of intent rather than the sole definition of that boundary. Truly internal implementation details usually need no documentation comment.

- Use a concise brief and complete applicable contract sections in the project's native documentation format. Omit inapplicable sections and boilerplate; do not restate type annotations without explaining meaning.
- Keep free-form bodies exceptional: use a short body only for a caller-facing concept or interaction that must be understood together and cannot be explained clearly in the brief, members, or contract sections. Importance or non-obviousness alone does not justify a body.
- Assign facts to their owning interfaces. Put input and result semantics in the brief or applicable contract sections, failures in the error section, and member facts on members. Remove duplication rather than moving it under Notes or Details or overloading the brief.
- Keep type documentation self-contained: describe intrinsic meaning, members, enforced invariants, and obligations for correct use. Avoid narrating external parsers, factories, or consumers. Put an operation's behavior and guarantees on that operation; public construction or mutation may bypass validation, so do not promise that every instance is validated when only one operation guarantees it. Distinguish type-wide guarantees from operation-specific guarantees.
- Check callers and propagated failures before describing errors. Preserve caller-relevant obligations; omit speculative failures and implementation walkthroughs. Use examples when requested and when they materially clarify correct use.
- Use Title Case for authored headings, keeping interior articles, short conjunctions, and short prepositions (such as "and", "or", "of", "to") lowercase, while preserving required documentation tags, identifiers, and syntax.

Read [Python documentation](documentation-python.md) or [Rust documentation](documentation-rust.md) when editing documentation in those languages. Use native formats and existing tooling for other languages.

Private doc comments are useful only for otherwise unclear contracts or constraints. Documentation-only work does not authorize restructuring code or changing behavior to fit a comment.

Follow project documentation lints, including for otherwise internal items, within Documentation Scope. Do not weaken checks, change visibility, or rename items to evade them.

## Write Usage Documentation Within Scope

Before editing a README, built-in help, or user guide, identify its audience, core purpose, and the task it helps the reader complete. Inspect the relevant entry points, supported installation method, examples, and actual help. Preserve prerequisites, consequential limitations, compatibility information, and applicable project conventions.

Match each edit to the agreed documentation map before writing.

Keep a README focused on its purpose, necessary setup, and a representative path to a useful result. Revise the owning passage with concise, direct prose and Title Case for authored headings. Avoid redundant feature inventories, implementation narration, and change-history details. Do not impose a fixed section template.

Keep existing examples runnable from their stated starting conditions, with required inputs and enough observable output to recognize success. Capture help from the actual documented command and version, identify the command, and preserve the captured text verbatim. Do not reconstruct help, silently edit it, apply Title Case inside it, or present a shortened block as complete. Use an identified subcommand's help or a link when full help would overwhelm the document.

Use existing help and references for discovery. For authorized additions, put substantial workflows or concepts in separate documents only when readers need them, link from the relevant starting point, and avoid duplicating help or API reference material. Reuse existing documentation-generation mechanisms; do not introduce tooling merely to refresh a small output block.

## Verify Documentation Edits

Run existing documentation lints, builds, and executable examples where applicable. Check format and attachment of changed source documentation, including review fixes; inspect rendered or extracted output when syntax may hide or misattach it. Check relevant links, prerequisites, examples, and captured help against actual behavior where feasible, using temporary inputs and avoiding unintended external effects. Report unavailable execution and unverified output accurately.

## Final Documentation Accuracy Check

At the end of every code change, after implementation and review fixes and before handoff, explicitly check whether existing documentation needs updating:

1. Discover existing documentation related to the changed behavior in the repository; the plan's file list and edit map are not an exhaustive inspection list. Include interface contracts, inline implementation comments in touched code, READMEs, built-in help, guides, and examples. Inspect relevant content even if its file or comment lines were unchanged. Check existing comments against the current logic, assumptions, and rationale.
2. Identify each document's core point, audience, and level of detail. Match needed corrections to Documentation Scope and the plan's map; ask immediately about unplanned usage-documentation needs. Correct or remove stale source comments within affected code.
3. Audit the usage-documentation diff for unplanned edits and new facts inserted alongside valid corrections, including facts taken from implementation requirements. Remove unauthorized additions while preserving planned corrections. Verify permitted edits with the applicable checks above, within the task's review cadence; do not add a documentation-only review round. Repeat the affected accuracy check if later code changes invalidate its result.

Briefly state in the handoff whether planned documentation was updated, no update was needed, or an unplanned need remains awaiting a decision. Report unmet project requirements without expanding scope.
