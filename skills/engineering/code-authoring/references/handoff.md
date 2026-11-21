# Final Handoff

`code-authoring`'s Handoff section names the parts of a handoff. This reference explains what each part is for, how to scale them, and what good ones look like.

## What the Handoff Is For

The reader owns the project and is a capable engineer, but did not watch the work and may not have the code open. The handoff exists to give them a technical understanding of the change: how the code works now, why it is worth having, what it costs, and where it might be wrong.

Test a draft this way: pick an input or situation the handoff does not mention, and ask whether the text alone settles what the code does with it. If it does, the handoff explains the change. If it does not, the handoff only reports on it.

Explain the program; do not let an account of your own activity stand in for that. Plan items ticked off, lists of files touched, and guarantees restated as though restating proved them say what the agent did, not how the code behaves. Saying what you ran and what you saw is different: that is evidence, and Verification depends on it.

Use simple wording: describe what happens before explaining how it works. Keep sentences short and explain unfamiliar terms only when needed.

## Scale to the Change

Size the handoff by the number of distinct ideas in the change, not by its line count. A one-idea change gets a paragraph even when its diff is mostly tests. A rename or a move gets two sentences.

Three sizes cover most changes:

- A tiny change is one idea, even when it touches two coupled lines. It has no headings: the opening sentence, the summary, the excerpt that matters, and a few closing sentences on verification, value, and cost. For a tiny bug fix, the before and after fit in a sentence or two. If one decision awaits the user, the change is still tiny: end with `## Decisions Awaiting You` and its one item, and add no other heading. Everything else folds into sentences: a side effect, a doubt, and what was not run each get one. Use one short `console` block when the output itself is the evidence, as with a failure you reproduced; otherwise describe the run in a sentence. Leave out probes that passed.
- A middling change is two or three ideas. Use the `##` headings that have content and no subheadings. Keep How It Works to a paragraph or two per idea. Under Value and Cost, write one short paragraph on the value and one on the cost.
- A larger change uses the full shape, with a subheading per piece.

Size the handoff by the change. A problem you found beside it, or a decision it raises, does not move it up a size.

Leave out any part with nothing to say, except the cost, which is always stated. The prediction test has a stopping point. State the rule the code follows and one or two cases that show its edges; do not list every form it accepts, which is what the tests are for.

## A Problem You Found

Writing the handoff often turns up something: a case that fails, a missing test, a doubt worth running. If the fix is within the agreed scope, go back and make it, then write the handoff about the finished work, saying in a clause what you added. A test is missing when the changed behavior has a case that no test reaches; a neighboring case is something to mention under Verification, not a reason to widen the work. If it needs the user's decision, give it exactly one home:

- A defect or gap you recommend fixing goes under `## Decisions Awaiting You`, with the evidence there. The summary names it in a clause, and no other section restates it.
- A confirmed problem you recommend leaving goes first under What It Costs, saying whether this change created it or it was already there.
- Something that might be wrong, but that you could not confirm, goes under `## Where I Would Aim Doubt`.

Elsewhere, refer to the item in a few words instead of repeating it.

Code that detects things by pattern will always miss some forms. Describe what it does not catch as a class under What It Costs, not as a list. A wrong result on valid input is different: that is a defect, and it follows the rules above.

With no plan, the scope is the request as the user would read it. The same symptom from a different trigger is a neighboring problem: raise it as a decision instead of widening the fix. If you cannot make an in-scope fix, say so and treat it as a decision.

A side effect is different from a problem. When the change alters behavior the user did not ask about, give it its own sentence in How It Works, and name it in the summary if a user would notice it.

For a documentation-only change, describe the guidance and its limits without inventing runtime behavior.

## The Opening

Start with one ordinary sentence that restates the goal in the user's terms, beginning `You wanted`. Take it from the plan's goal sentence and rephrase only as far as grammar needs: "Make `report --since` include the boundary date" becomes "You wanted `report --since DATE` to include entries dated exactly on DATE." With no plan, restate the request. This lets the reader see at once whether the goal was understood.

Follow it with a short summary paragraph with no heading or label. Its first sentence is bold and states the mechanism: what the code now does differently and where, not only the outcome. "The player now picks an input mode before each command" tells the reader where to look; "commands no longer hang" does not. When the change has two halves, one bold sentence may name both, but keep it to what a reader can hold at once. Then say what that achieves, and give the results of the project's checks and whether usage documentation changed or needed to, as one clause. The project's checks are the ones its CI configuration or task runner defines; name any you did not run. The clause can be bare, as in "lint, type checks, and tests passed". Total test counts add nothing, so leave them out of the handoff unless a failure makes them matter. End by naming any decision that awaits the user and any gap that affects confidence, such as a platform you could not run on, since those are what the reader most needs to act on. Say nothing when there is none. A reader who stops here must not be misled.

