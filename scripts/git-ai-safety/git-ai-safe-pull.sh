#!/usr/bin/env bash
set -euo pipefail

REMOTE="${1:-origin}"
BRANCH="${2:-$(git rev-parse --abbrev-ref HEAD)}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -x "${SCRIPT_DIR}/git-ai-preflight.sh" ]]; then
  echo "[ERROR] Missing executable preflight script at ${SCRIPT_DIR}/git-ai-preflight.sh"
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "[ERROR] Working tree is not clean. Commit/stash changes before safe pull."
  exit 1
fi

"${SCRIPT_DIR}/git-ai-preflight.sh" "${REMOTE}"
"${SCRIPT_DIR}/git-ai-sync-notes.sh" "${REMOTE}" || true

echo "[INFO] Pulling ${REMOTE}/${BRANCH} with rebase..."
git pull --rebase --autostash "${REMOTE}" "${BRANCH}"

echo "[INFO] Re-ensuring git-ai hooks after pull..."
git-ai git-hooks ensure >/dev/null || true

echo "[OK] Safe pull completed."
