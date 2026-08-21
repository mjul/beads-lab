"""Acceptance: Cloud Agent install leaves bd on PATH without manual steps."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "cloud-agent-install.sh"
ENVIRONMENT_JSON = REPO_ROOT / ".cursor" / "environment.json"


def test_environment_json_runs_cloud_agent_install() -> None:
    """Cloud Agent bootstrap must invoke the repo install script."""
    config = json.loads(ENVIRONMENT_JSON.read_text(encoding="utf-8"))
    assert "$schema" not in config
    assert config["name"] == "beads-lab"
    assert "cloud-agent-install" in config["install"]


def test_install_script_declares_bd_path_and_project_sync() -> None:
    """Install must persist ~/.local/bin, install bd if needed, and sync deps."""
    text = INSTALL_SCRIPT.read_text(encoding="utf-8")
    assert INSTALL_SCRIPT.stat().st_mode & 0o111, "install script must be executable"
    assert ".local/bin" in text
    assert ".bashrc" in text
    assert ".profile" in text
    assert "gastownhall/beads" in text or "install-beads-mcp.sh" in text
    assert "uv sync" in text
    assert "bd version" in text or "bd --version" in text


def test_running_install_leaves_bd_invokable() -> None:
    """Running the install script must leave `bd version` succeeding on PATH."""
    env = os.environ.copy()
    # Simulate a fresh agent shell that has not yet inherited a custom PATH.
    path_parts = [
        p for p in env.get("PATH", "").split(os.pathsep) if p and ".local/bin" not in p
    ]
    env["PATH"] = os.pathsep.join(path_parts)

    subprocess.run(
        [str(INSTALL_SCRIPT)],
        cwd=REPO_ROOT,
        check=True,
        env=env,
        timeout=300,
    )

    # Login/profile-style PATH: ~/.local/bin first, as Cloud Agent shells should see.
    env["PATH"] = f"{Path.home() / '.local' / 'bin'}{os.pathsep}{env['PATH']}"
    result = subprocess.run(
        ["bd", "version"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert result.stdout.strip() or result.stderr.strip()
