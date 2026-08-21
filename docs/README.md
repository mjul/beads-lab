# Architecture documentation

High-level design lives here. Application code does not.

## Dual-agent loop

| Role | Subagent | Owns | Does not own |
| --- | --- | --- | --- |
| Architecture | `architecture` (`.cursor/agents/architecture.md`) | Concepts, interfaces, module boundaries, high-level examples in this `docs/` tree, `bd` backlog structure | Production code and tests |
| Implementation | `implementer` (`.cursor/agents/implementer.md`) | TDD against ready `bd` tasks, minimal code (YAGNI) | Conceptual redesign |

Flow:

1. **Architecture** clarifies denotations and composition, writes Markdown here (including high-level examples), files tasks/subtasks in `bd`.
2. **Implementer** claims ready work, reads the issue + these docs, writes a failing test, then the simplest code that passes.
3. When implementation hits unhandled cases or awkward seams, the implementer files `arch-feedback:` issues in `bd`.
4. **Architecture** reviews feedback, evolves docs and backlog (or closes feedback as YAGNI).

Parent orchestration for draining ready work: `.agents/skills/backlog-loop/` (implementation phase → architecture phase → repeat).

## Denotational checklist (for docs authors)

Every named module or interface in these docs should state:

- **Meaning** — what it denotes
- **Composition** — how meanings combine
- **Invariants** — what must remain true
- **Dependencies** — allowed edges only
- **Examples** — at least one high-level scenario or composition sketch (not production code) showing intended use

## Index

| Doc | Purpose |
| --- | --- |
| [prd.md](./prd.md) | Product requirements: Lisp-prefix rational calculator (+ unparse FR8, CLI polish FR9) |
| [architecture.md](./architecture.md) | Modules, protocols, denotations, CLI contract, backlog status |
| [pretty-print.md](./pretty-print.md) | Shipped: `unparse` Expr → canonical Lisp-prefix string |
| [cli-polish.md](./cli-polish.md) | Shipped: shared CLI driver + `--show-expr` display mode |
| [console-scripts.md](./console-scripts.md) | Shipped: `pyproject` console script entry points |
| [glossary.md](./glossary.md) | Shared vocabulary |
| [agents-workflow.md](./agents-workflow.md) | How to invoke and hand off between subagents |
