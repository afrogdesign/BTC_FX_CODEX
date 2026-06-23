from __future__ import annotations

import json
import os
import subprocess
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
    publish_notification_detail,
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


def _sample_detail_payload() -> dict[str, object]:
    return {
        "signal_id": "20260331_010500",
        "timestamp_jst": "2026-03-31T01:05:00+09:00",
        "summary_subject": "下方向バイアス / 上側流動性回収待ち",
        "system_label": "Ver02.3v3-OBS",
        "notification_kind": "main",
        "signal_tier": "normal",
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
        "confidence": 66,
        "rr_estimate": 1.18,
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
            "execution_precision_action": "wait_only",
            "execution_precision_flags": ["short_at_major_support_wait_only"],
            "execution_precision_reason": "主要サポートが近く、15分足ショートは追いかけず待機",
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
        "chart_snapshot": {
            "candles_4h": [
                {"timestamp": 1_775_746_800_000, "open": 65900, "high": 66120, "low": 65780, "close": 66040},
                {"timestamp": 1_775_761_200_000, "open": 66040, "high": 66190, "low": 65880, "close": 65960},
                {"timestamp": 1_775_775_600_000, "open": 65960, "high": 66080, "low": 65790, "close": 65830},
            ],
            "candles_1h": [
                {"timestamp": 1_775_775_600_000, "open": 65920, "high": 66030, "low": 65890, "close": 65980},
                {"timestamp": 1_775_779_200_000, "open": 65980, "high": 66040, "low": 65830, "close": 65870},
                {"timestamp": 1_775_782_800_000, "open": 65870, "high": 65910, "low": 65790, "close": 65820},
            ],
            "candles_15m": [
                {"timestamp": 1_775_781_000_000, "open": 65840, "high": 65890, "low": 65810, "close": 65870},
                {"timestamp": 1_775_782_800_000, "open": 65870, "high": 65910, "low": 65820, "close": 65835},
                {"timestamp": 1_775_789_100_000, "open": 65835, "high": 65860, "low": 65795, "close": 65818},
            ],
        },
    }


