---
name: gitmoji-commits
description: Create GitMoji commit proposals from repository changes, using official GitMoji shortcodes, recent commit style, explicit user confirmation, rare optional bodies, and heredoc commit commands.
---

# GitMoji Commits

Use this skill when the user asks to suggest, prepare, or make commits using GitMoji conventions.

## Inspect First

Before proposing any commit message, inspect the repository:

```bash
git status --short
git diff --stat
git diff --staged --stat
git log -10 --oneline
```

Then inspect only the relevant diffs needed to understand the changed files and proposed grouping:

```bash
git diff -- path/to/file
git diff --staged -- path/to/file
```

For untracked files, inspect file contents only as needed to decide whether they belong in the proposal.

If the current directory is not a git repository, stop and return exactly:

```text
I can't create a GitMoji commit proposal because this directory is not a git repository.
```

If there are no tracked, staged, or untracked changes to commit, stop and return exactly:

```text
I can't create a GitMoji commit proposal because there are no changes to commit.
```

## Message Rules

- Use GitMoji shortcodes only, never literal emoji characters.
- Before choosing a shortcode, read [references/gitmoji-shortcodes.md](references/gitmoji-shortcodes.md) and choose from that bundled snapshot.
- Use this subject format: `:shortcode: Imperative message`.
- Do not use scopes.
- Use imperative mood for subjects: "Add", "Fix", "Update", "Remove", "Document", "Refactor".
- Keep subjects concise and specific.
- Let this skill's rules override conflicting recent commit style.
- Use the last 10 commits only for tone, capitalization, vocabulary, and typical message length.

Priority order:

1. The user's explicit instruction.
2. This skill's format and safety rules.
3. Bundled GitMoji shortcode usage.
4. Repository style from the last 10 commits.

## Gotchas

- Do not inspect or include ignored files unless the user explicitly asks. If the user asks to include ignored files, ask for confirmation before using `git add -f`.
- If staged and unstaged changes touch the same file, stop and ask whether to commit the full file or only the staged content.
- For empty repositories, use the exact initial commit flow below.

## Empty Repository

If `git log -10 --oneline` fails because the repository has no commits yet, propose exactly one commit:

```text
:tada: Initial commit
```

Initial commit rules:

- Do not split the initial commit unless the user explicitly asks.
- Do not add a commit body unless the user explicitly asks.
- Show `- All Repository Files` in the proposal instead of individual paths.
- After confirmation, stage with `git add -A`.

Initial commit proposal:

```markdown
I would like to make the following commit:

---

:tada: Initial commit

- All Repository Files

---

Let me know if you'd like me to commit these changes.
```

Initial commit command:

```bash
git add -A && git commit -F - <<'EOF'
:tada: Initial commit
EOF
```

## Grouping Changes

Group changed files into one or more coherent commits:

- Keep unrelated changes in separate commits when the diff supports it.
- Commit only staged changes when the user explicitly asks for staged-only commits.
- Otherwise, propose commits from the full working tree, including unstaged tracked changes and untracked files.
- Choose which files should be staged for each proposed commit; do not require the user to stage files first.
- Avoid partial-file staging. If one file contains changes that belong to different commits, ask the user to split the file or confirm a single commit for that file.
- Preserve the user's staging intent when they explicitly ask to commit staged changes.

## Commit Bodies

Most commits should be subject-only. Add a body only in rare exception cases:

- The user explicitly asks for a body.
- The subject cannot explain why the change was made.
- The change has migration, setup, deployment, or manual follow-up details.
- The change is breaking, security-sensitive, or operationally risky.
- Multiple files changed for a non-obvious shared reason that cannot fit in a clear subject.

Do not add a body just because recent commits commonly use bodies. If a body is already justified by the rules above, use recent commits only for body tone and length.

When a body is used:

- Show it as block-quoted bullets in the confirmation proposal.
- Use past tense.
- End each bullet with punctuation.
- Use 1-3 bullets in normal cases.
- Keep the body factual and specific.
- Use a bulleted body in the actual commit message too.

Example body:

```markdown
> - Required HMAC verification before processing webhook events.
> - Updated local webhook setup to require signed test payloads.
```

## Confirmation Format

Always ask for confirmation before staging or committing. Do not run `git add` or `git commit` before the user confirms.

For one subject-only commit:

```markdown
I would like to make the following commit:

---

:memo: Document GitMoji commit workflow

- skills/gitmoji-commits/SKILL.md
- skills/gitmoji-commits/references/gitmoji-shortcodes.md

---

Let me know if you'd like me to commit these changes.
```

For one commit with a body:

```markdown
I would like to make the following commit:

---

:boom: Require signed webhook payloads

> - Required HMAC verification before processing webhook events.
> - Updated local webhook setup to require signed test payloads.

- src/webhooks.ts
- tests/webhooks.test.ts

---

Let me know if you'd like me to commit these changes.
```

For multiple commits:

```markdown
I would like to make the following commits:

---

:sparkles: Add repository import workflow

- src/importer.ts
- src/repository.ts

---

:white_check_mark: Cover importer edge cases

- tests/importer.test.ts
- tests/fixtures/import-source.json

---

Let me know if you'd like me to commit these changes.
```

Use the framed `---` format for every proposal, including subject-only commits.

## After Confirmation

Before committing, always re-run `git status --short` and compare it to the confirmed proposal.

If files were added, removed, renamed, or modified outside the confirmed proposal, stop and ask for confirmation again.

Run one combined harness command per commit. Use heredoc commit messages for every commit, including subject-only commits.

For normal working-tree commits, stage only the files confirmed for that commit with `git add path/to/file ...`, then commit. Do not use `git add -A` except for the initial commit flow or when the user explicitly confirms staging the entire working tree.

Subject-only command:

```bash
git add skills/gitmoji-commits/SKILL.md skills/gitmoji-commits/references/gitmoji-shortcodes.md && git commit -F - <<'EOF'
:memo: Document GitMoji commit workflow
EOF
```

Exception-case command with body:

```bash
git add src/webhooks.ts tests/webhooks.test.ts && git commit -F - <<'EOF'
:boom: Require signed webhook payloads

- Required HMAC verification before processing webhook events.
- Updated local webhook setup to require signed test payloads.
EOF
```

After committing, report the commit hash or hashes and the final `git status --short`.
