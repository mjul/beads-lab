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

## Type check (ty)

```bash
uv run ty check src tests
```

`ty` is a dev dependency (Astral’s type checker), installed with `uv sync --group dev`.

## Calculator CLI

This repo includes a **Lisp-prefix rational calculator** over ℚ with two interchangeable evaluators (stack machine and free-monad interpreter). Both share one parser and agree on results.

After `uv sync --group dev`, evaluate an expression with either entry style:

```bash
# Module entry points
uv run python -m beads_lab.stack_machine '(+ 1 (* 2 3))'
uv run python -m beads_lab.free_monad '(pow 2 3)'

# Console scripts (same behavior)
uv run beads-stack '(+ 1 (* 2 3))'
uv run beads-free '(pow 2 3)'
```

Success prints the rational result on stdout; parse or domain failures go to stderr with a non-zero exit code.

Full CLI contract (output modes, argv rules): [docs/cli-polish.md](docs/cli-polish.md). Module map and denotations: [docs/architecture.md](docs/architecture.md).

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

To drain the backlog in phases (implementation first, then architecture, then switch back), use the **backlog-loop** skill: `.agents/skills/backlog-loop/`.