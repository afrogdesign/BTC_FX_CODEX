from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.market_map import _detect_role_flip, build_market_map


class _MiniSeries(list):
    def tolist(self) -> list[float]:
        return list(self)


class _MiniDataFrame:
    def __init__(self, rows: list[dict[str, float]]) -> None:
        self._rows = [dict(row) for row in rows]

    def __getitem__(self, key: str) -> _MiniSeries:
        return _MiniSeries(row[key] for row in self._rows)

    def itertuples(self, index: bool = False) -> object:
        for row in self._rows:
            yield SimpleNamespace(**row)


def _df(rows: list[dict[str, float]]) -> _MiniDataFrame:
    return _MiniDataFrame(rows)


def _flat_rows(price: float, count: int = 24) -> list[dict[str, float]]:
    return [
        {"open": price, "high": price + 0.4, "low": price - 0.4, "close": price, "volume": 10.0}
        for _ in range(count)
    ]


def _inputs(
    *,
    df_15m: _MiniDataFrame,
    support_price: float = 95.0,
    resistance_price: float = 105.0,
    structure_4h: str = "mixed",
    structure_1h: str = "mixed",
    structure_15m: str = "mixed",
    signal_1h: str = "wait",
    signal_15m: str = "wait",
) -> dict[str, dict[str, object]]:
    df_4h = _df(_flat_rows(100.0))
    df_1h = _df(_flat_rows(100.0))
    return {
        "4h": {
            "df": df_4h,
            "swings": {"lows": [{"price": support_price}], "highs": [{"price": resistance_price}]},
            "structure": structure_4h,
            "signal": "wait",
        },
        "1h": {
            "df": df_1h,
            "swings": {"lows": [{"price": support_price + 0.3}], "highs": [{"price": resistance_price - 0.2}]},
            "structure": structure_1h,
            "signal": signal_1h,
        },
        "15m": {
            "df": df_15m,
            "swings": {"lows": [{"price": support_price}], "highs": [{"price": resistance_price}]},
            "structure": structure_15m,
            "signal": signal_15m,
        },
    }


