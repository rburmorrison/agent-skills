# Readable Code Examples

These fragments illustrate language-agnostic decisions. Adapt the types and syntax to the actual project's conventions and supported versions.

## Logical Paragraphs

A dense report hides intermediate concepts:

```python
def render_failures(checks: Sequence[Check]) -> str:
    return "\n".join([
        f"{sum(not check.passed for check in checks)} checks failed",
        *(f"- {check.name}: {check.message}" for check in checks if not check.passed),
    ])
```

Name the stages, introduce them with short comments, and separate changes of purpose:

```python
def render_failures(checks: Sequence[Check]) -> str:
    # Collect failed checks and count them for the summary.
    failed_checks = [check for check in checks if not check.passed]
    summary = f"{len(failed_checks)} checks failed"

    # Format the details for each failed check.
    details = [
        f"- {check.name}: {check.message}"
        for check in failed_checks
    ]

    # Assemble the summary and details into the report.
    return "\n".join([summary, *details])
```

This remains one coherent function. The simple comprehension is useful; three extra helpers would add little meaning.

## Named Domain Values

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

## Cohesive Branches

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

The arms form one dispatch operation, so neither the function nor its individual arms need step comments. Indentation provides the structure. Use ordinary conditionals for straightforward predicates.

## Implementation Comments

### Short Functions With Multiple Steps

Logical steps, rather than function length or statement count, determine whether step comments are required. Even this short function has two stages:

```rust
fn normalize_tags(input: &str) -> Vec<String> {
    // Collect nonempty tags in lowercase.
    let mut tags: Vec<_> = input
        .split(',')
        .map(str::trim)
        .filter(|tag| !tag.is_empty())
        .map(str::to_lowercase)
        .collect();

    // Sort and remove duplicate tags.
    tags.sort_unstable();
    tags.dedup();

    tags
}
```

Collecting the values and organizing them have different purposes. Sorting and deduplication work together as one stage. The final return needs no separate comment.

### Decisions and Ordering

Name the stage with an imperative comment and explain why a consequential decision or ordering constraint is necessary:

```rust
fn prepare_text(
    bytes: &[u8],
    max_bytes: usize,
) -> Result<Option<&str>, std::str::Utf8Error> {
    // Skip oversized content before scanning its encoding.
    // This keeps validation work within the configured size limit.
    if bytes.len() > max_bytes {
        return Ok(None);
    }

    // Validate the encoding before returning the content as text.
    let text = std::str::from_utf8(bytes)?;

    Ok(Some(text))
}
```

The size check explains both its purpose and why it precedes encoding validation. The rationale belongs beside that decision, not only in API documentation or the handoff.

### Stages Inside a Loop

Apply the same standard inside nested processing. This fragment assumes `Section` has a string `title` and a list of string `entries`:

```rust
fn render_sections(sections: &[Section]) -> String {
    let mut output = String::new();

    for section in sections {
        // Write the section heading.
        output.push_str(&section.title);
        output.push('\n');

        // Write the entries beneath the heading.
        for entry in &section.entries {
            output.push_str("- ");
            output.push_str(entry);
            output.push('\n');
        }

        // Separate this section from the next.
        output.push('\n');
    }

    output
}
```

The comments identify three stages within the outer loop. A single comment such as "Write the heading and entries" would hide the transition into the inner loop; comment each stage where it starts. Routine buffer initialization and returning the result need no narration, but whitespace still separates them from the traversal. Keep cohesive code together instead of creating helpers solely to shorten the function or avoid comments.

### Single-Step Functions

Straightforward predicates and mappings usually need no implementation comments:

```rust
fn same_content(before: &[u8], after: &[u8]) -> bool {
    before == after
}

fn is_within_limit(content: &[u8], max_bytes: u64) -> bool {
    let byte_count = content.len() as u64;
    byte_count <= max_bytes
}
```

Both functions perform one logical operation even though the second uses two statements. The dispatch function under [Cohesive Branches](#cohesive-branches) is also one operation despite its length. A single-step function can still need a rationale comment when its behavior is surprising.

### Top of a Block

A comment can immediately follow the opening of its enclosing block. Explain the reason for otherwise surprising behavior:

```python
if cache_entry is not None:
    # Expired entries remain available while a refresh is in progress.
    if refresh_pending or cache_entry.expires_at > now:
        return cache_entry.value
```

### Within a Block

After preceding code, leave a blank line above the comment and keep it adjacent to the code it explains:

```python
records = parse_records(source)

# Preserve input order because later entries depend on earlier ones.
for record in records:
    apply_record(record)
```

### Longer Explanations

Use consecutive single-line comments as one group, with a blank line above the group. Do not use a block comment or a standalone string for an implementation explanation:

```rust
let boundary = buffer.len() - overlap;

// Retain the overlapping suffix because a delimiter may span two chunks.
// The next read will prepend these bytes before scanning again.
buffer.drain(..boundary);
```

This fragment assumes `overlap` is no greater than the buffer length and that the surrounding reader scans the retained bytes with the next chunk.

### API Documentation Syntax

Keep native documentation syntax for API contracts. For example, Rust uses `///` for the function's caller-facing brief and `//` for the implementation rationale:

```rust
/// Return whether the entry is unexpired at `now` or a refresh is in progress.
fn can_serve(entry: &CacheEntry, now: Instant, refresh_pending: bool) -> bool {
    // Expired entries remain available while a refresh is in progress.
    refresh_pending || entry.expires_at > now
}
```

Python API docstrings likewise retain their normal triple-quoted syntax. The single-line implementation-comment rule does not replace API documentation formats; see the [Python](documentation-python.md) and [Rust](documentation-rust.md) references for their contract requirements.

### Keeping Existing Comments Accurate

Suppose a change adds forced refreshes, leaving this existing comment inaccurate:

```python
# Refresh only after the cached entry expires.
if force_refresh or cache_entry.expires_at <= now:
    refresh_cache()
```

Update the comment to reflect the changed condition and preserve useful intent:

```python
# Honor forced refreshes even when cached data has not expired.
if force_refresh or cache_entry.expires_at <= now:
    refresh_cache()
```

Check existing comments in touched logic even when their lines are absent from the code diff. Leave accurate comments unchanged. Update stale stage comments when the process changes; remove comments whose stage or rationale no longer applies. Clear individual statements do not make a useful stage comment redundant.

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
# Read the source at the I/O boundary.
source = read source at the I/O boundary

# Parse and validate the records before writing.
records = parse source
entries = validate records

# Import the validated entries atomically.
summary = import entries atomically through storage
return summary
```

The plan must define errors and transaction behavior before implementation. Parsing and validation should operate on values without reaching into storage or the environment. A small converter may need fewer modules; this is a responsibility example, not a mandatory directory template.

When a calculation depends on stored state, separating it does not require moving the read outside the transaction. Illustrative orchestration can remain small:

```text
with store.transaction() as transaction:
    # Plan updates from the state visible to this transaction.
    current = transaction.load_items()
    changes = plan_updates(current, requested)

    # Apply updates within the same transaction to preserve consistency.
    transaction.apply(changes)

# Summarize the committed changes.
return summarize(changes)
```

Here `plan_updates` owns the substantial domain calculation using ordinary values; the surrounding operation owns the read, write, and commit boundary. Use the existing transaction API. Do not add a framework or extract every statement into a helper.

Watch for repeated linear searches inside a collection traversal. An ordered sequence can preserve output order while a set or map supports membership or lookup. Choose each collection for its role rather than turning a linear transformation into a quadratic one.
