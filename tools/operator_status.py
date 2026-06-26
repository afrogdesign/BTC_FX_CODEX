from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.runtime_public_status import _format_pretty_status, build_runtime_public_status


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Short operator-facing runtime status wrapper")
    parser.add_argument("--check", action="store_true", help="print the pretty summary and exit with a status code")
    return parser


def _exit_code_from_status(operator_status: object) -> int:
    status = str(operator_status)
    if status == "ok":
        return 0
    if status == "waiting_for_html_cycle":
        return 2
    if status == "startup_status_unavailable":
        return 3
    return 3


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()
    payload = build_runtime_public_status()
    print(_format_pretty_status(payload))
    if args.check:
        return _exit_code_from_status(payload.get("operator_status"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
