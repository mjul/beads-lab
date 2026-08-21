"""Parser and Evaluator protocols — the swappable interface surface (FR3).

Failure style (fixed for this project):
  - Parser.parse raises beads_lab.values.ParseError on ill-formed input.
  - Evaluator.evaluate raises beads_lab.values.DomainError when ⟦Expr⟧ fails
    (e.g. division by zero). Do not return Result/Either; raise instead.
"""

from __future__ import annotations

from typing import Protocol

from beads_lab.expression import Expr
from beads_lab.values import Rational


class Parser(Protocol):
    """Maps a source string to an Expr AST."""

    def parse(self, source: str) -> Expr:
        """Parse ``source`` into an expression, or raise ParseError."""
        ...


class Evaluator(Protocol):
    """Maps an Expr to a rational (Fraction)."""

    def evaluate(self, expr: Expr) -> Rational:
        """Evaluate ``expr``, or raise DomainError on domain failure."""
        ...


def run(parser: Parser, evaluator: Evaluator, source: str) -> Rational:
    """Compose parser then evaluator; optional CLI convenience, not a new semantics."""
    return evaluator.evaluate(parser.parse(source))
