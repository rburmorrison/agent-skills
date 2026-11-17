---
name: code-authoring
description: Write or modify code, tests, interface documentation, READMEs, help, and user guides within the agreed scope. Apply readable code and documentation standards, verify behavior, and finish code changes by checking existing documentation for accuracy.
---

# Code Authoring

Use for new code, features, fixes, refactors, and source or usage documentation edits. For planning or review tasks, apply the relevant standards without executing the authoring workflow.

Use the agreed plan and decisions from the conversation. If consequential behavior or scope remains unresolved, complete planning with the user one question at a time before editing; use `plan-changes` if available. A small unambiguous task needs only proportionate planning.

## Documentation

Source comments and API doc comments/docstrings are allowed for affected code. Edit usage documentation (READMEs, guides, standalone reference material, built-in help, and user examples) only at the plan's documentation-map entries; for anything else, ask under Roadblocks and Handoff. Read [the documentation reference](references/documentation.md) before editing any documentation or doc comments, and again for the final accuracy check.

## Execute Within Scope

Choose only routine local implementation details within the plan's remaining discretion, preserving agreed behavior, public contracts, architectural boundaries, and scope. Do not invent missing validation rules, error policies, compatibility decisions, or architecture and call them implementation details. Follow the plan's contracts and rationale; when a consequential gap or conflict appears, use the immediate-question policy below. Necessary supporting changes must serve the requested outcome. Keep optional cleanup, new features, dependency upgrades, and reorganizations outside the change unless planned.

Build toward a functional, declarative core with effects at explicit edges. Concentrate filesystem, network, database, clock, randomness, and environment access in coordinating operations, and pass ordinary values into pure transformations and decisions while preserving transaction and snapshot boundaries. Prefer immutable domain values and operations that return new values over mutating inputs or shared state; when a decision determines writes or commands, return it as a value and apply it separately. State what a result is rather than how to build it where that reads more clearly: mapping, filtering, and grouping expressions over accumulator loops, a dependency's declarative APIs over hand-written procedures, and declarative domain rules as described below. Local mutation inside one function, ordered I/O, and framework APIs built around mutable state remain direct when clearer. Follow the plan's pure and effectful contracts; moving a decision into an effectful operation is a consequential change. Use the project's existing mechanisms; introduce abstractions only for a concrete responsibility or dependency, and avoid functional machinery such as effect wrappers that makes the code harder to read.

Before implementing behavior an existing dependency may provide, inspect its supported-version documentation or implementation. Prefer its built-in behavior and configuration over custom parsing, help generation, layout arithmetic, or equivalent machinery. Keep custom code for a demonstrated application requirement or contract gap, and explain that gap near the adapter. A wrapper must add a cohesive responsibility, not merely rename or reproduce dependency behavior. Do not add a dependency merely to avoid a small cohesive operation. If reuse would change an agreed contract, resolve that choice before switching; missing evidence is not proof that replacement is necessary.

Manage dependencies through the project's package manager. Use actual package information and supported-version constraints; do not guess versions or hand-edit dependency entries as a shortcut. Respect existing workspace dependencies and lockfile policy. If the needed tool is unavailable, apply the blocker policy instead of silently bypassing it.

## Shape Readable Code

- Name domain concepts, responsibilities, and operations using the problem's vocabulary.
- Prefer named records, fields, and explicit variants for domain values crossing boundaries. Local, immediately unpacked tuples remain useful. Add runtime validation at external boundaries when required; do not add a validation dependency merely to name internal fields.
- Group statements that perform one conceptual step. Separate changes of purpose with whitespace. Within a stage, also separate setup from traversal, and completed loops or early-return guards from subsequent result construction or a final return. These smaller breaks need no extra comment. Compact match arms generally form one unit and need no extra blank lines.
- Extract coherent operations with meaningful names. Keep a simple sequence together when splitting it would add navigation without improving comprehension.
- Organize modules by responsibility and reasons to change. Keep types near the code that owns their meaning. Treat size and complexity as inspection signals rather than incentives to create trivial files or helpers.
- Use idioms supported by the declared language version. Pattern matching suits meaningful variants and structured alternatives; ordinary predicates can remain conditionals.
- Keep affected interface documentation and source comments accurate using [the documentation reference](references/documentation.md).

Read [the code examples](references/code-examples.md) for non-trivial implementation or when resolving a style tradeoff. Their languages illustrate shared principles rather than restricting the skill's scope.

### Prefer Declarative Domain Rules

Prefer expressing a coherent family of domain rules as meaningful declarations interpreted by a small shared mechanism when that makes the rules easier to read than procedural branching. Put related selectors, metadata, and policy together so a reader can understand what defines each case in one place. Consider this with only two cases; readability is sufficient reason, without waiting for extensive duplication.

Keep the mechanism general across those declarations instead of teaching selection, execution, and related state separate versions of each case. Prefer supported declarative dependency APIs where available. Pure functions, encapsulated mutation, or renamed helpers alone do not satisfy this preference if the domain policy remains scattered through branches.

