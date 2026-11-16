---
name: review-changes
description: Independently review a completed code change or targeted fixes against the agreed plan, reporting concrete correctness, maintainability, scope, and test findings.
---

# Review Changes

Review the actual changed state against the agreed plan and applicable project instructions. This is a read-only review; the implementing agent owns fixes. Review instructions do not authorize broad refactoring or a specialized security audit.

## Establish the Review Boundary

Read the plan, consequential decisions, and verification results. Honor the requested review unit: the completed change, a planned implementation step, or a targeted fix. Identify the base and reviewed state, including untracked/new files. Inspect the relevant diff and enough surrounding code, callers, and tests to understand affected contracts. For step reviews, distinguish current acceptance criteria from work deliberately assigned to later steps. Do not claim to have reviewed omitted files or results you did not inspect.

Use fresh context for an independent review: a supplied brief and source evidence, without the implementer's conversation history. If that history was inherited, disclose the limitation. Assess evidence without adopting the implementer's desired verdict. If the plan or base is missing, inspect what is available and state the review limitation. Do not invent acceptance criteria or reinterpret an agreed decision as an implementation defect.

For a targeted follow-up, review the stated unresolved risk, the fix, and paths its effects can reach. Expand only where the evidence shows the prior conclusions may no longer hold. Another full review of already reviewed scope is normally warranted only when substantial rework makes the earlier assessment obsolete. Reviews of distinct steps follow the task's agreed cadence.

## Assess the Change

Read the relevant code and documentation standards in `code-authoring` when assessing the change, using the host's available skill locations rather than assuming sibling directories. Apply those standards within this read-only review without executing its authoring workflow or starting another reviewer. If unavailable, report that coverage limitation and use the supplied requirements.

Check documentation against the documentation reference in `code-authoring`. Flag usage-documentation edits outside the plan's map, and unrequested new facts even when inserted into an existing paragraph or taken from code requirements. Inspect existing usage documentation related to changed behavior even when absent from the diff; report a needed unplanned correction as a plan amendment awaiting user confirmation, not an instruction to edit it, and report project requirements needing unrequested additions as a scope conflict. Check affected source doc comments/docstrings for contract accuracy, useful completeness, and unnecessary explanation; when recommending shortening, identify the facts to preserve and their destinations.

- Does it implement the agreed behavior, including errors, edge cases, and partial failures?
- Does every consequential choice trace to the plan and user agreement or an established requirement? Flag invented policies and undisclosed deviations even when tests pass; routine syntax and helper choices remain implementation discretion.
- Are public contracts, domain invariants, validation, and data ownership preserved?
- Is I/O concentrated at clear boundaries, with core logic understandable independently?
- For a coherent family of domain rules, does the change follow `code-authoring`'s declarative-rules preference? Judge the concrete readability benefit and the edits another case would need; accept direct one-off decisions and exhaustive mappings when clearer, and flag disproportionate frameworks.
- Are names, logical grouping, functions, and modules readable without unnecessary indirection or fragmentation?
- Do repeated collection lookups introduce avoidable scaling costs? Identify the actual traversal and lookup cost, rather than requesting speculative optimization.
- Does custom code duplicate an existing dependency's capability? Inspect the supported version's documentation or implementation before proposing replacement, and preserve custom behavior that addresses a real application-specific contract gap. Existing custom code or a passing test fake does not by itself justify keeping a duplicate.
- Do domain values retain meaning through named fields and appropriate types? Are idioms compatible with supported language versions?
- Are all changed responsibilities and dependencies necessary for the agreed scope?
- Do tests exercise meaningful behavior at the real boundary, with clear setup and assertions? Are they redundant or coupled to incidental implementation details?
- Do dependency integration tests invoke the real configured capability and check application outcomes, including relevant failures? Identify claims established only by a fake or duplicate implementation.
- Was the changed workflow exercised through the actual application entry point with observable results and relevant state, or is the execution limitation clearly stated? Distinguish workflow evidence from unit-test results; do not demand unavailable tools or unauthorized external actions.
- Are tooling changes justified? Are suppressions rare, narrow, and accompanied by a specific reason, including configuration-level exceptions?
- Do affected interface contracts, help, and usage examples match the implemented behavior and documentation lints? Check completeness and unnecessary prose without expanding the review into unrelated documentation.

Apply lighter style expectations to test failure shortcuts, while retaining logical grouping and step comments for multistep tests. Do not report an allowed test failure shortcut as a production-style violation. Distinguish a concrete readability problem from personal taste; identify the cost or contract at stake.

## Separate Behavior from Instruction Compliance

Perform two distinct assessments of the completed change. First check behavior, contracts, and tests. Then check compliance with the agreed scope and the concrete instructions in `code-authoring` and project guidance. Passing tests and correct behavior do not excuse an instruction violation. A specific violation of an explicit instruction is an actionable finding, even when it does not change runtime behavior; distinguish it from personal preference. Such findings are normally Should-fix, and Blocker only when they break agreed behavior or scope.

For usage documentation, compare added and rewritten factual claims with both the original text and the plan's documentation map, point to unauthorized clauses, and recommend removing them while keeping authorized corrections.

For implementation comments, identify each affected function's stages, including short functions and nested processing, and check them against `code-authoring`'s step-comment standard, including comment syntax, placement, and blank-line breaks. Flag the specific missing stage or rationale the reader must reconstruct. Do not demand comments for routine initialization, final returns, or straightforward single-step predicates and mappings, or recommend trivial helper extraction to avoid comments. Formatting tools passing does not establish these checks passed.

## Report Findings

The default review is a quick, pointed check: verify agreed behavior and failure paths first, then instruction compliance.

Give each finding one priority, and order findings by priority:

- **Blocker:** agreed behavior, a public contract, data integrity, or a required check is broken, or the plan cannot be fulfilled.
- **Should-fix:** a concrete violation of an explicit instruction or a maintainability problem with a named cost, without behavior impact.
- **Nit:** optional improvement; never required for completion.

Read [the reviewer brief and finding format](references/reviewer-brief.md). Prioritize actionable, evidence-backed findings with precise file locations, a concrete trigger or readability cost, and the consequence. Suggest the smallest correction consistent with the plan.

Separate verified defects from uncertainty and optional ideas. Keep speculative future features outside required fixes. If the code reveals that the plan cannot be fulfilled within scope, report that conflict as a blocker instead of choosing new behavior.

If there are no actionable findings, say so and state any material coverage limitation. Do not manufacture a finding or an exhaustive file inventory to justify the review. Return the result to the implementing agent, which decides fixes, reruns checks, and prepares the user's final handoff.
