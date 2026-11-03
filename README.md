# Agent Skills

My personal collection of agent skills. Each skill lives in `skills/<category>/<name>/` and is defined by a `SKILL.md` file.

## Skills

**Engineering**:

- [gitmoji-commits](skills/engineering/gitmoji-commits/SKILL.md) - Creates subject-first GitMoji commits from repository changes.
- [plan-changes](skills/engineering/plan-changes/SKILL.md) - Resolves consequential decisions before editing and specifies substantial operations, their data contracts, and I/O ownership before implementation.
- [implement-changes](skills/engineering/implement-changes/SKILL.md) - Implements agreed changes with clear responsibility boundaries, readable behavior tests, automatic review, and a concise handoff.
- [review-changes](skills/engineering/review-changes/SKILL.md) - Reviews a completed change or targeted fixes against the plan using fresh context and a supplied brief; reads the relevant documentation skills when reviewing documentation.
- [setup-project](skills/engineering/setup-project/SKILL.md) - Establishes strict project tooling, with Rust and Python profiles.
- [document-usage](skills/engineering/document-usage/SKILL.md) - Keeps quick-start READMEs, built-in help, and concise user guides aligned with the software.
- [document-code](skills/engineering/document-code/SKILL.md) - Maintains concise interface briefs and contract sections, omits unnecessary prose bodies, and keeps implementation comments selective while respecting documentation lints.
- [align-codebase](skills/engineering/align-codebase/SKILL.md) (manual) - Plans and applies a scoped, behavior-preserving alignment of an existing codebase with these conventions.
- [implement-verified-steps](skills/engineering/implement-verified-steps/SKILL.md) (manual) - Checks and independently reviews each planned step, with targeted follow-up only for concrete unresolved risks.

## Usage

Install all skills globally from this repository with the Skills CLI:

```bash
npx skills add rburmorrison/agent-skills --global
```

Omit `--global` to install skills for the current project instead.

Documentation reviews use `document-code` and `document-usage`; install them with `review-changes`.

Install skills globally by name:

```bash
# Engineering
npx skills add rburmorrison/agent-skills --global --skill gitmoji-commits
npx skills add rburmorrison/agent-skills --global --skill plan-changes
npx skills add rburmorrison/agent-skills --global --skill implement-changes
npx skills add rburmorrison/agent-skills --global --skill review-changes
npx skills add rburmorrison/agent-skills --global --skill setup-project
npx skills add rburmorrison/agent-skills --global --skill document-usage
npx skills add rburmorrison/agent-skills --global --skill document-code
npx skills add rburmorrison/agent-skills --global --skill align-codebase
npx skills add rburmorrison/agent-skills --global --skill implement-verified-steps
```

## Personal Guidance

After installing the engineering skills, copy or merge [personal-engineering.md](guidance/personal-engineering.md) into your agent's personal instructions, preserving any existing guidance. Skill installation alone does not install this guidance.

The shared rules are model-agnostic and language-agnostic. Language-specific settings live in the setup skill's [Rust](skills/engineering/setup-project/references/rust.md) and [Python](skills/engineering/setup-project/references/python.md) profiles. Independent review requires a host that supports reviewer agents; the implementation skill reports when that capability is unavailable.

The two manual workflows reuse the shared engineering skills. Select `align-codebase` or `implement-verified-steps` explicitly using your agent's skill invocation mechanism. Explicit task instructions can override the usual conventions or review cadence, while unaffected defaults remain in force.