Keep ordinary one-off conditionals, exhaustive mappings, local mutation, and ordered I/O direct when clearer. Use the smallest representation with a concrete readability benefit; do not build a generic framework or configuration language. See [the domain-rule example](references/code-examples.md#declarative-domain-rules) for the distinction.

### Explain Steps and Decisions

For every function with more than one logical step, introduce each meaningful stage with a brief, imperative implementation comment and separate stages with blank lines. The comment names the stage and, unless the code already makes it plain, why the stage exists or must happen where it does. Sketch these stage comments before filling in the implementation, and revise them when the flow changes. Apply this to short functions too, and to distinct stages within loops or branches. A logical step is a coherent purpose, not an individual statement: collecting values and then organizing them are separate stages; sorting and deduplicating those values can form one stage. Routine buffer initialization and a final return do not automatically need their own comments.

A broad comment naming several distinct stages does not replace comments at their transitions. Selecting whether work is allowed and performing that work are separate stages, as are writing a heading and rendering its entries. Place each comment where its stage begins.

Write every stage comment as exactly one line, within the file's line-length limit including indentation, or 80 characters when the project sets none. Put the reason in that line as a short clause (`so ...`, `because ...`, `before ...`). Check each stage comment against these rules:

- **Reason source.** A reason names something the stage's own code does not show: a property of the input, a later consumer, an ordering dependency, or a failure it prevents.
- **Grounding.** Write only a reason you can trace to the code, the plan or task, a test, or observed behavior. If you cannot say where it came from, it may be plausible but false; name the stage alone.
- **Rejected reasons.** Drop a reason that describes the code below it, repeats the stage name in other words, or claims tidiness or correctness. Keep the stage name alone; do not invent a replacement.
- **Deletion test.** Remove the reason clause. If a reader loses nothing, leave it removed.
- **Overlong lines.** Cut words before cutting facts. If two facts the code cannot show still do not fit, keep the one that explains why the stage exists and drop the other. Never continue a stage comment onto a second line.
- **Routine setup.** Initialization, unpacking, and returns that need no comment do not gain one to carry a reason.

These rules can remove a reason, never a stage comment. Every stage keeps its one-line comment and the blank line above it, with or without a reason.

Use step comments to make the process scannable even when individual statements are clear. Explain consequential decisions, ordering requirements, assumptions, and constraints near the relevant code, including why a check or exception is necessary. A single-step function usually needs no comment unless its rationale is otherwise unclear; a straightforward predicate or mapping remains one step regardless of its line count. Keep clear names and cohesive code, and avoid narrating every assignment or match arm. Do not fragment a coherent function merely to avoid step comments.

- Use standalone single-line comments in the language's ordinary comment syntax, such as `#` or `//`. Do not use multiline or block-comment syntax for implementation comments.
- Stage comments are always one line. Only a rationale comment on a specific decision, whose one constraint cannot be stated in a line, may use consecutive single-line comments as one group, without blank lines between them. This should be rare.
- Put a blank line above each comment group unless it is the first content at the top of its enclosing code block. Keep the comment adjacent to the code it explains.
- Keep API documentation syntax separate: native docstrings and documentation comments follow [the documentation reference](references/documentation.md), not these implementation-comment formatting rules.

When correcting or shortening existing comments, preserve useful rationale. Include unchanged comments in the final documentation accuracy check.

See [the implementation comment examples](references/code-examples.md#implementation-comments) for short multistep functions, nested stages, single-step exceptions, and decision rationale.

After formatting and before independent review or handoff, perform a separate readability pass on the finished source, including changed tests:

1. Read each affected function and its nested blocks in execution order. Identify where the purpose changes, then check that a local stage comment marks each transition; reading only the existing comments can conceal an omitted stage.
2. For each stage comment, confirm it is one line within the length limit, then apply the reason-source, grounding, and deletion tests above. For each reason, name where it came from; if you cannot, remove the reason and keep the stage name. Also confirm that no stage with a non-obvious constraint lacks a reason.
3. Check each comment group's preceding line and its attachment to the stage it describes. Check the smaller whitespace breaks around setup, traversal, guards, and results even where no new comment is needed.
4. In tests, trace setup, action, assertions, and each new scenario. Correct broad or misplaced comments and missing paragraphs before reporting the work ready. Passing formatters and tests does not complete this pass.

## Verify Behavior

Read [the testing guidance](references/testing.md) when adding or changing tests. Cover meaningful agreed behavior and failure cases with readable setup, actions, and assertions. Test count is not a target.

Run applicable project formatting, linting, type, and behavior checks. Record what ran and any limitations. Do not claim that checks passed when they were unavailable or not executed.

Also exercise the changed behavior as a user would when feasible, using the actual application entry point rather than only test helpers. Follow the planned workflow: for a CLI, invoke the command with representative inputs and inspect output and persisted state; for a UI, run through the affected flow in the app or browser; for an API or library, use a realistic client or caller. Check a representative success and relevant failure, within authorized scope and using disposable data where possible. Automated user-workflow execution is acceptable; another isolated unit test is not a substitute. Do not perform unauthorized external mutations for verification.

If the workflow cannot run because tools, credentials, services, or an executable application are unavailable, use the closest feasible check and state precisely what remains unverified. Do not treat passing tests as evidence that an unexecuted user workflow works. Record the workflow attempted, observed results, and limitations for review and handoff.

Lint and type-check suppressions must be rare, narrowly scoped, and accompanied by a specific reason. Prefer fixing the underlying problem. Use native justification syntax when available, otherwise a nearby explanation. Explain configuration-level exceptions beside the setting; do not weaken checks simply to obtain a pass.

## Independent Review

For non-trivial changes, the default review is one quick, pointed review of the completed change by a fresh-context subagent running on the implementing model, without an upgrade; a separate review with a more capable model is the developer's choice. Honor an explicit task or invoked workflow's review cadence instead; do not append the default review to that workflow. Disable conversation-history inheritance when starting a reviewer: for tools exposing `fork_turns`, use `"none"`. Supply a self-contained review brief instead. Behavioral changes involving interacting components, public contracts, persistence, or significant refactoring normally qualify. Pure formatting and typo corrections usually do not.

Give the reviewer the agreed plan and decisions, actual final diff including new files, relevant code, and verification results. Use `review-changes` if available. Do not supply the implementer's self-assessment or a desired verdict. Use the task's chosen reviewer model; if none was chosen, use the environment's normal inheritance rather than guessing model IDs or upgrading silently.

Assess findings against the code. Fix validated Blocker and Should-fix findings within scope and rerun affected checks. Fix a validated Nit only when the fix touches only lines this change already modifies, changes no behavior or test expectations, and needs no new file, dependency, or user decision. Applying a Nit that fails any condition is out of scope, however small or worthwhile it seems; raise any other Nit you recommend making as a decision in the handoff, and drop the rest. Nits never block completion. Request a targeted follow-up autonomously only when a material change to logic, interfaces, or component interactions leaves a concrete risk uncovered by the existing review and checks. State that risk and the follow-up scope before requesting it. A second full review of the same scope is exceptional and appropriate when substantial rework invalidates the first review. Resolved findings and passing required checks normally finish the review; do not seek repeated clean verdicts or leave a known defect unaddressed solely to satisfy a round count.

If reviewer capability is unavailable, perform a distinct self-review and disclose that independent review was unavailable. A self-review must not be described as independent.

## Roadblocks and Handoff

Handle routine local obstacles autonomously. When a missing consequential decision, changed requirement, or unplanned usage-documentation edit is discovered, explain the concrete issue, options, and recommendation and ask the user immediately, one question at a time. Pause dependent work and continue useful independent work. Do not reopen settled decisions without new evidence, silently narrow requirements, or wait until handoff to reveal the choice. Record the answer and reason in the plan before resuming dependent work. If an answer or capability remains unavailable, clearly mark the affected work incomplete and report what is needed.

Installation, commits, publishing, and other external actions require authorization from the task; this workflow does not supply it.

## Handoff

After fixes and verification, write the handoff in this format, even when the work stops on an open question:

- **Summary:** a short paragraph with no heading, label, or bullets. Open with a bold sentence stating what changed, such as `**Imports now skip blank lines instead of failing.**`, not a `**Summary:**` label, then say why and name any gap that affects confidence. It may mention the review.
- **`## Invariants`** and **`## Failure Modes and Recovery`:** one `###` subheading per guarantee or failure, each opening with a bold sentence and supported by a short source excerpt and verified link where available.
- **`## Verification and Remaining Uncertainty`:** if everything passed, one sentence naming what ran and whether planned documentation was updated. Detail only failed or skipped checks, unexercised behavior, and blocked work. No tables or lists of tests.
- **`## Decisions Awaiting You`:** only when decisions remain. Number each item: a bold title naming the choice, the current state and what each option would change, then a recommendation and why. If you recommend keeping things as they are, leave the item out; for example, drop "I recommend leaving the duplicate parser as it is." Plan deviations and unresolved findings go here, described as choices about the code, never by review labels such as Nit or Should-fix.

Use no other sections, and put `---` before each section heading. Read [the handoff guidance](references/handoff.md) for coverage, evidence, links, and examples.

## Before Handoff

1. The change stays within the agreed scope and remaining discretion; every consequential gap was asked about, not decided (Execute Within Scope, Roadblocks and Handoff).
2. Formatting, lint, type, and behavior checks ran; results are recorded accurately, including anything not run (Verify Behavior).
3. The changed behavior was exercised through the actual entry point, or the limitation is stated (Verify Behavior).
4. The readability pass is done: each multistep function and test has a one-line stage comment at every transition that gives the reason where the code does not, with blank lines between stages (Explain Steps and Decisions).
5. Usage-documentation edits match the documentation map exactly; related documentation was inspected and any unplanned need was asked about ([documentation reference](references/documentation.md)).
6. For non-trivial changes, the independent review ran; validated Blocker and Should-fix findings are fixed and affected checks rerun. Each applied Nit touches only lines this change already modifies and changes no behavior or tests; revert any that does not (Independent Review).
7. The handoff follows the Handoff format: a bold-led summary paragraph, then only its sections, with a recommendation and why for each decision (Handoff).
