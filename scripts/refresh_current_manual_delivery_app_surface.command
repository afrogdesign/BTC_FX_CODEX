#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

if [ -x "./.venv312/bin/python" ]; then
    PYTHON="./.venv312/bin/python"
else
    PYTHON="python3"
fi

"$PYTHON" tools/log_feedback.py refresh-and-check-current-manual-delivery-app-surface --stdout-json

printf '%s\n' 'local_app_surface_index=local/manual_delivery_app_surface/index.html'
printf '%s\n' 'local_app_surface_manifest=local/manual_delivery_app_surface/app-surface-manifest.json'
printf '%s\n' 'local_app_surface_note=Open index.html manually for human review only.'
