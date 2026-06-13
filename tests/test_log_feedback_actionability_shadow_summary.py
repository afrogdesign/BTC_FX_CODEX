from __future__ import annotations

import csv
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.trade.actionability_gate import ACTIONABILITY_SAFETY, ACTIONABILITY_SHADOW_DECISION_HEADER


class LogFeedbackActionabilityShadowSummaryTest(unittest.TestCase):
    def _run_cli(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BASE_DIR / "tools" / "log_feedback.py"), "summarize-actionability-shadow-decisions", *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_shadow_csv(self, path: Path, rows: list[dict[str, str]], *, fieldnames: list[str] | None = None) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames or ACTIONABILITY_SHADOW_DECISION_HEADER)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return path

    def _expected_markdown(self, rows: list[dict[str, str]]) -> str:
        def value_for(row: dict[str, str], field_name: str) -> str:
            normalized = str(row.get(field_name, "")).strip()
            return normalized if normalized else "UNKNOWN"

        def section(title: str, field_name: str) -> list[str]:
            counts = Counter(value_for(row, field_name) for row in rows)
            lines = [f"## {title}", ""]
            if counts:
                for label in sorted(counts):
                    lines.append(f"- {label}: {counts[label]}件")
            else:
                lines.append("- none")
            lines.append("")
            return lines

        lines = [
            "# Actionability Shadow Decision Summary",
            "",
            "- safety boundary: report-only, not FORMAL_GO, no automatic order, human decides manually",
            f"- total row count: {len(rows)}",
            "",
        ]
        lines.extend(section("Counts by actionability_label", "actionability_label"))
        lines.extend(section("Counts by human_action", "human_action"))
        lines.extend(section("Counts by active_plan_label", "active_plan_label"))
        lines.extend(section("Counts by final_outcome", "final_outcome"))
        lines.extend(section("Counts by source_readiness", "source_readiness"))
        return "\n".join(lines) + "\n"

    def test_help_includes_required_arguments(self) -> None:
        result = self._run_cli(["--help"])

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("summarize-actionability-shadow-decisions", result.stdout)
        self.assertIn("--input-csv", result.stdout)
        self.assertIn("--output-md", result.stdout)

    def test_stdout_summary_is_deterministic_when_output_md_is_omitted(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_csv = base_dir / "logs" / "csv" / "active_plan_shadow_decisions.csv"
            rows = [
                {
                    "generated_at_jst": "2026-06-13T10:00:00+09:00",
                    "signal_id": "sig-001",
                    "symbol": "BTC_USDT",
                    "timeframe": "15m",
                    "active_plan_label": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit_zone_mid",
                    "actionability_label": "ACTIONABLE_COPY_READY",
                    "actionability_reasons": "deterministic_checks_passed",
                    "human_action": "manual_copy_review",
                    "actionability_safety": ACTIONABILITY_SAFETY,
                    "source_readiness": "ready",
                    "pending_caveat": "pending_coverage_caveat: diagnostic=coverage_ok",
                    "detail_report_path": "運用資料/reports/analysis/example.md",
                    "final_outcome": "pending",
                    "notes": "",
                },
                {
                    "generated_at_jst": "2026-06-13T11:00:00+09:00",
                    "signal_id": "sig-002",
                    "symbol": "BTC_USDT",
                    "timeframe": "15m",
                    "active_plan_label": "",
                    "side": "review_required",
                    "entry_mode": "review_required",
                    "actionability_label": "",
                    "actionability_reasons": "",
                    "human_action": "",
                    "actionability_safety": ACTIONABILITY_SAFETY,
                    "source_readiness": "",
                    "pending_caveat": "pending_coverage_caveat: diagnostic=no_intraperiod_evidence",
                    "detail_report_path": "運用資料/reports/analysis/example.md",
                    "final_outcome": "reviewed",
                    "notes": "blank-value row",
                },
            ]
            self._write_shadow_csv(input_csv, rows)

            result = self._run_cli(["--input-csv", str(input_csv)])

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, self._expected_markdown(rows))

    def test_output_md_writes_same_markdown_and_prints_compact_line(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_csv = base_dir / "logs" / "csv" / "active_plan_shadow_decisions.csv"
            output_md = base_dir / "summary.md"
            rows = [
                {
                    "generated_at_jst": "2026-06-13T10:00:00+09:00",
                    "signal_id": "sig-001",
                    "symbol": "BTC_USDT",
                    "timeframe": "15m",
                    "active_plan_label": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit_zone_mid",
                    "actionability_label": "ACTIONABLE_COPY_READY",
                    "actionability_reasons": "deterministic_checks_passed",
                    "human_action": "manual_copy_review",
                    "actionability_safety": ACTIONABILITY_SAFETY,
                    "source_readiness": "ready",
                    "pending_caveat": "pending_coverage_caveat: diagnostic=coverage_ok",
                    "detail_report_path": "運用資料/reports/analysis/example.md",
                    "final_outcome": "pending",
                    "notes": "",
                },
                {
                    "generated_at_jst": "2026-06-13T11:00:00+09:00",
                    "signal_id": "sig-002",
                    "symbol": "BTC_USDT",
                    "timeframe": "15m",
                    "active_plan_label": "",
                    "side": "review_required",
                    "entry_mode": "review_required",
                    "actionability_label": "",
                    "actionability_reasons": "",
                    "human_action": "",
                    "actionability_safety": ACTIONABILITY_SAFETY,
                    "source_readiness": "",
                    "pending_caveat": "pending_coverage_caveat: diagnostic=no_intraperiod_evidence",
                    "detail_report_path": "運用資料/reports/analysis/example.md",
                    "final_outcome": "reviewed",
                    "notes": "blank-value row",
                },
            ]
            self._write_shadow_csv(input_csv, rows)

            result = self._run_cli(["--input-csv", str(input_csv), "--output-md", str(output_md)])

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, f"actionability_shadow_summary_output_md={output_md}\n")
            self.assertEqual(output_md.read_text(encoding="utf-8"), self._expected_markdown(rows))

    def test_empty_header_only_csv_succeeds(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_csv = base_dir / "logs" / "csv" / "active_plan_shadow_decisions.csv"
            self._write_shadow_csv(input_csv, [])

            result = self._run_cli(["--input-csv", str(input_csv)])

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("- total row count: 0", result.stdout)
            self.assertEqual(result.stdout, self._expected_markdown([]))

    def test_missing_required_columns_fail_clearly(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_csv = base_dir / "logs" / "csv" / "active_plan_shadow_decisions.csv"
            self._write_shadow_csv(input_csv, [], fieldnames=["generated_at_jst", "signal_id", "symbol"])

            result = self._run_cli(["--input-csv", str(input_csv)])

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input_csv missing required columns:", result.stderr)
            self.assertIn("actionability_label", result.stderr)

    def test_rejects_paper_positions_csv_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_csv = base_dir / "logs" / "csv" / "paper_positions.csv"
            self._write_shadow_csv(input_csv, [])

            result = self._run_cli(["--input-csv", str(input_csv)])

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not be paper_positions.csv", result.stderr)

