#!/usr/bin/env bash
set -euo pipefail

REMOTE="${1:-origin}"
BRANCH="${2:-$(git rev-parse --abbrev-ref HEAD)}"
NOTES_REF="refs/notes/ai"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/git-ai-preflight.sh" "${REMOTE}"
"${SCRIPT_DIR}/git-ai-sync-notes.sh" "${REMOTE}" || true

echo "[INFO] Pushing branch ${BRANCH} to ${REMOTE}..."
git push "${REMOTE}" "${BRANCH}"

if git show-ref --verify --quiet "${NOTES_REF}"; then
  echo "[INFO] Pushing AI notes ${NOTES_REF} to ${REMOTE}..."
  if ! git push "${REMOTE}" "${NOTES_REF}:${NOTES_REF}"; then
    echo "[WARN] Failed to push ${NOTES_REF} (likely divergence)."
    echo "       Run ${SCRIPT_DIR}/git-ai-sync-notes.sh ${REMOTE}, resolve notes divergence, then retry."
    exit 2
  fi
else
  echo "[INFO] No local ${NOTES_REF} found. Skipping notes push."
fi

echo "[OK] Safe push completed."