## How It Works

This is the core of the handoff. Explain the change as you would at a whiteboard, following the order the code runs. A piece is an idea, not a file or a function. Give each one a subheading named after what it does, then say what it does now, how it connects to the next piece, and why it is built that way. Fold a piece that needs only a sentence into its neighbor.

Guarantees and failure handling belong in the sentence that explains the mechanism producing them: "the read and both writes share one transaction, so a failed update rolls back the inserts." Do not collect them into a separate catalog.

Include the facts a reader needs to reason about cases you did not cover: which existing mechanism the change reuses, what state it adds, what it deliberately leaves alone, existing behavior the reader might assume it fixed, and the units behind any number. "Limits of 500 and 1000" explains nothing; "500 nested items and 1000 syntax levels" does.

When the work departed from the plan, say where and why. Agreement with the plan is the default and needs no mention.

For a sprawling change, open this section with a sentence or two on reading order: which piece carries the decision, and which parts are mechanical.

## Before and After

For a bug fix, or any piece that changes existing behavior, open How It Works with one real input traced through the old code and the new code, to the point where they diverge. Use the same input on both sides. A small table works well when the steps line up:

| Step | Before | After |
| --- | --- | --- |
| The step, named plainly | What the old code did | What the new code does |

Use prose instead when a cell would need a sentence of explanation. Keep the trace to the steps: when the same input is also your verification run, show its output once, under Verification.

State the behavior, not the edit: "a file with a 2000-arm else-if chain was left unanalyzed and is now analyzed", not "changed `parse`". Say whether each side was observed or only read. Run the old code when that is cheap; seeing the failure happen is the most convincing evidence a fix can have. Wholly new behavior has no before, and a refactor has no difference to show, so neither needs this part.

## Value and Cost

Under `### What It Adds`, say who benefits, in what situation, and how much. Be honest when the answer is "rarely" or "a little", and say when how often is your estimate. If this is hard to write, say so; the change may not have been worth making.

Under `### What It Costs`, open with a sentence that sizes the technical debt the change adds as none, small, moderate, or significant. Small debt is local: someone working in that code will see it. Moderate debt is something a future change elsewhere must know about, or a known gap left open. Significant debt constrains the design or will need paying down. Then list each item as a plain sentence: new state, a second way of doing something, a special case, a hard-coded value, a known gap left open, or something a future change must remember. Always state the cost, even when it is none, because that is a claim the reader wants made. List only what someone working on this code later would need to know; a sentence is enough when the debt is small.

A tiny change covers both in a few sentences with no headings, and a middling change in two short paragraphs with no subheadings.

## Verification

Show what happened when the change ran through the application's actual entry point: each command or action, followed by its output in a `console` block. Copy output verbatim and trim it only by cutting whole lines, marking each cut with `...`. Terminal escape codes may be stripped; say so when they are. When output is long and its content is not the point, cut it down to the lines that matter, or describe it in a sentence. Include a representative success and a relevant failure when both ran. Never reconstruct output from memory or from what the code should print.

Say what the run was given: the contents of any input file the reader cannot see, in a sentence. The command line may be simplified when you describe what was left off, such as a timeout or a filter. Say how the run differs from real use when that matters, for example input piped in where a person would type. An exit status, or a run that hung and had to be killed, has no output to quote, so state it in a sentence.

Then say, in sentences, how each remaining fact is known: you ran it and saw this, a named test asserts this, or you read the code and believe this. A bare "tests pass" belongs in the summary. Here, name the test that covers the changed behavior and, where it matters, what that test would not catch. Cases already stated in How It Works need no second listing; one sentence saying they were each run or are asserted by the named tests is enough.

Say plainly what was not checked: a failed or skipped check, a workflow that could not run, or an old behavior you did not reproduce. An existing test is not evidence that it passed, and passing tests are not evidence that an unexecuted workflow works.

When the plan named guarantees or failure cases, mention one here only when it is unmet, untested, or different from the plan.

If the work is blocked, state clearly that the task is incomplete, what independent work finished, what remains blocked, and what decision or capability is needed. A passing subset of checks does not complete blocked acceptance criteria.

## Where I Would Aim Doubt

List, in order, the places you would look first if this change turned out to be wrong, each with why. Say in the sentence itself how far each was checked: ran, tested, covered only indirectly, or read only. When flagging a problem, say whether this change created it, exposed it, or only passed by it.

