# Agent Skills

My personal collection of agent skills. Each skill lives in `skills/<category>/<name>/` and is defined by a `SKILL.md` file.

## Skills

**Engineering**:

- [gitmoji-commits](skills/engineering/gitmoji-commits/SKILL.md) - Creates subject-first GitMoji commits from repository changes.
- [plan-changes](skills/engineering/plan-changes/SKILL.md) - Resolves consequential decisions before editing, designs toward a functional, declarative core with explicit effect boundaries, and assigns documentation facts to their owning interfaces.
- [code-authoring](skills/engineering/code-authoring/SKILL.md) - Writes code and planned documentation changes with clear responsibility boundaries, readable behavior tests, and automatic review; finishes code changes by checking existing documentation for needed accuracy updates.
- [review-changes](skills/engineering/review-changes/SKILL.md) - Reviews a completed change or targeted fixes using fresh context and the shared documentation guidance.
- [setup-project](skills/engineering/setup-project/SKILL.md) - Establishes strict project tooling, with Rust and Python profiles.
- [agents-md](skills/engineering/agents-md/SKILL.md) - Creates and edits `AGENTS.md` and `CLAUDE.md` files as short rule lists with a dedicated verification section, preserving the format of existing files.
- [align-codebase](skills/engineering/align-codebase/SKILL.md) (manual) - Plans and applies a scoped, behavior-preserving alignment of an existing codebase with these conventions.
- [implement-verified-steps](skills/engineering/implement-verified-steps/SKILL.md) (manual) - Checks and independently reviews each planned step, with targeted follow-up only for concrete unresolved risks.

**Documentation**:

- [visual-explainers](skills/documentation/visual-explainers/SKILL.md) - Creates standalone, offline HTML explainers from a JSON document using built-in components, diagrams, interactive charts, and math. A Python 3.11+ builder embeds all assets; the user chooses the content, structure, and [theme](docs/visual-explainers/themes.md).
- [code-explainers](skills/documentation/code-explainers/SKILL.md) - Explains a past change, a subsystem, or a concept in a codebase to its owner, using excerpts and diffs taken from the real source and git history. Renders with `visual-explainers`.

## Usage

Install all skills globally from this repository with the Skills CLI:

```bash
npx skills add rburmorrison/agent-skills --global
```

Omit `--global` to install skills for the current project instead.

Install skills globally by name:

```bash
# Engineering
npx skills add rburmorrison/agent-skills --global --skill gitmoji-commits
npx skills add rburmorrison/agent-skills --global --skill plan-changes
npx skills add rburmorrison/agent-skills --global --skill code-authoring
npx skills add rburmorrison/agent-skills --global --skill review-changes
npx skills add rburmorrison/agent-skills --global --skill setup-project
npx skills add rburmorrison/agent-skills --global --skill agents-md
npx skills add rburmorrison/agent-skills --global --skill align-codebase
npx skills add rburmorrison/agent-skills --global --skill implement-verified-steps

# Documentation
npx skills add rburmorrison/agent-skills --global --skill visual-explainers
npx skills add rburmorrison/agent-skills --global --skill code-explainers
```

## Engineering Workflow Guidance

Add the section in [engineering-workflow.md](guidance/engineering-workflow.md) to a global or project `AGENTS.md` or `CLAUDE.md`.

`plan-changes` delegates code exploration to your harness's exploration subagent when it has one. This lowers cost only when that agent runs on a cheaper model than the planner. Claude Code, Codex, and OpenCode do not run it on a low-cost model by default, so set the agent's model in your harness configuration.

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/),
[Just](https://just.systems/man/en/), and Node.js, then run:

```bash
just setup
just check
```

`just check` verifies Python formatting, Ruff lints, strict basedpyright types,
minified JavaScript and WOFF2 font freshness, Python behavior tests, and
JavaScript build, navigation, diagram, and chart tests. Use `just format` to
format Python files, or run `just lint`, `just typecheck`, and `just test`
separately. `just --list` shows all recipes.

The explainer builder requires Python 3.11+ and includes its syntax highlighter; generation and viewing work offline without installing dependencies.
Python development tools are managed by uv and pinned in `uv.lock`.
JavaScript development tools are managed by npm and pinned in `package-lock.json`.

## License

Copyright (C) 2026 Ryan Burmeister-Morrison.

Except for third-party material with its own license, this repository is licensed
under the GNU Affero General Public License, version 3 or (at your option) any
later version (`AGPL-3.0-or-later`). See [LICENSE](LICENSE) for the full terms.
This work is provided without any warranty, including the implied warranties of
merchantability or fitness for a particular purpose.

The bundled [Manrope](skills/documentation/visual-explainers/assets/fonts/manrope-OFL.txt),
[JetBrains Mono](skills/documentation/visual-explainers/assets/fonts/jetbrainsmono-OFL.txt),
[IBM Plex Sans](skills/documentation/visual-explainers/assets/fonts/ibmplexsans-OFL.txt),
[IBM Plex Mono](skills/documentation/visual-explainers/assets/fonts/ibmplexmono-OFL.txt),
and [Inter](skills/documentation/visual-explainers/assets/fonts/inter-OFL.txt)
fonts retain their SIL Open Font License 1.1 terms. The bundled
[Pygments archive](skills/documentation/visual-explainers/scripts/vendor/pygments-2.21.0.zip)
retains its BSD license and includes its upstream license and author notices.
