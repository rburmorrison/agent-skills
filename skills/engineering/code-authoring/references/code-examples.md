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

Name the intermediate values and separate changes of purpose:

```python
def render_failures(checks: Sequence[Check]) -> str:
    # Filter once so the count and the details describe the same failures.
    failed_checks = [check for check in checks if not check.passed]
    summary = f"{len(failed_checks)} checks failed"

    details = [
        f"- {check.name}: {check.message}"
        for check in failed_checks
    ]

    return "\n".join([summary, *details])
```

Blank lines separate the three stages. Only the first carries a comment, because filtering once is a choice the code does not explain. This remains one coherent function. The simple comprehension is useful; three extra helpers would add little meaning.

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

## Declarative Domain Rules

A membership program has two benefit tiers. Separate branches for eligibility, discount, and shipping credit make the reader reconstruct what each tier means, even if every helper is pure. Put the related rules together:

```rust
struct BenefitTier {
    name: &'static str,
    minimum_points: u32,
    discount_percent: u8,
    shipping_credit_cents: u32,
}

const BENEFIT_TIERS: &[BenefitTier] = &[
    BenefitTier {
        name: "standard",
        minimum_points: 0,
        discount_percent: 0,
        shipping_credit_cents: 0,
    },
    BenefitTier {
        name: "plus",
        minimum_points: 1_000,
        discount_percent: 5,
        shipping_credit_cents: 500,
    },
];

fn benefit_tier(points: u32) -> Option<&'static BenefitTier> {
    BENEFIT_TIERS
        .iter()
        .filter(|tier| points >= tier.minimum_points)
        .max_by_key(|tier| tier.minimum_points)
}
```

The shared selection rule is highest eligible threshold; the declarations state each tier's eligibility and benefits. Consumers read the selected tier's fields rather than matching its name to recover the policy. A third tier primarily adds a declaration. This can improve readability with one consumer and two tiers; it does not depend on duplicated strings or a large case count. The example assumes distinct thresholds, and the zero-point tier covers every `u32` input.

Keep a standalone decision such as `if invoice.overdue() { send_reminder(invoice)?; }` direct when there is no coherent family of rules to clarify. Likewise, an exhaustive match that is already the clearest complete statement of a policy needs no descriptor layer. Prefer a dependency's supported declarations when they already express the required rules.

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

The arms form one dispatch operation, so neither the function nor its individual arms need comments or internal blank lines. Indentation provides the structure. Use ordinary conditionals for straightforward predicates.

## Implementation Comments

### Spacing Carries the Structure

Blank lines mark the stages; a comment appears only where the code cannot explain itself. This function has two stages and one comment:

```rust
fn normalize_tags(input: &str) -> Vec<String> {
    let mut tags: Vec<_> = input
        .split(',')
        .map(str::trim)
        .filter(|tag| !tag.is_empty())
        .map(str::to_lowercase)
        .collect();

    // Sort before deduplicating; `dedup` removes only adjacent repeats.
    tags.sort_unstable();
    tags.dedup();

    tags
}
```

Collecting the values and organizing them have different purposes, so a blank line separates them. The collecting stage reads directly from its code and needs no comment. The second stage has an ordering constraint the code does not show, so it gets one.

### Decisions and Ordering

Say why a consequential decision or ordering constraint is necessary, beside the code it governs:

```rust
fn prepare_text(
    bytes: &[u8],
    max_bytes: usize,
) -> Result<Option<&str>, std::str::Utf8Error> {
    // Skip oversized content first so validation work stays bounded.
    if bytes.len() > max_bytes {
        return Ok(None);
    }

    let text = std::str::from_utf8(bytes)?;

    Ok(Some(text))
}
```

The size check explains why it precedes encoding validation. The validation line needs nothing: a comment such as `// Validate the encoding.` would only repeat it.

### Stages Inside a Loop

Space nested stages the same way. This fragment assumes `Section` has a string `title` and a list of string `entries`:

```rust
fn render_sections(sections: &[Section]) -> String {
    let mut output = String::new();

    for section in sections {
        output.push_str(&section.title);
        output.push('\n');

        for entry in &section.entries {
            output.push_str("- ");
            output.push_str(entry);
            output.push('\n');
        }

        output.push('\n');
    }

    output
}
```

Every stage here is obvious from its code, so the function has no comments at all. Whitespace still separates the title, the entries, and the closing blank line, and sets the buffer setup and the return apart from the traversal. Keep cohesive code together instead of creating helpers solely to shorten the function.

### Comments That Add Nothing

Counterexamples, not models. The first two restate their statements, and the third labels a stage whose code already names it:

```rust
// Push the title.
output.push_str(&section.title);

// Push a newline.
output.push('\n');

// Merge overlapping ranges.
let merged = merge_overlapping(ranges);
```

Delete all three. A generic claim does not rescue one: `// Merge overlapping ranges so the result is correct and clean.` is still noise. This version earns its place, because it states a downstream dependency the code cannot show:

```rust
// Merge overlaps so later lookups can binary-search disjoint ranges.
let merged = merge_overlapping(ranges);
```

