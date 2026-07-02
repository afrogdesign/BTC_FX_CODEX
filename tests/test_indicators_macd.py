from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.indicators.macd import calculate_macd, classify_macd_momentum


class MacdIndicatorTest(unittest.TestCase):
    def test_rising_series_produces_constructive_up_state(self) -> None:
        close = pd.Series([float(i) for i in range(1, 61)])
        macd = calculate_macd(close)
        state = classify_macd_momentum(macd["macd"], macd["signal"], macd["histogram"], float(macd["histogram"].iloc[-2]))

        self.assertEqual(state["state"], "constructive_up")
        self.assertTrue(state["above_signal"])
        self.assertTrue(state["histogram_improving"])
        self.assertGreater(float(macd["histogram"].iloc[-1]), float(macd["histogram"].iloc[0]))

    def test_falling_series_produces_constructive_down_state(self) -> None:
        close = pd.Series([float(i) for i in range(60, 0, -1)])
        macd = calculate_macd(close)
        state = classify_macd_momentum(macd["macd"], macd["signal"], macd["histogram"], float(macd["histogram"].iloc[-2]))

        self.assertEqual(state["state"], "constructive_down")
        self.assertTrue(state["below_signal"])
        self.assertTrue(state["histogram_weakening"])
        self.assertLess(float(macd["histogram"].iloc[-1]), float(macd["histogram"].iloc[0]))

    def test_short_input_is_handled_safely(self) -> None:
        close = pd.Series([100.0, 101.0, 102.0])
        macd = calculate_macd(close)
        state = classify_macd_momentum(macd["macd"], macd["signal"], macd["histogram"])

        self.assertEqual(len(macd["macd"]), 3)
        self.assertEqual(len(macd["signal"]), 3)
        self.assertEqual(len(macd["histogram"]), 3)
        self.assertIn(state["state"], {"neutral", "upward", "downward", "constructive_up", "constructive_down"})
