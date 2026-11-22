---
name: code-authoring
description: Write or modify source code, tests, interface documentation, READMEs, help, and user guides within the agreed scope. Apply readable code and documentation standards, verify behavior, and finish code changes by checking existing documentation for accuracy. Not for configuration, manifest, or data files. For non-trivial changes without an agreed plan, use plan-changes first.
---

# Code Authoring

Use for new code, features, fixes, refactors, and source or usage documentation edits. For planning or review tasks, apply the relevant standards without executing the authoring workflow.

Do not use this skill for configuration, manifest, lockfile, or data files, such as `Cargo.toml`, `clippy.toml`, `package.json`, or CI workflows. A task that edits only those files does not load it. When a code change also touches them, edit them directly in the file's own conventions: the code-shaping, comment, review, and handoff standards here do not apply to them. Only Dependency Management and the suppression rule under Verify Behavior govern those files.

Use the agreed plan and decisions: the `.plans/` file named in the conversation or task when one exists, otherwise the plan held by the harness or the conversation. If consequential behavior or scope remains unresolved, complete planning with the user one question at a time before editing; use `plan-changes` if available. A small unambiguous task needs only proportionate planning.

## Documentation

Source comments and API doc comments/docstrings are allowed for affected code. Edit usage documentation (READMEs, guides, standalone reference material, built-in help, and user examples) only at the plan's documentation-map entries; for anything else, ask under Roadblocks and Handoff. Read [the documentation reference](references/documentation.md) before editing any documentation or doc comments, and again for the final accuracy check.

## Execute Within Scope

**Scope**

- Choose only routine local implementation details within the plan's remaining discretion, preserving agreed behavior, public contracts, architectural boundaries, and scope.
- Do not invent missing validation rules, error policies, compatibility decisions, or architecture and call them implementation details.
- Follow the plan's contracts and rationale. When a consequential gap or conflict appears, use the immediate-question policy under Roadblocks and Handoff.
- Necessary supporting changes must serve the requested outcome. Keep optional cleanup, new features, dependency upgrades, and reorganizations outside the change unless planned.

**Functional, declarative core**

