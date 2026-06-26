from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.presentation.sanitize import sanitize_flag_list, sanitize_reason_codes, sanitize_user_text


class ReasonCodeSanitizeTest(unittest.TestCase):
    def test_known_codes_are_translated(self) -> None:
        items = sanitize_reason_codes(["bid_wall_close", "upper_liquidity_close"])
        self.assertIn("近い買い板があり短期ノイズに注意", items)
        self.assertIn("上側流動性が近く先に振られやすい", items)

    def test_unknown_codes_are_hidden(self) -> None:
        items = sanitize_reason_codes(["unknown_xxx"])
        self.assertEqual(items, ["内部要因のため詳細省略"])

    def test_user_text_replaces_raw_codes(self) -> None:
        text = sanitize_user_text("bid_wall_close / upper_liquidity_close / custom_unknown_flag")
        self.assertNotIn("bid_wall_close", text)
        self.assertNotIn("upper_liquidity_close", text)
        self.assertNotIn("custom_unknown_flag", text)
        self.assertIn("内部要因のため詳細省略", text)
