from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.log_feedback import ACTIVE_PLAN_PAPER_CANDIDATE_HEADER, build_active_plan_paper_candidates


class ActivePlanPaperCandidatesTests(unittest.TestCase):
    def _active_plan_json(self) -> str:
        return json.dumps(
            {
                "plan_version": "active_trade_plan_v1",
                "primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                "headline": "下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。",
                "side_plans": {
                    "long": {
                        "side": "long",
                        "entry_zone_low": 60322.42,
                        "entry_zone_high": 60524.08,
                        "entry_mid": 60423.25,
                        "stop_loss": 60025.57,
                        "tp1": 60940.23,
                        "tp2": 61377.68,
                        "rr_current_tp1": 1.44,
                        "rr_current_tp2": 2.66,
                        "rr_zone_mid_tp1": 1.3,
                        "rr_zone_mid_tp2": 2.4,
                        "market_entry_status": "blocked",
                        "limit_entry_status": "allowed",
                        "counter_scalp_status": "conditional",
                        "breakout_status": "blocked",
                        "next_condition": "60,322-60,524 へ押し、15分足で反発継続なら候補",
                    },
                    "short": {
                        "side": "short",
                        "entry_zone_low": 60680.82,
                        "entry_zone_high": 60882.88,
                        "entry_mid": 60781.85,
                        "stop_loss": 61179.73,
                        "tp1": 60264.61,
                        "tp2": 59826.94,
                        "rr_current_tp1": 0.58,
                        "rr_current_tp2": 1.37,
                        "rr_zone_mid_tp1": 1.3,
                        "rr_zone_mid_tp2": 2.4,
                        "market_entry_status": "blocked",
                        "limit_entry_status": "allowed",
                        "counter_scalp_status": "blocked",
                        "breakout_status": "blocked",
                        "next_condition": "60,681-60,883 へ戻り、15分足で再失速するなら候補",
                    },
                },
            },
            ensure_ascii=False,
        )

    def _write_trades_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        path = base_dir / "logs" / "csv" / "trades.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "signal_id",
            "timestamp_jst",
            "current_price",
            "active_primary_action",
            "active_subject_label",
            "active_headline",
            "active_trade_plan_json",
        ]
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        return path

    def _read_candidates(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", newline="", encoding="utf-8") as fp:
            return list(csv.DictReader(fp))

    def test_active_plan_paper_candidate_header_contains_expected_columns(self) -> None:
        expected = [
            "candidate_id",
            "source_signal_id",
            "timestamp_jst",
            "active_primary_action",
            "candidate_type",
            "candidate_status",
            "side",
            "entry_mode",
            "entry_price",
            "entry_zone_low",
            "entry_zone_high",
            "stop_loss",
            "tp1",
            "tp2",
            "rr_current_tp1",
            "rr_current_tp2",
            "rr_zone_mid_tp1",
            "rr_zone_mid_tp2",
            "market_entry_status",
            "limit_entry_status",
            "counter_scalp_status",
            "breakout_status",
            "active_subject_label",
            "active_headline",
            "next_condition",
        ]
        self.assertEqual(ACTIVE_PLAN_PAPER_CANDIDATE_HEADER, expected)

    def test_build_active_plan_paper_candidates_extracts_limit_and_counter_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "current_price": "60513.0",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                        "active_subject_label": "戻り売り待ち・短期反発注意",
                        "active_headline": "下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。",
                        "active_trade_plan_json": self._active_plan_json(),
                    }
                ],
            )

            output_csv = build_active_plan_paper_candidates(base_dir=base_dir)
            rows = self._read_candidates(output_csv)

        self.assertEqual(len(rows), 3)
        candidate_types = sorted(row["candidate_type"] for row in rows)
        self.assertEqual(candidate_types, ["active_counter_scalp", "active_limit_retest", "active_limit_retest"])

        by_id = {row["candidate_id"]: row for row in rows}
        self.assertIn("s1:active_limit_retest:short", by_id)
        self.assertIn("s1:active_limit_retest:long", by_id)
        self.assertIn("s1:active_counter_scalp:long", by_id)

        short_limit = by_id["s1:active_limit_retest:short"]
        self.assertEqual(short_limit["side"], "short")
        self.assertEqual(short_limit["entry_mode"], "limit_zone_mid")
        self.assertEqual(short_limit["candidate_status"], "candidate")
        self.assertEqual(short_limit["entry_price"], "60781.85")
        self.assertEqual(short_limit["active_subject_label"], "戻り売り待ち・短期反発注意")
        self.assertIn("再失速", short_limit["next_condition"])

        long_counter = by_id["s1:active_counter_scalp:long"]
        self.assertEqual(long_counter["side"], "long")
        self.assertEqual(long_counter["entry_mode"], "market_conditional")
        self.assertEqual(long_counter["candidate_status"], "conditional")
        self.assertIn("反発継続", long_counter["next_condition"])

    def test_build_active_plan_paper_candidates_extracts_market_candidate(self) -> None:
        active_plan = json.loads(self._active_plan_json())
        active_plan["primary_action"] = "ACTIVE_MARKET_SMALL"
        active_plan["side_plans"]["short"]["market_entry_status"] = "allowed"
        active_plan["side_plans"]["short"]["limit_entry_status"] = "blocked"
        active_plan["side_plans"]["long"]["limit_entry_status"] = "blocked"
        active_plan["side_plans"]["long"]["counter_scalp_status"] = "blocked"

        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "current_price": "60750.0",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "active_subject_label": "小ロット成行ショート候補",
                        "active_headline": "成行候補。",
                        "active_trade_plan_json": json.dumps(active_plan, ensure_ascii=False),
                    }
                ],
            )

            output_csv = build_active_plan_paper_candidates(base_dir=base_dir)
            rows = self._read_candidates(output_csv)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["candidate_id"], "s2:active_market_small:short")
        self.assertEqual(rows[0]["candidate_type"], "active_market_small")
        self.assertEqual(rows[0]["entry_mode"], "market")
        self.assertEqual(rows[0]["entry_price"], "60750.0")

    def test_build_active_plan_paper_candidates_ignores_missing_or_malformed_active_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "active_trade_plan_json": "",
                    },
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "active_trade_plan_json": "{malformed",
                    },
                ],
            )

            output_csv = build_active_plan_paper_candidates(base_dir=base_dir)
            rows = self._read_candidates(output_csv)

        self.assertEqual(rows, [])

    def test_build_active_plan_paper_candidates_filters_by_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "old",
                        "timestamp_jst": "2026-06-06T09:05:00+09:00",
                        "current_price": "60513.0",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "active_trade_plan_json": self._active_plan_json(),
                    },
                    {
                        "signal_id": "target",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "current_price": "60513.0",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "active_trade_plan_json": self._active_plan_json(),
                    },
                ],
            )

            output_csv = build_active_plan_paper_candidates(
                base_dir=base_dir,
                date_from="2026-06-07",
                date_to="2026-06-07",
            )
            rows = self._read_candidates(output_csv)

        self.assertTrue(rows)
        self.assertTrue(all(row["source_signal_id"] == "target" for row in rows))

    def test_build_active_plan_paper_candidates_accepts_output_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "current_price": "60513.0",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "active_trade_plan_json": self._active_plan_json(),
                    }
                ],
            )
            output_csv = base_dir / "custom" / "active_plan_candidates.csv"

            result_path = build_active_plan_paper_candidates(base_dir=base_dir, output_csv=output_csv)
            self.assertEqual(result_path, output_csv)
            self.assertTrue(output_csv.exists())


if __name__ == "__main__":
    unittest.main()
