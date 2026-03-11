#!/usr/bin/env bash
set -euo pipefail

REMOTE="${1:-origin}"
NOTES_REF="refs/notes/ai"
TMP_REF="refs/notes/ai-remote-tmp"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "[ERROR] Current directory is not a git repository."
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "[ERROR] git is required."
  exit 1
fi

echo "[INFO] Syncing ${NOTES_REF} from remote ${REMOTE}..."

if ! git ls-remote --exit-code "${REMOTE}" "${NOTES_REF}" >/dev/null 2>&1; then
  echo "[INFO] Remote has no ${NOTES_REF}. Nothing to sync."
  exit 0
fi

if git fetch "${REMOTE}" "${NOTES_REF}:${NOTES_REF}" >/dev/null 2>&1; then
  echo "[OK] ${NOTES_REF} synced (fast-forward/no-change)."
  exit 0
fi

echo "[WARN] Direct sync failed (likely divergence). Fetching remote notes to ${TMP_REF}."
git fetch "${REMOTE}" "${NOTES_REF}:${TMP_REF}" >/dev/null

echo "[WARN] Local and remote AI notes diverged."
echo "       Remote notes were fetched to: ${TMP_REF}"
echo "       You can inspect with:"
echo "         git log ${NOTES_REF} --oneline -n 5"
echo "         git log ${TMP_REF} --oneline -n 5"
echo "       Then resolve manually (e.g. git notes merge) before pushing."
exit 2
