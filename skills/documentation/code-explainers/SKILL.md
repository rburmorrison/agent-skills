---
name: code-explainers
description: Explain a past change, a subsystem, or a concept in a codebase to its owner as a visual explainer grounded in the real source and git history. Use when the user wants to understand existing code, its architecture, or the decisions behind it.
---

# Code Explainers

Produce one explainer that lets the reader understand a part of their own codebase at a technical level. Assume a competent programmer who delegated much of this code to an agent and is not familiar with it: they know the language, not this code's names, structure, or history. This skill owns the investigation and the teaching; `visual-explainers` owns rendering. Treat the explained repository as read-only.

Answer in chat when a few sentences and one excerpt settle the question. Build an explainer when the answer needs several pieces of code, a process, or a comparison, or when the user asks for one.

## Establish the Subject

Identify which kind of explanation is wanted, because each has a different shape:

- **A change:** what one commit, range, or pull request did, why, and what it means for callers.
- **A subsystem:** what a part of the code is responsible for, its pieces, and how one run of it proceeds.
- **A concept:** an idea the code implements, taught from first principles and then located in the code.

State the subject and its boundary in one sentence before investigating. Ask one question only when the subject or the kind is ambiguous enough to change what you would read. Include code outside the named area when the subject's correctness depends on it; cite such code without explaining it.

## Investigate Before Writing

Read the code itself, with its callers, tests, and history. Do not explain from memory of having written or seen the code.

- **Pin a commit.** Record the commit the explanation describes with `git rev-parse --short HEAD`, or the commit under study for a change. Every line number refers to that commit. When the working tree has moved on from a change being explained, describe the code as of that commit and name later commits explicitly.
- **Find intent where it is written.** Look in this order: commit messages and bodies, comments and doc comments, test names and test comments, then project documentation. Tests are often the only statement of why an edge case is handled.
- **Use the codebase's words.** Adopt its names for things and define each on first use. Where the code distinguishes two terms a reader would conflate, say so.
- **Trace one real path.** Follow a concrete input through the code rather than describing components in the abstract. For a subsystem, pick the steady-state path that crosses the most components and leave other branches to annotations or a table.

## Keep Every Claim Checkable

A polished page looks authoritative whether or not it is right, so the evidence rules matter more than the presentation.

- **Extract, never retype.** Generate the document JSON with a script that reads every excerpt and both sides of every diff from `git show <commit>:<path>`, and computes start lines from the file. Keep the script beside the JSON so the document can be regenerated.
- **Recompute numbers.** Derive figures from the source and compare them with values the repository's tests assert. Trust the code over general knowledge and over commit titles, and say so when they disagree.
- **Separate stated from inferred.** A claim is stated when a commit, comment, test, or document says it. Anything else about motive is inference: mark it with the bold word **Inference** in prose, or a "Basis" column holding Stated or Inference in a table. Often the mechanism is stated and the motive is not; split them.
- **Say what was not run.** If you did not build or run tests, cite tests as evidence of intent, not as passing checks.
- **Report what you find.** Stale comments, mismatched names, or contract violations discovered along the way belong in a short closing section and in the handoff. Do not fix them.

Show sources without burying the prose in parentheses: set `title` to the file path on every code block and diff, with a code block's `start` and a diff's `before_start` and `after_start`, so excerpts carry their own file and line numbers; give tables a "Defined In" column; and name a section's main file once. Reserve inline `file:line` citations for claims no shown excerpt supports. State the pinned commit in a note near the top.

## Shape the Explanation

Lead with the main point in one or two sentences, then give the smallest big picture that makes the rest readable, then the detail.

- **A change:** what changed in one paragraph and a short table; where the changed code sits; the before and after as the reader would observe it, taken from tests, fixtures, or documentation when the repository has them; why; the code changes; consequences and what a caller must now do differently.
- **A subsystem:** its responsibilities and main guarantee; the pieces and how they connect, with a diagram; one run walked through step by step; the state it keeps and why; edge cases and the decisions behind them. Include a diff only where a design rule came from a specific fix, and name that diff's commit, since it predates the pinned one.
- **A concept:** the idea in plain terms; a small worked example built from nothing; the general rule or math, kept to what the code actually uses; the variants that exist, in a table; where the code defines and applies it; how it has been extended.

Define terms inline when first needed and collect project terms in one table early. Do not include material only because it was touched or because a component exists to display it.

## Choose What to Show

- **Annotated code** for code being explained as it stands. Show whole functions on the path being walked, not fragments; split a function longer than about forty lines at a natural boundary. Put each note after the lines it explains, with `lines` set.
- **Diffs** for how code came to be this way. Use the enclosing function or type on both sides and let `context` collapse what did not change. When one commit touches distant parts of a file, use one diff per part. Explain a diff with its `annotations` rather than a paragraph above it. Use `unified` when source lines run long and the same `view` throughout.
- **Which files:** for a change, prefer the type definitions, the producer, one consumer, and one test or migration example; summarize the rest in a list with paths. When the same code belongs in both a walkthrough and a diff, annotate it in the walkthrough and point forward to the diff.
- **Diagrams** for real relationships: a graph for components, a sequence for one run. Graphs cannot contain cycles, so describe a feedback path in prose or as a sequence message.
- **Output and data** copied from the repository. If real output must be shortened to be readable, label it as abridged and put the complete version in a disclosure.

Keep the document to what a reader can finish in one sitting: roughly ten to fifteen minutes. This limit outranks showing whole functions: show in full only the functions that carry the main path's decisions, and cite the rest by file and line. Move secondary cases into a table or a disclosure.

## Build and Hand Off

Follow `visual-explainers` to compose, render, and inspect the document, including its theme question; read its component reference in parts if it is long. If that skill is unavailable, tell the user and deliver the same content as a Markdown document instead. Keep identifiers, lowercase project names, and commit hashes out of headings, where Title Case would alter them.

Save the JSON, the generator script, and the HTML together where the user asks. Without a stated location, do not add them to the explained repository's tracked files; use an untracked folder and say where it is.

In the handoff, give the output path and the pinned commit, list what you inferred and what you could not verify, and repeat any findings about the code itself.
