"""Free-monad evaluator: free structure + algebra → Fraction (bl-i7g.4.1)."""

from __future__ import annotations

from fractions import Fraction

import pytest

from beads_lab.expression import App, Builtin, Lit, Op

# Import under test — must exist for bl-i7g.4.1
from beads_lab.free_monad import Evaluator
from beads_lab.parser import Parser
from beads_lab.protocols import Evaluator as EvaluatorProtocol
from beads_lab.protocols import run
from beads_lab.stack_machine import Evaluator as StackEvaluator
from beads_lab.values import DomainError, ParseError


@pytest.fixture
def evaluator() -> Evaluator:
    return Evaluator()


@pytest.fixture
def parser() -> Parser:
    return Parser()


@pytest.fixture
def stack() -> StackEvaluator:
    return StackEvaluator()


def test_evaluator_satisfies_protocol_structurally(evaluator: Evaluator) -> None:
    typed: EvaluatorProtocol = evaluator
    assert typed.evaluate(Lit(42)) == Fraction(42)


SUCCESS_CASES = [
    ("42", Fraction(42)),
    ("-7", Fraction(-7)),
    ("(+)", Fraction(0)),
    ("(*)", Fraction(1)),
    ("(+ 1 2)", Fraction(3)),
    ("(* 2 (+ 3 4))", Fraction(14)),
    ("(- 5)", Fraction(-5)),
    ("(- 10 3 1)", Fraction(6)),
    ("(/ 2)", Fraction(1, 2)),
    ("(/ 8 2 2)", Fraction(2)),
    ("(mod 10 3)", Fraction(1)),
    ("(mod -10 3)", Fraction(2)),
    ("(mod 10 -3)", Fraction(-2)),
    ("(pow 2 3)", Fraction(8)),
    ("(pow 2 -3)", Fraction(1, 8)),
    ("(pow -2 3)", Fraction(-8)),
    ("(pow 0 5)", Fraction(0)),
    ("(+ 1 (* 2 3))", Fraction(7)),
]

DOMAIN_ERROR_SOURCES = [
    "(/ 0)",
    "(/ 1 0)",
    "(/ 8 2 0)",
    "(mod 1 0)",
    "(pow 0 0)",
    "(pow 0 -1)",
]

DOMAIN_ERROR_EXPRS = [
    App(Op.DIV, (Lit(0),)),
    App(Op.DIV, (Lit(1), Lit(0))),
    App(Builtin.MOD, (Lit(1), Lit(0))),
    App(Builtin.MOD, (App(Op.DIV, (Lit(1), Lit(2))), Lit(2))),
    App(Builtin.MOD, (Lit(2), App(Op.DIV, (Lit(1), Lit(2))))),
    App(Builtin.POW, (Lit(2), App(Op.DIV, (Lit(1), Lit(2))))),
    App(Builtin.POW, (Lit(0), Lit(0))),
    App(Builtin.POW, (Lit(0), Lit(-1))),
]


@pytest.mark.parametrize(("source", "expected"), SUCCESS_CASES)
def test_run_matches_denotation_table(
    parser: Parser, evaluator: Evaluator, source: str, expected: Fraction
) -> None:
    assert run(parser, evaluator, source) == expected


@pytest.mark.parametrize(("source", "expected"), SUCCESS_CASES)
def test_agrees_with_stack_on_success(
    parser: Parser,
    evaluator: Evaluator,
    stack: StackEvaluator,
    source: str,
    expected: Fraction,
) -> None:
    expr = parser.parse(source)
    assert evaluator.evaluate(expr) == stack.evaluate(expr) == expected


def test_evaluate_lit_and_nested_app_directly(evaluator: Evaluator) -> None:
    expr = App(Op.MUL, (Lit(2), App(Op.ADD, (Lit(3), Lit(4)))))
    assert evaluator.evaluate(expr) == Fraction(14)


@pytest.mark.parametrize("source", DOMAIN_ERROR_SOURCES)
def test_domain_errors_via_parser_and_evaluator(
    parser: Parser, evaluator: Evaluator, source: str
) -> None:
    with pytest.raises(DomainError):
        run(parser, evaluator, source)


@pytest.mark.parametrize("source", DOMAIN_ERROR_SOURCES)
def test_domain_error_class_agrees_with_stack(
    parser: Parser, evaluator: Evaluator, stack: StackEvaluator, source: str
) -> None:
    expr = parser.parse(source)
    with pytest.raises(DomainError):
        stack.evaluate(expr)
    with pytest.raises(DomainError):
        evaluator.evaluate(expr)


@pytest.mark.parametrize("expr", DOMAIN_ERROR_EXPRS)
def test_domain_error_on_direct_expr(evaluator: Evaluator, expr: App) -> None:
    with pytest.raises(DomainError):
        evaluator.evaluate(expr)


def test_domain_error_is_not_parse_error(evaluator: Evaluator) -> None:
    with pytest.raises(DomainError) as exc_info:
        evaluator.evaluate(App(Op.DIV, (Lit(0),)))
    assert not isinstance(exc_info.value, ParseError)
