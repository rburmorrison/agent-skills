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

Check affected source documentation for contract accuracy, completeness within the authorized documentation scope, and unnecessary explanation. When recommending shortening, identify the facts to preserve and their destinations. Retain concise bodies that meet the authoring standards' exception criteria. Inspect existing documentation related to changed behavior even when it is absent from the diff; identify stale claims or examples at the document's existing level of detail. Leave accurate documentation unchanged and do not require additions the user has not requested. Report project requirements that would need such additions as a scope conflict. Report actionable findings and material coverage limitations.

For each automatic documentation edit, check which existing statement or example the code change made inaccurate and whether the edit only corrects it. Flag unrequested new facts even when inserted into an existing paragraph or taken from implementation requirements. Apply the separate allowance for useful implementation comments from `code-authoring`.

- Does it implement the agreed behavior, including errors, edge cases, and partial failures?
- Are public contracts, domain invariants, validation, and data ownership preserved?
- Is I/O concentrated at clear boundaries, with core logic understandable independently?
- Are names, logical grouping, functions, and modules readable without unnecessary indirection or fragmentation?
- Do repeated collection lookups introduce avoidable scaling costs? Identify the actual traversal and lookup cost, rather than requesting speculative optimization.
- Do domain values retain meaning through named fields and appropriate types? Are idioms compatible with supported language versions?
- Are all changed responsibilities and dependencies necessary for the agreed scope?
- Do tests exercise meaningful behavior at the real boundary, with clear setup and assertions? Are they redundant or coupled to incidental implementation details?
- Are tooling changes justified? Are suppressions rare, narrow, and accompanied by a specific reason, including configuration-level exceptions?
- Do affected interface contracts, help, and usage examples match the implemented behavior and documentation lints? Check completeness and unnecessary prose without expanding the review into unrelated documentation.

Apply lighter style expectations to tests. Do not report an allowed test failure shortcut as a production-style violation. Distinguish a concrete readability problem from personal taste; identify the cost or contract at stake.

## Separate Behavior From Instruction Compliance

Perform two distinct assessments of the completed change. First check behavior, contracts, and tests. Then check compliance with the agreed scope and the concrete instructions in `code-authoring` and project guidance. Passing tests and correct behavior do not excuse an instruction violation. A specific violation of an explicit instruction is an actionable finding, even when it does not change runtime behavior; distinguish it from personal preference.

For documentation, compare added and rewritten factual claims with the original text. Identify the existing statement made inaccurate by the implementation and whether each new claim is needed to correct it. Flag a claim that merely adds an accurate but previously undocumented fact unless the user requested the addition. A code requirement is not permission to expand documentation. Point to the extra clause and recommend removing only that clause while keeping necessary corrections. Retain the separate allowance for useful implementation comments.

For implementation comments, apply the actual syntax and spacing requirements to each touched group. Check the line before the group's first comment, not just lines within the group. Verify ordinary single-line syntax and the required blank line unless the group starts its enclosing block. Keep API documentation syntax separate. Formatting tools passing does not establish these checks passed.

Check existing documentation related to changed behavior even when it is absent from the diff. Do not let the compliance check become an excuse to leave an already documented claim inaccurate.

## Report Findings

Read [the reviewer brief and finding format](references/reviewer-brief.md). Prioritize actionable, evidence-backed findings with precise file locations, a concrete trigger or readability cost, and the consequence. Suggest the smallest correction consistent with the plan.

Separate verified defects from uncertainty and optional ideas. Keep speculative future features outside required fixes. If the code reveals that the plan cannot be fulfilled within scope, report that conflict as a blocker instead of choosing new behavior.

If there are no actionable findings, say so and state any material coverage limitation. Do not manufacture a finding or an exhaustive file inventory to justify the review. Return the result to the implementing agent, which decides fixes, reruns checks, and prepares the user's final handoff.
