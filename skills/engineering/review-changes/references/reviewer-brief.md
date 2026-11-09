# Reviewer Brief

Start the reviewer without inheriting the implementation conversation. The implementing agent should supply this brief instead:

- The requested outcome, agreed plan, decision record with reasons and agreement, documentation change map, remaining implementation discretion, and exclusions.
- The repository or workspace location and an unambiguous base and current state, including new files.
- Relevant interfaces and source locations needed to understand the change.
- Checks actually run, their results, and known limitations; distinguish tests from actual user-workflow execution and observed application state.
- For a follow-up, the original finding, the fix, and affected paths.

Do not include a desired verdict or instruct the reviewer to confirm the implementer's reasoning. Review the evidence independently. A reviewed diff must correspond to the final state being handed off, or the later edits must receive appropriate verification.

## Finding Format

For each actionable finding, provide:

1. A short title and appropriate priority.
2. A verified file path and the smallest useful line location.
3. The input, condition, or maintenance task that exposes the issue.
4. The resulting failure, contract violation, or concrete comprehension cost.
5. The smallest in-scope correction or the decision that is blocked.

Keep findings concise. Explain one issue per finding. Avoid generic advice such as "improve error handling" without identifying the missing behavior and its consequence.

Example finding content:

> A storage error after the first update leaves that update committed. The agreed import contract requires the whole batch to roll back. Route the batch through the existing transaction operation and exercise an error after at least one write.

The actual report must attach the verified code location; this example deliberately supplies no fictional file link.

Finish with a short coverage statement and any unresolved uncertainty. Test results and source inspection are distinct evidence; do not claim to have executed a check based solely on an implementer's report.
