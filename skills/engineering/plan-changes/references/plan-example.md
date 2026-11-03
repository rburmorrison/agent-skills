# Example: catalog import

This is an illustrative plan. Paths and interfaces must be verified or chosen for the actual project before use.

## Resolve one decision at a time

Request: "Add CSV import for the catalog."

First ask: "When an identifier already exists, should import reject it, update it, or skip it? I recommend rejecting it initially so an import cannot silently replace catalog data."

Wait for the response. If the user chooses updates, record that choice and its reason. The next question can then address invalid rows or transaction behavior. Do not bundle the interview into a questionnaire.

## Agreed behavior

- Existing identifiers are updated; new identifiers are inserted.
- Validate all records before starting writes. Report invalid records with source row numbers.
- Any validation or storage failure leaves the catalog unchanged.
- Input format is CSV only. Export, format detection, and UI work are outside scope.

The user chose updates to support recurring imports. They chose atomicity to make failures straightforward to correct and retry.

## Design

The CLI owns reading the input file and displaying results. The following operation names illustrate the decisions the planner should make; choose actual paths and interfaces from the repository.

| Operation and owning module | Contract and responsibility | I/O |
|---|---|---|
| `parse_catalog` in catalog parsing | Text → input records retaining source row numbers, or parsing errors. | None |
| `validate_catalog` in catalog validation | Input records → validated entries, or row-specific validation errors. | None |
| `plan_import` in catalog import planning | Current catalog entries and validated input → `ImportPlan` with named inserts and updates. Decides which records change. | None |
| `import_catalog` in catalog storage | Validated entries → `ImportResult` with inserted and updated counts, or a storage error. Owns the transaction, reads current entries, calls `plan_import`, applies the plan, and commits or rolls back. | Database |

The request flows from CLI file reading through parsing and validation to `import_catalog`, then back to CLI result display. Invalid input never reaches writes. Keep current-state reads, planning, and application within the storage consistency boundary. Verify that the existing isolation, locking, or conflict checks prevent concurrent changes from invalidating the plan; sharing a transaction alone does not establish that guarantee. Reuse the existing transaction capability and confirm that it rolls back both inserts and updates on failure.

In a real plan, specify the exact record fields, validation rules, error representation, existing entry points, storage interface, and proposed file locations. These choices depend on the repository and user answers. Incidental helpers and syntax remain implementation choices.

## Sequence and verification

1. Add the parsing, validation, and import-planning types and operations in the modules identified during investigation.
2. Implement the import transaction using the existing storage capability and the pure import plan.
3. Add the CLI entry point using the repository's existing argument and error conventions.
4. Verify valid inserts and updates, row-specific validation errors, no writes for invalid input, and rollback when storage fails partway through a batch.
5. Run the project's established formatting, lint, type, and relevant test commands. Provide the actual commands in the real plan.
6. Have an independent reviewer inspect the diff against these decisions, especially validation order and atomicity. Fix validated findings within scope.

Tests should establish those observable contracts. A fixture database or fake adapter should exercise the real transaction boundary rather than merely assert that a method with "atomic" in its name was called.

If investigation finds no atomic storage capability, resolve that architectural issue before implementation. If an unforeseen limitation appears later, complete independent parsing and validation work, leave unsupported integration explicitly incomplete, and report the roadblock without substituting partial writes.
