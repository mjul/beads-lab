"""Unparse Expr → canonical Lisp-prefix string (docs/pretty-print.md)."""

from __future__ import annotations

from pathlib import Path

import pytest

from beads_lab.expression import App, Builtin, Lit, Op
from beads_lab.printer import unparse


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        # Example A — literals
        (Lit(0), "0"),
        (Lit(42), "42"),
        (Lit(-3), "-3"),
        # Example A — simple app / nullary
        (App(Op.ADD, (Lit(1), Lit(2))), "(+ 1 2)"),
        (App(Op.MUL, ()), "(*)"),
        (App(Op.ADD, ()), "(+)"),
        # Unary / n-ary - and /
        (App(Op.SUB, (Lit(5),)), "(- 5)"),
        (App(Op.DIV, (Lit(2),)), "(/ 2)"),
        (App(Op.SUB, (Lit(10), Lit(3), Lit(1))), "(- 10 3 1)"),
        (App(Op.DIV, (Lit(8), Lit(2), Lit(2))), "(/ 8 2 2)"),
        # Example B — nesting
        (App(Op.ADD, (Lit(1), App(Op.MUL, (Lit(2), Lit(3))))), "(+ 1 (* 2 3))"),
        # Example C — builtins
        (App(Builtin.MOD, (Lit(10), Lit(3))), "(mod 10 3)"),
        (App(Builtin.POW, (Lit(2), Lit(3))), "(pow 2 3)"),
    ],
)
def test_unparse_expr_to_canonical_string(expr: Lit | App, expected: str) -> None:
    assert unparse(expr) == expected


def test_unparse_app_spacing_invariants() -> None:
    """One space between tokens; no space after '(' or before ')'; no newlines."""
    result = unparse(App(Op.ADD, (Lit(1), App(Op.MUL, (Lit(2), Lit(3))))))
    assert result == "(+ 1 (* 2 3))"
    assert "  " not in result
    assert "\n" not in result
    assert "( " not in result
    assert " )" not in result


def test_printer_source_imports_expression_only() -> None:
    source = Path(__file__).resolve().parents[1] / "src" / "beads_lab" / "printer.py"
    text = source.read_text(encoding="utf-8")
    assert "expression" in text
    for forbidden in (
        "beads_lab.parser",
        "beads_lab.stack_machine",
        "beads_lab.free_monad",
        "beads_lab.values",
        "beads_lab.protocols",
        "from .parser",
        "from .stack_machine",
        "from .free_monad",
        "from .values",
        "from .protocols",
    ):
        assert forbidden not in text
