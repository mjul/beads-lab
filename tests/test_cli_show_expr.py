"""E2E --show-expr coverage for stack_machine and free_monad entry points."""

from __future__ import annotations

import subprocess
import sys

import pytest

MODULES = ("beads_lab.stack_machine", "beads_lab.free_monad")

SHOW_EXPR_CASES: list[tuple[str, str]] = [
    ("(+ 1 (* 2 3))", "(+ 1 (* 2 3))"),
    ("(  +  1  2 )", "(+ 1 2)"),
    ("(pow 2 3)", "(pow 2 3)"),
    ("(/ 1 0)", "(/ 1 0)"),
]


def _run_module(module: str, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module, *argv],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("module", MODULES)
@pytest.mark.parametrize(("source", "expected"), SHOW_EXPR_CASES)
def test_show_expr_prints_canonical_unparse(
    module: str,
    source: str,
    expected: str,
) -> None:
    result = _run_module(module, "--show-expr", source)
    assert result.returncode == 0
    assert result.stdout.strip() == expected
    assert result.stderr == ""


@pytest.mark.parametrize("module", MODULES)
def test_show_expr_flag_may_follow_expression(module: str) -> None:
    result = _run_module(module, "(+ 1 2)", "--show-expr")
    assert result.returncode == 0
    assert result.stdout.strip() == "(+ 1 2)"
    assert result.stderr == ""


@pytest.mark.parametrize("module", MODULES)
def test_show_expr_domain_error_source_does_not_evaluate(module: str) -> None:
    show = _run_module(module, "--show-expr", "(/ 1 0)")
    evaluate = _run_module(module, "(/ 1 0)")
    assert show.returncode == 0
    assert show.stdout.strip() == "(/ 1 0)"
    assert show.stderr == ""
    assert evaluate.returncode != 0
    assert evaluate.stdout == ""
    assert evaluate.stderr.strip() != ""


@pytest.mark.parametrize("module", MODULES)
def test_default_evaluate_mode_unchanged(module: str) -> None:
    result = _run_module(module, "(+ 1 2)")
    assert result.returncode == 0
    assert result.stdout.strip() == "3"
    assert result.stderr == ""
