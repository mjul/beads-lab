# Architecture: rational Lisp-prefix calculator

This document defines modules, protocols, and **denotational** meaning. Implementers realize these meanings; they do not invent alternate ADTs.

## Module map

```text
beads_lab/
  expression.py     # Expr ADT (syntax)
  values.py         # Rational = fractions.Fraction; error types (conceptual)
  protocols.py      # Parser, Evaluator protocols
  parser.py         # str → Expr
  printer.py        # Expr → canonical Lisp-prefix str (unparse; next capability)
  stack_machine.py  # Evaluator + CLI (stack realization)
  free_monad.py     # Evaluator + CLI (free-monad realization)
```

Dependency direction (allowed edges only):

```text
expression ← parser, printer
expression ← stack_machine, free_monad
protocols  ← parser, stack_machine, free_monad   (implement / type against)
values     ← stack_machine, free_monad
parser     ← stack_machine, free_monad           (CLI composition only)
```

`stack_machine` and `free_monad` must **not** depend on each other.
`printer` must **not** depend on `parser` or either evaluator (round-trips compose in tests only).

## Carriers and denotations

### Rational values

- **Carrier**: ℚ, the field of rational numbers.
- **Concrete denotation**: Python `fractions.Fraction` in canonical form (unique representation with positive denominator).
- **Composition**: field operations \(+\), \(-\), \(\times\), \(\div\) on ℚ (partial for \(\div\) when divisor = 0).

### Expression ADT (`Expr`)

`Expr` denotes an **abstract syntax tree**, not a value.

Informal grammar of the carrier:

```text
Expr ::= Lit(ℤ)
       | App(Op, Expr*)           # Op ∈ {+, -, *, /}
       | App(Builtin, Expr*)      # Builtin ∈ {mod, pow}
```

(Names `Lit` / `App` are conceptual; implementer may use dataclasses/enums/ADTs that preserve this structure.)

**Composition of syntax**: tree substitution / nesting. Associativity of *syntax* is just tree structure; arithmetic associativity is a property of ⟦·⟧, not of the ADT.

### Parsing

\[
\mathrm{parse} : \mathsf{String} \rightharpoonup \mathsf{Expr}
\]

Partial: fails on ill-formed token streams (unbalanced parens, unknown heads, empty input that is not a single expression, etc.).

**Observables**: given a string, either a unique `Expr` (up to ADT equality) or a parse error. No evaluator dependency.

**Consistency**: `parser.py` is the sole implementation used by both CLIs.

### Evaluation (shared denotation)

Both evaluators realize the same totalization of:

\[
[\![\cdot]\!] : \mathsf{Expr} \rightharpoonup \mathbb{Q}
\]

Defined by structural recursion (sketch):

| Form | Denotation |
| --- | --- |
| \(\mathrm{Lit}(n)\) | \(n\) as rational |
| \((+ \; e_1 \ldots e_k)\) | \(\sum_i [\![e_i]\!]\) (empty → 0) |
| \((* \; e_1 \ldots e_k)\) | \(\prod_i [\![e_i]\!]\) (empty → 1) |
| \((- \; e)\) | \(-[\![e]\!]\) |
| \((- \; e_1 \; e_2 \ldots e_k)\) \(k\ge 2\) | left fold subtraction |
| \((/ \; e)\) | \(1 / [\![e]\!]\) if nonzero |
| \((/ \; e_1 \; e_2 \ldots e_k)\) \(k\ge 2\) | left fold division |
| \((\mathrm{mod} \; e_1 \; e_2)\) | integer modulus when both dens = 1; else domain error |
| \((\mathrm{pow} \; e_1 \; e_2)\) | \([\![e_1]\!]^{n}\) when \([\![e_2]\!] = n \in \mathbb{Z}\); else domain error |

**Domain errors** (evaluation fails; not parse failures):

- Division or reciprocal with divisor 0
- `mod` with non-integer arguments or modulus 0
- `pow` with non-integer exponent
- Wrong arity for `mod` / `pow` (must be exactly 2) — may be parse-time *or* eval-time; prefer **parse-time or ADT construction** once heads are known, but if deferred, both evaluators must agree

**`mod` sign convention**: match Python’s `int.__mod__` on the integer numerators (same as `Fraction` with denominator 1): result has the sign of the divisor, \(0 \le |r| < |m|\) in the usual Python sense.

**`pow`**: for negative exponents, result is the rational reciprocal power when the base ≠ 0; `0` to a non-positive integer exponent is a domain error.

**Composition law (observational)**: for all strings `s` that parse,

