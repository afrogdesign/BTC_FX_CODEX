from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.support_resistance import (
    build_all_support_resistance,
    build_support_resistance,
    select_nearest_directional_zones,
    sort_zones_by_distance,
)


def _mock_df() -> pd.DataFrame:
    rows = []
    base_ts = 1_700_000_000_000
    for i in range(20):
        rows.append(
            {
                "timestamp": base_ts + i * 60_000,
                "open": 70000 + i,
                "high": 70100 + i,
                "low": 69900 + i,
                "close": 70000 + i,
                "volume": 10 + i,
            }
        )
    return pd.DataFrame(rows)


class SupportResistanceTest(unittest.TestCase):
    def test_all_and_top3_are_separated(self) -> None:
        df = _mock_df()
        swings = {
            "lows": [{"price": p} for p in [62000, 64000, 66000, 68000, 70000]],
            "highs": [{"price": p} for p in [71000, 73000, 75000, 77000, 79000]],
        }
        per_tf_inputs = {
            "4h": {"df": df, "swings": swings},
            "1h": {"df": df, "swings": swings},
        }
        all_support, all_resistance = build_all_support_resistance(per_tf_inputs, 100.0)
        top_support, top_resistance = build_support_resistance(per_tf_inputs, 100.0)
        self.assertGreaterEqual(len(all_support), 5)
        self.assertGreaterEqual(len(all_resistance), 5)
        self.assertEqual(len(top_support), 3)
        self.assertEqual(len(top_resistance), 3)

    def test_sort_zones_by_distance_has_distance_key(self) -> None:
        zones = [
            {"low": 69000.0, "high": 69200.0, "strength": 3},
            {"low": 70500.0, "high": 70700.0, "strength": 5},
            {"low": 70050.0, "high": 70100.0, "strength": 1},
        ]
        sorted_zones = sort_zones_by_distance(70080.0, zones)
        self.assertEqual(sorted_zones[0]["low"], 70050.0)
        self.assertIn("distance_from_price", sorted_zones[0])

    def test_select_nearest_directional_zones_filters_by_side(self) -> None:
        support_zones = [
            {"low": 69600.0, "high": 69850.0, "strength": 12},
            {"low": 70190.0, "high": 70320.0, "strength": 10},
            {"low": 69270.0, "high": 69400.0, "strength": 6},
        ]
        resistance_zones = [
            {"low": 69930.0, "high": 70210.0, "strength": 45},
            {"low": 69370.0, "high": 69540.0, "strength": 24},
            {"low": 70260.0, "high": 70390.0, "strength": 11},
        ]

        nearest_support = select_nearest_directional_zones(69883.7, support_zones, "support")
        nearest_resistance = select_nearest_directional_zones(69883.7, resistance_zones, "resistance")

        self.assertEqual([zone["low"] for zone in nearest_support], [69600.0, 69270.0])
        self.assertEqual([zone["low"] for zone in nearest_resistance], [69930.0, 70260.0])


if __name__ == "__main__":
    unittest.main()
