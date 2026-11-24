---
name: code-authoring
description: My preferences for writing and changing source code, tests, doc comments, READMEs, help, and user guides, and for how to involve me while doing it. Use whenever editing code or its documentation. Not for configuration, manifest, lockfile, or data files.
---

# Code Authoring

These are preferences, not a procedure. Apply them with judgment and in proportion to the change. An explicit instruction from me, or a codebase's established style, wins over anything here.

## Work With Me

I want to be part of the work while it happens, not handed a finished result.

- **Share the approach first.** Before any change larger than a small fix, tell me in a few plain sentences what you intend to change and where, and name the choices I might make differently. If there are real choices, wait for my reply. If there are none, say so and carry on.
- **Ask when the question comes up.** Ask in ordinary prose with enough context that I can answer without opening the code. Do not save questions for the end, and do not settle behavior, error policy, compatibility, or structure on my behalf because a default seemed reasonable.
- **Stop at surprises.** If the code does not work the way either of us assumed, the request conflicts with what is there, or the approach is not working, tell me before working around it.
- **Show something small early.** Get the core of the change working and show it to me before extending or polishing it.
- **Stay within the request.** Mention cleanup, refactors, and upgrades you would recommend instead of doing them.
- **Close briefly.** Say what changed and how it works now, what you ran and what you saw, what you could not verify, and anything left for me to decide. Scale it to the change; a small fix needs a few sentences.

## Design

- **Follow the project first.** In an existing codebase, write new code the way the surrounding code is written: its structure, its error handling, where it performs I/O, and how it manages state. The two preferences below apply to new projects and to code with no settled convention. Where they differ from the project's conventions, the project wins; do not restructure existing code toward them, and tell me if you think a move would be worth it.
- **Functional core, effects at the edges.** Keep calculations and decisions in pure functions over ordinary values. Keep filesystem, network, database, clock, randomness, and environment access in thin coordinating code that passes values in. When a decision determines writes, return it as a value and apply it separately.
- **Say what the result is.** Prefer immutable values, mapping and filtering expressions, and a dependency's declarative APIs over accumulator loops and hand-written procedures, where that reads more clearly. Local mutation inside one function and ordered I/O stay direct.
- **Keep related rules together.** When several cases share a shape, such as tiers, formats, or policies, declare them in one place and interpret them with one small mechanism instead of scattering them through branches. A one-off conditional stays a conditional.
- **Use what is already there.** Check what an existing dependency or project mechanism provides before writing custom parsing, formatting, layout, or scheduling. Add dependencies through the package manager with real version information.
- **No speculative structure.** Add an abstraction or module only for a concrete responsibility that exists now.

Read [the code examples](references/code-examples.md) when a design or style choice is unclear.

## Readability

The code should explain itself; comments cover only what it cannot.

- **Use clear, descriptive names.** Name functions, variables, and types for what they mean in the problem, in full words. A reader should know what a value holds and what a function does without opening its definition.
- **Keep functions to a few stages.** When a function grows past a few stages, extract the ones that have a name worth giving, so the function reads as a short sequence of named operations. Do not split a single cohesive stage just to make it shorter.
- **Use concrete types.** Give parameters, results, and fields the most specific type that fits. Use named records and explicit variants instead of positional tuples, untyped maps, bare strings standing in for a fixed set of values, or catch-all types such as `Any`. Reach for a generic or abstract type only when the code really handles more than one.
- **Space the stages.** Separate changes of purpose with a blank line. Also separate setup from the loop that uses it, and guards or a finished loop from the result that follows. This applies to every function and test, with or without comments.
- **Comment only what the code cannot say.** Add an inline comment where a stage is not obvious from its code: why it exists, why it must come before or after another, a constraint or assumption it relies on, or behavior a reader would find surprising. A stage whose code already says what it does gets spacing and no comment.
- **Keep comments short and plain.** Write one ordinary sentence in single-line comment syntax, directly above the code it explains. Do not write labels such as `Validation` or `Step 1:`, and do not narrate statements.
- **Keep existing comments true.** Update or remove a comment the change made inaccurate, including comments on lines you did not otherwise touch.

## Tests and Verification

- Test behavior at the boundary where it can be observed, with a small set of distinct scenarios. Read [the testing guidance](references/testing.md) when adding or changing tests.
- Run the project's formatting, lint, type, and test checks.
- Exercise the change the way a user would, through the real command, UI, API, or caller, when that is feasible.
- Never report a check as passing unless it ran. Say plainly what was not run or could not be verified.
- Fix the cause of a lint or type error. A suppression is rare, narrow, and carries its reason.

## Documentation

- Write doc comments for interfaces the change adds or alters.
- In READMEs, guides, help, and examples, correct what the change made inaccurate and leave accurate text alone. Suggest new sections, examples, or facts to me instead of adding them.
- Read [the documentation reference](references/documentation.md) before editing documentation or doc comments.
