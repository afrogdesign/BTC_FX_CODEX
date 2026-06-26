from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import ACTIVE_PLAN_PAPER_CANDIDATE_HEADER, daily_sync


def _write_active_plan_paper_candidates_csv(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(",".join(ACTIVE_PLAN_PAPER_CANDIDATE_HEADER) + "\n", encoding="utf-8")
    return path


class DailySyncActivePlanCandidatesTests(unittest.TestCase):
    def test_daily_sync_builds_active_plan_paper_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            review_note = base_dir / "review.md"
            output_md = base_dir / "report.md"

            outcomes_path = base_dir / "logs" / "csv" / "signal_outcomes.csv"
            reviews_path = base_dir / "logs" / "csv" / "user_reviews.csv"
            shadow_path = base_dir / "logs" / "csv" / "shadow_log.csv"
            observation_path = base_dir / "logs" / "csv" / "observation_paper_orders.csv"
            phase1b_path = base_dir / "logs" / "csv" / "phase1b_lite_paper_orders.csv"
            paper_positions_path = base_dir / "logs" / "csv" / "paper_positions.csv"
            candidates_path = base_dir / "logs" / "csv" / "active_plan_paper_candidates.csv"
            review_form_path = base_dir / "review_form.html"

            sync_stats = {
                "eligible": 0,
                "reused": 0,
                "created": 0,
                "skipped_existing_ai": 0,
                "skipped_human_override": 0,
                "request_failed": 0,
                "backlog_pending": 0,
                "resolved_cli_fallback": 0,
            }

            _write_active_plan_paper_candidates_csv(candidates_path)

            with (
                patch("tools.log_feedback.update_outcomes", return_value=outcomes_path),
                patch("tools.log_feedback.import_reviews", return_value=reviews_path),
                patch("tools.log_feedback.sync_ai_post_reviews", return_value=(reviews_path, sync_stats)),
                patch("tools.log_feedback.build_shadow_log", return_value=shadow_path),
                patch("tools.log_feedback.build_observation_paper_orders", return_value=observation_path),
                patch("tools.log_feedback.build_phase1b_lite_paper_orders", return_value=phase1b_path),
                patch("tools.log_feedback.build_paper_positions", return_value=paper_positions_path),
                patch("tools.log_feedback.build_active_plan_paper_candidates", return_value=candidates_path) as candidates_mock,
                patch("tools.log_feedback.export_review_queue", return_value=review_note),
                patch("tools.log_feedback._review_form_path", return_value=review_form_path),
                patch("tools.log_feedback._ai_review_health_summary", return_value="ai health ok"),
                patch("tools.log_feedback.build_feedback_report", return_value=None),
            ):
                result = daily_sync(
                    base_dir=base_dir,
                    review_note_path=review_note,
                    output_md=output_md,
                    max_new_reviews=0,
                )

        candidates_mock.assert_called_once_with(
            base_dir=base_dir,
            trades_path=base_dir / "logs" / "csv" / "trades.csv",
        )
        self.assertEqual(result["active_plan_paper_candidates_path"], candidates_path)
        self.assertEqual(result["paper_positions_path"], paper_positions_path)
        self.assertEqual(result["report_path"], output_md)


if __name__ == "__main__":
    unittest.main()
