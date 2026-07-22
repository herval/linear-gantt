# Linear Gantt Chart Visualizer - task runner
# Requires: uv (https://docs.astral.sh/uv/) and just (https://github.com/casey/just)

# List available recipes
default:
    @just --list

# Install/sync all dependencies (including dev) into the managed venv
sync:
    uv sync

# Run the Streamlit app
run: sync
    uv run streamlit run app.py

# Run the full test suite
test:
    uv run pytest

# Run tests with coverage report
cov:
    uv run pytest --cov=src --cov-report=term-missing

# Open a Python REPL inside the project environment
shell:
    uv run python

# Remove the virtual environment and caches
clean:
    rm -rf .venv .pytest_cache htmlcov .coverage
    find . -type d -name __pycache__ -exec rm -rf {} +
