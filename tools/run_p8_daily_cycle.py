from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parents[1]
JST = ZoneInfo("Asia/Tokyo")
DEFAULT_CANDIDATES = "logs/csv/active_plan_candidates.csv"
DEFAULT_SIGNAL_CONTEXT = "logs/csv/trades.csv"
DEFAULT_OHLCV = "logs/csv/active_plan_intraperiod_ohlcv.csv"
DEFAULT_STATUS = "logs/runtime/p8_daily_cycle_last_result.json"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the report-only daily P8 operating cycle.")
    parser.add_argument("--date", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo-root", default=str(BASE_DIR), help=argparse.SUPPRESS)
    parser.add_argument("--python-bin", default="", help=argparse.SUPPRESS)
    parser.add_argument("--status-path", default=DEFAULT_STATUS, help=argparse.SUPPRESS)
    parser.add_argument("--output-base", default="logs/p8_operating_cycles", help=argparse.SUPPRESS)
    parser.add_argument("--include-turning-precursor-shadow", action="store_true")
    parser.add_argument("--include-macro-structure-shadow", action="store_true")
    return parser


def _date(value: str) -> str:
    if value:
        return datetime.strptime(value, "%Y%m%d").strftime("%Y%m%d")
    return datetime.now(JST).strftime("%Y%m%d")


def _atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".p8-daily-status-", dir=path.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        temporary.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _latest_previous_manifest(root: Path, output_base: Path, report_date: str) -> Path | None:
    candidates = []
    if output_base.exists():
        for directory in output_base.iterdir():
            if not directory.is_dir() or directory.name >= report_date or not directory.name.isdigit():
                continue
            path = directory / "p8_v2" / "p8_daily_manifest_v2.json"
            if path.is_file(): candidates.append(path)
    return sorted(candidates)[-1] if candidates else None


def _parse_json_line(stdout: str) -> dict[str, object]:
    for line in reversed([item.strip() for item in stdout.splitlines() if item.strip()]):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict): return value
    return {}


def _build_argv(root: Path, report_date: str, output_root: Path, python_bin: str, episodes: Path | None, links: Path | None, include_turning_precursor_shadow: bool = False, include_macro_structure_shadow: bool = False) -> list[str]:
    argv = [python_bin, "tools/log_feedback.py", "run-p8-operating-cycle", "--date", report_date, "--candidates", DEFAULT_CANDIDATES, "--signal-context", DEFAULT_SIGNAL_CONTEXT, "--ohlcv", DEFAULT_OHLCV, "--output-root", _relative(output_root, root), "--fetch-public-ohlcv", "--replace-output", "--stdout-json"]
    if episodes is not None and links is not None:
        argv.extend(["--actual-episodes", _relative(episodes, root), "--actual-links", _relative(links, root)])
    if include_turning_precursor_shadow:
        argv.append("--include-turning-precursor-shadow")
    if include_macro_structure_shadow:
        argv.append("--include-macro-structure-shadow")
    return argv


