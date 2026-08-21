"""Stack-machine evaluator: post-order walk of Expr → Fraction."""

from __future__ import annotations

from beads_lab.expression import Builtin, Expr, Lit, Op
from beads_lab.values import DomainError, Rational


class Evaluator:
    """Realize ⟦Expr⟧ with a stack of rationals (post-order / postfix apply)."""

    def evaluate(self, expr: Expr) -> Rational:
        stack: list[Rational] = []
        self._eval(expr, stack)
        return stack[-1]

    def _eval(self, expr: Expr, stack: list[Rational]) -> None:
        if isinstance(expr, Lit):
            stack.append(Rational(expr.value))
            return
        for arg in expr.args:
            self._eval(arg, stack)
        n = len(expr.args)
        args = [stack.pop() for _ in range(n)]
        args.reverse()
        stack.append(self._apply(expr.head, args))

    def _apply(self, head: Op | Builtin, args: list[Rational]) -> Rational:
        if isinstance(head, Builtin):
            return self._apply_builtin(head, args)
        return self._apply_op(head, args)

    def _apply_op(self, op: Op, args: list[Rational]) -> Rational:
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
            return self._div(Rational(1), args[0])
        result = args[0]
        for a in args[1:]:
            result = self._div(result, a)
        return result

    def _apply_builtin(self, builtin: Builtin, args: list[Rational]) -> Rational:
        # App construction already enforces arity 2 for builtins.
        a, b = args
        if builtin is Builtin.MOD:
            return self._mod(a, b)
        return self._pow(a, b)

    def _div(self, numerator: Rational, denominator: Rational) -> Rational:
        if denominator == 0:
            raise DomainError("division by zero")
        return numerator / denominator

    def _mod(self, a: Rational, b: Rational) -> Rational:
        if a.denominator != 1 or b.denominator != 1:
            raise DomainError("mod requires integer arguments")
        if b.numerator == 0:
            raise DomainError("mod by zero")
        return Rational(a.numerator % b.numerator)

    def _pow(self, base: Rational, exponent: Rational) -> Rational:
        if exponent.denominator != 1:
            raise DomainError("pow requires an integer exponent")
        n = exponent.numerator
        if base == 0 and n <= 0:
            raise DomainError("zero raised to a non-positive exponent")
        return base**n
