from __future__ import annotations

import sys
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import CURRENT_EMAIL_SUBJECT_PREFIX, build_summary_body, build_summary_subject  # noqa: E402
from src.notification.followup import evaluate_followup_notification  # noqa: E402


def _base_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "timestamp_jst": "2026-03-11T09:05:00+09:00",
        "notification_kind": "main",
        "bias": "long",
        "current_price": 70356.3,
        "trade_execution_gate": "blocked",
        "primary_setup_status": "watch",
        "primary_setup_reason": "entry_zone_not_reached",
        "signals_4h": "long",
        "signals_1h": "long",
        "signals_15m": "wait",
        "support_zones": [{"low": 69900.0, "high": 70010.0, "distance_from_price": 346.3}],
        "resistance_zones": [{"low": 70450.0, "high": 70600.0, "distance_from_price": 93.7}],
        "long_setup": {"status": "watch"},
        "short_setup": {"status": "watch"},
        "detail_page_url": "https://server.afrog.jp/btc-monitor/notifications/manual-trading/main/20260706_160500.html",
        "actionability_safety": "report-only / no automatic order / human decides manually",
    }
    payload.update(overrides)
    return payload


class SummaryFormatTest(unittest.TestCase):
    def test_compact_main_subject_and_body_are_short(self) -> None:
        payload = _base_payload()
        subject = build_summary_subject(payload)
        body, provider = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertEqual(provider, "api")
        self.assertTrue(subject.startswith(f"{CURRENT_EMAIL_SUBJECT_PREFIX} 📊 結論 | "))
        self.assertIn("BTC 70,356", subject)
        self.assertIn("【結論】", body)
        self.assertIn("実行候補ではない。", body)
        self.assertIn("HTML確認", body)
        self.assertIn("通常バイアス: 上方向", body)
        self.assertIn("現在: 70,356.30", body)
        self.assertIn("上: 70,450.00 - 70,600.00", body)
        self.assertIn("下: 69,900.00 - 70,010.00", body)
        self.assertIn("詳細:", body)
        self.assertIn("※ report-only / no automatic order / human decides manually", body)
        self.assertLessEqual(len([line for line in body.splitlines() if line.strip()]), 25)
        self.assertNotIn("【ローカル確認】", body)
        self.assertNotIn("【実行ゲート】", body)
        self.assertNotIn("【観測ゲート】", body)
        self.assertNotIn("【Operator Triage Summary】", body)
        self.assertNotIn("【Post-Eval】", body)

    def test_compact_attention_body_highlights_reason_and_url(self) -> None:
        payload = _base_payload(
            notification_kind="attention",
            bias="short",
            current_price=70765.2,
            signals_4h="wait",
            signals_1h="short",
        )
        subject = build_summary_subject(payload)
        body, provider = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertEqual(provider, "api")
        self.assertTrue(subject.startswith(f"{CURRENT_EMAIL_SUBJECT_PREFIX} 👀 注意報 | "))
        self.assertIn("【注意報】", body)
        self.assertIn("実行候補ではない。高優先で監視。", body)
        self.assertIn("Big Chance: なし", body)
        self.assertIn("通常バイアス: 下方向", body)
        self.assertIn("現在: 70,765.20", body)
        self.assertIn("詳細:", body)
        self.assertIn("※ report-only / no automatic order / human decides manually", body)
        self.assertLessEqual(len([line for line in body.splitlines() if line.strip()]), 25)
        self.assertNotIn("【ローカル確認】", body)
        self.assertNotIn("【実行ゲート】", body)
        self.assertNotIn("【観測ゲート】", body)

    def test_cli_attention_body_uses_compact_body(self) -> None:
        payload = _base_payload(
            notification_kind="attention",
            bias="short",
            current_price=70765.2,
            signals_4h="wait",
            signals_1h="short",
        )
        body, provider = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertEqual(provider, "cli")
        self.assertIn("【注意報】", body)
        self.assertIn("実行候補ではない。高優先で監視。", body)
        self.assertIn("保有中:", body)
        self.assertIn("未保有:", body)
        self.assertIn("Big Chance:", body)
        self.assertIn("詳細:", body)
        self.assertNotIn("【行動判定】", body)
        self.assertNotIn("actionability_label:", body)
        self.assertNotIn("【ローカル確認】", body)
        self.assertNotIn("【実行ゲート】", body)
        self.assertNotIn("【観測ゲート】", body)
        self.assertNotIn("local/manual_delivery_app_surface", body)
        self.assertLessEqual(len([line for line in body.splitlines() if line.strip()]), 25)

    def test_compact_followup_body_and_subject(self) -> None:
        baseline = {
            "signal_id": "20260705_220500",
            "notification_kind": "main",
            "bias": "long",
            "timestamp_utc": "2026-07-05T12:05:00Z",
            "notified_at_utc": "2026-07-05T12:05:00Z",
            "confidence": 74,
        }
        current = _base_payload(
            signal_id="20260705_230500",
            timestamp_jst="2026-07-05T23:10:00+09:00",
            timestamp_utc="2026-07-05T14:10:00Z",
            notification_kind="followup",
            bias="wait",
            signals_1h="wait",
            confidence=57,
            long_setup={"status": "invalid"},
            followup_context={
                "subject_hint": "⏱期限切れ",
            },
        )
        evaluation = evaluate_followup_notification(current, None, baseline, None, _followup_cfg())
        current["followup_context"] = evaluation
        current["summary_subject"] = build_summary_subject(current)
        body, provider = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=current,
        )

        self.assertEqual(provider, "api")
        self.assertIn("⏱期限切れ", current["summary_subject"])
        self.assertIn("【期限切れ・再評価】", body)
        self.assertIn("前回通知は失効。新規根拠として使わない。", body)
        self.assertIn("保有中:", body)
        self.assertIn("未保有:", body)
        self.assertIn("Big Chance:", body)
        self.assertIn("詳細:", body)
        self.assertIn("※ report-only / no automatic order / human decides manually", body)
        self.assertLessEqual(len([line for line in body.splitlines() if line.strip()]), 25)

    def test_cli_followup_body_is_compact(self) -> None:
        baseline = {
            "signal_id": "20260705_220500",
            "notification_kind": "main",
            "bias": "long",
            "timestamp_utc": "2026-07-05T12:05:00Z",
            "notified_at_utc": "2026-07-05T12:05:00Z",
            "confidence": 74,
        }
        current = _base_payload(
            signal_id="20260705_230500",
            timestamp_jst="2026-07-05T23:10:00+09:00",
            timestamp_utc="2026-07-05T14:10:00Z",
            notification_kind="followup",
            bias="wait",
            signals_1h="wait",
            confidence=57,
            long_setup={"status": "invalid"},
            followup_context={
                "subject_hint": "⏱期限切れ",
            },
        )
        evaluation = evaluate_followup_notification(current, None, baseline, None, _followup_cfg())
        current["followup_context"] = evaluation
        body, provider = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=current,
        )

        self.assertEqual(provider, "cli")
        self.assertIn("【期限切れ・再評価】", body)
        self.assertIn("前回通知は失効。新規根拠として使わない。", body)
        self.assertIn("保有中:", body)
        self.assertIn("未保有:", body)
        self.assertIn("Big Chance:", body)
        self.assertIn("詳細:", body)
        self.assertIn("※ report-only / no automatic order / human decides manually", body)
        self.assertLessEqual(len([line for line in body.splitlines() if line.strip()]), 25)

    def test_cli_main_body_is_compact(self) -> None:
        payload = _base_payload()
        body, provider = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertEqual(provider, "cli")
        self.assertIn("【結論】", body)
        self.assertIn("実行候補ではない。", body)
        self.assertIn("HTML確認", body)
        self.assertIn("Big Chance:", body)
        self.assertIn("詳細:", body)
        self.assertNotIn("【行動判定】", body)
        self.assertNotIn("【ローカル確認】", body)
        self.assertLessEqual(len([line for line in body.splitlines() if line.strip()]), 25)

    def test_compact_subject_suppresses_legacy_labels(self) -> None:
        payload = _base_payload(system_label="Ver02.6-v2", system_mode_label="CLI")
        subject = build_summary_subject(payload)

        self.assertNotIn("Ver", subject)
        self.assertNotIn("[CLI]", subject)
        self.assertNotIn("[API]", subject)
        self.assertNotIn("[機械判定のみ]", subject)

    def test_compact_body_is_short_and_excludes_debug_sections(self) -> None:
        payload = _base_payload()
        body, _provider = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertLessEqual(len([line for line in body.splitlines() if line.strip()]), 25)
        self.assertNotIn("【ローカル確認】", body)
        self.assertNotIn("【実行ゲート】", body)
        self.assertNotIn("【観測ゲート】", body)
        self.assertNotIn("【Operator Triage Summary】", body)
        self.assertNotIn("【Post-Eval】", body)


def _followup_cfg() -> object:
    from types import SimpleNamespace

    return SimpleNamespace(
        FOLLOWUP_VALIDITY_MINUTES=60,
        FOLLOWUP_ALERT_COOLDOWN_MINUTES=60,
        FOLLOWUP_CONFIDENCE_DROP_MIN=10,
        CONFIDENCE_LONG_MIN=45,
        CONFIDENCE_SHORT_MIN=55,
        CONFIDENCE_ALERT_CHANGE=10,
        ALERT_COOLDOWN_MINUTES=60,
        ATTENTION_ALERT_SCORE_MIN=55,
        ATTENTION_ALERT_GAP_MIN=15,
        ATTENTION_ALERT_COOLDOWN_MINUTES=60,
    )


if __name__ == "__main__":
    unittest.main()
