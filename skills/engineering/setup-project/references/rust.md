# Rust tooling profile

Use the project's agreed Rust edition, minimum supported version, and toolchain. Check that the chosen toolchain supports the configuration. Create the package with Cargo and manage dependencies with `cargo add` and `cargo remove`; respect workspace dependency and lockfile conventions.

Merge [cargo-lints.toml](../assets/rust/cargo-lints.toml) into the manifest. It enables Clippy's default, pedantic, and nursery groups, plus the explicit unwrap and cognitive-complexity restrictions. The group priority lets specific, justified exceptions override a group when necessary.

For a Cargo workspace, put the shared settings under `[workspace.lints.clippy]` and enable `[lints] workspace = true` in each participating package. Verify the actual members inherit them; a root setting alone is insufficient.

Place [clippy.toml](../assets/rust/clippy.toml) at the appropriate project/workspace configuration root. It sets the cognitive-complexity threshold to 15 and allows unwraps and expects in tests. The production unwrap restriction also applies to const code. The expect test allowance preserves the relaxed test policy if a project additionally enables `expect_used`; this profile does not itself enable that lint.

Handle expected production failures explicitly; do not replace an unwrap with another panic merely to satisfy the rule. Test shortcuts are acceptable where they improve readability.

Clippy's cognitive-complexity lint is a rough signal with documented limitations. Inspect responsibilities and nesting instead of mechanically splitting code to reduce its score. Pedantic/nursery diagnostics also require judgment; a rare exception must name the rule, use the narrowest scope, and state the specific reason. Use native `reason` syntax when supported by the selected toolchain.

Typical checks:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings
cargo test
```

Add `--workspace` and the planned feature/platform selections where appropriate. Use `--all-features` only when that combination is supported. Ensure test targets are linted so the configured exemptions and remaining checks are exercised.

Primary references: [Cargo lint configuration](https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section), [workspace lint inheritance](https://doc.rust-lang.org/cargo/reference/workspaces.html#the-lints-table), [Clippy test exemptions](https://doc.rust-lang.org/clippy/lint_configuration.html#allow-unwrap-in-tests), [cognitive-complexity limitations](https://clippy.rust-lang.org/master/index.html#cognitive_complexity).
