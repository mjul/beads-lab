---
name: beads
description: Use when working in a repository that uses bd or Beads for durable project task tracking, issue dependencies, blocker management, multi-session handoff, or shared work memory. Trigger when the user asks to find ready work, claim or close tasks, create follow-up work, inspect blockers, recover project context, or choose between local planning and persistent project tracking.
---

# Beads

Use Beads as the shared project task system. Local plans, scratch files, and personal memories are useful, but they are not the durable source of truth for project work.

## First Step

Run:

```bash
bd prime
```

If that prints nothing, check whether the repository has an active Beads workspace:

```bash
bd where
```

## Preferred Route

Use the `bd` CLI when shell access is available. It is the most compact and direct Beads interface.

## Core CLI Workflow

1. Find work:

```bash
bd ready
bd list --status=open
bd list --status=in_progress
```

2. Inspect before editing:

```bash
bd show <id>
```

3. Claim work atomically:

```bash
bd update <id> --claim
```

4. Create durable follow-up work when implementation reveals new tasks:

```bash
bd create "Short title" --description="Why this exists and what needs to be done" --type=task --priority=2
```

5. Close completed work:

```bash
bd close <id> --reason="Completed"
```

6. Push backlog changes to the remote (required for persistence):

```bash
bd dolt push
```

Run this after creating, updating, or closing issues when the backlog must survive session end, handoff, or another machine/clone. Issue data lives in the local Dolt database (`.beads/embeddeddolt/`), not in normal git commits on code branches; sync uses `refs/dolt/data` on the git remote.

In ephemeral environments (e.g. Cursor Cloud Agents), the local database is discarded when the VM ends. Without `bd dolt push`, backlog changes are lost. Do not assume `git commit` / `git push` persists issues unless JSONL export is explicitly enabled and committed.

Fresh clones do not get issues from `git clone` alone — run `bd bootstrap` or `bd dolt pull` to hydrate from `refs/dolt/data`.

## What Belongs In Beads

Use Beads for:

- shared project tasks
- blockers and dependencies
- discovered follow-up work
- work that must survive thread reset, compaction, or handoff
- status that another person or agent should be able to resume

Use agent-local planning tools only for the current turn's execution checklist. Do not treat them as shared project state.

## Rules

- Do not create markdown TODO files as the source of truth when Beads is available.
- Do not use `bd edit`; it opens an interactive editor. Use `bd update` flags instead.
- Prefer `--json` when parsing `bd` output programmatically.
- If hooks are installed, `bd prime` may already be injected. Run it manually when context is missing.
- Do not auto-close or mutate tasks unless the work is actually complete.
- After mutating the backlog (`bd create`, `bd update`, `bd close`, dependency changes), run `bd dolt push` before session end unless the user explicitly asked not to sync.
