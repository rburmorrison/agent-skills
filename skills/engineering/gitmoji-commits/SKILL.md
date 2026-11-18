---
name: gitmoji-commits
description: Create GitMoji commits from repository changes, using official GitMoji shortcodes, recent commit style, rare optional bodies, and heredoc commit commands. Use when the user asks to commit changes, split changes into commits, or suggest a commit message.
---

# GitMoji Commits

Use this skill when the user asks to suggest, prepare, or make commits using GitMoji conventions.

## Choose the Mode

Decide the mode from the user's request before running anything:

- **Commit mode** is the default. Use it when the user asks to commit, make commits, or prepare commits. Choose the messages and file groups, then commit without asking the user to approve them.
- **Suggest mode** applies when the user asks only for a message or a plan: "suggest", "draft", "propose", "what should the commit message be", or "don't commit yet". Inspect the repository and choose messages and file groups the same way, then show them in the Suggestion Format. Do not run `git add` or `git commit`.

## Safety Rules

These apply in both modes unless the user explicitly asks otherwise:

- Never run `git push`, `git commit --amend`, `git rebase`, `git reset`, `git stash`, or `git checkout` on files.
- Never pass `--no-verify` or skip hooks in any other way.
- Never use `git add -A`, `git add .`, or `git commit -a` except in the Empty Repository flow.
- If a commit command fails, including a failing hook, stop. Show the command's error output, say which commits already succeeded, and ask how to proceed. Do not retry, fix the code, or change the staged files on your own.

## Inspect First

Before choosing any commit message, inspect the repository:

```bash
git status
git status --short
git diff --stat
git diff --staged --stat
git log -10 --oneline
```

Then inspect only the relevant diffs needed to understand the changed files and their grouping:

```bash
git diff -- path/to/file
git diff --staged -- path/to/file
```

For untracked files, inspect file contents only as needed to decide whether they belong in a commit.

Read each `git status --short` line as two status columns followed by the path:

- The first column is the staged change and the second is the unstaged change. A space means no change in that column.
- `??` marks an untracked file.
- `U` in either column, `AA`, or `DD` marks an unresolved conflict.
- Any other line with a letter in both columns, such as `MM` or `AM`, means the file has staged and unstaged changes.

## Stop Conditions

Check these in order after inspecting. When one applies, stop and return its message exactly, in either mode.

If `git status` fails because the current directory is not a git repository:

```text
I can't create a GitMoji commit because this directory is not a git repository.
```

If `git status` says a merge, rebase, cherry-pick, revert, or bisect is in progress, or lists unmerged paths:

```text
I can't create a GitMoji commit because a merge, rebase, cherry-pick, revert, or bisect is in progress.
```

If `git status --short` prints nothing:

```text
I can't create a GitMoji commit because there are no changes to commit.
```

If the user asked for staged-only commits and `git diff --staged --stat` prints nothing:

```text
I can't create a GitMoji commit because nothing is staged.
```

## Message Rules

- Use GitMoji shortcodes in commit messages, suggestions, and commands. Use literal emoji only in the post-commit user-facing record described below.
- Choose the shortcode by following the Choosing a Shortcode steps below, and choose only from the Shortcode Reference table at the end of this skill. Do not recall shortcodes from memory.
- Use this subject format: `:shortcode: Imperative message`.
- Do not use scopes.
- Use imperative mood for subjects: "Add", "Fix", "Update", "Remove", "Document", "Refactor".
- Keep subjects specific: name what changed, not that something changed.
- Keep the message after the shortcode to 72 characters or fewer, and do not end it with a period.
- Let this skill's rules override conflicting recent commit style.
- Use the last 10 commits only for tone, capitalization, vocabulary, and typical message length.

Priority order:

1. The user's explicit instruction.
2. This skill's format and safety rules.
3. Bundled GitMoji shortcode usage.
4. Repository style from the last 10 commits.

## Files to Leave Out

- Do not inspect or include ignored files unless the user explicitly asks. If the user asks to include ignored files, ask for confirmation before using `git add -f`.
- Leave an untracked or newly added file out of every commit when it looks like a secret or like generated output:
  - Secrets: `.env` files, private keys such as `*.pem`, `*.key`, and `id_rsa`, credential or token files, and any file whose contents include a real password, token, or API key.
  - Generated output: dependency and build directories such as `node_modules/`, `dist/`, `build/`, `target/`, and `__pycache__/`, plus logs, caches, and editor or operating-system files such as `.DS_Store`.
