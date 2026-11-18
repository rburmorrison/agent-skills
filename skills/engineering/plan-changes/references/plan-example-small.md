# Example: Inclusive Report Bound

This is a completed illustrative plan for a small fix in a fictional Python CLI repository. Paths, symbols, and commands are assumed investigation findings; a real planner must inspect its project and replace them with verified facts.

The plan has one implementation step, so it stays in the chat and no file is written.

Goal: Make `report --since DATE` include entries dated exactly on DATE.

## Request and Investigation

Request: "`report --since DATE` drops entries dated exactly on DATE. Fix it."

`src/tracker/report.py`, `select_entries(entries, since)`, filters with `entry.date > since`. The `--since` help text and `README.md` ("Reports") both say the bound is inclusive, so the code is the outlier.

## Decisions

None consequential: the intended behavior is already documented, and no other caller of `select_entries` was found (`grep -rn select_entries src tests`).

## Change

In `select_entries`, replace `entry.date > since` with `entry.date >= since`. Add one case to `tests/test_report.py`: an entry dated exactly on `since` is included. Exit statuses, output format, and the no-bound path stay unchanged.

## Invariants and Failure Modes

- I1: An entry dated on the `--since` date appears in the report.

## Checks

- `uv run pytest tests/test_report.py`: all pass; the new case fails before the change.
- `uv run ruff check .` and `uv run basedpyright`: no findings.

## User Workflow

In a temporary directory, add entries dated 2026-03-01 and 2026-03-02. Run `uv run tracker report --since 2026-03-01 --db <temp>/tracker.db`; expect both entries. Run with `--since 2026-03-02`; expect only the second.

No usage-documentation edits planned. Help and README already state the intended behavior.

## Implementer Brief

- Load `code-authoring`.
- No usage-documentation edits planned.
- Change only the comparison and its test; stop and ask before touching other callers, output, or exit statuses.
- Run the checks above and the workflow; report results separately.
- No independent review needed for this one-line fix.