Doubt and debt are different. Doubt is "this might be wrong". Debt is "this is right, but it costs something later". A doubt that came from reading can be wrong when run, so run it when that is cheap. Once it is confirmed it is no longer a doubt; A Problem You Found says where it goes.

List only real observations. A doubt you ran and cleared is no longer a doubt; mention what you probed in a sentence under Verification. Before omitting the section, ask what kind of input or situation you did not try, and name it if there is one. Omit the section when there is nothing to list.

## Choices Made Without Asking

List each choice you made where a reasonable alternative existed and the plan did not settle it, one line each: the choice, then its reason. Local variable names, syntax, and helper extraction the plan left to routine discretion do not belong. With no plan, list only a choice the user might well have made differently, and do not repeat design that How It Works already explains. If writing an entry shows the choice changed behavior, scope, or a contract, it was not yours to make: put it under `## Decisions Awaiting You` instead.

## Decisions Awaiting You

A decision is a choice whose answer changes the code, documentation, or plan: a plan deviation needing approval, a fix you recommend but cannot make without approval, an unplanned documentation need, or a question blocking completion. Before listing an item, ask: if the user accepts my recommendation, will I change something? If not, drop it; this removes suggestions you recommend against, minor wording within specified behavior, and anything you can resolve within the plan. A plan deviation you already made is the exception: always list it, even when you recommend keeping it, because the user has not agreed to it.

Number each item. Give it a bold title naming the choice, then the current state, what each option would change, and your recommendation with its reason.

## Excerpts and Links

Use a code excerpt where the code is the clearest explanation: the few lines where the decision lives. One or two per piece is usually enough. Do not recap the diff or reproduce whole functions. Use a fenced block with a language tag, copy source accurately, and label omissions.

Link the places where the change lives, each once, as a Markdown link with an absolute path and a one-based line number that you checked after all fixes. A test named in code font needs no link, and neither does an identifier named in passing. Use short descriptive labels, not directions to read or review code. A label may be a name in code font, but do not wrap the whole link in backticks. Link changed guidance the same way for documentation-only work.

## Formatting

Write in sentences. Do not prefix lines with labels such as `Value:`, `Tested:`, or `Source:`; say the same thing as a sentence, and let a subheading carry the topic where one is needed. Bold is for the summary's opening sentence and the titles of numbered decisions.

Use a table only for parallel facts: three or more things that share the same attributes. Use a list for discrete items, and paragraphs for reasoning.

## Examples

These examples use fictional paths, line numbers, test names, and results. Replace them with verified locations and actual evidence; never copy their links or claims into a handoff unchanged.

### A Tiny Fix

````markdown
You wanted `report --since DATE` to include entries dated exactly on DATE.

**The date filter now compares with `>=` where it used `>`.** The help text and README already described the bound as inclusive; only the code excluded it. Lint, type checks, and tests passed, and no documentation needed updating.

```python
return [entry for entry in entries if entry.date >= since]
```

[Date filter](/absolute/project/src/tracker/report.py:37)

I ran `tracker report --since 2026-03-01` against a database with an entry on that date, and the entry appeared. `test_entry_on_since_date_is_included` asserts the same thing. This fixes every report whose range starts on a day with entries, and it adds no debt.
````

### A Middling Bug Fix

````markdown
You wanted `tracker sync` to stop retrying uploads the server has rejected for good.

**The upload loop now asks `classify_failure` what to do with each failed response, and retries only when the answer is `Retry`.** A rejected entry is recorded as failed and the sync moves on, where it used to retry that entry forever. Formatting, lint, type checks, and tests passed, and no usage documentation mentioned retries. One decision awaits you: a `429` whose `Retry-After` header holds a date stops the sync.

## How It Works

An entry the server answers with `404`:

| Step | Before | After |
| --- | --- | --- |
| The response arrives | Any status other than 200 counts as a failure | Same |
| The loop decides what to do | Always waits and retries | `classify_failure` returns `GiveUp` |
| The entry | Stays at the front of the queue | Is marked `failed` with the status |
| The sync | Never reaches the next entry | Continues with the next entry |

The Before column is from reading the old loop. I did not run the old code.

`classify_failure` is a pure function from a response to `Retry` or `GiveUp`. Timeouts, connection errors, `429`, and every `5xx` status retry. Every other `4xx` status gives up.

```python
if response.status == 429 or response.status >= 500:
    return Retry(after=retry_delay(response))
return GiveUp(reason=f"server answered {response.status}")
```

[Failure classification](/absolute/project/src/tracker/sync.py:58)

The [upload loop](/absolute/project/src/tracker/sync.py:91) applies the decision. On `Retry` it waits and tries the same entry again, as before, up to the existing limit of five attempts. On `GiveUp` it writes the reason to the entry's `sync_error` column and takes the next entry. The entry is not deleted, so a later sync skips it until the user edits it.

