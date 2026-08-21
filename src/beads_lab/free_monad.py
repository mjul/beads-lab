"""Free-monad evaluator: free structure over calculator ops + algebra → Fraction."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from beads_lab.expression import Builtin, Expr, Lit, Op
from beads_lab.parser import Parser
from beads_lab.protocols import run
from beads_lab.values import DomainError, ParseError, Rational

_USAGE = "Usage: python -m beads_lab.free_monad <expression>"

# ---------------------------------------------------------------------------
# Free structure: Free F ∅ over the calculator instruction functor F.
#
#   F X  ≅  Lit(ℤ)  |  Op(op, [X])  |  Builtin(b, X, X)
#   Free F a  ≅  Pure a  |  Free (F (Free F a))
#
# We only need programs that terminate in ℚ (no open Pure holes), so the
# public carrier is FreeProg = Free (F FreeProg) with Lit as the leaf layer.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FreeLit:
    """Instruction: inject an integer literal into the free program."""

    value: int


@dataclass(frozen=True, slots=True)
class FreeOp:
    """Instruction: apply an n-ary arithmetic operator to free subprograms."""

    op: Op
    args: tuple[FreeProg, ...]


@dataclass(frozen=True, slots=True)
class FreeBuiltin:
    """Instruction: apply a binary builtin to free subprograms."""

    builtin: Builtin
    left: FreeProg
    right: FreeProg


type FreeProg = FreeLit | FreeOp | FreeBuiltin


def to_free(expr: Expr) -> FreeProg:
    """Reflect Expr into the free structure (syntax-as-program)."""
    if isinstance(expr, Lit):
        return FreeLit(expr.value)
    if isinstance(expr.head, Builtin):
        left, right = expr.args
        return FreeBuiltin(expr.head, to_free(left), to_free(right))
    return FreeOp(expr.head, tuple(to_free(a) for a in expr.args))


def _alg_op(op: Op, args: tuple[Rational, ...]) -> Rational:
    """Algebra F ℚ → ℚ for Op layers (shared denotation table)."""
    if op is Op.ADD:
        return sum(args, Rational(0))
    if op is Op.MUL:
        result = Rational(1)
        for a in args:
            result *= a
        return result
    if op is Op.SUB:
        if not args:
            raise DomainError("subtraction requires at least one argument")
        if len(args) == 1:
            return -args[0]
        result = args[0]
        for a in args[1:]:
            result -= a
        return result
    # Op.DIV
    if not args:
        raise DomainError("division requires at least one argument")
    if len(args) == 1:
        return _div(Rational(1), args[0])
    result = args[0]
    for a in args[1:]:
        result = _div(result, a)
    return result


def _alg_builtin(builtin: Builtin, left: Rational, right: Rational) -> Rational:
    """Algebra F ℚ → ℚ for Builtin layers."""
    if builtin is Builtin.MOD:
        return _mod(left, right)
    return _pow(left, right)


def _div(numerator: Rational, denominator: Rational) -> Rational:
    if denominator == 0:
        raise DomainError("division by zero")
    return numerator / denominator


def _mod(a: Rational, b: Rational) -> Rational:
    if a.denominator != 1 or b.denominator != 1:
        raise DomainError("mod requires integer arguments")
    if b.numerator == 0:
        raise DomainError("mod by zero")
    return Rational(a.numerator % b.numerator)


def _pow(base: Rational, exponent: Rational) -> Rational:
    if exponent.denominator != 1:
        raise DomainError("pow requires an integer exponent")
    n = exponent.numerator
    if base == 0 and n <= 0:
        raise DomainError("zero raised to a non-positive exponent")
    return base**n


def interpret(program: FreeProg) -> Rational:
    """Fold FreeProg with the calculator algebra F ℚ → ℚ."""
    if isinstance(program, FreeLit):
        return Rational(program.value)
    if isinstance(program, FreeBuiltin):
        return _alg_builtin(
            program.builtin,
            interpret(program.left),
            interpret(program.right),
        )
    args = tuple(interpret(a) for a in program.args)
    return _alg_op(program.op, args)


class Evaluator:
    """Realize ⟦Expr⟧ by reflecting into Free then interpreting with the algebra."""

    def evaluate(self, expr: Expr) -> Rational:
        return interpret(to_free(expr))


def main(argv: list[str] | None = None) -> int:
    """One-shot CLI: exactly one expression argv → print Fraction or error."""
    args = sys.argv if argv is None else argv
    if len(args) != 2:
        print(_USAGE, file=sys.stderr)
        return 2
    try:
        result = run(Parser(), Evaluator(), args[1])
    except (ParseError, DomainError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
