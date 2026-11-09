---
name: setup-project
description: Establish a new project's package-manager workflow, strict formatting, linting, type checking, and verification commands using the relevant language profile.
---

# Setup Project

Use for new projects or an explicitly requested tooling setup. Keep existing-project feature work within its established tooling unless changing that tooling is part of the agreed plan.

## Plan the Setup

Inspect the destination and applicable instructions before creating files. Establish the project kind, supported language/runtime versions, package manager, and required checks. Ask consequential questions one at a time. Select compatible tools during planning; setup writes start only when implementation is authorized.

Keep the shared policy language-agnostic: formatting, deliberate strict linting, static type checks where applicable, readable behavior tests, and repeatable verification. Read only the relevant profile:

- Rust: [profile](references/rust.md), with Cargo lint and Clippy configuration assets.
- Python: [profile](references/python.md), with Ruff and strict type-checking configuration assets.
- Other languages: use the ecosystem's package manager and supported strict tooling to achieve the same outcomes. Verify current primary documentation; do not transplant Rust/Python rules or thresholds literally.

Profiles are defaults for new projects. Respect explicit user choices and supported-version constraints. Resolve conflicts during planning. A tool-specific complexity score is an inspection signal, not a proof of readability or an equivalent measure across languages.

## Initialize and Configure

Use the package manager's initialization and dependency commands. Resolve packages from actual package information with the agreed compatibility constraints; do not invent versions or add dependencies by hand. Preserve the package manager's lockfile policy.

Read the selected assets before applying them. Merge their configuration tables deliberately; do not replace an existing manifest or append duplicate TOML tables. Adapt package/workspace scope and supported-version settings to the planned project. Assets contain tooling configuration, not application dependencies.

Enable a deliberate strict rule set, including type checking where applicable. Encode appropriate test exemptions in the tooling. Every suppression or exception must have a specific reason beside its configuration or use site. Prefer native justification syntax. Never disable broad groups or verification commands simply to make the new project pass.

Give dependencies, source files, and modules homes justified by the actual project's responsibilities. Do not create speculative directories, placeholder abstractions, or redundant automation layers.

## Verify and Hand Off

Run formatting checks, linting, type checks where applicable, and relevant tests with the configured project tools. Check the actual configuration is discovered and covers the intended production and test code. Adapt feature/platform coverage to supported combinations.

Make the agreed verification commands easy to run through existing project or CI mechanisms. When adding CI, use the same tool versions and commands exercised locally. Apply `code-authoring`'s documentation boundary: usage-documentation edits must be planned accuracy corrections or explicitly requested additions; setup alone does not authorize new guides or facts.

Report what was configured and verified, plus material limitations. If a required tool or capability is unavailable, do not silently weaken the profile; finish independent setup work and clearly report the roadblock. Use the implementation and independent-review workflow for non-trivial setup changes when those skills are available.
