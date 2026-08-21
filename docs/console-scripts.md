# Capability: Console script entry points

Thin packaging layer over the shipped evaluator CLIs. Does **not** change ⟦·⟧, parsing, evaluation, or CLI argv semantics.

## Motivation

Today the calculator is invoked only via `python -m beads_lab.stack_machine` / `python -m beads_lab.free_monad`. That is correct but easy to miss in README and demos. `pyproject.toml` still exposes a placeholder `beads-lab` script that prints `"Hello from beads-lab!"` — not wired to the calculator.

Console scripts give discoverable shell commands after `uv sync` / install, reusing the same `main()` entry points (and therefore the shared `cli.py` driver once `--show-expr` lands).

## Module map (unchanged)

No new Python modules. Only `[project.scripts]` entries in `pyproject.toml` pointing at existing `main()` functions:

```text
beads_lab.stack_machine.main  →  beads-stack  (proposed name)
beads_lab.free_monad.main       →  beads-free   (proposed name)
```

Remove or replace the placeholder `beads-lab = "beads_lab:main"` stub in the same change set.

## Denotations

### Console script

\[
\mathrm{script\_main} : \mathsf{Argv} \to \mathsf{ExitCode}
\]

**Meaning**: identical to the corresponding module’s `main()` — evaluate mode by default; `--show-expr` when present on `cli.main` (FR9). No second argv parser, no new flags beyond what `cli.py` already accepts.

**Composition**: packaging only; denotation factors through existing `cli.main(parser, evaluator, usage)`.

### Observables

An implementer verifies without reading `pyproject.toml` internals:

- After `uv sync`, `uv run beads-stack '(+ 1 2)'` prints `3` with exit 0 (same as `-m beads_lab.stack_machine`).
- `uv run beads-free '(pow 2 3)'` prints `8`.
- Usage / parse / domain failures match module CLI tests (stderr non-empty, stdout empty on failure).
- When `--show-expr` is shipped on `cli.py`, both scripts honor it identically to `-m` entry points.
- Placeholder `beads-lab` hello-world script is gone.

## What this does *not* denote

- New calculator semantics or argv shapes
- A third evaluator or merged “super CLI”
- Shell completion, man pages, or global install docs beyond README examples
- Changing default module `__main__` behavior

## High-level examples

### Example A — evaluate (default)

| Command | Stdout | Exit |
| --- | --- | --- |
| `uv run beads-stack '(+ 1 (* 2 3))'` | `7` | 0 |
| `uv run beads-free '(pow 2 3)'` | `8` | 0 |

### Example B — show-expr (when FR9 code is on branch)

| Command | Stdout |
| --- | --- |
| `uv run beads-stack --show-expr '(  +  1  2 )'` | `(+ 1 2)` |

(Same string as `python -m beads_lab.stack_machine --show-expr …`.)

### Example C — README discoverability

README gains a **Calculator CLI** section listing both `-m` and `uv run beads-*` forms so agents and humans do not rely on spelunking `src/`.

## Invariants (implementer checklist)

- Script targets call existing `main()` without wrapper logic duplication.
- No new imports between `stack_machine` and `free_monad`.
- Removing `beads_lab:main` stub is acceptable; drop `reverse_string`-only demo from user-facing paths if nothing else needs it (property tests may keep importing the helper from the package).

## Relation to shipped work

| Piece | Status |
| --- | --- |
| Shared `cli.py` + mains migration | Shipped on master (#33) |
| `--show-expr` + E2E tests | Land via stacked PRs or master merge before script tests assert show-expr |
| Console scripts | **This capability** |

## References

- CLI contract: [cli-polish.md](./cli-polish.md)
- Module map: [architecture.md](./architecture.md)
- Product surface: [prd.md](./prd.md)
