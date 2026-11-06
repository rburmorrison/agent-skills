# List the available development commands.
default:
    @just --list

# Install the locked Python development tools.
setup:
    uv sync --locked

# Format Python source and tests.
format:
    uv run --locked ruff format .

# Check Python formatting without changing files.
format-check:
    uv run --locked ruff format --check .

# Run the configured Ruff rules.
lint:
    uv run --locked ruff check .

# Type-check Python source and tests with basedpyright.
typecheck:
    uv run --locked basedpyright

# Run Python behavior tests and JavaScript navigation tests.
test:
    uv run --locked python -m unittest discover -s skills/documentation/visual-explainers/tests -p 'test_*.py'
    node skills/documentation/visual-explainers/tests/test_navigation.js

# Run all verification without changing source files.
check: format-check lint typecheck test
