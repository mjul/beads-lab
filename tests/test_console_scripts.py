"""Console script subprocess smoke tests (docs/console-scripts.md; workspace-fv5)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS: list[tuple[str, str]] = [
    ("beads-stack", "beads_lab.stack_machine"),
    ("beads-free", "beads_lab.free_monad"),
]


def _run_uv_script(script: str, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", script, *argv],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )


def _run_module(module: str, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module, *argv],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )


@pytest.mark.parametrize(("script", "module"), SCRIPTS)
def test_console_script_matches_module_evaluate_success(
    script: str,
    module: str,
) -> None:
    source = "(+ 1 2)"
    script_result = _run_uv_script(script, source)
    module_result = _run_module(module, source)
    assert script_result.returncode == 0
    assert module_result.returncode == 0
    assert script_result.stdout.strip() == "3"
    assert script_result.stdout == module_result.stdout
    assert script_result.stderr == ""


@pytest.mark.parametrize(("script", "module"), SCRIPTS)
def test_console_script_matches_module_usage_error(script: str, module: str) -> None:
    script_result = _run_uv_script(script)
    module_result = _run_module(module)
    assert script_result.returncode != 0
    assert module_result.returncode != 0
    assert script_result.stdout == ""
    assert module_result.stdout == ""
    assert script_result.stderr.strip() != ""
    assert module_result.stderr.strip() != ""


@pytest.mark.parametrize(("script", "module"), SCRIPTS)
def test_console_script_matches_module_parse_error(script: str, module: str) -> None:
    source = "(+ 1"
    script_result = _run_uv_script(script, source)
    module_result = _run_module(module, source)
    assert script_result.returncode != 0
    assert module_result.returncode != 0
    assert script_result.stdout == ""
    assert module_result.stdout == ""
    assert script_result.stderr.strip() != ""
    assert module_result.stderr.strip() != ""


@pytest.mark.parametrize(("script", "module"), SCRIPTS)
def test_console_script_matches_module_domain_error(script: str, module: str) -> None:
    source = "(/ 1 0)"
    script_result = _run_uv_script(script, source)
    module_result = _run_module(module, source)
    assert script_result.returncode != 0
    assert module_result.returncode != 0
    assert script_result.stdout == ""
    assert module_result.stdout == ""
    assert script_result.stderr.strip() != ""
    assert module_result.stderr.strip() != ""
