from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import (
    VER03_V4_EMAIL_SUBJECT_PREFIX,
    _apply_ver03_v4_subject_prefix,
    build_summary_body,
    build_summary_subject,
)


class SummaryFormatTest(unittest.TestCase):
    def test_ready_case_separates_direction_and_execution(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "API",
            "prelabel": "ENTRY_OK",
            "signal_tier": "strong_machine",
            "bias": "long",
            "current_price": 70356.3,
            "confidence": 79,
            "rr_estimate": 1.85,
            "confidence_direction_shadow": 88.0,
            "confidence_execution_shadow": 72.0,
            "confidence_wait_shadow": 18.0,
            "phase": "pullback",
            "long_display_score": 72,
            "short_display_score": 55,
            "score_gap": 17,
            "market_regime": "uptrend",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "long",
            "funding_rate_display": "ほぼ中立 (+0.0037%)",
            "atr_ratio": 0.85,
            "volume_ratio": 1.21,
            "support_zones": [{"low": 69900.0, "high": 70010.0, "distance_from_price": 346.3}],
            "resistance_zones": [{"low": 70450.0, "high": 70600.0, "distance_from_price": 93.7}],
            "long_setup": {
                "status": "ready",
                "entry_zone": {"low": 70000.0, "high": 70100.0},
                "stop_loss": 69700.0,
                "tp1": 70800.0,
                "tp2": 71200.0,
            },
            "short_setup": {
                "status": "watch",
                "entry_zone": {"low": 70600.0, "high": 70700.0},
                "stop_loss": 70900.0,
                "tp1": 70000.0,
                "tp2": 69500.0,
            },
            "primary_setup_status": "ready",
            "primary_setup_reason": "inside_entry_zone_with_trigger",
            "trade_execution_gate": "pass",
            "paper_order_status": "draft",
            "warning_flags": [],
            "risk_flags": [],
            "no_trade_flags": [],
            "ai_advice": {
                "decision": "LONG",
                "quality": "A",
                "confidence": 0.82,
                "primary_reason": "上方向は維持だが断定ではなく条件付きで見る局面。",
                "next_condition": "出来高維持を確認",
                "warnings": [],
            },
            "app_contract_data": {
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
                        "local/report-only / no load_config / no .env read / no os.environ value read / "
                        "no secret/API key exposure / no exchange/private/account/order endpoint access / "
                        "no FORMAL_GO / no automatic order"
                    ),
                },
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
        }

        subject = build_summary_subject(payload)
        body, provider_used = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertEqual(provider_used, "api")
        self.assertTrue(subject.startswith(f"{VER03_V4_EMAIL_SUBJECT_PREFIX} 📊 [通常監視・実行不可] "))
        self.assertNotIn("[BTCFX Ver03-v2]", subject)
        self.assertIn("上方向バイアス", subject)
        self.assertIn("【BTC:70,356】 2026-03-11 09:05 [Ver02.3] [API]", subject)
        self.assertNotIn("条件付きで検討 |", subject)
        self.assertNotIn("総合強度", subject)
        self.assertIn("これは執行候補です。", body)
        self.assertIn("paper_order_status: draft", body)
        self.assertIn("最終ランク: 📊 通常監視・実行不可（監視と再評価のための通知です）", body)
        self.assertIn("補足状態: 執行可（条件成立）", body)
        self.assertIn("方向判断: 相場は上方向バイアスです", body)
        self.assertIn("執行判断: 条件付きで検討", body)
        self.assertIn("現値帯の扱い: 現値帯のみ条件付き", body)
        self.assertIn("方向の強さ: 88.0", body)
        self.assertIn("実行しやすさ: 72.0", body)
        self.assertIn("待機圧力: 18.0", body)
        self.assertIn("位置評価: 位置条件は悪くない", body)
        self.assertIn("【ロング/ショートのセットアップ状況】", body)
        self.assertIn("【手動アクション確認】", body)
        self.assertIn("Entry mode", body)
        self.assertIn("Entry condition", body)
        self.assertIn("TP / SL", body)
        self.assertIn("Invalidation / wait", body)
        self.assertIn("Timeout / validity", body)
        self.assertIn("Safety", body)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", body)
        self.assertIn("【ローカル確認】", body)
        self.assertIn("scripts/refresh_current_manual_delivery_app_surface.command", body)
        self.assertIn("refresh-and-check-current-manual-delivery-app-surface --stdout-json", body)
        self.assertIn("local/manual_delivery_app_surface/index.html", body)
        self.assertIn("local/manual_delivery_app_surface/app-dashboard.html", body)
        self.assertIn("local/manual_delivery_app_surface/app-ready.json", body)
        self.assertIn("local/manual_delivery_app_surface/app-snapshot.json", body)
        self.assertIn("local/manual_delivery_app_surface/app-surface-manifest.json", body)
        self.assertIn("自動発注なし / 通知送信追加なし / 最終判断は人間", body)
        self.assertIn("【Safe Config Schema Audit】", body)
        self.assertIn("local/report-only / no load_config / no .env read / no os.environ value read / no secret/API key exposure / no exchange/private/account/order endpoint access / no FORMAL_GO / no automatic order", body)
        self.assertIn("command: ./.venv312/bin/python tools/safe_config_schema_audit.py", body)
        self.assertIn("stdout_json_command: ./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json", body)
        self.assertIn("schema_version: safe_config_schema_audit.v1", body)
        self.assertIn("contract_only: true", body)
        self.assertIn("command_executed_by_app: false", body)
        self.assertIn("reads_env_values: false", body)
        self.assertIn("reads_dotenv_values: false", body)
        self.assertIn("calls_private_endpoints: false", body)
        self.assertIn("calls_order_endpoints: false", body)
        self.assertIn("live_trading_allowed: false", body)
        self.assertIn("secret_values_exposed: false", body)
        self.assertIn("【Operator Triage Summary】", body)
        self.assertIn("summary_status: ready_for_human_review", body)
        self.assertIn("all_evidence_present: true", body)
        self.assertIn("all_evidence_ready: true", body)
        self.assertIn("operator_status_diagnostic present: true", body)
        self.assertIn("operator_status_diagnostic ready: true", body)
        self.assertIn("safe_config_schema_audit present: true", body)
        self.assertIn("safe_config_schema_audit ready: true", body)
        self.assertIn("intraperiod_review_stdout_json present: true", body)
        self.assertIn("intraperiod_review_stdout_json ready: true", body)
        self.assertIn("manual_action_checklist_surface present: true", body)
        self.assertIn("manual_action_checklist_surface ready: true", body)
        self.assertIn("safety_boundary: report-only / not FORMAL_GO / no automatic order / human decides manually", body)
        self.assertIn("note: derived from existing app contract data only", body)
        self.assertIn("【Integrated Evidence Overview】", body)
        self.assertIn("summary_status: ready_for_human_review", body)
        self.assertIn("all_evidence_present: true", body)
        self.assertIn("all_evidence_ready: true", body)
        self.assertIn("intraperiod_review_stdout_json ready_or_valid: true", body)
        self.assertIn("operator_status_diagnostic ready_or_valid: true", body)
        self.assertIn("safe_config_schema_audit ready_or_valid: true", body)
        self.assertIn("operator_triage_summary ready_or_valid: true", body)
        self.assertIn("manual_action_checklist_surface ready_or_valid: true", body)
        self.assertIn("note: derived from existing app contract/status data only", body)
        self.assertNotIn("smtp", body.lower())
        self.assertNotIn("Gmail", body)
        self.assertNotIn("send_email", body)
        self.assertNotIn("private/order", body)
        self.assertNotIn("automatic_order_allowed=true", body)

    def test_active_plan_subject_prefers_ver03_v4_prefix(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "API",
            "prelabel": "ENTRY_OK",
            "signal_tier": "strong_machine",
            "bias": "long",
            "current_price": 70356.3,
            "confidence": 79,
            "rr_estimate": 1.85,
            "confidence_direction_shadow": 88.0,
            "confidence_execution_shadow": 72.0,
            "confidence_wait_shadow": 18.0,
            "phase": "pullback",
            "long_display_score": 72,
            "short_display_score": 55,
            "score_gap": 17,
            "market_regime": "uptrend",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "long",
            "funding_rate_display": "ほぼ中立 (+0.0037%)",
            "atr_ratio": 0.85,
            "volume_ratio": 1.21,
            "support_zones": [{"low": 69900.0, "high": 70010.0, "distance_from_price": 346.3}],
            "resistance_zones": [{"low": 70450.0, "high": 70600.0, "distance_from_price": 93.7}],
            "long_setup": {
                "status": "ready",
                "entry_zone": {"low": 70000.0, "high": 70100.0},
                "stop_loss": 69700.0,
                "tp1": 70800.0,
                "tp2": 71200.0,
            },
            "short_setup": {
                "status": "watch",
                "entry_zone": {"low": 70600.0, "high": 70700.0},
                "stop_loss": 70900.0,
                "tp1": 70000.0,
                "tp2": 69500.0,
            },
            "primary_setup_status": "ready",
            "primary_setup_reason": "inside_entry_zone_with_trigger",
            "trade_execution_gate": "pass",
            "paper_order_status": "draft",
            "warning_flags": [],
            "risk_flags": [],
            "no_trade_flags": [],
            "ai_advice": {
                "decision": "LONG",
                "quality": "A",
                "confidence": 0.82,
                "primary_reason": "上方向は維持だが断定ではなく条件付きで見る局面。",
                "next_condition": "出来高維持を確認",
                "warnings": [],
            },
            "app_contract_data": {
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
                        "local/report-only / no load_config / no .env read / no os.environ value read / "
                        "no secret/API key exposure / no exchange/private/account/order endpoint access / "
                        "no FORMAL_GO / no automatic order"
                    ),
                },
            },
            "active_primary_action": "ACTIVE_LIMIT_RETEST",
            "active_headline": "押し目待ちで監視",
        }

        subject = build_summary_subject(payload)

        self.assertTrue(subject.startswith(f"{VER03_V4_EMAIL_SUBJECT_PREFIX} 📊 [通常監視・実行不可] "))
        self.assertIn("押し目買い待ち / 実弾不可・行動計画 | 押し目待ちで監視", subject)
        self.assertIn("【BTC:70,356】 2026-03-11 09:05 [Ver02.3] [API]", subject)

    def test_attention_subject_and_body_are_wait_first(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-15T06:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "CLI",
            "notification_kind": "attention",
            "bias": "short",
            "current_price": 70765.2,
            "long_display_score": 38,
            "short_display_score": 59,
            "score_gap": -21,
            "signals_4h": "wait",
            "signals_1h": "short",
            "signals_15m": "wait",
            "prelabel": "SWEEP_WAIT",
            "primary_setup_status": "watch",
            "primary_setup_reason": "near_entry_zone_waiting_trigger",
            "confidence": 41,
            "confidence_direction_shadow": 62.0,
            "confidence_execution_shadow": 28.0,
            "confidence_wait_shadow": 64.0,
            "warning_flags": ["Critical_zone_warning"],
            "risk_flags": ["upper_liquidity_close"],
            "no_trade_flags": ["sweep_incomplete"],
            "app_contract_data": {
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
                        "local/report-only / no load_config / no .env read / no os.environ value read / "
                        "no secret/API key exposure / no exchange/private/account/order endpoint access / "
                        "no FORMAL_GO / no automatic order"
                    ),
                },
            },
        }

        subject = build_summary_subject(payload)
        body, provider_used = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )
        self.assertEqual(provider_used, "api")
        self.assertTrue(subject.startswith(f"{VER03_V4_EMAIL_SUBJECT_PREFIX} [機械判定のみ] 👀 [注意報・売買非推奨] "))
        self.assertNotIn("[BTCFX Ver03-v2]", subject)
        self.assertIn("下方向バイアス", subject)
        self.assertNotIn("🔥", subject)
        self.assertNotIn("🟠", subject)
        self.assertNotIn("📊", subject)
        self.assertNotIn("総合強度", subject)
        self.assertIn("これは売買推奨メールではありません。", body)
        self.assertIn("最終ランク: 👀 注意報・売買非推奨（方向変化の早期共有。売買推奨ではありません）", body)
        self.assertIn("補足状態: 注意報（方向変化の早期共有）", body)
        self.assertIn("上側流動性スイープ完了後に再評価", body)
        self.assertIn("方向の強さ: 62.0", body)
        self.assertIn("実行しやすさ: 28.0", body)
        self.assertIn("待機圧力: 64.0", body)
        self.assertIn("方向判断: 相場は下方向バイアスです", body)
        self.assertIn("【手動アクション確認】", body)
        self.assertIn("Entry mode", body)
        self.assertIn("Entry condition", body)
        self.assertIn("TP / SL", body)
        self.assertIn("Invalidation / wait", body)
        self.assertIn("Timeout / validity", body)
        self.assertIn("Safety", body)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", body)
        self.assertIn("【ローカル確認】", body)
        self.assertIn("scripts/refresh_current_manual_delivery_app_surface.command", body)
        self.assertIn("refresh-and-check-current-manual-delivery-app-surface --stdout-json", body)
        self.assertIn("local/manual_delivery_app_surface/index.html", body)
        self.assertIn("local/manual_delivery_app_surface/app-dashboard.html", body)
        self.assertIn("local/manual_delivery_app_surface/app-ready.json", body)
        self.assertIn("local/manual_delivery_app_surface/app-snapshot.json", body)
        self.assertIn("local/manual_delivery_app_surface/app-surface-manifest.json", body)
        self.assertIn("自動発注なし / 通知送信追加なし / 最終判断は人間", body)
        self.assertIn("【Safe Config Schema Audit】", body)
        self.assertIn("command: ./.venv312/bin/python tools/safe_config_schema_audit.py", body)
        self.assertIn("stdout_json_command: ./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json", body)
        self.assertIn("schema_version: safe_config_schema_audit.v1", body)
        self.assertIn("contract_only: true", body)
        self.assertIn("command_executed_by_app: false", body)
        self.assertIn("reads_env_values: false", body)
        self.assertIn("reads_dotenv_values: false", body)
        self.assertIn("calls_private_endpoints: false", body)
        self.assertIn("calls_order_endpoints: false", body)
        self.assertIn("live_trading_allowed: false", body)
        self.assertIn("secret_values_exposed: false", body)
        self.assertIn("【Operator Triage Summary】", body)
        self.assertIn("summary_status: ready_for_human_review", body)
        self.assertIn("operator_status_diagnostic present: true", body)
        self.assertIn("safe_config_schema_audit ready: true", body)
        self.assertIn("manual_action_checklist_surface ready: true", body)
        self.assertIn("local/report-only / no load_config / no .env read / no os.environ value read / no secret/API key exposure / no exchange/private/account/order endpoint access / no FORMAL_GO / no automatic order", body)
        self.assertNotIn("smtp", body.lower())
        self.assertNotIn("Gmail", body)
        self.assertNotIn("send_email", body)
        self.assertNotIn("private/order", body)
        self.assertNotIn("automatic_order_allowed=true", body)
        self.assertNotIn("入る条件がかなりそろっています", body)

    def test_attention_summary_body_renders_operator_triage_summary_from_app_surface_validation_data(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-15T06:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "CLI",
            "notification_kind": "attention",
            "bias": "short",
            "current_price": 70765.2,
            "long_display_score": 38,
            "short_display_score": 59,
            "score_gap": -21,
            "signals_4h": "wait",
            "signals_1h": "short",
            "signals_15m": "wait",
            "prelabel": "SWEEP_WAIT",
            "primary_setup_status": "watch",
            "primary_setup_reason": "near_entry_zone_waiting_trigger",
            "confidence": 41,
            "confidence_direction_shadow": 62.0,
            "confidence_execution_shadow": 28.0,
            "confidence_wait_shadow": 64.0,
            "warning_flags": ["Critical_zone_warning"],
            "risk_flags": ["upper_liquidity_close"],
            "no_trade_flags": ["sweep_incomplete"],
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

        body, _provider_used = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertIn("【Operator Triage Summary】", body)
        self.assertIn("summary_status: ready_for_human_review", body)
        self.assertIn("operator_status_diagnostic present: true", body)
        self.assertIn("safe_config_schema_audit ready: true", body)
        self.assertIn("manual_action_checklist_surface ready: true", body)
        self.assertIn("【Integrated Evidence Overview】", body)
        self.assertIn("summary_status: ready_for_human_review", body)
        self.assertIn("all_evidence_present: true", body)
        self.assertIn("all_evidence_ready: true", body)
        self.assertIn("intraperiod_review_stdout_json present: true", body)
        self.assertIn("intraperiod_review_stdout_json ready_or_valid: true", body)
        self.assertIn("operator_status_diagnostic ready_or_valid: true", body)
        self.assertIn("safe_config_schema_audit ready_or_valid: true", body)
        self.assertIn("operator_triage_summary ready_or_valid: true", body)
        self.assertIn("manual_action_checklist_surface ready_or_valid: true", body)
        self.assertIn("safety_boundary: report-only / not FORMAL_GO / no automatic order / human decides manually", body)
        self.assertIn("note: derived from existing app contract/status data only", body)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", body)
        self.assertNotIn("smtp", body.lower())
        self.assertNotIn("Gmail", body)
        self.assertNotIn("send_email", body)
        self.assertNotIn("private/order", body)
        self.assertNotIn("automatic_order_allowed=true", body)

    def test_operator_triage_summary_is_hidden_when_absent(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "API",
            "prelabel": "ENTRY_OK",
            "signal_tier": "strong_machine",
            "bias": "long",
            "current_price": 70356.3,
            "confidence": 79,
            "rr_estimate": 1.85,
            "confidence_direction_shadow": 88.0,
            "confidence_execution_shadow": 72.0,
            "confidence_wait_shadow": 18.0,
            "phase": "pullback",
            "long_display_score": 72,
            "short_display_score": 55,
            "score_gap": 17,
            "market_regime": "uptrend",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "long",
            "funding_rate_display": "ほぼ中立 (+0.0037%)",
            "atr_ratio": 0.85,
            "volume_ratio": 1.21,
            "support_zones": [{"low": 69900.0, "high": 70010.0, "distance_from_price": 346.3}],
            "resistance_zones": [{"low": 70450.0, "high": 70600.0, "distance_from_price": 93.7}],
            "long_setup": {
                "status": "ready",
                "entry_zone": {"low": 70000.0, "high": 70100.0},
                "stop_loss": 69700.0,
                "tp1": 70800.0,
                "tp2": 71200.0,
            },
            "short_setup": {
                "status": "watch",
                "entry_zone": {"low": 70600.0, "high": 70700.0},
                "stop_loss": 70900.0,
                "tp1": 70000.0,
                "tp2": 69500.0,
            },
            "primary_setup_status": "ready",
            "primary_setup_reason": "inside_entry_zone_with_trigger",
            "trade_execution_gate": "pass",
            "paper_order_status": "draft",
            "warning_flags": [],
            "risk_flags": [],
            "no_trade_flags": [],
            "ai_advice": {
                "decision": "LONG",
                "quality": "A",
                "confidence": 0.82,
                "primary_reason": "上方向は維持だが断定ではなく条件付きで見る局面。",
                "next_condition": "出来高維持を確認",
                "warnings": [],
            },
        }

        body, _provider_used = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertNotIn("【Operator Triage Summary】", body)
        self.assertNotIn("【Integrated Evidence Overview】", body)
        self.assertNotIn("operator_status_diagnostic present:", body)
        self.assertNotIn("safe_config_schema_audit ready:", body)

    def test_operator_triage_summary_is_rendered_from_app_surface_validation_data(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "API",
            "prelabel": "ENTRY_OK",
            "signal_tier": "strong_machine",
            "bias": "long",
            "current_price": 70356.3,
            "confidence": 79,
            "rr_estimate": 1.85,
            "confidence_direction_shadow": 88.0,
            "confidence_execution_shadow": 72.0,
            "confidence_wait_shadow": 18.0,
            "phase": "pullback",
            "long_display_score": 72,
            "short_display_score": 55,
            "score_gap": 17,
            "market_regime": "uptrend",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "long",
            "funding_rate_display": "ほぼ中立 (+0.0037%)",
            "atr_ratio": 0.85,
            "volume_ratio": 1.21,
            "support_zones": [{"low": 69900.0, "high": 70010.0, "distance_from_price": 346.3}],
            "resistance_zones": [{"low": 70450.0, "high": 70600.0, "distance_from_price": 93.7}],
            "long_setup": {
                "status": "ready",
                "entry_zone": {"low": 70000.0, "high": 70100.0},
                "stop_loss": 69700.0,
                "tp1": 70800.0,
                "tp2": 71200.0,
            },
            "short_setup": {
                "status": "watch",
                "entry_zone": {"low": 70600.0, "high": 70700.0},
                "stop_loss": 70900.0,
                "tp1": 70000.0,
                "tp2": 69500.0,
            },
            "primary_setup_status": "ready",
            "primary_setup_reason": "inside_entry_zone_with_trigger",
            "trade_execution_gate": "pass",
            "paper_order_status": "draft",
            "warning_flags": [],
            "risk_flags": [],
            "no_trade_flags": [],
            "ai_advice": {
                "decision": "LONG",
                "quality": "A",
                "confidence": 0.82,
                "primary_reason": "上方向は維持だが断定ではなく条件付きで見る局面。",
                "next_condition": "出来高維持を確認",
                "warnings": [],
            },
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
                }
            },
        }

        body, _provider_used = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertIn("【Operator Triage Summary】", body)
        self.assertIn("summary_status: ready_for_human_review", body)
        self.assertIn("operator_status_diagnostic present: true", body)
        self.assertIn("safe_config_schema_audit ready: true", body)
        self.assertIn("manual_action_checklist_surface ready: true", body)
        self.assertNotIn("smtp", body.lower())
        self.assertNotIn("send_email", body)
        self.assertNotIn("private/order", body)
        self.assertNotIn("automatic_order_allowed=true", body)

    def test_machine_only_subject_warns_and_body_hides_internal_codes(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-17T03:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "CLI",
            "prelabel": "SWEEP_WAIT",
            "bias": "short",
            "signal_tier": "normal",
            "primary_setup_status": "watch",
            "primary_setup_reason": "near_entry_zone_waiting_trigger",
            "trade_execution_gate": "blocked",
            "phase1_observation_gate": "pass",
            "phase1_observation_type": "setup_watch_learning",
            "current_price": 73911.8,
            "confidence": 66,
            "rr_estimate": 1.18,
            "confidence_direction_shadow": 74.0,
            "confidence_execution_shadow": 31.0,
            "confidence_wait_shadow": 58.0,
            "warning_flags": [],
            "risk_flags": ["bid_wall_close", "upper_liquidity_close"],
            "no_trade_flags": ["sweep_incomplete"],
            "long_setup": {"status": "invalid", "entry_zone": {"low": 73349.0, "high": 73683.0}, "stop_loss": 73051.0, "tp1": 73734.0, "tp2": 74892.0},
            "short_setup": {"status": "watch", "entry_zone": {"low": 73734.0, "high": 74104.0}, "stop_loss": 74557.0, "tp1": 73683.0, "tp2": 72506.0},
            "ai_advice": None,
        }

        subject = build_summary_subject(payload)
        body, _provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertTrue(subject.startswith(f"{VER03_V4_EMAIL_SUBJECT_PREFIX} [機械判定のみ] "))
        self.assertIn("🟠 [高優先監視・実行不可]", subject)
        self.assertIn("下方向バイアス", body)
        self.assertIn("方向・構造は強いため、高優先で監視する通知です。", body)
        self.assertIn("観測タイプ: setup_watch_learning", body)
        self.assertIn("最終ランク: 🟠 高優先監視・実行不可（方向・構造は強いが、実行候補ではありません）", body)
        self.assertIn("補足状態: 監視（条件接近）", body)
        self.assertNotIn("総合強度", subject)
        self.assertIn("上側流動性スイープ完了後に再評価", body)
        self.assertIn("近い買い板があり短期ノイズに注意", body)
        self.assertIn("上側流動性が近く先に振られやすい", body)
        self.assertNotIn("bid_wall_close", body)
        self.assertNotIn("upper_liquidity_close", body)
        self.assertNotIn("【Safe Config Schema Audit】", body)

    def test_ver03_v4_subject_prefix_helper_strips_and_does_not_duplicate(self) -> None:
        already_prefixed = f"  {VER03_V4_EMAIL_SUBJECT_PREFIX} 既存件名  "
        self.assertEqual(
            _apply_ver03_v4_subject_prefix(already_prefixed),
            f"{VER03_V4_EMAIL_SUBJECT_PREFIX} 既存件名",
        )
        self.assertEqual(
            _apply_ver03_v4_subject_prefix("  既存件名  "),
            f"{VER03_V4_EMAIL_SUBJECT_PREFIX} 既存件名",
        )

    def test_entry_ok_invalid_is_not_presented_as_strong_entry(self) -> None:
        payload = {
            "timestamp_jst": "2026-04-04T20:05:00+09:00",
            "system_label": "Ver02.4-v1",
            "system_mode_label": "CLI",
            "prelabel": "ENTRY_OK",
            "bias": "short",
            "signal_tier": "normal",
            "primary_setup_status": "invalid",
            "primary_setup_reason": "rr_below_min",
            "current_price": 70200.0,
            "confidence": 52,
            "rr_estimate": 1.05,
            "score_gap": 12,
            "confidence_direction_shadow": 74.0,
            "confidence_execution_shadow": 22.0,
            "confidence_wait_shadow": 61.0,
            "warning_flags": ["Critical_zone_warning"],
            "risk_flags": ["upper_liquidity_close"],
            "no_trade_flags": ["RR_insufficient_short", "RR_insufficient"],
        }

        subject = build_summary_subject(payload)
        body, _provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertIn("📊 [通常監視・実行不可]", subject)
        self.assertNotIn("🟠 [高め本通知]", subject)
        self.assertIn("位置評価: 位置は悪くないがRR未成立", body)
        self.assertIn("執行判断: 見送り", body)

    def test_entry_ok_invalid_confidence_reason_is_labeled_as_strength_unmet(self) -> None:
        payload = {
            "timestamp_jst": "2026-04-04T20:05:00+09:00",
            "system_label": "Ver02.4-v1",
            "system_mode_label": "CLI",
            "prelabel": "ENTRY_OK",
            "bias": "long",
            "signal_tier": "normal",
            "primary_setup_status": "invalid",
            "primary_setup_reason": "confidence_below_min",
            "current_price": 70200.0,
            "confidence": 40,
            "rr_estimate": 1.4,
            "score_gap": 12,
            "confidence_direction_shadow": 70.0,
            "confidence_execution_shadow": 30.0,
            "confidence_wait_shadow": 55.0,
            "warning_flags": [],
            "risk_flags": [],
            "no_trade_flags": [],
        }

        body, _provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertIn("位置評価: 位置は悪くないが強度未成立", body)

    def test_watch_blocked_long_reversal_is_presented_as_monitoring_not_long_entry(self) -> None:
        payload = {
            "timestamp_jst": "2026-04-29T19:05:00+09:00",
            "system_label": "Ver02.5-v5",
            "system_mode_label": "CLI",
            "notification_kind": "main",
            "prelabel": "ENTRY_OK",
            "bias": "long",
            "signal_tier": "normal",
            "trade_execution_gate": "blocked",
            "primary_setup_status": "watch",
            "primary_setup_reason": "entry_zone_not_reached",
            "current_price": 77605.5,
            "confidence": 68,
            "rr_estimate": 1.35,
            "score_gap": 42,
            "confidence_direction_shadow": 92.0,
            "confidence_execution_shadow": 24.0,
            "confidence_wait_shadow": 78.0,
            "warning_flags": [],
            "risk_flags": ["sweep_incomplete", "lower_liquidity_close", "long_reversal_risk"],
            "no_trade_flags": [],
            "market_regime": "transition",
            "phase": "breakout",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "short",
            "long_display_score": 92,
            "short_display_score": 50,
            "long_setup": {"status": "watch", "entry_zone": {"low": 77100.0, "high": 77300.0}, "stop_loss": 76800.0, "tp1": 78100.0, "tp2": 78600.0},
            "short_setup": {"status": "watch", "entry_zone": {"low": 77680.0, "high": 77850.0}, "stop_loss": 78150.0, "tp1": 77100.0, "tp2": 76700.0},
            "ai_advice": None,
        }

        subject = build_summary_subject(payload)
        body, _provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertIn("📊 [通常監視・実行不可]", subject)
        self.assertNotIn("🟠 [高め本通知]", subject)
        self.assertIn("上方向監視", subject)
        self.assertIn("下落警戒", subject)
        self.assertIn("これは実行候補ではありません。", body)
        self.assertIn("通常監視と再評価のための通知です。", body)
        self.assertIn("執行判断: 監視継続（実行不可）", body)
        self.assertIn("位置評価: 位置は悪くないが未到達", body)
        self.assertIn("最終ランク: 📊 通常監視・実行不可（監視と再評価のための通知です）", body)

    def test_normal_summary_body_surfaces_actionability_section_near_top(self) -> None:
        payload = {
            "timestamp_jst": "2026-06-12T10:05:00+09:00",
            "system_label": "Ver03-v3",
            "system_mode_label": "CLI",
            "prelabel": "ENTRY_OK",
            "bias": "long",
            "signal_tier": "normal",
            "primary_setup_status": "ready",
            "primary_setup_reason": "inside_entry_zone_with_trigger",
            "trade_execution_gate": "blocked",
            "phase1_observation_gate": "blocked",
            "current_price": 70200.0,
            "confidence_direction_shadow": 74.0,
            "confidence_execution_shadow": 41.0,
            "confidence_wait_shadow": 22.0,
            "warning_flags": [],
            "risk_flags": [],
            "no_trade_flags": [],
            "actionability_label": "ACTIONABLE_COPY_READY",
            "human_action": "manual_copy_review",
            "actionability_reasons": ["deterministic_checks_passed"],
            "actionability_safety": "report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually",
            "active_primary_action": "ACTIVE_LIMIT_RETEST",
            "active_headline": "押し目待ちで監視",
        }

        body, _provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertIn("【行動判定】", body)
        self.assertIn("判定: 手動確認すれば行動候補", body)
        self.assertIn("次の行動: 内容を確認して、手動で判断", body)
        self.assertIn("理由:", body)
        self.assertIn("決定的チェックを通過", body)
        self.assertIn("安全:", body)
        self.assertIn("これは正式GOではありません", body)
        self.assertIn("自動発注はしません", body)
        self.assertIn("最終判断は人間が行います", body)
        self.assertIn("機械判定:", body)
        self.assertIn("actionability_label: ACTIONABLE_COPY_READY", body)
        self.assertIn("human_action: manual_copy_review", body)
        self.assertIn("actionability_reasons: deterministic_checks_passed", body)
        self.assertIn(
            "actionability_safety: report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually",
            body,
        )
        self.assertLess(body.index("【行動判定】"), body.index("【実行ゲート】"))

    def test_attention_summary_body_surfaces_non_actionable_actionability_section(self) -> None:
        payload = {
            "timestamp_jst": "2026-06-12T11:05:00+09:00",
            "system_label": "Ver03-v3",
            "system_mode_label": "CLI",
            "notification_kind": "attention",
            "prelabel": "SWEEP_WAIT",
            "bias": "short",
            "current_price": 70123.4,
            "long_display_score": 42,
            "short_display_score": 61,
            "score_gap": -19,
            "signals_4h": "wait",
            "signals_1h": "short",
            "signals_15m": "wait",
            "primary_setup_status": "watch",
            "primary_setup_reason": "near_entry_zone_waiting_trigger",
            "confidence_direction_shadow": 58.0,
            "confidence_execution_shadow": 18.0,
            "confidence_wait_shadow": 71.0,
            "warning_flags": [],
            "risk_flags": ["upper_liquidity_close"],
            "no_trade_flags": [],
            "actionability_label": "AUTO_REJECT",
            "human_action": "do_nothing",
            "actionability_reasons": ["source_not_ready:review_required_data_quality_not_ok"],
            "actionability_safety": "report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually",
        }

        body, _provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertIn("【行動判定】", body)
        self.assertIn("判定: 行動候補から除外。今回は見送り", body)
        self.assertIn("次の行動: 何もしない", body)
        self.assertIn("データ鮮度または入力状態が不十分", body)
        self.assertIn("actionability_label: AUTO_REJECT", body)
        self.assertIn("human_action: do_nothing", body)
        self.assertIn("actionability_reasons: source_not_ready:review_required_data_quality_not_ok", body)
        self.assertIn(
            "actionability_safety: report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually",
            body,
        )
        self.assertIn("これは正式GOではありません", body)
        self.assertIn("自動発注はしません", body)
        self.assertIn("最終判断は人間が行います", body)
        self.assertLess(body.index("【行動判定】"), body.index("【実行ゲート】"))
