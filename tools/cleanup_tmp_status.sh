#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$BASE_DIR/tmp"

mkdir -p "$TMP_DIR/status" "$TMP_DIR/snapshots" "$TMP_DIR/errors"

rm -f "$TMP_DIR/.DS_Store" "$TMP_DIR/prod_ver021_snapshot.tgz"
rm -rf "$TMP_DIR/prod_ver02_snapshot"

if [[ -f "$TMP_DIR/prod_status_summary.json" ]]; then
  mv "$TMP_DIR/prod_status_summary.json" "$TMP_DIR/status/prod_status_summary.json"
fi
if [[ -f "$TMP_DIR/prod_status_summary.md" ]]; then
  mv "$TMP_DIR/prod_status_summary.md" "$TMP_DIR/status/prod_status_summary.md"
fi
if [[ -f "$TMP_DIR/prod_status_sync_last_success.txt" ]]; then
  mv "$TMP_DIR/prod_status_sync_last_success.txt" "$TMP_DIR/status/prod_status_sync_last_success.txt"
fi
if [[ -f "$TMP_DIR/prod_status_sync_last_error.txt" ]]; then
  mv "$TMP_DIR/prod_status_sync_last_error.txt" "$TMP_DIR/errors/prod_status_sync_last_error.txt"
fi
if [[ -f "$TMP_DIR/prod_status_sync_last_error.log" ]]; then
  mv "$TMP_DIR/prod_status_sync_last_error.log" "$TMP_DIR/errors/prod_status_sync_last_error.log"
fi
if [[ -f "$TMP_DIR/prod_status_sync_pull.log" ]]; then
  mv "$TMP_DIR/prod_status_sync_pull.log" "$TMP_DIR/errors/prod_status_sync_pull.log"
fi
if [[ -f "$TMP_DIR/prod_status_sync_summary.log" ]]; then
  mv "$TMP_DIR/prod_status_sync_summary.log" "$TMP_DIR/errors/prod_status_sync_summary.log"
fi
if [[ -d "$TMP_DIR/prod_ver021_snapshot" ]]; then
  rm -rf "$TMP_DIR/snapshots/prod_ver021_snapshot"
  mv "$TMP_DIR/prod_ver021_snapshot" "$TMP_DIR/snapshots/prod_ver021_snapshot"
fi
if [[ -d "$TMP_DIR/prod_ver021_snapshot_live" ]]; then
  rm -rf "$TMP_DIR/snapshots/prod_ver021_snapshot_live"
  mv "$TMP_DIR/prod_ver021_snapshot_live" "$TMP_DIR/snapshots/prod_ver021_snapshot_live"
fi

find "$TMP_DIR" -maxdepth 1 -type f | sed 's#^#leftover_file:#'
echo "cleanup_done:$TMP_DIR"
