from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
import unittest
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = BASE_DIR / "tools"
for candidate in (str(BASE_DIR), str(TOOLS_DIR)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import build_value_defense_observation_snapshot as snapshot_tool  # noqa: E402


def _fixture_result(
    *,
    summary_subject: str = "[BTCFX Manual Trading Report] 👀 [注意報・売買非推奨] 下方向監視 | 下方向への転換を確認 【BTC:62,789】 2026-07-05 14:05",
    system_label: str = "Ver04-v2",
    signal_id: str = "20260705_050500",
    timestamp_jst: str = "2026-07-05T14:05:00.553234+09:00",
    notification_kind: str = "attention",
    detail_page_status: str = "published",
    was_notified: bool = True,
    detail_page_url: str = "https://server.afrog.jp/btc-monitor/notifications/manual-trading/attention/20260705_050500.html",
    detail_page_local_path: str = "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/logs/notifications_html/manual-trading/attention/20260705_050500.html",
) -> dict[str, object]:
    return {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "notification_kind": notification_kind,
        "detail_page_status": detail_page_status,
        "detail_page_url": detail_page_url,
        "detail_page_local_path": detail_page_local_path,
        "summary_subject": summary_subject,
        "current_price": 62789.0,
        "bias": "short",
        "primary_setup_side": "short",
        "primary_setup_status": "watch",
        "primary_setup_reason": "confidence_below_min",
        "was_notified": was_notified,
        "system_label": system_label,
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


def _write_self_review_current_artifact(base_dir: Path) -> Path:
    payload = {
        "schema_version": "judgment_self_review.v1",
        "report_fingerprint": "jsr_test_1234567890ab",
        "review_queue_count": 10,
        "change_readiness": {
            "change_readiness_status": "observe_more",
            "change_readiness_level": "low",
            "human_approval_required": "yes",
            "tuning_review_allowed": "no",
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
        },
        "run_metadata": {
            "report_fingerprint": "jsr_test_runmeta_abcdef12",
        },
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }
    path = base_dir / "local" / "self_review_current_check" / "self_review_current.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _attack_review_fixture_result() -> dict[str, object]:
    result = _fixture_result()
    result.update(
        {
            "current_price": 63350.0,
            "market_map_primary_state": "transition_early_up",
            "market_map_flags": ["resistance_to_support_flip", "resistance_to_support_retest_confirmed"],
            "active_level_role": "runner_setup",
            "level_flip_state": "resistance_to_support",
            "failed_breakout_state": "trend_flip",
            "trend_flip_state": "trend_flip",
            "transition_direction": "up",
            "bias": "long",
        }
    )
    return result


class ValueDefenseObservationSnapshotTest(unittest.TestCase):
    def test_dry_run_stdout_json_does_not_write_files(self) -> None:
        result = _fixture_result()
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "result.json"
            input_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            out_dir = Path(tmp_dir) / "snapshot"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = snapshot_tool.main(
                    [
                        "--input",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                        "--dry-run",
                        "--stdout-json",
                        "--signal-id",
                        "20260705_050500",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["schema_version"], "value_defense_observation_snapshot.v1")
            self.assertEqual(payload["operator_label_status"]["html_title_expected"], "BTCFX Manual Trading Report")
            self.assertEqual(payload["operator_label_status"]["path_slug_expected"], "manual-trading")
            self.assertFalse(payload["operator_label_status"]["legacy_operator_label_leak_visible"])
            self.assertEqual(payload["current_price_position_long"], "inside_shallow_retest_zone")
            self.assertEqual(payload["current_price_position_short"], "below_zones")
            self.assertFalse(out_dir.exists())

    def test_dry_run_no_send_input_still_emits_json_without_files(self) -> None:
        result = _fixture_result(
            was_notified=False,
            notification_kind="none",
            detail_page_status="disabled",
            detail_page_url="",
            detail_page_local_path="",
            summary_subject="notification no-send smoke",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "result.json"
            input_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            out_dir = Path(tmp_dir) / "snapshot"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = snapshot_tool.main(
                    [
                        "--input",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                        "--dry-run",
                        "--stdout-json",
                    ]
                )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["notification_kind"], "none")
        self.assertEqual(payload["detail_page_status"], "disabled")
        self.assertFalse(out_dir.exists())

    def test_non_dry_run_no_send_input_refuses_to_write_by_default(self) -> None:
        result = _fixture_result(
            was_notified=False,
            notification_kind="none",
            detail_page_status="disabled",
            detail_page_url="",
            detail_page_local_path="",
            summary_subject="notification no-send smoke",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "result.json"
            input_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            out_dir = Path(tmp_dir) / "snapshot"
            with self.assertRaises(SystemExit) as exc, contextlib.redirect_stderr(io.StringIO()):
                snapshot_tool.main(
                    [
                        "--input",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                    ]
                )

        self.assertNotEqual(exc.exception.code, 0)
        self.assertFalse(out_dir.exists())

    def test_allow_non_notified_permits_writing_no_send_input(self) -> None:
        result = _fixture_result(
            was_notified=False,
            notification_kind="none",
            detail_page_status="disabled",
            detail_page_url="",
            detail_page_local_path="",
            summary_subject="notification no-send smoke",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "result.json"
            input_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            out_dir = Path(tmp_dir) / "snapshot"
            exit_code = snapshot_tool.main(
                [
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--allow-non-notified",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((out_dir / "20260705_050500.json").exists())
            self.assertTrue((out_dir / "latest.json").exists())
            snapshot = json.loads((out_dir / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["notification_kind"], "none")
            self.assertEqual(snapshot["detail_page_status"], "disabled")

    def test_non_dry_run_writes_all_expected_files(self) -> None:
        result = _fixture_result()
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "result.json"
            input_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            out_dir = Path(tmp_dir) / "snapshot"
            exit_code = snapshot_tool.main(
                [
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--signal-id",
                    "20260705_050500",
                ]
            )

            self.assertEqual(exit_code, 0)
            for name in ("20260705_050500.json", "20260705_050500.md", "latest.json", "latest.md"):
                self.assertTrue((out_dir / name).exists(), name)

            snapshot = json.loads((out_dir / "latest.json").read_text(encoding="utf-8"))
            markdown = (out_dir / "latest.md").read_text(encoding="utf-8")
            self.assertEqual(snapshot["operator_label_status"]["legacy_operator_label_leak_visible"], False)
            self.assertIn("Phase4 tuning remains blocked until observation evidence is reviewed and human approval is explicit.", markdown)
            self.assertIn("report-only / not_FORMAL_GO / no automatic order / human decides manually", markdown)

    def test_legacy_operator_leak_uses_only_operator_facing_fields(self) -> None:
        stable_result = _fixture_result(system_label="Ver02.6-v2")
        stable_snapshot = snapshot_tool.build_value_defense_observation_snapshot(
            stable_result, source_file=Path("/tmp/result.json")
        )
        self.assertFalse(stable_snapshot["operator_label_status"]["legacy_operator_label_leak_visible"])

        leaked_result = _fixture_result(summary_subject="[BTCFX Ver04-v2] [API] [CLI] legacy subject")
        leaked_snapshot = snapshot_tool.build_value_defense_observation_snapshot(
            leaked_result, source_file=Path("/tmp/result.json")
        )
        self.assertTrue(leaked_snapshot["operator_label_status"]["legacy_operator_label_leak_visible"])

    def test_markdown_includes_safety_and_phase4_block_line(self) -> None:
        snapshot = snapshot_tool.build_value_defense_observation_snapshot(
            _fixture_result(),
            source_file=Path("/tmp/result.json"),
        )
        markdown = snapshot_tool.render_observation_markdown(snapshot)
        self.assertIn("Phase4 tuning remains blocked until observation evidence is reviewed and human approval is explicit.", markdown)
        self.assertIn("report-only / not_FORMAL_GO / no automatic order / human decides manually", markdown)

    def test_attack_review_flags_are_present_and_compact(self) -> None:
        snapshot = snapshot_tool.build_value_defense_observation_snapshot(
            _attack_review_fixture_result(),
            source_file=Path("/tmp/result.json"),
        )
        flags = snapshot["attack_review_flags"]
        self.assertIsInstance(flags, dict)
        self.assertEqual(flags["schema_version"], "value_defense_attack_review_flags.v1")
        self.assertTrue(flags["review_only"])
        self.assertEqual(flags["phase4_tuning_allowed"], "no")
        self.assertEqual(flags["human_approval_required"], "yes")
        self.assertEqual(flags["safety_boundary"], "report-only / not FORMAL_GO / no automatic order / human decides manually")
        self.assertIn("trend_transition_candidate", flags["watch_tags"])
        self.assertIn("higher_timeframe_reclaim", flags["watch_tags"])
        self.assertIn("breakout_extension_candidate", flags["watch_tags"])
        self.assertIn("tp_too_conservative", flags["watch_tags"])
        self.assertIn("short_invalidated_by_reclaim", flags["watch_tags"])
        self.assertIn("runner_should_have_been_considered", flags["watch_tags"])
        self.assertIn("micro_profit_trap_risk", flags["watch_tags"])
        self.assertIn("trend_transition_candidate", flags["matched_tags"])
        self.assertIn("higher_timeframe_reclaim", flags["matched_tags"])
        self.assertIn("breakout_extension_candidate", flags["matched_tags"])
        self.assertIn("runner_should_have_been_considered", flags["matched_tags"])
        self.assertIn("micro_profit_trap_risk", flags["matched_tags"])
        self.assertIn("short_invalidated_by_reclaim", flags["matched_tags"])
        self.assertEqual(flags["evidence"]["current_price_position_long"], "above_zones")
        self.assertEqual(flags["evidence"]["current_price_position_short"], "above_zones")
        markdown = snapshot_tool.render_observation_markdown(snapshot)
        self.assertIn("## Attack Review Flags", markdown)
        self.assertIn("phase4_tuning_allowed: no", markdown)
        self.assertIn("human_approval_required: yes", markdown)

    def test_missing_self_review_artifact_keeps_none(self) -> None:
        result = _fixture_result()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            logs_dir = base_dir / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            input_path = logs_dir / "last_result.json"
            input_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

            snapshot = snapshot_tool.build_value_defense_observation_snapshot(
                result,
                source_file=input_path,
            )

        self.assertIsNone(snapshot["self_review_readiness"])

    def test_available_self_review_artifact_is_compactly_summarized(self) -> None:
        result = _fixture_result()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            logs_dir = base_dir / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            input_path = logs_dir / "last_result.json"
            input_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            _write_self_review_current_artifact(base_dir)

            snapshot = snapshot_tool.build_value_defense_observation_snapshot(
                result,
                source_file=input_path,
            )
            markdown = snapshot_tool.render_observation_markdown(snapshot)

        readiness = snapshot["self_review_readiness"]
        self.assertIsInstance(readiness, dict)
        self.assertEqual(readiness["schema_version"], "judgment_self_review.v1")
        self.assertEqual(readiness["report_fingerprint"], "jsr_test_1234567890ab")
        self.assertEqual(readiness["run_metadata_fingerprint"], "jsr_test_runmeta_abcdef12")
        self.assertEqual(readiness["review_queue_count"], 10)
        self.assertEqual(readiness["change_readiness_status"], "observe_more")
        self.assertEqual(readiness["change_readiness_level"], "low")
        self.assertEqual(readiness["human_approval_required"], "yes")
        self.assertEqual(readiness["tuning_review_allowed"], "no")
        self.assertEqual(
            readiness["safety_boundary"],
            "report-only / not FORMAL_GO / no automatic order / human decides manually",
        )
        self.assertIn("## Self Review Readiness", markdown)
        self.assertIn("change_readiness_status: observe_more", markdown)
        self.assertIn("tuning_review_allowed: no", markdown)

    def test_signal_guard_mismatch_exits_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "result.json"
            input_path.write_text(json.dumps(_fixture_result(), ensure_ascii=False, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                snapshot_tool.main(
                    [
                        "--input",
                        str(input_path),
                        "--signal-id",
                        "20260705_999999",
                    ]
                )
        self.assertNotEqual(exc.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
