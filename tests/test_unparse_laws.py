"""Composition laws for unparse (docs/pretty-print.md).

1. Left inverse: parse(unparse(e)) == e
2. Normalization: unparse(parse(s)) is the canonical representative

Public APIs only: Parser, unparse, Expr ADT. No evaluator assertions.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from beads_lab.expression import App, Builtin, Expr, Lit, Op
from beads_lab.parser import Parser
from beads_lab.printer import unparse

# Fixed corpus: ADT-built trees covering literals, nullary, unary, n-ary,
# builtins, and nesting (docs/pretty-print.md Examples A–C).
ROUND_TRIP_EXPRS: list[Expr] = [
    Lit(0),
    Lit(42),
    Lit(-7),
    App(Op.ADD, ()),
    App(Op.MUL, ()),
    App(Op.ADD, (Lit(1), Lit(2))),
    App(Op.SUB, (Lit(5),)),
    App(Op.DIV, (Lit(2),)),
    App(Op.SUB, (Lit(10), Lit(3), Lit(1))),
    App(Op.DIV, (Lit(8), Lit(2), Lit(2))),
    App(Op.MUL, (Lit(2), Lit(3), Lit(4))),
    App(Op.ADD, (Lit(1), App(Op.MUL, (Lit(2), Lit(3))))),
    App(Op.MUL, (Lit(2), App(Op.ADD, (Lit(3), Lit(4))))),
    App(Builtin.MOD, (Lit(10), Lit(3))),
    App(Builtin.POW, (Lit(2), Lit(3))),
    App(Builtin.POW, (App(Op.ADD, (Lit(1), Lit(1))), App(Op.MUL, (Lit(2), Lit(2))))),
    App(Builtin.MOD, (App(Op.MUL, (Lit(3), Lit(4))), App(Op.ADD, (Lit(1), Lit(2))))),
]

ROUND_TRIP_SOURCES = [
    "42",
    "-7",
    "0",
    "(+)",
    "(*)",
    "(+ 1 2)",
    "(- 5)",
    "(/ 2)",
    "(- 10 3 1)",
    "(/ 8 2 2)",
    "(* 2 3 4)",
    "(+ 1 (* 2 3))",
    "(* 2 (+ 3 4))",
    "(mod 10 3)",
    "(pow 2 3)",
    "(pow (+ 1 1) (* 2 2))",
    "(mod (* 3 4) (+ 1 2))",
    "(* (pow 2 3) (mod 10 3))",
]

# Example C + spaced variants: (input, exact canonical unparse(parse(s))).
NORMALIZATION_CASES: list[tuple[str, str]] = [
    ("(  mod   10  3 )", "(mod 10 3)"),
    ("(pow 2 3)", "(pow 2 3)"),
    ("  (  +   1\n2\t)  ", "(+ 1 2)"),
    ("(  *  )", "(*)"),
    ("( + )", "(+)"),
    ("(-   5)", "(- 5)"),
    ("( /  8  2  2 )", "(/ 8 2 2)"),
    ("(  pow   2   3  )", "(pow 2 3)"),
    ("(+  1  (  *  2  3 ) )", "(+ 1 (* 2 3))"),
    ("  42  ", "42"),
    ("\n-7\t", "-7"),
]


@pytest.fixture
def parser() -> Parser:
    return Parser()


@pytest.mark.parametrize("expr", ROUND_TRIP_EXPRS)
def test_parse_unparse_round_trip_on_adt_corpus(parser: Parser, expr: Expr) -> None:
    """Left inverse: Parser().parse(unparse(e)) == e for ADT-built Expr."""
    assert parser.parse(unparse(expr)) == expr


@pytest.mark.parametrize("source", ROUND_TRIP_SOURCES)
def test_parse_unparse_round_trip_on_parsed_corpus(parser: Parser, source: str) -> None:
    """Left inverse also holds for Expr obtained by parsing known strings."""
    expr = parser.parse(source)
    assert parser.parse(unparse(expr)) == expr


@st.composite
def well_formed_exprs(draw: st.DrawFn) -> Expr:
    """Generate well-formed Expr trees (ADT constraints only)."""

    def leaf() -> st.SearchStrategy[Expr]:
        return st.integers(min_value=-50, max_value=50).map(Lit)

    def extend(children: st.SearchStrategy[Expr]) -> st.SearchStrategy[Expr]:
        op_app = st.builds(
            App,
            st.sampled_from(list(Op)),
            st.lists(children, min_size=0, max_size=4).map(tuple),
        )
        builtin_app = st.builds(
            App,
            st.sampled_from(list(Builtin)),
            st.tuples(children, children),
        )
        return st.one_of(op_app, builtin_app)

    return draw(st.recursive(leaf(), extend, max_leaves=12))


@given(expr=well_formed_exprs())
@settings(max_examples=100, deadline=None)
def test_parse_unparse_round_trip_hypothesis(expr: Expr) -> None:
    """Property: parse(unparse(e)) == e for random well-formed Expr trees."""
    assert Parser().parse(unparse(expr)) == expr


@pytest.mark.parametrize(("source", "canonical"), NORMALIZATION_CASES)
def test_unparse_parse_normalizes_to_canonical_string(
    parser: Parser, source: str, canonical: str
) -> None:
    """unparse(parse(s)) equals the exact canonical representative."""
    assert unparse(parser.parse(source)) == canonical


@pytest.mark.parametrize(("source", "canonical"), NORMALIZATION_CASES)
def test_parse_unparse_parse_equals_parse(
    parser: Parser, source: str, canonical: str
) -> None:
    """Normalization law: parse(unparse(parse(s))) == parse(s)."""
    parsed = parser.parse(source)
    assert parser.parse(unparse(parsed)) == parsed
    assert unparse(parsed) == canonical
