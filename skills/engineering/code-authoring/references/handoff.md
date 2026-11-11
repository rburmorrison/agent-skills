# Final Handoff

Start with a short paragraph explaining what changed and why. Put any verification gap that materially affects confidence near the beginning, especially when the change has not been executed. Use simple wording: describe what happens before explaining how it works. Keep sentences short and explain unfamiliar terms only when needed.

## Structure And Coverage

Use these section headings, with clear spacing between sections:

- **Invariants**: guarantees the change establishes or preserves.
- **Failure Modes And Recovery**: relevant ways the changed behavior can fail, what the user or caller sees, what state remains, and how recovery works or where it stops.
- **Verification And Remaining Uncertainty**: checks actually run, observed workflow results, and anything still unverified or incomplete.

Use the example below as the default layout. Put a horizontal rule (`---`) before each major section, separating the opening summary from Invariants and separating subsequent sections. Give each distinct invariant and failure mode its own short, plain-language subheading (`###`). Bold the first sentence of each item or standalone paragraph, including the opening summary. Make that sentence a self-contained core point; put supporting explanation in regular text. Reading only the bold sentences should reveal the important guarantees, failure responses, and gaps.

Cover every consequential invariant and failure mode in the change; do not impose an item cap. Include details that affect correctness, user-visible behavior, compatibility, data integrity, recovery, or confidence in the change. Do not invent speculative failure catalogs or enumerate unrelated guarantees. Keep distinct guarantees visible rather than hiding them in a broad combined claim. Reduce repetition and unnecessary mechanics, not coverage.

Scale supporting detail to the change. Keep explanations brief, but retain the evidence needed to assess each claim under Evidence And Links below. Include entry points, internal names, data flow, and design reasons only when they help assess a claim or limitation. Do not require a numbered code tour or an inventory of changed files. For small changes, keep applicable sections brief and omit empty sections. For documentation-only changes, describe the guidance and its limits without inventing runtime behavior.

## Evidence And Links

For each consequential invariant or failure response, include a short fenced excerpt when available source directly shows the check, state change, error handling, or assertion supporting it. A source link alone does not replace that evidence. Put the block beneath the plain-language claim and explanation, followed by its verified source link. Use a language tag; do not substitute inline snippets.

Choose the smallest excerpt that supports the claim without hiding necessary context. Do not add decorative blocks, reproduce whole functions unnecessarily, or repeat the same evidence across sections. When a claim depends on a broader flow that no short excerpt explains, describe that flow briefly and link its relevant locations. Documentation-only changes need excerpts only when the wording itself helps assess the change. Copy source and output accurately; label omissions or illustrative material.

Before sending a code-change handoff with no fenced evidence, check whether the source contains a short excerpt that directly supports an important claim. If it does, include it. Omit blocks only when they would not provide meaningful evidence; never invent code or results to fill the format.

Every named code location must have a clickable Markdown source link with an absolute path and verified one-based line number. Link directly to the relevant implementation, contract, or test after all fixes. Use short descriptive labels, not directions to read or review code, and do not wrap links in backticks. Link changed guidance the same way when handing off documentation-only work.

Distinguish intended guarantees, source evidence, and observed results. Source inspection shows how a guarantee is implemented; an existing test is not evidence that it passed. Describe only what executed checks establish, and state limits beside claims when needed. Do not present desired behavior as an observed success.

## Verification And Incomplete Work

Prefer a verification table when several behaviors map clearly to evidence and results or gaps. Use columns such as **Behavior**, **Evidence**, and **Result Or Gap**; adapt them to the information. Link relevant test or source locations in the evidence column, and distinguish passed checks from inspected-but-unrun tests. Keep cells brief and put longer explanations outside the table. Use prose when there is only one check or when the information does not form a useful mapping. Do not force a table, repeat the same coverage in prose, or use a table as a substitute for evidence blocks in the earlier sections.

Summarize important behavior checked by tests separately from the actual user workflow exercised and its visible results or state changes. If the workflow did not run, say why and what remains unverified. Group related cases instead of listing every test function or command; do not repeat evidence already attached to an item. State whether planned documentation was updated, no update was needed, or an unplanned need awaits a decision. Mention significant independent review findings and their resolution when useful; always surface unresolved findings. Do not claim checks or independent review passed unless they ran and support that claim.

If blocked, clearly state that the task is incomplete, what independent work finished, what remains blocked, and what decision or capability is needed. A passing subset of checks does not complete blocked acceptance criteria.

## Example

This example uses fictional paths, line numbers, and results. Replace them with verified locations and actual evidence; never copy its links or claims into a handoff unchanged.

````markdown
**CSV imports now validate the whole file before saving records.** Invalid input cannot leave a partially imported dataset.

**Connection loss during commit remains unverified.** If the commit outcome is unknown, these checks do not establish whether retrying is safe.

---

## Invariants

### All-Or-Nothing Writes

**An import saves every validated record or saves nothing.** All writes share one transaction.

```python
with transaction.atomic():
    save_records(validated_rows)
```

**Source:** [Import Transaction](/absolute/project/catalog/importer.py:84)

---

## Failure Modes And Recovery

### Invalid Input

**An invalid row stops the import before any writes.** The error identifies the row and field so the user can correct the file and retry.

```python
validated_rows = validate_rows(rows)
save_in_transaction(validated_rows)
```

**Source:** [Input Validation](/absolute/project/catalog/importer.py:71)

### Storage Failure

**A write failure before commit rolls back the import.** Existing records remain unchanged, and the command reports that the import failed.

**Source:** [Import Transaction](/absolute/project/catalog/importer.py:84)

---

## Verification And Remaining Uncertainty

**Tests and CLI checks confirmed the main import behaviors.** Connection loss during commit remains outside the executed checks.

| Behavior | Evidence | Result Or Gap |
| --- | --- | --- |
| Invalid rows leave stored records unchanged | [Validation Test](/absolute/project/tests/test_importer.py:42) | Passed |
| Write failures before commit roll back the import | [Rollback Test](/absolute/project/tests/test_importer.py:68) | Passed |
| Valid and invalid files work through the CLI | Disposable imports and database inspection | Valid file saved expected records; invalid final row left records unchanged |
| Connection loss during commit | No executed check | Retry safety remains unverified |

**No usage-documentation updates were needed.** Existing instructions remain accurate.
````
