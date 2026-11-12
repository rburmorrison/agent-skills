---
name: code-authoring
description: Write or modify code, tests, interface documentation, READMEs, help, and user guides within the agreed scope. Apply readable code and documentation standards, verify behavior, and finish code changes by checking existing documentation for accuracy.
---

# Code Authoring

Use for new code, features, fixes, refactors, and source or usage documentation edits. For planning or review tasks, apply the relevant standards without executing the authoring workflow.

Use the agreed plan and decisions from the conversation. If consequential behavior or scope remains unresolved, complete planning with the user one question at a time before editing; use `plan-changes` if available. A small unambiguous task needs only proportionate planning.

## Documentation Scope

Code changes allow useful inline implementation comments and source API doc comments/docstrings for affected code without listing each in the plan. Usage documentation—READMEs, guides, standalone reference material, built-in help, and user examples—requires a bounded documentation map: exact location, existing inaccurate claim and correction or explicitly requested addition, and verification. Correct claims at their existing level of detail; leave accurate content unchanged. An omitted map permits no usage-documentation edits. A direct, explicit documentation request supplies scope and may use a brief plan.

New documents, sections, examples, or previously undocumented facts require an explicit user request or confirmation recorded in the plan, even inside an existing passage. Do not infer permission from code requirements, general plan approval, or your judgment that an addition would help. An accuracy inspection, reviewer finding, or documentation lint does not expand scope. For an unplanned edit, leave the material unchanged and use the immediate-question procedure under Roadblocks and Handoff.

## Execute Within Scope

Choose only routine local implementation details within the plan's remaining discretion, preserving agreed behavior, public contracts, architectural boundaries, and scope. Do not invent missing validation rules, error policies, compatibility decisions, or architecture and call them implementation details. Follow the plan's contracts and rationale; when a consequential gap or conflict appears, use the immediate-question policy below. Necessary supporting changes must serve the requested outcome. Keep optional cleanup, new features, dependency upgrades, and reorganizations outside the change unless planned.

Concentrate filesystem, network, database, clock, and environment access at explicit boundaries where applicable. Separate substantial domain calculations from orchestration, passing ordinary values into core transformations and decisions while preserving transaction and snapshot boundaries. Use the project's existing mechanisms; introduce abstractions only for a concrete responsibility or dependency.

Before implementing behavior an existing dependency may provide, inspect its supported-version documentation or implementation. Prefer its built-in behavior and configuration over custom parsing, help generation, layout arithmetic, or equivalent machinery. Keep custom code for a demonstrated application requirement or contract gap, and explain that gap near the adapter. A wrapper must add a cohesive responsibility, not merely rename or reproduce dependency behavior. If reuse would change an agreed contract, resolve that choice before switching; missing evidence is not proof that replacement is necessary.

Manage dependencies through the project's package manager. Use actual package information and supported-version constraints; do not guess versions or hand-edit dependency entries as a shortcut. Respect existing workspace dependencies and lockfile policy. If the needed tool is unavailable, apply the blocker policy instead of silently bypassing it.

## Shape Readable Code

- Name domain concepts, responsibilities, and operations using the problem's vocabulary.
- Prefer named records, fields, and explicit variants for domain values crossing boundaries. Local, immediately unpacked tuples remain useful. Add runtime validation at external boundaries when required; do not add a validation dependency merely to name internal fields.
- Group statements that perform one conceptual step. Separate changes of purpose with whitespace. Within a stage, also separate setup from traversal, and completed loops or early-return guards from subsequent result construction or a final return. These smaller breaks need no extra comment. Compact match arms generally form one unit and need no extra blank lines.
- Extract coherent operations with meaningful names. Keep a simple sequence together when splitting it would add navigation without improving comprehension.
- Organize modules by responsibility and reasons to change. Keep types near the code that owns their meaning. Treat size and complexity as inspection signals rather than incentives to create trivial files or helpers.
- Use idioms supported by the declared language version. Pattern matching suits meaningful variants and structured alternatives; ordinary predicates can remain conditionals.
- Keep affected interface documentation and source comments accurate using the documentation standards below.

Read [the code examples](references/code-examples.md) for non-trivial implementation or when resolving a style tradeoff. Their languages illustrate shared principles rather than restricting the skill's scope.

### Prefer Declarative Domain Rules

