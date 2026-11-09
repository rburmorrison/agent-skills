# Final Handoff

Start with a short paragraph explaining what changed and why. Then explain the resulting code in a concise numbered list, beginning with the relevant entry point and following the flow of the changed behavior. Identify what invokes that entry point, such as a command, request, user action, or caller; it may be existing code rather than a changed function.

Give each item a bold, factual label and the function or component name, a clickable source link, and short labeled lines explaining its role. Use labels such as **Trigger**, **Role**, **Input → output**, **Behavior**, **Effect**, and **Reason** where useful. Describe how the parts connect, what happens to the data or state, and the important logic or design reasons needed to understand the code. Explain unfamiliar types when they matter to that flow.

Use descriptive wording such as "Entry point", "Parsing and validation", or "Persistence". Keep the explanation factual; avoid directions such as "Start here", "Follow the data", or "Review this". Use the numbered list rather than a table, and do not turn it into a checklist of work for the user.

Scale the explanation to the change. A small fix may need only one item. Include the locations and relationships that help the user understand the output; do not enumerate every changed file or narrate every line. Adapt the labels to the information rather than filling every field mechanically. For documentation-only changes, explain the relevant documents and their relationships without inventing a runtime flow.

Every code location named in the handoff must have a clickable Markdown link to its source using an absolute path and a one-based line. Verify paths and lines after all fixes, and link directly to the relevant function, component, branch, or contract. Use plain link labels with enough path context to distinguish duplicate file names; do not wrap links in backticks. Links support understanding even when no human review is needed.

Keep verification separate from the code explanation in a short closing paragraph. Summarize important behavior established by tests, the actual user workflow exercised and its observed results, and material limitations. Distinguish tests from application execution; if the workflow could not run, say why and what remains unverified. Group related cases; avoid a test-function inventory. State whether planned usage-documentation edits were made or no edits were needed, and surface any unplanned need awaiting confirmation. Mention significant independent review findings and their resolution when useful. Always surface unresolved findings. Do not claim checks or independent review passed unless they actually ran and their results support the claim.

If blocked, clearly state that the task is incomplete, what independent work was finished, what remains blocked, and what decision or capability is needed. A passing subset of tests does not make blocked acceptance criteria complete.

Illustrative Markdown example with fictional paths, line numbers, and results. Replace them with verified locations and actual evidence; never copy the example links or claims into a handoff unchanged.

```markdown
Added CSV import with validation before database writes.

1. **Entry point — `import_catalog()`**\
   [commands/import.py:84](/absolute/project/commands/import.py:84)\
   **Trigger:** The `catalog import` command.\
   **Role:** Coordinates reading the file, validating rows, and saving records.

2. **Parsing and validation — `parse_rows()`**\
   [catalog/parser.py:26](/absolute/project/catalog/parser.py:26)\
   **Input → output:** CSV text → `CatalogEntry` objects, each containing one record's validated values.\
   **Behavior:** Rejects malformed rows before any records reach storage.

3. **Persistence — `save_entries()`**\
   [catalog/store.py:51](/absolute/project/catalog/store.py:51)\
   **Effect:** Writes the validated records to the database in one transaction.\
   **Reason:** A storage failure rolls back the entire import, preventing partially saved results.

Tests passed for valid imports, invalid rows, and rollback after storage failure. Running the CLI with valid input saved the expected records; invalid input reported the row error and left the database unchanged. No usage-documentation updates were needed.
```
