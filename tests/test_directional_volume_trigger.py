from __future__ import annotations

import unittest

from main import _directional_volume_triggers


class DirectionalVolumeTriggerTests(unittest.TestCase):
    def test_volume_only_doji_does_not_trigger_both_directions(self) -> None:
        result = _directional_volume_triggers(
            volume_ratio=3.0,
            volume_threshold=2.0,
            candle_open=100,
            candle_high=110,
            candle_low=90,
            candle_close=101,
            range_high=120,
            range_low=80,
            breakout_up=False,
            breakout_down=False,
            market_map={"flags": []},
        )

        self.assertEqual(result, {"trigger_up": False, "trigger_down": False})

    def test_bullish_high_volume_triggers_up_only(self) -> None:
        result = _directional_volume_triggers(
            volume_ratio=3.0,
            volume_threshold=2.0,
            candle_open=100,
            candle_high=112,
            candle_low=98,
            candle_close=111,
            range_high=112,
            range_low=90,
            breakout_up=False,
            breakout_down=False,
            market_map={"flags": []},
        )

        self.assertEqual(result, {"trigger_up": True, "trigger_down": False})

    def test_bearish_high_volume_triggers_down_only(self) -> None:
        result = _directional_volume_triggers(
            volume_ratio=3.0,
            volume_threshold=2.0,
            candle_open=110,
            candle_high=112,
            candle_low=98,
            candle_close=99,
            range_high=120,
            range_low=98,
            breakout_up=False,
            breakout_down=False,
            market_map={"flags": []},
        )

        self.assertEqual(result, {"trigger_up": False, "trigger_down": True})

    def test_breakout_remains_directional_without_volume(self) -> None:
        up = _directional_volume_triggers(
            volume_ratio=1.0,
            volume_threshold=2.0,
            candle_open=100,
            candle_high=105,
            candle_low=95,
            candle_close=102,
            range_high=105,
            range_low=95,
            breakout_up=True,
            breakout_down=False,
            market_map={"flags": []},
        )
        down = _directional_volume_triggers(
            volume_ratio=1.0,
            volume_threshold=2.0,
            candle_open=100,
            candle_high=105,
            candle_low=95,
            candle_close=98,
            range_high=105,
            range_low=95,
            breakout_up=False,
            breakout_down=True,
            market_map={"flags": []},
        )

        self.assertEqual(up, {"trigger_up": True, "trigger_down": False})
        self.assertEqual(down, {"trigger_up": False, "trigger_down": True})

    def test_only_confirmed_market_map_flags_trigger_direction(self) -> None:
        long_result = _directional_volume_triggers(
            volume_ratio=1.0,
            volume_threshold=2.0,
            candle_open=100,
            candle_high=105,
            candle_low=95,
            candle_close=101,
            range_high=105,
            range_low=95,
            breakout_up=False,
            breakout_down=False,
            market_map={"flags": ["resistance_to_support_retest_confirmed"]},
        )
        short_result = _directional_volume_triggers(
            volume_ratio=1.0,
            volume_threshold=2.0,
            candle_open=100,
            candle_high=105,
            candle_low=95,
            candle_close=99,
            range_high=105,
            range_low=95,
            breakout_up=False,
            breakout_down=False,
            market_map={"flags": ["support_to_resistance_retest_confirmed"]},
        )

        self.assertEqual(long_result, {"trigger_up": True, "trigger_down": False})
        self.assertEqual(short_result, {"trigger_up": False, "trigger_down": True})

    def test_plain_flip_and_failed_breakout_do_not_trigger(self) -> None:
        result = _directional_volume_triggers(volume_ratio=1.0, volume_threshold=2.0, candle_open=100, candle_high=105, candle_low=95, candle_close=100, range_high=105, range_low=95, breakout_up=False, breakout_down=False, market_map={"flags": ["resistance_to_support_flip", "failed_breakout_up_reversal"]})
        self.assertEqual(result, {"trigger_up": False, "trigger_down": False})

    def test_market_map_conflict_blocks_only_market_map_triggers(self) -> None:
        conflicted = {"flags": ["resistance_to_support_retest_confirmed", "support_to_resistance_retest_confirmed"], "market_map_conflicts": ["market_map_direction_conflict"]}
        blocked = _directional_volume_triggers(volume_ratio=1.0, volume_threshold=2.0, candle_open=100, candle_high=105, candle_low=95, candle_close=100, range_high=105, range_low=95, breakout_up=False, breakout_down=False, market_map=conflicted)
        explicit = _directional_volume_triggers(volume_ratio=1.0, volume_threshold=2.0, candle_open=100, candle_high=105, candle_low=95, candle_close=100, range_high=105, range_low=95, breakout_up=True, breakout_down=False, market_map=conflicted)
        self.assertEqual(blocked, {"trigger_up": False, "trigger_down": False})
        self.assertEqual(explicit, {"trigger_up": True, "trigger_down": False})

    def test_explicit_opposing_breakouts_can_still_create_both(self) -> None:
        result = _directional_volume_triggers(
            volume_ratio=1.0,
            volume_threshold=2.0,
            candle_open=100,
            candle_high=105,
            candle_low=95,
            candle_close=100,
            range_high=105,
            range_low=95,
            breakout_up=True,
            breakout_down=True,
            market_map={"flags": []},
        )

        self.assertEqual(result, {"trigger_up": True, "trigger_down": True})


if __name__ == "__main__":
    unittest.main()
