## Engineering Workflow

For changes beyond a small, unambiguous correction, plan before editing. Use `plan-changes`: investigate, ask consequential questions one at a time, and get agreement on decisions affecting behavior, scope, public contracts, data ownership, I/O boundaries, and architecture. Silence or general permission to implement is not agreement to a new choice.

Before editing any file, including for a small fix, invoke the `code-authoring` skill and follow it through verification and handoff. When continuing an agreed plan, including after a model switch or in a new session, read its plan file when one exists and follow the plan and its Implementer Brief, and ask immediately about any consequential gap instead of deciding it.

Use `setup-project` when establishing a new project. For non-trivial changes, run one independent review in a fresh-context subagent using `review-changes`.

Verify changes as a user would, through the actual CLI, UI, API, or caller when feasible, and report what remains unverified. Never claim a check passed unless it ran.

These are defaults: explicit task instructions override them. They do not authorize additional scope, commits, publishing, installation, or external actions. If a named skill is unavailable, say so instead of claiming it was used.
