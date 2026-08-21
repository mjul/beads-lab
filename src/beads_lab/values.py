"""Rational carrier and shared error types for the calculator."""

from fractions import Fraction

Rational = Fraction


class ParseError(Exception):
    """Ill-formed input rejected by the parser (not a denotation failure)."""


class DomainError(Exception):
    """Well-formed Expr whose denotation fails (e.g. division by zero)."""
