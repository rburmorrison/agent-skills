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

- The CLI owns reading the input file and displaying results. It passes text to parsing code.
- Parsing converts rows to a named input-record type that preserves the source row number. It performs no file or database access.
- Domain validation produces valid catalog entries or a collection of row-specific errors. The result distinguishes success from failure explicitly.
- The import operation invokes validation before calling the existing atomic storage operation. Confirm that this operation really rolls back both inserts and updates on failure during investigation.
- The result contains named inserted and updated counts. Errors distinguish invalid input from storage failure.

In a real plan, name the existing entry points, exact data fields, validation rules, error representation, storage interface, and proposed file locations. These choices depend on the repository and user answers; the example does not supply substitutes for that investigation.

## Sequence and verification

1. Add the parsing and validation types and operations in the modules identified during investigation.
2. Connect the existing atomic storage operation to the import workflow.
3. Add the CLI entry point using the repository's existing argument and error conventions.
4. Verify valid inserts and updates, row-specific validation errors, no writes for invalid input, and rollback when storage fails partway through a batch.
5. Run the project's established formatting, lint, type, and relevant test commands. Provide the actual commands in the real plan.
6. Have an independent reviewer inspect the diff against these decisions, especially validation order and atomicity. Fix validated findings within scope.

Tests should establish those observable contracts. A fixture database or fake adapter should exercise the real transaction boundary rather than merely assert that a method with "atomic" in its name was called.

If investigation finds no atomic storage capability, resolve that architectural issue before implementation. If an unforeseen limitation appears later, complete independent parsing and validation work, leave unsupported integration explicitly incomplete, and report the roadblock without substituting partial writes.
