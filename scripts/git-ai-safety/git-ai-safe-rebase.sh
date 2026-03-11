#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <base-ref> [remote]"
  echo "Example: $0 origin/main origin"
  exit 1
fi

BASE_REF="$1"
REMOTE="${2:-origin}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
BACKUP_BRANCH="backup/${CURRENT_BRANCH}-$(date +%Y%m%d%H%M%S)"

"${SCRIPT_DIR}/git-ai-preflight.sh" "${REMOTE}"
"${SCRIPT_DIR}/git-ai-sync-notes.sh" "${REMOTE}" || true

echo "[INFO] Creating backup branch: ${BACKUP_BRANCH}"
git branch "${BACKUP_BRANCH}"

echo "[INFO] Rebasing ${CURRENT_BRANCH} onto ${BASE_REF}..."
if ! git rebase "${BASE_REF}"; then
  echo "[WARN] Rebase failed with conflicts."
  echo "       Resolve conflicts, then run: git rebase --continue"
  echo "       Or abort with:              git rebase --abort"
  echo "       Backup branch created at:   ${BACKUP_BRANCH}"
  exit 2
fi

echo "[INFO] Re-ensuring git-ai hooks after rebase..."
git-ai git-hooks ensure >/dev/null || true

echo "[OK] Safe rebase completed."
echo "[INFO] If everything looks good, you can delete backup branch:"
echo "       git branch -D ${BACKUP_BRANCH}"
