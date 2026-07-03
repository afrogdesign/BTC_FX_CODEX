from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.rr import build_setup  # noqa: E402
from src.analysis.value_defense_entry_layer import build_value_defense_entry_layer  # noqa: E402


class ValueDefenseEntryLayerTests(unittest.TestCase):
    def test_long_example_derives_value_defense_fields(self) -> None:
        payload = build_value_defense_entry_layer(
            side="long",
            price=61330.0,
            atr=100.0,
            setup={
                "status": "ready",
                "entry_zone": {"low": 61467.0, "high": 61555.0},
                "entry_mid": 61511.0,
                "stop_loss": 61209.0,
            },
            support_zones=[
                {"low": 61467.0, "high": 61555.0, "strength": 4},
                {"low": 61280.0, "high": 61350.0, "strength": 7},
            ],
            resistance_zones=[
                {"low": 61864.0, "high": 61920.0, "strength": 5},
                {"low": 62173.0, "high": 62210.0, "strength": 5},
            ],
        )

        self.assertEqual(payload["schema_version"], "value_defense_entry_layer.v1")
        self.assertEqual(payload["side"], "long")
        self.assertEqual(payload["market_entry_status"], "ready")
        self.assertEqual(payload["shallow_retest_zone"], {"low": 61467.0, "high": 61555.0})
        self.assertEqual(payload["value_defense_zone"], {"low": 61280.0, "high": 61350.0})
        self.assertEqual(payload["defense_zone_basis"], "next_support_below_shallow_zone")
        self.assertEqual(payload["invalidation_zone"], {"low": 61201.0, "high": 61217.0})
        self.assertEqual(payload["reclaim_trigger"], 61408.5)
        self.assertEqual(payload["continuation_trigger"], 61511.0)
        self.assertEqual(payload["lifecycle_state"], "defense_zone_touched")
        self.assertEqual(payload["shallow_retest_risk"], "high")
        self.assertIn("report-only", payload["safety_boundary"])
        payload_text = json.dumps(payload, ensure_ascii=False).lower()
        self.assertNotIn('"formal_go": true', payload_text)
        self.assertNotIn('"automatic_order": true', payload_text)

    def test_short_example_derives_mirror_fields(self) -> None:
        payload = build_value_defense_entry_layer(
            side="short",
            price=61890.0,
            atr=100.0,
            setup={
                "status": "watch",
                "entry_zone": {"low": 61580.0, "high": 61650.0},
                "entry_mid": 61615.0,
                "stop_loss": 62020.0,
            },
            support_zones=[
                {"low": 61467.0, "high": 61555.0, "strength": 4},
            ],
            resistance_zones=[
                {"low": 61580.0, "high": 61650.0, "strength": 4},
                {"low": 61864.0, "high": 61910.0, "strength": 7},
                {"low": 62173.0, "high": 62210.0, "strength": 5},
            ],
        )

        self.assertEqual(payload["side"], "short")
        self.assertEqual(payload["shallow_retest_zone"], {"low": 61580.0, "high": 61650.0})
        self.assertEqual(payload["value_defense_zone"], {"low": 61864.0, "high": 61910.0})
        self.assertEqual(payload["defense_zone_basis"], "next_resistance_above_shallow_zone")
        self.assertEqual(payload["invalidation_zone"], {"low": 62012.0, "high": 62028.0})
        self.assertEqual(payload["reclaim_trigger"], 61757.0)
        self.assertEqual(payload["continuation_trigger"], 61615.0)
        self.assertEqual(payload["lifecycle_state"], "defense_zone_touched")
        self.assertEqual(payload["shallow_retest_risk"], "high")

    def test_unknown_side_returns_unresolved_payload(self) -> None:
        payload = build_value_defense_entry_layer(
            side="",
            price=61330.0,
            atr=100.0,
            setup={
                "status": "watch",
                "entry_zone": {"low": 61467.0, "high": 61555.0},
                "entry_mid": 61511.0,
                "stop_loss": 61209.0,
            },
            support_zones=[
                {"low": 61467.0, "high": 61555.0, "strength": 4},
                {"low": 61280.0, "high": 61350.0, "strength": 7},
            ],
            resistance_zones=[
                {"low": 61864.0, "high": 61920.0, "strength": 5},
            ],
        )

        self.assertEqual(payload["side"], "")
        self.assertEqual(payload["lifecycle_state"], "unresolved")
        self.assertEqual(payload["defense_zone_basis"], "side_unknown")
        self.assertEqual(payload["shallow_retest_risk"], "unresolved")
        self.assertIsNone(payload["value_defense_zone"])
        self.assertIsNone(payload["invalidation_zone"])
        self.assertIsNone(payload["reclaim_trigger"])
        self.assertEqual(payload["continuation_trigger"], 61511.0)
        self.assertIn("report-only", payload["safety_boundary"])
        self.assertIn("未確定", payload["operator_guidance"])

    def test_build_setup_includes_value_defense_entry_layer_without_status_change(self) -> None:
        setup, flags = build_setup(
            side="long",
            price=61567.0,
            atr=100.0,
            support_zones=[
                {"low": 61467.0, "high": 61555.0, "strength": 4},
                {"low": 61280.0, "high": 61350.0, "strength": 7},
            ],
            resistance_zones=[
                {"low": 61864.0, "high": 61920.0, "strength": 5},
                {"low": 62173.0, "high": 62210.0, "strength": 5},
            ],
            sl_atr_multiplier=1.5,
            min_rr_ratio=1.0,
            confidence=80,
            confidence_min=45,
            atr_ratio=1.0,
            atr_ratio_min=0.25,
            atr_ratio_max=2.4,
            funding_rate=0.0,
            funding_warning=999.0,
            funding_prohibited=999.0,
            trigger_ready=True,
            warning_count=0,
        )

        self.assertEqual(setup["status"], "watch")
        self.assertEqual(setup["status_reason_code"], "near_entry_zone_waiting_trigger")
        self.assertEqual(flags, [])
        self.assertIn("value_defense_entry_layer", setup)
        self.assertEqual(setup["value_defense_entry_layer"]["schema_version"], "value_defense_entry_layer.v1")
        self.assertEqual(setup["value_defense_entry_layer"]["market_entry_status"], "watch")
        self.assertIn("report-only", setup["value_defense_entry_layer"]["safety_boundary"])
        setup_text = json.dumps(setup["value_defense_entry_layer"], ensure_ascii=False).lower()
        self.assertNotIn('"formal_go": true', setup_text)
        self.assertNotIn('"automatic_order": true', setup_text)


if __name__ == "__main__":
    unittest.main()
