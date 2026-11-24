# Documentation

Doc comments and docstrings for code the change affects are part of the change. Usage documentation (READMEs, guides, standalone reference material, built-in help, and user examples) is edited to stay accurate, not to grow.

## Usage Documentation Scope

Correct claims the change made inaccurate, at their existing level of detail, and leave accurate content unchanged. A new document, section, example, or previously undocumented fact needs the user's request or agreement, even inside an existing passage; suggest it instead of adding it. A direct request to write documentation supplies its own scope.

## Document Interfaces and Decisions

Apply these standards to source doc comments, docstrings, and standalone interface documentation. Inspect the affected code, callers, existing documentation, and tooling before promising a contract.

Interfaces intended for other components, including within the project, are the boundary for caller-facing contracts. Include types and relevant members, not just functions. Visibility keywords, underscores, and module names are evidence of intent rather than the sole definition of that boundary. Truly internal implementation details usually need no documentation comment.

- Use a concise brief and complete applicable contract sections in the project's native documentation format. Omit inapplicable sections and boilerplate; do not restate type annotations without explaining meaning.
- Keep free-form bodies exceptional: use a short body only for a caller-facing concept or interaction that must be understood together and cannot be explained clearly in the brief, members, or contract sections. Importance or non-obviousness alone does not justify a body.
- Assign facts to their owning interfaces. Put input and result semantics in the brief or applicable contract sections, failures in the error section, and member facts on members. Remove duplication rather than moving it under Notes or Details or overloading the brief.
- Keep type documentation self-contained: describe intrinsic meaning, members, enforced invariants, and obligations for correct use. Avoid narrating external parsers, factories, or consumers. Put an operation's behavior and guarantees on that operation; public construction or mutation may bypass validation, so do not promise that every instance is validated when only one operation guarantees it.
- Check callers and propagated failures before describing errors. Preserve caller-relevant obligations; omit speculative failures and implementation walkthroughs. Use examples when requested and when they materially clarify correct use.
- Use Title Case for authored headings, keeping interior articles, short conjunctions, and short prepositions (such as "and", "or", "of", "to") lowercase, while preserving required documentation tags, identifiers, and syntax.

Read [Python documentation](documentation-python.md) or [Rust documentation](documentation-rust.md) when editing documentation in those languages. Use native formats and existing tooling for other languages.

Private doc comments are useful only for otherwise unclear contracts or constraints. Documentation-only work does not authorize restructuring code or changing behavior to fit a comment.

Follow project documentation lints, including for otherwise internal items. Do not weaken checks, change visibility, or rename items to evade them.

## Write Usage Documentation

Before editing a README, built-in help, or user guide, identify its audience, core purpose, and the task it helps the reader complete. Inspect the relevant entry points, supported installation method, examples, and actual help. Preserve prerequisites, consequential limitations, compatibility information, and applicable project conventions.

Keep a README focused on its purpose, necessary setup, and a representative path to a useful result. Revise the owning passage with concise, direct prose and Title Case for authored headings. Avoid redundant feature inventories, implementation narration, and change-history details. Do not impose a fixed section template.

Keep existing examples runnable from their stated starting conditions, with required inputs and enough observable output to recognize success. Capture help from the actual documented command and version, identify the command, and preserve the captured text verbatim. Do not reconstruct help, silently edit it, apply Title Case inside it, or present a shortened block as complete. Use an identified subcommand's help or a link when full help would overwhelm the document.

For agreed additions, put substantial workflows or concepts in separate documents only when readers need them, link from the relevant starting point, and avoid duplicating help or API reference material. Reuse existing documentation-generation mechanisms; do not introduce tooling merely to refresh a small output block.

## Check Accuracy Before Finishing

After a code change, look for existing documentation the change may have made wrong: interface contracts, comments in touched code, READMEs, built-in help, guides, and examples, including ones the diff does not touch. Correct what is inaccurate within the scope above, and tell the user about anything that would need an addition.

Run existing documentation lints, builds, and executable examples where applicable. Check links, prerequisites, examples, and captured help against actual behavior where feasible. Say what could not be run or verified.
