#!/usr/bin/env bash
set -euo pipefail

# Run from repo root no matter where you call it
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

DATE=""        # optional: YYYY-MM-DD
FORCE=""       # optional: --force

for arg in "$@"; do
  case "$arg" in
    --force)
      FORCE="--force"
      ;;
    *)
      # treat the first non-flag as date
      if [[ -z "$DATE" ]]; then
        DATE="$arg"
      fi
      ;;
  esac
done

SNAPSHOT_CMD=(python3 backend/tools/make_history_snapshot.py)
if [[ -n "$DATE" ]]; then
  SNAPSHOT_CMD+=(--date "$DATE")
fi
if [[ "$FORCE" == "--force" ]]; then
  SNAPSHOT_CMD+=(--force)
fi

echo "==> ORA: generating history snapshot..."
"${SNAPSHOT_CMD[@]}"

echo "==> ORA: validating history snapshots..."
python3 backend/tools/validate_history.py

# Determine output filename (same logic as generator)
if [[ -n "$DATE" ]]; then
  FILE="backend/data/history/${DATE}.json"
else
  # Use UTC date for filename
  FILE="backend/data/history/$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
PY
).json"
fi

if [[ ! -f "$FILE" ]]; then
  echo "❌ Expected snapshot file not found: $FILE"
  exit 2
fi

echo "==> ORA: git status (pre-add)"
git status --porcelain || true

echo "==> ORA: staging snapshot + tools..."
git add "$FILE" backend/tools/make_history_snapshot.py backend/tools/validate_history.py backend/tools/snapshot_and_push.sh

# If nothing changed, don't create empty commit
if git diff --cached --quiet; then
  echo "ℹ️  No changes to commit (snapshot may be identical)."
  echo "✅ Done."
  exit 0
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"

MSG="Add history snapshot $(basename "$FILE" .json)"
echo "==> ORA: committing on branch '$BRANCH'..."
git commit -m "$MSG"

echo "==> ORA: pushing..."
git push

echo "✅ Snapshot committed + pushed: $FILE"

