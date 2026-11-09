---
name: code-authoring
description: Write or modify code, tests, interface documentation, READMEs, help, and user guides within the agreed scope. Apply readable code and documentation standards, verify behavior, and finish code changes by checking existing documentation for accuracy.
---

# Code Authoring

Use for new code, features, fixes, refactors, and source or usage documentation edits. For planning or review tasks, apply the relevant standards without executing the authoring workflow. Ordinary code changes authorize selective implementation comments and accuracy updates to existing documentation; other documentation additions require the user's direction.

For each automatic documentation edit, identify the existing statement or example made inaccurate by the code change and revise only what is necessary to correct it. Adding a previously undocumented fact inside an existing paragraph, sentence, or API documentation block is still new documentation. Do not add such facts merely because they are accurate, relevant, or mentioned in the implementation requirements. A requirement for code to provide or preserve behavior is not a request to document it. New information requires the user's direction. The selective implementation comments described below remain a separate allowance.

Use the agreed plan and decisions from the conversation. If consequential behavior or scope remains unresolved, complete planning with the user one question at a time before editing; use `plan-changes` if available. A small unambiguous task needs only proportionate planning.

## Execute Within Scope

Choose local implementation details autonomously while preserving agreed behavior, public contracts, architectural boundaries, and scope. Necessary supporting changes must serve the requested outcome. Keep optional cleanup, new features, dependency upgrades, and reorganizations outside the change unless planned.

Concentrate filesystem, network, database, clock, and environment access at explicit boundaries where applicable. Pass ordinary values into core transformations and decisions. Use the project's existing boundary mechanisms; introduce abstractions only when they make a concrete responsibility or dependency easier to manage.

Manage dependencies through the project's package manager. Use actual package information and supported-version constraints; do not guess versions or hand-edit dependency entries as a shortcut. Respect existing workspace dependencies and lockfile policy. If the needed tool is unavailable, apply the blocker policy instead of silently bypassing it.

## Shape Readable Code

- Name domain concepts, responsibilities, and operations using the problem's vocabulary.
- Prefer named records, fields, and explicit variants for domain values crossing boundaries. Local, immediately unpacked tuples remain useful. Add runtime validation at external boundaries when required; do not add a validation dependency merely to name internal fields.
- Group statements that perform one conceptual step. Separate changes of purpose with whitespace. Compact match arms generally form one unit and need no extra blank lines.
- Extract coherent operations with meaningful names. Keep a simple sequence together when splitting it would add navigation without improving comprehension.
- When substantial domain calculations sit among I/O operations, separate the calculation from the orchestration. Preserve transaction and snapshot boundaries while doing so.
- Organize modules by responsibility and reasons to change. Keep types near the code that owns their meaning. Treat size and complexity as inspection signals rather than incentives to create trivial files or helpers.
- Use idioms supported by the declared language version. Pattern matching suits meaningful variants and structured alternatives; ordinary predicates can remain conditionals.
- Keep affected interface documentation and source comments accurate using the documentation standards below.

Read [the code examples](references/code-examples.md) for non-trivial implementation or when resolving a style tradeoff. Their languages illustrate shared principles rather than restricting the skill's scope.

### Explain Non-Trivial Logic

Add implementation comments only when they explain something the code does not make clear, such as a non-obvious assumption, meaningful edge case, or reason a decision is necessary. Do not add comments merely because the logic is complex; complex code that already communicates its meaning needs no explanatory comment. Prefer clear names and cohesive code where they convey the meaning directly. Place useful comments near the relevant code, and do not narrate assignments, branches, or obvious calls.

- Use standalone single-line comments in the language's ordinary comment syntax, such as `#` or `//`. Do not use multiline or block-comment syntax for implementation comments.
- For longer explanations, use consecutive single-line comments as one group, without blank lines between them.
- Put a blank line above each comment group unless it is the first content at the top of its enclosing code block. Keep the comment adjacent to the code it explains.
- Keep API documentation syntax separate: native docstrings and documentation comments follow the interface documentation standards below, not these implementation-comment formatting rules.