\[
[\![\mathrm{parse}(s)]\!]_{\mathsf{stack}} \;\equiv\; [\![\mathrm{parse}(s)]\!]_{\mathsf{free}}
\]

(same rational or same domain-error class). This is the **consistency** obligation between the two modules.

## Protocols

Single interface surface (Python `typing.Protocol`):

```text
Parser:
  parse(source: str) -> Expr
  # raises / returns a documented parse failure — pick one style in implementation
  # and stick to it in tests

Evaluator:
  evaluate(expr: Expr) -> Fraction
  # domain errors: documented exception type shared or aliased
```

Optional convenience (not a second semantic object):

```text
def run(parser: Parser, evaluator: Evaluator, source: str) -> Fraction:
    return evaluator.evaluate(parser.parse(source))
```

CLIs are thin: argv string → `run` → print `Fraction` (normalize string form, e.g. `Fraction` `__str__`).

## Realization strategies (what differs)

### Stack machine (`stack_machine.py`)

- **Denotation of the machine**: a stack of rationals + control from walking `Expr` (or an explicit instruction list derived from `Expr`).
- Post-order evaluation: evaluate children, push, apply operator to popped args, push result.
- Must not change ⟦·⟧; stack is an operational artifact.

### Free monad interpreter (`free_monad.py`)

- **Syntax-as-program**: reflect `Expr` (or an instruction functor of arithmetic ops) into a free monad / free structure.
- **Interpreter**: algebra `F ℚ → ℚ` implementing the same table as ⟦·⟧.
- Free composition of programs corresponds to composition of `Expr` subtrees; the interpreter preserves that denotation.

Keep the free construction **minimal**: enough to demonstrate interpretation of a free structure over calculator operations—not a general effects framework.

## Error taxonomy

| Kind | Origin | Examples |
| --- | --- | --- |
| Parse error | `parser` | unbalanced `)`, unknown symbol, truncated input |
| Domain error | `Evaluator` | `/ 0`, `mod` non-int, bad `pow` |

Do not conflate these in tests or CLI exit semantics: prefer distinct exception types or error tags.

## CLI contract

Both modules expose a `__main__` / `main` that:

1. Accepts exactly one expression string (beyond program name); excess/missing args → usage error.
2. Uses `parser.py` + that module’s `Evaluator`.
3. On success: prints the rational to stdout (stable, test-friendly).
4. On parse/domain error: non-zero exit and message on stderr.

## Testing guidance (for implementer)

- Prefer high-level tests against `Parser` / `Evaluator` protocols and CLI.
- Cross-check: property or parametrized tests that stack and free agree on a corpus of expressions.
- Do not assert stack depth or free-monad node shapes unless a task explicitly asks.

## Out of scope for this architecture pass

Concrete class names beyond the conceptual ADT, packaging entry points in `pyproject.toml` (implementer may add script entries when implementing CLI tasks), and performance targets.

## Backlog (Beads)

### Shipped — Lisp-prefix rational calculator

Epic **workspace-bp7** (*Lisp-prefix rational calculator*; earlier design id `bl-i7g`) is **complete**. Features and leaf tasks covered protocols, shared `parser.py`, stack-machine and free-monad evaluators + CLIs, and FR7 observational equivalence (**workspace-cw3**). Module reality on master matches the map above (minus `printer.py` until the next epic lands).

Do **not** redesign ⟦·⟧, the `Expr` ADT, or the two evaluators for new work.

### Next — pretty-print / unparse

Epic **workspace-o2p** — canonical `Expr` → Lisp-prefix string (inverse of parse; does not change evaluation). Spec: [pretty-print.md](./pretty-print.md).

| ID | Role | Notes |
| --- | --- | --- |
| `workspace-o2p` | Epic (track) | Already decomposed; prefer leaf tasks. Close when feature is done. |
| `workspace-o2p.2` | Feature | Blocked until all four leaf tasks close |
| `workspace-9rn` | Task | **`unparse` Lit** — first ready implementable leaf |
| `workspace-nca` | Task | **`unparse` App** — depends on `workspace-9rn` |
| `workspace-6ns` | Task | **Syntax round-trip** — depends on `workspace-nca` |
| `workspace-fzz` | Task | **Canonical normalization** — depends on `workspace-nca` |

Implementable order (dependencies in `bd`):

1. `workspace-9rn` — `unparse` literals
2. `workspace-nca` — `unparse` applications
3. `workspace-6ns` + `workspace-fzz` — round-trip and normalization (parallel after App)

Start with: `bd update workspace-9rn --claim` (or `bd ready --type=task`).
