# Readable behavior tests

Derive cases from agreed behavior, invariants, and meaningful failures. Prefer a small set of distinct scenarios over repeated tests of equivalent paths. Add cases when they protect a separate contract; do not optimize for a numeric test or coverage target unless the project requires one.

Test at the boundary where the behavior can actually be observed. Use focused tests for non-trivial pure logic and integration tests for interactions such as transactions and serialization. A fake that simply implements the desired behavior does not establish that the production adapter has it.

Name tests after the behavior they establish. Keep setup, action, and expected outcome easy to identify. Keep input and expected values close enough to understand together. Some repetition is preferable to a fixture hierarchy or generic test harness that hides the scenario.

Use parameterization when cases share a readable structure. Separate materially different behaviors when a table would require flags, branching, or knowledge of distant fixtures. Share expensive resources or genuinely repeated setup without hiding the reason a case exists.

Keep error assertions specific enough to protect the contract, while allowing harmless wording and implementation changes. Avoid asserting private call order, internal helper names, incidental container layout, or other details unless they are part of the agreed behavior.

Tests have lighter style restrictions. Failure-on-error shortcuts are acceptable when they make setup clearer; in Rust, `unwrap()` is acceptable in tests and `expect()` is optional when its message helps. Use the equivalent idiom in other languages. Encode routine test exemptions in tooling with a reason beside the setting, instead of repeating suppressions throughout tests.

## Example: a rejected update preserves state

This example assumes `Catalog` and its immutable `Entry` type come from the application, and that the catalog exposes its entries for reading:

```python
import pytest

from catalog import Catalog, Entry


def test_invalid_title_preserves_existing_entry() -> None:
    catalog = Catalog()
    original = Entry(identifier="alpha", title="Original")
    catalog.save(original)

    with pytest.raises(ValueError):
        catalog.rename("alpha", " \t ")

    assert catalog.entries["alpha"] == original
```

The three blocks show setup, the rejected action, and its observable consequence. The test invokes the application's real catalog operation; it does not mock the validation helper or assert private call order. The named test and nearby expected value explain the contract without a generic fixture harness. A transaction guarantee would additionally need a test against the actual storage adapter.

## Reporting coverage

For a catalog import, useful commitments might be:

- Valid input inserts new entries and updates existing identifiers.
- Invalid records produce source-row errors before any write.
- A storage failure rolls back the entire batch.

Verify the real boundary behind each commitment. The handoff can summarize these behaviors together without listing every test function. Do not claim a commitment is covered unless an executed test or other stated evidence actually checks it.
