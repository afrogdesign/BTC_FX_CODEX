#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROD_HOST="${BTC_MONITOR_PROD_HOST:-mbp2020-btc}"
PROD_DIR="${BTC_MONITOR_PROD_DIR:-/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor}"
LOCAL_SNAPSHOT_DIR="${BTC_MONITOR_PROD_SNAPSHOT_DIR:-$BASE_DIR/tmp/snapshots/prod_ver021_snapshot}"
PROD_SSH_PASSWORD="${BTC_MONITOR_PROD_SSH_PASSWORD:-}"
LIGHT_MODE=0

ASKPASS_SCRIPT=""
RSYNC_SSH_CMD="ssh"

cleanup() {
  if [[ -n "$ASKPASS_SCRIPT" && -f "$ASKPASS_SCRIPT" ]]; then
    rm -f "$ASKPASS_SCRIPT"
  fi
}

if [[ -n "$PROD_SSH_PASSWORD" ]]; then
  ASKPASS_SCRIPT="$(mktemp "${TMPDIR:-/tmp}/btc_askpass.XXXXXX")"
  chmod 700 "$ASKPASS_SCRIPT"
  cat >"$ASKPASS_SCRIPT" <<'EOF'
#!/bin/sh
printf '%s\n' "${BTC_MONITOR_PROD_SSH_PASSWORD:-}"
EOF
  RSYNC_SSH_CMD="env SSH_ASKPASS=$ASKPASS_SCRIPT SSH_ASKPASS_REQUIRE=force DISPLAY=:0 ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password,keyboard-interactive -o IdentitiesOnly=yes -o IdentityAgent=none"
  trap cleanup EXIT
fi

usage() {
  cat <<'EOF'
使い方:
  zsh tools/pull_ver021_prod_logs.sh [--light]

概要:
  MBP2020 本番 Ver02.1 の確認に必要なログだけを、
  ローカルの tmp/snapshots/prod_ver021_snapshot/ へ取得します。

通常取得対象:
  logs/heartbeat.txt
  logs/last_result.json
  logs/csv/
  logs/signals/
  logs/cache/
  logs/runtime/monitor.pid

軽量取得対象（--light）:
  logs/heartbeat.txt
  logs/last_result.json
  logs/runtime/monitor.pid

任意設定（鍵認証で入れない場合の予備）:
  export BTC_MONITOR_PROD_SSH_PASSWORD='***'
  zsh tools/pull_ver021_prod_logs.sh

秘密情報ファイルから明示的に読みたい場合:
  zsh tools/pull_ver021_prod_logs_with_password.sh
EOF
}

for arg in "$@"; do
  case "$arg" in
    --light)
      LIGHT_MODE=1
      ;;
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
echo "light_mode:$LIGHT_MODE"

rsync -av -e "$RSYNC_SSH_CMD" \
  --delete \
  "$PROD_HOST":"$PROD_DIR/logs/heartbeat.txt" \
  "$PROD_HOST":"$PROD_DIR/logs/last_result.json" \
  "$LOCAL_SNAPSHOT_DIR"/

mkdir -p "$LOCAL_SNAPSHOT_DIR/runtime"
rsync -av -e "$RSYNC_SSH_CMD" --delete "$PROD_HOST":"$PROD_DIR/logs/runtime/monitor.pid" "$LOCAL_SNAPSHOT_DIR/runtime/" || true

if [[ "$LIGHT_MODE" -eq 1 ]]; then
  echo "pull_done:$LOCAL_SNAPSHOT_DIR"
  exit 0
fi

for subdir in csv signals cache runtime; do
  mkdir -p "$LOCAL_SNAPSHOT_DIR/$subdir"
done

rsync -av -e "$RSYNC_SSH_CMD" --delete "$PROD_HOST":"$PROD_DIR/logs/csv/" "$LOCAL_SNAPSHOT_DIR/csv/"
rsync -av -e "$RSYNC_SSH_CMD" --delete "$PROD_HOST":"$PROD_DIR/logs/signals/" "$LOCAL_SNAPSHOT_DIR/signals/"
rsync -av -e "$RSYNC_SSH_CMD" --delete "$PROD_HOST":"$PROD_DIR/logs/cache/" "$LOCAL_SNAPSHOT_DIR/cache/"

echo "pull_done:$LOCAL_SNAPSHOT_DIR"
