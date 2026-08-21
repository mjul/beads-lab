# Capability: pretty-print / unparse

Inverse of parsing: map an `Expr` AST to a **canonical Lisp-prefix string**. Does **not** change ⟦·⟧; evaluators and the shared parser stay as shipped.

## Motivation

The calculator already has `parse : String ⇀ Expr`. Without the inverse, CLIs and tests cannot show AST shape as source text, and round-trip laws are hard to state. A single unparser unlocks readable dumps and observational checks without touching evaluation.

## Module map (addition)

```text
beads_lab/
  …                 # calculator modules (shipped; do not redesign)
  printer.py        # Expr → canonical Lisp-prefix str
```

Dependency direction (new edges only):

```text
expression ← printer
```

- `printer` must **not** depend on `parser`, `stack_machine`, `free_monad`, or `values` beyond what `Expr` already needs (no evaluation, no error types required for success path).
- `parser` must **not** depend on `printer` (composition lives in tests / future CLI helpers only).

## Denotation

\[
\mathrm{unparse} : \mathsf{Expr} \to \mathsf{String}
\]

Total on well-formed `Expr` values constructed by the ADT (including trees the parser would accept). Every output is a finite Lisp-prefix string that the shared `parser` accepts.

**Meaning of the string**: the same abstract syntax as the input tree, written in a **canonical concrete syntax** (defined below)—not an arbitrary pretty layout with line breaks or indentation (YAGNI).

## Canonical concrete syntax

| Form | Canonical string |
| --- | --- |
| `Lit(n)` | Decimal integer token: `0`, `42`, `-7` (no leading `+`; no extra zeros except the single digit `0`) |
| `App(op, [])` | `(+)` or `(*)` only for nullary `+` / `*` (other nullary heads are not in the ADT) |
| `App(head, e₁…eₖ)` `k≥1` | `(` + head lexeme + (` ` + unparse(eᵢ))⁺ + `)` |
| Head lexeme | `Op` → its symbol (`+`, `-`, `*`, `/`); `Builtin` → its name (`mod`, `pow`) |

**Spacing invariant**: exactly one space between head and first arg, and between consecutive args; no space after `(` or before `)`; no trailing whitespace; no newlines.

**Composition**: `unparse` is defined by structural recursion on `Expr`. Unparsing a tree is the concatenation of unparsed subtrees inside one outer form—associativity of string concat matches nesting of the ADT.

## Composition with parse (observational laws)

Let `parse` be the shared parser (raises `ParseError` on ill-formed input).

1. **Left inverse (syntax round-trip)** — for every well-formed `Expr` `e`:

   \[
   \mathrm{parse}(\mathrm{unparse}(e)) \;=\; e
   \]

   (ADT equality.)

2. **Normalization** — for every string `s` that `parse` accepts:

   \[
   \mathrm{parse}(\mathrm{unparse}(\mathrm{parse}(s))) \;=\; \mathrm{parse}(s)
   \]

   Equivalently, `unparse(parse(s))` is the **canonical representative** of the equivalence class of strings that parse to the same `Expr` (whitespace / token spacing may differ from `s`).

Unparse does **not** claim `unparse(parse(s)) = s` (source strings are not unique).

## What this does *not* denote

- Evaluation / rationals / domain errors
- Source maps, spans, or error-location annotations
- Multi-line or indented “pretty” layouts
- Quoting, symbols beyond calculator heads, or non-`Expr` values
- A second parser; round-trips always use existing `parser.py`

## Public surface (conceptual)

```text
unparse(expr: Expr) -> str
```

A `Printer` protocol is **out of scope** (single canonical realization; YAGNI). Call sites import the function (or a thin module-level API) from `printer.py`.

Optional later (not this epic): CLIs may print `unparse(expr)` in debug paths; default CLI output remains the rational.

## High-level examples

### Example A — literal and simple app

| Expr (conceptual) | `unparse` result |
| --- | --- |
| `Lit(42)` | `42` |
| `Lit(-3)` | `-3` |
| `App(+, [Lit(1), Lit(2)])` | `(+ 1 2)` |
| `App(*, [])` | `(*)` |

### Example B — nesting

Conceptual tree: `App(+, [Lit(1), App(*, [Lit(2), Lit(3)])])`

- `unparse` → `(+ 1 (* 2 3))`
- `parse` of that string recovers the same tree
- Evaluation (unchanged): ⟦·⟧ = 7

### Example C — builtins and whitespace normalization

| Input string `s` | `parse(s)` then `unparse` |
| --- | --- |
| `(  mod   10  3 )` | `(mod 10 3)` |
| `(pow 2 3)` | `(pow 2 3)` |

### Example D — composition law sketch (tests)

Corpus / property: generate or list `Expr` values → assert `parse(unparse(e)) == e`. Separately, for strings that parse, assert `parse(unparse(parse(s))) == parse(s)`.

## Invariants (implementer checklist)

- Output uses only calculator lexemes and parentheses; no float syntax.
- Nullary `+` / `*` unparse to `(+)` / `(*)` (matches parser / PRD empty sum and product).
- Unary `-` / `/` unparse as `(- e)` / `(/ e)`; n-ary folds as `(- e1 e2 …)` / `(/ e1 e2 …)`.
- Does not call an `Evaluator`; does not import stack/free modules.
- Round-trip law (1) holds for every `Expr` the ADT allows (including trees only reachable via ADT construction, if any).

## Observables

An implementer verifies without peeking at printer internals:

- Fixture table: known `Expr` → exact expected string.
- `parse(unparse(e)) == e` on a fixed corpus and (recommended) Hypothesis-generated well-formed trees.
- `unparse(parse(s))` matches the fixture canonical string for spaced variants of `s`.
- Import/dependency: `printer` does not import evaluators; evaluators need not import `printer`.

## Relation to shipped calculator

| Piece | Status |
| --- | --- |
| `Expr`, `Parser`, both `Evaluator`s, CLIs, FR1–FR7 | Shipped — do not redesign |
| `unparse` / `printer.py` | This capability |

## References

- Shared AST and parse denotation: [architecture.md](./architecture.md)
- Product language surface: [prd.md](./prd.md)
- Terms: [glossary.md](./glossary.md)
