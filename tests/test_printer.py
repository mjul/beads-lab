"""Unparse Expr → canonical Lisp-prefix string (workspace-9rn)."""

from __future__ import annotations

from pathlib import Path

import pytest

from beads_lab.expression import App, Lit, Op
from beads_lab.printer import unparse


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (Lit(0), "0"),
        (Lit(42), "42"),
        (Lit(-3), "-3"),
    ],
)
def test_unparse_lit_to_decimal_token(expr: Lit, expected: str) -> None:
    assert unparse(expr) == expected


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


def test_unparse_app_not_required_yet() -> None:
    """YAGNI split: App may remain unimplemented until workspace-nca."""
    expr = App(Op.ADD, (Lit(1), Lit(2)))
    try:
        result = unparse(expr)
    except NotImplementedError:
        return
    assert result == "(+ 1 2)"
