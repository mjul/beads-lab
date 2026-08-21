#!/usr/bin/env bash
# Run gitleaks with beads-lab custom rules (Cloud Agent token patterns).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT}/.gitleaks.toml"
GITLEAKS_VERSION="${GITLEAKS_VERSION:-8.24.2}"
INSTALL_DIR="${HOME}/.local/bin"

usage() {
  cat <<'EOF'
Usage: scripts/gitleaks.sh <command>

Commands:
  protect   Scan staged changes (pre-commit). Exits non-zero on findings.
  audit     Scan full git history. Exits non-zero on findings.
  install   Download gitleaks to ~/.local/bin if missing.

Environment:
  GITLEAKS_VERSION   Release to install (default: 8.24.2)
EOF
}

ensure_gitleaks() {
  if command -v gitleaks >/dev/null 2>&1; then
    return 0
  fi
  if [ -x "${INSTALL_DIR}/gitleaks" ]; then
    export PATH="${INSTALL_DIR}:${PATH}"
    return 0
  fi
  echo "gitleaks not found; run: scripts/gitleaks.sh install" >&2
  return 1
}

install_gitleaks() {
  local archive="gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
  local url="https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/${archive}"
  local tmp
  tmp="$(mktemp -d)"

  curl -fsSL "${url}" -o "${tmp}/${archive}"
  tar -xzf "${tmp}/${archive}" -C "${tmp}"
  mkdir -p "${INSTALL_DIR}"
  install -m 0755 "${tmp}/gitleaks" "${INSTALL_DIR}/gitleaks"
  rm -rf "${tmp}"
  export PATH="${INSTALL_DIR}:${PATH}"
  echo "installed gitleaks $(gitleaks version) to ${INSTALL_DIR}/gitleaks"
}

cmd="${1:-}"
case "${cmd}" in
  install)
    install_gitleaks
    ;;
  protect)
    ensure_gitleaks
    gitleaks protect --staged --source "${ROOT}" --config "${CONFIG}" --redact
    ;;
  audit)
    ensure_gitleaks
    gitleaks detect --source "${ROOT}" --config "${CONFIG}" --redact -v
    ;;
  -h | --help | help)
    usage
    ;;
  *)
    echo "error: unknown command: ${cmd:-}" >&2
    usage >&2
    exit 2
    ;;
esac
