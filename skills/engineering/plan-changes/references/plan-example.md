# Example: Atomic Catalog Import

This is a completed illustrative plan for a fictional Python CLI repository, not a claim about files in the skills repository. The paths, existing interfaces, and commands below are assumed investigation findings. A real planner must inspect its project and replace these with verified facts; do not hand placeholders to the implementer.

## Request and Investigation

Request: "Make the existing CSV import update existing identifiers and make the whole import atomic."

The existing `catalog import FILE --db PATH` command accepts UTF-8 CSV with the exact header `identifier,title`. Identifiers are case-sensitive, nonempty strings; titles must contain non-whitespace characters. Values are preserved without trimming. These rules remain unchanged. The CLI reports input errors on stderr with exit status 2 and storage errors with status 1. `catalog list --db PATH` prints entries as CSV sorted by identifier.

Existing locations inspected:

- `src/catalog/cli.py`: `main(argv)` owns arguments, file reading, error display, and exit status.
- `src/catalog/csv_input.py`: `parse_catalog(text)` produces `InputRow(row_number: int, identifier: str, title: str)`. Row numbers count logical CSV records starting at 1 for the header. It rejects malformed CSV, wrong headers, and missing or surplus fields as `InputError(message: str)`.
- `src/catalog/models.py`: immutable `Entry(identifier: str, title: str)` represents stored values.
- `src/catalog/store.py`: `CatalogStore.transaction(immediate=True)` begins a SQLite immediate transaction before yielding `CatalogTransaction`; commits on normal exit and rolls back on exception. `CatalogTransaction.read_all()`, `insert(entry)`, and `update(entry)` share that connection. The existing adapter prevents another writer changing entries during this transaction. Database failures propagate as `StorageError`.
- `tests/test_store.py`: covers the adapter's rollback and competing-writer behavior. `pyproject.toml` defines the `catalog` entry point and existing pytest/Ruff/type-check tooling.
- `README.md`, "Import": says "Existing identifiers are rejected." Other import instructions and the existing example remain accurate. CLI help says "Import catalog entries from CSV" and remains accurate.

## Decisions and Agreement

Ask consequential questions individually and wait for each answer. For example, after confirming updates, ask what should happen when the same identifier appears twice in one input file; explain why rejecting both avoids an implicit first/last-wins policy. Do not present this completed table as a substitute for that conversation.

For this example, the following answers have already been obtained:

| ID | Confirmed Decision | Basis and Reason |
|---|---|---|
| D1 | Update matching identifiers and insert new ones. | Explicit request; recurring imports should replace existing titles. |
| D2 | Validate all rows before storage; any validation or storage failure leaves the catalog unchanged. | Explicit request, with validation order confirmed to avoid writes for invalid input. |
| D3 | Reject duplicate identifiers within the file; report both record numbers. | User confirmed after discussing first/last-wins alternatives; avoids silent loss of input. |
| D4 | A header-only file succeeds with zero inserts and zero updates. | User confirmed that an empty recurring batch is harmless. An empty file still fails the existing header check. |
| D5 | Count every matching identifier as updated, even if its title is unchanged. | User confirmed counts should describe input disposition, not changed-value counts. |
| D6 | Keep SQLite and the existing immediate transaction adapter; serialize competing writers. | User confirmed this architectural choice and its contention tradeoff after the planner verified feasibility. |
| D7 | Correct the README's rejection statement only; add no tutorial or new example. | Accuracy correction in scope; user declined the planner's optional walkthrough suggestion. |
| D8 | Report the first validation error in input order; within a row check identifier, title, then duplication. | User confirmed this precedence after discussing aggregate errors; deterministic feedback keeps the CLI's correction-and-retry flow simple. |

Preserve existing CSV syntax, validation of individual fields, exit statuses, and error rendering. Export, new formats, UI work, schema changes, dependencies, and unrelated refactoring are excluded. No consequential questions remain open.

## Types and Operation Contracts

New immutable types in `src/catalog/importer.py`:

- `ImportPlan(inserts: tuple[Entry, ...], updates: tuple[Entry, ...])`: each identifier occurs once across both fields. Each field preserves relative input order. It contains no transaction or database handle.
- `ImportResult(inserted: int, updated: int)`: nonnegative counts of successfully committed input entries, following D5. Never returned before commit succeeds.

| Operation | Exact Boundary and Responsibility | I/O |
|---|---|---|
| Existing `csv_input.parse_catalog` | `str -> tuple[InputRow, ...]`; preserve its syntax/header/row-width checks and errors. | None |
| New `importer.validate_catalog` | `tuple[InputRow, ...] -> tuple[Entry, ...]`; enforce existing field rules and D3, or raise `InputError`. Scan in input order; within each row check identifier, title, then duplication. Report the first error. Duplicate message: `row {current}: duplicate identifier {identifier!r}; first seen at row {first}`. | None |
| New `importer.plan_import` | `current: Mapping[str, Entry], incoming: tuple[Entry, ...] -> ImportPlan`; caller supplies validated, unique entries. Partition by identifier membership, with D5 for unchanged titles. | None |
| New `store.CatalogStore.import_catalog` | `tuple[Entry, ...] -> ImportResult`; caller supplies validated entries. Own the immediate transaction, current-state read, pure planning, application, and error propagation. | SQLite |
| Existing `cli.main` | Read UTF-8 text with existing file/decoding error handling; parse, validate, call storage, then print `Inserted {inserted}; updated {updated}` to stdout and return 0. Preserve existing failure rendering and statuses. | File and terminal |

