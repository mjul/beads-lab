"""Shared Lisp-prefix parser: string → Expr (bl-i7g.2.1)."""

from __future__ import annotations

import pytest

from beads_lab.expression import App, Builtin, Lit, Op
from beads_lab.parser import Parser
from beads_lab.protocols import Parser as ParserProtocol
from beads_lab.values import ParseError


@pytest.fixture
def parser() -> Parser:
    return Parser()


def test_parser_satisfies_protocol_structurally(parser: Parser) -> None:
    typed: ParserProtocol = parser
    assert typed.parse("42") == Lit(42)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("42", Lit(42)),
        ("-7", Lit(-7)),
        ("0", Lit(0)),
        ("(+ 1 2)", App(Op.ADD, (Lit(1), Lit(2)))),
        (
            "(* 2 (+ 3 4))",
            App(Op.MUL, (Lit(2), App(Op.ADD, (Lit(3), Lit(4))))),
        ),
        ("(mod 10 3)", App(Builtin.MOD, (Lit(10), Lit(3)))),
        ("(pow 2 3)", App(Builtin.POW, (Lit(2), Lit(3)))),
        ("(+)", App(Op.ADD, ())),
        ("(*)", App(Op.MUL, ())),
        ("(- 5)", App(Op.SUB, (Lit(5),))),
        ("(/ 2)", App(Op.DIV, (Lit(2),))),
        (
            "(- 10 3 1)",
            App(Op.SUB, (Lit(10), Lit(3), Lit(1))),
        ),
    ],
)
def test_well_formed_sources_parse_to_expr(
    parser: Parser, source: str, expected: Lit | App
) -> None:
    assert parser.parse(source) == expected


def test_whitespace_separates_tokens_and_is_insignificant(parser: Parser) -> None:
    assert parser.parse("  ( +   1\n2\t)  ") == App(Op.ADD, (Lit(1), Lit(2)))


@pytest.mark.parametrize(
    "source",
    [
        "",
        "   ",
        "(",
        "(+",
        "(+ 1",
        "(+ 1 2",
        ")",
        "(+ 1 2))",
        "((+ 1 2)",
        "(foo 1)",
        "(1 2)",
        "(mod 1)",
        "(mod 1 2 3)",
        "(pow)",
        "(pow 2)",
        "1 2",
        "(+ 1 2) 3",
        "1.5",
        "(+ 1.5 2)",
        "()",
    ],
)
def test_ill_formed_sources_raise_parse_error(parser: Parser, source: str) -> None:
    with pytest.raises(ParseError):
        parser.parse(source)
