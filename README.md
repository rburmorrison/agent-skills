# Agent Skills

My personal collection of agent skills. Each skill lives in `skills/<category>/<name>/` and is defined by a `SKILL.md` file.

## Skills

**Engineering**:

- [gitmoji-commits](skills/engineering/gitmoji-commits/SKILL.md) - Creates subject-first GitMoji commits from repository changes.
- [plan-changes](skills/engineering/plan-changes/SKILL.md) - Resolves consequential decisions before editing and plans concrete operations, contracts, and failure boundaries.
- [implement-changes](skills/engineering/implement-changes/SKILL.md) - Implements agreed changes with clear responsibility boundaries, readable behavior tests, automatic review, and a concise handoff.
- [review-changes](skills/engineering/review-changes/SKILL.md) - Reviews a completed change or targeted fixes against the plan using fresh context and a supplied brief.
- [setup-project](skills/engineering/setup-project/SKILL.md) - Establishes strict project tooling, with Rust and Python profiles.

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

## Personal guidance

After installing the engineering skills, copy or merge [personal-engineering.md](guidance/personal-engineering.md) into your agent's personal instructions. For Codex, use `~/.codex/AGENTS.md`; preserve any existing instructions. Skill installation alone does not install this guidance.

The shared rules are language-agnostic. Language-specific settings live in the setup skill's [Rust](skills/engineering/setup-project/references/rust.md) and [Python](skills/engineering/setup-project/references/python.md) profiles. Independent review requires a host that supports reviewer agents; the implementation skill reports when that capability is unavailable.
