# Agent Skills

My personal collection of agent skills. Each skill lives in `skills/<category>/<name>/` and is defined by a `SKILL.md` file.

## Skills

**Engineering**:

- [gitmoji-commits](skills/engineering/gitmoji-commits/SKILL.md) - Creates subject-first GitMoji commits from repository changes.
- [setup-project](skills/engineering/setup-project/SKILL.md) - Establishes strict project tooling and a starter `AGENTS.md`, with Rust and Python profiles.
- [agents-md](skills/engineering/agents-md/SKILL.md) - Creates and edits `AGENTS.md` and `CLAUDE.md` files as short rule lists with a dedicated verification section, preserving the format of existing files.

**Documentation**:

- [visual-explainers](skills/documentation/visual-explainers/SKILL.md) - Creates standalone, offline HTML explainers from a JSON document using built-in components, diagrams, interactive charts, and math. A Python 3.11+ builder embeds all assets; the user chooses the content, structure, and [theme](docs/visual-explainers/themes.md).

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
npx skills add rburmorrison/agent-skills --global --skill setup-project
npx skills add rburmorrison/agent-skills --global --skill agents-md

# Documentation
npx skills add rburmorrison/agent-skills --global --skill visual-explainers
```

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
