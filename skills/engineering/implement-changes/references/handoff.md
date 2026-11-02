# Final handoff

Start with plain sentences explaining what changed, why, and the useful parts of the approach. Avoid obligatory "Recap:" and "Human review:" prefixes. Scale the response to the work.

Recommend human review only for decisions that benefit from judgment: consequential behavior, contracts, architectural tradeoffs, or unresolved uncertainty. Prioritize a small number of useful locations. Do not enumerate every changed file or send the user through routine plumbing.

Use a table when it helps scanning:

| Location | Decision to inspect |
| --- | --- |
| Clickable file name and verified line | The specific behavior or tradeoff worth the user's attention |

Replace the illustrative cells with actual locations and decisions. Link to local files using an absolute path and one-based line, for example `[import.py:84](/absolute/project/import.py:84)`. Verify every path and line after all fixes; never copy the illustrative path or invent a link. Include enough path context in labels to distinguish duplicate file names. Link directly to the smallest useful function, branch, or contract.

It is acceptable to say that no targeted human review is recommended when the change is routine and the evidence supports that judgment. Omit the table in that case. Do not claim all checks or independent review passed unless they actually ran and their results support the claim.

Summarize the important behavioral commitments established by tests, the relevant checks run, and material verification limitations. Group related cases; avoid a test-function inventory. Mention significant independent review findings and their resolution when useful. Always surface unresolved findings.

If blocked, clearly state that the task is incomplete, what independent work was finished, what remains blocked, and what decision or capability is needed. A passing subset of tests does not make blocked acceptance criteria complete.

Example prose, to adapt only when supported by the actual change and evidence:

> Added CSV import with validation before database writes, so malformed input cannot leave a partially imported catalog. The existing transaction boundary handles inserts and updates together.
>
> Tests cover valid inserts and updates, row-specific validation errors, and rollback after a storage failure. Formatting, linting, type checking, and the affected tests passed. Independent review found an error-propagation issue; it was fixed and the affected checks passed again.

Add targeted local review links only if they help the user assess a meaningful decision. Avoid unnecessary sections, context, or implementation narration.