- Commit the remaining files, or in suggest mode suggest commits for them. Then list each file left out and the reason under `Left uncommitted:`, after the Closing Report's hashes or at the end of the Suggestion Format.
- If a tracked file's diff adds what looks like a real password, token, or API key, stop and ask before committing that file.

## Grouping Changes

Group changed files into one or more coherent commits:

- Keep unrelated changes in separate commits when the diff supports it.
- By default, commit the full working tree: staged changes, unstaged tracked changes, and untracked files, except Files to Leave Out. Choose which files go in each commit; do not require the user to stage files first.
- When the user explicitly asks to commit only staged changes, make exactly one commit from the staged content and leave everything else untouched.
- Avoid partial-file staging. If one file contains changes that belong to different commits, ask the user to split the file or confirm a single commit for that file.
- In the default flow, if a file has both staged and unstaged changes, stop and ask whether to commit the full file or only the staged content. A staged-only request already answers this: commit the staged content.

## Commit Bodies

Most commits should be subject-only. Add a body only in rare exception cases:

- The user explicitly asks for a body.
- The subject cannot explain why the change was made.
- The change has migration, setup, deployment, or manual follow-up details.
- The change is breaking, security-sensitive, or operationally risky.
- Multiple files changed for a non-obvious shared reason that cannot fit in a clear subject.

Do not add a body just because recent commits commonly use bodies. If a body is already justified by the rules above, use recent commits only for body tone and length.

When a body is used:

- Show it as block-quoted bullets in the commit record.
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

## Empty Repository

If `git log -10 --oneline` fails because the repository has no commits yet, use exactly one commit:

```text
:tada: Initial commit
```

Initial commit rules:

- Do not split the initial commit unless the user explicitly asks.
- Do not add a commit body unless the user explicitly asks.
- If any file matches Files to Leave Out, stop and ask before committing, because `git add -A` would include it.
- Show `- All Repository Files` in the record instead of individual paths.
- Stage with `git add -A`.

Initial commit command:

```bash
git add -A && git commit -F - <<'EOF'
:tada: Initial commit
EOF
```

After the initial commit succeeds, show this record, followed by the Closing Report:

```markdown
I made the following commit:

---

🎉 Initial commit

- All Repository Files

---
```

## Commit

In commit mode, after choosing shortcodes, subjects, bodies, and file groups, commit immediately. Do not ask the user to approve those choices.

Immediately before the first commit, run `git status --short` again. It must show the same paths and status codes as the inspection. If anything differs, the working tree changed while you worked: stop and ask.

After each commit, run `git status --short` again. It must show exactly these files, with none missing and none added:

- The files of the commits still to make.
- The files left out under Files to Leave Out.
- The files the user asked to leave untouched, such as unstaged and untracked files in a staged-only commit.

If a file is missing or an extra file appears, stop and ask.

Run one combined shell command per commit. Use heredoc commit messages for every commit, including subject-only commits.

For normal working-tree commits, name the commit's files after `--` in the `git commit` command. Git then commits exactly those files as they are in the working tree, whether their changes are staged or not, and leaves every other file out, including files that were already staged:

- List every file of the commit after `--`, including deleted files.
- For a moved or renamed file, list both the old path and the new path.
- Run `git add` first only for the commit's untracked files (`??`), because `git commit` rejects a path Git does not know. Leave `git add` out when the commit has no untracked files.
- Wrap a path in double quotes when it contains spaces.
- Keep `-F -` before `--`. Everything after `--` is read as a path.

Subject-only command for files Git already tracks:

```bash
git commit -F - -- skills/engineering/gitmoji-commits/SKILL.md README.md <<'EOF'
:memo: Document GitMoji commit workflow
EOF
```

Exception-case command with a body, where `tests/webhooks.test.ts` is untracked:

```bash
git add tests/webhooks.test.ts && git commit -F - -- src/webhooks.ts tests/webhooks.test.ts <<'EOF'
:boom: Require signed webhook payloads

- Required HMAC verification before processing webhook events.
- Updated local webhook setup to require signed test payloads.
EOF
```

Staged-only command, with no `git add` and no paths, so that Git commits the staged content and unstaged changes stay out:

