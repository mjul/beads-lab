# Capability: CLI polish (shared driver + `--show-expr`)

Thin presentation layer over shipped parse / eval / unparse. Does **not** change ⟦·⟧, the `Expr` ADT, either evaluator, or canonical `unparse`.

## Motivation

`stack_machine.main` and `free_monad.main` are identical except for which `Evaluator` they construct and the usage string. Adding flags (or any argv shape change) twice invites drift. A shared CLI driver also gives a single place to compose `unparse(parse(s))` as an optional **display** mode without touching evaluation semantics.

## Module map (addition)

```text
beads_lab/
  …                 # calculator + printer (shipped; do not redesign)
  cli.py            # shared one-shot CLI driver (argv → exit code)
```

Dependency direction (new edges only):

```text
parser, printer, protocols, values  ←  cli
cli  ←  stack_machine, free_monad     # each main delegates; injects its Evaluator
```

- `cli` must **not** import `stack_machine` or `free_monad` (evaluator is injected).
- `stack_machine` and `free_monad` still must **not** depend on each other.
- `cli` may import `parser` / `printer` for the `--show-expr` path; evaluators still need not import `printer` except via this thin CLI layer.

## Denotations

### Shared CLI driver

\[
\mathrm{cli\_main} : \mathsf{Argv} \times \mathsf{Evaluator} \times \mathsf{Usage} \to \mathsf{ExitCode}
\]

with side effects: write to stdout / stderr.

**Meaning**: interpret argv as a one-shot calculator invocation; choose an **output mode**; on success print one line to stdout; on failure print a message to stderr and return a non-zero exit code. Identity of the injected `Evaluator` does not change ⟦·⟧ (FR7 still holds for the evaluate path).

**Composition**: `cli_main` is a pure orchestration of existing maps (`parse`, `evaluate` / `unparse`). It introduces no new arithmetic meaning.

### Output modes

| Mode | When | Stdout (success) | Uses evaluator? |
| --- | --- | --- | --- |
| **Evaluate** (default) | no `--show-expr` | `str(Fraction)` from `run(parser, evaluator, source)` | yes |
| **Show-expr** | `--show-expr` present | `unparse(parse(source))` | no |

Show-expr denotes **canonical concrete syntax** of the parsed tree (same string FR8 already defines)—not evaluation, not `repr(Expr)`, not a second pretty-printer.

### Argv shape

Normative behavior (concrete flag spelling may be `--show-expr`; keep it a single long option, no short alias required):

1. Program name is `argv[0]` (ignored for semantics; used only in usage text if desired).
2. Exactly one expression string among the non-flag arguments.
3. Optional flag `--show-expr` may appear before or after the expression string.
4. Missing expression, excess non-flag args, or unknown flags → usage error (exit ≠ 0, message on stderr, empty stdout).

**Backward compatibility**: `python -m beads_lab.stack_machine '(+ 1 2)'` (no flags) remains evaluate mode with the same success/failure exit contract as today.

## What this does *not* denote

- Changes to ⟦·⟧, parse errors vs domain errors taxonomy, or FR7
- A REPL, multi-expression argv, file input, or interactive prompt
- Printing both Fraction and unparsed form in one invocation (YAGNI; pick one mode)
- Alternate rational display (exact vs mixed number)—out of scope
- A `Printer` protocol or moving `unparse` into `cli`

## Public surface (conceptual)

```text
# cli.py
def main(
    argv: list[str] | None,
    *,
    evaluator: Evaluator,
    usage: str,
) -> int: ...

# stack_machine / free_monad keep thin wrappers:
def main(argv=None) -> int:
    return cli.main(argv, evaluator=Evaluator(), usage=_USAGE)
```

Existing `protocols.run` stays the evaluate composition; CLI driver may call it for default mode.

## High-level examples

### Example A — default evaluate (unchanged meaning)

| Invocation (conceptual) | Stdout | Exit |
| --- | --- | --- |
| `stack_machine '(+ 1 (* 2 3))'` | `7` | 0 |
| `free_monad '(/ 1 0)'` | (empty; domain message on stderr) | ≠ 0 |

Both entry points still agree on success value / domain-error class when they evaluate the same string (FR7).

### Example B — `--show-expr` (syntax only)

| Invocation (conceptual) | Stdout | Notes |
| --- | --- | --- |
| `stack_machine --show-expr '(+ 1 (* 2 3))'` | `(+ 1 (* 2 3))` | no evaluation |
| `free_monad --show-expr '(  +  1  2 )'` | `(+ 1 2)` | whitespace normalized via unparse |
| `stack_machine --show-expr '(/ 1 0)'` | `(/ 1 0)` | domain error **not** raised (no eval) |

Stack and free CLIs must print the **same** show-expr string for the same source (both use shared `parse` + `unparse`).

### Example C — usage failures

| Argv (conceptual) | Outcome |
| --- | --- |
| no expression | usage error |
| two expression strings | usage error |
| `--show-expr` alone | usage error |
| unknown `--foo` | usage error |

### Example D — composition sketch (tests)

- Default mode: existing CLI corpus stays green after both mains delegate to `cli.main`.
- Show-expr: for fixtures `s`, assert stdout == `unparse(parse(s))` on **both** `-m beads_lab.stack_machine` and `-m beads_lab.free_monad`.
- Import boundary: `cli` does not import evaluator modules; evaluator modules do not gain a dependency on each other.

## Invariants (implementer checklist)

- Default mode exit codes and stdout for valid evaluate cases match pre-polish behavior (`Fraction` `__str__`).
- Show-expr never calls `Evaluator.evaluate`.
- Parse errors in either mode: stderr message, non-zero exit, empty stdout.
- Domain errors only in evaluate mode.
- Usage text may mention `--show-expr`; keep messages test-friendly (non-empty stderr on usage failure is enough unless a task requires exact text).

## Observables

An implementer verifies without peeking at argv-parser internals:

- Parametrized / duplicated CLI tests: same expression → same Fraction on both modules (regression).
- Show-expr fixtures: spaced input → canonical unparse string on both modules.
- `(/ 1 0)` with `--show-expr` exits 0 with stdout `(/ 1 0)`; without the flag, non-zero domain failure.
- Dependency / import check: no `stack_machine` ↔ `free_monad` edge; `cli` not imported by `parser` / `printer`.

## Relation to shipped work

| Piece | Status |
| --- | --- |
| `Expr`, parse, both evaluators, FR1–FR7 | Shipped — do not redesign |
| `unparse` / `printer.py` / FR8 | Shipped — reuse only |
| Shared CLI driver + `--show-expr` | **This capability** |

## References

- CLI contract baseline: [architecture.md](./architecture.md)
- Unparse laws: [pretty-print.md](./pretty-print.md)
- Product surface: [prd.md](./prd.md)
- Terms: [glossary.md](./glossary.md)
