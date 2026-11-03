---
name: implement-verified-steps
description: Implement an agreed plan through distinct steps with checks and one independent review per step. Use only when explicitly requested, with targeted follow-up only for concrete unresolved risks.
---

# Implement Verified Steps

Use only when explicitly invoked or when the user explicitly requests this workflow. It is available for any model; do not infer model capability or change model selection. This workflow replaces the usual review cadence for the task. Reuse `plan-changes`, `implement-changes`, and `review-changes` for their shared policies rather than adding a separate coding standard. Disclose unavailable supporting skills or reviewer capability.

## Set the Checkpoints before Implementation

Use the agreed plan and decisions, including after a model switch. If meaningful steps are missing, complete planning with `plan-changes` before editing. Resolve consequential questions one at a time during planning; do not restart the interview between implementation steps.

Each step must state its coherent responsibility, affected operations and contracts, dependencies, acceptance criteria, and relevant checks. Choose meaningful, verifiable checkpoints rather than a step for every file, function, or edit. A small task may need only one step. Identify final integration checks and what the final step's review must assess across the completed work.

Record the requested review cadence and other overrides in the plan. Keep a compact progress record in the conversation: completed steps, the state reviewed, check results, finding dispositions, and remaining work. Create a progress file only when requested or required by the project. Carry this record through model switches; do not repeat completed reviews solely because the model changed.

## Complete One Step at a Time

1. Implement the current step using `implement-changes`, within the agreed scope.
2. Run its relevant checks. Confirm that tests exercise the claimed behavior and failure boundary; an earlier failure must not masquerade as proof of a later error path.
3. Obtain one independent review of the step using `review-changes`. Start the reviewer with fresh context (`fork_turns="none"` where supported). Supply the overall plan, current step and its starting/reviewed state, actual changes including new files, relevant surrounding contracts, and check results. Mark planned future work so it is not mistaken for a current defect. Use the task's reviewer model or normal inheritance; do not silently upgrade it.
4. Assess findings, fix validated issues within scope, and rerun affected checks. Resolve optional suggestions against the agreed requirements rather than accumulating cleanup work.
5. Finish the step when validated findings are resolved and required checks pass. Record any material verification limitation accurately, then continue automatically. Do not ask for approval between agreed steps.

## Keep Reviews Bounded

The default is one independent review per planned step. Fixing findings does not automatically require another review. Extra confidence, cosmetic changes, or the mere existence of edits are not sufficient reasons for a new pass.

Request a follow-up only when a material fix leaves a concrete risk that the existing review and checks do not cover. Before requesting it, state: "This fix changed X. Y remains unverified. The follow-up will check Z." Keep that review targeted to the risk and affected paths. A repeated full review is exceptional and requires substantial rework that invalidated the earlier assessment.

Do not run a "review until no findings" loop. Repeated concerns without new evidence should be resolved against the agreed contracts. If a material issue cannot be resolved within the agreed scope or available capabilities, mark the affected work incomplete, finish useful independent work, and report the blocker at the end. Do not advance dependent work as if a blocked checkpoint passed.

If later edits affect a completed step, rerun affected checks and reassess only the review conclusions those edits invalidate. Apply the same concrete-risk criterion before requesting another reviewer.

## Finish

Use the final step's review to assess integration with the completed steps, then complete the planned final checks. Do not automatically append another full-project review. If a required check or independent review was unavailable, follow the shared fallback and disclose the limitation; never mark it as performed or passed.

Use the standard concise handoff. Summarize the important behavior established, verification, and any unresolved work. Report the number of step reviews and any follow-ups with their reasons, without dumping every command or repeating the full progress record.
