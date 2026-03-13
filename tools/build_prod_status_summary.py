from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _file_mtime_jst(path: Path) -> str:
    if not path.exists():
        return ""
    return datetime.fromtimestamp(path.stat().st_mtime).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _build_side_summary(label: str, base_dir: Path) -> dict[str, Any]:
    heartbeat_path = base_dir / "heartbeat.txt"
    last_result_path = base_dir / "last_result.json"
    runtime_pid_path = base_dir / "runtime" / "monitor.pid"
    errors_dir = base_dir / "errors"

    last_result = _read_json(last_result_path)
    latest_error = ""
    if errors_dir.exists():
        error_files = sorted(errors_dir.glob("*.log"))
        if error_files:
            latest_error = error_files[-1].name

    return {
        "label": label,
        "base_dir": str(base_dir),
        "heartbeat_exists": heartbeat_path.exists(),
        "heartbeat_text": _read_text(heartbeat_path),
        "heartbeat_mtime_jst": _file_mtime_jst(heartbeat_path),
        "last_result_exists": last_result_path.exists(),
        "last_result_mtime_jst": _file_mtime_jst(last_result_path),
        "signal_id": last_result.get("signal_id", ""),
        "timestamp_jst": last_result.get("timestamp_jst", ""),
        "system_label": last_result.get("system_label", ""),
        "system_mode_label": last_result.get("system_mode_label", ""),
        "ai_decision": last_result.get("ai_decision", ""),
        "data_quality_flag": last_result.get("data_quality_flag", ""),
        "summary_subject": last_result.get("summary_subject", ""),
        "monitor_pid": _read_text(runtime_pid_path),
        "latest_error_log": latest_error,
    }


def _build_comparison(api_side: dict[str, Any], cli_side: dict[str, Any]) -> dict[str, Any]:
    same_signal_id = bool(api_side.get("signal_id")) and api_side.get("signal_id") == cli_side.get("signal_id")
    same_heartbeat = bool(api_side.get("heartbeat_text")) and api_side.get("heartbeat_text") == cli_side.get("heartbeat_text")
    return {
        "same_signal_id": same_signal_id,
        "same_heartbeat_text": same_heartbeat,
        "api_signal_id": api_side.get("signal_id", ""),
        "cli_signal_id": cli_side.get("signal_id", ""),
        "api_data_quality_flag": api_side.get("data_quality_flag", ""),
        "cli_data_quality_flag": cli_side.get("data_quality_flag", ""),
        "api_latest_error_log": api_side.get("latest_error_log", ""),
        "cli_latest_error_log": cli_side.get("latest_error_log", ""),
    }


def _build_markdown(summary: dict[str, Any]) -> str:
    generated_at = summary["generated_at_jst"]
    api_side = summary["api_snapshot"]
    cli_side = summary["cli_local"]
    comparison = summary["comparison"]
    lines = [
        "# 本番状態サマリ",
        "",
        f"更新日: {generated_at}",
        "",
        "## API 本番 snapshot",
        f"- signal_id: `{api_side['signal_id'] or 'なし'}`",
        f"- heartbeat: `{api_side['heartbeat_text'] or 'なし'}`",
        f"- last_result: `{api_side['timestamp_jst'] or 'なし'}` / `{api_side['data_quality_flag'] or 'なし'}` / `{api_side['ai_decision'] or 'なし'}`",
        f"- subject: `{api_side['summary_subject'] or 'なし'}`",
        f"- latest_error: `{api_side['latest_error_log'] or 'なし'}`",
        "",
        "## CLI 開発 local",
        f"- signal_id: `{cli_side['signal_id'] or 'なし'}`",
        f"- heartbeat: `{cli_side['heartbeat_text'] or 'なし'}`",
        f"- last_result: `{cli_side['timestamp_jst'] or 'なし'}` / `{cli_side['data_quality_flag'] or 'なし'}` / `{cli_side['ai_decision'] or 'なし'}`",
        f"- subject: `{cli_side['summary_subject'] or 'なし'}`",
        f"- latest_error: `{cli_side['latest_error_log'] or 'なし'}`",
        "",
        "## 比較メモ",
        f"- 同じ signal_id か: `{comparison['same_signal_id']}`",
        f"- heartbeat 完全一致か: `{comparison['same_heartbeat_text']}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="本番 API snapshot とローカル CLI の軽量サマリを生成します。")
    parser.add_argument("--snapshot-dir", default="tmp/prod_ver021_snapshot", help="本番 snapshot ディレクトリ")
    parser.add_argument("--local-logs-dir", default="logs", help="ローカル logs ディレクトリ")
    parser.add_argument("--output-json", default="tmp/prod_status_summary.json", help="出力 JSON パス")
    parser.add_argument("--output-md", default="tmp/prod_status_summary.md", help="出力 Markdown パス")
    args = parser.parse_args()

    snapshot_dir = Path(args.snapshot_dir)
    local_logs_dir = Path(args.local_logs_dir)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)

    api_side = _build_side_summary("api_snapshot", snapshot_dir)
    cli_side = _build_side_summary("cli_local", local_logs_dir)

    summary = {
        "generated_at_jst": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M JST"),
        "api_snapshot": api_side,
        "cli_local": cli_side,
        "comparison": _build_comparison(api_side, cli_side),
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(_build_markdown(summary), encoding="utf-8")
    print(f"summary_json:{output_json}")
    print(f"summary_md:{output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
