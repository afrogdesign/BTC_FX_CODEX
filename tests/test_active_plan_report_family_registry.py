from __future__ import annotations

import unittest
from pathlib import Path

from tools.log_feedback import REPORT_FAMILY_SPECS


def _spec_by_name() -> dict[str, dict[str, object]]:
    return {str(spec.get("name", "")): spec for spec in REPORT_FAMILY_SPECS}


class ActivePlanReportFamilyRegistryTests(unittest.TestCase):
    def test_active_plan_report_families_are_registered(self) -> None:
        specs = _spec_by_name()

        expected_names = [
            "active_trade_plan_diagnostics",
            "active_trade_plan_effectiveness",
            "active_plan_candidate_outcomes",
        ]

        for name in expected_names:
            with self.subTest(name=name):
                self.assertIn(name, specs)

    def test_active_plan_report_family_patterns_are_fixed(self) -> None:
        specs = _spec_by_name()

        expected = {
            "active_trade_plan_diagnostics": {
                "pattern": "active_trade_plan_diagnostics_*.md",
                "date_pattern": r"active_trade_plan_diagnostics_(\d{8})\.md$",
            },
            "active_trade_plan_effectiveness": {
                "pattern": "active_trade_plan_effectiveness_*.md",
                "date_pattern": r"active_trade_plan_effectiveness_(\d{8})\.md$",
            },
            "active_plan_candidate_outcomes": {
                "pattern": "active_plan_candidate_outcomes_*.md",
                "date_pattern": r"active_plan_candidate_outcomes_(\d{8})\.md$",
            },
        }

        for name, values in expected.items():
            with self.subTest(name=name):
                spec = specs[name]
                self.assertEqual(spec.get("pattern"), values["pattern"])
                self.assertEqual(spec.get("date_pattern"), values["date_pattern"])

    def test_active_plan_report_families_are_current_analysis_reports(self) -> None:
        specs = _spec_by_name()
        expected_names = [
            "active_trade_plan_diagnostics",
            "active_trade_plan_effectiveness",
            "active_plan_candidate_outcomes",
        ]

        expected_roots = [
            ("active", Path("運用資料") / "reports" / "analysis"),
            ("archive", Path("運用資料") / "reports" / "archive" / "analysis"),
        ]

        for name in expected_names:
            with self.subTest(name=name):
                spec = specs[name]
                self.assertEqual(spec.get("section"), "current")
                self.assertEqual(spec.get("search_roots"), expected_roots)

    def test_active_plan_report_families_have_purpose_text(self) -> None:
        specs = _spec_by_name()
        expected_names = [
            "active_trade_plan_diagnostics",
            "active_trade_plan_effectiveness",
            "active_plan_candidate_outcomes",
        ]

        for name in expected_names:
            with self.subTest(name=name):
                self.assertTrue(str(specs[name].get("label", "")).strip())
                self.assertTrue(str(specs[name].get("purpose", "")).strip())


if __name__ == "__main__":
    unittest.main()
