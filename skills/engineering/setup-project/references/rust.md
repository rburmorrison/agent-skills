# Rust Tooling Profile

Create the package with Cargo and manage dependencies with `cargo add` and `cargo remove`; respect workspace dependency and lockfile conventions. Keep the edition Cargo initializes with. The profile mandates no Rust version: do not add `rust-version` or a `rust-toolchain.toml` unless the user asks for one. The suppression lints below need Rust 1.81 or later.

Merge [cargo-lints.toml](../assets/rust/cargo-lints.toml) into the manifest. It denies Clippy's default, pedantic, and nursery groups, plus three restriction lints: `unwrap_used`, `allow_attributes`, and `allow_attributes_without_reason`. The group priority lets a specific, justified exception override a group when necessary.

For a Cargo workspace, put the shared settings under `[workspace.lints.clippy]` and enable `[lints] workspace = true` in each participating package. Verify the actual members inherit them; a root setting alone is insufficient.

Place [clippy.toml](../assets/rust/clippy.toml) at the appropriate project/workspace configuration root. It allows unwraps and expects in tests, and keeps the unwrap restriction in const code. The expect test allowance preserves the relaxed test policy if a project additionally enables `expect_used`; this profile does not itself enable that lint.

Unwraps are denied outside tests. `expect` stays available for the rare invariant that cannot be handled as an error.

Every source suppression must be `#[expect(clippy::rule, reason = "...")]` at the narrowest scope. `#[allow]` and a missing reason are both lint errors, and an `#[expect]` that no longer matches a diagnostic fails the build. A manifest-level override has no reason field, so put the reason in a comment beside it.

Cognitive complexity comes from the nursery group at Clippy's default threshold of 25. Do not lower it without a concrete project reason, documented with the setting.

Append this documentation rule to `## Repository Rules` in the project's `AGENTS.md`:

```markdown
- Document public and cross-module items with a concise brief, adding `# Errors`, `# Panics`, and `# Safety` sections only when applicable. Omit empty contract sections, redundant prose across levels, and `# Examples` unless they materially clarify use.
```

Typical checks:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings
cargo test
```

Add `--workspace` and the planned feature/platform selections where appropriate. Use `--all-features` only when that combination is supported. Ensure test targets are linted so the configured exemptions and remaining checks are exercised.

Primary references: [Cargo lint configuration](https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section), [workspace lint inheritance](https://doc.rust-lang.org/cargo/reference/workspaces.html#the-lints-table), [Clippy test exemptions](https://doc.rust-lang.org/clippy/lint_configuration.html#allow-unwrap-in-tests), [`allow_attributes`](https://rust-lang.github.io/rust-clippy/master/index.html#allow_attributes), [cognitive-complexity limitations](https://rust-lang.github.io/rust-clippy/master/index.html#cognitive_complexity).
