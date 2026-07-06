from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.big_chance import (  # noqa: E402
    build_big_chance_artifact as _build_big_chance_artifact,
    write_big_chance_artifact as _write_big_chance_artifact,
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a local Big Chance / Failed Thesis artifact.")
    parser.add_argument("--input", default="logs/last_result.json", help="Input result JSON path.")
    parser.add_argument("--previous", help="Optional previous result JSON path.")
    parser.add_argument("--out-dir", default="local/big_chance", help="Output directory.")
    parser.add_argument("--signal-id", help="Optional guard for the input signal id.")
    parser.add_argument("--replay-signal-id", help="Optional replay prefix for output files.")
    parser.add_argument("--stdout-json", action="store_true", help="Print the generated JSON artifact.")
    parser.add_argument("--dry-run", action="store_true", help="Build only; do not write files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    current = _read_json(input_path)
    if args.signal_id and str(current.get("signal_id", "")).strip() != str(args.signal_id).strip():
        raise SystemExit(
            f"signal_id mismatch: expected {args.signal_id}, got {current.get('signal_id', '')}"
        )
    previous = _read_json(Path(args.previous)) if args.previous else None
    artifact = _build_big_chance_artifact(
        current,
        previous=previous,
        source_file=input_path,
        replay_signal_id=args.replay_signal_id,
    )
    if args.stdout_json:
        sys.stdout.write(json.dumps(artifact, ensure_ascii=False, sort_keys=True) + "\n")
    if not args.dry_run:
        _write_big_chance_artifact(
            artifact,
            Path(args.out_dir),
            replay_signal_id=args.replay_signal_id,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
