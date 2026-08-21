"""Pretty-print / unparse: Expr → canonical Lisp-prefix string."""

from __future__ import annotations

from beads_lab.expression import App, Expr, Lit


def unparse(expr: Expr) -> str:
    """Map an Expr to its canonical concrete syntax string."""
    match expr:
        case Lit(value):
            return str(value)
        case App():
            raise NotImplementedError("unparse for App is not implemented yet")
        case _:
            raise TypeError(f"expected Expr, got {type(expr)!r}")
