---
name: agents-md
description: Create or edit agent instruction files, AGENTS.md and CLAUDE.md, keeping them short and explicit about what they mandate. Use for every change to one of these files, including adding, rewording, or removing a single rule, recording a project convention or verification command for future agents, and when the edit is one step of a larger request. Load before writing to the file.
---

# AGENTS.md

Use this skill before creating or editing an `AGENTS.md` or `CLAUDE.md` file at any level of a repository. These files are loaded into every agent session, so each line costs attention in all of them: keep the file short enough that a reader can tell at a glance what it requires and what it leaves open.

## Choose the File

- If neither file exists, create `AGENTS.md`. Do not create `CLAUDE.md`.
- If only one exists, edit that one. Do not rename it or add the other unless the user asks.
- If both exist, find which one holds the rules and edit that one. When `CLAUDE.md` only imports `AGENTS.md`, such as with a single `@AGENTS.md` line, leave it alone. When both hold rules, do not copy rules between them; add the rule to `AGENTS.md` and tell the user the two files overlap.
- If the user asks for both files, put the rules in `AGENTS.md` and make `CLAUDE.md` the single line `@AGENTS.md`.
- A nested file, such as `packages/api/AGENTS.md`, holds only rules specific to that directory. Do not repeat rules from a parent file.
- A user-level file outside a repository, such as `~/.claude/CLAUDE.md`, keeps the name its harness requires.

## Choose the Format

Read the whole file before editing it. It fits the standard format when its first line is `# AGENTS.md` and its rules are bulleted lists.

- **New file, or a file that fits:** use the Standard Format below.
- **Any other existing file:** follow the format it already has, including its headings, list style, and tone. Make only the requested change. Do not convert it to the standard format or tidy unrelated rules unless the user asks.

## Standard Format

````markdown
# AGENTS.md

This repository is a command-line importer for bank statements.

## Repository Rules

- Edit the readable sources in `assets/`, not the generated `.min.js` files; the build overwrites them.
- Keep parsers free of I/O so they can be tested with strings.

## Verification

```bash
# After any change
just check

# After editing JavaScript in assets/
just build-js
```
````

- Start the file with `# AGENTS.md`.
- Follow the title with one sentence saying what the repository is. Do not describe the architecture or directory layout.
- Write rules as bullets under `## Repository Rules`. Add further topic sections, with Title Case headings, only once that list would mix unrelated subjects.
- Put `## Verification` last. It holds one fenced `bash` block and nothing else: a comment line stating when to run, followed by the commands to run at that point, with a blank line between groups.
- Leave out `## Verification` when the repository has no commands to run.

## Write Rules

- Add a rule only when an agent would get it wrong without it. Leave out anything the code, the tool configuration, the README, or a linter already makes clear, and anything true of every project.
- Write one rule per bullet, as an imperative: "Run", "Edit", "Keep", "Do not".
- Name the trigger and the action, using exact paths and commands: "After editing X, run Y", not "keep generated files fresh".
- Add a short reason when the rule would otherwise look arbitrary, so agents can apply it to cases the rule does not name. Skip the reason when it is obvious.
- Keep a rule to one sentence where possible. If it needs a paragraph, link to a document instead.
- State each rule once. Before adding a rule, check for an existing one it duplicates or contradicts, and edit that one instead.
- Remove a rule when it stops being true. Do not leave it with a note that it is outdated.
- Do not record task history, change notes, or temporary instructions.

## Write Verification Commands

- Use commands that exist. Confirm each one in the repository's task runner, package scripts, or CI configuration before writing it; do not invent a command the project might have.
- Prefer the project's single aggregate check, such as `just check`, over listing its parts.
- Write each "when" comment as an event an agent can recognize: "After any change", "After editing files in `migrations/`", "Before committing".
- Anything that is not a command stays a bullet rule: "Review the README after changing a skill" belongs under the rules, not in the block.
- When a new command replaces a rule bullet that says the same thing, remove the bullet.

## Check the Result

Before finishing, read the edited file once more and confirm:

1. The change is only what was asked, in the file's own format.
2. No rule is duplicated, contradicted, or restated from a parent file.
3. In the standard format: the title is first, then the one-sentence description and `## Repository Rules`; `## Verification` is last and contains only the code block.
4. Every command and path in the file exists.

Tell the user which file was edited and what it now requires. If the file has grown long or mixes rules with descriptive prose, say so rather than rewriting it.
