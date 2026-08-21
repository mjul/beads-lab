"""FR7 / composition law: stack and free evaluators agree on denotation.

For every successfully parsed source string ``s``:

    ⟦parse(s)⟧_stack  ≡  ⟦parse(s)⟧_free

(same ``Fraction`` on success, or both raise ``DomainError``).

Public surface only: ``Parser``, both ``Evaluator`` classes, and
``protocols.run``. No private stack/free internals.
"""

from __future__ import annotations

from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from beads_lab.free_monad import Evaluator as FreeEvaluator
from beads_lab.parser import Parser
from beads_lab.protocols import run
from beads_lab.stack_machine import Evaluator as StackEvaluator
from beads_lab.values import DomainError, ParseError

# Representative corpus: ops, builtins, nesting, and domain failures.
AGREEMENT_SOURCES = [
    # literals
    "42",
    "-7",
    "0",
    # nullary / identity ops
    "(+)",
    "(*)",
    # binary / n-ary arithmetic
    "(+ 1 2)",
    "(- 5)",
    "(- 10 3 1)",
    "(* 2 3 4)",
    "(/ 2)",
    "(/ 8 2 2)",
    # builtins
    "(mod 10 3)",
    "(mod -10 3)",
    "(mod 10 -3)",
    "(pow 2 3)",
    "(pow 2 -3)",
    "(pow -2 3)",
    "(pow 0 5)",
    # nested forms
    "(* 2 (+ 3 4))",
    "(+ 1 (* 2 3))",
    "(/ (+ 1 3) (- 5 1))",
    "(pow (+ 1 1) (* 2 2))",
    "(mod (* 3 4) (+ 1 2))",
    "(* (pow 2 3) (mod 10 3))",
    # domain-error representatives (must agree on DomainError class)
    "(/ 0)",
    "(/ 1 0)",
    "(/ 8 2 0)",
    "(mod 1 0)",
    "(pow 0 0)",
    "(pow 0 -1)",
    "(mod (/ 1 2) 2)",
    "(mod 2 (/ 1 2))",
    "(pow 2 (/ 1 2))",
]


@pytest.fixture
def parser() -> Parser:
    return Parser()


@pytest.fixture
def stack() -> StackEvaluator:
    return StackEvaluator()


@pytest.fixture
def free() -> FreeEvaluator:
    return FreeEvaluator()


def _denotation(
    evaluator: StackEvaluator | FreeEvaluator, source: str, parser: Parser
) -> Fraction | type[DomainError]:
    """Evaluate via public ``run``; return Fraction or DomainError class."""
    try:
        return run(parser, evaluator, source)
    except DomainError:
        return DomainError


@pytest.mark.parametrize("source", AGREEMENT_SOURCES)
def test_stack_and_free_agree_on_parsed_source(
    parser: Parser,
    stack: StackEvaluator,
    free: FreeEvaluator,
    source: str,
) -> None:
    """FR7: same success value or same domain-error class (parametrized corpus)."""
    # Must parse — corpus is well-formed by construction.
    parser.parse(source)

    stack_result = _denotation(stack, source, parser)
    free_result = _denotation(free, source, parser)
    assert stack_result == free_result


@pytest.mark.parametrize("source", AGREEMENT_SOURCES)
def test_evaluate_path_agrees_with_run(
    parser: Parser,
    stack: StackEvaluator,
    free: FreeEvaluator,
    source: str,
) -> None:
    """Agreement also holds when both call ``evaluate`` on the same Expr."""
    expr = parser.parse(source)

    def via_evaluate(
        ev: StackEvaluator | FreeEvaluator,
    ) -> Fraction | type[DomainError]:
        try:
            return ev.evaluate(expr)
        except DomainError:
            return DomainError

    expected = _denotation(stack, source, parser)
    assert via_evaluate(stack) == via_evaluate(free) == expected


def test_corpus_covers_ops_builtins_nesting_and_domain_errors(
    parser: Parser,
) -> None:
    """Sanity: corpus includes successes and DomainError cases (not only parses)."""
    stack = StackEvaluator()
    outcomes = {_denotation(stack, s, parser) for s in AGREEMENT_SOURCES}
    assert any(isinstance(o, Fraction) for o in outcomes)
    assert DomainError in outcomes


# --- Hypothesis: random well-formed Lisp-prefix sources ---

_OPS = ("+", "-", "*", "/")
_BUILTINS = ("mod", "pow")


def _format_app(head: str, args: list[str]) -> str:
    if not args:
        return f"({head})"
    return f"({head} {' '.join(args)})"


@st.composite
def well_formed_sources(draw: st.DrawFn) -> str:
    """Build nested Lisp-prefix strings that the shared Parser accepts."""

    def leaf() -> st.SearchStrategy[str]:
        return st.integers(min_value=-20, max_value=20).map(str)

    def extend(children: st.SearchStrategy[str]) -> st.SearchStrategy[str]:
        op_form = st.tuples(
            st.sampled_from(_OPS),
            st.lists(children, min_size=0, max_size=2),
        ).map(lambda pair: _format_app(pair[0], pair[1]))
        builtin_form = st.tuples(
            st.sampled_from(_BUILTINS),
            st.lists(children, min_size=2, max_size=2),
        ).map(lambda pair: _format_app(pair[0], pair[1]))
        return st.one_of(op_form, builtin_form)

    return draw(st.recursive(leaf(), extend, max_leaves=6))


@given(source=well_formed_sources())
@settings(max_examples=20, deadline=None)
def test_stack_and_free_agree_on_random_well_formed_sources(source: str) -> None:
    """Property: for every generated string that parses, denotations coincide."""
    parser = Parser()
    stack = StackEvaluator()
    free = FreeEvaluator()

    try:
        parser.parse(source)
    except ParseError:
        # Strategy should only emit well-formed input; treat as filter miss.
        return

    assert _denotation(stack, source, parser) == _denotation(free, source, parser)
