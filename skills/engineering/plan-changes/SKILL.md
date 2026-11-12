---
name: plan-changes
description: Investigate and plan a feature, fix, or refactor before editing. Resolve consequential decisions one at a time and produce concrete implementation steps.
---

# Plan Changes

Complete planning before implementation. Scale the work to the change: a small correction can have a short plan; a substantial feature needs explicit contracts and boundaries. Planning-only requests remain planning-only.

## Investigate

Read applicable project instructions and the code relevant to the requested behavior. Identify the current behavior, entry points, data types, I/O owners, dependencies, and verification commands. Inspect enough surrounding code to check the proposed approach's feasibility; avoid an unrelated repository survey.

Use available project context before asking for information. Distinguish established facts, user decisions, technical choices, and unresolved assumptions. Check external contracts and tool capabilities where the proposed design depends on them.

Before designing custom parsing, formatting, layout, scheduling, or other behavior covered by an existing dependency, inspect the supported version's documentation or implementation and relevant call sites. Identify the built-in capability, the application policy it leaves to the caller, and any concrete contract gap. Prefer using or configuring that capability; a wrapper or replacement must own a responsibility the dependency does not already satisfy. Do not add a dependency merely to avoid a small cohesive operation. Record unavailable evidence as uncertainty rather than assuming a capability exists or is missing.

## Resolve Decisions

Ask as many questions as necessary to reach agreement, one consequential question at a time. Do not bundle independent choices into a single confirmation; a shared topic does not make them one decision. Explain the options, practical effects, and reason for your recommendation. Wait for the answer before asking the next question or deciding dependent behavior. Do not shorten the interview to meet a question quota, avoid bothering the user, or rush to a plan. Reuse explicit answers already given; silence, an unanswered recommendation, and general permission to implement are not agreement to a new consequential choice.

Questions belong here when they change observable behavior, scope, public contracts, persistence, compatibility, or architectural commitments. Include edge cases, failure policy, dependencies, and documentation additions when they affect those commitments. A choice being technical or recommended does not make it routine. Confirm new consequential choices with the user before encoding them as settled; do not first reveal them in a completed plan. Choose routine technical details using the requirements and project conventions, and explain material implementation choices in the plan.

Keep a decision record: each consequential choice, its rationale, and the user answer or established requirement that supports it. Distinguish confirmed decisions, existing behavior to preserve, routine technical choices, and open questions. Audit the proposed happy path, failures, and edge cases for assumptions that could surprise the user. Resolve any consequential open question before declaring the plan ready.

Establish the outcome and exclusions. Include necessary supporting changes and explain why they are needed. Keep optional improvements separate. Plan for plausible evolution supported by the requirements, without speculative frameworks or abstractions.

For new projects, use `setup-project` if available to select tooling and supported versions during planning; initialization and configuration writes belong to implementation. Resolve any material tooling conflict before editing.

## Produce an Implementation-Ready Plan

Make the following explicit when relevant, without imposing empty sections on small tasks:

- Agreed behavior, acceptance criteria, and exclusions.
- The decision record, including answers from the conversation and task-specific overrides to the usual conventions or review cadence.
- Existing file paths and symbols to change; distinguish proposed new locations from existing ones.
- Concrete operation contracts as specified below, including invariants and data flow.
- A documentation change map, including an explicit statement when no usage-documentation edits are planned.
- Implementation steps, each with affected paths and symbols, concrete changes, existing mechanisms to reuse, dependencies, and acceptance criteria.
- Meaningful behavior and failure cases with inputs and expected outcomes, plus runnable project check commands.
- A feasible user-workflow check: setup, actual application entry point, actions, expected visible results and state, and cleanup. Record known obstacles to execution.
- Remaining routine discretion, such as incidental helper extraction and idiomatic syntax.
- Independent review coverage for non-trivial changes and any known verification limitations.

When source documentation or caller-facing behavior changes, read the relevant documentation standards in `code-authoring` from the available skill locations without executing its authoring workflow. If unavailable, state the limitation and use the supplied requirements.

For READMEs, guides, standalone reference material, built-in help, and user examples, name each planned edit's path and section or symbol, the existing claim made inaccurate by the change, the required correction, and its verification. Listing a file or saying "update documentation" is not sufficient scope. Leave accurate content unchanged. New documents, sections, examples, or previously undocumented facts require an explicit user request or confirmation, even inside an existing passage. You may ask whether the user wants a specific addition and explain why; wait for confirmation before including it. Record that authorization in the map. If none is needed or requested, state "No usage-documentation edits planned." The implementer must not edit usage documentation outside this map; a newly discovered need requires a confirmed plan amendment.

Source implementation comments and API doc comments/docstrings remain allowed within the affected code under `code-authoring`; they do not require listing every comment in the map. Assign contract facts to their owning interfaces, keep member facts on members, and distinguish type-wide guarantees from operation-specific guarantees. This allowance does not authorize expanding guides or standalone documentation. Plan a final accuracy inspection, including related documentation outside the edit map; inspection does not authorize unplanned edits. Surface project requirements that would need additions beyond the requested scope.

Make responsibility boundaries a concrete planning deliverable for non-trivial changes. For each substantial operation, specify:

- Its proposed function or method name, module, and responsibility.
- Its exact boundary signature or equivalent input/result contract, including named types and fields, their meaning, and relevant constraints.
- Whether it performs I/O, and which operation owns coordination, error handling, and any transaction or snapshot.
- Precise validation rules, error categories and presentation, and partial-failure behavior. Include relevant parser or adapter failure families as well as domain failures; inspect the boundary implementation when needed.
- Pseudocode where ordering or algorithm choices affect correctness.

When substantial calculations would otherwise sit among I/O operations, plan a pure operation accepting ordinary values and a separate operation that coordinates external effects. Keep reads, calculations, and writes within the required consistency boundary. Choose these boundaries from the actual behavior and code; a step such as "implement storage logic" leaves that design unfinished.

For each coherent family of domain rules, compare meaningful declarations interpreted by a small shared mechanism with procedural branching. Choose the representation that makes the rules easiest to read together, even with only two cases and before duplication becomes costly. Keep related selectors and metadata together, prefer supported declarative dependency APIs, and record the concrete readability benefit in the plan. Keep one-off decisions and inherently ordered operations direct; do not invent a framework or configuration language without a concrete benefit.

Before finishing, trace a representative request and a meaningful failure through the proposed operations. Check that each responsibility has an owner and the implementer can connect their contracts without choosing the major decomposition. Connect acceptance criteria to implementation steps and verification scenarios. Check that paths and reused capabilities were inspected, consequential choices have agreement and reasons, the documentation map is bounded, and remaining discretion is only routine. Keep cohesive sequences together; do not prescribe every helper, create layers without a concrete purpose, or use function-length targets.

Do not assume the same model will implement. A model switch in the same chat preserves the conversation, but the plan must still state the decisions and concrete work. Avoid vague steps such as "add validation" or unresolved menus of approaches. Read [the plan example](references/plan-example.md) when calibrating the necessary detail.

Use the chat for the plan unless the user or project asks for a saved artifact. Do not edit source or configuration while planning. Do not turn approval of a planning-only deliverable into authorization to implement.

## Transition

Once planning is complete and implementation is authorized, carry forward the plan and decisions; do not restart the interview after a model switch. Use `code-authoring` if available.

Carry this rule into the handoff: a new consequential choice or change to agreed decisions or documentation scope requires an immediate user question. Pause dependent work, continue independent work, and record the answer and rationale before resuming. Follow `code-authoring`'s Roadblocks and Handoff procedure when available. Work awaiting an answer or required capability remains explicitly incomplete.
