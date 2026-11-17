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

# Regenerate committed WOFF2 fonts from the bundled TrueType sources.
build-fonts:
    uv run --locked python scripts/build_fonts.py

# Check generated WOFF2 fonts without changing files.
check-fonts:
    uv run --locked python scripts/build_fonts.py --check

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

# Run Python behavior tests and JavaScript build, navigation, diagram, chart, and hexfield tests.
test:
    uv run --locked python -m unittest discover -s skills/documentation/visual-explainers/tests -p 'test_*.py'
    node tests/test-javascript-build.mjs
    node skills/documentation/visual-explainers/tests/test_navigation.js
    node skills/documentation/visual-explainers/tests/test_diagram_view.js
    node skills/documentation/visual-explainers/tests/test_charts.js
    node skills/documentation/visual-explainers/tests/test_hexfield.js

# Run all verification without changing source files.
check: format-check lint typecheck check-js check-fonts test
