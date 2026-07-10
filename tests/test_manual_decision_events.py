from __future__ import annotations

import csv
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from src.feedback.manual_decision_events import DECISION_HEADERS, record_manual_decision


class ManualDecisionEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.output = Path(self.tmp.name) / "manual_decisions.csv"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def kwargs(self) -> dict[str, object]:
        return {"scenario_id": "scn_" + "1" * 24, "human_checked_at_jst": "2026-07-10T10:00:00+09:00", "decision_stage": "entry", "human_action": "watched_no_entry", "human_side": "none", "reason_code": ["trigger_missing"], "output_csv": self.output}

    def test_append_and_duplicate_noop(self) -> None:
        first = record_manual_decision(**self.kwargs())
        second = record_manual_decision(**self.kwargs())
        self.assertTrue(first["event_written"])
        self.assertTrue(second["duplicate_event"])
        with self.output.open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(len(rows), 1)
        self.assertEqual((self.output.read_text(encoding="utf-8").splitlines()[0]).split(","), DECISION_HEADERS)

    def test_entered_requires_side_and_stage(self) -> None:
        values = self.kwargs()
        values.update(human_action="entered", human_side="none")
        result = record_manual_decision(**values)
        self.assertEqual(result["exit_code"], 2)

    def test_sensitive_note_and_invalid_number_rejected(self) -> None:
        values = self.kwargs()
        values["manual_note"] = "source_uid_hash leaked"
        self.assertEqual(record_manual_decision(**values)["exit_code"], 2)
        values = self.kwargs()
        values["observed_price"] = "not-a-number"
        self.assertEqual(record_manual_decision(**values)["exit_code"], 2)

    def test_zero_price_is_retained_and_dry_run_does_not_write(self) -> None:
        values = self.kwargs()
        values.update(observed_price="0", planned_entry_price="0", dry_run=True)
        result = record_manual_decision(**values)
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(self.output.exists())

    def test_noncanonical_scenario_id_rejected_without_file(self) -> None:
        values = self.kwargs()
        values["scenario_id"] = "scn_bad"
        self.assertEqual(record_manual_decision(**values)["exit_code"], 2)

    def test_signal_only_decision_is_allowed(self) -> None:
        values = self.kwargs()
        values["scenario_id"] = ""
        values["signal_id"] = "sig-1"
        self.assertEqual(record_manual_decision(**values)["exit_code"], 0)

    def test_unknown_reason_rejected(self) -> None:
        values = self.kwargs()
        values["reason_code"] = ["not-allowed"]
        self.assertEqual(record_manual_decision(**values)["exit_code"], 2)

    def test_note_length_and_line_normalization(self) -> None:
        values = self.kwargs()
        values["manual_note"] = "line1\nline2"
        self.assertEqual(record_manual_decision(**values)["exit_code"], 0)
        values = self.kwargs()
        values["manual_note"] = "x" * 281
        self.assertEqual(record_manual_decision(**values)["exit_code"], 2)

    def test_correction_requires_existing_target(self) -> None:
        values = self.kwargs()
        values["supersedes_decision_event_id"] = "mde_" + "a" * 24
        self.assertEqual(record_manual_decision(**values)["exit_code"], 3)

    def test_valid_correction_and_double_supersede_rejected(self) -> None:
        first = record_manual_decision(**self.kwargs())
        values = self.kwargs()
        values["human_checked_at_jst"] = "2026-07-10T10:01:00+09:00"
        values["supersedes_decision_event_id"] = first["decision_event_id"]
        correction = record_manual_decision(**values)
        self.assertEqual(correction["exit_code"], 0)
        values["human_checked_at_jst"] = "2026-07-10T10:02:00+09:00"
        self.assertEqual(record_manual_decision(**values)["exit_code"], 3)

    def test_existing_malformed_correction_history_fails_closed(self) -> None:
        malformed = {key: "" for key in DECISION_HEADERS}
        malformed.update(schema_version="manual_decision_event.v1", decision_event_id="mde_" + "a" * 24, supersedes_decision_event_id="mde_" + "b" * 24)
        with self.output.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=DECISION_HEADERS); writer.writeheader(); writer.writerow(malformed)
        values = self.kwargs()
        self.assertEqual(record_manual_decision(**values)["exit_code"], 4)

    def test_existing_output_is_preserved_on_write_failure(self) -> None:
        values = self.kwargs()
        original = record_manual_decision(**values)
        before = self.output.read_bytes()
        with patch("src.feedback.manual_decision_events._write", side_effect=OSError("fail")):
            values["human_checked_at_jst"] = "2026-07-10T10:03:00+09:00"
            result = record_manual_decision(**values)
        self.assertEqual(result["exit_code"], 4)
        self.assertEqual(before, self.output.read_bytes())


if __name__ == "__main__":
    unittest.main()