```bash
git commit -F - <<'EOF'
:bug: Fix expired session redirect
EOF
```

After the commits succeed, show the framed record and then the closing report, both described below.

## Confirmation Format

Use this format only after the commit succeeds, as a record of what was done. The frame ends after the file list.

In this user-facing record only, display the subject's GitMoji as its literal emoji. Copy the emoji from the Emoji column of the shortcode's row in the Shortcode Reference table; for example, `:lock:` becomes 🔒. Keep the rest of the subject unchanged and retain shortcodes everywhere else, including the stored commit message and commands.

For one subject-only commit:

```markdown
I made the following commit:

---

📝 Document GitMoji commit workflow

- skills/engineering/gitmoji-commits/SKILL.md
- README.md

---
```

For one commit with a body:

```markdown
I made the following commit:

---

💥 Require signed webhook payloads

> - Required HMAC verification before processing webhook events.
> - Updated local webhook setup to require signed test payloads.

- src/webhooks.ts
- tests/webhooks.test.ts

---
```

For multiple commits:

```markdown
I made the following commits:

---

✨ Add repository import workflow

- src/importer.ts
- src/repository.ts

---

✅ Cover importer edge cases

- tests/importer.test.ts
- tests/fixtures/import-source.json

---
```

Use the framed `---` format for every commit record, including subject-only commits.

### Closing Report

After the frame, report the commit hashes and the final working tree state. Get the hashes, oldest first, with `git log -N --reverse --format='%h %s'`, where `N` is the number of commits you made. Then run `git status --short` and show its output, or `Working tree clean.` when it prints nothing. Add `Left uncommitted:` only when files were left out.

```markdown
- `4d43b44` :sparkles: Add repository import workflow
- `8722490` :white_check_mark: Cover importer edge cases

Left uncommitted:

- `.env` (looks like a secret)

Remaining `git status --short`:

    ?? .env
```

## Suggestion Format

Use this format in suggest mode. Keep shortcodes, not literal emoji, so the user can copy each message as it would be committed. Show a body the same way as in the Confirmation Format.

```markdown
I suggest the following commits. Nothing was committed.

---

:sparkles: Add repository import workflow

- src/importer.ts
- src/repository.ts

---

:white_check_mark: Cover importer edge cases

- tests/importer.test.ts
- tests/fixtures/import-source.json

---
```

For a single commit, write "I suggest the following commit. Nothing was committed."

When files were left out, end with the same `Left uncommitted:` list as the Closing Report:

```markdown
Left uncommitted:

- `.env` (looks like a secret)
```

## Choosing a Shortcode

Choose one shortcode per commit, in this order:

1. State the commit's primary purpose in one sentence: the reason the change exists. Tests, documentation, and configuration that only support that purpose do not change the shortcode. A feature committed with its tests is `:sparkles:`, not `:white_check_mark:`.
2. If the commit breaks existing callers, users, or stored data, use `:boom:` whatever else it does.
3. Check the Common Choices below. Most commits match one of them.
4. If a row in the full Shortcode Reference describes the whole commit more exactly, use that row instead. For example, a commit that only adds a database migration is `:card_file_box:`, not `:sparkles:`.
5. If two rows still fit, apply the Tie-Breakers.

Never invent a shortcode or use one that is missing from the Shortcode Reference.

### Common Choices

| Shortcode | Use when the commit primarily... |
| --- | --- |
| `:sparkles:` | Adds behavior a user or caller can now use. |
| `:bug:` | Corrects behavior that was wrong. |
| `:recycle:` | Restructures code without changing behavior. |
| `:memo:` | Changes documentation files such as READMEs and guides. |
| `:white_check_mark:` | Changes only tests. |
| `:wrench:` | Changes only configuration files. |
| `:fire:` | Removes code or files that were still in use. |
| `:zap:` | Makes existing behavior faster or lighter. |
| `:lipstick:` | Changes only how the UI looks. |
| `:arrow_up:` | Raises the version of an existing dependency. |
| `:heavy_plus_sign:` | Adds a new dependency. |
| `:truck:` | Only moves or renames files or paths. |

### Tie-Breakers

