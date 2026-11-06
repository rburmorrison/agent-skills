---
name: document-usage
description: Write or update quick-start READMEs, built-in help, and concise user guides. Use whenever editing these documents, including during fixes or skill maintenance, and when usage changes require documentation updates.
---

# Document Usage

Help readers reach a useful result quickly, then explore through the software's own help. Read and apply this skill before editing a README, built-in help, or user guide, even when documentation is incidental to a fix or skill update. Use `document-code` for source documentation and comments.

## Establish the Reader's Task

Inspect the relevant entry points, existing documentation, supported installation method, examples, and help output. Establish what the reader needs to do and what the software actually supports. Preserve applicable project conventions and necessary information; brevity is not a reason to omit prerequisites, consequential limitations, or compatibility requirements.

Use the agreed behavior and scope. Resolve consequential uncertainty during planning, using `plan-changes` when available. Documentation work does not authorize new product behavior, dependency changes, or a repository-wide rewrite. If code and the agreed contract disagree, report the discrepancy rather than documenting invented behavior as established fact.

## Write a Quick Start

Give the README a short purpose statement, necessary setup, and one representative example that reaches a useful result. A few additional common workflows are fine when they are genuinely simple and help someone get started. Do not impose a fixed section template or turn the README into an exhaustive manual.

Make examples runnable for the stated starting conditions. Include required input or a small fixture when needed, and enough expected output or observable effect to recognize success. Prefer a concrete example with a short explanation over a long conceptual introduction.

Use built-in help for ordinary discovery. For CLIs, include verbatim usage or help output where appropriate: capture it from the actual documented command and version, identify that command, and preserve the captured text. Do not reconstruct output, silently edit it, or apply Title Case inside it. If full help overwhelms the quick start, use a clearly identified relevant command's output or link to help instead of presenting a shortened block as complete.

Use Title Case for authored headings. Keep prose concise and direct. Avoid redundant feature inventories, narration of implementation details, and sections added only because a template contains them.

Put substantial workflows or concepts in separate documents only when readers need them, and link from the relevant starting point. Do not create extra documents merely to relocate unnecessary prose or duplicate help and API reference material.

## Keep Documentation Current

Before editing, identify what the reader must understand or do differently and which existing statement or example becomes inaccurate. If the document remains accurate and sufficient, leave it unchanged; a bug fix or internal refinement does not by itself require a README edit.

Revise the owning passage at its existing level of detail rather than appending a sentence about each fix. Keep README summaries focused on purpose, capabilities, and getting started. Put necessary operational details in the relevant help, interface contract, or task guide; omit details that do not help the reader act or decide. A requirement to keep documentation current is not a requirement to describe every change. Do not rewrite accurate prose merely to produce a documentation diff.

Update affected examples, built-in help, guides, and captured output in the same change as the behavior they describe. Preserve unrelated documentation and avoid creating a changelog entry or new guide unless the task or project requires it.

Keep ordinary commands understandable through their names and help. Improve help within the agreed scope when a changed option or workflow needs explanation; use `document-code` for affected source comments and public contracts. Reuse an existing documentation generation mechanism when present. Do not introduce a generator, dependency, or CI workflow merely to refresh a small output block.

## Verify the Reader's Path

Run relevant examples and compare captured usage with the actual program where feasible, using temporary inputs and avoiding unintended external effects. Check links, prerequisites, and consistency between help, examples, and current behavior. Review added prose for duplicated facts and change-history narration, and confirm each detail belongs at that document's level. Run existing documentation checks when applicable; accurately report unavailable execution or unverified output.

Use the task's existing review cadence and concise handoff. Documentation does not require an additional review round. Report material verification limitations without turning the handoff into another user guide.
