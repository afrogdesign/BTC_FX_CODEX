#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$BASE_DIR/tmp"
STATUS_DIR="$TMP_DIR/status"
ERROR_DIR="$TMP_DIR/errors"
SUCCESS_FILE="$STATUS_DIR/prod_status_sync_last_success.txt"
ERROR_FILE="$ERROR_DIR/prod_status_sync_last_error.txt"
PULL_LOG="$ERROR_DIR/prod_status_sync_pull.log"
SUMMARY_LOG="$ERROR_DIR/prod_status_sync_summary.log"
OUTPUT_JSON="$STATUS_DIR/prod_status_summary.json"
SUMMARY_PYTHON="$BASE_DIR/.venv312/bin/python"

mkdir -p "$STATUS_DIR" "$ERROR_DIR" "$TMP_DIR/snapshots"

cd "$BASE_DIR"

if [[ ! -x "$SUMMARY_PYTHON" ]]; then
  SUMMARY_PYTHON="${PYTHON_BIN:-python3}"
fi

if ! zsh tools/pull_ver021_prod_logs_auto.sh --light >"$PULL_LOG" 2>&1; then
  printf '%s\n' "$(date '+%Y-%m-%d %H:%M JST') pull_failed" >"$ERROR_FILE"
  cp "$PULL_LOG" "$ERROR_DIR/prod_status_sync_last_error.log"
  echo "status_sync_failed:$PULL_LOG"
  exit 1
fi

if ! "$SUMMARY_PYTHON" tools/build_prod_status_summary.py >"$SUMMARY_LOG" 2>&1; then
  printf '%s\n' "$(date '+%Y-%m-%d %H:%M JST') summary_failed" >"$ERROR_FILE"
  cp "$SUMMARY_LOG" "$ERROR_DIR/prod_status_sync_last_error.log"
  echo "status_summary_failed:$SUMMARY_LOG"
  exit 1
fi

printf '%s\n' "$(date '+%Y-%m-%d %H:%M JST')" >"$SUCCESS_FILE"
rm -f "$ERROR_FILE" "$ERROR_DIR/prod_status_sync_last_error.log" "$PULL_LOG" "$SUMMARY_LOG"

echo "status_sync_done:$OUTPUT_JSON"
