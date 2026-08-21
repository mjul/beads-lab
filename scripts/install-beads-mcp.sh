#!/usr/bin/env bash
# Idempotent installer for bd CLI + beads-mcp (Cursor workspace MCP).
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

if ! command -v bd >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/gastownhall/beads/main/scripts/install.sh | bash || true
  export PATH="${HOME}/.local/bin:${PATH}"
fi

if ! command -v bd >/dev/null 2>&1; then
  echo "error: bd CLI not found on PATH after install" >&2
  exit 1
fi

uv tool install --quiet beads-mcp

# Ensure shells and Cursor MCP launches see ~/.local/bin
mkdir -p "${HOME}/.local/bin"
if ! grep -qE '(\$HOME|\$\{HOME\})/\.local/bin' "${HOME}/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.bashrc"
fi

echo "bd: $(bd version 2>/dev/null || bd --version)"
echo "beads-mcp: $(command -v beads-mcp)"
echo "uvx beads-mcp ready"
