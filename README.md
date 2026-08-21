# beads-lab

Trying out [beads (`bd`)](https://github.com/gastownhall/beads) — a distributed graph issue tracker for AI coding agents.

## Prerequisites

Install the `bd` CLI (system-wide; do not clone the beads repo into this project):

```bash
curl -fsSL https://raw.githubusercontent.com/gastownhall/beads/main/scripts/install.sh | bash
# Ensure ~/.local/bin is on your PATH, then:
bd version
```

## Project setup

This repository is already initialized. After cloning:

```bash
bd dolt pull          # sync issue data if a Dolt remote is configured
bd setup cursor       # Cursor rules → .cursor/rules/beads.mdc
bd prime              # load agent workflow context
bd ready              # find available work
uv sync --group dev   # Python deps (incl. ruff)
```

Fresh init (already done here):

```bash
bd init --quiet
bd setup cursor
```

## Lint and format (ruff)

```bash
uv run ruff check .           # lint
uv run ruff check --fix .    # lint + apply safe fixes
uv run ruff format .          # format
uv run ruff format --check .  # CI-style format check
```

Config lives in `[tool.ruff]` in `pyproject.toml`.

## Agent workflow

See `AGENTS.md` and `.cursor/rules/beads.mdc`. Short version:

```bash
bd ready
bd update <id> --claim
# …do the work…
bd close <id>
bd dolt push
```
