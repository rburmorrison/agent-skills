# Agent Skills

My personal collection of agent skills. Each skill lives in `skills/<category>/<name>/` and is defined by a `SKILL.md` file.

## Skills

**Engineering**:

- `gitmoji-commits` - Proposes subject-first GitMoji commit messages from repository changes.

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
```
