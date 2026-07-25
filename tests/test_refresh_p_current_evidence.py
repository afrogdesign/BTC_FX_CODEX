import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from datetime import datetime, timezone
from tools.refresh_p_current_evidence import _collapse_snapshots, _head, refresh


class RefreshCurrentEvidenceTests(unittest.TestCase):
    @staticmethod
    def accepted(rows_by_date):
        result = []
        for date, rows in rows_by_date:
            result.append({"date": date, "path": None, "manifest": {}})
        return result

    def test_trial_snapshot_revision_selects_latest_without_double_count(self):
        accepted = [{"date": "20260711", "path": None}, {"date": "20260712", "path": None}]
        import tempfile, csv
        with tempfile.TemporaryDirectory() as td:
            for date, outcome in (("20260711", "pending"), ("20260712", "not_entered")):
                path = Path(td) / date; path.mkdir()
                with (path / "facts.csv").open("w", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["trial_fact_id","scenario_id","scenario_event_id","signal_id","candidate_id","event_timestamp_utc","side","setup_family","classifier_method_version","outcome_status"]); writer.writeheader(); writer.writerow({"trial_fact_id":"tf1","scenario_id":"sc1","scenario_event_id":"se1","signal_id":"s1","candidate_id":"c1","event_timestamp_utc":"2026-07-10T00:00:00Z","side":"long","setup_family":"x","classifier_method_version":"v1","outcome_status":outcome})
            for item in accepted: item["path"] = Path(td) / item["date"]
            rows, meta, _, stats = _collapse_snapshots(accepted, "facts.csv", "daily_trial_facts", "proxy_trial_fact", datetime(2026, 7, 24, tzinfo=timezone.utc))
            self.assertEqual(len(rows), 1); self.assertEqual(rows[0]["outcome_status"], "not_entered"); self.assertEqual(stats["snapshot_revised_identity_count"], 1); self.assertEqual(stats["snapshot_superseded_row_count"], 1); self.assertEqual(meta["row_count"], 1)

    def test_snapshot_versions_stay_separate_and_anchor_conflict_fails(self):
        import tempfile, csv
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "20260724"; path.mkdir()
            fields=["classification_id","source_signal_id","candidate_id","event_timestamp_utc","side","classifier_method_version","operator_class"]
            with (path / "classes.csv").open("w", newline="") as handle:
                writer=csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerow({"classification_id":"c1","source_signal_id":"s1","candidate_id":"x","event_timestamp_utc":"2026-07-10T00:00:00Z","side":"long","classifier_method_version":"v1","operator_class":"A"}); writer.writerow({"classification_id":"c1","source_signal_id":"s1","candidate_id":"x","event_timestamp_utc":"2026-07-10T00:00:00Z","side":"long","classifier_method_version":"v4","operator_class":"B"})
            accepted=[{"date":"20260724","path":path}]; rows, _, _, stats=_collapse_snapshots(accepted,"classes.csv","daily_classifications","classification",datetime(2026,7,24,tzinfo=timezone.utc)); self.assertEqual(len(rows),2); self.assertEqual(stats["selected_snapshot_row_count"],2)
            path2 = Path(td) / "20260725"; path2.mkdir(); raw = (path / "classes.csv").read_text(); (path2 / "classes.csv").write_text(raw.replace(",long,v4,", ",short,v4,"))
            with self.assertRaisesRegex(ValueError,"snapshot_immutable_anchor_conflict"):
                _collapse_snapshots([{"date":"20260724","path":path},{"date":"20260725","path":path2}],"classes.csv","daily_classifications","classification",datetime(2026,7,25,tzinfo=timezone.utc))
    def test_incomplete_selected_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); day = root / "logs/p8_operating_cycles/20260724"; day.mkdir(parents=True)
            (day / "cycle_manifest.json").write_text(json.dumps({"source": {"max_timestamp": "2026-07-24T00:00:00Z"}}))
            with self.assertRaisesRegex(ValueError, "selected_current_directory_incomplete"):
                refresh(root, root / "logs/p8_operating_cycles", root / "out", "Ver04-v5", "a" * 40)

    def test_source_head_override_is_recorded_and_invalid_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); day = root / "logs/p8_operating_cycles/20260724"; day.mkdir(parents=True)
            manifest = {"source": {"max_timestamp": "2026-07-24T00:00:00Z"}}
            (day / "cycle_manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "invalid_source_head"):
                _head(root, "not-a-head")


if __name__ == "__main__":
    unittest.main()
