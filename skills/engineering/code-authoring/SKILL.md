---
name: code-authoring
description: Write or modify code, tests, interface documentation, READMEs, help, and user guides within the agreed scope. Apply readable code and documentation standards, verify behavior, and finish code changes by checking existing documentation for accuracy.
---

# Code Authoring

Use for new code, features, fixes, refactors, and source or usage documentation edits. For planning or review tasks, apply the relevant standards without executing the authoring workflow. Code changes allow useful inline implementation comments and source API doc comments/docstrings for affected code. READMEs, guides, standalone reference material, built-in help, and user examples follow the stricter planned-edit boundary below.

Edit usage documentation only where the agreed plan names the location and specific accuracy correction or user-requested addition. An omitted documentation map is not permission to choose edits; if no usage-documentation edits are planned, leave it untouched. A direct, explicit documentation request supplies scope and may use a brief plan. Adding a previously undocumented fact to an existing passage is still an addition, even if accurate, relevant, or mentioned in the code requirements. New documentation or facts require an explicit user request or confirmation recorded in the plan. Do not infer that permission from a code request, general plan approval, or your judgment that more documentation would help.

Use the agreed plan and decisions from the conversation. If consequential behavior or scope remains unresolved, complete planning with the user one question at a time before editing; use `plan-changes` if available. A small unambiguous task needs only proportionate planning.

## Execute Within Scope

Choose only routine local implementation details within the plan's remaining discretion, preserving agreed behavior, public contracts, architectural boundaries, and scope. Do not invent missing validation rules, error policies, compatibility decisions, or architecture and call them implementation details. Follow the plan's contracts and rationale; when a consequential gap or conflict appears, use the immediate-question policy below. Necessary supporting changes must serve the requested outcome. Keep optional cleanup, new features, dependency upgrades, and reorganizations outside the change unless planned.

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

Apply these standards to source API doc comments/docstrings for affected code and to standalone interface documentation within the planned documentation scope. Useful source contracts may be added or updated as part of implementation; do not use this allowance to expand READMEs, guides, or other standalone material. Inspect the affected code, callers, existing documentation, and tooling before promising a contract.

Interfaces intended for other components, including within the project, are the boundary for caller-facing contracts. Include types and relevant members, not just functions. Visibility keywords, underscores, and module names are evidence of intent rather than the sole definition of that boundary. Truly internal implementation details usually need no documentation comment.

- Within the authorized documentation scope, use a concise brief and complete applicable contract sections in the project's native documentation format. For usage documentation, these standards do not authorize adding previously undocumented facts. Omit inapplicable sections and boilerplate; do not restate type annotations without explaining meaning.
- Keep free-form bodies exceptional: use a short body only for a caller-facing concept or interaction that must be understood together and cannot be explained clearly in the brief, members, or contract sections. Importance or non-obviousness alone does not justify a body.
- Assign facts to their owning interfaces. Put input and result semantics in the brief or applicable contract sections, failures in the error section, and member facts on members. Remove duplication rather than moving it under Notes or Details or overloading the brief.
- Keep type documentation self-contained: describe intrinsic meaning, members, enforced invariants, and obligations for correct use. Avoid narrating external parsers, factories, or consumers. Put an operation's behavior and guarantees on that operation; public construction or mutation may bypass validation, so do not promise that every instance is validated when only one operation guarantees it.
- Check callers and propagated failures before describing errors. Preserve caller-relevant obligations; omit speculative failures and implementation walkthroughs. Use examples when requested and when they materially clarify correct use.
- Use Title Case for authored headings while preserving required documentation tags, identifiers, and syntax.

Read [Python documentation](references/documentation-python.md) or [Rust documentation](references/documentation-rust.md) when editing documentation in those languages. Use native formats and existing tooling for other languages.

Private doc comments are useful only for otherwise unclear contracts or constraints. Documentation-only work does not authorize restructuring code or changing behavior to fit a comment.

Follow project documentation lints, including for otherwise internal items. Source doc comments required for affected code are within the allowance above. Do not weaken checks, change visibility, or rename items to evade them. If a check requires usage-documentation additions beyond the agreed scope, ask for the required plan amendment rather than silently adding documentation or suppressing the check.

## Write Usage Documentation Within Scope