| When choosing between | Use |
| --- | --- |
| `:bug:`, `:adhesive_bandage:`, `:ambulance:` | `:ambulance:` only for an urgent fix to a failure in production. `:adhesive_bandage:` for a trivial fix of a few lines to a minor issue. `:bug:` for every other fix. |
| `:bug:`, `:lock:` | `:lock:` when the wrong behavior is a security or privacy weakness. |
| `:bug:`, `:pencil2:` | `:pencil2:` when the only fix is spelling or wording, in code or in documentation. |
| `:recycle:`, `:art:` | `:art:` for formatting and layout only, such as whitespace, ordering, and line breaks. `:recycle:` when names, functions, or modules are reorganized. |
| `:recycle:`, `:building_construction:` | `:building_construction:` only when the boundaries between major components change. |
| `:recycle:`, `:truck:` | `:truck:` when files only move or change name. `:recycle:` when their contents are also reorganized. |
| `:fire:`, `:coffin:` | `:coffin:` when the removed code was already unused. `:fire:` when it was still in use. |
| `:fire:`, `:heavy_minus_sign:` | `:heavy_minus_sign:` when the removal is a dependency. |
| `:memo:`, `:bulb:` | `:bulb:` when only comments inside source files change. `:memo:` for documentation files. |
| `:memo:`, `:speech_balloon:` | `:speech_balloon:` when the text is shown by the running program, such as labels and messages. |
| `:white_check_mark:`, `:test_tube:` | `:test_tube:` only when the added test is expected to fail for now. |
| `:white_check_mark:`, `:clown_face:`, `:camera_flash:` | `:clown_face:` when only mocks change. `:camera_flash:` when only snapshots change. `:white_check_mark:` for other test changes. |
| `:wrench:`, `:hammer:`, `:construction_worker:` | `:construction_worker:` for CI pipeline definitions. `:hammer:` for scripts developers run. `:wrench:` for other configuration. |
| `:wrench:`, `:see_no_evil:` | `:see_no_evil:` when only `.gitignore` changes. |
| `:construction_worker:`, `:green_heart:` | `:green_heart:` when the change repairs a failing CI build. `:construction_worker:` for other CI changes. |
| `:arrow_up:`, `:arrow_down:`, `:pushpin:` | `:pushpin:` when a version range becomes an exact version. Otherwise `:arrow_up:` for a higher version and `:arrow_down:` for a lower one. |
| `:sparkles:`, `:children_crossing:` | `:children_crossing:` when an existing feature becomes easier to use and no new capability is added. |
| `:sparkles:`, `:necktie:` | `:sparkles:` for new capability. `:necktie:` when an existing business rule changes. |
| `:lipstick:`, `:dizzy:`, `:iphone:` | `:dizzy:` for animations and transitions. `:iphone:` for layout across screen sizes. `:lipstick:` for other visual changes. |
| `:lock:`, `:passport_control:`, `:closed_lock_with_key:` | `:passport_control:` for roles and permissions. `:closed_lock_with_key:` for stored secrets. `:lock:` for other security fixes. |

## Shortcode Reference

This table is a bundled snapshot of the official list at https://gitmoji.dev/. Use it instead of reaching online.

Use shortcodes exactly as written. The Emoji column exists only for the user-facing record shown after a commit.

