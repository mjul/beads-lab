---
name: backlog-loop
description: Drain the Beads backlog in phases — exhaust ready implementation work via the implementer subagent, then architecture work via the architecture subagent, then switch back. Loop until a full cycle finds nothing left. Use when the user asks to work the next backlog item, clear or drain the backlog, or run the architecture↔implementer loop.
---

# Backlog Loop

Parent-agent skill. You **orchestrate**; you do **not** implement code or rewrite architecture docs yourself. Delegate every unit of work to the matching subagent.

Companion skills/agents:

- Beads: `.agents/skills/beads/SKILL.md`
- Implementer: `.cursor/agents/implementer.md` (`/implementer`, Task `subagent_type: implementer`)
- Architecture: `.cursor/agents/architecture.md` (`/architecture`, Task `subagent_type: architecture`)

## When to apply

- User asks to work the next backlog item, drain the backlog, or run the dual-agent loop
- Ready `bd` work exists and should be routed rather than done inline

Skip when the user names a single concrete edit with no backlog involvement, or explicitly asks you to do the work yourself without subagents.

## First step

```bash
bd prime
bd ready --json
bd list --status=open --json   # optional: see blocked / not-yet-ready context
```

If `bd ready` is empty and there is no architecture work (see classify), stop and report that the backlog is clear for this loop.

## Classify each issue

Inspect `bd show <id>` (title, type, description, labels). Assign **exactly one** lane:

| Lane | Prefer when… |
| --- | --- |
| **implementation** | Ready `task` / `bug` / concrete `chore` with an acceptance intent that needs code or test changes under `src/` / `tests/` (or similarly shippable tooling). Not an epic/feature umbrella. |
| **architecture** | Title starts with `arch-feedback:` or `arch-review:`; type is `epic` or `feature` needing design/decomposition; work is docs-first under `docs/`; backlog shaping; conceptual redesign; or the issue says design is incomplete. |

If ambiguous, prefer **architecture** when the issue is about meaning, interfaces, or backlog structure; otherwise **implementation**.

Do not claim issues in the parent. The subagent claims (`bd update <id> --claim`).

## Phase machine

Start in phase **implementation**.

```text
phase = implementation
idle_rounds = 0          # consecutive phases that found no eligible work

while idle_rounds < 2:   # stop after one empty implementation + one empty architecture pass
    eligible = ready issues whose lane matches phase
    if eligible is empty:
        idle_rounds += 1
        phase = architecture if phase == implementation else implementation
        continue

    idle_rounds = 0
    # Drain this phase completely before switching
    while eligible is non-empty:
        pick highest-priority eligible issue (stable: bd ready order)
        delegate to the subagent for that lane (below)
        refresh: bd ready --json
        eligible = ready issues whose lane matches phase

    phase = architecture if phase == implementation else implementation
```

Rules:

1. **Drain before switch** — finish all currently ready work in the active phase before changing phase.
2. **Always re-query** `bd ready` after each delegation (new tasks or `arch-feedback:` may appear).
3. **Route by lane, not by phase name alone** — in an implementation phase, skip architecture-classified ready issues (leave them for the architecture phase). Symmetric for architecture phase.
4. **Stop** when both phases in a row find no eligible ready work, or the user cancels.
5. **Do not** infinite-loop on the same failing issue: if a subagent returns blocked/failed twice on the same ID, leave it open, note the blocker, and continue with other eligible work (or switch phase if none remain).

## Delegation

For each picked issue, launch the matching subagent with a **fresh, complete** prompt (subagents have no parent context):

### Implementation → `/implementer`

- Task tool: `subagent_type: implementer`
- Prompt must include: issue ID, title, that they should `bd prime`, `bd show <id>`, claim, follow test-first + YAGNI, close or file `arch-feedback:` as needed, and return the hand-back fields from the implementer agent file.

### Architecture → `/architecture`

- Task tool: `subagent_type: architecture`
- Prompt must include: issue ID(s), whether this is feedback review vs epic/feature decomposition vs docs work, relevant `docs/` paths, that they must not write application code, and return the hand-back fields from the architecture agent file.

Prefer **one issue per implementer** invocation. Architecture may batch closely related `arch-feedback:` IDs in one invocation when they share the same design surface.

Wait for the subagent to finish before picking the next issue in the phase (unless the user explicitly asked for parallel workers — default is sequential).

## After each delegation

1. Skim the hand-back: closed IDs, new IDs (especially `arch-feedback:`), blockers.
2. Do not re-implement or re-architect in the parent unless the subagent failed to start.
3. Continue the phase machine.

## Session close (when the loop stops)

1. Summarize: phases run, issues closed/created, remaining ready/blocked.
2. If a meaningful chunk finished, leave Beads memory: `bd remember "…"`.
3. Follow the repo’s Beads profile / orchestrator rules for commit, `bd dolt push`, and git push — do not sync unless authorized.

## Anti-patterns

- Parent writing `src/` or `tests/` while this skill is active
- Parent rewriting `docs/` architecture while this skill is active (except tiny clarifications the subagent already requested you to apply)
- Alternating one-impl / one-arch each time instead of **draining** the current phase
- Using markdown TODOs instead of `bd`
- Claiming in the parent and then also asking the subagent to claim (double-claim races)
