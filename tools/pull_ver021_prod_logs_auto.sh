#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SECRET_FILE="${BTC_MONITOR_SECRET_FILE:-/Users/marupro/CODEX/Global_BOX/10_共通仕様/秘密情報管理.md}"

if [[ -z "${BTC_MONITOR_PROD_SSH_PASSWORD:-}" && -r "$SECRET_FILE" ]]; then
  pw="$(awk -F'`' '/SSH パスワード/{print $2; exit}' "$SECRET_FILE")"
  if [[ -n "$pw" ]]; then
    export BTC_MONITOR_PROD_SSH_PASSWORD="$pw"
  fi
fi

if [[ -z "${BTC_MONITOR_PROD_SSH_PASSWORD:-}" ]]; then
  echo "error: BTC_MONITOR_PROD_SSH_PASSWORD が未設定です。" >&2
  echo "hint: 秘密情報管理.md から読み取れない場合は環境変数で指定してください。" >&2
  exit 1
fi

exec zsh "$BASE_DIR/tools/pull_ver021_prod_logs.sh" "$@"
