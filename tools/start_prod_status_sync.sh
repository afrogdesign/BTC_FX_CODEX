#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_NAME="com.afrog.btc-monitor-status-sync.plist"
PLIST_SRC="$BASE_DIR/deploy/$PLIST_NAME"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME"
LABEL="com.afrog.btc-monitor-status-sync"
GUI_DOMAIN="gui/$(id -u)"

mkdir -p "$HOME/Library/LaunchAgents" "$BASE_DIR/logs/runtime"
cp "$PLIST_SRC" "$PLIST_DST"

launchctl bootout "$GUI_DOMAIN/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "$GUI_DOMAIN" "$PLIST_DST"
launchctl kickstart -k "$GUI_DOMAIN/$LABEL"
launchctl print "$GUI_DOMAIN/$LABEL" | sed -n '1,40p'