def run_daily_cycle(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    report_date = _date(args.date)
    output_root = root / args.output_base / report_date
    status_path = root / args.status_path
    python_bin = args.python_bin or str(root / ".venv312" / "bin" / "python")
    episodes = root / "logs/csv/manual_trade_episodes.csv"
    links = root / "logs/csv/manual_trade_signal_links.csv"
    episodes_exists, links_exists = episodes.exists(), links.exists()
    started = datetime.now(JST).isoformat()
    if episodes_exists != links_exists:
        payload = {"started_at_jst": started, "finished_at_jst": datetime.now(JST).isoformat(), "report_date": report_date, "status": "actual_pair_incomplete", "returncode": 2, "output_root": _relative(output_root, root), "manifest_path": "", "summary_path": "", "actual_input_status": "actual_pair_incomplete", "error_codes": ["actual_pair_incomplete"], "safety_boundary": SAFETY}
        if not args.dry_run:
            _atomic_json(status_path, payload)
        else:
            print(json.dumps({"status": "dry_run", "actual_input_status": "actual_pair_incomplete"}, separators=(",", ":")))
        return 2
    argv = _build_argv(root, report_date, output_root, python_bin, episodes if episodes_exists else None, links if links_exists else None, bool(args.include_turning_precursor_shadow), bool(args.include_macro_structure_shadow))
    if args.dry_run:
        print(json.dumps({"status": "dry_run", "stages": ["core_p8", "current_evidence_refresh", "p8_p9_v2"], "command": argv, "evidence_command": [python_bin, "tools/refresh_p_current_evidence.py"], "p8_v2_command": [python_bin, "tools/build_p8_daily_manifest_v2.py"], "turning_precursor_shadow_enabled": bool(args.include_turning_precursor_shadow), "macro_structure_shadow_enabled": bool(args.include_macro_structure_shadow)}, ensure_ascii=False, separators=(",", ":")))
        return 0
    completed = subprocess.run(argv, cwd=root, capture_output=True, text=True, encoding="utf-8")
    finished = datetime.now(JST).isoformat()
    parsed: dict[str, object] = {}
    for line in reversed([item.strip() for item in completed.stdout.splitlines() if item.strip()]):
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            parsed = candidate
            break
    success = completed.returncode == 0 and parsed.get("ok") is True
    evidence_result: dict[str, object] = {"status": "not_run"}
    p8_v2_result: dict[str, object] = {"status": "not_run"}
    report_stage_failure = False
    cycle_manifest_path = output_root / "cycle_manifest.json"
    if success and cycle_manifest_path.is_file():
        evidence_cmd = [python_bin, "tools/refresh_p_current_evidence.py", "--repo-root", str(root), "--current-date", report_date, "--runtime-generation", "Ver04-v5", "--stdout-json"]
        evidence_completed = subprocess.run(evidence_cmd, cwd=root, capture_output=True, text=True, encoding="utf-8")
        evidence_result = _parse_json_line(evidence_completed.stdout)
        evidence_result["status"] = "success" if evidence_completed.returncode == 0 and evidence_result.get("ok") is True else "failed"
        if evidence_result["status"] != "success": report_stage_failure = True
        if not report_stage_failure:
            cumulative = root / "local/reports/p_evidence/p_current_generation/latest/evidence_manifest.json"
            modern = root / "local/reports/p_evidence/p_current_generation/latest/modern_attribution_report.json"
            p8_root = output_root / "p8_v2"
            p8_cmd = [python_bin, "tools/build_p8_daily_manifest_v2.py", "--cycle-manifest", _relative(cycle_manifest_path, root), "--trial-report", _relative(output_root / "manual_operator_trial_evidence.json", root), "--trial-facts", _relative(output_root / "manual_operator_trial_facts.csv", root), "--review-queue", _relative(output_root / "manual_operator_trial_review_queue.csv", root), "--cumulative-manifest", _relative(cumulative, root), "--modern-attribution-report", _relative(modern, root), "--output-root", _relative(p8_root, root), "--runtime-generation", "Ver04-v5", "--stdout-json", "--replace-output"]
            previous = _latest_previous_manifest(root, root / args.output_base, report_date)
            if previous is not None: p8_cmd.extend(["--previous-v2-manifest", _relative(previous, root)])
            p8_completed = subprocess.run(p8_cmd, cwd=root, capture_output=True, text=True, encoding="utf-8")
            p8_v2_result = _parse_json_line(p8_completed.stdout)
            p8_v2_result["status"] = "success" if p8_completed.returncode == 0 and p8_v2_result.get("ok") is True else "failed"
            if p8_v2_result["status"] != "success": report_stage_failure = True
    if success and report_stage_failure:
        status = "partial_failure"
    else:
        status = "success" if success else "failed"
    status = "success" if success else "failed"
    payload = {
        "started_at_jst": started, "finished_at_jst": finished, "report_date": report_date,
        "status": status, "returncode": int(completed.returncode if not report_stage_failure else (p8_v2_result.get("returncode") or 1)), "output_root": _relative(output_root, root),
        "manifest_path": f"{_relative(output_root, root)}/cycle_manifest.json" if success else "",
        "summary_path": f"{_relative(output_root, root)}/cycle_summary.md" if success else "",
        "actual_input_status": "provided" if episodes_exists else "missing",
        "counts": parsed.get("counts", {}), "readiness": parsed.get("p9_readiness", {}),
        "issue_001": parsed.get("issue_001", {}), "error_codes": parsed.get("errors", []) if not success else [],
        "turning_precursor_shadow": parsed.get("turning_precursor_shadow", {"enabled": bool(args.include_turning_precursor_shadow), "status": "disabled"}),
        "macro_structure_shadow": parsed.get("macro_structure_shadow", {"enabled": bool(args.include_macro_structure_shadow), "status": "disabled"}),
        "evidence_refresh": {"status": evidence_result.get("status", "not_run"), "run_id": evidence_result.get("run_id", ""), "latest_manifest_path": "local/reports/p_evidence/p_current_generation/latest/evidence_manifest.json" if evidence_result.get("status") == "success" else "", "current_v4_classification_rows": evidence_result.get("current_v4_classification_rows", 0), "current_v4_proxy_trial_rows": evidence_result.get("current_v4_proxy_trial_rows", 0)},
        "formal_gate_semantic_impact": {"status": "success" if evidence_result.get("status") == "success" else evidence_result.get("status", "not_run"), "rows_where_no_trade_blocker_would_be_removed": evidence_result.get("formal_gate_semantic_impact", {}).get("rows_where_no_trade_blocker_would_be_removed", 0), "rows_potentially_changed_to_pass": evidence_result.get("formal_gate_semantic_impact", {}).get("rows_potentially_changed_to_pass", 0)},
        "p8_v2": {"status": p8_v2_result.get("status", "not_run"), "run_id": p8_v2_result.get("run_id", ""), "manifest_path": _relative(output_root / "p8_v2/p8_daily_manifest_v2.json", root) if p8_v2_result.get("status") == "success" else "", "readiness_state": p8_v2_result.get("readiness_v2_state", ""), "missing_requirements": p8_v2_result.get("missing_requirements", [])},
        "safety_boundary": SAFETY,
    }
    _atomic_json(status_path, payload)
    print(json.dumps({"status": status, "report_date": report_date, "returncode": int(payload["returncode"]), "output_root": payload["output_root"], "actual_input_status": payload["actual_input_status"], "counts": payload["counts"], "readiness": payload["readiness"], "turning_precursor_shadow": payload["turning_precursor_shadow"], "macro_structure_shadow": payload["macro_structure_shadow"], "evidence_refresh": payload["evidence_refresh"], "formal_gate_semantic_impact": payload["formal_gate_semantic_impact"], "p8_v2": payload["p8_v2"]}, ensure_ascii=False, separators=(",", ":")))
    return 0 if status == "success" else (completed.returncode or 1)


def main(argv: list[str] | None = None) -> int:
    return run_daily_cycle(_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
