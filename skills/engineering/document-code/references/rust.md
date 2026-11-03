# Rust Documentation

Use a concise brief for documented items. Add `# Errors` for fallible operations, explaining the error conditions callers need to handle. Add `# Panics` when the function can panic under a caller-relevant condition, and `# Safety` for unsafe interfaces with caller obligations. These contracts must not be lost in pursuit of brevity; do not add empty sections to infallible, non-panicking, safe functions.

Put short argument and result semantics, such as units or encoding, in the brief. Put failure conditions in `# Errors` or the other applicable contract section. Do not add a prose body merely because a parameter has a non-obvious constraint. Use examples when they materially clarify correct use; do not require a doctest for every trivial item.

For a decoder that accepts exactly four little-endian bytes, this body is unnecessary:

```rust
/// Decode a counter.
///
/// The input must contain exactly four bytes in little-endian order.
///
/// # Errors
///
/// Returns `DecodeError::WrongLength` unless the input contains exactly four bytes.
```

Keep the same contract in the brief and error section:

```rust
/// Decode a four-byte, little-endian counter.
///
/// # Errors
///
/// Returns `DecodeError::WrongLength` unless the input contains exactly four bytes.
```

These are documentation fragments, assuming the decoder and its `DecodeError` type exist. Public types, variants, fields, traits, and associated items need their applicable contracts, not just their containing function. Describe invariants and member meaning without repeating the same prose at every level. For trait implementations, use the trait's contract and document meaningful differences rather than mechanically copying it onto each implementation.

Check visibility, consumers, and configured Rust and Clippy documentation lints. A crate-internal interface consumed across modules may deserve documentation even when a public-item lint does not require it. Conversely, an internal implementation item covered by an enforced documentation lint must still be documented. Run the project's relevant documentation checks and doctests without introducing unrelated tooling changes.
