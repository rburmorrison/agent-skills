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

Check affected source doc comments/docstrings for contract accuracy, useful completeness, and unnecessary explanation under their separate allowance. When recommending shortening, identify the facts to preserve and their destinations. Retain concise bodies that meet the authoring standards' exception criteria. Inspect existing usage documentation related to changed behavior even when absent from the diff; identify stale claims or examples at the document's existing level of detail. Leave accurate content unchanged. If a necessary usage-documentation correction is outside the plan's map, report the need for user confirmation of a plan amendment, not an instruction to edit it immediately. Report project requirements needing unrequested additions as a scope conflict.

For each usage-documentation edit, check its planned location and correction or explicit user authorization for an addition. Flag unplanned edits even when they fix accuracy, and unrequested new facts even when inserted into an existing paragraph or taken from code requirements. Apply the separate allowances for useful implementation comments and source API doc comments/docstrings from `code-authoring`.

- Does it implement the agreed behavior, including errors, edge cases, and partial failures?
- Does every consequential choice trace to the plan and user agreement or an established requirement? Flag invented policies and undisclosed deviations even when tests pass; routine syntax and helper choices remain implementation discretion.
- Are public contracts, domain invariants, validation, and data ownership preserved?
- Is I/O concentrated at clear boundaries, with core logic understandable independently?
- Are names, logical grouping, functions, and modules readable without unnecessary indirection or fragmentation?
- Do repeated collection lookups introduce avoidable scaling costs? Identify the actual traversal and lookup cost, rather than requesting speculative optimization.
- Does custom code duplicate an existing dependency's capability? Inspect the supported version's documentation or implementation before proposing replacement. Identify the application-specific contract gap, if any; a wrapper, manual algorithm, or test fake is not justified merely because it already exists or passes tests. Preserve custom behavior the dependency cannot satisfy.
- Do domain values retain meaning through named fields and appropriate types? Are idioms compatible with supported language versions?
- Are all changed responsibilities and dependencies necessary for the agreed scope?
- Do tests exercise meaningful behavior at the real boundary, with clear setup and assertions? Are they redundant or coupled to incidental implementation details?
- Do dependency integration tests invoke the real configured capability and check application outcomes, including relevant failures? Identify claims established only by a fake or duplicate implementation.
- Was the changed workflow exercised through the actual application entry point with observable results and relevant state, or is the execution limitation clearly stated? Distinguish workflow evidence from unit-test results; do not demand unavailable tools or unauthorized external actions.
- Are tooling changes justified? Are suppressions rare, narrow, and accompanied by a specific reason, including configuration-level exceptions?
- Do affected interface contracts, help, and usage examples match the implemented behavior and documentation lints? Check completeness and unnecessary prose without expanding the review into unrelated documentation.

Apply lighter style expectations to test failure shortcuts, while retaining logical grouping and step comments for multistep tests. Do not report an allowed test failure shortcut as a production-style violation. Distinguish a concrete readability problem from personal taste; identify the cost or contract at stake.

## Separate Behavior From Instruction Compliance

Perform two distinct assessments of the completed change. First check behavior, contracts, and tests. Then check compliance with the agreed scope and the concrete instructions in `code-authoring` and project guidance. Passing tests and correct behavior do not excuse an instruction violation. A specific violation of an explicit instruction is an actionable finding, even when it does not change runtime behavior; distinguish it from personal preference.

For usage documentation, compare added and rewritten factual claims with both the original text and the plan's documentation map. A code requirement, reviewer suggestion, or accuracy inspection is not permission to expand the edit scope. Point to unauthorized clauses and recommend removing them while keeping authorized corrections. Treat useful source implementation comments and API doc comments/docstrings under their separate standards.

For implementation comments, first identify the logical stages in each affected function, including short functions and nested processing. Flag missing short, imperative stage comments, missing whitespace between stages, and unexplained consequential decisions or ordering requirements. A broad comment naming several stages does not replace comments at their transitions. Also check smaller whitespace breaks between setup and traversal or completed processing and a final return. Identify the specific stage or rationale the reader must reconstruct. Do not demand comments for routine initialization, final returns, or straightforward single-step predicates and mappings, or recommend trivial helper extraction to avoid comments.

Then check comment syntax and placement. Check the line before each group's first comment, not just lines within the group. Verify ordinary single-line syntax and the required blank line unless the group starts its enclosing block. Keep API documentation syntax separate. Formatting tools passing does not establish these checks passed.

Check related existing documentation even when absent from the diff. Surface unplanned stale claims as unresolved plan amendments; do not silently ignore them or authorize their repair yourself.

## Report Findings

Read [the reviewer brief and finding format](references/reviewer-brief.md). Prioritize actionable, evidence-backed findings with precise file locations, a concrete trigger or readability cost, and the consequence. Suggest the smallest correction consistent with the plan.

Separate verified defects from uncertainty and optional ideas. Keep speculative future features outside required fixes. If the code reveals that the plan cannot be fulfilled within scope, report that conflict as a blocker instead of choosing new behavior.

If there are no actionable findings, say so and state any material coverage limitation. Do not manufacture a finding or an exhaustive file inventory to justify the review. Return the result to the implementing agent, which decides fixes, reruns checks, and prepares the user's final handoff.
