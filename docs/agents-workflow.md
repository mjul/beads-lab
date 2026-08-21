# Architecture ↔ implementer workflow

Custom Cursor subagents (also linked for Claude/Codex):

- `.cursor/agents/architecture.md`
- `.cursor/agents/implementer.md`

## When to delegate

| Ask the parent to run… | When… |
| --- | --- |
| **architecture** | Designing or revising modules/interfaces; writing `docs/` (with high-level examples); shaping the `bd` backlog; reviewing `arch-feedback:` issues |
| **implementer** | A concrete `bd` task is ready; you want TDD + YAGNI code; you need implementation feedback filed back to architecture |

Invoke via Cursor’s Task/subagent delegation (or `/architecture`, `/implementer` where supported). Give the subagent the issue ID, relevant doc paths, and any constraints — subagents start with a clean context.

## Parent agent checklist

1. Prefer **architecture** before large implementation spreadsheets of tasks.
2. Prefer **implementer** for a single claimed (or clearly identified) ready issue.
3. After implementer returns `arch-feedback:` IDs, schedule **architecture** to review them before piling on more features.
4. Keep `bd` as the source of truth for work; do not create markdown TODO lists.
5. When a task (or meaningful chunk) finishes, require a short **hand-off memory** via `bd remember` (what landed, TIL / tips & tricks, improvement ideas for docs/skills/agents). Search prior learnings with `bd memories <keyword>`.
6. To **drain the backlog** (all ready implementation, then architecture, then switch back until idle), use the **backlog-loop** skill: `.agents/skills/backlog-loop/SKILL.md`.

## Backlog loop (phased drain)

When the user asks to work the next backlog item(s) or clear ready work, follow `.agents/skills/backlog-loop/SKILL.md`:

1. Start in **implementation** phase — delegate every ready implementation-classified issue to `/implementer` until that lane is empty.
2. Switch to **architecture** — delegate ready architecture work (`arch-feedback:`, epics/features, docs/design) to `/architecture` until that lane is empty.
3. Switch back to implementation and repeat until a full cycle finds nothing in either lane.

The parent orchestrates only; it does not write app code or architecture docs while the loop is active.

## Beads patterns

```bash
bd ready                          # implementer picks from here
bd update <id> --claim
bd create "arch-feedback: …" --description="…" --type=task
bd dep add <issue> <depends-on>
bd close <id> --reason="…"
```

Architecture decomposes work into epics/features/tasks with dependencies.
Implementer closes tasks and opens `arch-feedback:` issues when the design is incomplete or cumbersome.
