"""Shared Lisp-prefix parser: string → Expr (sole implementation for both CLIs)."""

from __future__ import annotations

from beads_lab.expression import App, Builtin, Expr, Lit, Op
from beads_lab.values import ParseError

_OPS: dict[str, Op] = {op.value: op for op in Op}
_BUILTINS: dict[str, Builtin] = {b.value: b for b in Builtin}


class Parser:
    """Maps a Lisp-prefix source string to an Expr AST."""

    def parse(self, source: str) -> Expr:
        tokens = _tokenize(source)
        if not tokens:
            raise ParseError("empty input")
        expr, index = _parse_expr(tokens, 0)
        if index != len(tokens):
            raise ParseError(f"trailing input after expression: {tokens[index]!r}")
        return expr


def _tokenize(source: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            tokens.append(ch)
            i += 1
            continue
        start = i
        while i < n and not source[i].isspace() and source[i] not in "()":
            i += 1
        tokens.append(source[start:i])
    return tokens


def _parse_expr(tokens: list[str], index: int) -> tuple[Expr, int]:
    if index >= len(tokens):
        raise ParseError("truncated input")
    tok = tokens[index]
    if tok == "(":
        return _parse_form(tokens, index + 1)
    if tok == ")":
        raise ParseError("unexpected ')'")
    return Lit(_parse_int_atom(tok)), index + 1


def _parse_form(tokens: list[str], index: int) -> tuple[Expr, int]:
    if index >= len(tokens):
        raise ParseError("truncated input: expected head after '('")
    head_tok = tokens[index]
    if head_tok in "()":
        raise ParseError(f"expected operator or builtin head, got {head_tok!r}")
    head = _resolve_head(head_tok)
    index += 1
    args: list[Expr] = []
    while index < len(tokens) and tokens[index] != ")":
        arg, index = _parse_expr(tokens, index)
        args.append(arg)
    if index >= len(tokens):
        raise ParseError("truncated input: missing ')'")
    index += 1  # consume ')'
    try:
        return App(head, tuple(args)), index
    except ValueError as exc:
        raise ParseError(str(exc)) from exc


def _resolve_head(tok: str) -> Op | Builtin:
    if tok in _OPS:
        return _OPS[tok]
    if tok in _BUILTINS:
        return _BUILTINS[tok]
    raise ParseError(f"unknown head: {tok!r}")


def _parse_int_atom(tok: str) -> int:
    if tok == "-" or not _is_integer_literal(tok):
        raise ParseError(f"expected integer literal, got {tok!r}")
    return int(tok)


def _is_integer_literal(tok: str) -> bool:
    if not tok:
        return False
    body = tok[1:] if tok[0] == "-" else tok
    return bool(body) and body.isdigit()
