## Engineering Workflow

Before editing source code, tests, or their documentation, load the `code-authoring` skill and apply its preferences, including how to involve me while the work happens. Use `setup-project` when establishing a new project.

Add, remove, and upgrade dependencies with the ecosystem's own command, such as `cargo add` or `uv add`, instead of editing the manifest or lockfile by hand.

Verify changes as a user would, through the actual CLI, UI, API, or caller when feasible, and report what remains unverified. Never claim a check passed unless it ran.

These are defaults: explicit task instructions override them. They do not authorize additional scope, commits, publishing, installation, or external actions. If a named skill is unavailable, say so instead of claiming it was used.
