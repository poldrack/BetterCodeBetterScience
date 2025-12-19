# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an open-source book on building better code for science using AI, authored by Russell Poldrack. The rendered book is published at https://poldrack.github.io/BetterCodeBetterScience/.

## Build Commands

```bash
# Install dependencies (uses uv package manager)
uv pip install -r pyproject.toml
uv pip install -e .

# Build book as HTML and serve locally
myst build --html
npx serve _build/html

# Build PDF (requires LaTeX)
jupyter-book build book/ --builder pdflatex

# Clean build artifacts
rm -rf book/_build
```

## Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/BetterCodeBetterScience --cov-report term-missing

# Run specific test modules
pytest tests/textmining/
pytest tests/property_based_testing/
pytest tests/narps/

# Run tests with specific markers
pytest -m unit
pytest -m integration
```

Test markers defined in pyproject.toml: `unit` and `integration`.

## Linting and Code Quality

```bash
# Spell checking (configured in pyproject.toml)
codespell

# Python linting and formatting
ruff check .
ruff format .

# Pre-commit hooks (runs codespell)
pre-commit run --all-files
```

## Project Structure

- `book/` - MyST markdown chapters (configured in myst.yml)
- `src/BetterCodeBetterScience/` - Example Python code referenced in book chapters
- `tests/` - Test examples demonstrating testing concepts from the book
- `data/` - Data files for examples
- `scripts/` - Utility scripts
- `_build/` - Build output (gitignored)

## Key Configuration Files

- `myst.yml` - MyST book configuration (table of contents, exports, site settings)
- `pyproject.toml` - Python dependencies, pytest config, codespell settings
- `.pre-commit-config.yaml` - Pre-commit hooks (codespell)

## Contribution Guidelines

- New text should be authored by a human (AI may be used to check/improve text)
- Code examples should follow PEP8
- Avoid introducing new dependencies when possible
- Custom words for codespell are in `project-words.txt`
