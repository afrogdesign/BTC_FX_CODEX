#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$BASE_DIR/tmp"
SUCCESS_FILE="$TMP_DIR/prod_status_sync_last_success.txt"
ERROR_FILE="$TMP_DIR/prod_status_sync_last_error.txt"
PULL_LOG="$TMP_DIR/prod_status_sync_pull.log"
SUMMARY_LOG="$TMP_DIR/prod_status_sync_summary.log"

mkdir -p "$TMP_DIR"

cd "$BASE_DIR"

if ! zsh tools/pull_ver021_prod_logs_auto.sh --light >"$PULL_LOG" 2>&1; then
  printf '%s\n' "$(date '+%Y-%m-%d %H:%M JST') pull_failed" >"$ERROR_FILE"
  cp "$PULL_LOG" "$TMP_DIR/prod_status_sync_last_error.log"
  echo "status_sync_failed:$PULL_LOG"
  exit 1
fi

if ! .venv312/bin/python tools/build_prod_status_summary.py >"$SUMMARY_LOG" 2>&1; then
  printf '%s\n' "$(date '+%Y-%m-%d %H:%M JST') summary_failed" >"$ERROR_FILE"
  cp "$SUMMARY_LOG" "$TMP_DIR/prod_status_sync_last_error.log"
  echo "status_summary_failed:$SUMMARY_LOG"
  exit 1
fi

printf '%s\n' "$(date '+%Y-%m-%d %H:%M JST')" >"$SUCCESS_FILE"
rm -f "$ERROR_FILE" "$TMP_DIR/prod_status_sync_last_error.log"

echo "status_sync_done:$BASE_DIR/tmp/prod_status_summary.json"
