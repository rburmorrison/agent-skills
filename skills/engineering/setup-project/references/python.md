# Python Tooling Profile

Establish the supported Python version and project kind during planning. Use uv for a new project unless another package manager is required. Let initialization record the agreed `requires-python`; keep formatter, linter, and type-checker targets consistent with that range.

The bundled default uses Ruff for formatting/linting, basedpyright in strict mode for type checking, and pytest for behavior tests. If the project requires another checker or test framework, select the equivalent checks during planning and adapt the configuration. Do not add competing tools to an established project merely to match this example.

Initialize with uv using the planned Python version and project kind. Install development tools through the manager:

```sh
uv add --dev ruff basedpyright pytest
```

Merge [pyproject-tooling.toml](../assets/python/pyproject-tooling.toml) into the initialized manifest, preserving its existing tables and package-manager output. Ruff can infer its target from `requires-python` in a project manifest. Set basedpyright's `pythonVersion` to the project's minimum supported version; do not assume the running interpreter represents that minimum.

The asset's `select` list is the baseline for every new project: errors and style, imports, naming, modern syntax, common bugs, simplification, Pylint checks, complexity, unused arguments, commented-out code, stray prints, exception handling, pathlib, timezone-aware datetimes, performance, security, pytest style, and suppression hygiene. Remove a baseline family only for a concrete project reason, written beside the setting; a command-line tool that prints its output may drop `T20`, for example. `E501` is ignored because the formatter owns line length.

During planning, add the families that fit the project. Ruff has many more than any one project needs, so choose them by what the project does:

- `ASYNC` for asyncio, Trio, or AnyIO code.
- `LOG` and `G` when the project uses the standard `logging` module.
- `FBT` for libraries, where boolean positional arguments obscure call sites.
- `DJ`, `FAST`, `NPY`, `PD`, or `AIR` for Django, FastAPI, NumPy, pandas, or Airflow.
- `ANN` only when basedpyright is not the type checker; strict mode already requires annotations.

Docstring rules (`D`, `DOC`) are not selected. `code-authoring` owns docstring content, and Ruff's `DOC` rules are preview-only and reject documented exceptions that a callee raises.

The McCabe threshold is 15, and Pylint's own size and branch thresholds stay at their defaults. Adjust any of them only for a concrete project reason, documented with the setting.

The test exceptions permit assertion statements and literal expected values in recognized test paths. Keep test discovery paths and the exemptions aligned. Additional exemptions must be narrow and explained.

Every suppression names its rule and carries a reason: `# noqa: RULE` or `# pyright: ignore[rule]`, followed by the reason in the same comment. The tooling rejects a suppression with no rule code (`PGH003`, `PGH004`, `reportIgnoreCommentWithoutRule`) and one that no longer suppresses anything (`RUF100`, `reportUnnecessaryTypeIgnoreComment`). Neither tool can check that a reason is present, so check that yourself. Do not blanket-ignore a file or missing imports to obtain a pass.

Typical checks:

```sh
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
uv run pytest
```

Adapt the type-check and test paths to the actual package layout, keeping intended production and test code covered. Do not create meaningless tests just to satisfy an empty test run; report no tests collected honestly for a scaffold with no behavior yet.

Primary references: [uv dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/), [Ruff configuration](https://docs.astral.sh/ruff/configuration/), [Ruff suppression behavior](https://docs.astral.sh/ruff/linter/#error-suppression), [basedpyright configuration](https://docs.basedpyright.com/latest/configuration/config-files/).