`importer.py` imports only the existing domain/error types and standard-library collection types. `store.py` imports the import types and pure planner; `importer.py` must not import storage. No new repository/service layer is needed.

Storage sequence:

```text
begin existing immediate transaction
    read current entries into identifier -> Entry mapping
    call plan_import(current, incoming)
    apply inserts in their input order
    apply updates in their input order
commit using existing context manager
return ImportResult(len(inserts), len(updates))
```

Any read, insert, update, or commit failure propagates through the existing adapter, rolls back, and produces no success output. Do not catch a storage error inside the transaction and return normally. Keep the read, plan, and writes on the same transaction; a transaction using a stale pre-read would violate D2/D6.

Representative request: CLI reads CSV, parser retains record numbers, validator rejects bad input, storage locks and reads, pure planning partitions entries, storage applies and commits, CLI prints counts. Failure trace: after one insert succeeds, an update fails; the adapter rolls back both changes, the CLI prints the storage error, and returns 1.

## Documentation Change Map

| Location | Existing Claim and Planned Change | Verification |
|---|---|---|
| `README.md`, "Import", sentence "Existing identifiers are rejected." | Replace only with "Existing identifiers are updated." This corrects behavior changed by D1. Add no sentences about atomicity, duplicate handling, or counts; those would be new facts. | Compare the changed sentence with the CLI walkthrough and inspect the diff for added facts. |

No other usage-documentation edits are planned. In particular, leave existing help and examples unchanged. If another stale claim is discovered, inspect it but ask the user to confirm a plan amendment before editing it. Source comments and API doc comments/docstrings for affected code remain allowed: the plan/result types own member meaning, validation owns input constraints, and `import_catalog` owns transaction guarantees.

## Implementation Steps and Checks

1. **Pure import operations.** Add the named types, validation, and planning operations in `src/catalog/importer.py`, reusing `Entry` and `InputError`. Add `tests/test_importer.py`. Acceptance: existing field validation is preserved; D3/D4 errors and empty input are deterministic; new and existing entries partition in input order, including unchanged titles under D5. Run `uv run pytest tests/test_importer.py`.
2. **Storage integration.** Add `CatalogStore.import_catalog` in `src/catalog/store.py` using the existing transaction adapter; depends on step 1. Extend `tests/test_store.py`. Start with `alpha=Old`, import `beta=New` and `alpha=Revised`, and assert counts `(1, 1)` and both stored values. Force an update failure after the insert has executed inside the real transaction; assert the original state survives. Exercise read/commit failure propagation using the existing adapter fixtures and retain the competing-writer check. Run `uv run pytest tests/test_store.py`.
3. **CLI integration.** Wire existing import handling to parsing, validation, and storage in `src/catalog/cli.py`; depends on steps 1 and 2. Extend `tests/test_cli.py`: valid import exits 0 with exact counts, invalid fields and duplicate rows exit 2 without writes, header-only input reports `(0, 0)`, file/encoding errors preserve existing behavior, storage failure exits 1 without success output. Run `uv run pytest tests/test_cli.py`.
4. **Workflow and completion.** Run the walkthrough below, make the single planned README correction, and inspect related documentation for accuracy without authorizing extra edits. Run `uv run ruff format --check .`, `uv run ruff check .`, `uv run basedpyright`, and `uv run pytest`. Obtain one independent review of the completed diff against D1–D8, especially validation-before-storage, rollback, and documentation scope. Fix validated findings and rerun affected checks within the agreed review cadence.

The failure tests must reach the claimed boundary: a transaction rollback test needs a real successful write before the injected failure. A fake implementing rollback itself does not verify the production adapter.

## User Workflow

Use a disposable temporary directory and database. From the project root, invoke the real CLI through `uv run catalog`; do not substitute test helpers.

1. Write `initial.csv` containing header `identifier,title` and record `alpha,Old`. Run `uv run catalog import <temp>/initial.csv --db <temp>/catalog.db`; expect exit 0 and `Inserted 1; updated 0`.
2. Write `changes.csv` with the same header and records `beta,New` and `alpha,Revised`. Import it into that database; expect exit 0 and `Inserted 1; updated 1`.
3. Run `uv run catalog list --db <temp>/catalog.db`; expect the header and sorted records `alpha,Revised` and `beta,New`.
4. Import a file containing header `identifier,title` and records `gamma,One` and `gamma,Two`; expect exit 2 and a duplicate error naming records 2 and 3. List again and confirm no `gamma` and no other state change.
5. Remove only the temporary artifacts created for this walkthrough. Report the commands/actions actually run and observed output/state separately from test results.

The example assumes a runnable local CLI and SQLite adapter. If the real environment cannot execute the workflow, attempt the closest feasible check and disclose the missing capability and unverified behavior; do not claim the walkthrough passed based on unit tests.

## Remaining Discretion and Changes to the Plan

The implementer may choose local variable names, idiomatic loops, private helper extraction, and fixture organization within these contracts. It must not choose new validation rules, change counts or statuses, relax atomicity, add abstractions or dependencies, or expand usage documentation.

If investigation cannot establish the transaction guarantee, resolve that architecture with the user before finalizing the plan. If implementation later uncovers a consequential gap, explain it and ask immediately; pause dependent work, continue independent work, and amend the decision record after the answer. Do not substitute partial writes or defer the question to the final report.
