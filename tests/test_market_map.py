from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.market_map import build_market_map


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
) -> dict[str, dict[str, object]]:
    df_4h = _df(_flat_rows(100.0))
    df_1h = _df(_flat_rows(100.0))
    return {
        "4h": {
            "df": df_4h,
            "swings": {"lows": [{"price": support_price}], "highs": [{"price": resistance_price}]},
            "structure": structure_4h,
        },
        "1h": {
            "df": df_1h,
            "swings": {"lows": [{"price": support_price + 0.3}], "highs": [{"price": resistance_price - 0.2}]},
            "structure": structure_1h,
        },
        "15m": {
            "df": df_15m,
            "swings": {"lows": [{"price": support_price}], "highs": [{"price": resistance_price}]},
            "structure": structure_15m,
        },
    }


class MarketMapTest(unittest.TestCase):
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
            ),
            volume_info={"expansion_score": 1.0},
            breakout_up=False,
            breakout_down=True,
            cfg=SimpleNamespace(),
        )

        self.assertEqual(result["level_flip_state"], "support_to_resistance_confirmed")
        self.assertIn("support_to_resistance_flip", result["flags"])
        self.assertEqual(result["trend_flip_state"], "confirmed_down")

    def test_resistance_to_support_flip_is_confirmed_after_retest_hold(self) -> None:
        rows = _flat_rows(100.0, 16) + [
            {"open": 100.4, "high": 101.6, "low": 100.2, "close": 101.3, "volume": 14.0},
            {"open": 101.3, "high": 102.0, "low": 100.6, "close": 101.8, "volume": 12.0},
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
            ),
            volume_info={"expansion_score": 1.0},
            breakout_up=True,
            breakout_down=False,
            cfg=SimpleNamespace(),
        )

        self.assertEqual(result["level_flip_state"], "resistance_to_support_confirmed")
        self.assertIn("resistance_to_support_flip", result["flags"])
        self.assertEqual(result["trend_flip_state"], "confirmed_up")

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
