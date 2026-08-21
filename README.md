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

Cursor Cloud Agent environments use `.cursor/environment.json`, which runs
`./scripts/cloud-agent-install.sh` to install `bd` (via `$HOME/.local/bin` on
PATH) and sync project dependencies—no manual install step required.

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

### Architecture and implementer subagents

Two custom subagents encode the design ↔ build loop (see `docs/agents-workflow.md`):

| Subagent | Path | Responsibility |
| --- | --- | --- |
| `architecture` | `.cursor/agents/architecture.md` | Modules/interfaces/abstractions with denotational consistency; writes `docs/`; fills the `bd` backlog. Does not write app code. |
| `implementer` | `.cursor/agents/implementer.md` | Claims ready `bd` tasks, TDD + YAGNI, simplest code that works; posts `arch-feedback:` issues when the design is incomplete or awkward. |

Delegate via Cursor’s Task/subagent tooling (or `/architecture` / `/implementer` where available).