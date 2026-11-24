# Readable Code Examples

These fragments illustrate language-agnostic decisions. Adapt the types and syntax to the actual project's conventions and supported versions. The design examples, such as separating decisions from effects, show the default for new projects and for code with no settled convention; in an existing codebase, its conventions come first.

## Self-Documenting Code

The code should carry its own explanation through names, types, and shape. Most good functions here have no comments at all.

### Name the Intermediate Values

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

`failed_checks`, `summary`, and `details` tell the reader what each part is, and blank lines separate the three stages. Only the first carries a comment, because filtering once is a choice the code does not explain. This is also the right size: three stages in one coherent function. Extracting helpers here would add navigation without adding meaning.

### Descriptive Names

Abbreviated names make the reader open the definition, and sometimes the callers, to learn what a value holds:

```python
def calc(d: Sequence[Order], t: datetime) -> int:
    return sum(o.amt for o in d if o.ts > t)
```

Full words from the problem's vocabulary, with units where they matter, make the signature its own description:

```python
def revenue_cents_since(orders: Sequence[Order], cutoff: datetime) -> int:
    return sum(
        order.amount_cents
        for order in orders
        if order.placed_at > cutoff
    )
```

### Concrete Types

Positional fields lose meaning at call sites:

```rust
type SearchMatch = (PathBuf, usize, String);

println!("{}:{}: {}", found.0.display(), found.1, found.2);
```

A named record keeps the contract visible:

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

A string standing in for a fixed set of values lets a typo compile and leaves related data loosely attached:

```rust
struct Job {
    id: JobId,
    status: String,
    retries: Option<u32>,
}

if job.status == "failed" && job.retries.unwrap_or(0) < MAX_RETRIES {
    requeue(&job);
}
```

An explicit variant names every state and carries the data that belongs to it:

```rust
enum JobStatus {
    Queued,
    Running,
    Succeeded,
    Failed { retries: u32 },
}

struct Job {
    id: JobId,
    status: JobStatus,
}

if let JobStatus::Failed { retries } = job.status {
    if retries < MAX_RETRIES {
        requeue(&job);
    }
}
```

The same applies to untyped maps and catch-all types: a `dict[str, Any]` passed between functions becomes a dataclass, and a parameter typed `object` or `Any` takes the type the function actually uses. Local iteration pairs can remain immediately unpacked tuples. Runtime validation is a separate concern from naming fields.

### Function Size

Most functions should hold one to three stages and fit comfortably on a screen, often in five to twenty lines. That is a description of what reads well, not a limit to enforce. `render_failures` above is a typical size. This function has grown past it; selecting, grouping, composing, and sending are four stages, and the last two are tangled inside one loop:

```python
def send_overdue_reminders(
    invoices: Sequence[Invoice],
    today: date,
    mailer: Mailer,
) -> ReminderReport:
    overdue = [
        invoice
        for invoice in invoices
        if invoice.due < today and not invoice.paid
    ]

    by_customer: defaultdict[CustomerId, list[Invoice]] = defaultdict(list)
    for invoice in overdue:
        by_customer[invoice.customer].append(invoice)

    failed: list[CustomerId] = []
    for customer, customer_invoices in by_customer.items():
        total_cents = sum(invoice.amount_cents for invoice in customer_invoices)
        lines = [
            f"- {invoice.number}: due {invoice.due.isoformat()}"
            for invoice in customer_invoices
        ]
        body = "\n".join([
            f"{len(customer_invoices)} invoices overdue, {format_cents(total_cents)} in total.",
            *lines,
        ])

        try:
            mailer.send(customer, subject="Overdue invoices", body=body)
        except MailError:
            failed.append(customer)

    return ReminderReport(sent=len(by_customer) - len(failed), failed=tuple(failed))
```

Extract each stage that has a name worth giving. The top function then reads as a summary of the work:

```python
def send_overdue_reminders(
    invoices: Sequence[Invoice],
    today: date,
    mailer: Mailer,
) -> ReminderReport:
    overdue_by_customer = group_by_customer(overdue_invoices(invoices, today))
    reminders = [
        compose_reminder(customer, customer_invoices)
        for customer, customer_invoices in overdue_by_customer.items()
    ]

    return deliver(reminders, mailer)


def overdue_invoices(invoices: Sequence[Invoice], today: date) -> list[Invoice]:
    return [
        invoice
        for invoice in invoices
        if invoice.due < today and not invoice.paid
    ]


def group_by_customer(
    invoices: Sequence[Invoice],
) -> dict[CustomerId, list[Invoice]]:
    grouped: defaultdict[CustomerId, list[Invoice]] = defaultdict(list)

    for invoice in invoices:
        grouped[invoice.customer].append(invoice)

    return dict(grouped)


def compose_reminder(customer: CustomerId, invoices: Sequence[Invoice]) -> Reminder:
    total_cents = sum(invoice.amount_cents for invoice in invoices)
    summary = f"{len(invoices)} invoices overdue, {format_cents(total_cents)} in total."
    details = [
        f"- {invoice.number}: due {invoice.due.isoformat()}"
        for invoice in invoices
    ]

    return Reminder(
        customer=customer,
        subject="Overdue invoices",
        body="\n".join([summary, *details]),
    )


def deliver(reminders: Sequence[Reminder], mailer: Mailer) -> ReminderReport:
    failed: list[CustomerId] = []

    for reminder in reminders:
        try:
            mailer.send(reminder.customer, subject=reminder.subject, body=reminder.body)
        except MailError:
            failed.append(reminder.customer)

    return ReminderReport(sent=len(reminders) - len(failed), failed=tuple(failed))
```

Each function now has one to three stages and a name that says what it returns, and none needs a comment. `Reminder` gives the composed message a concrete type, so composing can be tested without a mailer and only `deliver` has an effect.

Split by purpose, not by length. A function that performs one cohesive stage stays whole even when it is long, such as the dispatch under [Cohesive Branches](#cohesive-branches), and a three-stage function like `render_failures` gains nothing from helpers.

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

## Comments

### Spacing Carries the Structure

Blank lines mark the stages; a comment appears only where the code cannot explain itself. Every stage in this function is obvious from its code, so it has no comments. This fragment assumes `Section` has a string `title` and a list of string `entries`:

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

Whitespace separates the title, the entries, and the closing blank line, and sets the buffer setup and the return apart from the traversal. This is the common case.

### A Reason the Code Cannot Show

Comment a stage when a reader could not recover its reason from the code: an ordering constraint, an assumption, or surprising behavior. Here the first stage needs nothing and the second depends on an ordering the code does not explain:

```rust
fn normalize_tags(input: &str) -> Vec<String> {
    let mut tags: Vec<_> = input
        .split(',')
        .map(str::trim)
        .filter(|tag| !tag.is_empty())
        .map(str::to_lowercase)
        .collect();

    // Sort first because `dedup` removes only adjacent repeats.
    tags.sort_unstable();
    tags.dedup();

    tags
}
```

Put the comment directly above the code it explains, with a blank line above the comment unless it opens its block. Rationale usually fits one line. When it cannot, use consecutive single-line comments as one group, not a block comment or a standalone string.

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
    # Read inside the transaction so the plan matches what gets written.
    current = transaction.load_items()
    changes = plan_updates(current, requested)

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
