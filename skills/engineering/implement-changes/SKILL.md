---
name: implement-changes
description: Implement an agreed feature, fix, or refactor with readable code, focused tests, independent review, and a concise review guide.
---

# Implement Changes

Use the agreed plan and decisions from the conversation, including after a model switch. If consequential behavior or scope remains unresolved, complete planning with the user one question at a time before editing; use `plan-changes` if available. A small unambiguous task needs only proportionate planning.

## Execute within scope

Choose local implementation details autonomously while preserving agreed behavior, public contracts, architectural boundaries, and scope. Necessary supporting changes must serve the requested outcome. Keep optional cleanup, new features, dependency upgrades, and reorganizations outside the change unless planned.

Concentrate filesystem, network, database, clock, and environment access at explicit boundaries where applicable. Pass ordinary values into core transformations and decisions. Use the project's existing boundary mechanisms; introduce abstractions only when they make a concrete responsibility or dependency easier to manage.

Manage dependencies through the project's package manager. Use actual package information and supported-version constraints; do not guess versions or hand-edit dependency entries as a shortcut. Respect existing workspace dependencies and lockfile policy. If the needed tool is unavailable, apply the blocker policy instead of silently bypassing it.

## Shape readable code

- Name domain concepts, responsibilities, and operations using the problem's vocabulary.
- Prefer named records, fields, and explicit variants for domain values crossing boundaries. Local, immediately unpacked tuples remain useful. Add runtime validation at external boundaries when required; do not add a validation dependency merely to name internal fields.
- Group statements that perform one conceptual step. Separate changes of purpose with whitespace. Compact match arms generally form one unit and need no extra blank lines.
- Extract coherent operations with meaningful names. Keep a simple sequence together when splitting it would add navigation without improving comprehension.
- Organize modules by responsibility and reasons to change. Keep types near the code that owns their meaning. Treat size and complexity as inspection signals rather than incentives to create trivial files or helpers.
- Use idioms supported by the declared language version. Pattern matching suits meaningful variants and structured alternatives; ordinary predicates can remain conditionals.
- Explain non-obvious decisions, contracts, and constraints when needed. Avoid comments that narrate obvious statements or documentation added solely for volume.

Read [the code examples](references/code-examples.md) for non-trivial implementation or when resolving a style tradeoff. Their languages illustrate shared principles rather than restricting the skill's scope.

## Verify behavior

Read [the testing guidance](references/testing.md) when adding or changing tests. Cover meaningful agreed behavior and failure cases with readable setup, actions, and assertions. Test count is not a target.

Run applicable project formatting, linting, type, and behavior checks. Record what ran and any limitations. Do not claim that checks passed when they were unavailable or not executed.

Lint and type-check suppressions must be rare, narrowly scoped, and accompanied by a specific reason. Prefer fixing the underlying problem. Use native justification syntax when available, otherwise a nearby explanation. Explain configuration-level exceptions beside the setting; do not weaken checks simply to obtain a pass.

## Independent review

For non-trivial changes, delegate one full review to a separate agent with fresh context. Behavioral changes involving interacting components, public contracts, persistence, or significant refactoring normally qualify. Pure formatting and typo corrections usually do not.

Give the reviewer the agreed plan and decisions, actual final diff including new files, relevant code, and verification results. Use `review-changes` if available. Do not supply the implementer's self-assessment or a desired verdict. Use the task's chosen reviewer model; if none was chosen, use the environment's normal inheritance rather than guessing model IDs or upgrading silently.

Assess findings against the code. Fix validated findings within scope and rerun affected checks. Request a targeted follow-up autonomously when a fix materially changes logic, interfaces, or component interactions. A second full review is exceptional and appropriate when substantial rework invalidates the first review. Do not repeat full reviews as a ritual or leave a known defect unaddressed solely to satisfy a round count.

If reviewer capability is unavailable, perform a distinct self-review and disclose that independent review was unavailable. A self-review must not be described as independent.

## Roadblocks and handoff

Handle routine local obstacles autonomously. If completion requires changing agreed behavior or scope, finish useful independent work and report the roadblock at the end. Clearly mark the task incomplete, identify what remains, and explain the decision or capability needed. Do not start another design interview during implementation, silently narrow requirements, or expose unfinished behavior as complete.

Follow [the handoff guidance](references/handoff.md) after fixes and verification. Report concise outcomes, important behavioral commitments, and only useful human review targets. Installation, commits, publishing, and other external actions require authorization from the task; this workflow does not supply it.
