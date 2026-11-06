# Agent Skills

My personal collection of agent skills. Each skill lives in `skills/<category>/<name>/` and is defined by a `SKILL.md` file.

## Skills

**Engineering**:

- [gitmoji-commits](skills/engineering/gitmoji-commits/SKILL.md) - Creates subject-first GitMoji commits from repository changes.
- [plan-changes](skills/engineering/plan-changes/SKILL.md) - Resolves consequential decisions before editing, specifies responsibility boundaries, and assigns documentation facts to their owning interfaces.
- [implement-changes](skills/engineering/implement-changes/SKILL.md) - Implements agreed changes with clear responsibility boundaries, readable behavior tests, automatic review, and a concise handoff.
- [review-changes](skills/engineering/review-changes/SKILL.md) - Reviews a completed change or targeted fixes using fresh context and the shared documentation guidance.
- [setup-project](skills/engineering/setup-project/SKILL.md) - Establishes strict project tooling, with Rust and Python profiles.
- [document-usage](skills/engineering/document-usage/SKILL.md) - Maintains task-focused READMEs, built-in help, and user guides, with details placed where readers need them.
- [document-code](skills/engineering/document-code/SKILL.md) - Uses concise briefs and complete contracts, keeps type documentation self-contained, and reserves short bodies for exceptional caller-facing context.
- [align-codebase](skills/engineering/align-codebase/SKILL.md) (manual) - Plans and applies a scoped, behavior-preserving alignment of an existing codebase with these conventions.
- [implement-verified-steps](skills/engineering/implement-verified-steps/SKILL.md) (manual) - Checks and independently reviews each planned step, with targeted follow-up only for concrete unresolved risks.

**Documentation**:

- [visual-explainers](skills/documentation/visual-explainers/SKILL.md) - Creates standalone HTML explainers with reusable content components, diagrams, eight interactive chart types, and 72 SVG icons. Includes themes, full-width text, and responsive contents navigation with section tracking. A Python standard-library builder embeds fonts, images, and other assets for offline use; the user chooses the content and structure.

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
npx skills add rburmorrison/agent-skills --global --skill implement-changes
npx skills add rburmorrison/agent-skills --global --skill review-changes
npx skills add rburmorrison/agent-skills --global --skill setup-project
npx skills add rburmorrison/agent-skills --global --skill document-usage
npx skills add rburmorrison/agent-skills --global --skill document-code
npx skills add rburmorrison/agent-skills --global --skill align-codebase
npx skills add rburmorrison/agent-skills --global --skill implement-verified-steps

# Documentation
npx skills add rburmorrison/agent-skills --global --skill visual-explainers
```

## Personal Guidance

Add the contents of [personal-engineering.md](guidance/personal-engineering.md) to your global `AGENTS.md` or `CLAUDE.md`.
