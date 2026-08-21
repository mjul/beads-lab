# Glossary

| Term | Meaning |
| --- | --- |
| **ℚ / rational** | Field of fractions of integers; concrete type `fractions.Fraction`. |
| **Expr** | Abstract syntax tree for the calculator language (literals and applications). |
| **Lisp prefix** | Fully parenthesized prefix forms: `(op arg…)`. |
| **Parse** | Partial map string → Expr. |
| **Unparse / pretty-print** | Total map Expr → canonical Lisp-prefix string (inverse of parse up to whitespace). |
| **Canonical concrete syntax** | Unique spacing and lexeme choices produced by `unparse` (see [pretty-print.md](./pretty-print.md)). |
| **CLI driver** | Shared one-shot argv → exit orchestration; injects an `Evaluator` for evaluate mode (see [cli-polish.md](./cli-polish.md)). |
| **`--show-expr`** | CLI output mode: print `unparse(parse(s))` without evaluating. |
| **⟦·⟧ / denotation** | Shared mathematical meaning of an Expr as a rational (or domain failure). |
| **Parser (protocol)** | Interface with `parse(str) -> Expr`. |
| **Evaluator (protocol)** | Interface with `evaluate(Expr) -> Fraction`. |
| **Domain error** | Failure of ⟦·⟧ on a well-formed Expr (e.g. division by zero). |
| **Stack machine** | Operational evaluator using an explicit value stack; same ⟦·⟧. |
| **Free monad interpreter** | Evaluator that interprets a free structure of ops into ℚ; same ⟦·⟧. |
| **arch-feedback** | `bd` issue prefix used by the implementer when design blocks or hurts implementation. |
