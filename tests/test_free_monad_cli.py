"""CLI for free_monad: one-shot argv → Fraction (bl-i7g.4.2)."""

from __future__ import annotations

import subprocess
import sys

import pytest

from beads_lab.free_monad import main

Capsys = pytest.CaptureFixture[str]


def test_main_prints_fraction_for_valid_expression(capsys: Capsys) -> None:
    code = main(["free_monad", "(pow 2 3)"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == "8"
    assert captured.err == ""


def test_main_missing_expression_is_usage_error(capsys: Capsys) -> None:
    code = main(["free_monad"])
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


def test_main_excess_args_is_usage_error(capsys: Capsys) -> None:
    code = main(["free_monad", "(+ 1 2)", "extra"])
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


def test_main_parse_error_to_stderr(capsys: Capsys) -> None:
    code = main(["free_monad", "(+ 1"])
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


def test_main_domain_error_to_stderr(capsys: Capsys) -> None:
    code = main(["free_monad", "(/ 1 0)"])
    captured = capsys.readouterr()
    assert code != 0
    assert captured.out == ""
    assert captured.err.strip() != ""


def test_module_cli_subprocess_prints_eight() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "beads_lab.free_monad", "(pow 2 3)"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "8"
    assert result.stderr == ""