| Shortcode | Emoji | Use when the commit primarily... |
| --- | --- | --- |
| `:art:` | 🎨 | Improves code structure or formatting. |
| `:zap:` | ⚡ | Improves performance. |
| `:fire:` | 🔥 | Removes code or files. |
| `:bug:` | 🐛 | Fixes a bug. |
| `:ambulance:` | 🚑 | Applies a critical hotfix. |
| `:sparkles:` | ✨ | Introduces new features. |
| `:memo:` | 📝 | Adds or updates documentation. |
| `:rocket:` | 🚀 | Deploys changes. |
| `:lipstick:` | 💄 | Adds or updates UI or style files. |
| `:tada:` | 🎉 | Begins a project. |
| `:white_check_mark:` | ✅ | Adds, updates, or passes tests. |
| `:lock:` | 🔒 | Fixes security or privacy issues. |
| `:closed_lock_with_key:` | 🔐 | Adds or updates secrets. |
| `:bookmark:` | 🔖 | Adds release or version tags. |
| `:rotating_light:` | 🚨 | Fixes compiler or linter warnings. |
| `:construction:` | 🚧 | Marks work in progress. |
| `:green_heart:` | 💚 | Fixes CI build issues. |
| `:arrow_down:` | ⬇️ | Downgrades dependencies. |
| `:arrow_up:` | ⬆️ | Upgrades dependencies. |
| `:pushpin:` | 📌 | Pins dependencies to specific versions. |
| `:construction_worker:` | 👷 | Adds or updates CI build systems. |
| `:chart_with_upwards_trend:` | 📈 | Adds or updates analytics or tracking code. |
| `:recycle:` | ♻️ | Refactors code. |
| `:heavy_plus_sign:` | ➕ | Adds a dependency. |
| `:heavy_minus_sign:` | ➖ | Removes a dependency. |
| `:wrench:` | 🔧 | Adds or updates configuration files. |
| `:hammer:` | 🔨 | Adds or updates development scripts. |
| `:globe_with_meridians:` | 🌐 | Changes internationalization or localization. |
| `:pencil2:` | ✏️ | Fixes typos. |
| `:poop:` | 💩 | Writes code that needs improvement. |
| `:rewind:` | ⏪ | Reverts changes. |
| `:twisted_rightwards_arrows:` | 🔀 | Merges branches. |
| `:package:` | 📦 | Adds or updates compiled files or packages. |
| `:alien:` | 👽 | Updates code because of external API changes. |
| `:truck:` | 🚚 | Moves or renames files, paths, routes, or other resources. |
| `:page_facing_up:` | 📄 | Adds or updates a license. |
| `:boom:` | 💥 | Introduces breaking changes. |
| `:bento:` | 🍱 | Adds or updates assets. |
| `:wheelchair:` | ♿ | Improves accessibility. |
| `:bulb:` | 💡 | Adds or updates source code comments. |
| `:beers:` | 🍻 | Writes code drunkenly. Avoid unless the repository already uses it intentionally. |
| `:speech_balloon:` | 💬 | Adds or updates text and literals. |
| `:card_file_box:` | 🗃️ | Performs database-related changes. |
| `:loud_sound:` | 🔊 | Adds or updates logs. |
| `:mute:` | 🔇 | Removes logs. |
| `:busts_in_silhouette:` | 👥 | Adds or updates contributors. |
| `:children_crossing:` | 🚸 | Improves user experience or usability. |
| `:building_construction:` | 🏗️ | Makes architectural changes. |
| `:iphone:` | 📱 | Works on responsive design. |
| `:clown_face:` | 🤡 | Adds or updates mocks. |
| `:egg:` | 🥚 | Adds or updates an easter egg. |
| `:see_no_evil:` | 🙈 | Adds or updates a `.gitignore` file. |
| `:camera_flash:` | 📸 | Adds or updates snapshots. |
| `:alembic:` | ⚗️ | Performs experiments. |
| `:mag:` | 🔍 | Improves SEO. |
| `:label:` | 🏷️ | Adds or updates types. |
| `:seedling:` | 🌱 | Adds or updates seed files. |
| `:triangular_flag_on_post:` | 🚩 | Adds, updates, or removes feature flags. |
| `:goal_net:` | 🥅 | Catches errors. |
| `:dizzy:` | 💫 | Adds or updates animations and transitions. |
| `:wastebasket:` | 🗑️ | Deprecates code that needs cleanup. |
| `:passport_control:` | 🛂 | Changes authorization, roles, or permissions. |
| `:adhesive_bandage:` | 🩹 | Applies a simple fix for a non-critical issue. |
| `:monocle_face:` | 🧐 | Performs data exploration or inspection. |
| `:coffin:` | ⚰️ | Removes dead code. |
| `:test_tube:` | 🧪 | Adds a failing test. |
| `:necktie:` | 👔 | Adds or updates business logic. |
| `:stethoscope:` | 🩺 | Adds or updates health checks. |
| `:bricks:` | 🧱 | Changes infrastructure. |
| `:technologist:` | 🧑‍💻 | Improves developer experience. |
| `:money_with_wings:` | 💸 | Adds sponsorships or money-related infrastructure. |
| `:thread:` | 🧵 | Adds or updates multithreading or concurrency code. |
| `:safety_vest:` | 🦺 | Adds or updates validation code. |
| `:airplane:` | ✈️ | Improves offline support. |
| `:t-rex:` | 🦖 | Adds backwards compatibility. |