When modifying code, inspect its existing implementation comments even when the comment lines themselves are unchanged. Check that they still describe the logic, assumptions, and rationale accurately. Correct or remove stale comments after checking current behavior, preserve useful rationale when shortening them, and leave accurate comments unchanged. Include these comments in the final documentation accuracy check.

See [the implementation comment examples](references/code-examples.md#implementation-comments) when choosing comment placement or syntax, or updating a stale explanation.

## Document Interfaces and Decisions

Apply these interface documentation standards to existing documentation and documentation additions requested by the user. A code change alone does not authorize documenting previously undocumented interfaces or adding API explanations. Inspect the affected code, callers, existing documentation, and tooling before promising a contract.

Interfaces intended for other components, including within the project, are the boundary for caller-facing contracts. Include types and relevant members, not just functions. Visibility keywords, underscores, and module names are evidence of intent rather than the sole definition of that boundary. Truly internal implementation details usually need no documentation comment.

- Within the authorized documentation scope, use a concise brief and complete applicable contract or example sections in the project's native documentation format. These format and completeness standards do not authorize adding previously undocumented facts. Omit inapplicable sections and boilerplate; do not restate type annotations without explaining meaning.
- Keep free-form bodies exceptional: use a short body only for a caller-facing concept or interaction that must be understood together and cannot be explained clearly in the brief, members, or contract sections. Importance or non-obviousness alone does not justify a body.
- Assign facts to their owning interfaces. Put input and result semantics in the brief or applicable contract sections, failures in the error section, and member facts on members. Remove duplication rather than moving it under Notes or Details or overloading the brief.
- Keep type documentation self-contained: describe intrinsic meaning, members, enforced invariants, and obligations for correct use. Avoid narrating external parsers, factories, or consumers. Put an operation's behavior and guarantees on that operation; public construction or mutation may bypass validation, so do not promise that every instance is validated when only one operation guarantees it.
- Check callers and propagated failures before describing errors. Preserve caller-relevant obligations; omit speculative failures and implementation walkthroughs. Use examples when requested and when they materially clarify correct use.
- Use Title Case for authored headings while preserving required documentation tags, identifiers, and syntax.

Read [Python documentation](references/documentation-python.md) or [Rust documentation](references/documentation-rust.md) when editing documentation in those languages. Use native formats and existing tooling for other languages.

Private doc comments are useful only for otherwise unclear contracts or constraints. Documentation-only work does not authorize restructuring code or changing behavior to fit a comment.

Follow project documentation lints, including for otherwise internal items. Do not weaken checks, change visibility, or rename items to evade them. If a check requires documentation additions beyond the user's request, report that scope conflict rather than silently adding documentation or suppressing the check.

## Write Usage Documentation Within Scope

Before editing a README, built-in help, or user guide, identify its audience, core purpose, and the task it helps the reader complete. Inspect the relevant entry points, supported installation method, examples, and actual help. Preserve prerequisites, consequential limitations, compatibility information, and applicable project conventions.

Keep a README focused on its purpose, necessary setup, and a representative path to a useful result. Revise the owning passage at its existing level of detail. Keep prose concise and direct, with Title Case for authored headings. Preserve accurate content; avoid redundant feature inventories, implementation narration, and change-history details. Do not impose a fixed section template.

Keep existing examples runnable from their stated starting conditions, with required inputs and enough observable output to recognize success. Capture help from the actual documented command and version, identify the command, and preserve the captured text verbatim. Do not reconstruct help, silently edit it, apply Title Case inside it, or present a shortened block as complete. Use an identified subcommand's help or a link when full help would overwhelm the document.

Use existing help and references for discovery. New sections, examples, guides, or expanded explanations require the user's request. When additions are requested, put substantial workflows or concepts in separate documents only when readers need them, link from the relevant starting point, and avoid duplicating help or API reference material. Reuse existing documentation-generation mechanisms; do not introduce tooling merely to refresh a small output block.

## Verify Behavior

Read [the testing guidance](references/testing.md) when adding or changing tests. Cover meaningful agreed behavior and failure cases with readable setup, actions, and assertions. Test count is not a target.

Run applicable project formatting, linting, type, and behavior checks. Record what ran and any limitations. Do not claim that checks passed when they were unavailable or not executed.

For documentation edits, run existing documentation lints, builds, and executable examples where applicable. Check format and attachment of changed source documentation, including review fixes; inspect rendered or extracted output when syntax may hide or misattach it. Check relevant links, prerequisites, examples, and captured help against actual behavior where feasible, using temporary inputs and avoiding unintended external effects. Report unavailable execution and unverified output accurately.

Lint and type-check suppressions must be rare, narrowly scoped, and accompanied by a specific reason. Prefer fixing the underlying problem. Use native justification syntax when available, otherwise a nearby explanation. Explain configuration-level exceptions beside the setting; do not weaken checks simply to obtain a pass.

## Independent Review

For non-trivial changes, default to one full review of the completed change by a separate agent with fresh context. Honor an explicit task or invoked workflow's review cadence instead; do not append the default review to that workflow. Disable conversation-history inheritance when starting a reviewer: for tools exposing `fork_turns`, use `"none"`. Supply a self-contained review brief instead. Behavioral changes involving interacting components, public contracts, persistence, or significant refactoring normally qualify. Pure formatting and typo corrections usually do not.

Give the reviewer the agreed plan and decisions, actual final diff including new files, relevant code, and verification results. Use `review-changes` if available. Do not supply the implementer's self-assessment or a desired verdict. Use the task's chosen reviewer model; if none was chosen, use the environment's normal inheritance rather than guessing model IDs or upgrading silently.

Assess findings against the code. Fix validated findings within scope and rerun affected checks. Request a targeted follow-up autonomously only when a material change to logic, interfaces, or component interactions leaves a concrete risk uncovered by the existing review and checks. State that risk and the follow-up scope before requesting it. A second full review of the same scope is exceptional and appropriate when substantial rework invalidates the first review. Resolved findings and passing required checks normally finish the review; do not seek repeated clean verdicts or leave a known defect unaddressed solely to satisfy a round count.

If reviewer capability is unavailable, perform a distinct self-review and disclose that independent review was unavailable. A self-review must not be described as independent.

## Final Documentation Accuracy Check

At the end of every code change, after implementation and review fixes and before handoff, explicitly check whether existing documentation needs updating:

1. Identify the existing documentation related to the changed behavior: interface contracts, inline implementation comments in touched code, READMEs, built-in help, guides, and examples. Inspect the relevant content even if no documentation file or comment line was edited during implementation. Check existing comments against the current logic, assumptions, and rationale alongside the rest of the documentation.
2. Identify each document's core point, audience, and level of detail. For each proposed accuracy update, identify the existing claim, instruction, or example the code change makes inaccurate. If there is none, leave that passage unchanged unless the user requested a documentation addition. A code change does not by itself require a documentation edit.
3. Correct or remove stale information in the owning passage and update existing examples or help only as needed to preserve accuracy and purpose. Leave accurate and sufficient documentation unchanged. Apart from the selective implementation comments described above, do not add new topics, sections, examples, guides, or descriptions of previously undocumented behavior; the user decides what new documentation to add. If related documentation does not exist, this check does not authorize creating it.
4. Review the documentation diff for new facts inserted alongside valid corrections, including facts taken from implementation requirements. Remove unrequested additions while preserving the necessary corrections and the separately allowed implementation comments. Verify accuracy updates with the applicable documentation checks above. Keep them within the task's review cadence; do not add a documentation-only review round. Repeat the affected accuracy check if later code changes invalidate its result.

Briefly state in the handoff whether existing documentation was updated or no update was needed, with any material limitation. If new documentation is needed to satisfy a project requirement, report the unmet requirement for the user's decision rather than expanding scope.

## Roadblocks and Handoff

Handle routine local obstacles autonomously. If completion requires changing agreed behavior or scope, finish useful independent work and report the roadblock at the end. Clearly mark the task incomplete, identify what remains, and explain the decision or capability needed. Do not start another design interview during implementation, silently narrow requirements, or expose unfinished behavior as complete.

Follow [the handoff guidance](references/handoff.md) after fixes and verification. Report concise outcomes, important behavioral commitments, and only useful human review targets. Installation, commits, publishing, and other external actions require authorization from the task; this workflow does not supply it.
