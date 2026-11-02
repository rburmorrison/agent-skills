---
name: review-changes
description: Independently review a completed code change or targeted fixes against the agreed plan, reporting concrete correctness, maintainability, scope, and test findings.
---

# Review Changes

Review the actual changed state against the agreed plan and applicable project instructions. This is a read-only review; the implementing agent owns fixes. Review instructions do not authorize broad refactoring or a specialized security audit.

## Establish the review boundary

Read the plan, consequential decisions, and verification results. Identify the base and reviewed state, including untracked/new files. Inspect the relevant diff and enough surrounding code, callers, and tests to understand affected contracts. Do not claim to have reviewed omitted files or results you did not inspect.

Use fresh context for an independent review. Assess evidence without adopting the implementer's desired verdict. If the plan or base is missing, inspect what is available and state the review limitation. Do not invent acceptance criteria or reinterpret an agreed decision as an implementation defect.

For a targeted follow-up, review the fix and paths its effects can reach. Expand only where the evidence shows the prior conclusions may no longer hold. Another full review is warranted only when substantial rework makes the earlier assessment obsolete.

## Assess the change

- Does it implement the agreed behavior, including errors, edge cases, and partial failures?
- Are public contracts, domain invariants, validation, and data ownership preserved?
- Is I/O concentrated at clear boundaries, with core logic understandable independently?
- Are names, logical grouping, functions, and modules readable without unnecessary indirection or fragmentation?
- Do domain values retain meaning through named fields and appropriate types? Are idioms compatible with supported language versions?
- Are all changed responsibilities and dependencies necessary for the agreed scope?
- Do tests exercise meaningful behavior at the real boundary, with clear setup and assertions? Are they redundant or coupled to incidental implementation details?
- Are tooling changes justified? Are suppressions rare, narrow, and accompanied by a specific reason, including configuration-level exceptions?

Apply lighter style expectations to tests. Do not report an allowed test failure shortcut as a production-style violation. Distinguish a concrete readability problem from personal taste; identify the cost or contract at stake.

## Report findings

Read [the reviewer brief and finding format](references/reviewer-brief.md). Prioritize actionable, evidence-backed findings with precise file locations, a concrete trigger or readability cost, and the consequence. Suggest the smallest correction consistent with the plan.

Separate verified defects from uncertainty and optional ideas. Keep speculative future features outside required fixes. If the code reveals that the plan cannot be fulfilled within scope, report that conflict as a blocker instead of choosing new behavior.

If there are no actionable findings, say so and state any material coverage limitation. Do not manufacture a finding or an exhaustive file inventory to justify the review. Return the result to the implementing agent, which decides fixes, reruns checks, and prepares the user's final handoff.
