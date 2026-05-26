from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parents[1]
JST = ZoneInfo("Asia/Tokyo")
DEFAULT_DATE_FROM = "2026-04-18"
DEFAULT_MARKET_MAP_DATE_FROM = "2026-05-13"


@dataclass
class StepSpec:
    name: str
    argv: list[str] | None
    output_md: str | None = None
    status: str = "pending"
    note: str | None = None


def _build_log_feedback_commands() -> set[str]:
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    from tools.log_feedback import _build_parser

    parser = _build_parser()
    for action in getattr(parser, "_actions", []):
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict):
            return set(choices.keys())
    return set()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the daily BTC Monitor report set.")
    parser.add_argument("--date", default="")
    parser.add_argument("--date-from", default="")
    parser.add_argument("--date-to", default="")
    parser.add_argument("--max-new-ai-reviews", type=int, default=8)
    parser.add_argument("--skip-ai", action="store_true")
    parser.add_argument("--skip-heavy", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--python-bin", default=".venv312/bin/python")
    return parser


def _resolve_dates(date_token: str, date_from: str, date_to: str) -> tuple[str, str, str]:
    now_jst = datetime.now(tz=JST)
    if date_token:
        parsed = datetime.strptime(date_token, "%Y%m%d")
        resolved_date = parsed.strftime("%Y%m%d")
        resolved_date_to = parsed.strftime("%Y-%m-%d")
    else:
        resolved_date = now_jst.strftime("%Y%m%d")
        resolved_date_to = now_jst.strftime("%Y-%m-%d")
    return resolved_date, (date_from or DEFAULT_DATE_FROM), (date_to or resolved_date_to)


def _rel(path: Path) -> str:
    return path.relative_to(BASE_DIR).as_posix()


def _step(
    python_bin: str,
    command: str,
    *,
    output_md: Path | None = None,
    extra_args: list[str] | None = None,
    name: str | None = None,
) -> StepSpec:
    argv = [python_bin, "tools/log_feedback.py", command]
    if extra_args:
        argv.extend(extra_args)
    if output_md is not None:
        argv.extend(["--output-md", _rel(output_md)])
    return StepSpec(name=name or command, argv=argv, output_md=_rel(output_md) if output_md else None)


def _build_steps(args: argparse.Namespace) -> tuple[list[StepSpec], dict[str, str]]:
    date_token, date_from, date_to = _resolve_dates(args.date, args.date_from, args.date_to)
    commands = _build_log_feedback_commands()
    python_bin = args.python_bin
    reports_dir = BASE_DIR / "運用資料" / "reports"
    analysis_dir = reports_dir / "analysis"
    ai_max = 0 if args.skip_ai else int(args.max_new_ai_reviews)

    steps = [
        _step(
            python_bin,
            "daily-sync",
            output_md=reports_dir / f"feedback_daily_sync_{date_token}.md",
            extra_args=["--max-new-ai-reviews", str(ai_max)],
            name="daily-sync",
        )
    ]

    if not args.skip_heavy:
        if "build-paper-opportunity-diagnostics-report" in commands:
            steps.append(
                _step(
                    python_bin,
                    "build-paper-opportunity-diagnostics-report",
                    output_md=analysis_dir / f"paper_opportunity_diagnostics_{date_token}.md",
                    extra_args=["--date-from", date_from, "--date-to", date_to],
                    name="paper-opportunity-diagnostics",
                )
            )
        else:
            steps.append(StepSpec(name="paper-opportunity-diagnostics", argv=None, status="skipped_missing_command"))

        if "build-market-map-effectiveness-report" in commands:
            steps.append(
                _step(
                    python_bin,
                    "build-market-map-effectiveness-report",
                    output_md=analysis_dir / f"market_map_effectiveness_{date_token}.md",
                    extra_args=["--date-from", DEFAULT_MARKET_MAP_DATE_FROM, "--date-to", date_to],
                    name="market-map-effectiveness",
                )
            )
        else:
            steps.append(StepSpec(name="market-map-effectiveness", argv=None, status="skipped_missing_command"))

    if "build-operational-focus-report" in commands:
        steps.append(
            _step(
                python_bin,
                "build-operational-focus-report",
                output_md=analysis_dir / f"operational_focus_{date_token}.md",
                extra_args=["--date-from", date_from, "--date-to", date_to],
                name="operational-focus",
            )
        )
    else:
        steps.append(StepSpec(name="operational-focus", argv=None, status="skipped_missing_command"))

    if not args.skip_heavy:
        if "build-paper-entry-sl-wait-redesign-report" in commands:
            steps.append(
                _step(
                    python_bin,
                    "build-paper-entry-sl-wait-redesign-report",
                    output_md=analysis_dir / f"paper_entry_sl_wait_redesign_{date_token}.md",
                    extra_args=["--date-from", date_from, "--date-to", date_to],
                    name="paper-entry-sl-wait-redesign",
                )
            )
        elif "build-paper-opportunity-diagnostics-report" in commands:
            steps.append(
                _step(
                    python_bin,
                    "build-paper-opportunity-diagnostics-report",
                    output_md=analysis_dir / f"paper_entry_sl_wait_redesign_{date_token}.md",
                    extra_args=["--date-from", date_from, "--date-to", date_to],
                    name="paper-entry-sl-wait-redesign",
                )
            )
        else:
            steps.append(StepSpec(name="paper-entry-sl-wait-redesign", argv=None, status="skipped_missing_command"))

    if "build-report-hub" in commands:
        steps.append(_step(python_bin, "build-report-hub", name="report-hub"))
    else:
        steps.append(StepSpec(name="report-hub", argv=None, status="skipped_missing_command"))

    return steps, {"date": date_token, "date_from": date_from, "date_to": date_to}


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_daily_reports(args: argparse.Namespace) -> int:
    steps, dates = _build_steps(args)
    if args.dry_run:
        for step in steps:
            if step.argv is None:
                print(f"[skip:{step.status}] {step.name}")
            else:
                print(" ".join(step.argv))
        return 0

    runtime_dir = BASE_DIR / "logs" / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    out_path = runtime_dir / "daily_reports.out"
    err_path = runtime_dir / "daily_reports.err"
    result_path = runtime_dir / "daily_reports_last_result.json"

    started_at = datetime.now(tz=JST)
    out_chunks: list[str] = []
    err_chunks: list[str] = []
    result_steps: list[dict[str, Any]] = []
    has_failures = False

    for step in steps:
        if step.argv is None:
            result_steps.append(
                {
                    "name": step.name,
                    "status": step.status,
                    "returncode": None,
                    "output_md": step.output_md,
                }
            )
            continue

        out_chunks.append(f"$ {' '.join(step.argv)}\n")
        completed = subprocess.run(
            step.argv,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        step_status = "success" if completed.returncode == 0 else "failed"
        if completed.stdout:
            out_chunks.append(completed.stdout)
            if not completed.stdout.endswith("\n"):
                out_chunks.append("\n")
        if completed.stderr:
            err_chunks.append(f"[{step.name}]\n")
            err_chunks.append(completed.stderr)
            if not completed.stderr.endswith("\n"):
                err_chunks.append("\n")
        if completed.returncode != 0:
            has_failures = True
        result_steps.append(
            {
                "name": step.name,
                "status": step_status,
                "returncode": completed.returncode,
                "output_md": step.output_md,
            }
        )

    finished_at = datetime.now(tz=JST)
    _write_text(out_path, "".join(out_chunks))
    _write_text(err_path, "".join(err_chunks))
    result = {
        "started_at_jst": started_at.isoformat(),
        "finished_at_jst": finished_at.isoformat(),
        "status": "partial_failed" if has_failures else "success",
        "date": dates["date"],
        "date_from": dates["date_from"],
        "date_to": dates["date_to"],
        "steps": result_steps,
    }
    _write_text(result_path, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(result_path)
    return 0 if not has_failures else 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_daily_reports(args)


if __name__ == "__main__":
    raise SystemExit(main())
