from __future__ import annotations

import argparse
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.notification.detail_page import build_notification_detail_html
from src.storage.json_store import load_json


def _default_output_path(signal_id: str) -> Path:
    return BASE_DIR / "tmp" / "notification_detail_preview" / f"{signal_id or 'preview'}.html"


def main() -> None:
    parser = argparse.ArgumentParser(description="signal snapshot JSON から通知詳細HTMLを再生成します。")
    parser.add_argument("--input", required=True, help="入力 JSON パス")
    parser.add_argument("--output", help="出力 HTML パス。未指定時は tmp/notification_detail_preview/")
    args = parser.parse_args()

    input_path = Path(args.input)
    payload = load_json(input_path)
    if payload is None:
        raise SystemExit(f"invalid json: {input_path}")

    signal_id = str(payload.get("signal_id", "")).strip()
    output_path = Path(args.output) if args.output else _default_output_path(signal_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_notification_detail_html(payload), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
