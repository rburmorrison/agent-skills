---
name: plan-changes
description: Investigate and plan a non-trivial change before editing, resolving consequential decisions one at a time and producing concrete implementation steps. Use when building, changing, or fleshing out anything with design choices or open questions, even if no plan was requested. Skip for questions and simple, direct edits such as targeted fixes or refactors.
---

# Plan Changes

Complete planning before implementation. Scale the work to the change: a small correction can have a short plan; a substantial feature needs explicit contracts and boundaries. Planning-only requests remain planning-only.

## Investigate

Read applicable project instructions and the code relevant to the requested behavior. Identify the current behavior, entry points, data types, I/O owners, where state is mutated or hidden inputs such as the clock and environment are read, dependencies, and verification commands. Inspect enough surrounding code to check the proposed approach's feasibility; avoid an unrelated repository survey.

When the relevant code's location is unknown or spread across the codebase, and the harness provides a subagent meant for code exploration or the user or project names one, delegate the search to it; otherwise investigate directly. Choose the agent, never its model: the harness's configuration sets the model, so do not pick, guess, or compare models. Ask the explorer for paths, line ranges, short excerpts, and what it searched without finding. Treat its report as leads. Read for yourself every range you will quote to the user, plan to change, or rely on for a contract, and run the search yourself when a decision depends on a list being complete, such as every caller of a signature that will change. Throughout this skill, inspected code means code you read.

Use available project context before asking for information. Distinguish established facts, user decisions, technical choices, and unresolved assumptions. Check external contracts and tool capabilities where the proposed design depends on them.

Before designing custom parsing, formatting, layout, scheduling, or other behavior covered by an existing dependency, inspect the supported version's documentation or implementation and relevant call sites, and plan to reuse its capability as `code-authoring` requires. Record the evidence found and any unavailable evidence as uncertainty rather than assuming a capability exists or is missing.

## Resolve Decisions

Ask as many questions as necessary to reach agreement, one consequential question at a time. Do not bundle independent choices into a single confirmation; a shared topic does not make them one decision. Explain the options, practical effects, and reason for your recommendation. Wait for the answer before asking the next question or deciding dependent behavior. Do not shorten the interview to meet a question quota, avoid bothering the user, or rush to a plan. Reuse explicit answers already given; silence, an unanswered recommendation, and general permission to implement are not agreement to a new consequential choice.

Questions belong here when they change observable behavior, scope, public contracts, persistence, compatibility, or architectural commitments. Include edge cases, failure policy, dependencies, and documentation additions when they affect those commitments. A choice being technical or recommended does not make it routine. Confirm new consequential choices with the user before encoding them as settled; do not first reveal them in a completed plan. Choose routine technical details using the requirements and project conventions, and explain material implementation choices in the plan.

Keep a decision record: each consequential choice, its rationale, and the user answer or established requirement that supports it. Distinguish confirmed decisions, existing behavior to preserve, routine technical choices, and open questions. Audit the proposed happy path, failures, and edge cases for assumptions that could surprise the user. Resolve any consequential open question before declaring the plan ready.

Establish the outcome and exclusions. Include necessary supporting changes and explain why they are needed. Keep optional improvements separate. Plan for plausible evolution supported by the requirements, without speculative frameworks or abstractions.

For new projects, use `setup-project` if available to select tooling and supported versions during planning; initialization and configuration writes belong to implementation. Resolve any material tooling conflict before editing.

### Present Decision Context

Present every decision in this shape, with all of its context ahead of the request for an answer:

```markdown
**Decision 2 of 3: Should an Invoice Be Reminded More Than Once?**

**Situation:** The reminder job will run daily. Nothing currently records that a reminder was sent, so without a rule, every overdue invoice gets an email every day.

**Options:**
- **A. Once only.** Needs a `reminded_at` column. Customers who ignore the first email never hear again.
- **B. Every 7 days until paid (recommended).** Same column, plus an interval check.
- **C. Daily.** No schema change, but likely to generate complaints.

**Why B:** The payment-failed emails already repeat weekly, so customers get one consistent cadence. A stops chasing after one ignored email, which defeats the feature. C saves a migration, but daily emails are the likeliest to be marked as spam.

**Cost to Reverse:** A to B is a one-line change later. C to either needs the migration anyway.
```

