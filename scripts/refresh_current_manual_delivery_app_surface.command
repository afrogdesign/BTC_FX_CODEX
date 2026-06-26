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

READY_GATE_JSON=$("$PYTHON" tools/log_feedback.py refresh-and-check-current-manual-delivery-app-surface --stdout-json)

SUMMARY_LINES=$(READY_GATE_JSON="$READY_GATE_JSON" "$PYTHON" - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["READY_GATE_JSON"])
required_keys = [
    "current_manual_delivery_app_ready",
    "readiness_status",
    "allowed_next_action",
    "human_review_required",
    "trade_execution_allowed",
    "automatic_order_allowed",
    "external_notification_allowed",
    "paper_positions_integration",
    "app_dashboard_html",
    "app_snapshot_json",
    "app_snapshot_status_json",
    "app_surface_manifest_json",
    "safety_boundary",
]
missing_keys = [key for key in required_keys if key not in data]
if missing_keys:
    print("missing ready gate keys: " + ", ".join(missing_keys), file=sys.stderr)
    raise SystemExit(1)


def as_bool(value: object) -> str:
    return "true" if bool(value) else "false"


print(f"manual_trade_ready={as_bool(data['current_manual_delivery_app_ready'])}")
print(f"readiness_status={data['readiness_status']}")
print(f"allowed_next_action={data['allowed_next_action']}")
print(f"human_review_required={as_bool(data['human_review_required'])}")
print(f"trade_execution_allowed={as_bool(data['trade_execution_allowed'])}")
print(f"automatic_order_allowed={as_bool(data['automatic_order_allowed'])}")
print(f"external_notification_allowed={as_bool(data['external_notification_allowed'])}")
print(f"paper_positions_integration={as_bool(data['paper_positions_integration'])}")
print(f"dashboard={data['app_dashboard_html']}")
print(f"snapshot={data['app_snapshot_json']}")
print(f"snapshot_status={data['app_snapshot_status_json']}")
print(f"manifest={data['app_surface_manifest_json']}")
print(f"safety_boundary={data['safety_boundary']}")
PY
)

printf '%s\n' "$READY_GATE_JSON"

printf '%s\n' 'local_app_surface_index=local/manual_delivery_app_surface/index.html'
printf '%s\n' 'local_app_surface_dashboard=local/manual_delivery_app_surface/app-dashboard.html'
printf '%s\n' 'local_app_surface_manifest=local/manual_delivery_app_surface/app-surface-manifest.json'
printf '%s\n' 'local_app_surface_note=Open index.html manually for human review only.'
printf '%s\n' "$SUMMARY_LINES"
