---
name: plan-changes
description: Investigate and plan a feature, fix, or refactor before editing. Resolve consequential decisions one at a time and produce concrete implementation steps.
---

# Plan Changes

Complete planning before implementation. Scale the work to the change: a small correction can have a short plan; a substantial feature needs explicit contracts and boundaries. Planning-only requests remain planning-only.

## Investigate

Read applicable project instructions and the code relevant to the requested behavior. Identify the current behavior, entry points, data types, I/O owners, dependencies, and verification commands. Inspect enough surrounding code to check the proposed approach's feasibility; avoid an unrelated repository survey.

Use available project context before asking for information. Distinguish established facts, user decisions, technical choices, and unresolved assumptions. Check external contracts and tool capabilities where the proposed design depends on them.

## Resolve decisions

Ask one consequential question at a time. Explain its practical effect and offer a recommendation when useful. Wait for the answer before asking the next question or deciding dependent behavior. Allow follow-up discussion; there is no fixed question quota.

Questions belong here when they change observable behavior, scope, public contracts, persistence, compatibility, or architectural commitments. Choose routine technical details using the requirements and project conventions. Describe consequential technical choices in the plan so the user can understand them before implementation.

Establish the outcome and exclusions. Include necessary supporting changes and explain why they are needed. Keep optional improvements separate. Plan for plausible evolution supported by the requirements, without speculative frameworks or abstractions.

For new projects, use `setup-project` if available to select tooling and supported versions during planning; initialization and configuration writes belong to implementation. Resolve any material tooling conflict before editing.

## Produce an implementation-ready plan

Make the following explicit when relevant, without imposing empty sections on small tasks:

- Agreed behavior, acceptance criteria, and exclusions.
- Consequential decisions and their reasons, including answers from the conversation.
- Existing file paths and symbols to change; distinguish proposed new locations from existing ones.
- Responsibilities, named domain types, interfaces, invariants, and data flow.
- I/O ownership, validation, error propagation, and partial-failure behavior.
- Implementation sequence and dependencies between steps.
- Meaningful behavior and failure cases to verify, plus runnable project check commands.
- Independent review coverage for non-trivial changes and any known verification limitations.

Make responsibility boundaries a concrete planning deliverable for non-trivial changes. For each substantial operation, specify:

- Its proposed function or method name, module, and responsibility.
- Its inputs and result, including the named types or fields that cross the boundary.
- Whether it performs I/O, and which operation owns coordination, errors, and any transaction or snapshot.

When substantial calculations would otherwise sit among I/O operations, plan a pure operation accepting ordinary values and a separate operation that coordinates external effects. Keep reads, calculations, and writes within the required consistency boundary. Choose these boundaries from the actual behavior and code; a step such as "implement storage logic" leaves that design unfinished.

Before finishing, trace a representative request through the proposed operations. Check that each responsibility has an owner and the implementer can connect their contracts without choosing the major decomposition. Keep cohesive sequences together; do not prescribe every helper, create layers without a concrete purpose, or use function-length targets.

When error categories are part of the contract, identify relevant parser or adapter failure families as well as domain-validation failures; inspect the boundary implementation when needed.

Resolve the design sufficiently for implementation to proceed within agreed behavior, scope, public contracts, and architectural boundaries. Leave routine details such as incidental helper extraction and idiomatic syntax to implementation.

Do not assume the same model will implement. A model switch in the same chat preserves the conversation, but the plan must still state the decisions and concrete work. Avoid vague steps such as "add validation" or unresolved menus of approaches. Read [the plan example](references/plan-example.md) when calibrating the necessary detail.

Use the chat for the plan unless the user or project asks for a saved artifact. Do not edit source or configuration while planning. Do not turn approval of a planning-only deliverable into authorization to implement.

## Transition

Once planning is complete and implementation is authorized, carry forward the plan and decisions; do not restart the interview after a model switch. Use `implement-changes` if available.

The implementation fallback is fixed: handle local obstacles autonomously; if completion requires changing an agreed decision, finish useful independent work and clearly report the blocker and incomplete work at the end. Known unresolved behavioral decisions must be settled before starting, rather than deferred to that fallback.