- **Title.** One question that frames the actual choice in behavior or responsibilities, in Title Case. Number it, and give the total when it is known. Do not repeat the question at the bottom.
- **Situation.** Say why the requested work introduces this decision and what happens today, in enough detail to answer without asking what the code does, what would replace it, or what the alternatives mean. Ground current behavior in inspected code: name the file and symbol, and when the choice turns on what the code does, put a focused excerpt directly beneath with a plain-language explanation; a file link alone is not sufficient context. Label proposed code, simplified excerpts, and pseudocode so they cannot be mistaken for the current implementation. For a new addition, describe the surrounding workflow, what triggers the feature, and what does not exist yet; use a concrete scenario rather than inventing an implementation to replace. State uncertainty when evidence is unavailable.
- **Options.** Letter each option and give it its own bullet: a bold plain-language name, then what it changes in practice. Name the consequential behavior the user is deciding, not an implementation label such as "use the library" or "add caching." Compare the options on the same input or usage scenario, and put material consequences beside the option they belong to: user-visible effects, compatibility, persistence, error handling, dependencies, new responsibilities, and implementation or maintenance costs. For a change to existing behavior, make clear what each option replaces and what it preserves. Mark exactly one option `(recommended)`.
- **Why.** Head it with the recommended option's letter. Argue for the recommendation against each other option by name, tied to the requirements and inspected evidence, and include its material downside.
- **Cost to Reverse.** Say what changing the answer later would take.

Keep all five parts and scale their length to the decision; a simple question needs one sentence in each. Add a table, a before-and-after excerpt, or a worked failure or edge case beneath **Situation** only when it makes the options easier to compare.

Provide this context with the question before requesting an answer, including when using a question tool with short option labels. The user should not need to reconstruct the investigation or read a completed plan to understand the decision.

## Produce an Implementation-Ready Plan

Make the following explicit when relevant, without imposing empty sections on small tasks:

- A one-sentence goal stating the requested outcome in the user's terms. Questions and the handoff repeat it, so write it to stand alone.
- Agreed behavior, acceptance criteria, and exclusions.
- The decision record, including answers from the conversation and task-specific overrides to the usual conventions or review cadence.
- Existing file paths and symbols to change; distinguish proposed new locations from existing ones.
- Concrete operation contracts as specified below, including invariants and the data-flow chain.
- A documentation change map, including an explicit statement when no usage-documentation edits are planned.
- Implementation steps, each with affected paths and symbols, concrete changes, existing mechanisms to reuse, dependencies, and acceptance criteria.
- Meaningful behavior and failure cases with inputs and expected outcomes, plus runnable project check commands.
- A feasible user-workflow check: setup, actual application entry point, actions, expected visible results and state, and cleanup. Record known obstacles to execution.
- The guarantees and failure handling the change must establish, each as one numbered sentence (`G1`, `F1`). A guarantee is something always or never true after the change, for every input. A failure-handling entry says what goes wrong, what the user sees, what state is left, and how to recover. The implementation and the review are checked against this list; the handoff explains how the code establishes each one and flags any that is unmet or untested.
- The material routine choices you made without asking, one line each with its reason, so the user can spot a choice that should have been a question. This list never holds a consequential choice; those are asked.
- Remaining routine discretion, such as incidental helper extraction and idiomatic syntax.
- Whether the change is small as `code-authoring`'s Independent Review defines, and so needs no independent review; otherwise the independent review coverage. Include any known verification limitations.
- An Implementer Brief closing the plan, as described below.

When source documentation or caller-facing behavior changes, read the documentation reference in `code-authoring` (`references/documentation.md`) from the available skill locations without executing its authoring workflow; if unavailable, state the limitation and use the supplied requirements. Produce the documentation change map as that reference defines it, ask the user before planning any addition, and state "No usage-documentation edits planned." when none are planned. Plan the final accuracy inspection it describes.

Make responsibility boundaries a concrete planning deliverable for non-trivial changes. For each substantial operation, specify:

- Its proposed function or method name, module, and responsibility.
- Its exact boundary signature or equivalent input/result contract, including named types and fields, their meaning, and relevant constraints.
- Whether it is pure or has effects: I/O, mutation of its inputs or shared state, or hidden inputs such as time, randomness, or environment. For effects, name which operation owns coordination, error handling, and any transaction or snapshot.
- Precise validation rules, error categories and presentation, and partial-failure behavior. Include relevant parser or adapter failure families as well as domain failures; inspect the boundary implementation when needed.
- A stage outline: the operation's ordered stages, each as one plain sentence saying what the stage does, with the reason where ordering or a constraint matters. The implementer turns each into its stage comment.
- Pseudocode where ordering or algorithm choices affect correctness.

### Design Toward a Functional, Declarative Core

Default to a core that states what the result is rather than scripting how to reach it, built from pure operations, with effects at named edges:

