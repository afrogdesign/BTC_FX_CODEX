#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$BASE_DIR/deploy/com.afrog.btc-monitor.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.afrog.btc-monitor.plist"
LABEL="com.afrog.btc-monitor"

# 実行ログの出力先と LaunchAgents 配置先を事前に作成
mkdir -p "$BASE_DIR/logs/runtime"
mkdir -p "$HOME/Library/LaunchAgents"

# launchd の定義ファイルを更新し、古いジョブを外してから再登録
cp "$PLIST_SRC" "$PLIST_DEST"
launchctl bootout "gui/$(id -u)" "$PLIST_DEST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

# launchd が割り当てた実PIDを保存して、運用確認をしやすくする
PID="$(launchctl print "gui/$(id -u)/$LABEL" | awk '/^\tpid = / {print $3; exit}')"
if [[ -n "$PID" ]]; then
  echo "$PID" > "$BASE_DIR/logs/runtime/monitor.pid"
fi

echo "launch_agent_started:$LABEL"
