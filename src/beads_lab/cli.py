"""Shared one-shot CLI driver: argv + injected Evaluator → exit code."""

from __future__ import annotations

import sys

from beads_lab.parser import Parser
from beads_lab.printer import unparse
from beads_lab.protocols import Evaluator, run
from beads_lab.values import DomainError, ParseError


def _parse_argv(argv: list[str]) -> tuple[str, bool] | None:
    """Return (expression, show_expr) or None on usage error."""
    show_expr = False
    expressions: list[str] = []
    for arg in argv[1:]:
        if arg == "--show-expr":
            show_expr = True
        elif arg.startswith("-"):
            return None
        else:
            expressions.append(arg)
    if len(expressions) != 1:
        return None
    return expressions[0], show_expr


def main(
    argv: list[str] | None,
    *,
    evaluator: Evaluator,
    usage: str,
) -> int:
    """Evaluate or show-expr mode: one expression argv → print result or error."""
    args = sys.argv if argv is None else argv
    parsed = _parse_argv(args)
    if parsed is None:
        print(usage, file=sys.stderr)
        return 2
    source, show_expr = parsed
    parser = Parser()
    if show_expr:
        try:
            expr = parser.parse(source)
        except ParseError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(unparse(expr))
        return 0
    try:
        result = run(parser, evaluator, source)
    except (ParseError, DomainError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(result)
    return 0
