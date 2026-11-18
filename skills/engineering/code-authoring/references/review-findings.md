# Handling Review Findings

Read this when the independent review returns. `code-authoring`'s Independent Review section owns when to review and how to start the reviewer.

## Which Findings to Fix

- Assess each finding against the code before acting on it.
- Fix validated Blocker and Should-fix findings within scope, and rerun affected checks.
- Fix a validated Nit only when all of these hold:
  - the fix touches only lines this change already modifies;
  - it changes no behavior or test expectations;
  - it needs no new file, dependency, or user decision.
- Applying a Nit that fails any condition is out of scope, however small or worthwhile it seems. Raise any other Nit you recommend making as a decision in the handoff, and drop the rest.
- Nits never block completion.

## When to Review Again

- Request a targeted follow-up autonomously only when a material change to logic, interfaces, or component interactions leaves a concrete risk uncovered by the existing review and checks. State that risk and the follow-up scope before requesting it.
- A second full review of the same scope is exceptional and appropriate when substantial rework invalidates the first review.
- Resolved findings and passing required checks normally finish the review. Do not seek repeated clean verdicts or leave a known defect unaddressed solely to satisfy a round count.
