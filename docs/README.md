# Architecture documentation

High-level design lives here. Application code does not.

## Dual-agent loop

| Role | Subagent | Owns | Does not own |
| --- | --- | --- | --- |
| Architecture | `architecture` (`.cursor/agents/architecture.md`) | Concepts, interfaces, module boundaries, this `docs/` tree, `bd` backlog structure | Production code and tests |
| Implementation | `implementer` (`.cursor/agents/implementer.md`) | TDD against ready `bd` tasks, minimal code (YAGNI) | Conceptual redesign |

Flow:

1. **Architecture** clarifies denotations and composition, writes Markdown here, files tasks/subtasks in `bd`.
2. **Implementer** claims ready work, reads the issue + these docs, writes a failing test, then the simplest code that passes.
3. When implementation hits unhandled cases or awkward seams, the implementer files `arch-feedback:` issues in `bd`.
4. **Architecture** reviews feedback, evolves docs and backlog (or closes feedback as YAGNI).

## Denotational checklist (for docs authors)

Every named module or interface in these docs should state:

- **Meaning** — what it denotes
- **Composition** — how meanings combine
- **Invariants** — what must remain true
- **Dependencies** — allowed edges only

## Index

| Doc | Purpose |
| --- | --- |
| [agents-workflow.md](./agents-workflow.md) | How to invoke and hand off between subagents |
| *(add module docs here)* | Interface contracts and glossaries as the design grows |
