#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import MASKED_KEYS, REQUIRED_KEYS


ACCEPTED_PREFIXES = [
    "MEXC_",
    "OPENAI_",
    "BINANCE_",
    "NOTIFICATION_HTML_",
]


def build_audit_data() -> dict[str, Any]:
    return {
        "schema_version": "safe_config_schema_audit.v1",
        "required_keys": list(REQUIRED_KEYS),
        "masked_keys": sorted(MASKED_KEYS),
        "accepted_prefixes": list(ACCEPTED_PREFIXES),
        "reads_env_values": False,
        "reads_dotenv_values": False,
        "calls_private_endpoints": False,
        "calls_order_endpoints": False,
        "live_trading_allowed": False,
        "secret_values_exposed": False,
        "safety_boundary": "static config schema audit only / no load_config / no .env / no os.environ / no secrets / no private/account/order endpoints / no live trading",
    }


def build_audit_text() -> str:
    data = build_audit_data()
    lines = [
        "Safe Config Schema Audit",
        "",
        f"schema_version: {data['schema_version']}",
        f"required_keys: {', '.join(data['required_keys'])}",
        f"masked_keys: {', '.join(data['masked_keys'])}",
        f"accepted_prefixes: {', '.join(data['accepted_prefixes'])}",
        f"reads_env_values: {str(data['reads_env_values']).lower()}",
        f"reads_dotenv_values: {str(data['reads_dotenv_values']).lower()}",
        f"calls_private_endpoints: {str(data['calls_private_endpoints']).lower()}",
        f"calls_order_endpoints: {str(data['calls_order_endpoints']).lower()}",
        f"live_trading_allowed: {str(data['live_trading_allowed']).lower()}",
        f"secret_values_exposed: {str(data['secret_values_exposed']).lower()}",
        f"safety_boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="safe_config_schema_audit")
    parser.add_argument("--stdout-json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    data = build_audit_data()
    if args.stdout_json:
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(build_audit_text(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
