# PRD: Lisp-prefix rational calculator

## Problem

We need a small, well-specified calculator that evaluates arithmetic expressions written in **Lisp prefix notation**, with values in the **rationals over the integers** (ℚ). Two evaluation strategies must share one parser and one semantic contract so they stay interchangeable.

## Goals

1. Parse a string into an expression ADT.
2. Evaluate an expression to an exact rational value.
3. Expose a **single protocol surface** for parsing and evaluation so implementations are swappable.
4. Ship **two evaluator realizations** with separate CLIs, both using the same parser:
   - stack machine (`stack_machine.py`)
   - free-monad interpreter (`free_monad.py`)
5. Keep the design small enough for TDD with YAGNI (no variables, no user-defined functions, no REPL beyond one-shot CLI).

## Non-goals (YAGNI)

- Infix/float approximation modes
- Variables, bindings, or `lambda`
- Macros, quoting, or full Lisp
- Multiprecision beyond Python `int` / `fractions.Fraction`
- Interactive REPL, files-as-programs, or package plugins
- Source maps, spans, or multi-line indented layouts (canonical single-line `unparse` shipped; see FR8)
- Alternate rational print modes (exact vs mixed number) until a later epic
- Printing both Fraction and unparsed form in one CLI invocation (see FR9 / [cli-polish.md](./cli-polish.md) for single-mode `--show-expr`)

## Users and interface

- **Primary user**: developer / agent running expressions from the shell for verification and demos.
- **Invocation**: each evaluator entry point takes **one expression string** as a command-line argument (unit of input = that string), optionally with `--show-expr`, parses with shared `parser.py`, and prints either the rational result or the canonical unparsed form (or a clear error) on stdout/stderr. Shared driver: [cli-polish.md](./cli-polish.md).

Example shape (concrete packaging left to implementer; behavior is normative):

```bash
uv run python -m beads_lab.stack_machine '(+ 1 (* 2 3))'
uv run python -m beads_lab.free_monad '(pow 2 3)'
uv run python -m beads_lab.stack_machine --show-expr '(  +  1  2 )'
```

## Language surface

### Syntax (Lisp prefix)

- An **atom** is an integer literal: digits with optional leading `-` on the atom itself only when the token is a negative literal (e.g. `-42`). Whitespace separates tokens.
- A **form** is `(` followed by an operator or built-in name, zero or more expressions, then `)`.
- Nesting is unrestricted (finite trees).

Examples:

| Source | Meaning |
| --- | --- |
| `42` | literal |
| `(+ 1 2)` | sum |
| `(* 2 (+ 3 4))` | nested |
| `(mod 10 3)` | remainder |
| `(pow 2 3)` | exponentiation |

### Operators

| Symbol | Role | Arity |
| --- | --- | --- |
| `+` | addition | n-ary, n ≥ 0; empty sum = 0 |
| `*` | multiplication | n-ary, n ≥ 0; empty product = 1 |
| `-` | negation / subtraction | unary: negate; n ≥ 2: left-associative fold \(a - b - \cdots\) |
| `/` | division | unary: reciprocal; n ≥ 2: left-associative fold \(a / b / \cdots\) |

### Built-in functions

| Name | Arity | Meaning |
| --- | --- | --- |
| `mod` | 2 | remainder of first argument modulo second (see semantics doc for sign convention) |
| `pow` | 2 | exponentiation: base raised to an **integer** exponent |

### Value domain

- All successful evaluations yield a value in ℚ, represented concretely by `fractions.Fraction` (integers as denominators 1).
- Integer literals denote themselves as rationals.

## Functional requirements

| ID | Requirement |
| --- | --- |
| FR1 | Parser maps a well-formed string to an expression ADT; rejects ill-formed input with a parse error. |
| FR2 | Evaluator maps a well-formed expression to a rational, or a domain error (e.g. division by zero). |
| FR3 | `Parser` and `Evaluator` are defined as protocols; stack-machine and free-monad evaluators both satisfy `Evaluator`. |
| FR4 | Shared `parser.py` is the only parser used by both CLIs. |
| FR5 | Stack-machine evaluator lives in `stack_machine.py` and provides a CLI entry. |
| FR6 | Free-monad interpreter lives in `free_monad.py` and provides a CLI entry. |
| FR7 | For every successfully parsed expression, both evaluators agree on success value or both signal the same class of domain error (observational equivalence of denotation). |
| FR8 | `unparse` maps every well-formed `Expr` to a canonical Lisp-prefix string such that `parse(unparse(e)) = e`; whitespace variants that parse normalize via `unparse` (see [pretty-print.md](./pretty-print.md)). |
| FR9 | Both CLIs share one driver: default mode prints the rational; optional `--show-expr` prints `unparse(parse(s))` without evaluating (see [cli-polish.md](./cli-polish.md)). |

## Non-functional requirements

- Exact arithmetic (no silent float).
- Small public surface; tests target protocols and CLI behavior, not private helpers.
- Clear module boundaries documented in `docs/architecture.md`.

## Success metrics

- Docs define denotations for Expr, ℚ, parse, eval, unparse, and (FR9) CLI output modes.
- Calculator epic (FR1–FR7) and pretty-print (FR8) shipped; next backlog covers CLI polish with dependencies and observables.
- Implementer can TDD each task from docs without inventing competing ADTs.

## Open decisions (resolved here)

| Topic | Decision |
| --- | --- |
| Rational representation | `fractions.Fraction` |
| `pow` exponent | must be an integer (denominator 1); otherwise domain error |
| `mod` on rationals | require both arguments to be integers (ℤ ⊂ ℚ); else domain error |
| Package layout | under `beads_lab` (see architecture) |

## References

- Architecture & denotations: [architecture.md](./architecture.md)
- Pretty-print / unparse: [pretty-print.md](./pretty-print.md)
- CLI polish: [cli-polish.md](./cli-polish.md)
- Glossary: [glossary.md](./glossary.md)
- Agent workflow: [agents-workflow.md](./agents-workflow.md)
