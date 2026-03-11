#!/usr/bin/env bash
set -euo pipefail

REMOTE="${1:-origin}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[ERROR] Missing required command: $1"
    exit 1
  fi
}

require_cmd git
require_cmd git-ai

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "[ERROR] Current directory is not a git repository."
  exit 1
fi

if [[ -f ".git/MERGE_HEAD" ]]; then
  echo "[ERROR] An unfinished merge was detected (.git/MERGE_HEAD exists)."
  exit 1
fi

if [[ -d ".git/rebase-apply" || -d ".git/rebase-merge" ]]; then
  echo "[ERROR] An unfinished rebase was detected."
  exit 1
fi

if [[ -n "$(git ls-files -u)" ]]; then
  echo "[ERROR] Unresolved conflicts detected in index."
  exit 1
fi

echo "[INFO] Ensuring git-ai local hooks..."
git-ai git-hooks ensure >/dev/null

echo "[INFO] Fetching remote branch and AI notes from ${REMOTE}..."
git fetch "${REMOTE}" --prune
git fetch "${REMOTE}" "refs/notes/ai:refs/notes/ai" >/dev/null 2>&1 || true

echo "[INFO] git-ai runtime status:"
git-ai status || true

echo "[OK] Preflight checks passed."
