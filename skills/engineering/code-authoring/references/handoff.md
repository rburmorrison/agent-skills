# Final Handoff

`code-authoring`'s Handoff section defines the request line, the summary, the sections, and their format. This reference covers coverage, evidence, links, observed behavior, unverified work, choices, decisions, and examples.

Use simple wording: describe what happens before explaining how it works. Keep sentences short and explain unfamiliar terms only when needed.

## Coverage

Make each bold opening sentence a self-contained core point; put supporting explanation in regular text. Reading only the bold sentences should reveal the important guarantees, failure responses, and gaps.

An invariant is something always or never true after the change, for every input. A failure mode is what goes wrong, what the user sees, what state is left behind, and how to recover.

Cover every invariant and failure mode the plan named, in the plan's order, and mark any you add `(not in the plan)` in its subheading. Cover every consequential invariant and failure mode in the change; do not impose an item cap. Include details that affect correctness, user-visible behavior, compatibility, data integrity, recovery, or confidence in the change. Do not invent speculative failure catalogs or enumerate unrelated guarantees. Keep distinct guarantees visible rather than hiding them in a broad combined claim. Reduce repetition and unnecessary mechanics, not coverage.

Scale supporting detail to the change. Include entry points, internal names, data flow, and design reasons only when they help assess a claim or limitation. Do not require a numbered code tour or an inventory of changed files. For small changes, keep applicable sections brief and omit empty sections. For documentation-only changes, describe the guidance and its limits without inventing runtime behavior.

## Evidence and Links

For each consequential invariant or failure response, include a short fenced excerpt when available source directly shows the check, state change, error handling, or assertion supporting it. A source link alone does not replace that evidence. Put the block beneath the plain-language claim and explanation, followed by its verified source link. Use a language tag; do not substitute inline snippets.

Choose the smallest excerpt that supports the claim without hiding necessary context. Do not add decorative blocks, reproduce whole functions unnecessarily, or repeat the same evidence across sections. When a claim depends on a broader flow that no short excerpt explains, describe that flow briefly and link its relevant locations. Documentation-only changes need excerpts only when the wording itself helps assess the change. Copy source and output accurately; label omissions or illustrative material.

End each invariant and failure mode with an `**Exercised by:**` line naming the test or observed run that actually reached it, after the source link. Name a test only when it ran and its assertions cover the claim; a test that merely touches the same function does not count. Write `not exercised` when nothing did, and repeat that item under `## Not Verified`.

Before sending a code-change handoff with no fenced evidence, check whether the source contains a short excerpt that directly supports an important claim. If it does, include it. Omit blocks only when they would not provide meaningful evidence; never invent code or results to fill the format.

Every named code location must have a clickable Markdown source link with an absolute path and verified one-based line number. Link directly to the relevant implementation, contract, or test after all fixes. Use short descriptive labels, not directions to read or review code, and do not wrap links in backticks. Link changed guidance the same way when handing off documentation-only work.

Distinguish intended guarantees, source evidence, and observed results. Source inspection shows how a guarantee is implemented; an existing test is not evidence that it passed. Describe only what executed checks establish, and state limits beside claims when needed. Do not present desired behavior as an observed success.

## Observed Behavior

Show what happened when the change ran through the application's actual entry point: each command or action, followed by its output. Copy output verbatim, add no comments or annotations to it, and trim it only by cutting whole lines, marking each cut with `...`. Include a representative success and a relevant failure when both ran. Test, lint, and type results do not belong here; the summary gives them as one clause. Omit the section when the workflow could not run, and say so under `## Not Verified`. Never reconstruct output from memory or from what the code should print.

## Not Verified

Include this section only when something is unverified: a failed or skipped check, a `not exercised` item, a workflow that could not run, or blocked work. Give each gap a bold sentence naming what was not checked, then why, what could go wrong, and how to check it.

Do not claim checks passed unless they ran and support that claim. If blocked, clearly state that the task is incomplete, what independent work finished, what remains blocked, and what decision or capability is needed. A passing subset of checks does not complete blocked acceptance criteria.

## Choices Made Without Asking

List each choice you made where a reasonable alternative existed and the plan did not settle it, one line each: the choice, then its reason. Local variable names, syntax, and helper extraction the plan left to routine discretion do not belong. If writing an entry shows the choice changed behavior, scope, or a contract, it was not yours to make: put it under `## Decisions Awaiting You` instead.

## Decisions

A decision is a choice whose answer changes the code, documentation, or plan: a plan deviation needing approval, a fix you recommend but cannot make without approval, an unplanned documentation need, or a question blocking completion. Before listing an item, ask: if the user accepts my recommendation, will I change something? If not, drop it; this removes suggestions you recommend against, minor wording within specified behavior, and anything you can resolve within the plan. A plan deviation you already made is the exception: always list it, even when you recommend keeping it, because the user has not agreed to it.