Before editing a README, built-in help, or user guide, identify its audience, core purpose, and the task it helps the reader complete. Inspect the relevant entry points, supported installation method, examples, and actual help. Preserve prerequisites, consequential limitations, compatibility information, and applicable project conventions.

Match each edit to the plan's documentation map: exact location, existing inaccurate claim and correction, or explicitly requested addition, plus verification. Correct only that claim at the existing level of detail. If the needed edit is absent from the map, leave the document unchanged and ask the user to confirm an amendment. A final accuracy check or reviewer finding does not bypass this boundary.

Keep a README focused on its purpose, necessary setup, and a representative path to a useful result. Revise the owning passage at its existing level of detail. Keep prose concise and direct, with Title Case for authored headings. Preserve accurate content; avoid redundant feature inventories, implementation narration, and change-history details. Do not impose a fixed section template.

Keep existing examples runnable from their stated starting conditions, with required inputs and enough observable output to recognize success. Capture help from the actual documented command and version, identify the command, and preserve the captured text verbatim. Do not reconstruct help, silently edit it, apply Title Case inside it, or present a shortened block as complete. Use an identified subcommand's help or a link when full help would overwhelm the document.

Use existing help and references for discovery. New sections, examples, guides, or expanded explanations require the user's request. When additions are requested, put substantial workflows or concepts in separate documents only when readers need them, link from the relevant starting point, and avoid duplicating help or API reference material. Reuse existing documentation-generation mechanisms; do not introduce tooling merely to refresh a small output block.

## Verify Behavior

Read [the testing guidance](references/testing.md) when adding or changing tests. Cover meaningful agreed behavior and failure cases with readable setup, actions, and assertions. Test count is not a target.

Run applicable project formatting, linting, type, and behavior checks. Record what ran and any limitations. Do not claim that checks passed when they were unavailable or not executed.

Also exercise the changed behavior as a user would when feasible, using the actual application entry point rather than only test helpers. Follow the planned workflow: for a CLI, invoke the command with representative inputs and inspect output and persisted state; for a UI, run through the affected flow in the app or browser; for an API or library, use a realistic client or caller. Check a representative success and relevant failure, within authorized scope and using disposable data where possible. Automated user-workflow execution is acceptable; another isolated unit test is not a substitute. Do not perform unauthorized external mutations for verification.

If the workflow cannot run because tools, credentials, services, or an executable application are unavailable, use the closest feasible check and state precisely what remains unverified. Do not treat passing tests as evidence that an unexecuted user workflow works. Record the workflow attempted, observed results, and limitations for review and handoff.

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
2. Identify each document's core point, audience, and level of detail. For usage documentation, identify the existing claim, instruction, or example made inaccurate and match any correction to the plan's documentation map. If an unplanned correction or addition is needed, leave it unchanged and immediately ask for a plan amendment; continue independent work while awaiting the answer. Inspection itself does not authorize an edit.
3. Correct source comments and doc comments within the affected code as needed. For usage documentation, apply only planned accuracy corrections and explicitly requested additions. Leave accurate content unchanged. If related documentation does not exist, this check does not authorize creating it.
4. Review the usage-documentation diff for unplanned edits and new facts inserted alongside valid corrections, including facts taken from implementation requirements. Remove unauthorized additions while preserving planned corrections and the separate source-comment allowance. Verify permitted edits with the applicable documentation checks above. Keep them within the task's review cadence; do not add a documentation-only review round. Repeat the affected accuracy check if later code changes invalidate its result.

Briefly state in the handoff whether planned documentation was updated, no update was needed, or an unplanned need remains awaiting a decision. Report unmet project requirements without expanding scope.

## Roadblocks and Handoff

Handle routine local obstacles autonomously. When a missing consequential decision, changed requirement, or unplanned usage-documentation edit is discovered, explain the concrete issue, options, and recommendation and ask the user immediately, one question at a time. Pause dependent work and continue useful independent work. Do not reopen settled decisions without new evidence, silently narrow requirements, or wait until handoff to reveal the choice. Record the answer and reason in the plan before resuming dependent work. If an answer or capability remains unavailable, clearly mark the affected work incomplete and report what is needed.

Follow [the handoff guidance](references/handoff.md) after fixes and verification. Report concise outcomes, important behavioral commitments, and only useful human review targets. Installation, commits, publishing, and other external actions require authorization from the task; this workflow does not supply it.
