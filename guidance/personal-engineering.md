# Personal Engineering Guidance

Complete planning before editing. Ask consequential questions one at a time, allowing each answer to inform the next. Resolve decisions affecting behavior, scope, public contracts, data ownership, I/O boundaries, and architecture before implementation. Scale planning to the change; a small, unambiguous correction needs only a brief plan.

Use `plan-changes` to prepare an implementation-ready plan. Continue from an agreed plan when one exists, including after a model switch in the same chat. Preserve the decisions and their reasons from the conversation. Do not infer the future implementing model's capabilities.

Use `code-authoring` to carry out an agreed change. Choose local implementation details autonomously within its boundaries. Keep optional improvements outside the change unless included in the agreed scope.

Prefer meaningful domain names, explicit data contracts, cohesive functions and modules, and concentrated I/O boundaries. Use whitespace between conceptual units; compact match arms usually form one unit. Test readability matters more than applying every production style restriction to tests.

Use `setup-project` when establishing a new project. Establish strict tooling appropriate to its language and supported versions. Manage dependencies through the project's package manager rather than guessing versions and editing dependency entries by hand.

Lint suppressions must be rare, narrowly scoped, and accompanied by a specific reason. Explain configuration-level exceptions beside the setting. Fix underlying issues when possible; do not weaken checks merely to obtain a passing result.

For non-trivial changes, use a separate reviewer agent with fresh context and the `review-changes` skill. Fix validated findings within scope and rerun affected checks. Default to one full review; request targeted follow-ups autonomously when fixes warrant them.

If completing a change requires altering agreed behavior or scope, finish useful independent work and report the roadblock at the end. Clearly identify incomplete work. Do not invent new behavior, silently narrow acceptance criteria, or interrupt implementation with another design interview.

Keep the final handoff concise. Explain what changed, why, and the useful details of the approach in plain sentences. Summarize important tested behavior and verification results. When human attention would help, provide a small, prioritized table of clickable local file links with verified line numbers and the decision worth inspecting. It is acceptable to recommend no targeted human review.

Apply the documentation standards in `code-authoring` to source documentation, READMEs, built-in help, and user guides, including during fixes and skill maintenance. At the end of a code change, inspect related existing documentation, consider its core purpose, and update only what the change makes inaccurate. Adding a previously undocumented fact to an existing passage is new documentation, even if the fact is accurate, relevant, or stated in implementation requirements. Leave accurate documentation unchanged; the user decides what new documentation to add. Keep interface contracts brief but complete within the authorized scope, with a separate allowance for selective implementation comments. Follow documentation lints even for otherwise internal items, report requirements that would need unrequested additions, and use Title Case for authored headings.

These conventions are defaults. Follow explicit task-specific instructions that override them, retain unaffected defaults, and record the overrides in the plan so they survive model changes. An explicitly requested review cadence replaces the default cadence rather than adding another mandatory review.

These defaults support the current request and applicable project conventions. They do not authorize additional scope, commits, publishing, installation, or external actions. If a named skill or required reviewer capability is unavailable, state the limitation rather than claiming it was used.
