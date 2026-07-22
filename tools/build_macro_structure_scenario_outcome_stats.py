#!/usr/bin/env python3
"""Build local-only M-STATS1 scenario outcome counts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.feedback.macro_structure_scenario_outcome_stats import (
    ScenarioOutcomeStatsError,
    publish_scenario_outcome_stats,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic macro scenario outcome counts")
    parser.add_argument("--operator-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--max-artifacts", type=int)
    parser.add_argument("--stdout-json", action="store_true")
    args = parser.parse_args()
    try:
        summary = publish_scenario_outcome_stats(args.operator_root, args.output_root, max_artifacts=args.max_artifacts)
    except ScenarioOutcomeStatsError as exc:
        print(json.dumps({"status": "failed", "error_code": exc.code}, ensure_ascii=False), file=sys.stderr)
        return 2
    if args.stdout_json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
