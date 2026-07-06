from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import main  # noqa: E402
from src.analysis.big_chance import build_big_chance_artifact, write_big_chance_artifact  # noqa: E402
from tests.test_big_chance import _payload  # noqa: E402


class BigChanceArtifactTests(unittest.TestCase):
    def test_cli_dry_run_stdout_json_writes_nothing(self) -> None:
        current = _payload(
            signal_id="20260706_150500",
            timestamp_jst="2026-07-06T15:05:00+09:00",
            bias="long",
            current_price=50_100,
            signals_4h="short",
            signals_1h="wait",
            signals_15m="short",
            market_map_primary_state="early_down_transition",
            market_map_flags=["support_to_resistance_flip"],
            level_flip_state="support_to_resistance_confirmed",
            trend_flip_state="trend_flip_early_down",
            failed_breakout_state="failed_long_breakout",
            transition_direction="down",
            long_zone=(47_000, 47_500, 46_800, 47_200, 46_200, 46_600, 46_900, 47_100, "invalidated"),
            short_zone=(52_000, 52_500, 52_600, 53_100, 53_600, 54_000, 52_850, 53_050, "watch"),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "input.json"
            input_path.write_text(json.dumps(current, ensure_ascii=False), encoding="utf-8")
            out_dir = Path(tmp_dir) / "out"
            cmd = [
                sys.executable,
                str(BASE_DIR / "tools" / "build_big_chance_artifact.py"),
                "--input",
                str(input_path),
                "--out-dir",
                str(out_dir),
                "--dry-run",
                "--stdout-json",
            ]
            completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
            artifact = json.loads(completed.stdout)

            self.assertTrue(artifact["candidate"]["present"])
            self.assertFalse(out_dir.exists())

    def test_non_dry_run_and_runtime_helper_write_artifacts(self) -> None:
        current = _payload(
            signal_id="20260706_151500",
            timestamp_jst="2026-07-06T15:15:00+09:00",
            bias="short",
            current_price=60_100,
            signals_4h="long",
            signals_1h="wait",
            signals_15m="long",
            market_map_primary_state="early_up_transition",
            market_map_flags=["resistance_to_support_flip", "resistance_to_support_retest_confirmed"],
            level_flip_state="resistance_to_support_confirmed",
            trend_flip_state="trend_flip_early_up",
            failed_breakout_state="failed_short_breakout",
            transition_direction="up",
            long_zone=(62_000, 62_500, 62_600, 63_100, 63_600, 64_000, 62_850, 63_050, "watch"),
            short_zone=(57_000, 57_500, 56_800, 57_200, 56_200, 56_600, 56_900, 57_100, "invalidated"),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            artifact = build_big_chance_artifact(current, source_file=tmp_path / "logs" / "last_result.json")
            json_path, md_path, latest_json_path, latest_md_path = write_big_chance_artifact(artifact, tmp_path / "local" / "big_chance")

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertTrue(latest_json_path.exists())
            self.assertTrue(latest_md_path.exists())
            self.assertIn("Big Chance / Failed Thesis", md_path.read_text(encoding="utf-8"))

            hook_dir = tmp_path / "hook"
            hook_status = main._maybe_write_big_chance_artifact(
                current,
                base_dir=hook_dir,
                previous_result={"signal_id": "20260706_141500", "notification_kind": "attention", "bias": "short"},
            )
            self.assertTrue(hook_status["written"])
            self.assertEqual(hook_status["status"], "written")
            self.assertTrue((hook_dir / "local" / "big_chance" / "20260706_151500.json").exists())


if __name__ == "__main__":
    unittest.main()
