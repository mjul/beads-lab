"""Shared one-shot CLI driver: argv + injected Evaluator → exit code."""

from __future__ import annotations

import sys

from beads_lab.parser import Parser
from beads_lab.protocols import Evaluator, run
from beads_lab.values import DomainError, ParseError


def main(
    argv: list[str] | None,
    *,
    evaluator: Evaluator,
    usage: str,
) -> int:
    """Evaluate mode: exactly one expression argv → print Fraction or error."""
    args = sys.argv if argv is None else argv
    if len(args) != 2:
        print(usage, file=sys.stderr)
        return 2
    try:
        result = run(Parser(), evaluator, args[1])
    except (ParseError, DomainError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(result)
    return 0
