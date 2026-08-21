"""Expression ADT: abstract syntax trees for the Lisp-prefix calculator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Op(Enum):
    """Arithmetic operators: +, -, *, /."""

    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"


class Builtin(Enum):
    """Built-in heads with fixed arity: mod, pow."""

    MOD = "mod"
    POW = "pow"


@dataclass(frozen=True, slots=True)
class Lit:
    """Integer literal node (ℤ)."""

    value: int


@dataclass(frozen=True, slots=True)
class App:
    """Application of an operator or builtin to zero or more subexpressions."""

    head: Op | Builtin
    args: tuple[Expr, ...]

    def __post_init__(self) -> None:
        if isinstance(self.head, Builtin) and len(self.args) != 2:
            name = self.head.value
            n = len(self.args)
            raise ValueError(f"{name} requires exactly 2 arguments, got {n}")


type Expr = Lit | App
