#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$BASE_DIR/deploy/com.afrog.btc-review-form.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.afrog.btc-review-form.plist"
LABEL="com.afrog.btc-review-form"

mkdir -p "$BASE_DIR/logs/runtime"
mkdir -p "$HOME/Library/LaunchAgents"

cp "$PLIST_SRC" "$PLIST_DEST"
launchctl bootout "gui/$(id -u)" "$PLIST_DEST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

echo "launch_agent_started:$LABEL"
