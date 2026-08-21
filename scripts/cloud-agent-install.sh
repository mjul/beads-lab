#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap: bd on PATH + project deps.
# Invoked from .cursor/environment.json "install".
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

export PATH="${HOME}/.local/bin:${PATH}"

# bd CLI + uv + beads-mcp + ~/.bashrc PATH (idempotent)
"${ROOT}/scripts/install-beads-mcp.sh"

# Persist ~/.local/bin for login shells (Cloud Agent / non-interactive)
ensure_local_bin_on_path() {
  local file="$1"
  mkdir -p "$(dirname "${file}")"
  touch "${file}"
  if ! grep -qE '(\$HOME|\$\{HOME\})/\.local/bin' "${file}" 2>/dev/null; then
    printf '\n# beads-lab: ensure bd (and uv tools) are on PATH\n' >> "${file}"
    printf 'export PATH="$HOME/.local/bin:$PATH"\n' >> "${file}"
  fi
}

ensure_local_bin_on_path "${HOME}/.bashrc"
ensure_local_bin_on_path "${HOME}/.profile"

if ! command -v bd >/dev/null 2>&1; then
  echo "error: bd CLI still missing on PATH after install" >&2
  echo "expected bd under \$HOME/.local/bin (PATH=${PATH})" >&2
  exit 1
fi

uv sync --group dev

echo "cloud-agent-install: $(bd version 2>/dev/null || bd --version)"
