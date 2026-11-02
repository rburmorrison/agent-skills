# Python tooling profile

Establish the supported Python version and project kind during planning. Use uv for a new project unless another package manager is required. Let initialization record the agreed `requires-python`; keep formatter, linter, and type-checker targets consistent with that range.

The bundled default uses Ruff for formatting/linting, mypy in strict mode for type checking, and pytest for behavior tests. If the project requires another checker or test framework, select the equivalent checks during planning and adapt the configuration. Do not add competing tools to an established project merely to match this example.

Initialize with uv using the planned Python version and project kind. Install development tools through the manager:

```sh
uv add --dev ruff mypy pytest
```

Merge [pyproject-tooling.toml](../assets/python/pyproject-tooling.toml) into the initialized manifest, preserving its existing tables and package-manager output. Ruff can infer its target from `requires-python` in a project manifest. Set mypy's `python_version` to the project's minimum supported version; do not assume the running interpreter represents that minimum.

The selected rules cover errors, imports, modern syntax, common bugs, unnecessary complexity, common security mistakes, and suppression hygiene. Docstring requirements are intentionally not selected: documentation should explain useful contracts and decisions, with concise usage examples. Formatters determine mechanical layout; preserve logical grouping within that layout.

The McCabe threshold is 15. This is a Python-profile default, not an assertion that Ruff's metric equals Clippy's cognitive-complexity score. Adjust it only for a concrete project reason, documented with the setting.

The test exception permits assertion statements in recognized test paths because they are the test framework's behavior checks. Keep test discovery paths and the exemption aligned. Additional exemptions must be narrow and explained. Use specific error codes for `noqa` or type ignores and put a reason alongside them; do not blanket-ignore a file or missing imports to obtain a pass.

Typical checks:

```sh
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest
```

Adapt the type-check and test paths to the actual package layout, keeping intended production and test code covered. Do not create meaningless tests just to satisfy an empty test run; report no tests collected honestly for a scaffold with no behavior yet.

Primary references: [uv dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/), [Ruff configuration](https://docs.astral.sh/ruff/configuration/), [Ruff suppression behavior](https://docs.astral.sh/ruff/linter/#error-suppression), [mypy configuration](https://mypy.readthedocs.io/en/stable/config_file.html).
