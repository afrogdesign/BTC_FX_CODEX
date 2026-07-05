from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import main  # noqa: E402


def _runtime_hook_result_payload(
    *,
    was_notified: bool = True,
    signal_id: str = "20260705_050500",
    notification_kind: str = "attention",
    detail_page_status: str = "published",
    summary_subject: str = "[BTCFX Manual Trading Report] 15分足観測",
) -> dict[str, object]:
    return {
        "signal_id": signal_id,
        "timestamp_jst": "2026-07-05T14:05:00.553234+09:00",
        "was_notified": was_notified,
        "notification_kind": notification_kind,
        "detail_page_status": detail_page_status,
        "summary_subject": summary_subject,
        "detail_page_url": "https://server.afrog.jp/btc-monitor/notifications/manual-trading/attention/20260705_050500.html",
        "detail_page_local_path": "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/logs/notifications_html/manual-trading/attention/20260705_050500.html",
        "current_price": 62789.0,
        "bias": "short",
        "primary_setup_side": "short",
        "primary_setup_status": "watch",
        "primary_setup_reason": "confidence_below_min",
        "system_label": "Ver02.6-v2",
        "system_mode_label": "CLI",
        "long_setup": {
            "value_defense_entry_layer": {
                "side": "long",
                "lifecycle_state": "shallow_retest_risk",
                "market_entry_status": "invalid",
                "shallow_retest_zone": {"low": 62723.32, "high": 62801.18},
                "shallow_retest_risk": "high",
                "value_defense_zone": {"low": 62479.84, "high": 62601.29},
                "defense_zone_basis": "next_support_below_shallow_zone",
                "invalidation_zone": {"low": 62532.46, "high": 62551.78},
                "reclaim_trigger": 62662.31,
                "continuation_trigger": 62762.25,
                "operator_guidance": "浅い押し目だけで決め打ちせず、本命押し目と invalidation を先に確認する。",
                "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
            }
        },
        "short_setup": {
            "value_defense_entry_layer": {
                "side": "short",
                "lifecycle_state": "continuation_candidate",
                "market_entry_status": "invalid",
                "shallow_retest_zone": {"low": 62894.24, "high": 62981.47},
                "shallow_retest_risk": "high",
                "value_defense_zone": {"low": 63028.17, "high": 63091.23},
                "defense_zone_basis": "next_resistance_above_shallow_zone",
                "invalidation_zone": {"low": 63153.01, "high": 63172.33},
                "reclaim_trigger": 63004.82,
                "continuation_trigger": 62937.85,
                "operator_guidance": "浅い戻り売りだけで決め打ちせず、本命戻り売りと invalidation を先に確認する。",
                "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
            }
        },
    }


class ValueDefenseObservationRuntimeHookTest(unittest.TestCase):
    def test_helper_writes_snapshot_when_eligible(self) -> None:
        payload = _runtime_hook_result_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            status = main._maybe_write_value_defense_observation_snapshot(payload, base_dir=base_dir)

            out_dir = base_dir / "local" / "value_defense_observation"
            self.assertEqual(status["status"], "written")
            self.assertTrue(status["written"])
            self.assertEqual(status["signal_id"], "20260705_050500")
            self.assertEqual(status["source_file"], str(base_dir / "logs" / "last_result.json"))
            self.assertEqual(status["out_dir"], str(out_dir))
            self.assertTrue((out_dir / "20260705_050500.json").exists())
            self.assertTrue((out_dir / "20260705_050500.md").exists())
            self.assertTrue((out_dir / "latest.json").exists())
            self.assertTrue((out_dir / "latest.md").exists())

            snapshot = json.loads((out_dir / "latest.json").read_text(encoding="utf-8"))
            markdown = (out_dir / "latest.md").read_text(encoding="utf-8")
            self.assertEqual(snapshot["phase4_status"], "blocked_until_observation_review_and_human_approval")
            self.assertIn("report-only / not_FORMAL_GO / no automatic order / human decides manually", markdown)
            self.assertFalse(snapshot["operator_label_status"]["legacy_operator_label_leak_visible"])

    def test_helper_skips_when_not_notified(self) -> None:
        payload = _runtime_hook_result_payload(was_notified=False)
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            status = main._maybe_write_value_defense_observation_snapshot(payload, base_dir=base_dir)

            self.assertEqual(status["status"], "skipped")
            self.assertFalse(status["written"])
            self.assertEqual(status["reason"], "not_eligible")
            self.assertFalse((base_dir / "local" / "value_defense_observation").exists())

    def test_helper_skips_when_signal_id_missing(self) -> None:
        payload = _runtime_hook_result_payload(signal_id="")
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            status = main._maybe_write_value_defense_observation_snapshot(payload, base_dir=base_dir)

            self.assertEqual(status["status"], "skipped")
            self.assertFalse(status["written"])
            self.assertFalse((base_dir / "local" / "value_defense_observation").exists())

    def test_helper_returns_failure_status_when_writer_raises(self) -> None:
        payload = _runtime_hook_result_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            with mock.patch.object(
                main,
                "write_value_defense_observation_snapshot",
                side_effect=RuntimeError("boom"),
            ):
                status = main._maybe_write_value_defense_observation_snapshot(payload, base_dir=base_dir)

            self.assertEqual(status["status"], "failed")
            self.assertFalse(status["written"])
            self.assertIn("boom", status["error"])
            self.assertEqual(status["signal_id"], "20260705_050500")


if __name__ == "__main__":
    unittest.main()
