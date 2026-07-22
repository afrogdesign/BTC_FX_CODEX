"""Bounded report-only runtime wrapper for the accepted M-OPS pipeline."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.feedback.macro_structure_daily_operation import _fetch_public_ohlcv

SERVICE_SCHEMA_VERSION = "macro_structure_runtime_service.v1"
SERVICE_METHOD_VERSION = "macro_structure_runtime_service.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
JST = ZoneInfo("Asia/Tokyo")
TIMEFRAMES = ("15m", "1h", "4h")
DEFAULT_INPUT_ROOT = "local/runtime/macro_structure_inputs"
DEFAULT_SNAPSHOT_ROOT = "local/reports/macro_structure"
DEFAULT_HISTORY_ROOT = "local/reports/macro_structure/history"
DEFAULT_OPERATOR_ROOT = "local/reports/macro_structure/operator"
DEFAULT_HEALTH_ROOT = "local/reports/macro_structure/health"
DEFAULT_STATUS = "logs/runtime/macro_structure_service_last_result.json"
DEFAULT_LOCK = "logs/runtime/macro_structure_service.lock"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the report-only macro structure service.")
    parser.add_argument("--symbol", default="BTC_USDT")
    parser.add_argument("--ohlcv-limit", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo-root", default=str(BASE_DIR), help=argparse.SUPPRESS)
    parser.add_argument("--python-bin", default="", help=argparse.SUPPRESS)
    parser.add_argument("--status-path", default=DEFAULT_STATUS, help=argparse.SUPPRESS)
    parser.add_argument("--input-root", default=DEFAULT_INPUT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--snapshot-root", default=DEFAULT_SNAPSHOT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--history-root", default=DEFAULT_HISTORY_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--operator-root", default=DEFAULT_OPERATOR_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--health-root", default=DEFAULT_HEALTH_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--lock-path", default=DEFAULT_LOCK, help=argparse.SUPPRESS)
    return parser


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalized_evaluation_time() -> datetime:
    return _utc_now().astimezone(timezone.utc).replace(second=0, microsecond=0)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _jst_iso(value: datetime) -> str:
    return value.astimezone(JST).isoformat()


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".macro-service-status-", dir=path.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        temporary.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_compact_json(stdout: str) -> dict[str, Any]:
    for line in reversed([line.strip() for line in stdout.splitlines() if line.strip()]):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("compact_json_missing")


def _promote_complete_inputs(stage: Path, latest: Path) -> None:
    latest.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if latest.exists():
        backup = Path(tempfile.mkdtemp(prefix=".macro-input-previous-", dir=latest.parent))
        backup.rmdir()
        latest.replace(backup)
    try:
        stage.replace(latest)
    except Exception:
        if latest.exists():
            shutil.rmtree(latest)
        if backup is not None and backup.exists():
            backup.replace(latest)
        raise
    if backup is not None and backup.exists():
        shutil.rmtree(backup)


def _stage_public_inputs(root: Path, symbol: str, limit: int) -> tuple[Path, dict[str, str]]:
    root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".macro-input-stage-", dir=root))
    try:
        paths: dict[str, Path] = {}
        for interval in TIMEFRAMES:
            path = stage / f"ohlcv_{interval}.csv"
            _fetch_public_ohlcv(path, int(limit), interval, symbol)
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError(f"public_input_{interval}_invalid")
            paths[interval] = path
        latest = root / "latest"
        _promote_complete_inputs(stage, latest)
        return latest, {interval: _sha256(latest / f"ohlcv_{interval}.csv") for interval in TIMEFRAMES}
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def _build_commands(root: Path, python_bin: Path, symbol: str, limit: int, evaluation: datetime, input_root: Path, snapshot_root: Path, history_root: Path, operator_root: Path) -> list[tuple[str, list[str]]]:
    relative = lambda path: _relative(path, root)
    inputs = input_root / "latest"
    common = [str(python_bin), "tools/log_feedback.py"]
    return [
        ("snapshot", common + ["run-macro-structure-daily", "--ohlcv-15m", relative(inputs / "ohlcv_15m.csv"), "--ohlcv-1h", relative(inputs / "ohlcv_1h.csv"), "--ohlcv-4h", relative(inputs / "ohlcv_4h.csv"), "--output-root", relative(snapshot_root), "--symbol", symbol, "--ohlcv-limit", str(limit), "--evaluation-time-utc", _iso(evaluation), "--stdout-json"]),
        ("history", common + ["run-macro-structure-history", "--snapshot-root", relative(snapshot_root), "--output-root", relative(history_root), "--symbol", symbol, "--stdout-json"]),
        ("operator", common + ["render-macro-structure-operator", "--snapshot-root", relative(snapshot_root), "--history-root", relative(history_root), "--ohlcv-15m-csv", relative(inputs / "ohlcv_15m.csv"), "--ohlcv-4h-csv", relative(inputs / "ohlcv_4h.csv"), "--output-root", relative(operator_root), "--symbol", symbol, "--stdout-json"]),
    ]


def _build_health_command(root: Path, python_bin: Path, symbol: str, evaluation: datetime, status_path: Path, snapshot_root: Path, history_root: Path, operator_root: Path, plist: Path, health_root: Path) -> list[str]:
    relative = lambda path: _relative(path, root)
    return [
        str(python_bin), "tools/log_feedback.py", "check-macro-structure-health",
        "--runtime-status", relative(status_path),
        "--snapshot-root", relative(snapshot_root),
        "--history-root", relative(history_root),
        "--operator-root", relative(operator_root),
        "--plist", relative(plist),
        "--output-root", relative(health_root),
        "--evaluation-time-utc", _iso(evaluation),
        "--stdout-json",
    ]


def _step_summary(name: str, returncode: int, parsed: dict[str, Any] | None, error_code: str = "") -> dict[str, Any]:
    result = {"name": name, "status": "success" if returncode == 0 and parsed and parsed.get("ok") is True else "failed", "return_code": int(returncode)}
    if error_code:
        result["error_code"] = error_code
    return result


def _run_step(name: str, argv: list[str], root: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    completed = subprocess.run(argv, cwd=root, capture_output=True, text=True, encoding="utf-8")
    try:
        parsed = _parse_compact_json(completed.stdout)
    except ValueError as exc:
        return _step_summary(name, completed.returncode, None, str(exc)), None
    if completed.returncode != 0 or parsed.get("ok") is not True:
        error_code = str(parsed.get("error_code") or "operation_failed")
        return _step_summary(name, completed.returncode, parsed, error_code), parsed
    return _step_summary(name, completed.returncode, parsed), parsed


def _health_generation(argv: list[str], root: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(argv, cwd=root, capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return {"attempted": True, "status": "failed", "return_code": 1, "error_code": "health_subprocess_failed"}
    try:
        parsed = _parse_compact_json(completed.stdout)
    except ValueError:
        return {"attempted": True, "status": "failed", "return_code": int(completed.returncode), "error_code": "health_compact_json_missing"}
    state = parsed.get("health_state")
    expected = {"healthy": 0, "healthy_insufficient": 0, "degraded": 2, "overdue": 2, "failed": 3, "inconsistent": 3, "unavailable": 3}
    if parsed.get("report_written") is not True:
        return {"attempted": True, "status": "failed", "return_code": int(completed.returncode), "error_code": "health_report_not_written"}
    if state not in expected or not isinstance(parsed.get("health_artifact_id"), str) or not parsed["health_artifact_id"]:
        return {"attempted": True, "status": "failed", "return_code": int(completed.returncode), "error_code": "health_result_invalid"}
    if completed.returncode != expected[state] or parsed.get("exit_code") != expected[state]:
        return {"attempted": True, "status": "failed", "return_code": int(completed.returncode), "error_code": "health_exit_code_mismatch"}
    result = {"attempted": True, "status": "published", "return_code": int(completed.returncode), "health_state": state, "health_artifact_id": parsed["health_artifact_id"], "report_written": True}
    if parsed.get("operator_html_path") is not None:
        result["operator_html_path"] = parsed["operator_html_path"]
    return result


def _planned_output(root: Path, args: argparse.Namespace, evaluation: datetime, commands: list[tuple[str, list[str]]]) -> dict[str, Any]:
    input_root = root / args.input_root
    snapshot_root = root / args.snapshot_root
    history_root = root / args.history_root
    operator_root = root / args.operator_root
    status_path = root / args.status_path
    health_root = root / args.health_root
    health_command = _build_health_command(root, root / (args.python_bin or (root / ".venv312" / "bin" / "python")), args.symbol, evaluation, status_path, snapshot_root, history_root, operator_root, root / "deploy/com.afrog.btc-macro-structure.plist", health_root)
    return {
        "ok": True,
        "status": "dry_run",
        "symbol": args.symbol,
        "evaluation_time_rule": "capture one aware UTC time and normalize to minute precision",
        "evaluation_utc": _iso(evaluation),
        "roots": {"inputs": _relative(input_root / "latest", root), "snapshot": _relative(snapshot_root, root), "history": _relative(history_root, root), "operator": _relative(operator_root, root)},
        "commands": [argv for _, argv in commands],
        "health_command": health_command,
        "health_output_root": _relative(health_root, root),
        "safety_boundary": SAFETY,
    }


def run_service(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root = Path(args.repo_root).resolve()
    python_bin = Path(args.python_bin or (root / ".venv312" / "bin" / "python"))
    input_root = root / args.input_root
    snapshot_root = root / args.snapshot_root
    history_root = root / args.history_root
    operator_root = root / args.operator_root
    health_root = root / args.health_root
    status_path = root / args.status_path
    lock_path = root / args.lock_path
    evaluation = _normalized_evaluation_time()
    commands = _build_commands(root, python_bin, args.symbol, args.ohlcv_limit, evaluation, input_root, snapshot_root, history_root, operator_root)
    health_command = _build_health_command(root, python_bin, args.symbol, evaluation, status_path, snapshot_root, history_root, operator_root, root / "deploy/com.afrog.btc-macro-structure.plist", health_root)
    if args.dry_run:
        result = _planned_output(root, args, evaluation, commands)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0, result

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_handle = lock_path.open("a+")
    try:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            result = {"ok": False, "status": "already_running", "service_schema_version": SERVICE_SCHEMA_VERSION, "service_method_version": SERVICE_METHOD_VERSION, "symbol": args.symbol, "report_only": True, "private_actual_trade_input": False, "automatic_order_allowed": False, "safety_boundary": SAFETY}
            print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            return 0, result
        started = _utc_now().astimezone(timezone.utc)
        status: dict[str, Any] = {"ok": False, "service_schema_version": SERVICE_SCHEMA_VERSION, "service_method_version": SERVICE_METHOD_VERSION, "status": "failed", "started_at_utc": _iso(started), "started_at_jst": _jst_iso(started), "evaluation_utc": _iso(evaluation), "evaluation_jst": _jst_iso(evaluation), "symbol": args.symbol, "steps": [], "public_input_fingerprints": {}, "report_only": True, "private_actual_trade_input": False, "automatic_order_allowed": False, "safety_boundary": SAFETY}
        try:
            input_latest, fingerprints = _stage_public_inputs(input_root, args.symbol, args.ohlcv_limit)
            status["public_input_fingerprints"] = fingerprints
            status["public_input_root"] = _relative(input_latest, root)
            parsed_steps: list[dict[str, Any]] = []
            for name, argv in commands:
                step, parsed = _run_step(name, argv, root)
                status["steps"].append(step)
                if step["status"] != "success":
                    status["error_code"] = step.get("error_code", "operation_failed")
                    break
                parsed_value = parsed or {}
                parsed_steps.append(parsed_value)
                if name == "snapshot":
                    status.update({
                        "snapshot_run_id": parsed_value.get("run_id"),
                        "snapshot_id": parsed_value.get("snapshot_id"),
                        "snapshot_result_status": parsed_value.get("result_status"),
                        "stale_status": parsed_value.get("stale_status"),
                        "continuity_status": parsed_value.get("continuity_status"),
                        "data_quality_status": parsed_value.get("data_quality_status"),
                        "snapshot_artifact_root": "local/reports/macro_structure",
                    })
                elif name == "history":
                    status.update({
                        "history_id": parsed_value.get("history_id"),
                        "history_result_status": parsed_value.get("history_result_status") or parsed_value.get("result_status"),
                        "history_artifact_root": "local/reports/macro_structure/history",
                    })
                elif name == "operator":
                    status.update({
                        "operator_artifact_id": parsed_value.get("operator_artifact_id") or parsed_value.get("artifact_id"),
                        "operator_result_status": parsed_value.get("result_status"),
                        "operator_latest_entry_status": parsed_value.get("latest_entry_status"),
                        "operator_latest_entry_id": parsed_value.get("latest_entry_id"),
                        "operator_latest_entry_method_version": parsed_value.get("latest_entry_method_version"),
                        "operator_artifact_root": "local/reports/macro_structure/operator",
                    })
            if len(parsed_steps) == len(commands):
                snapshot, history, operator = parsed_steps
                status.update({
                    "status": "success", "ok": True,
                    "snapshot_run_id": snapshot.get("run_id"), "snapshot_id": snapshot.get("snapshot_id"),
                    "history_id": history.get("history_id"), "operator_artifact_id": operator.get("operator_artifact_id") or operator.get("artifact_id"),
                    "snapshot_result_status": snapshot.get("result_status"), "history_result_status": history.get("history_result_status") or history.get("result_status"),
                    "stale_status": snapshot.get("stale_status"), "continuity_status": snapshot.get("continuity_status"), "data_quality_status": snapshot.get("data_quality_status"),
                    "snapshot_artifact_root": "local/reports/macro_structure", "history_artifact_root": "local/reports/macro_structure/history", "operator_artifact_root": "local/reports/macro_structure/operator",
                })
        except (OSError, ValueError) as exc:
            status["error_code"] = str(exc)
        finished = _utc_now().astimezone(timezone.utc)
        status["finished_at_utc"] = _iso(finished)
        status["finished_at_jst"] = _jst_iso(finished)
        _atomic_json(status_path, status)
        health_generation = {"attempted": False, "status": "not_run"}
        if status.get("status") != "already_running":
            health_generation = _health_generation(_build_health_command(root, python_bin, args.symbol, finished, status_path, snapshot_root, history_root, operator_root, root / "deploy/com.afrog.btc-macro-structure.plist", health_root), root)
        compact = {key: value for key, value in status.items() if key not in {"public_input_fingerprints"}}
        compact["health_generation"] = health_generation
        print(json.dumps(compact, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        result = dict(status)
        result["health_generation"] = health_generation
        return (0 if status.get("ok") is True else 1), result
    finally:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        finally:
            lock_handle.close()


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    return run_service(args)[0]


if __name__ == "__main__":
    raise SystemExit(main())
