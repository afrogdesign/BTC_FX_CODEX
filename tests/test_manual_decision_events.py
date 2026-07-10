from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.feedback.manual_decision_events import DECISION_HEADERS, record_manual_decision


class ManualDecisionEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.output = Path(self.tmp.name) / "manual_decisions.csv"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def kwargs(self) -> dict[str, object]:
        return {"scenario_id": "scn_1", "human_checked_at_jst": "2026-07-10T10:00:00+09:00", "decision_stage": "entry", "human_action": "watched_no_entry", "human_side": "none", "reason_code": ["trigger_missing"], "output_csv": self.output}

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


if __name__ == "__main__":
    unittest.main()
