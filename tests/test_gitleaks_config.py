"""Acceptance: gitleaks config flags Cloud Agent GitHub token patterns."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / ".gitleaks.toml"
GITLEAKS_SCRIPT = REPO_ROOT / "scripts" / "gitleaks.sh"

# Synthetic JWT-shaped fixture (not a real credential).
FAKE_GHS_TOKEN = (
    "ghs_123456_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJ0ZXN0In0."
    "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
)
FAKE_CREDENTIAL_URL = f"x-access-token:{FAKE_GHS_TOKEN}@github.com/example/repo"


def test_gitleaks_config_declares_cloud_agent_rules() -> None:
    data = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    assert data["extend"]["useDefault"] is True
    rule_ids = {rule["id"] for rule in data["rules"]}
    assert rule_ids == {
        "github-credential-url-x-access-token",
        "github-app-installation-token-jwt",
    }


def test_gitleaks_detects_synthetic_cloud_agent_patterns(tmp_path: Path) -> None:
    """Custom rules must flag JWT-shaped ghs_ tokens and x-access-token URLs."""
    subprocess.run(
        [str(GITLEAKS_SCRIPT), "install"],
        cwd=REPO_ROOT,
        check=True,
        timeout=120,
    )

    fixture = tmp_path / "fixture.txt"
    fixture.write_text(
        f"sync.remote: git+https://{FAKE_CREDENTIAL_URL}\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "gitleaks",
            "detect",
            "--no-git",
            "--source",
            str(tmp_path),
            "--config",
            str(CONFIG),
            "-v",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0, result.stdout + result.stderr
    combined = result.stdout + result.stderr
    assert "github-app-installation-token-jwt" in combined
    assert "github-credential-url-x-access-token" in combined
