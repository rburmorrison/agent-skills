---
name: document-code
description: Document public interfaces with concise briefs and complete applicable contracts, maintain them as code changes, and add selective comments for non-obvious implementation rationale. Follow documentation lints even for internal items.
---

# Document Code

Document the contract another caller needs while keeping the implementation readable through names, grouping, intermediate values, cohesive functions, and locality. Use this skill when adding or changing interfaces or source documentation; use `document-usage` for READMEs, help, and user guides.

## Identify the Documentation Boundary

Inspect the affected code, callers, existing documentation, and documentation tooling. Interfaces intended for other components to consume need full documentation, including interfaces used only within the same project. Include public types and relevant members, not just functions. Visibility keywords, underscores, and module names are evidence of intent rather than the sole definition of this boundary.

Truly internal implementation details usually need no documentation comment. Project documentation lints take precedence: document every item they require, even if the item would otherwise be treated as internal. Do not weaken or suppress those rules merely to avoid documentation, or change visibility or naming to evade them.

## Describe the Contract Briefly

Start with a concise brief and complete applicable contract or example sections in the language and project's documentation format. A body is free-form prose outside the brief and named contract or example sections. Add a short body only for an exceptional caller-facing concept or interaction that must be understood as a whole and cannot be explained clearly in the brief, relevant members, or applicable contract sections. A fact being important or non-obvious does not by itself justify a body. Preserve all obligations needed for correct use.

Assign each fact to the interface that owns it. Put input and result semantics in the brief or applicable contract sections, failure conditions in the error section, and member-specific facts on the relevant members. Remove duplicated explanations rather than moving them under Notes or Details, and keep the brief readable rather than packing several contracts into it.

Keep type documentation self-contained: describe the type's intrinsic meaning, members, and enforced invariants without narrating external parsers, factories, or consumers. Obligations for interpreting or using the type are part of its own contract, not a description of its callers' implementations; retain exceptional context needed to understand those obligations together. Put an operation's behavior and guarantees on that operation. Public construction or mutation may bypass validation; do not describe every instance as validated when only a particular operation provides that guarantee.

Use Title Case for authored section headings while preserving required documentation tags, identifiers, and syntax. Omit inapplicable sections rather than filling them with boilerplate. Avoid restating type annotations without explaining meaning, and avoid implementation walkthroughs. Add an example when it materially clarifies correct use.

Read the relevant language reference when documenting these languages:

- [Python](references/python.md): briefs, arguments, results, exceptions, and public attributes.
- [Rust](references/rust.md): briefs, error contracts, public items, and other required sections.

For other languages, apply the same principles through their native documentation format and existing project tooling. Do not impose Python or Rust syntax on them.

## Keep Implementation Comments Selective

Use private doc comments only when a non-obvious contract or constraint would otherwise be unclear. Inline comments should explain meaningful edge cases or the reason for a decision that is sensible but not self-explanatory. Place the explanation near the decision; do not narrate assignments, branches, or obvious function calls.

Prefer self-documenting code within the agreed implementation scope. A documentation-only task does not authorize restructuring the code. Preserve useful rationale even when shortening comments; remove stale explanations only after checking what the current code does.

## Maintain and Verify

Update affected documentation in the same change as signatures, return values, error behavior, invariants, or assumptions. Check callers and propagated failures before promising a contract; distinguish caller-relevant errors from speculative failures. Do not document desired behavior as if it already exists, or change behavior to fit an old comment.

Run applicable documentation lints, builds, and executable examples already supported by the project. Check changed documentation blocks against the required format, including edits made to resolve review findings. Inspect the rendered or extracted result when source syntax might hide or misattach documentation. Keep edits tied to the task and affected contracts rather than documenting every untouched symbol.

Use the task's existing verification and review cadence; do not add a documentation-only review round. Report material gaps or unavailable checks accurately.
