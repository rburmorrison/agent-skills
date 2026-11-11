# Final Handoff

Start with a short paragraph explaining what changed and why. Put any verification gap that materially affects confidence near the beginning, especially when the change has not been executed. Use simple wording: describe what happens before explaining how it works. Keep sentences short and explain unfamiliar terms only when needed.

## Structure And Coverage

Use these section headings, with clear spacing between sections:

- **Invariants**: guarantees the change establishes or preserves.
- **Failure Modes And Recovery**: relevant ways the changed behavior can fail, what the user or caller sees, what state remains, and how recovery works or where it stops.
- **Verification And Remaining Uncertainty**: checks actually run, observed workflow results, and anything still unverified or incomplete.

Give distinct items short descriptive subheadings when that helps scanning. Bold the first sentence of each item or standalone paragraph, including the opening summary. Make that sentence a self-contained core point; put supporting explanation in regular text. Reading only the bold sentences should reveal the important guarantees, failure responses, and gaps. Use section dividers when they help readers see where longer sections end.

Cover every consequential invariant and failure mode in the change; do not impose an item cap. Include details that affect correctness, user-visible behavior, compatibility, data integrity, recovery, or confidence in the change. Do not invent speculative failure catalogs or enumerate unrelated guarantees. Keep distinct guarantees visible rather than hiding them in a broad combined claim. Reduce repetition and unnecessary mechanics, not coverage.

Scale supporting detail to the change. A straightforward item may need only a sentence and a source link; a subtle guarantee may need an explanation and evidence. Include entry points, internal names, data flow, and design reasons only when they help assess a claim or limitation. Do not require a numbered code tour or an inventory of changed files. For small changes, keep applicable sections brief and omit empty sections. For documentation-only changes, describe the guidance and its limits without inventing runtime behavior.

## Evidence And Links

Attach evidence to the claim it supports. Use short fenced code blocks with a language tag for source excerpts, assertions, or command output when they make the claim easier to assess. Do not use inline snippets for evidence, force a block into every item, or repeat the same evidence in several sections. Copy source and output accurately; label omissions or illustrative material. Include enough context to avoid making an excerpt appear to prove more than it does.

Every named code location must have a clickable Markdown source link with an absolute path and verified one-based line number. Link directly to the relevant implementation, contract, or test after all fixes. Use short descriptive labels, not directions to read or review code, and do not wrap links in backticks. Link changed guidance the same way when handing off documentation-only work.

Distinguish intended guarantees, source evidence, and observed results. Source inspection shows how a guarantee is implemented; an existing test is not evidence that it passed. Describe only what executed checks establish, and state limits beside claims when needed. Do not present desired behavior as an observed success.

## Verification And Incomplete Work

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

**Tests passed for valid input, invalid rows, and rollback after a write failure.** The CLI also imported a valid disposable file and rejected an invalid final row without changing stored records.

**No usage-documentation updates were needed.** Existing instructions remain accurate.
````
