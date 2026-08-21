"""Shared evaluate-mode CLI driver (docs/cli-polish.md; workspace-gsn)."""

from __future__ import annotations

from pathlib import Path

import pytest

from beads_lab import cli
from beads_lab.expression import Expr
from beads_lab.free_monad import Evaluator as FreeEvaluator
from beads_lab.stack_machine import Evaluator as StackEvaluator
from beads_lab.values import Rational

Capsys = pytest.CaptureFixture[str]

_USAGE = "Usage: test-cli <expression>"


class _ExplodingEvaluator:
    """Fails the test if evaluate is invoked (show-expr must not evaluate)."""

    def evaluate(self, expr: Expr) -> Rational:
        raise AssertionError("evaluate must not be called in --show-expr mode")


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["prog", "--show-expr", "(+ 1 (* 2 3))"], "(+ 1 (* 2 3))"),
        (["prog", "(+ 1 (* 2 3))", "--show-expr"], "(+ 1 (* 2 3))"),
        (["prog", "--show-expr", "(  +  1  2 )"], "(+ 1 2)"),
        (["prog", "--show-expr", "(/ 1 0)"], "(/ 1 0)"),
    ],
)
def test_show_expr_prints_unparsed_expression(
    capsys: Capsys,
    argv: list[str],
    expected: str,
) -> None:
    code = cli.main(argv, evaluator=_ExplodingEvaluator(), usage=_USAGE)
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == expected
    assert captured.err == ""


@pytest.mark.parametrize(
    "argv",
    [
        ["prog", "--show-expr"],
        ["prog", "--foo", "(+ 1 2)"],
        ["prog", "(+ 1 2)", "--unknown"],
    ],
)
def test_show_expr_usage_errors(capsys: Capsys, argv: list[str]) -> None:
    code = cli.main(argv, evaluator=StackEvaluator(), usage=_USAGE)
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


@pytest.mark.parametrize("evaluator", [StackEvaluator(), FreeEvaluator()])
def test_show_expr_parse_error_to_stderr(
    capsys: Capsys,
    evaluator: StackEvaluator | FreeEvaluator,
) -> None:
    code = cli.main(["prog", "--show-expr", "(+ 1"], evaluator=evaluator, usage=_USAGE)
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


@pytest.mark.parametrize(
    ("evaluator", "source", "expected"),
    [
        (StackEvaluator(), "(+ 1 (* 2 3))", "7"),
        (FreeEvaluator(), "(pow 2 3)", "8"),
    ],
)
def test_main_prints_fraction_for_valid_expression(
    capsys: Capsys,
    evaluator: StackEvaluator | FreeEvaluator,
    source: str,
    expected: str,
) -> None:
    code = cli.main(["prog", source], evaluator=evaluator, usage=_USAGE)
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == expected
    assert captured.err == ""


@pytest.mark.parametrize("evaluator", [StackEvaluator(), FreeEvaluator()])
def test_main_missing_expression_is_usage_error(
    capsys: Capsys,
    evaluator: StackEvaluator | FreeEvaluator,
) -> None:
    code = cli.main(["prog"], evaluator=evaluator, usage=_USAGE)
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


@pytest.mark.parametrize("evaluator", [StackEvaluator(), FreeEvaluator()])
def test_main_excess_args_is_usage_error(
    capsys: Capsys,
    evaluator: StackEvaluator | FreeEvaluator,
) -> None:
    code = cli.main(["prog", "(+ 1 2)", "extra"], evaluator=evaluator, usage=_USAGE)
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


@pytest.mark.parametrize("evaluator", [StackEvaluator(), FreeEvaluator()])
def test_main_parse_error_to_stderr(
    capsys: Capsys,
    evaluator: StackEvaluator | FreeEvaluator,
) -> None:
    code = cli.main(["prog", "(+ 1"], evaluator=evaluator, usage=_USAGE)
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


@pytest.mark.parametrize("evaluator", [StackEvaluator(), FreeEvaluator()])
def test_main_domain_error_to_stderr(
    capsys: Capsys,
    evaluator: StackEvaluator | FreeEvaluator,
) -> None:
    code = cli.main(["prog", "(/ 1 0)"], evaluator=evaluator, usage=_USAGE)
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


def test_cli_source_does_not_import_evaluators() -> None:
    source = Path(__file__).resolve().parents[1] / "src" / "beads_lab" / "cli.py"
    text = source.read_text(encoding="utf-8")
    for forbidden in (
        "stack_machine",
        "free_monad",
        "beads_lab.stack_machine",
        "beads_lab.free_monad",
        "from .stack_machine",
        "from .free_monad",
    ):
        assert forbidden not in text
    assert "printer" in text