### Single-Step Functions

Straightforward predicates and mappings need no implementation comments:

```rust
fn same_content(before: &[u8], after: &[u8]) -> bool {
    before == after
}

fn is_within_limit(content: &[u8], max_bytes: u64) -> bool {
    let byte_count = content.len() as u64;
    byte_count <= max_bytes
}
```

Both functions perform one logical operation even though the second uses two statements. The dispatch function under [Cohesive Branches](#cohesive-branches) is also one operation despite its length. A single-step function can still need a comment when its behavior is surprising.

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

### Longer Rationale

Rationale usually fits one line:

```rust
let boundary = buffer.len() - overlap;

// Keep the overlapping suffix because a delimiter may span two chunks.
buffer.drain(..boundary);
```

This fragment assumes `overlap` is no greater than the buffer length and that the surrounding reader scans the retained bytes with the next chunk. When a constraint cannot be stated in one line, use consecutive single-line comments as one group, not a block comment or a standalone string.

### API Documentation Syntax

Keep native documentation syntax for API contracts. For example, Rust uses `///` for the function's caller-facing brief and `//` for the implementation rationale:

```rust
/// Return whether the entry is unexpired at `now` or a refresh is in progress.
fn can_serve(entry: &CacheEntry, now: Instant, refresh_pending: bool) -> bool {
    // Expired entries remain available while a refresh is in progress.
    refresh_pending || entry.expires_at > now
}
```

Python API docstrings likewise retain their normal triple-quoted syntax; see the [Python](documentation-python.md) and [Rust](documentation-rust.md) references for their contract requirements.

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

Check existing comments in touched logic even when their lines are absent from the code diff. Leave accurate comments unchanged, and remove comments whose rationale no longer applies.

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

# Reject invalid input before anything is written.
records = parse source
entries = validate records

summary = import entries atomically through storage
return summary
```

Settle errors and transaction behavior before implementation. Parsing and validation should operate on values without reaching into storage or the environment. A small converter may need fewer modules; this is a responsibility example, not a mandatory directory template.

When a calculation depends on stored state, separating it does not require moving the read outside the transaction. Illustrative orchestration can remain small:

```text
with store.transaction() as transaction:
    # Plan updates from the state visible to this transaction.
    current = transaction.load_items()
    changes = plan_updates(current, requested)

    # Apply updates within the same transaction to preserve consistency.
    transaction.apply(changes)

return summarize(changes)
```

Here `plan_updates` is pure: it receives ordinary values and returns `changes`, a value describing the writes, without touching storage or modifying `current`. The surrounding operation owns the read, write, and commit boundary. Tests can cover the decision with plain values and reserve the real transaction for the apply step. Use the existing transaction API. Do not add a framework or extract every statement into a helper.

Watch for repeated linear searches inside a collection traversal. An ordered sequence can preserve output order while a set or map supports membership or lookup. Choose each collection for its role rather than turning a linear transformation into a quadratic one.

## Decide, Then Apply

A cleanup that reads the clock, decides, and writes in one loop cannot be tested without a store, and judges each session at a slightly different instant:

```python
def expire_sessions(store: SessionStore) -> None:
    for session in store.load_sessions():
        if session.last_seen < datetime.now(UTC) - IDLE_LIMIT:
            store.delete(session.identifier)
```

Return the decision as a value, and apply it separately:

```python
@dataclass(frozen=True)
class Expiry:
    identifiers: tuple[str, ...]


def plan_expiry(sessions: Sequence[Session], now: datetime) -> Expiry:
    cutoff = now - IDLE_LIMIT

    return Expiry(
        tuple(
            session.identifier
            for session in sessions
            if session.last_seen < cutoff
        )
    )


def expire_sessions(store: SessionStore, now: datetime) -> Expiry:
    # Decide from one read of the store, before any session is deleted.
    expiry = plan_expiry(store.load_sessions(), now)

    for identifier in expiry.identifiers:
        store.delete(identifier)

    return expiry
```

`plan_expiry` is pure: the caller passes the sessions and the time, and a test needs only plain values. `Expiry` describes the writes without performing them, so the caller can log it, show it in a dry run, or apply it. `expire_sessions` stays thin and owns both effects. Its loop remains a loop because it performs ordered writes.

## Expressions over Accumulator Loops

An accumulator makes the reader run the loop to learn what the result is:

```python
overdue = []
for invoice in invoices:
    if invoice.due < today and not invoice.paid:
        overdue.append(invoice.number)
overdue.sort()
```

An expression states the result directly:

```python
overdue = sorted(
    invoice.number
    for invoice in invoices
    if invoice.due < today and not invoice.paid
)
```

Keep the loop when the expression would be harder to read. Totals per customer need a sort and a grouping pass as an expression; a local accumulator inside one function is clearer, and nothing outside the function can see the mutation:

```python
def paid_totals(orders: Sequence[Order]) -> dict[str, int]:
    totals: defaultdict[str, int] = defaultdict(int)

    for order in orders:
        if order.paid:
            totals[order.customer] += order.amount_cents

    return dict(totals)
```