Prefer expressing a coherent family of domain rules as meaningful declarations interpreted by a small shared mechanism when that makes the rules easier to read than procedural branching. Put related selectors, metadata, and policy together so a reader can understand what defines each case in one place. Consider this with only two cases; readability is sufficient reason, without waiting for extensive duplication.

Keep the mechanism general across those declarations instead of teaching selection, execution, and related state separate versions of each case. Prefer supported declarative dependency APIs where available. Pure functions, encapsulated mutation, or renamed helpers alone do not satisfy this preference if the domain policy remains scattered through branches.

Keep ordinary one-off conditionals, exhaustive mappings, local mutation, and ordered I/O direct when clearer. Use the smallest representation with a concrete readability benefit; do not build a generic framework or configuration language. See [the domain-rule example](references/code-examples.md#declarative-domain-rules) for the distinction.

### Explain Steps and Decisions

For every function with more than one logical step, introduce each meaningful stage with a short, imperative implementation comment and separate stages with blank lines. Sketch these stage comments before filling in the implementation, and revise them when the flow changes. Apply this to short functions too, and to distinct stages within loops or branches. A logical step is a coherent purpose, not an individual statement: collecting values and then organizing them are separate stages; sorting and deduplicating those values can form one stage. Routine buffer initialization and a final return do not automatically need their own comments.

A broad comment naming several distinct stages does not replace comments at their transitions. Selecting whether work is allowed and performing that work are separate stages, as are writing a heading and rendering its entries. Place each comment where its stage begins.

Use step comments to make the process scannable even when individual statements are clear. Explain consequential decisions, ordering requirements, assumptions, and constraints near the relevant code, including why a check or exception is necessary. A single-step function usually needs no comment unless its rationale is otherwise unclear; a straightforward predicate or mapping remains one step regardless of its line count. Keep clear names and cohesive code, and avoid narrating every assignment or match arm. Do not fragment a coherent function merely to avoid step comments.

- Use standalone single-line comments in the language's ordinary comment syntax, such as `#` or `//`. Do not use multiline or block-comment syntax for implementation comments.
- For longer explanations, use consecutive single-line comments as one group, without blank lines between them.
- Put a blank line above each comment group unless it is the first content at the top of its enclosing code block. Keep the comment adjacent to the code it explains.
- Keep API documentation syntax separate: native docstrings and documentation comments follow the interface documentation standards below, not these implementation-comment formatting rules.

When correcting or shortening existing comments, preserve useful rationale. Include unchanged comments in the final documentation accuracy check.

See [the implementation comment examples](references/code-examples.md#implementation-comments) for short multistep functions, nested stages, single-step exceptions, and decision rationale.

After formatting and before independent review or handoff, perform a separate readability pass on the finished source, including changed tests:

1. Read each affected function and its nested blocks in execution order. Identify where the purpose changes, then check that a local stage comment marks each transition; reading only the existing comments can conceal an omitted stage.
2. Check each comment group's preceding line and its attachment to the stage it describes. Check the smaller whitespace breaks around setup, traversal, guards, and results even where no new comment is needed.
3. In tests, trace setup, action, assertions, and each new scenario. Correct broad or misplaced comments and missing paragraphs before reporting the work ready. Passing formatters and tests does not complete this pass.

## Document Interfaces and Decisions

Apply these standards to source API doc comments/docstrings and authorized standalone interface documentation. Inspect the affected code, callers, existing documentation, and tooling before promising a contract.

Interfaces intended for other components, including within the project, are the boundary for caller-facing contracts. Include types and relevant members, not just functions. Visibility keywords, underscores, and module names are evidence of intent rather than the sole definition of that boundary. Truly internal implementation details usually need no documentation comment.

- Use a concise brief and complete applicable contract sections in the project's native documentation format. Omit inapplicable sections and boilerplate; do not restate type annotations without explaining meaning.
- Keep free-form bodies exceptional: use a short body only for a caller-facing concept or interaction that must be understood together and cannot be explained clearly in the brief, members, or contract sections. Importance or non-obviousness alone does not justify a body.
- Assign facts to their owning interfaces. Put input and result semantics in the brief or applicable contract sections, failures in the error section, and member facts on members. Remove duplication rather than moving it under Notes or Details or overloading the brief.
- Keep type documentation self-contained: describe intrinsic meaning, members, enforced invariants, and obligations for correct use. Avoid narrating external parsers, factories, or consumers. Put an operation's behavior and guarantees on that operation; public construction or mutation may bypass validation, so do not promise that every instance is validated when only one operation guarantees it.
- Check callers and propagated failures before describing errors. Preserve caller-relevant obligations; omit speculative failures and implementation walkthroughs. Use examples when requested and when they materially clarify correct use.
- Use Title Case for authored headings while preserving required documentation tags, identifiers, and syntax.

Read [Python documentation](references/documentation-python.md) or [Rust documentation](references/documentation-rust.md) when editing documentation in those languages. Use native formats and existing tooling for other languages.

Private doc comments are useful only for otherwise unclear contracts or constraints. Documentation-only work does not authorize restructuring code or changing behavior to fit a comment.

Follow project documentation lints, including for otherwise internal items, within Documentation Scope. Do not weaken checks, change visibility, or rename items to evade them.

## Write Usage Documentation Within Scope

Before editing a README, built-in help, or user guide, identify its audience, core purpose, and the task it helps the reader complete. Inspect the relevant entry points, supported installation method, examples, and actual help. Preserve prerequisites, consequential limitations, compatibility information, and applicable project conventions.

Match each edit to the agreed documentation map before writing.

Keep a README focused on its purpose, necessary setup, and a representative path to a useful result. Revise the owning passage with concise, direct prose and Title Case for authored headings. Avoid redundant feature inventories, implementation narration, and change-history details. Do not impose a fixed section template.

Keep existing examples runnable from their stated starting conditions, with required inputs and enough observable output to recognize success. Capture help from the actual documented command and version, identify the command, and preserve the captured text verbatim. Do not reconstruct help, silently edit it, apply Title Case inside it, or present a shortened block as complete. Use an identified subcommand's help or a link when full help would overwhelm the document.

Use existing help and references for discovery. For authorized additions, put substantial workflows or concepts in separate documents only when readers need them, link from the relevant starting point, and avoid duplicating help or API reference material. Reuse existing documentation-generation mechanisms; do not introduce tooling merely to refresh a small output block.

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

1. Discover existing documentation related to the changed behavior in the repository; the plan's file list and edit map are not an exhaustive inspection list. Include interface contracts, inline implementation comments in touched code, READMEs, built-in help, guides, and examples. Inspect relevant content even if its file or comment lines were unchanged. Check existing comments against the current logic, assumptions, and rationale.
2. Identify each document's core point, audience, and level of detail. Match needed corrections to Documentation Scope and the plan's map; ask immediately about unplanned usage-documentation needs. Correct or remove stale source comments within affected code.
3. Audit the usage-documentation diff for unplanned edits and new facts inserted alongside valid corrections, including facts taken from implementation requirements. Remove unauthorized additions while preserving planned corrections. Verify permitted edits with the applicable documentation checks above, within the task's review cadence; do not add a documentation-only review round. Repeat the affected accuracy check if later code changes invalidate its result.

Briefly state in the handoff whether planned documentation was updated, no update was needed, or an unplanned need remains awaiting a decision. Report unmet project requirements without expanding scope.

## Roadblocks and Handoff

Handle routine local obstacles autonomously. When a missing consequential decision, changed requirement, or unplanned usage-documentation edit is discovered, explain the concrete issue, options, and recommendation and ask the user immediately, one question at a time. Pause dependent work and continue useful independent work. Do not reopen settled decisions without new evidence, silently narrow requirements, or wait until handoff to reveal the choice. Record the answer and reason in the plan before resuming dependent work. If an answer or capability remains unavailable, clearly mark the affected work incomplete and report what is needed.

Follow [the handoff guidance](references/handoff.md) after fixes and verification. Use simple wording and bold first sentences under Invariants, Failure Modes and Recovery, and Verification and Remaining Uncertainty. Separate major sections with horizontal rules and give each invariant and failure mode a short subheading. Prefer a verification table when several behaviors map clearly to evidence and results or gaps; otherwise use prose. Cover every consequential guarantee and failure mode without an item cap; include short fenced evidence wherever available source directly supports an important claim, followed by verified source links. Links alone do not replace applicable evidence blocks. Distinguish intended behavior from observed results and remaining uncertainty. Installation, commits, publishing, and other external actions require authorization from the task; this workflow does not supply it.
