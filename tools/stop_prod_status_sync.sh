#!/bin/zsh

set -eu

LABEL="com.afrog.btc-monitor-status-sync"
GUI_DOMAIN="gui/$(id -u)"

launchctl bootout "$GUI_DOMAIN/$LABEL"
