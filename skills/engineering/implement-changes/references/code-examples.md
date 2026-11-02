# Readable code examples

These fragments illustrate language-agnostic decisions. Adapt the types and syntax to the actual project's conventions and supported versions.

## Logical paragraphs

A dense report hides intermediate concepts:

```python
def render_failures(checks: Sequence[Check]) -> str:
    return "\n".join([
        f"{sum(not check.passed for check in checks)} checks failed",
        *(f"- {check.name}: {check.message}" for check in checks if not check.passed),
    ])
```

Name the stages and separate changes of purpose:

```python
def render_failures(checks: Sequence[Check]) -> str:
    failed_checks = [check for check in checks if not check.passed]
    summary = f"{len(failed_checks)} checks failed"

    details = [
        f"- {check.name}: {check.message}"
        for check in failed_checks
    ]

    return "\n".join([summary, *details])
```

This remains one coherent function. The simple comprehension is useful; three extra helpers would add little meaning.

## Named domain values

Positional fields lose meaning at call sites:

```rust
type SearchMatch = (PathBuf, usize, String);

println!("{}:{}: {}", found.0.display(), found.1, found.2);
```

A named domain value keeps the contract visible:

```rust
struct SearchMatch {
    path: PathBuf,
    line_number: usize,
    text: String,
}

println!(
    "{}:{}: {}",
    found.path.display(),
    found.line_number,
    found.text,
);
```

Choose the equivalent record, dataclass, named tuple, struct, or explicit variant in the target language. Local iteration pairs can remain immediately unpacked tuples. Runtime validation is a separate concern from naming fields.

## Cohesive branches

For several variants of one event, a compact match exposes both the variant and its data:

```python
def handle_event(event: FileEvent, index: SearchIndex) -> None:
    match event:
        case FileCreated(path=path):
            index.add(path)
        case FileMoved(source=source, destination=destination):
            index.move(source, destination)
        case FileDeleted(path=path):
            index.remove(path)
        case _:
            raise TypeError(f"Unsupported event: {type(event).__name__}")
```

The arms form one unit; indentation provides the structure. Use ordinary conditionals for straightforward predicates.

## Responsibilities and I/O

A catalog import with actual parsing, domain rules, and storage responsibilities can use modules such as:

```text
cli                arguments, help, file input, and output
import             workflow orchestration
import/parse       input text to named records
catalog            domain types and validation
storage            database access and transaction boundary
```

The workflow then reads as a sequence of meaningful operations:

```text
source = read source at the I/O boundary
records = parse source
entries = validate records
summary = import entries atomically through storage
return summary
```

The plan must define errors and transaction behavior before implementation. Parsing and validation should operate on values without reaching into storage or the environment. A small converter may need fewer modules; this is a responsibility example, not a mandatory directory template.
