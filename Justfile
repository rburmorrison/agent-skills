# List the available development commands.
default:
    @just --list

# Install the locked Python and JavaScript development tools.
setup:
    uv sync --locked
    npm ci --ignore-scripts --no-audit --no-fund

# Regenerate committed minified browser assets from readable JavaScript.
build-js:
    node scripts/build-javascript.mjs

# Check generated JavaScript without changing files.
check-js:
    node scripts/build-javascript.mjs --check

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

# Run Python behavior tests and JavaScript build and navigation tests.
test:
    uv run --locked python -m unittest discover -s skills/documentation/visual-explainers/tests -p 'test_*.py'
    node tests/test-javascript-build.mjs
    node skills/documentation/visual-explainers/tests/test_navigation.js

# Run all verification without changing source files.
check: format-check lint typecheck check-js test