class MarketMapTest(unittest.TestCase):
    def test_historical_break_candidates_bypass_three_nearer_unbroken_levels(self) -> None:
        def level(low: float, high: float, strength: float) -> dict[str, object]:
            return {"low": low, "high": high, "mid": (low + high) / 2, "strength": strength, "source": "15m", "sources": ["15m"], "confluence_count": 1, "reaction_count": 1, "wick_rejections": 0, "volume_touches": 0, "last_touch_age": 0}
        up_rows = _flat_rows(100.0, 16) + [{"open": 100.0, "high": 100.3, "low": 100.0, "close": 100.2, "volume": 10.0}, {"open": 100.2, "high": 100.2, "low": 100.0, "close": 100.05, "volume": 10.0}, {"open": 100.05, "high": 100.2, "low": 100.0, "close": 100.05, "volume": 10.0}]
        state, reference, _ = _detect_role_flip(price=100.05, atr=1.0, supports=[], resistances=[level(99.9, 100.1, 9), level(99.8, 100.12, 8), level(99.7, 100.14, 7), level(100.0, 100.0, 1)], df_15m=_df(up_rows), cfg=SimpleNamespace())
        self.assertEqual(state, "resistance_to_support_confirmed")
        self.assertEqual(reference["high"], 100.0)
        self.assertLess(reference["break_index"], reference["retest_index"])
        self.assertLess(reference["retest_index"], reference["hold_index"])

        down_rows = _flat_rows(100.0, 16) + [{"open": 100.0, "high": 100.0, "low": 99.7, "close": 99.8, "volume": 10.0}, {"open": 99.8, "high": 100.0, "low": 99.8, "close": 99.95, "volume": 10.0}, {"open": 99.95, "high": 100.0, "low": 99.8, "close": 99.95, "volume": 10.0}]
        state, reference, _ = _detect_role_flip(price=99.95, atr=1.0, supports=[level(99.9, 100.1, 9), level(99.88, 100.2, 8), level(99.86, 100.3, 7), level(100.0, 100.0, 1)], resistances=[], df_15m=_df(down_rows), cfg=SimpleNamespace())
        self.assertEqual(state, "support_to_resistance_confirmed")
        self.assertEqual(reference["low"], 100.0)
    def test_multitimeframe_levels_merge_and_keep_confluence(self) -> None:
        result = build_market_map(
            price=100.0,
            atr=2.0,
            per_tf_inputs=_inputs(df_15m=_df(_flat_rows(100.0))),
            volume_info={"expansion_score": 1.2},
            breakout_up=False,
            breakout_down=False,
            cfg=SimpleNamespace(),
        )

        support = result["nearest_major_support"]
        resistance = result["nearest_major_resistance"]
        self.assertGreaterEqual(support["confluence_count"], 2)
        self.assertGreaterEqual(resistance["confluence_count"], 2)
        self.assertIn("4h", support["sources"])
        self.assertIn("1h", resistance["sources"])

    def test_support_to_resistance_flip_is_confirmed_after_retest_failure(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 99.7, "high": 100.1, "low": 98.6, "close": 98.8, "volume": 14.0},
            {"open": 98.8, "high": 99.4, "low": 98.4, "close": 98.7, "volume": 12.0},
            {"open": 98.7, "high": 99.2, "low": 98.2, "close": 98.5, "volume": 11.0},
        ]
        result = build_market_map(
            price=98.7,
            atr=1.0,
            per_tf_inputs=_inputs(
                df_15m=_df(rows),
                support_price=100.0,
                resistance_price=106.0,
                structure_1h="lh_ll",
                structure_15m="lh_ll",
                signal_1h="short",
                signal_15m="short",
            ),
            volume_info={"expansion_score": 1.2},
            breakout_up=False,
            breakout_down=True,
            cfg=SimpleNamespace(),
        )

        self.assertEqual(result["level_flip_state"], "support_to_resistance_confirmed")
        self.assertIn("support_to_resistance_flip", result["flags"])
        self.assertEqual(result["trend_flip_state"], "confirmed_down")
        self.assertEqual(result["market_map_primary_state"], "confirmed_down")

    def test_resistance_to_support_flip_is_confirmed_after_retest_hold(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.4, "high": 101.6, "low": 100.2, "close": 101.3, "volume": 14.0},
            {"open": 101.3, "high": 102.0, "low": 100.6, "close": 101.8, "volume": 12.0},
            {"open": 101.8, "high": 102.2, "low": 101.1, "close": 101.9, "volume": 11.0},
        ]
        result = build_market_map(
            price=101.8,
            atr=1.0,
            per_tf_inputs=_inputs(
                df_15m=_df(rows),
                support_price=94.0,
                resistance_price=100.0,
                structure_1h="hh_hl",
                structure_15m="hh_hl",
                signal_1h="long",
                signal_15m="long",
            ),
            volume_info={"expansion_score": 1.2},
            breakout_up=True,
            breakout_down=False,
            cfg=SimpleNamespace(),
        )

        self.assertEqual(result["level_flip_state"], "resistance_to_support_confirmed")
        self.assertIn("resistance_to_support_flip", result["flags"])
        self.assertEqual(result["trend_flip_state"], "confirmed_up")
        self.assertEqual(result["market_map_primary_state"], "confirmed_up")

    def test_retest_before_break_and_same_bar_do_not_confirm(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.2, "high": 101.0, "low": 99.7, "close": 100.5, "volume": 10.0},
            {"open": 100.5, "high": 101.8, "low": 100.4, "close": 101.3, "volume": 10.0},
        ]
        result = build_market_map(price=101.3, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=94, resistance_price=100, signal_1h="long", signal_15m="long"), volume_info={}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertEqual(result["level_flip_state"], "resistance_to_support_early")
        self.assertIsNone(result["level_flip_reference"]["retest_index"])

    def test_opposite_15m_signal_keeps_ordered_flip_early(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.2, "high": 101.6, "low": 100.1, "close": 101.3, "volume": 10.0},
            {"open": 101.3, "high": 101.8, "low": 100.2, "close": 101.4, "volume": 10.0},
            {"open": 101.4, "high": 102.0, "low": 101.2, "close": 101.7, "volume": 10.0},
        ]
        result = build_market_map(price=101.7, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=94, resistance_price=100, structure_1h="hh_hl", signal_1h="long", signal_15m="short"), volume_info={}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertNotEqual(result["trend_flip_state"], "confirmed_up")
        self.assertIn("opposite_15m_signal_conflict", result["market_map_conflicts"])

    def test_interrupted_up_sequence_requires_a_new_break(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.2, "high": 101.6, "low": 100.1, "close": 101.3, "volume": 10.0},
            {"open": 101.3, "high": 101.4, "low": 99.4, "close": 99.9, "volume": 10.0},
            {"open": 99.9, "high": 101.0, "low": 100.1, "close": 100.5, "volume": 10.0},
            {"open": 100.5, "high": 101.2, "low": 100.4, "close": 101.0, "volume": 10.0},
        ]
        result = build_market_map(price=101.0, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=94, resistance_price=100, signal_1h="long", signal_15m="long"), volume_info={}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertNotEqual(result["level_flip_state"], "resistance_to_support_confirmed")

    def test_interrupted_down_sequence_requires_a_new_break(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 99.8, "high": 99.9, "low": 98.4, "close": 98.7, "volume": 10.0},
            {"open": 98.7, "high": 100.5, "low": 98.6, "close": 100.0, "volume": 10.0},
            {"open": 100.0, "high": 99.9, "low": 99.0, "close": 99.5, "volume": 10.0},
            {"open": 99.5, "high": 99.7, "low": 98.8, "close": 99.0, "volume": 10.0},
        ]
        result = build_market_map(price=98.9, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=100, resistance_price=106, signal_1h="short", signal_15m="short"), volume_info={}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertNotEqual(result["level_flip_state"], "support_to_resistance_confirmed")

    def test_new_break_after_invalidation_can_confirm(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.2, "high": 101.6, "low": 100.1, "close": 101.3, "volume": 10.0},
            {"open": 101.3, "high": 101.4, "low": 99.4, "close": 99.9, "volume": 10.0},
            {"open": 100.0, "high": 101.8, "low": 100.2, "close": 101.4, "volume": 10.0},
            {"open": 101.4, "high": 101.7, "low": 100.2, "close": 101.3, "volume": 10.0},
            {"open": 101.3, "high": 101.8, "low": 101.0, "close": 101.5, "volume": 10.0},
        ]
        result = build_market_map(price=101.5, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=94, resistance_price=100, signal_1h="long", signal_15m="long"), volume_info={}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertEqual(result["level_flip_state"], "resistance_to_support_confirmed")
        self.assertEqual(result["level_flip_reference"]["break_index"], 13)

    def test_opposite_15m_conflict_is_symmetric_down(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 99.8, "high": 99.9, "low": 98.4, "close": 98.7, "volume": 10.0},
            {"open": 98.7, "high": 99.8, "low": 98.5, "close": 98.8, "volume": 10.0},
            {"open": 98.8, "high": 99.2, "low": 98.5, "close": 98.7, "volume": 10.0},
        ]
        result = build_market_map(price=98.7, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=100, resistance_price=106, structure_1h="lh_ll", signal_1h="short", signal_15m="long"), volume_info={}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertNotEqual(result["trend_flip_state"], "confirmed_down")
        self.assertIn("opposite_15m_signal_conflict", result["market_map_conflicts"])

    def test_boundary_retest_and_hold_remain_confirmed_after_break(self) -> None:
        up_rows = _flat_rows(100.0, 16) + [
            {"open": 100.0, "high": 100.3, "low": 100.0, "close": 100.2, "volume": 10.0},
            {"open": 100.2, "high": 100.2, "low": 99.9, "close": 100.05, "volume": 10.0},
            {"open": 100.05, "high": 100.2, "low": 100.0, "close": 100.05, "volume": 10.0},
        ]
        up = build_market_map(price=100.05, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(up_rows), support_price=94, resistance_price=99, signal_1h="long", signal_15m="long"), volume_info={"expansion_score": 1.2}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertEqual(up["level_flip_state"], "resistance_to_support_confirmed")
        self.assertLess(up["level_flip_reference"]["break_index"], up["level_flip_reference"]["retest_index"])
        self.assertLess(up["level_flip_reference"]["retest_index"], up["level_flip_reference"]["hold_index"])

        down_rows = _flat_rows(100.0, 16) + [
            {"open": 100.0, "high": 100.0, "low": 99.7, "close": 99.8, "volume": 10.0},
            {"open": 99.8, "high": 100.1, "low": 99.8, "close": 99.95, "volume": 10.0},
            {"open": 99.95, "high": 100.0, "low": 99.8, "close": 99.95, "volume": 10.0},
        ]
        down = build_market_map(price=99.95, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(down_rows), support_price=101, resistance_price=106, signal_1h="short", signal_15m="short"), volume_info={"expansion_score": 1.2}, breakout_up=False, breakout_down=False, cfg=SimpleNamespace())
        self.assertEqual(down["level_flip_state"], "support_to_resistance_confirmed")

    def test_market_map_direction_conflict_prevents_confirmed_trend(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.0, "high": 101.6, "low": 100.0, "close": 101.3, "volume": 10.0},
            {"open": 101.3, "high": 101.5, "low": 100.1, "close": 101.2, "volume": 10.0},
            {"open": 101.2, "high": 104.0, "low": 101.1, "close": 101.2, "volume": 8.0},
        ]
        result = build_market_map(price=101.2, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=94, resistance_price=100, signal_1h="long", signal_15m="long"), volume_info={"expansion_score": 1.0}, breakout_up=True, breakout_down=False, cfg=SimpleNamespace())
        self.assertIn("market_map_direction_conflict", result["market_map_conflicts"])
        self.assertNotEqual(result["trend_flip_state"], "confirmed_up")
        self.assertNotIn("trend_flip_confirmed_up", result["flags"])
        self.assertEqual(result["market_map_primary_state"], "direction_conflict")

    def test_market_map_direction_conflict_is_symmetric_down(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.0, "high": 100.0, "low": 98.4, "close": 98.7, "volume": 10.0},
            {"open": 98.7, "high": 99.8, "low": 98.5, "close": 98.8, "volume": 10.0},
            {"open": 98.8, "high": 98.9, "low": 96.0, "close": 98.7, "volume": 8.0},
        ]
        result = build_market_map(price=98.7, atr=1.0, per_tf_inputs=_inputs(df_15m=_df(rows), support_price=100, resistance_price=106, signal_1h="short", signal_15m="short"), volume_info={"expansion_score": 1.0}, breakout_up=False, breakout_down=True, cfg=SimpleNamespace())
        self.assertIn("market_map_direction_conflict", result["market_map_conflicts"])
        self.assertNotEqual(result["trend_flip_state"], "confirmed_down")
        self.assertNotIn("trend_flip_confirmed_down", result["flags"])
        self.assertEqual(result["market_map_primary_state"], "direction_conflict")

    def test_failed_breakout_down_reversal_uses_major_resistance_rejection(self) -> None:
        rows = _flat_rows(103.0, 12) + [
            {"open": 103.5, "high": 104.0, "low": 103.0, "close": 103.8, "volume": 10.0},
            {"open": 104.2, "high": 106.3, "low": 103.8, "close": 104.7, "volume": 8.0},
        ]
        result = build_market_map(
            price=104.7,
            atr=1.0,
            per_tf_inputs=_inputs(df_15m=_df(rows), support_price=98.0, resistance_price=105.0),
            volume_info={"expansion_score": 1.0},
            breakout_up=True,
            breakout_down=False,
            cfg=SimpleNamespace(),
        )

        self.assertEqual(result["failed_breakout_state"], "down_reversal")
        self.assertIn("failed_breakout_down_reversal", result["flags"])
        self.assertIn("major_resistance_rejection", result["flags"])


if __name__ == "__main__":
    unittest.main()
