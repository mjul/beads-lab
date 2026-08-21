"""Expr ADT, Fraction alias, and distinct parse/domain errors (bl-i7g.1.1)."""

from fractions import Fraction as StdFraction

import pytest

from beads_lab.expression import App, Builtin, Lit, Op
from beads_lab.values import DomainError, ParseError, Rational


def test_rational_alias_is_fractions_fraction() -> None:
    assert Rational is StdFraction
    assert Rational(1, 2) == StdFraction(1, 2)


def test_parse_and_domain_errors_are_distinct_exception_types() -> None:
    assert issubclass(ParseError, Exception)
    assert issubclass(DomainError, Exception)
    assert ParseError is not DomainError
    assert not issubclass(ParseError, DomainError)
    assert not issubclass(DomainError, ParseError)


def test_lit_holds_integer_and_equals_structurally() -> None:
    assert Lit(42) == Lit(42)
    assert Lit(-7) != Lit(7)
    assert isinstance(Lit(0), (Lit, App))


def test_app_with_ops_allows_variable_arity() -> None:
    empty_sum = App(Op.ADD, ())
    nested = App(Op.MUL, (Lit(2), App(Op.ADD, (Lit(3), Lit(4)))))
    assert empty_sum == App(Op.ADD, ())
    assert nested.args[0] == Lit(2)
    assert isinstance(nested, (Lit, App))


def test_app_ops_cover_architecture_operators() -> None:
    assert {op.value for op in Op} == {"+", "-", "*", "/"}


def test_app_builtins_cover_mod_and_pow() -> None:
    assert {b.value for b in Builtin} == {"mod", "pow"}
    mod_app = App(Builtin.MOD, (Lit(10), Lit(3)))
    pow_app = App(Builtin.POW, (Lit(2), Lit(3)))
    assert mod_app == App(Builtin.MOD, (Lit(10), Lit(3)))
    assert pow_app != mod_app


def test_mod_and_pow_require_exactly_two_args_at_construction() -> None:
    with pytest.raises(ValueError):
        App(Builtin.MOD, (Lit(1),))
    with pytest.raises(ValueError):
        App(Builtin.POW, (Lit(1), Lit(2), Lit(3)))
    with pytest.raises(ValueError):
        App(Builtin.MOD, ())
