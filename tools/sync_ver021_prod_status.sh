#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$BASE_DIR"
zsh tools/pull_ver021_prod_logs_auto.sh --light
.venv312/bin/python tools/build_prod_status_summary.py

echo "status_sync_done:$BASE_DIR/tmp/prod_status_summary.json"
