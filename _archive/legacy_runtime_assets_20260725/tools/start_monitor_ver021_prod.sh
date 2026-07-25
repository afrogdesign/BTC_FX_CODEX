#!/bin/zsh

set -eu

BASE_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
PLIST_SRC="$BASE_DIR/deploy/com.afrog.btc-monitor-ver021.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.afrog.btc-monitor-ver021.plist"
LABEL="com.afrog.btc-monitor-ver021"
OLD_PLIST_DEST="$HOME/Library/LaunchAgents/com.afrog.btc-monitor-ver02.plist"

mkdir -p "$BASE_DIR/logs/runtime"
mkdir -p "$HOME/Library/LaunchAgents"

cp "$PLIST_SRC" "$PLIST_DEST"
launchctl bootout "gui/$(id -u)" "$OLD_PLIST_DEST" >/dev/null 2>&1 || true
launchctl bootout "gui/$(id -u)" "$PLIST_DEST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST"
launchctl kickstart -k "gui/$(id -u)/$LABEL"
rm -f "$OLD_PLIST_DEST"

PID="$(launchctl print "gui/$(id -u)/$LABEL" | awk '/^\tpid = / {print $3; exit}')"
if [[ -n "$PID" ]]; then
  echo "$PID" > "$BASE_DIR/logs/runtime/monitor.pid"
fi

echo "launch_agent_started:$LABEL"
