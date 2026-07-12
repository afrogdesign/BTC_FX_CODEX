from __future__ import annotations

import json
import unittest
from pathlib import Path

from main import _attach_side_aware_mtf_action


class SideAwareMtfActionIntegrationTests(unittest.TestCase):
    def test_canonical_result_assembly_attaches_complete_report_only_action(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = json.loads((root / "logs/signals/20260712_040500.json").read_text())
        _attach_side_aware_mtf_action(result, previous=None)
        action = result["side_aware_mtf_action"]
        self.assertEqual(action["schema_version"], "side_aware_mtf_action.v1")
        self.assertEqual(action["execution_context"]["primary_side"], "short")
        self.assertEqual(result["bias"], "long")
        self.assertEqual(result["trade_execution_gate"], "blocked")


if __name__ == "__main__":
    unittest.main()
