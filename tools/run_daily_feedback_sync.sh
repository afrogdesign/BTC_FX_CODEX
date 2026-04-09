#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$BASE_DIR/logs/runtime"

cd "$BASE_DIR"
exec "$BASE_DIR/.venv312/bin/python" tools/log_feedback.py daily-sync
