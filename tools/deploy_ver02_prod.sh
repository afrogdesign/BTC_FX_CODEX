#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROD_HOST="${BTC_MONITOR_PROD_HOST:-marupro@192.168.1.38}"
PROD_DIR="${BTC_MONITOR_PROD_DIR:-/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor}"
PROD_LABEL="${BTC_MONITOR_PROD_LABEL:-com.afrog.btc-monitor-ver02}"
RESTART_AFTER_DEPLOY=1

usage() {
  cat <<'EOF'
使い方:
  zsh tools/deploy_ver02_prod.sh [--no-restart]

概要:
  Git 管理下のコードだけを MBP2020 本番 Ver02 へ rsync で反映します。
  logs/ や .env、仮想環境は本番側のまま残します。

環境変数で上書きできる値:
  BTC_MONITOR_PROD_HOST   接続先ホスト
  BTC_MONITOR_PROD_DIR    本番配置先ディレクトリ
  BTC_MONITOR_PROD_LABEL  launchd ラベル
EOF
}

for arg in "$@"; do
  case "$arg" in
    --no-restart)
      RESTART_AFTER_DEPLOY=0
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

if ! git -C "$BASE_DIR" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "git repository not found: $BASE_DIR" >&2
  exit 1
fi

TMP_FILES="$(mktemp)"
trap 'rm -f "$TMP_FILES"' EXIT

git -C "$BASE_DIR" ls-files > "$TMP_FILES"

echo "deploy_target:$PROD_HOST:$PROD_DIR"
echo "sync_mode:git-tracked-files"

ssh "$PROD_HOST" "mkdir -p '$PROD_DIR'"
rsync -av --files-from="$TMP_FILES" "$BASE_DIR"/ "$PROD_HOST":"$PROD_DIR"/

if [[ "$RESTART_AFTER_DEPLOY" -eq 1 ]]; then
  ssh "$PROD_HOST" "cd '$PROD_DIR' && zsh tools/start_monitor_ver02_prod.sh '$PROD_DIR' && launchctl print gui/\$(id -u)/$PROD_LABEL | grep -E 'state =|pid ='"
else
  echo "restart_skipped:1"
fi

echo "deploy_done:$PROD_LABEL"