## Example

This example uses fictional paths, line numbers, test names, and results. Replace them with verified locations and actual evidence; never copy its links or claims into a handoff unchanged.

````markdown
You asked: Make `catalog import` update existing identifiers and apply each file completely or not at all.

**CSV imports now validate the whole file before saving records.** Invalid input cannot leave a partially imported dataset. Formatting, lint, type checks, and tests passed, and the planned README sentence was updated. Connection loss during commit is not verified.

---

## Invariants

### All-or-Nothing Writes

**An import saves every validated entry or saves nothing.** The read, the inserts, and the updates share one transaction.

```python
with self.transaction(immediate=True) as transaction:
    plan = plan_import(transaction.read_all(), entries)
    apply_plan(transaction, plan)
```

**Source:** [Import Transaction](/absolute/project/src/catalog/store.py:84)

**Exercised by:** `test_update_failure_after_insert_rolls_back`.

### Validation Before Storage

**No storage read or write happens until the whole file has validated.** The command validates every row first, and an error returns before the store is opened.

```python
entries = validate_catalog(parse_catalog(text))
result = store.import_catalog(entries)
```

**Source:** [Import Command](/absolute/project/src/catalog/cli.py:52)

**Exercised by:** `test_duplicate_row_exits_2_without_writes`.

### Each Identifier Counted Once

**Every input identifier is counted exactly once, as inserted or as updated.** The counts are the sizes of the two halves of the plan.

```python
return ImportResult(len(plan.inserts), len(plan.updates))
```

**Source:** [Import Result](/absolute/project/src/catalog/store.py:91)

**Exercised by:** `test_unchanged_title_counts_as_updated` and the first run under Observed Behavior.

---

## Failure Modes and Recovery

### Invalid Input

**An invalid row stops the import before any writes.** The command exits 2 and names the row, so the user can correct the file and rerun it.

**Source:** [Input Validation](/absolute/project/src/catalog/importer.py:71)

**Exercised by:** `test_duplicate_row_exits_2_without_writes` and the second run under Observed Behavior.

### Storage Failure

**A failure during the read or a write rolls back the import.** Existing entries remain unchanged, the command exits 1, and the user reruns the same file.

**Source:** [Import Transaction](/absolute/project/src/catalog/store.py:84)

**Exercised by:** `test_update_failure_after_insert_rolls_back`.

### Connection Loss During Commit (not in the plan)

**If the connection drops during commit, the command reports a storage failure without knowing whether the commit landed.**

**Source:** [Import Transaction](/absolute/project/src/catalog/store.py:84)

**Exercised by:** not exercised.

---

## Observed Behavior

```console
$ uv run catalog import changes.csv --db catalog.db
Inserted 1; updated 1
$ uv run catalog import duplicate.csv --db catalog.db
row 3: duplicate identifier 'gamma'; first seen at row 2
$ uv run catalog list --db catalog.db
identifier,title
alpha,Revised
beta,New
```

---

## Not Verified

**Connection loss during commit was not tested.** No check simulates it. If the commit landed but the command reported failure, a rerun would report every entry as updated. To check, drop the adapter's connection during commit in a storage test and rerun the import.

---

## Choices Made Without Asking

- Forced the rollback test's failure by making the second update raise through the existing adapter fixture, not by simulating a full disk, because the fixture already injects errors inside a real transaction.
- Took duplicate positions from `InputRow.row_number` instead of recounting rows, so both kinds of error number rows the same way.

---

## Decisions Awaiting You

1. **Trailing blank records.** The plan does not say what a blank final line does, and the parser currently rejects it as a short row. Skipping it would accept files exported by common spreadsheet tools; rejecting it keeps the header-and-records rule strict. Recommendation: skip a single trailing blank line, because it carries no data and the rejection message confuses users.
````

## Small Change Example

Scale the structure down for small changes; omit empty sections. This example is fictional, like the one above: the paths, line numbers, test names, and results are illustrative.

````markdown
You asked: Make `report --since DATE` include entries dated exactly on DATE.

**`report --since DATE` now includes entries dated exactly on DATE.** The help text and README already described the bound as inclusive; the code excluded it. Lint, type checks, and tests passed; no documentation updates were needed.

---

## Invariants

### Inclusive Lower Bound

**An entry dated on the `--since` date appears in the report.** The filter compares with `>=`.

```python
return [entry for entry in entries if entry.date >= since]
```

**Source:** [Date Filter](/absolute/project/src/tracker/report.py:37)

**Exercised by:** `test_entry_on_since_date_is_included` and the run below.

**No new failure mode was introduced.** Invalid dates and the no-bound path are unchanged.

---

## Observed Behavior

```console
$ uv run tracker report --since 2026-03-01 --db tracker.db
2026-03-01  Draft outline
2026-03-02  Review outline
```
````
