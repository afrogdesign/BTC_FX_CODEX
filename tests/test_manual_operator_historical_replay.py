from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.feedback.manual_operator_classifier import OUTPUT_HEADERS
from src.feedback.manual_operator_historical_replay import REPLAY_HEADERS, build_manual_operator_historical_replay
from src.feedback.manual_decision_events import DECISION_HEADERS
from src.feedback.manual_trade_episode_builder import EPISODE_HEADERS
from src.feedback.manual_trade_signal_linker import LINK_HEADERS
from src.feedback.manual_scenario_normalizer import EVENT_HEADERS, SCENARIO_HEADERS


class HistoricalReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, headers: list[str], rows: list[dict[str, str]]) -> Path:
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=headers); writer.writeheader(); writer.writerows(rows)
        return path

    def fixtures(self, operator: str = "A_FORMAL", outcome: str = "tp1_first") -> dict[str, Path]:
        sid = "scn_" + "1" * 24
        scenario = {key: "" for key in SCENARIO_HEADERS}; scenario.update(schema_version="manual_scenario.v1", scenario_id=sid, symbol="BTCUSDT", side="long", setup_family="limit_retest", scenario_status="resolved", lifecycle_state="proxy_resolved", proxy_outcome=outcome)
        event = {key: "" for key in EVENT_HEADERS}; event.update(schema_version="manual_scenario_event.v1", scenario_event_id="sce_" + "1" * 24, scenario_id=sid, candidate_id="c1", source_signal_id="sig1", event_timestamp_utc="2026-07-10T00:00:00Z", event_timestamp_jst="2026-07-10T09:00:00+09:00", grouping_status="new_scenario", symbol="BTCUSDT", side="long", setup_family="limit_retest", intraperiod_outcome=outcome, first_exit_reason=outcome)
        cls = {key: "" for key in OUTPUT_HEADERS}; cls.update(schema_version="manual_operator_classification.v1", classification_id="opc_" + "1" * 24, classifier_method_version="manual_operator_classifier.v1", scenario_event_id=event["scenario_event_id"], scenario_id=sid, candidate_id="c1", source_signal_id="sig1", event_timestamp_utc=event["event_timestamp_utc"], event_timestamp_jst=event["event_timestamp_jst"], symbol="BTCUSDT", side="long", setup_family="limit_retest", classification_status="classified", operator_class=operator, trade_execution_gate="pass" if operator == "A_FORMAL" else "blocked", primary_setup_status="ready", primary_setup_side="long", short_direction_min="55", short_execution_min="18", short_wait_max="75", short_tp1_rr_min="0.8", short_tp2_rr_min="1.5", long_direction_min="60", long_execution_min="22", long_wait_max="70", long_tp1_rr_min="1.0", long_tp2_rr_min="1.8")
        return {"scenarios": self.write("scenarios.csv", SCENARIO_HEADERS, [scenario]), "events": self.write("events.csv", EVENT_HEADERS, [event]), "classifications": self.write("classifications.csv", OUTPUT_HEADERS, [cls])}

    def build(self, fx: dict[str, Path], **kwargs: object) -> dict[str, object]:
        return build_manual_operator_historical_replay(scenarios=fx["scenarios"], scenario_events=fx["events"], classifications=fx["classifications"], output_csv=self.root / "replay.csv", output_json=self.root / "replay.json", output_md=self.root / "replay.md", report_date="20260710", **kwargs)

    def decision(self, *, scenario_id: str = "scn_" + "1" * 24, signal_id: str = "", checked: str = "2026-07-10T01:00:00Z", event_id: str = "dec_1", action: str = "watched_no_entry", status: str = "active", target: str = "") -> dict[str, str]:
        row = {key: "" for key in DECISION_HEADERS}; row.update(schema_version="manual_decision_event.v1", decision_event_id=event_id, identity_scope="scenario" if scenario_id else "signal_only", scenario_id=scenario_id, signal_id=signal_id, human_checked_at_utc=checked, human_checked_at_jst=checked, human_action=action, decision_stage="entry", human_side="none", record_status=status, supersedes_decision_event_id=target)
        return row

    def episode_inputs(self, *, status: str = "closed", realized: str = "10", fee: str = "2", opened: str = "2026-07-10T00:30:00Z", closed: str = "2026-07-10T01:30:00Z", confidence: str = "high", signal: str = "sig1") -> tuple[Path, Path]:
        episode = {key: "" for key in EPISODE_HEADERS}; episode.update(schema_version="manual_trade_episode.v1", episode_id="ep1", position_id="pos1", symbol="BTCUSDT", side="long", opened_at_utc=opened, closed_at_utc=closed, status=status, realized_pnl=realized, fee_total=fee, association_status="matched")
        link = {key: "" for key in LINK_HEADERS}; link.update(schema_version="manual_trade_signal_link.v2", link_id="ln1", episode_id="ep1", signal_id=signal, link_confidence=confidence, link_status="linked", side_compatibility="match", symbol_compatibility="match")
        return self.write("episodes.csv", EPISODE_HEADERS, [episode]), self.write("links.csv", LINK_HEADERS, [link])

    def test_policy_selection_and_proxy_outcome(self) -> None:
        fx = self.fixtures(); result = self.build(fx)
        self.assertTrue(result["ok"])
        self.assertEqual(result["policy_summaries"]["A_ONLY"]["selected_scenario_rows"], 1)
        self.assertEqual(result["policy_summaries"]["A_ONLY"]["resolved_positive_rows"], 1)
        with (self.root / "replay.csv").open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(rows[0]["selected_scenario_event_id"], "sce_" + "1" * 24)

    def test_c_observe_and_stop_overlay(self) -> None:
        fx = self.fixtures(operator="C_WATCH_ZONE"); result = self.build(fx)
        self.assertEqual(result["policy_summaries"]["A_PLUS_B_PLUS_C_OBSERVE"]["observe_only_rows"], 1)
        self.assertEqual(result["policy_summaries"]["A_PLUS_B_PLUS_C_OBSERVE"]["resolved_positive_rows"], 0)
        fx = self.fixtures(operator="STOP_OR_EXIT", outcome="sl_first"); result = self.build(fx)
        self.assertEqual(result["policy_summaries"]["STOP_OVERLAY"]["selected_scenario_rows"], 1)
        self.assertEqual(result["policy_summaries"]["STOP_OVERLAY"]["entry_candidate_rows"], 0)

    def test_validation_optional_pair_dry_run_and_determinism(self) -> None:
        fx = self.fixtures(); self.assertEqual(self.build(fx, trade_episodes=self.root / "episodes.csv")["exit_code"], 2)
        first = self.build(fx); bytes1 = tuple((self.root / name).read_bytes() for name in ("replay.csv", "replay.json", "replay.md")); second = self.build(fx); self.assertEqual(first["ok"], second["ok"]); self.assertEqual(bytes1, tuple((self.root / name).read_bytes() for name in ("replay.csv", "replay.json", "replay.md")))
        dry = self.build(fx, dry_run=True); self.assertFalse(dry["report_written"])

    def test_cli_compact_json_and_bad_input(self) -> None:
        fx = self.fixtures(); repo = Path(__file__).resolve().parents[1]
        cmd = [sys.executable, str(repo / "tools/log_feedback.py"), "build-manual-operator-historical-replay", "--scenarios", str(fx["scenarios"]), "--scenario-events", str(fx["events"]), "--classifications", str(fx["classifications"]), "--output-csv", str(self.root / "cli.csv"), "--output-json", str(self.root / "cli.json"), "--output-md", str(self.root / "cli.md"), "--date", "20260710", "--stdout-json"]
        ok = subprocess.run(cmd, cwd=repo, text=True, capture_output=True); self.assertEqual(ok.returncode, 0); self.assertEqual(len(ok.stdout.strip().splitlines()), 1); self.assertTrue(json.loads(ok.stdout)["ok"]); self.assertNotIn("Traceback", ok.stderr); self.assertNotIn(str(self.root), ok.stdout)
        bad = subprocess.run([*cmd[:cmd.index("--scenarios")], "--scenarios", str(self.root / "missing"), *cmd[cmd.index("--scenario-events"):]], cwd=repo, text=True, capture_output=True); self.assertNotEqual(bad.returncode, 0); self.assertNotIn("Traceback", bad.stderr)

    def test_timestamp_threshold_and_mfe_validation(self) -> None:
        fx = self.fixtures()
        with fx["classifications"].open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        row["long_direction_min"] = "NaN"; fx["classifications"] = self.write("bad-threshold.csv", OUTPUT_HEADERS, [row])
        self.assertEqual(self.build(fx)["exit_code"], 2)
        fx = self.fixtures()
        with fx["events"].open(newline="", encoding="utf-8") as fp:
            event = next(csv.DictReader(fp))
        event["mfe_r"] = "Infinity"; fx["events"] = self.write("bad-mfe.csv", EVENT_HEADERS, [event])
        self.assertEqual(self.build(fx)["exit_code"], 2)

    def test_existing_output_schema_is_fail_closed(self) -> None:
        fx = self.fixtures(); self.build(fx)
        (self.root / "replay.json").write_text('{"schema_version":"wrong"}\n', encoding="utf-8")
        self.assertEqual(self.build(fx)["exit_code"], 4)

    def test_classification_duplicate_and_status_integrity(self) -> None:
        fx = self.fixtures(); rows = list(csv.DictReader(fx["classifications"].open(newline="", encoding="utf-8")))
        fx["classifications"] = self.write("dup-identical.csv", OUTPUT_HEADERS, [rows[0], rows[0]]); self.assertEqual(self.build(fx)["exit_code"], 2)
        rows = [dict(rows[0]), dict(rows[0])]; rows[1]["operator_class"] = "C_WATCH_ZONE"; fx["classifications"] = self.write("dup-conflict.csv", OUTPUT_HEADERS, rows); self.assertEqual(self.build(fx)["exit_code"], 3)
        fx = self.fixtures(); rows = list(csv.DictReader(fx["classifications"].open(newline="", encoding="utf-8"))); rows[0]["classification_status"] = "insufficient_evidence"; rows[0]["operator_class"] = "A_FORMAL"; fx["classifications"] = self.write("bad-status.csv", OUTPUT_HEADERS, rows); self.assertEqual(self.build(fx)["exit_code"], 2)

    def test_scenario_event_duplicate_assignment(self) -> None:
        fx = self.fixtures(); event = list(csv.DictReader(fx["events"].open(newline="", encoding="utf-8")))[0]; fx["events"] = self.write("dup-events.csv", EVENT_HEADERS, [event, event]); fx["classifications"] = self.write("dup-classes.csv", OUTPUT_HEADERS, [next(csv.DictReader(fx["classifications"].open(newline="", encoding="utf-8")))] * 2); self.assertEqual(self.build(fx)["exit_code"], 2)
        event2 = dict(event); event2["candidate_id"] = "other"; fx["events"] = self.write("conf-events.csv", EVENT_HEADERS, [event, event2]); self.assertEqual(self.build(fx)["exit_code"], 3)

    def test_duplicate_classification_assignment_different_ids(self) -> None:
        fx = self.fixtures(); base = next(csv.DictReader(fx["classifications"].open(newline="", encoding="utf-8"))); duplicate = dict(base); duplicate["classification_id"] = "opc_" + "2" * 24; fx["classifications"] = self.write("same-assignment.csv", OUTPUT_HEADERS, [base, duplicate]); self.assertEqual(self.build(fx)["exit_code"], 2)
        duplicate["operator_class"] = "C_WATCH_ZONE"; fx["classifications"] = self.write("different-assignment.csv", OUTPUT_HEADERS, [base, duplicate]); self.assertEqual(self.build(fx)["exit_code"], 3)

    def test_multiple_correction_targets_rejected(self) -> None:
        fx = self.fixtures(); decisions = [self.decision(event_id="base"), self.decision(event_id="c1", status="correction", target="base"), self.decision(event_id="c2", status="correction", target="base")]; path = self.write("decisions.csv", DECISION_HEADERS, decisions); self.assertEqual(self.build(fx, decision_events=path)["exit_code"], 2)

    def test_decision_earliest_signal_only_preselection_ambiguous_orphan(self) -> None:
        fx = self.fixtures(); decisions = [self.decision(event_id="late", checked="2026-07-10T03:00:00Z", action="skipped"), self.decision(event_id="early", checked="2026-07-10T01:00:00Z", action="entered"), self.decision(scenario_id="", signal_id="sig1", event_id="signal", checked="2026-07-10T02:00:00Z", action="exited"), self.decision(scenario_id="", signal_id="other", event_id="orphan", checked="2026-07-10T02:00:00Z")]; path = self.write("decisions.csv", DECISION_HEADERS, decisions); result = self.build(fx, decision_events=path); self.assertEqual(result["decision_summary"]["policy_metrics"]["A_ONLY"]["entered_rows"], 1); self.assertGreaterEqual(result["decision_summary"]["policy_metrics"]["A_ONLY"]["orphan_decision_rows"], 1)

    def test_actual_stop_c_blank_signal_and_bad_episode(self) -> None:
        fx = self.fixtures(operator="STOP_OR_EXIT"); episodes, links = self.episode_inputs(); result = self.build(fx, trade_episodes=episodes, episode_links=links); self.assertEqual(result["actual_summary"]["policy_summaries"]["STOP_OVERLAY"]["actual_linked_episode_count"], 0)
        fx = self.fixtures(); episodes, links = self.episode_inputs(opened="bad"); self.assertEqual(self.build(fx, trade_episodes=episodes, episode_links=links)["exit_code"], 2)
        episodes, _ = self.episode_inputs(); blank = {key: "" for key in LINK_HEADERS}; blank.update(schema_version="manual_trade_signal_link.v2", link_id="ln2", episode_id="ep1", link_status="unmatched"); links = self.write("blank-link.csv", LINK_HEADERS, [blank]); self.assertEqual(self.build(fx, trade_episodes=episodes, episode_links=links)["exit_code"], 0)

    def test_actual_policy_metrics_and_markdown(self) -> None:
        fx = self.fixtures(); episodes, links = self.episode_inputs(realized="10", fee="2"); result = self.build(fx, trade_episodes=episodes, episode_links=links); summary = result["actual_summary"]["policy_summaries"]["A_ONLY"]; self.assertEqual(summary["actual_net_pnl_after_fee"], "8"); self.assertEqual(summary["actual_wins"], 1); self.assertIn("Human Decision Evidence", (self.root / "replay.md").read_text(encoding="utf-8")); self.assertIn("Actual Trade Evidence", (self.root / "replay.md").read_text(encoding="utf-8"))

    def test_actual_summary_contract_keys_and_open_episode(self) -> None:
        fx = self.fixtures(); episodes, links = self.episode_inputs(status="open", realized="10", fee="2", closed=""); result = self.build(fx, trade_episodes=episodes, episode_links=links); summary = result["actual_summary"]["policy_summaries"]["A_ONLY"]; self.assertEqual(summary["actual_gross_realized_pnl"], "0"); self.assertEqual(summary["actual_net_pnl_after_fee"], "0"); self.assertEqual(set(summary), {"actual_linked_episode_count", "actual_high_confidence_episode_count", "actual_medium_confidence_episode_count", "actual_gross_realized_pnl", "actual_fee_covered_episode_count", "actual_fee_missing_episode_count", "actual_net_pnl_after_fee", "actual_wins", "actual_losses", "actual_breakeven", "actual_profit_factor"})


if __name__ == "__main__": unittest.main()