class NotificationDetailPageTests(unittest.TestCase):
    def test_build_notification_detail_html_contains_explanations_and_escapes_text(self) -> None:
        payload = {
            **_sample_detail_payload(),
            "operator_triage_summary": {
                "summary_status": "ready_for_human_review",
                "all_evidence_present": True,
                "all_evidence_ready": True,
                "evidence": {
                    "operator_status_diagnostic": {"present": True, "ready": True},
                    "safe_config_schema_audit": {"present": True, "ready": True},
                    "intraperiod_review_stdout_json": {"present": True, "ready": True},
                    "manual_action_checklist_surface": {"present": True, "ready": True},
                },
                "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                "note": "derived from existing app contract data only",
            },
            "integrated_evidence_overview": {
                "summary_status": "ready_for_human_review",
                "all_evidence_present": True,
                "all_evidence_ready": True,
                "evidence": {
                    "intraperiod_review_stdout_json": {
                        "present": True,
                        "ready_or_valid": True,
                        "execution_required": False,
                    },
                    "operator_status_diagnostic": {
                        "present": True,
                        "ready_or_valid": True,
                        "execution_required": False,
                    },
                    "safe_config_schema_audit": {
                        "present": True,
                        "ready_or_valid": True,
                        "execution_required": False,
                    },
                    "operator_triage_summary": {
                        "present": True,
                        "ready_or_valid": True,
                        "execution_required": False,
                    },
                    "manual_action_checklist_surface": {
                        "present": True,
                        "ready_or_valid": True,
                        "execution_required": False,
                    },
                },
                "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                "note": "derived from existing app contract/status data only",
            },
            "safe_config_schema_audit": {
                "command": "./.venv312/bin/python tools/safe_config_schema_audit.py",
                "stdout_json_command": "./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json",
                "schema_version": "safe_config_schema_audit.v1",
                "contract_only": True,
                "command_executed_by_app": False,
                "reads_env_values": False,
                "reads_dotenv_values": False,
                "calls_private_endpoints": False,
                "calls_order_endpoints": False,
                "live_trading_allowed": False,
                "secret_values_exposed": False,
                "safety_boundary": (
                    "local/report-only / no load_config / no .env / no os.environ / "
                    "no secret/API key exposure / no exchange/private/account/order endpoint access / "
                    "no FORMAL_GO / no automatic order"
                ),
            },
            "integrated_evidence_overview_evidence_keys": [
                "intraperiod_review_stdout_json",
                "manual_action_checklist_surface",
                "operator_status_diagnostic",
                "operator_triage_summary",
                "safe_config_schema_audit",
            ],
            "integrated_evidence_overview_missing_evidence_keys": [],
            "integrated_evidence_overview_not_ready_evidence_keys": [],
            "integrated_evidence_overview_execution_required_keys": [],
        }

        html = build_notification_detail_html(payload)

        self.assertIn("3つの数字を丁寧に読む", html)
        self.assertIn("手動アクション確認", html)
        self.assertIn("最終ランク", html)
        self.assertIn("今の行動", html)
        self.assertIn("方向の強さ", html)
        self.assertIn("実行しやすさ", html)
        self.assertIn("待機圧力", html)
        self.assertIn("スコア差", html)
        self.assertIn("最終ランク", html)
        self.assertIn("📊 通常監視・実行不可", html)
        self.assertIn("補足状態", html)
        self.assertIn("ロング / ショートの再検討ライン", html)
        self.assertIn("15分足 執行チェック", html)
        self.assertIn("主要サポートが近く、15分足ショートは追いかけず待機", html)
        self.assertIn("4時間足: 大局方向", html)
        self.assertIn("1時間足: 帯の妥当性", html)
        self.assertIn("15分足: 入る価格 / SL / TP", html)
        self.assertIn("time-axis-label", html)
        self.assertIn("04/10 00:00", html)
        self.assertIn("11:45", html)
        self.assertNotIn("AI補足の読み解き", html)
        self.assertNotIn("&lt;強い下方向&gt;", html)
        self.assertIn("Ver03-v4 手動確認サポート", html)
        self.assertIn("この公開HTMLレポートは現在の手動取引判断のmain UI。", html)
        self.assertIn("通知メールは入口。", html)
        self.assertIn("local dashboard / app surface は確認と将来の承認・自動化の土台。", html)
        self.assertIn("3つは同じ判断ソースから出します。別判断系にしません。", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertIn("Intraperiod JSON 契約", html)
        self.assertIn("build-active-plan-intraperiod-review --stdout-json", html)
        self.assertIn("active_plan_intraperiod_review.v1", html)
        self.assertIn("intraperiod_review_stdout_json", html)
        self.assertIn("app contract", html)
        self.assertIn("ready gate", html)
        self.assertIn("local/report-only", html)
        self.assertIn("no exchange fetch", html)
        self.assertIn("no daily-sync wiring", html)
        self.assertIn("no secret/API key reading", html)
        self.assertIn("no automatic order", html)
        self.assertIn("no FORMAL_GO", html)
        self.assertIn("Safe Config Schema Audit", html)
        self.assertIn("Operator Triage Summary", html)
        self.assertIn("Integrated Evidence Overview", html)
        self.assertIn("summary_status", html)
        self.assertIn("all_evidence_present", html)
        self.assertIn("all_evidence_ready", html)
        self.assertIn("<strong>evidence_keys:</strong>", html)
        self.assertIn(
            "intraperiod_review_stdout_json, manual_action_checklist_surface, operator_status_diagnostic, operator_triage_summary, safe_config_schema_audit",
            html,
        )
        self.assertIn("<strong>missing_evidence_keys:</strong> none", html)
        self.assertIn("<strong>not_ready_evidence_keys:</strong> none", html)
        self.assertIn("<strong>execution_required_keys:</strong> none", html)
        self.assertIn("operator_status_diagnostic present", html)
        self.assertIn("safe_config_schema_audit ready", html)
        self.assertIn("intraperiod_review_stdout_json ready", html)
        self.assertIn("manual_action_checklist_surface ready", html)
        self.assertIn("operator_triage_summary present", html)
        self.assertIn("intraperiod_review_stdout_json ready_or_valid", html)
        self.assertIn("operator_status_diagnostic execution_required", html)
        self.assertIn("safe_config_schema_audit execution_required", html)
        self.assertIn("manual_action_checklist_surface execution_required", html)
        self.assertIn("note", html)
        self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py", html)
        self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json", html)
        self.assertIn("safe_config_schema_audit.v1", html)
        self.assertIn("contract_only", html)
        self.assertIn("command_executed_by_app", html)
        self.assertIn("reads_env_values", html)
        self.assertIn("reads_dotenv_values", html)
        self.assertIn("calls_private_endpoints", html)
        self.assertIn("calls_order_endpoints", html)
        self.assertIn("live_trading_allowed", html)
        self.assertIn("secret_values_exposed", html)
        self.assertIn("local/report-only / no load_config / no .env / no os.environ / no secret/API key exposure / no exchange/private/account/order endpoint access / no FORMAL_GO / no automatic order", html)
        self.assertIn("Entry mode", html)
        self.assertIn("Entry condition", html)
        self.assertIn("TP / SL", html)
        self.assertIn("Invalidation / wait", html)
        self.assertIn("Timeout / validity", html)
        self.assertIn("Safety", html)
        self.assertIn("ロング: 監視継続。 再検討帯 65,629.02 - 65,736.78", html)
        self.assertIn("ショート: 監視継続。 再検討帯 66,418.52 - 66,587.78", html)
        self.assertIn("scripts/refresh_current_manual_delivery_app_surface.command", html)
        self.assertIn("refresh-and-check-current-manual-delivery-app-surface --stdout-json", html)
        self.assertIn("local/manual_delivery_app_surface/index.html", html)
        self.assertIn("local/manual_delivery_app_surface/app-dashboard.html", html)
        self.assertIn("local/manual_delivery_app_surface/app-ready.json", html)
        self.assertIn("local/manual_delivery_app_surface/app-snapshot.json", html)
        self.assertIn("local/manual_delivery_app_surface/app-surface-manifest.json", html)
        self.assertIn("report-only", html)
        self.assertIn("local/report-only の表示です。既存の契約/検証データだけを使い、app surface はこの概要を実行しません。", html)
        self.assertNotIn("smtp", html.lower())
        self.assertNotIn("Gmail", html)
        self.assertNotIn("send_email", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

        attention_html = build_notification_detail_html({**payload, "notification_kind": "attention"})
        self.assertIn("手動アクション確認", attention_html)
        self.assertIn("Entry mode", attention_html)
        self.assertIn("Safety", attention_html)
        self.assertIn("Ver03-v4 手動確認サポート", attention_html)
        self.assertIn("Intraperiod JSON 契約", attention_html)
        self.assertIn("build-active-plan-intraperiod-review --stdout-json", attention_html)
        self.assertIn("active_plan_intraperiod_review.v1", attention_html)
        self.assertIn("intraperiod_review_stdout_json", attention_html)
        self.assertIn("app contract", attention_html)
        self.assertIn("ready gate", attention_html)
        self.assertIn("local/report-only", attention_html)
        self.assertIn("no exchange fetch", attention_html)
        self.assertIn("no daily-sync wiring", attention_html)
        self.assertIn("no secret/API key reading", attention_html)
        self.assertIn("no automatic order", attention_html)
        self.assertIn("no FORMAL_GO", attention_html)
        self.assertIn("local/manual_delivery_app_surface/app-dashboard.html", attention_html)
        self.assertIn("Operator Triage Summary", attention_html)
        self.assertIn("Integrated Evidence Overview", attention_html)
        self.assertIn("summary_status", attention_html)
        self.assertIn("all_evidence_present", attention_html)
        self.assertIn("<strong>evidence_keys:</strong>", attention_html)
        self.assertIn(
            "intraperiod_review_stdout_json, manual_action_checklist_surface, operator_status_diagnostic, operator_triage_summary, safe_config_schema_audit",
            attention_html,
        )
        self.assertIn("<strong>missing_evidence_keys:</strong> none", attention_html)
        self.assertIn("<strong>not_ready_evidence_keys:</strong> none", attention_html)
        self.assertIn("<strong>execution_required_keys:</strong> none", attention_html)
        self.assertIn("operator_status_diagnostic ready", attention_html)
        self.assertIn("safe_config_schema_audit ready", attention_html)
        self.assertIn("manual_action_checklist_surface ready", attention_html)
        self.assertIn("intraperiod_review_stdout_json ready_or_valid", attention_html)
        self.assertIn("operator_status_diagnostic ready_or_valid", attention_html)
        self.assertIn("safe_config_schema_audit ready_or_valid", attention_html)
        self.assertIn("operator_triage_summary ready_or_valid", attention_html)
        self.assertIn("manual_action_checklist_surface ready_or_valid", attention_html)
        self.assertIn("local/report-only の表示です。既存の契約/検証データだけを使い、app surface はこの概要を実行しません。", attention_html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", attention_html)
        self.assertNotIn("smtp", attention_html.lower())
        self.assertNotIn("Gmail", attention_html)
        self.assertNotIn("send_email", attention_html)
        self.assertNotIn("private/order", attention_html)
        self.assertNotIn("automatic_order_allowed=true", attention_html)

    def test_build_notification_detail_html_renders_operator_triage_summary_from_app_surface_validation_data(self) -> None:
        payload = {
            **_sample_detail_payload(),
            "app_surface_validation_data": {
                "operator_triage_summary": {
                    "summary_status": "ready_for_human_review",
                    "all_evidence_present": True,
                    "all_evidence_ready": True,
                    "evidence": {
                        "operator_status_diagnostic": {"present": True, "ready": True},
                        "safe_config_schema_audit": {"present": True, "ready": True},
                        "intraperiod_review_stdout_json": {"present": True, "ready": True},
                        "manual_action_checklist_surface": {"present": True, "ready": True},
                    },
                    "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    "note": "derived from existing app contract data only",
                },
                "integrated_evidence_overview": {
                    "summary_status": "ready_for_human_review",
                    "all_evidence_present": True,
                    "all_evidence_ready": True,
                    "evidence": {
                        "intraperiod_review_stdout_json": {
                            "present": True,
                            "ready_or_valid": True,
                            "execution_required": False,
                        },
                        "operator_status_diagnostic": {
                            "present": True,
                            "ready_or_valid": True,
                            "execution_required": False,
                        },
                        "safe_config_schema_audit": {
                            "present": True,
                            "ready_or_valid": True,
                            "execution_required": False,
                        },
                        "operator_triage_summary": {
                            "present": True,
                            "ready_or_valid": True,
                            "execution_required": False,
                        },
                        "manual_action_checklist_surface": {
                            "present": True,
                            "ready_or_valid": True,
                            "execution_required": False,
                        },
                    },
                    "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    "note": "derived from existing app contract/status data only",
                },
            },
        }

        html = build_notification_detail_html(payload)

        self.assertIn("Operator Triage Summary", html)
        self.assertIn("Integrated Evidence Overview", html)
        self.assertIn("summary_status", html)
        self.assertIn("all_evidence_present", html)
        self.assertIn("operator_status_diagnostic present", html)
        self.assertIn("safe_config_schema_audit ready", html)
        self.assertIn("intraperiod_review_stdout_json ready", html)
        self.assertIn("manual_action_checklist_surface ready", html)
        self.assertIn("intraperiod_review_stdout_json ready_or_valid", html)
        self.assertIn("operator_status_diagnostic ready_or_valid", html)
        self.assertIn("safe_config_schema_audit ready_or_valid", html)
        self.assertIn("operator_triage_summary ready_or_valid", html)
        self.assertIn("manual_action_checklist_surface ready_or_valid", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertIn("local/report-only の表示です。既存の契約/検証データだけを使い、app surface はこの概要を実行しません。", html)
        self.assertNotIn("smtp", html.lower())
        self.assertNotIn("Gmail", html)
        self.assertNotIn("send_email", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

    def test_build_notification_detail_html_hides_operator_triage_summary_when_absent(self) -> None:
        payload = _sample_detail_payload()

        html = build_notification_detail_html(payload)

        self.assertNotIn("Operator Triage Summary", html)
        self.assertNotIn("summary_status", html)
        self.assertNotIn("all_evidence_present", html)
        self.assertNotIn("Integrated Evidence Overview", html)
        self.assertNotIn("operator_status_diagnostic present", html)
        self.assertNotIn("safe_config_schema_audit ready", html)
        self.assertNotIn("manual_action_checklist_surface ready", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SMTP_PASSWORD", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

    def test_build_notification_detail_html_hides_safe_config_schema_audit_when_absent(self) -> None:
        payload = _sample_detail_payload()

        html = build_notification_detail_html(payload)

        self.assertNotIn("Safe Config Schema Audit", html)
        self.assertNotIn("safe_config_schema_audit.v1", html)
        self.assertNotIn("Integrated Evidence Overview", html)
        self.assertIn("Ver03-v4 手動確認サポート", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SMTP_PASSWORD", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

    def test_build_notification_detail_html_shows_runtime_startup_status_section(self) -> None:
        payload = _sample_detail_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            runtime_dir = base_dir / "logs" / "runtime"
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "startup_status.json").write_text(
                json.dumps(
                    {
                        "timestamp_utc": "2026-06-23T10:06:07.884053Z",
                        "pid": 83981,
                        "timezone": "Asia/Tokyo",
                        "report_times": ["00:05", "09:05", "20:05"],
                        "next_report_time": "2026-06-23T20:05:00+09:00",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            html = build_notification_detail_html(payload, base_dir=base_dir)

        self.assertIn("Runtime startup status", html)
        self.assertIn("timestamp_utc", html)
        self.assertIn("2026-06-23T10:06:07.884053Z", html)
        self.assertIn("pid", html)
        self.assertIn("83981", html)
        self.assertIn("timezone", html)
        self.assertIn("Asia/Tokyo", html)
        self.assertIn("next_report_time", html)
        self.assertIn("2026-06-23T20:05:00+09:00", html)
        self.assertIn("report_times count", html)
        self.assertIn("3", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SMTP_PASSWORD", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

    def test_build_notification_detail_html_handles_missing_runtime_startup_status(self) -> None:
        payload = _sample_detail_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            html = build_notification_detail_html(payload, base_dir=Path(tmp_dir))

        self.assertNotIn("Runtime startup status", html)
        self.assertNotIn("startup_status.json", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SMTP_PASSWORD", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

    def test_build_notification_detail_html_handles_malformed_runtime_startup_status(self) -> None:
        payload = _sample_detail_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            runtime_dir = base_dir / "logs" / "runtime"
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "startup_status.json").write_text("{not json", encoding="utf-8")

            html = build_notification_detail_html(payload, base_dir=base_dir)

        self.assertIn("Runtime startup status", html)
        self.assertIn("startup_status.json は利用不可です。", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SMTP_PASSWORD", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

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

    def test_detail_page_enabled_includes_attention_when_html_is_enabled(self) -> None:
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
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, required_env, clear=False):
                cfg = load_config(Path(tmp_dir))

        self.assertTrue(detail_page_enabled(cfg, {"notification_kind": "attention"}))
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
                        "verdict": "caution",
                        "agreement": "caution",
                        "reason": "stub",
                        "unique_risks": ["誤読リスク"],
                        "next_review_focus": "出来高確認",
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
            "detail_page_url": "https://server.afrog.jp/btc-monitor/notifications/ver02-4-v1/main/20260331_030500.html",
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
        self.assertIn("https://server.afrog.jp/btc-monitor/notifications/ver02-4-v1/main/20260331_030500.html", captured["body"])
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
                        "verdict": "caution",
                        "agreement": "caution",
                        "reason": "stub",
                        "unique_risks": ["誤読リスク"],
                        "next_review_focus": "出来高確認",
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

    def test_publish_notification_detail_uses_stable_ip_host(self) -> None:
        cfg = SimpleNamespace(
            NOTIFICATION_HTML_LOCAL_DIR="logs/notifications_html",
            NOTIFICATION_HTML_PUBLIC_BASE_URL="https://server.afrog.jp/btc-monitor/notifications",
            NOTIFICATION_HTML_REMOTE_SSH_HOST="maruPro@192.168.50.5",
            NOTIFICATION_HTML_REMOTE_SSH_KEY="~/.ssh/id_ed25519_afrog_lan",
            NOTIFICATION_HTML_REMOTE_DIR="/Volumes/Server_HD2/site/btc-monitor/notifications",
        )
        result = {
            "signal_id": "20260403_090500",
            "system_label": "Ver02.4-v1",
            "notification_kind": "main",
            "summary_subject": "subject",
        }
        calls: list[list[str]] = []

        def _fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "", "")

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            with patch("src.notification.detail_page.subprocess.run", side_effect=_fake_run):
                publish_info = publish_notification_detail(base_dir, cfg, result)

        self.assertEqual(publish_info["detail_page_status"], "published")
        self.assertEqual(publish_info["detail_page_remote_host"], "maruPro@192.168.50.5")
        self.assertIn(
            [
                "ssh",
                "-o",
                "IdentitiesOnly=yes",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=5",
                "-i",
                str(Path("~/.ssh/id_ed25519_afrog_lan").expanduser()),
                "maruPro@192.168.50.5",
                "mkdir",
                "-p",
                "/Volumes/Server_HD2/site/btc-monitor/notifications/ver02-4-v1/main",
            ],
            calls,
        )


if __name__ == "__main__":
    unittest.main()
