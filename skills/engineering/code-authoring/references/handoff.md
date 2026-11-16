# Final Handoff

`code-authoring`'s Handoff section defines the summary, the sections, and their format. This reference covers coverage, evidence, links, verification detail, decisions, and examples.

Use simple wording: describe what happens before explaining how it works. Keep sentences short and explain unfamiliar terms only when needed.

## Coverage

Make each bold opening sentence a self-contained core point; put supporting explanation in regular text. Reading only the bold sentences should reveal the important guarantees, failure responses, and gaps.

Cover every consequential invariant and failure mode in the change; do not impose an item cap. Include details that affect correctness, user-visible behavior, compatibility, data integrity, recovery, or confidence in the change. Do not invent speculative failure catalogs or enumerate unrelated guarantees. Keep distinct guarantees visible rather than hiding them in a broad combined claim. Reduce repetition and unnecessary mechanics, not coverage.

Scale supporting detail to the change. Include entry points, internal names, data flow, and design reasons only when they help assess a claim or limitation. Do not require a numbered code tour or an inventory of changed files. For small changes, keep applicable sections brief and omit empty sections. For documentation-only changes, describe the guidance and its limits without inventing runtime behavior.

## Evidence and Links

For each consequential invariant or failure response, include a short fenced excerpt when available source directly shows the check, state change, error handling, or assertion supporting it. A source link alone does not replace that evidence. Put the block beneath the plain-language claim and explanation, followed by its verified source link. Use a language tag; do not substitute inline snippets.

Choose the smallest excerpt that supports the claim without hiding necessary context. Do not add decorative blocks, reproduce whole functions unnecessarily, or repeat the same evidence across sections. When a claim depends on a broader flow that no short excerpt explains, describe that flow briefly and link its relevant locations. Documentation-only changes need excerpts only when the wording itself helps assess the change. Copy source and output accurately; label omissions or illustrative material.

Before sending a code-change handoff with no fenced evidence, check whether the source contains a short excerpt that directly supports an important claim. If it does, include it. Omit blocks only when they would not provide meaningful evidence; never invent code or results to fill the format.

Every named code location must have a clickable Markdown source link with an absolute path and verified one-based line number. Link directly to the relevant implementation, contract, or test after all fixes. Use short descriptive labels, not directions to read or review code, and do not wrap links in backticks. Link changed guidance the same way when handing off documentation-only work.

Distinguish intended guarantees, source evidence, and observed results. Source inspection shows how a guarantee is implemented; an existing test is not evidence that it passed. Describe only what executed checks establish, and state limits beside claims when needed. Do not present desired behavior as an observed success.

## Verification and Incomplete Work

Do not claim checks passed unless they ran and support that claim. If blocked, clearly state that the task is incomplete, what independent work finished, what remains blocked, and what decision or capability is needed. A passing subset of checks does not complete blocked acceptance criteria.

## Decisions

A decision is a choice whose answer changes the code, documentation, or plan: a plan deviation needing approval, a fix you recommend but cannot make without approval, an unplanned documentation need, or a question blocking completion. Before listing an item, ask: if the user accepts my recommendation, will I change something? If not, drop it; this removes suggestions you recommend against, minor wording within specified behavior, and anything you can resolve within the plan.

## Example

This example uses fictional paths, line numbers, and results. Replace them with verified locations and actual evidence; never copy its links or claims into a handoff unchanged.

````markdown
**CSV imports now validate the whole file before saving records.** Invalid input cannot leave a partially imported dataset.

**Connection loss during commit remains unverified.** If the commit outcome is unknown, these checks do not establish whether retrying is safe.

---

## Invariants

### All-or-Nothing Writes

**An import saves every validated record or saves nothing.** All writes share one transaction.

```python
with transaction.atomic():
    save_records(validated_rows)
```

**Source:** [Import Transaction](/absolute/project/catalog/importer.py:84)

---

## Failure Modes and Recovery

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

## Verification and Remaining Uncertainty

**Formatting, lint, type checks, tests, and the CLI import workflow passed; no documentation updates were needed.**

**Connection loss during commit was not tested.** No check simulates it, so retry safety after an unknown commit outcome is unverified.

---

## Decisions Awaiting You

1. **Duplicate keys within one file.** The plan does not say what a repeated key does, and the code currently keeps the last row. Rejecting the file would report the duplicate and save nothing; keeping the last row would silently drop the earlier one. Recommendation: reject the file, because other invalid rows already reject it and a silent overwrite could hide a data-entry mistake.
````

## Small Change Example

Scale the structure down for small changes; omit empty sections. This example is fictional, like the one above: the paths, line numbers, and results are illustrative.

````markdown
**`report --since DATE` now includes entries dated exactly on DATE.** The help text and README already described the bound as inclusive; the code excluded it.

---

## Invariants

### Inclusive Lower Bound

**An entry dated on the `--since` date appears in the report.** The filter compares with `>=`.

```python
return [entry for entry in entries if entry.date >= since]
```

**Source:** [Date Filter](/absolute/project/src/tracker/report.py:37)

**No new failure mode was introduced.** Invalid dates and the no-bound path are unchanged.

---

## Verification and Remaining Uncertainty

**Tests, including a new boundary test, and the `report --since` CLI check passed; no documentation updates were needed.**
````
