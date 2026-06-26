#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCH_DIR="$HOME/Library/LaunchAgents"

mkdir -p "$BASE_DIR/logs/runtime"
mkdir -p "$LAUNCH_DIR"

for name in \
  com.afrog.btc-feedback-daily-sync \
  com.afrog.btc-ai-post-reviews
do
  src="$BASE_DIR/deploy/$name.plist"
  dest="$LAUNCH_DIR/$name.plist"
  cp "$src" "$dest"
  launchctl bootout "gui/$(id -u)" "$dest" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$dest"
done

launchctl kickstart -k "gui/$(id -u)/com.afrog.btc-feedback-daily-sync"

echo "launch_agents_started:com.afrog.btc-feedback-daily-sync,com.afrog.btc-ai-post-reviews"
