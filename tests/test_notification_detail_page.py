from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import load_config
from main import run_cycle
from src.data.exchange_fetcher import MarketStructureSnapshot
from src.notification.detail_page import (
    build_notification_detail_html,
    detail_page_enabled,
    detail_page_paths,
)


def _sample_df(length: int = 260, *, trend: float = 1.0) -> pd.DataFrame:
    rows = []
    price = 100.0
    for i in range(length):
        if i < length - 25:
            price += trend * 0.3
        else:
            price -= trend * 0.08
        high = price + 0.6
        low = price - 0.6
        close = price + (0.1 if i % 2 == 0 else -0.05)
        volume = 100 + (i % 7) * 4
        if i >= length - 10:
            volume = 70 + (i % 3) * 2
        if i == length - 1:
            volume = 140
            high += 0.4
        rows.append(
            {
                "timestamp": 1_700_000_000_000 + i * 900_000,
                "open": price - 0.2,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
    return pd.DataFrame(rows)


class NotificationDetailPageTests(unittest.TestCase):
    def test_build_notification_detail_html_contains_explanations_and_escapes_text(self) -> None:
        payload = {
            "signal_id": "20260331_010500",
            "timestamp_jst": "2026-03-31T01:05:00+09:00",
            "summary_subject": "下方向バイアス / 上側流動性回収待ち",
            "system_label": "Ver02.3v3-OBS",
            "notification_kind": "main",
            "bias": "short",
            "prelabel": "SWEEP_WAIT",
            "market_regime": "downtrend",
            "phase": "pullback",
            "signals_4h": "short",
            "signals_1h": "short",
            "signals_15m": "wait",
            "long_display_score": 51,
            "short_display_score": 100,
            "score_gap": -49,
            "current_price": 65817.7,
            "funding_rate_display": "ほぼ中立 (+0.0028%)",
            "atr_ratio": 1.75,
            "volume_ratio": 4.53,
            "support_zones": [{"low": 65629.02, "high": 65736.78, "distance_from_price": 80.92}],
            "resistance_zones": [{"low": 66418.52, "high": 66587.78, "distance_from_price": 600.82}],
            "long_setup": {
                "status": "watch",
                "entry_zone": {"low": 65629.02, "high": 65736.78},
                "stop_loss": 65224.9,
                "tp1": 66418.52,
                "tp2": 66598.9,
            },
            "short_setup": {
                "status": "watch",
                "entry_zone": {"low": 66418.52, "high": 66587.78},
                "stop_loss": 66991.9,
                "tp1": 66341.98,
                "tp2": 65525.65,
            },
            "primary_setup_status": "watch",
            "primary_setup_reason": "near_entry_zone_waiting_trigger",
            "warning_flags": [],
            "risk_flags": ["upper_liquidity_close"],
            "no_trade_flags": ["sweep_incomplete", "rr_below_min"],
            "confidence_direction_shadow": 100,
            "confidence_execution_shadow": 7.0,
            "confidence_wait_shadow": 68.8,
            "ai_advice": {
                "primary_reason": "<強い下方向> だが RR_insufficient_short なので待ち",
                "next_condition": "upper_liquidity_close 解消を確認",
                "warnings": ["sweep_incomplete"],
            },
        }

        html = build_notification_detail_html(payload)

        self.assertIn("3つの数字を丁寧に読む", html)
        self.assertIn("ステータス", html)
        self.assertIn("今の行動", html)
        self.assertIn("方向の強さ", html)
        self.assertIn("実行しやすさ", html)
        self.assertIn("待機圧力", html)
        self.assertIn("スコア差", html)
        self.assertIn("ロング / ショートの再検討ライン", html)
        self.assertIn("&lt;強い下方向&gt;", html)
        self.assertNotIn("<強い下方向>", html)

    def test_detail_page_paths_use_slug_and_kind(self) -> None:
        cfg = SimpleNamespace(
            NOTIFICATION_HTML_LOCAL_DIR="logs/notifications_html",
            NOTIFICATION_HTML_PUBLIC_BASE_URL="https://server.afrog.jp/btc-monitor/notifications",
        )
        base_dir = BASE_DIR
        result = {
            "system_label": "Ver02.3v3 OBS",
            "notification_kind": "attention",
            "signal_id": "20260331_020500",
        }

        local_path, public_url = detail_page_paths(base_dir, cfg, result)

        self.assertIn("ver02-3v3-obs/attention/20260331_020500.html", str(local_path))
        self.assertTrue(public_url.endswith("/ver02-3v3-obs/attention/20260331_020500.html"))

    def test_detail_page_enabled_can_skip_attention(self) -> None:
        required_env = {
            "OPENAI_API_KEY": "x",
            "SMTP_HOST": "smtp",
            "SMTP_PORT": "587",
            "SMTP_USER": "u",
            "SMTP_PASSWORD": "p",
            "MAIL_FROM": "a@example.com",
            "MAIL_TO": "b@example.com",
            "NOTIFICATION_HTML_ENABLED": "true",
            "NOTIFICATION_HTML_INCLUDE_ATTENTION": "false",
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, required_env, clear=False):
                cfg = load_config(Path(tmp_dir))

        self.assertFalse(detail_page_enabled(cfg, {"notification_kind": "attention"}))
        self.assertTrue(detail_page_enabled(cfg, {"notification_kind": "main"}))

    def test_run_cycle_appends_detail_page_url_on_publish_success(self) -> None:
        required_env = {
            "OPENAI_API_KEY": "x",
            "SMTP_HOST": "smtp",
            "SMTP_PORT": "587",
            "SMTP_USER": "u",
            "SMTP_PASSWORD": "p",
            "MAIL_FROM": "a@example.com",
            "MAIL_TO": "b@example.com",
            "NOTIFICATION_HTML_ENABLED": "true",
        }
        df = _sample_df()
        captured: dict[str, str] = {}

        def _capture_send_email(**kwargs: str) -> None:
            captured["body"] = kwargs["body"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, required_env, clear=False):
                cfg = load_config(Path(tmp_dir))
            with patch("main.get_server_time_ms", return_value=1_700_000_000_000), patch(
                "main.fetch_klines", side_effect=[df, df, df]
            ), patch("main.validate_klines", return_value=True), patch(
                "main.fetch_market_structure", return_value=MarketStructureSnapshot(missing_fields=[])
            ), patch("main.fetch_funding_rate", return_value=0.0), patch(
                "main.resend_pending_email", return_value=None
            ), patch("main.cleanup_if_due", return_value=None), patch(
                "main.request_ai_advice",
                return_value=(
                    {
                        "decision": "LONG",
                        "quality": "B",
                        "confidence": 0.7,
                        "notes": "stub",
                    },
                    "api",
                ),
            ), patch(
                "main.build_summary_body", return_value=("summary body", "api")
            ), patch(
                "main.build_summary_subject", return_value="subject"
            ), patch(
                "main.should_notify",
                return_value={
                    "notify": True,
                    "notify_reason_codes": ["signal_tier_upgraded"],
                    "suppress_reason_codes": [],
                    "notification_kind": "main",
                },
            ), patch(
                "main.publish_notification_detail",
                return_value={
                    "detail_page_enabled": True,
                    "detail_page_status": "published",
                    "detail_page_url": "https://server.afrog.jp/btc-monitor/notifications/ver02/main/20260331_030500.html",
                    "detail_page_local_path": "/tmp/20260331_030500.html",
                    "detail_page_published_at_utc": "2026-03-30T18:05:00Z",
                },
            ), patch("main.send_email", side_effect=_capture_send_email), patch(
                "main.append_trade_log", return_value=Path(tmp_dir) / "logs" / "csv" / "trades.csv"
            ), patch(
                "main.save_signal_snapshot", return_value=Path(tmp_dir) / "logs" / "signals" / "x.json"
            ), patch("main.save_json", return_value=None):
                result = run_cycle(cfg=cfg, base_dir=Path(tmp_dir))

        self.assertIn("【詳細ページ】", captured["body"])
        self.assertIn("https://server.afrog.jp/btc-monitor/notifications/ver02/main/20260331_030500.html", captured["body"])
        self.assertEqual(result["detail_page_status"], "published")

    def test_run_cycle_keeps_plain_body_when_detail_page_publish_fails(self) -> None:
        required_env = {
            "OPENAI_API_KEY": "x",
            "SMTP_HOST": "smtp",
            "SMTP_PORT": "587",
            "SMTP_USER": "u",
            "SMTP_PASSWORD": "p",
            "MAIL_FROM": "a@example.com",
            "MAIL_TO": "b@example.com",
            "NOTIFICATION_HTML_ENABLED": "true",
        }
        df = _sample_df()
        captured: dict[str, str] = {}

        def _capture_send_email(**kwargs: str) -> None:
            captured["body"] = kwargs["body"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, required_env, clear=False):
                cfg = load_config(Path(tmp_dir))
            with patch("main.get_server_time_ms", return_value=1_700_000_000_000), patch(
                "main.fetch_klines", side_effect=[df, df, df]
            ), patch("main.validate_klines", return_value=True), patch(
                "main.fetch_market_structure", return_value=MarketStructureSnapshot(missing_fields=[])
            ), patch("main.fetch_funding_rate", return_value=0.0), patch(
                "main.resend_pending_email", return_value=None
            ), patch("main.cleanup_if_due", return_value=None), patch(
                "main.request_ai_advice",
                return_value=(
                    {
                        "decision": "LONG",
                        "quality": "B",
                        "confidence": 0.7,
                        "notes": "stub",
                    },
                    "api",
                ),
            ), patch(
                "main.build_summary_body", return_value=("summary body", "api")
            ), patch(
                "main.build_summary_subject", return_value="subject"
            ), patch(
                "main.should_notify",
                return_value={
                    "notify": True,
                    "notify_reason_codes": ["signal_tier_upgraded"],
                    "suppress_reason_codes": [],
                    "notification_kind": "main",
                },
            ), patch(
                "main.publish_notification_detail", side_effect=RuntimeError("publish failed")
            ), patch("main.send_email", side_effect=_capture_send_email), patch(
                "main.append_trade_log", return_value=Path(tmp_dir) / "logs" / "csv" / "trades.csv"
            ), patch(
                "main.save_signal_snapshot", return_value=Path(tmp_dir) / "logs" / "signals" / "x.json"
            ), patch("main.save_json", return_value=None):
                result = run_cycle(cfg=cfg, base_dir=Path(tmp_dir))

        self.assertEqual(captured["body"], "summary body")
        self.assertEqual(result["detail_page_status"], "failed")


if __name__ == "__main__":
    unittest.main()