## Value and Cost

One bad entry no longer blocks every entry behind it. Before this, a single deleted project on the server stopped all syncing from that device until the user found and removed the entry by hand.

This adds a small amount of debt. The statuses that retry are written out in `classify_failure`, so a server that starts using a new one needs a change there. `sync_error` is a new column that nothing clears except an edit to the entry.

## Verification

```console
$ uv run tracker sync --db tracker.db
Synced 2; failed 1
$ uv run tracker list --failed --db tracker.db
2026-03-02  Review outline  (server answered 404)
```

I ran this against the local test server with one entry pointing at a deleted project. `test_rejected_upload_is_marked_failed_and_skipped` covers the `404` path, and `test_server_error_still_retries` covers `503`. Neither covers `429`.

## Where I Would Aim Doubt

1. An entry that fails with a timeout five times is still dropped from this sync without a `sync_error`. I read that path and did not run it. This change passed by that behavior and did not alter it.

## Decisions Awaiting You

1. **A `Retry-After` date stops the sync.** `retry_delay` expects a number of seconds. I made the test server answer `429` with a date in that header, and the sync exited with `ValueError: invalid literal for int()`. The old loop ignored the header, so this change exposed the problem. Parsing both forms is about ten lines; treating an unreadable header as the default delay is one. Recommendation: use the default delay, because the request was about rejected uploads and the header's date form is rare.
2. **A way to retry failed entries.** Failed entries stay failed until edited. A `tracker sync --retry-failed` flag would clear `sync_error` first. Recommendation: add it, because a project restored on the server otherwise needs a manual edit to every affected entry.
````

### A Larger Feature

````markdown
You wanted `catalog import` to update existing identifiers and apply each file completely or not at all.

**`catalog import` now validates the whole file, works out the inserts and updates as a plan, and applies that plan inside one transaction.** An invalid row or a failed write leaves the catalog as it was. Formatting, lint, type checks, and tests passed, and the planned README sentence is updated. Connection loss during commit is not covered.

## How It Works

### The Command Validates Before It Opens the Store

Parsing and validation run over every row first. An invalid row exits 2 and names the row, before any read or write happens.

```python
entries = validate_catalog(parse_catalog(text))
result = store.import_catalog(entries)
```

[Import command](/absolute/project/src/catalog/cli.py:52)

### The Store Plans, Then Applies, in One Transaction

`import_catalog` reads the existing identifiers, splits the validated entries into inserts and updates, and applies both. The read and both writes share one immediate transaction, so a failed update rolls back the inserts, and no other writer can change the catalog between the read and the writes.

```python
with self.transaction(immediate=True) as transaction:
    plan = plan_import(transaction.read_all(), entries)
    apply_plan(transaction, plan)
```

`plan_import` is pure. The counts the command prints are the sizes of the plan's two halves, so every input identifier is counted exactly once. An entry whose title is unchanged still counts as updated. [Import transaction](/absolute/project/src/catalog/store.py:84)

### Storage Failures Exit 1 and Leave Nothing Behind

Any error inside the transaction rolls it back and exits 1. The user reruns the same file.

## Value and Cost

### What It Adds

A catalog can be corrected by importing a revised file, where it used to need a delete and a fresh import. A bad file can no longer leave half its rows in place, which previously meant restoring from a backup.

### What It Costs

This adds a small amount of debt, in two places.

- The immediate transaction holds the write lock for the whole import. Other writers wait for the length of the largest file.
- `ImportPlan` is a new type with one producer and one consumer.

## Verification

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

The second import exited 2, and the listing after it shows the catalog unchanged. `test_update_failure_after_insert_rolls_back` forces the second update to raise and asserts that the insert is gone. `test_duplicate_row_exits_2_without_writes` covers the validation path.

## Where I Would Aim Doubt

1. Connection loss during commit is read only. If the commit landed but the command reported a failure, a rerun would report every entry as updated. No test simulates it.

## Choices Made Without Asking

- Forced the rollback test's failure by making the second update raise through the existing adapter fixture, not by simulating a full disk, because the fixture already injects errors inside a real transaction.
- Took duplicate positions from `InputRow.row_number` instead of recounting rows, so both kinds of error number rows the same way.

## Decisions Awaiting You

1. **Trailing blank records.** The plan does not say what a blank final line does, and the parser currently rejects it as a short row. Skipping it would accept files exported by common spreadsheet tools; rejecting it keeps the header-and-records rule strict. Recommendation: skip a single trailing blank line, because it carries no data and the rejection message confuses users.
````
