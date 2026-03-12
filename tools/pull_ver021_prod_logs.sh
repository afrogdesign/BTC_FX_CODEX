#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROD_HOST="${BTC_MONITOR_PROD_HOST:-marupro@192.168.1.38}"
PROD_DIR="${BTC_MONITOR_PROD_DIR:-/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor}"
LOCAL_SNAPSHOT_DIR="${BTC_MONITOR_PROD_SNAPSHOT_DIR:-$BASE_DIR/tmp/prod_ver021_snapshot}"

usage() {
  cat <<'EOF'
使い方:
  zsh tools/pull_ver021_prod_logs.sh

概要:
  MBP2020 本番 Ver02.1 の確認に必要なログだけを、
  ローカルの tmp/prod_ver021_snapshot/ へ取得します。

取得対象:
  logs/heartbeat.txt
  logs/last_result.json
  logs/csv/
  logs/signals/
  logs/cache/
  logs/runtime/monitor.pid
EOF
}

for arg in "$@"; do
  case "$arg" in
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done

mkdir -p "$LOCAL_SNAPSHOT_DIR"

echo "pull_source:$PROD_HOST:$PROD_DIR"
echo "snapshot_dir:$LOCAL_SNAPSHOT_DIR"

rsync -av \
  --delete \
  "$PROD_HOST":"$PROD_DIR/logs/heartbeat.txt" \
  "$PROD_HOST":"$PROD_DIR/logs/last_result.json" \
  "$LOCAL_SNAPSHOT_DIR"/

for subdir in csv signals cache runtime; do
  mkdir -p "$LOCAL_SNAPSHOT_DIR/$subdir"
done

rsync -av --delete "$PROD_HOST":"$PROD_DIR/logs/csv/" "$LOCAL_SNAPSHOT_DIR/csv/"
rsync -av --delete "$PROD_HOST":"$PROD_DIR/logs/signals/" "$LOCAL_SNAPSHOT_DIR/signals/"
rsync -av --delete "$PROD_HOST":"$PROD_DIR/logs/cache/" "$LOCAL_SNAPSHOT_DIR/cache/"
rsync -av --delete "$PROD_HOST":"$PROD_DIR/logs/runtime/monitor.pid" "$LOCAL_SNAPSHOT_DIR/runtime/" || true

echo "pull_done:$LOCAL_SNAPSHOT_DIR"
