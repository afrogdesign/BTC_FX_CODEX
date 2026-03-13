#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

exec zsh "$BASE_DIR/tools/pull_ver021_prod_logs.sh" "$@"
