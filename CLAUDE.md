# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WorkMate is an AI-powered assistant that uses RAG (Retrieval-Augmented Generation) to answer project-related questions from a Notion workspace with source-backed insights. The project is in early development.

## Tech Stack

- Python 3.13.9
- Package manager: `uv` (uses `pyproject.toml` and `uv.lock`)
- Key dependencies: pandas, numpy, matplotlib, jupyter, requests

## Commands

```bash
# Install/sync dependencies (uses uv.lock for exact versions)
uv sync

# Run the application
uv run python main.py

# Add a dependency (NEVER on main — use a feature branch)
uv add <package>
uv lock              # always lock after adding/removing deps

# Remove a dependency
uv remove <package>
uv lock

# Run tests
uv run pytest
uv run pytest tests/test_file.py::test_name  # single test
```

## Frontend Commands

```bash
# Install frontend dependencies
cd frontend && npm install

# Start frontend dev server (localhost:5173)
cd frontend && npm run dev

# Build for production
cd frontend && npm run build
```

## Project Structure

- `main.py` — Application entry point
- `src/` — Python scripts and modules
- `frontend/` — React + Vite frontend (TypeScript, Tailwind, shadcn/ui)
- `tests/` — Test scripts
- `docs/` — Project documentation
- `input/` — Raw input files (git-ignored)
- `output/` — Generated files (git-ignored)

## Git Workflow — IMPORTANT

- **Never push or work directly on `main`.** Always create a branch first.
- **Open PRs for review before merging** into main.
- **Pull before pushing.**
- **Do not commit `input/`, `output/`, or large files.**

### Branch naming conventions

| Type    | Pattern                              | Example                              |
|---------|--------------------------------------|--------------------------------------|
| Feature | `feature/<username>/<description>`   | `feature/eowusu/add-routing`         |
| Bugfix  | `bugfix/<username>/<description>`    | `bugfix/eowusu/fix-map-render`       |
| Testing | `testing/<username>/<description>`   | `testing/eowusu/test-case`           |

### Remote

- Origin: `https://github.com/RubyRyn/WorkMate.git`