- Build toward a functional, declarative core with effects at explicit edges.
- Concentrate filesystem, network, database, clock, randomness, and environment access in coordinating operations. Pass ordinary values into pure transformations and decisions while preserving transaction and snapshot boundaries.
- Prefer immutable domain values and operations that return new values over mutating inputs or shared state.
- When a decision determines writes or commands, return it as a value and apply it separately. See [decide, then apply](references/code-examples.md#decide-then-apply).
- State what a result is rather than how to build it where that reads more clearly: mapping, filtering, and grouping expressions over accumulator loops, a dependency's declarative APIs over hand-written procedures, and declarative domain rules as described below. See [expressions over accumulator loops](references/code-examples.md#expressions-over-accumulator-loops).
- Local mutation inside one function, ordered I/O, and framework APIs built around mutable state remain direct when clearer. Imperative code is also appropriate for performance needs that are measured or a stated hot path, where the plan names the path, the data size, and the cost avoided.
- Follow the plan's pure and effectful contracts; moving a decision into an effectful operation is a consequential change.
- When the codebase has an established style that differs, such as consistently object-oriented code built around mutable state, match that style unless the plan or the user says otherwise.
- Use the project's existing mechanisms. Introduce abstractions only for a concrete responsibility or dependency, and avoid functional machinery such as effect wrappers that makes the code harder to read.

**Existing dependencies**

- Before implementing behavior an existing dependency may provide, inspect its supported-version documentation or implementation.
- Prefer its built-in behavior and configuration over custom parsing, help generation, layout arithmetic, or equivalent machinery.
- Keep custom code for a demonstrated application requirement or contract gap, and explain that gap near the adapter.
- A wrapper must add a cohesive responsibility, not merely rename or reproduce dependency behavior.
- Do not add a dependency merely to avoid a small cohesive operation.
- If reuse would change an agreed contract, resolve that choice before switching; missing evidence is not proof that replacement is necessary.

**Dependency management**

- Manage dependencies through the project's package manager.
- Use actual package information and supported-version constraints; do not guess versions or hand-edit dependency entries as a shortcut.
- Respect existing workspace dependencies and lockfile policy.
- If the needed tool is unavailable, apply the blocker policy instead of silently bypassing it.

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

For every function with more than one logical step, introduce each meaningful stage with a one-line implementation comment and separate stages with blank lines. Write the comment as a natural sentence that explains what the stage does in plain words, as you would say it to a colleague, and, unless the code already makes it plain, why the stage exists or must happen where it does. Do not write a terse label or tag such as `Validation`, `Step 1:`, or `Load:`. Sketch these stage comments before filling in the implementation, and revise them when the flow changes. Apply this to short functions too, and to distinct stages within loops or branches. A logical step is a coherent purpose, not an individual statement: collecting values and then organizing them are separate stages; sorting and deduplicating those values can form one stage. Routine buffer initialization and a final return do not automatically need their own comments.

A broad comment naming several distinct stages does not replace comments at their transitions. Selecting whether work is allowed and performing that work are separate stages, as are writing a heading and rendering its entries. Place each comment where its stage begins.

Write every stage comment as exactly one line, within the file's line-length limit including indentation, or 80 characters when the project sets none. Put the reason in that line as a short clause (`so ...`, `because ...`, `before ...`). Check each stage comment against these rules:

- **Reason source.** A reason names something the stage's own code does not show: a property of the input, a later consumer, an ordering dependency, or a failure it prevents.
- **Grounding.** Write only a reason you can trace to the code, the plan or task, a test, or observed behavior. If you cannot say where it came from, it may be plausible but false; explain the step alone.
- **Rejected reasons.** Drop a reason that describes the code below it, repeats the step's explanation in other words, or claims tidiness or correctness. Keep the explanation of the step alone; do not invent a replacement.
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
2. For each stage comment, confirm it is one line within the length limit, then apply the reason-source, grounding, and deletion tests above. For each reason, name where it came from; if you cannot, remove the reason and keep the explanation of the step. Also confirm that no stage with a non-obvious constraint lacks a reason.
3. Check each comment group's preceding line and its attachment to the stage it describes. Check the smaller whitespace breaks around setup, traversal, guards, and results even where no new comment is needed.
4. In tests, trace setup, action, assertions, and each new scenario. Correct broad or misplaced comments and missing paragraphs before reporting the work ready. Passing formatters and tests does not complete this pass.

## Verify Behavior

Read [the testing guidance](references/testing.md) when adding or changing tests. Cover meaningful agreed behavior and failure cases with readable setup, actions, and assertions. Test count is not a target.

Run applicable project formatting, linting, type, and behavior checks. Record what ran and any limitations. Do not claim that checks passed when they were unavailable or not executed.

Also exercise the changed behavior as a user would when feasible, using the actual application entry point rather than only test helpers. Follow the planned workflow: for a CLI, invoke the command with representative inputs and inspect output and persisted state; for a UI, run through the affected flow in the app or browser; for an API or library, use a realistic client or caller. Check a representative success and relevant failure, within authorized scope and using disposable data where possible. Automated user-workflow execution is acceptable; another isolated unit test is not a substitute. Do not perform unauthorized external mutations for verification.

If the workflow cannot run because tools, credentials, services, or an executable application are unavailable, use the closest feasible check and state precisely what remains unverified. Do not treat passing tests as evidence that an unexecuted user workflow works. Record the workflow attempted, observed results, and limitations for review and handoff.

Lint and type-check suppressions must be rare, narrowly scoped, and accompanied by a specific reason. Prefer fixing the underlying problem. Use native justification syntax when available, otherwise a nearby explanation. Explain configuration-level exceptions beside the setting; do not weaken checks simply to obtain a pass.

## Independent Review

**When**

- A small change needs no independent review; the Before Handoff checklist is its check. A change is small when all of these hold:
  1. It is confined to one function or one cohesive block, or to comments, documentation, or configuration values.
  2. It changes no public contract, persisted data or format, or interaction between components.
  3. Where the change alters behavior, a check that actually ran, a test or an entry-point run, exercises it.
  4. No consequential question came up during the work.
- Every other change gets, by default, one quick, pointed review of the completed change by a fresh-context subagent running on the implementing model, without an upgrade. A separate review with a more capable model is the developer's choice.
- When the plan states the review expectation, follow it. If a change planned as small stops meeting a condition, review it.
- An explicit request for a review overrides the small-change rule. Honor an explicit task or invoked workflow's review cadence instead of this default; do not append the default review to that workflow.

**Starting the reviewer**

- Disable conversation-history inheritance: for tools exposing `fork_turns`, use `"none"`. Supply a self-contained review brief instead.
- Give the reviewer the agreed plan and decisions (the plan file's path when one exists), the actual final diff including new files, relevant code, and verification results. Use `review-changes` if available.
- Do not supply the implementer's self-assessment or a desired verdict.
- Use the task's chosen reviewer model. If none was chosen, use the environment's normal inheritance rather than guessing model IDs or upgrading silently.
- If reviewer capability is unavailable, perform a distinct self-review and disclose that independent review was unavailable. A self-review must not be described as independent.

**After the review**

- When findings return, read [handling review findings](references/review-findings.md) before changing anything. It owns which findings to fix, how Nits are limited, and when a follow-up review is warranted.

## Roadblocks and Handoff

Handle routine local obstacles autonomously. When a missing consequential decision, changed requirement, or unplanned usage-documentation edit is discovered, ask the user immediately, one question at a time. The question always goes to the user; do not try to consult another model. Write it so the user can answer without opening the code:

1. Open with one sentence beginning `You wanted` that restates the plan's goal sentence, then state the concrete issue in one sentence.
2. Show the current code or text: the file, the symbol or section, a short excerpt, and what it does.
3. Compare the options on one concrete input or scenario.
4. State what each option changes for the user and for the code.
5. End with your recommendation and its downside, labelled `Implementer's recommendation`.

When the plan is a `.plans/` file, add the question and the excerpt under its `## Open Questions` before asking, so the evidence is on record for whoever helps the user answer. Record the answer and reason in the plan's decision record before resuming dependent work, and remove the open question. With no `.plans/` file, record the question, answer, and reason in the conversation.

Pause dependent work and continue useful independent work. Do not reopen settled decisions without new evidence, silently narrow requirements, or wait until handoff to reveal the choice. If an answer or capability remains unavailable, clearly mark the affected work incomplete and report what is needed.

Installation, commits, publishing, and other external actions require authorization from the task; this workflow does not supply it.

## Handoff

After fixes and verification, write the handoff, even when the work stops on an open question. Its purpose is to give the user a technical understanding of the change: how the code works now, what the change is worth, what it costs, and where it might be wrong. Explain the program; do not narrate or certify your own work. Read [the handoff guidance](references/handoff.md) before writing it, for what each part is for, how to scale them, and examples.

A handoff has these parts, in this order:

- **Opening sentence:** one ordinary sentence beginning `You wanted`, restating the plan's goal sentence in the user's terms. With no plan, restate the request.
- **Summary:** a short paragraph with no heading or label. Its bold first sentence states the mechanism, what the code now does differently and where, such as `**The date filter now compares with >= where it used >.**` Then say what that achieves, give the results of the project's checks, naming any not run, and whether usage documentation changed as one clause, and end by naming any decision that awaits the user and any gap that affects confidence. It may mention the review.
- **`## How It Works`:** the change explained in the order the code runs, with a subheading per piece in a larger change and a short source excerpt and a verified link where the code is the clearest explanation. Guarantees and failure handling appear where their mechanism is explained. For a bug fix, open with one real input traced before and after.
- **`## Value and Cost`:** who benefits and how much, then the technical debt the change adds, sized as none, small, moderate, or significant. A larger change puts these under `### What It Adds` and `### What It Costs`. Always state the cost.
- **`## Verification`:** the commands or actions actually run through the application's entry point with their verbatim output, then how each other fact is known (ran, tested, or read only) and what was not checked.
- **`## Where I Would Aim Doubt`:** only when there is any. The places to look first if the change turned out wrong, in order, each with why.
- **`## Choices Made Without Asking`:** only when there are any. One line each: the choice and its reason. List a choice when a reasonable alternative existed and the plan did not settle it; omit local names and syntax.
- **`## Decisions Awaiting You`:** only when decisions remain. Number each item: a bold title naming the choice, the current state and what each option would change, then a recommendation and why. If you recommend keeping things as they are, leave the item out; for example, drop "I recommend leaving the duplicate parser as it is." The exception is a plan deviation you already made: always list it, even when you recommend keeping it. Plan deviations and unresolved findings go here, described as choices about the code, never by review labels such as Nit or Should-fix.

Scale the parts to the number of distinct ideas in the change. A tiny change is one idea and needs no headings: the opening sentence, the summary, the excerpt that matters, and a few sentences covering verification, value, and cost, plus `## Decisions Awaiting You` when one decision awaits. A change of two or three ideas keeps the `##` headings and drops the subheadings. A found problem or a pending decision does not move a change up a size. Write in sentences, without label prefixes such as `Value:` or `Tested:`.

If writing the handoff turns up a defect or a missing test within the agreed scope, fix it first and hand off the finished work. Give anything that needs the user's decision one home, and refer to it elsewhere in a few words.

When the plan is a `.plans/` file, change its `Status:` line to `complete` once no decision awaits and nothing is blocked. Never delete a plan file.

## Before Handoff

1. The change stays within the agreed scope and remaining discretion; every consequential gap was asked about, not decided (Execute Within Scope, Roadblocks and Handoff).
2. Formatting, lint, type, and behavior checks ran; results are recorded accurately, including anything not run (Verify Behavior).
3. The changed behavior was exercised through the actual entry point, or the limitation is stated (Verify Behavior).
4. The readability pass is done: each multistep function and test has a one-line stage comment at every transition that gives the reason where the code does not, with blank lines between stages (Explain Steps and Decisions).
5. Usage-documentation edits match the documentation map exactly; related documentation was inspected and any unplanned need was asked about ([documentation reference](references/documentation.md)).
6. Unless no review is required (Independent Review), the independent review ran; validated Blocker and Should-fix findings are fixed and affected checks rerun. Each applied Nit touches only lines this change already modifies and changes no behavior or tests; revert any that does not (Independent Review).
7. The handoff opens with the `You wanted` sentence and a summary whose bold first sentence states the mechanism. It explains how the code works now, states the value and the cost, says how each verification fact is known, and gives each decision a recommendation and why. A reader could predict from it what the code does in a case it does not mention (Handoff).
8. A plan saved under `.plans/` has its answered questions in the decision record, and is marked `Status: complete` when no decision awaits and nothing is blocked (Roadblocks and Handoff, Handoff).