- Domain values are immutable. Operations return new values instead of modifying their inputs or shared state.
- Calculations and decisions are pure operations over ordinary values. Read hidden inputs such as the current time, randomness, environment, and configuration at the edge and pass them in.
- Rules, schemas, and transformations are declarations where that reads more clearly: rule tables per `code-authoring`'s declarative domain rules; a dependency's declarative APIs, such as schema validation, derived argument parsing, or set-based queries, rather than hand-written loops; and mapping, filtering, and grouping expressions rather than accumulator loops.
- When a decision determines writes, messages, or commands, represent the decision as a value describing those effects, and apply it in a separate operation (decide, then apply). When the goal is a target state, derive those effects by comparing the desired state with the current state rather than scripting each change. `ImportPlan` in [the full example](references/plan-example.md) has this shape.
- Coordinating operations stay thin: gather inputs, call the core, apply its result, and own error handling and any transaction. Keep reads, calculations, and writes within the required consistency boundary.

Imperative code remains appropriate where it is clearer or required: ordered I/O, local mutation inside one function, framework APIs built around mutable state, and performance needs that are measured or a stated hot path, where the plan names the path, the data size, and the cost avoided. Do not introduce effect systems, monadic wrappers, state threaded through unrelated operations, custom rule engines or configuration languages, or combinator chains harder to read than a loop. When the plan keeps a substantial calculation or state change imperative, record the concrete reason. Choose boundaries from the actual behavior and code; a step such as "implement storage logic" leaves that design unfinished.

For non-trivial changes, include a data-flow chain: the typed transformations from input to result, with each effectful step marked. Pseudocode supplements the chain where ordering affects correctness.

When the change modifies existing imperative code, plan to separate the pure core of the behavior being changed from its effects, within the operations the change already touches, preserving behavior and public contracts. Explain the separation in the plan, and confirm it with the user when it changes module boundaries or public interfaces. Restructuring beyond the touched behavior is an optional improvement: propose it separately rather than including it. When the codebase has an established style that differs, such as consistently object-oriented code built around mutable state, that style wins: plan to match it, and raise any move toward a functional core as a decision for the user.

For each coherent family of domain rules, decide the representation per `code-authoring`'s guidance on declarative domain rules and record the concrete readability reason in the plan.

### Check and Close the Plan

Before finishing, trace a representative request and a meaningful failure through the proposed operations. Check that each responsibility and effect has an owner, pure operations receive their inputs explicitly, and the implementer can connect their contracts without choosing the major decomposition. Connect acceptance criteria to implementation steps and verification scenarios. Check that paths and reused capabilities were inspected, consequential choices have agreement and reasons, the documentation map is bounded, and remaining discretion is only routine. Keep cohesive sequences together; do not prescribe every helper, create layers without a concrete purpose, or use function-length targets.

Every plan ends with an **Implementer Brief**: a short list (about 10 bullets at most) the implementing model reads before editing. It covers: load `code-authoring`; the documentation-map entries or "No usage-documentation edits planned."; this plan's stop-and-ask triggers (decisions deliberately left to the user, and changes that would need a plan amendment); the checks to run with expected results; the user-workflow check; the review expectation, either one independent review, none for a small change, or the task's agreed cadence; and, for a saved plan, marking the file complete at handoff. Restate only what this plan needs; do not copy general rules. Do not assume the same model or session will implement: the implementer may have only the plan file, so the plan must state the decisions and concrete work, avoiding vague steps such as "add validation" and unresolved menus of approaches. Read [the small example](references/plan-example-small.md) for small corrections and [the full example](references/plan-example.md) for substantial changes when calibrating the necessary detail.

### Save the Plan

Write a plan with more than one implementation step to a file; keep a smaller plan in the chat. A user or project instruction asking for a chat plan overrides this default.

When the harness has placed you in a planning mode that provides its own way to present or save a plan, deliver the full plan through that instead, and write nothing under `.plans/`. Use the same format: the title, `Status:` and `Goal:` lines, the plan, `## Open Questions`, and the Implementer Brief. The harness then shows the whole plan, so no separate chat summary is needed. In every other mode:

- Use the path `.plans/<YYYY-MM-DD>-<short-slug>.md` at the project root. When creating `.plans/`, also create `.plans/.gitignore` containing the single line `*`, so version control ignores the directory, including that file.
- Open the file with a `# ` title, then `Status: in progress`, then `Goal: ` and the goal sentence, each on its own line. Place an `## Open Questions` section, containing `None.` until the implementer records one, before the Implementer Brief.
- The file is the only full copy. In the chat, give the goal sentence, the decision record, the routine choices, and the file path, then ask for agreement. Revise the file in place when the user changes or rejects part of the plan.
- Never delete a plan file. The implementer marks it `Status: complete` at handoff, and the user removes it.
- If the project root cannot be written, say so and keep the full plan in the chat.

Do not edit source or configuration while planning. Do not turn approval of a planning-only deliverable into authorization to implement.

## Transition

Once planning is complete and implementation is authorized, carry forward the plan and decisions; do not restart the interview after a model switch. Use `code-authoring` if available. List this plan's stop-and-ask triggers in the Implementer Brief; the immediate-question procedure itself is owned by `code-authoring`'s Roadblocks and Handoff.
