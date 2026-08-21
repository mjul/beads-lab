"""Parser/Evaluator protocols and run composition (bl-i7g.1.2)."""

from fractions import Fraction

import pytest

from beads_lab.expression import Expr, Lit
from beads_lab.protocols import Evaluator, Parser, run
from beads_lab.values import DomainError, ParseError


class _StubParser:
    """Structural stand-in: parse only the sentinel source 'ok'."""

    def parse(self, source: str) -> Expr:
        if source != "ok":
            raise ParseError(f"ill-formed: {source!r}")
        return Lit(7)


class _StubEvaluator:
    """Structural stand-in: Lit(n) → n/1; reject Lit(0) as domain error."""

    def evaluate(self, expr: Expr) -> Fraction:
        if not isinstance(expr, Lit):
            raise DomainError("stub only handles Lit")
        if expr.value == 0:
            raise DomainError("zero domain")
        return Fraction(expr.value)


def test_run_composes_structural_parser_and_evaluator() -> None:
    parser: Parser = _StubParser()
    evaluator: Evaluator = _StubEvaluator()
    assert run(parser, evaluator, "ok") == Fraction(7)


def test_run_propagates_parse_error_from_parser() -> None:
    with pytest.raises(ParseError):
        run(_StubParser(), _StubEvaluator(), "nope")


def test_run_propagates_domain_error_from_evaluator() -> None:
    class ZeroParser:
        def parse(self, source: str) -> Expr:
            return Lit(0)

    with pytest.raises(DomainError):
        run(ZeroParser(), _StubEvaluator(), "anything")
