from __future__ import annotations

import json
import os
import re
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
from src.ai.summary import build_summary_subject
from src.data.exchange_fetcher import MarketStructureSnapshot
from src.analysis.value_defense_entry_layer import build_value_defense_entry_layer
from src.notification.detail_page import (
    build_notification_detail_html,
    detail_page_enabled,
    detail_page_paths,
    publish_notification_detail,
    _operator_dashboard_relative_balance,
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
    payload: dict[str, object] = {
        "signal_id": "20260331_010500",
        "timestamp_jst": "2026-03-31T01:05:00+09:00",
        "summary_subject": "",
        "system_label": "Ver02.6-v2",
        "system_mode_label": "CLI",
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
    payload["long_setup"]["value_defense_entry_layer"] = build_value_defense_entry_layer(
        side="long",
        price=payload["current_price"],
        atr=100.0,
        setup={
            "status": payload["long_setup"]["status"],
            "entry_zone": payload["long_setup"]["entry_zone"],
            "entry_mid": 65682.9,
            "stop_loss": payload["long_setup"]["stop_loss"],
        },
        support_zones=[
            {"low": 65629.02, "high": 65736.78, "strength": 4},
            {"low": 65480.0, "high": 65518.0, "strength": 7},
        ],
        resistance_zones=[
            {"low": 66418.52, "high": 66587.78, "strength": 5},
            {"low": 66790.0, "high": 66840.0, "strength": 4},
        ],
    )
    payload["short_setup"]["value_defense_entry_layer"] = build_value_defense_entry_layer(
        side="short",
        price=payload["current_price"],
        atr=100.0,
        setup={
            "status": payload["short_setup"]["status"],
            "entry_zone": payload["short_setup"]["entry_zone"],
            "entry_mid": 66503.15,
            "stop_loss": payload["short_setup"]["stop_loss"],
        },
        support_zones=[
            {"low": 65629.02, "high": 65736.78, "strength": 4},
            {"low": 65480.0, "high": 65518.0, "strength": 7},
        ],
        resistance_zones=[
            {"low": 66418.52, "high": 66587.78, "strength": 5},
            {"low": 66790.0, "high": 66840.0, "strength": 4},
            {"low": 66980.0, "high": 67010.0, "strength": 3},
        ],
    )
    payload["summary_subject"] = build_summary_subject(payload)
    return payload


def _sample_breakout_inversion_payload() -> dict[str, object]:
    payload = _sample_detail_payload()
    payload["breakout_inversion_flags"] = [
        "upside_breakout_follow_watch",
        "short_invalidation_watch",
        "missed_upside_breakout_watch",
        "downside_breakdown_follow_watch",
        "long_invalidation_watch",
        "missed_downside_breakdown_watch",
    ]
    payload["short_setup"] = {
        **payload["short_setup"],
        "execution_precision_flags": ["short_invalidated_by_up_break", "upside_breakout_follow_watch"],
        "execution_precision_reason": "上抜けが出ているため、ショート根拠は弱まりました。15分足で上方向の維持を確認します",
    }
    payload["long_setup"] = {
        **payload["long_setup"],
        "execution_precision_flags": ["long_invalidated_by_down_break", "downside_breakdown_follow_watch"],
        "execution_precision_reason": "下抜けが出ているため、ロング根拠は弱まりました。15分足で下方向の維持を確認します",
    }
    return payload


def _sample_momentum_payload() -> dict[str, object]:
    payload = _sample_breakout_inversion_payload()
    payload["momentum_confirmation_flags"] = [
        "upside_momentum_confirmed",
        "upside_ema_supportive",
        "upside_rsi_has_room",
        "upside_volume_confirmed",
        "upside_macd_confirmed",
        "upside_macd_histogram_improving",
        "short_countertrend_risk",
        "downside_momentum_confirmed",
        "downside_ema_supportive",
        "downside_rsi_has_room",
        "downside_volume_confirmed",
        "downside_macd_confirmed",
        "downside_macd_histogram_weakening",
        "long_countertrend_risk",
    ]
    return payload


def _sample_marker_overlap_payload() -> dict[str, object]:
    payload = _sample_detail_payload()
    payload["long_setup"] = {
        **payload["long_setup"],
        "stop_loss": 65710.0,
        "tp1": 65710.8,
        "tp2": 65711.2,
    }
    payload["short_setup"] = {
        **payload["short_setup"],
        "stop_loss": 65860.0,
        "tp1": 65859.7,
        "tp2": 65859.2,
    }
    return payload


def _major_turning_point_diagnostic_payload() -> dict[str, object]:
    return {
        "summary_status": "ready_for_human_review",
        "total_rows": 4,
        "counts": {
            "potential_missed_turn": 1,
            "potential_fakeout": 1,
            "bad_entry_timing": 1,
            "inconclusive": 1,
        },
        "representative_rows": [
            {
                "diagnostic_label": "potential_missed_turn",
                "candidate_id": "cand-missed-turn-1",
                "signal_id": "sig-missed-turn-1",
                "timestamp_jst": "2026-06-24T09:00:00+09:00",
                "candidate_type": "reversal_candidate",
                "active_primary_action": "manual_review",
                "side": "long",
                "entry_mode": "watch_only",
                "outcome": "tp2_first",
                "first_exit_reason": "tp2",
                "entry_reached_time": "2026-06-24T08:55:00+09:00",
                "mfe_r": 2.4,
                "mae_r": 0.3,
            },
            {
                "diagnostic_label": "potential_fakeout",
                "candidate_id": "cand-fakeout-1",
                "signal_id": "sig-fakeout-1",
                "timestamp_jst": "2026-06-24T09:15:00+09:00",
                "candidate_type": "turn_candidate",
                "active_primary_action": "manual_review",
                "side": "short",
                "entry_mode": "watch_only",
                "outcome": "sl_first",
                "first_exit_reason": "sl",
                "entry_reached_time": "2026-06-24T09:10:00+09:00",
                "mfe_r": 0.8,
                "mae_r": 1.2,
            },
            {
                "diagnostic_label": "bad_entry_timing",
                "candidate_id": "cand-bad-entry-1",
                "signal_id": "sig-bad-entry-1",
                "timestamp_jst": "2026-06-24T09:30:00+09:00",
                "candidate_type": "entry_timing_candidate",
                "active_primary_action": "manual_review",
                "side": "long",
                "entry_mode": "watch_only",
                "outcome": "timeout",
                "first_exit_reason": "",
                "entry_reached_time": "2026-06-24T09:25:00+09:00",
                "mfe_r": 0.5,
                "mae_r": 0.2,
            },
            {
                "diagnostic_label": "inconclusive",
                "candidate_id": "cand-inconclusive-1",
                "signal_id": "sig-inconclusive-1",
                "timestamp_jst": "2026-06-24T09:45:00+09:00",
                "candidate_type": "watch_only",
                "active_primary_action": "manual_review",
                "side": "wait",
                "entry_mode": "watch_only",
                "outcome": "pending",
                "first_exit_reason": "",
                "entry_reached_time": "",
                "mfe_r": "",
                "mae_r": "",
            },
        ],
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
        "note": (
            "derived from local active_plan_candidate_intraperiod_outcomes.csv only; post-hoc diagnostic support; "
            "does not confirm a major turn; does not authorize manual or automatic entry"
        ),
    }


def _evidence_quality_summary_payload() -> dict[str, object]:
    return {
        "valid_sample_definition": "rows excluding outcome == no_ohlcv",
        "total_rows": 1418,
        "no_ohlcv_rows": 1330,
        "valid_sample_rows": 88,
        "entry_reached_rows": 76,
        "win_like_rows": 35,
        "loss_like_rows": 39,
        "unresolved_entry_rows": 2,
        "potential_fakeout": 39,
        "potential_missed_turn": 35,
        "bad_entry_timing": 2,
        "safety_note": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }


def _ohlcv_source_coverage_summary_payload() -> dict[str, object]:
    return {
        "candidate_rows": 3,
        "ohlcv_input_rows": 2,
        "ohlcv_valid_rows": 2,
        "candidate_timestamp_rows": 3,
        "missing_candidate_timestamp_rows": 0,
        "window_covered_rows": 2,
        "window_missing_rows": 1,
        "no_global_ohlcv_risk_rows": 0,
        "window_missing_rate": 1 / 3,
        "ohlcv_start": "2026-06-30T00:30:00+00:00",
        "ohlcv_end": "2026-06-30T01:30:00+00:00",
        "candidate_timestamp_min": "2026-06-30T00:00:00+00:00",
        "candidate_timestamp_max": "2026-06-30T10:00:00+00:00",
        "candidate_max_after_ohlcv_end_hours": 8.5,
        "stale_threshold_hours": 24.0,
        "ohlcv_range_freshness_status": "fresh_for_latest_candidate",
        "freshness_note": "latest candidate is 8.5h after OHLCV end; OHLCV range is fresh enough for the latest candidate",
        "coverage_note": "report-only coverage summary from candidate timestamps and valid OHLCV bars; missing windows indicate source coverage gaps, not trading logic",
        "safety_note": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }


def _ohlcv_source_coverage_summary_stale_payload() -> dict[str, object]:
    payload = _ohlcv_source_coverage_summary_payload()
    payload.update(
        {
            "candidate_max_after_ohlcv_end_hours": 479.83358999527775,
            "ohlcv_range_freshness_status": "stale_before_latest_candidate",
            "freshness_note": "latest candidate is 479.8h after OHLCV end; old OHLCV coverage can silently dominate no_ohlcv",
        }
    )
    return payload


def _post_eval_recommendation_payload() -> dict[str, object]:
    return {
        "schema_version": "post_eval_recommendations.v1",
        "report_date": "20260702",
        "report_path": "運用資料/reports/post_eval/post_eval_recommendations_20260702.md",
        "output_csv_path": "logs/csv/post_eval_recommendation_candidates.csv",
        "candidate_count": 3,
        "top_recommendation_codes": [
            "PROXY_TOO_AGGRESSIVE_REVIEW",
            "SUBJECT_DEFENSIVE_WORDING_REVIEW",
            "TURNING_BRAKE_REVIEW",
        ],
        "priority_counts": {"high": 1, "medium": 1, "low": 1},
        "confidence_counts": {"actual_backed": 1, "proxy_backed": 2},
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually",
        "note": 'report-only note with <script>alert("x")</script> and UID-like text uid_1234567890abcdef',
        "human_approval_required": True,
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
                "operator_hint_status": "ready_for_human_review",
                "operator_hint_reason": "all integrated evidence is present and ready",
                "operator_hint_next_action": "continue manual review; do not execute diagnostics from app surface",
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
            "major_turning_point_diagnostic": _major_turning_point_diagnostic_payload(),
            "evidence_quality_summary": _evidence_quality_summary_payload(),
            "ohlcv_source_coverage_summary": _ohlcv_source_coverage_summary_payload(),
        }

        html = build_notification_detail_html(payload)
        self.assertIn('body class="v2-report operator-dashboard"', html)
        for class_name in ('shell', 'hero', 'workspace', 'side-card long', 'side-card short', 'chart-panel', 'details-panel', 'decision-word', 'metric', 'condition-grid'):
            self.assertIn(class_name, html)
        self.assertIn('浅い入り', html)
        self.assertIn('本命ゾーン', html)
        self.assertIn('4時間足: 大局方向', html)
        self.assertIn('1時間足: 帯の妥当性', html)
        self.assertIn('15分足: 入る価格 / SL / TP', html)
        self.assertIn('判断根拠と5つのスコア', html)
        self.assertIn('VALUE DEFENSE', html)
        self.assertIn('price-map', html)
        self.assertIn('diagnostic-grid', html)
        self.assertIn('report-only / not FORMAL_GO / no automatic order / human decides manually', html)
        self.assertNotIn('report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually', html)
        self.assertNotIn('Ver04-v1', html)
        self.assertNotIn('Ver03-v4', html)
        self.assertNotIn('Ver02.6-v2', html)
        self.assertNotIn('[BTCFX Ver03-v4]', html)
        self.assertNotIn('send_email', html)
        self.assertNotIn('private/order', html)

        attention_html = build_notification_detail_html({**payload, 'notification_kind': 'attention'})
        self.assertIn('body class="v2-report operator-dashboard"', attention_html)
        self.assertIn('class="shell"', attention_html)
        self.assertIn('class="hero"', attention_html)
        self.assertIn('class="workspace"', attention_html)
        self.assertIn('4時間足: 大局方向', attention_html)
        self.assertIn('1時間足: 帯の妥当性', attention_html)
        self.assertIn('15分足: 入る価格 / SL / TP', attention_html)
        self.assertIn('price-map', attention_html)
        self.assertIn('<summary>高度な検出レイヤー</summary>', attention_html)
        self.assertIn('report-only / not FORMAL_GO / no automatic order / human decides manually', attention_html)
        self.assertNotIn('report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually', attention_html)
        self.assertNotIn('Ver04-v1', attention_html)
        self.assertNotIn('Ver03-v4', attention_html)
        self.assertNotIn('send_email', attention_html)
        self.assertNotIn('private/order', attention_html)
    def test_build_notification_detail_html_renders_breakout_inversion_section(self) -> None:
        html = build_notification_detail_html(_sample_breakout_inversion_payload())
        match = re.search(r'<summary>高度な検出レイヤー</summary>(.*?)</details>', html, re.S)
        self.assertIsNotNone(match)
        section_html = match.group(1) if match else ""

        self.assertIn("BREAKOUT / INVERSION", html)
        self.assertIn("ショート根拠は弱まりつつあります", html)
        self.assertIn("15分足で上に維持できるか確認", html)
        self.assertIn("すぐ下に戻るならダマシ注意", html)
        self.assertIn("ロング根拠は弱まりつつあります", html)
        self.assertIn("15分足で下に維持できるか確認", html)
        self.assertIn("human decides manually", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertNotIn("automatic order allowed", section_html)
        self.assertNotIn("send_email", section_html)
        self.assertNotIn("private/account/order", section_html)

    def test_build_notification_detail_html_renders_intraperiod_early_warning_section(self) -> None:
        html = build_notification_detail_html(_sample_momentum_payload())
        match = re.search(r'<summary>高度な検出レイヤー</summary>(.*?)</details>', html, re.S)
        self.assertIsNotNone(match)
        section_html = match.group(1) if match else ""

        self.assertIn("BREAKOUT / INVERSION", html)
        self.assertIn("ショート方向は損失リスクが高い", html)
        self.assertIn("ロング方向は損失リスクが高い", html)
        self.assertIn("MACD", html)
        self.assertIn("report-only", html)
        self.assertIn("human decides manually", html)
        self.assertNotIn("automatic order allowed", section_html)
        self.assertNotIn("send_email", section_html)
        self.assertNotIn("private/account/order", section_html)

    def test_build_notification_detail_html_renders_momentum_confirmation_section(self) -> None:
        html = build_notification_detail_html(_sample_momentum_payload())
        match = re.search(r'<summary>高度な検出レイヤー</summary>(.*?)</details>', html, re.S)
        self.assertIsNotNone(match)
        section_html = match.group(1) if match else ""

        self.assertIn("MOMENTUM", html)
        self.assertIn("ショート方向は危険", html)
        self.assertIn("ロング方向は危険", html)
        self.assertIn("report-only", html)
        self.assertIn("human decides manually", html)
        self.assertNotIn("automatic order allowed", section_html)
        self.assertNotIn("send_email", section_html)
        self.assertNotIn("private/account/order", section_html)

    def test_build_notification_detail_html_staggers_close_marker_labels(self) -> None:
        html = build_notification_detail_html(_sample_marker_overlap_payload())
        long_marker_ys = sorted(
            float(value)
            for value in re.findall(
                r'<text x="[^"]+" y="([0-9.]+)" text-anchor="start" class="marker-label marker-long">',
                html,
            )
        )
        short_marker_ys = sorted(
            float(value)
            for value in re.findall(
                r'<text x="[^"]+" y="([0-9.]+)" text-anchor="end" class="marker-label marker-short">',
                html,
            )
        )

        self.assertGreaterEqual(len(long_marker_ys), 3)
        self.assertGreaterEqual(len(short_marker_ys), 3)
        self.assertGreaterEqual(long_marker_ys[1] - long_marker_ys[0], 17.5)
        self.assertGreaterEqual(long_marker_ys[2] - long_marker_ys[1], 17.5)
        self.assertGreaterEqual(short_marker_ys[1] - short_marker_ys[0], 17.5)
        self.assertGreaterEqual(short_marker_ys[2] - short_marker_ys[1], 17.5)

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
                "major_turning_point_diagnostic": _major_turning_point_diagnostic_payload(),
                "evidence_quality_summary": _evidence_quality_summary_payload(),
                "ohlcv_source_coverage_summary": _ohlcv_source_coverage_summary_payload(),
            },
            "integrated_evidence_overview_operator_hint_status": "ready_for_human_review",
            "integrated_evidence_overview_operator_hint_reason": "all integrated evidence is present and ready",
            "integrated_evidence_overview_operator_hint_next_action": "continue manual review; do not execute diagnostics from app surface",
        }

        html = build_notification_detail_html(payload)

        self.assertIn('body class="v2-report operator-dashboard"', html)
        self.assertIn('class="shell"', html)
        self.assertIn('class="hero"', html)
        self.assertIn('class="workspace"', html)
        self.assertIn('class="panel details-panel"', html)
        self.assertIn('Operator Triage Summary', html)
        self.assertIn('Integrated Evidence Overview', html)
        self.assertIn('summary_status', html)
        self.assertIn('ready_for_human_review', html)
        self.assertIn('&quot;representative_rows&quot;', html)
        self.assertIn('Evidence quality summary', html)
        self.assertIn('OHLCV source coverage summary', html)
        self.assertIn('report-only / not FORMAL_GO / no automatic order / human decides manually', html)
        self.assertNotIn('report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually', html)
        self.assertNotIn('Ver04-v1', html)
        self.assertNotIn('Ver03-v4', html)
        self.assertNotIn('send_email', html)
        self.assertNotIn('private/order', html)
    def test_build_notification_detail_html_hides_operator_triage_summary_when_absent(self) -> None:
        payload = _sample_detail_payload()

        html = build_notification_detail_html(payload)

        self.assertNotIn("Operator Triage Summary", html)
        self.assertNotIn("summary_status", html)
        self.assertNotIn("all_evidence_present", html)
        self.assertNotIn("Integrated Evidence Overview", html)
        self.assertNotIn("operator_hint_status", html)
        self.assertNotIn("大転換チャンス診断", html)
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
        self.assertNotIn("operator_hint_status", html)
        self.assertIn("内部ログ・Runtime・検証情報", html)
        self.assertNotIn("Ver03-v4 手動確認サポート", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SMTP_PASSWORD", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

    def test_build_notification_detail_html_uses_stable_product_title_and_hides_version_labels(self) -> None:
        payload = _sample_detail_payload()

        html = build_notification_detail_html(payload)

        self.assertIn("BTCFX Manual Trading Report", html)
        self.assertIn('body class="v2-report operator-dashboard"', html)
        for class_name in ("shell", "hero", "workspace", "side-card long", "side-card short", "chart-panel", "details-panel", "decision-word", "metric", "condition-grid"):
            self.assertIn(class_name, html)
        self.assertIn("浅い入り", html)
        self.assertIn("本命ゾーン", html)
        self.assertIn("判断根拠と5つのスコア", html)
        self.assertIn("内部ログ・Runtime・検証情報", html)
        self.assertNotIn("Ver02.6-v2", html)
        self.assertNotIn("Ver04-v1", html)
        self.assertNotIn("Ver04-v2", html)
        self.assertNotIn("[CLI]", html)
        self.assertNotIn("[API]", html)
        self.assertNotIn("[BTCFX Ver03-v4]", html)
        self.assertNotIn("Ver03-v4 手動確認サポート", html)

    def test_build_notification_detail_html_uses_v2_readability_layout(self) -> None:
        html = build_notification_detail_html(_sample_detail_payload())

        self.assertIn('body class="v2-report operator-dashboard"', html)
        for class_name in ("shell", "hero", "workspace", "side-card long", "side-card short", "chart-panel", "details-panel", "decision-word", "metric", "condition-grid"):
            self.assertIn(class_name, html)
        self.assertIn("浅い入り", html)
        self.assertIn("本命ゾーン", html)
        self.assertIn("判断根拠と5つのスコア", html)
        self.assertIn("待機理由", html)
        self.assertNotIn("Phase4 レビューキュー", html)
        self.assertNotIn("report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually", html)
        self.assertNotIn('class="sparkline"', html)
        self.assertNotIn("not FORMAL_GO order", html)

    def test_operator_dashboard_includes_sanitized_shadow_panel(self) -> None:
        payload = _sample_detail_payload()
        payload["active_trade_plan"] = {"side_plans": {"long": {"bias_alignment": "primary", "market_entry_status": "allowed", "entry_mid": 65000, "stop_loss": 64000, "tp1": 66000, "tp2": 67000, "rr_zone_mid_tp1": 1.2, "rr_zone_mid_tp2": 2.0}}}
        payload["big_chance_candidate"] = {"present": True, "score": 1, "grade": "C", "status": "armed", "headline": "shadow context", "macro_context": {}}
        html = build_notification_detail_html(payload)
        self.assertIn("SHADOW / REPORT ONLY", html)
        for text in ("not FORMAL_GO", "no automatic order", "human decides manually", "A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE", "STOP_OR_EXIT", "15分足", "64000", "66000", "67000"):
            self.assertIn(text, html)
        self.assertIn("shadow-card", html)
        self.assertLess(html.find('id="active-alerts"'), html.find("SHADOW / REPORT ONLY"))
        self.assertLess(html.find("SHADOW / REPORT ONLY"), html.find('class="workspace"'))
        for marker in ('chart-panel', 'side-card long', 'side-card short', 'VALUE DEFENSE', 'id="big-chance"'):
            self.assertIn(marker, html)
        escaped = build_notification_detail_html({**payload, "active_trade_plan": {"side_plans": {"long": {"entry_mid": "<unsafe>", "stop_loss": "<sl>", "tp1": "<tp1>", "tp2": "<tp2>"}}}})
        self.assertNotIn("<unsafe>", escaped)

    def test_shadow_degradation_preserves_detail_page(self) -> None:
        payload = _sample_detail_payload()
        for status in ("no_current_candidate", "insufficient_evidence", "malformed"):
            with patch("src.notification.detail_page.build_manual_operator_shadow_surface", return_value={"surface_status": status, "rows": [], "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"}):
                html = build_notification_detail_html(payload)
            self.assertIn('class="workspace"', html)
            self.assertIn("chart-panel", html)
            self.assertIn("SHADOW / REPORT ONLY", html)

    def test_relative_balance_meter_uses_deterministic_shares(self) -> None:
        cases = ((45, 15, "75", "25"), (100, 100, "50", "50"), (69, 21, "76.7", "23.3"), (89, 0, "100", "0"))
        for long_score, short_score, long_share, short_share in cases:
            with self.subTest(long_score=long_score, short_score=short_score):
                payload = _sample_detail_payload(); payload.update(long_display_score=long_score, short_display_score=short_score)
                balance = _operator_dashboard_relative_balance(payload)
                html = build_notification_detail_html(payload)
                self.assertEqual(balance["state"], "relative")
                self.assertIn(f'data-long-share="{long_share}"', html)
                self.assertIn(f'data-short-share="{short_share}"', html)
                self.assertIn(f'>{long_share}%</span>', html)
                self.assertIn(f'>{short_share}%</span>', html)

    def test_relative_balance_zero_scores_is_insufficient(self) -> None:
        payload = _sample_detail_payload(); payload.update(long_display_score=0, short_display_score=0)
        html = build_notification_detail_html(payload)
        self.assertIn('data-balance-state="insufficient"', html)
        self.assertIn("判定材料不足", html)
        self.assertIn("balance-track-insufficient", html)
        self.assertNotIn('data-long-share="50"', html)
        self.assertNotIn('data-short-share="50"', html)

    def test_relative_balance_is_between_shadow_and_workspace(self) -> None:
        html = build_notification_detail_html(_sample_detail_payload())
        self.assertLess(html.find('class="shadow-panel"'), html.find('class="balance-meter"'))
        self.assertLess(html.find('class="balance-meter"'), html.find('class="workspace"'))

    def test_relative_balance_preserves_side_card_absolute_scores_and_safety(self) -> None:
        payload = _sample_detail_payload(); payload.update(long_display_score=45, short_display_score=15)
        html = build_notification_detail_html(payload)
        self.assertIn('<div class="side-score"><strong>45</strong>', html)
        self.assertIn('<div class="side-score"><strong>15</strong>', html)
        self.assertIn("機械評価上の相対バランス。最終判断ではありません。", html)
        self.assertIn('aria-label="現在の相対優勢', html)

    def test_non_executable_execution_label_uses_wait_hero_token(self) -> None:
        payload = _sample_detail_payload()
        with patch(
            "src.notification.detail_page._notification_context_for_result",
            return_value={
                "execution_label": "監視継続（実行不可）",
                "reason_labels_full": ["15分足で確認"],
                "active_market_entry_now": {},
                "active_limit_retest_entry": {},
                "active_breakout_follow_entry": {},
                "active_countertrend_scalp_entry": {},
            },
        ):
            html = build_notification_detail_html(payload)
        self.assertIn('<div class="decision-word">WAIT</div>', html)
        self.assertNotIn('<div class="decision-word">監視継続（実行不可）</div>', html)
        self.assertIn('class="decision-copy"', html)

    def test_long_unexpected_hero_token_gets_compact_class(self) -> None:
        payload = _sample_detail_payload()
        with patch(
            "src.notification.detail_page._notification_context_for_result",
            return_value={
                "execution_label": "UNEXPECTEDLY_LONG_STATUS_TOKEN",
                "reason_labels_full": [],
                "active_market_entry_now": {},
                "active_limit_retest_entry": {},
                "active_breakout_follow_entry": {},
                "active_countertrend_scalp_entry": {},
            },
        ):
            html = build_notification_detail_html(payload)
        self.assertIn('class="decision-word compact"', html)
        self.assertIn("min-width:0", html)
        self.assertIn(".decision-copy { min-width:0;", html)

    def test_operator_dashboard_v2_structure_prices_and_value_defense(self) -> None:
        payload = _sample_detail_payload()
        payload["current_price"] = 63197.80
        payload["long_setup"]["value_defense_entry_layer"]["shallow_retest_zone"] = {"low": 63114.83, "high": 63266.9}
        html = build_notification_detail_html(payload)

        self.assertIn('body class="v2-report operator-dashboard"', html)
        self.assertIn('class="hero"', html)
        self.assertIn('id="active-alerts"', html)
        self.assertIn('aria-label="LONG trade plan"', html)
        self.assertIn('aria-label="SHORT trade plan"', html)
        self.assertIn('data-chart-view="15m"', html)
        self.assertIn('data-chart-view="1h"', html)
        self.assertIn('data-chart-view="4h"', html)
        self.assertIn('data-layer-mode="basic"', html)
        self.assertIn('data-layer-mode="full"', html)
        self.assertIn('class="chart-stage basic"', html)
        self.assertIn('viewBox="0 726 860 429"', html)
        self.assertIn('class="price-map chart-svg"', html)
        for selector in (".price-map-bg", ".candle-up", ".candle-down", ".value-defense-band-long", ".value-defense-band-short", ".current-price-line", ".zone-caption"):
            self.assertIn(selector, html)
        self.assertIn("63,198", html)
        self.assertEqual(payload["current_price"], 63197.80)
        for label in ("浅い入り", "本命ゾーン", "無効化", "回収条件", "継続条件"):
            self.assertGreaterEqual(html.count(label), 2)
        for caption in ("LONG 浅い入り", "LONG 本命ゾーン", "SHORT 浅い入り", "SHORT 本命ゾーン"):
            self.assertIn(caption, html)
        self.assertIn("判断が変わる条件", html)
        self.assertLess(html.find('id="big-chance"'), html.find('details-panel')) if 'id="big-chance"' in html else None
        self.assertIn("REPORT ONLY / HUMAN DECISION", html)
        self.assertNotIn("automatic order placed", html)
        advanced = re.search(r"<summary>高度な検出レイヤー</summary>(.*?)</details>", html, re.S)
        self.assertIsNotNone(advanced)
        self.assertNotIn("<details", advanced.group(1) if advanced else "")

    def test_operator_dashboard_v2_action_summary_keeps_both_sides(self) -> None:
        payload = _sample_detail_payload()
        payload["notification_context"] = {
            "active_market_entry_now": {"long": "allowed", "short": "blocked"},
        }
        with patch(
            "src.notification.detail_page._notification_context_for_result",
            return_value={
                "active_market_entry_now": {"long": "allowed", "short": "blocked"},
                "active_limit_retest_entry": {},
                "active_breakout_follow_entry": {},
                "active_countertrend_scalp_entry": {},
                "execution_label": "blocked",
            },
        ):
            html = build_notification_detail_html(payload)
        self.assertIn("Long: 監視可 / Short: 見送り", html)

    def test_operator_dashboard_v2_value_defense_expands_chart_geometry(self) -> None:
        payload = _sample_detail_payload()
        layer = payload["long_setup"]["value_defense_entry_layer"]
        layer["value_defense_zone"] = {"low": 70000.0, "high": 70100.0}
        html = build_notification_detail_html(payload)
        panel = html.split('y="726"', 1)[1]
        match = re.search(r'<rect x="83\.4" y="([0-9.]+)"[^>]+class="value-defense-band-long"', panel)
        self.assertIsNotNone(match)
        self.assertGreater(float(match.group(1)), 752.0)
        self.assertLess(float(match.group(1)), 1117.0)

    def test_operator_dashboard_v2_big_chance_and_context_share_lower_grid(self) -> None:
        payload = _sample_detail_payload()
        payload["big_chance_candidate"] = {
            "present": True,
            "score": 52,
            "grade": "C",
            "status": "armed",
            "headline": "ショート失敗からロング候補",
            "operator_summary": "補助監視",
            "macro_context": {"signals_4h": "wait", "signals_1h": "long", "signals_15m": "wait"},
        }
        html = build_notification_detail_html(payload)
        lower = re.search(r'<section class="lower-grid">(.*?)</section>\s*<section class="panel details-panel">', html, re.S)
        self.assertIsNotNone(lower)
        lower_html = lower.group(1) if lower else ""
        self.assertLess(lower_html.find("判断が変わる条件"), lower_html.find('id="big-chance"'))
        self.assertLess(lower_html.find('id="big-chance"'), lower_html.find('class="context-bar"'))
        self.assertIn("通常のLong / Short判断を上書きしません", lower_html)

    def test_operator_dashboard_v2_side_cards_hide_raw_execution_flags(self) -> None:
        html = build_notification_detail_html(_sample_breakout_inversion_payload())
        workspace = re.search(r'<main class="workspace">(.*?)</main>', html, re.S)
        self.assertIsNotNone(workspace)
        workspace_html = workspace.group(1) if workspace else ""
        for raw_flag in (
            "upside_breakout_follow_watch",
            "downside_breakdown_follow_watch",
            "short_invalidated_by_up_break",
            "long_invalidated_by_down_break",
        ):
            self.assertNotIn(raw_flag, workspace_html)
        self.assertIn("上抜け後の支持化を警戒", workspace_html)
        self.assertIn("下抜け後の抵抗化を警戒", workspace_html)

    def test_operator_dashboard_v2_big_chance_warning_appears_once(self) -> None:
        for status, expected in (("armed", "通常のLong / Short判断を上書きしません"), ("invalidated", "候補失効 / 再評価済み。通常のLong / Short判断を上書きしません")):
            payload = _sample_detail_payload()
            payload["big_chance_candidate"] = {
                "present": True,
                "score": 52,
                "grade": "C",
                "status": status,
                "headline": "候補",
                "macro_context": {},
            }
            html = build_notification_detail_html(payload)
            section = re.search(r'<section class="big-chance.*?</section>', html, re.S)
            self.assertIsNotNone(section)
            section_html = section.group(0) if section else ""
            self.assertEqual(section_html.count("通常のLong / Short判断を上書きしません"), 1)
            self.assertIn(expected, section_html)

    def test_operator_dashboard_v2_major_rows_are_plain_text(self) -> None:
        payload = {
            **_sample_detail_payload(),
            "major_turning_point_diagnostic": _major_turning_point_diagnostic_payload(),
        }
        html = build_notification_detail_html(payload)
        self.assertIn("代表行 1:", html)
        self.assertIn("candidate_id: cand-missed-turn-1", html)
        self.assertNotIn("&lt;div class=&quot;checklist-item&quot;", html)

    def test_operator_dashboard_v2_metric_css_uses_only_dynamic_widths(self) -> None:
        html = build_notification_detail_html(_sample_detail_payload())
        self.assertNotIn(".metric-fill.direction { width:54%", html)
        self.assertNotIn(".metric-fill.execution { width:10%", html)
        self.assertNotIn(".metric-fill.wait { width:88%", html)
        self.assertIn('style="width:100%"', html)
        self.assertIn('style="width:7%"', html)

    def test_operator_dashboard_v2_variants_degrade_safely(self) -> None:
        for kind in ("main", "attention", "followup"):
            html = build_notification_detail_html({**_sample_detail_payload(), "notification_kind": kind, "long_setup": {}, "short_setup": {}})
            self.assertIn('operator-dashboard', html)
            self.assertIn("LONG", html)
            self.assertIn("SHORT", html)
            self.assertIn("—", html)

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

        self.assertIn("manual-trading/attention/20260331_020500.html", str(local_path))
        self.assertTrue(public_url.endswith("/manual-trading/attention/20260331_020500.html"))
        self.assertNotIn("ver02-3v3-obs", str(local_path))
        self.assertNotIn("ver04-v2", str(local_path))

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
                "/Volumes/Server_HD2/site/btc-monitor/notifications/manual-trading/main",
            ],
            calls,
        )

    def test_build_notification_detail_html_renders_stale_ohlcv_warning(self) -> None:
        payload = {
            **_sample_detail_payload(),
            "ohlcv_source_coverage_summary": _ohlcv_source_coverage_summary_stale_payload(),
        }

        html = build_notification_detail_html(payload)

        self.assertIn("OHLCV stale coverage warning", html)
        self.assertIn("stale_before_latest_candidate", html)
        self.assertIn("candidate_max_after_ohlcv_end_hours: 479.83358999527775", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertIn("<script", html.lower())
        self.assertNotIn("fetch(", html.lower())

    def test_build_notification_detail_html_renders_post_eval_status_from_direct_payload(self) -> None:
        payload = {
            **_sample_detail_payload(),
            "post_eval_recommendations": _post_eval_recommendation_payload(),
        }

        html = build_notification_detail_html(payload)

        self.assertIn("Post-Eval Recommendation Status", html)
        self.assertIn("report-only recommendation status", html)
        self.assertIn("human approval is required before production wording/config/threshold/gate/runtime changes.", html)
        self.assertIn("does not authorize manual or automatic entry", html)
        self.assertIn("does not change notification sending behavior", html)
        self.assertIn("<strong>schema_version:</strong> post_eval_recommendations.v1", html)
        self.assertIn("<strong>report_date:</strong> 20260702", html)
        self.assertIn("<strong>candidate_count:</strong> 3", html)
        self.assertIn(
            "<strong>top_recommendation_codes:</strong> PROXY_TOO_AGGRESSIVE_REVIEW, SUBJECT_DEFENSIVE_WORDING_REVIEW, TURNING_BRAKE_REVIEW",
            html,
        )
        self.assertIn("<strong>priority_counts:</strong> high=1, medium=1, low=1", html)
        self.assertIn("<strong>confidence_counts:</strong> actual_backed=1, proxy_backed=2", html)
        self.assertIn("<strong>report_path:</strong> 運用資料/reports/post_eval/post_eval_recommendations_20260702.md", html)
        self.assertIn("<strong>output_csv_path:</strong> logs/csv/post_eval_recommendation_candidates.csv", html)
        self.assertIn(
            "<strong>safety_boundary:</strong> report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually",
            html,
        )
        self.assertIn("<strong>human_approval_required:</strong> true", html)
        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html)
        self.assertEqual(html.lower().count("<script"), 1)
        self.assertNotIn("fetch(", html.lower())
        self.assertNotIn("send_email", html)
        self.assertNotIn("Gmail", html)
        self.assertNotIn("smtp", html.lower())
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SMTP_PASSWORD", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)

    def test_build_notification_detail_html_renders_post_eval_status_from_nested_validation_data(self) -> None:
        payload = {
            **_sample_detail_payload(),
            "app_surface_validation_data": {
                "post_eval_recommendation_summary": _post_eval_recommendation_payload(),
            },
        }

        html = build_notification_detail_html(payload)

        self.assertIn("Post-Eval Recommendation Status", html)
        self.assertIn("post_eval_recommendations.v1", html)
        self.assertIn("logs/csv/post_eval_recommendation_candidates.csv", html)
        self.assertIn("report-only recommendation status", html)
        self.assertNotIn("uid_1234567890abcdef", html)

    def test_build_notification_detail_html_hides_post_eval_status_when_absent_and_handles_malformed_payload(self) -> None:
        absent_html = build_notification_detail_html(_sample_detail_payload())
        malformed_html = build_notification_detail_html(
            {
                **_sample_detail_payload(),
                "post_eval_recommendation_summary": "not-a-dict",
            }
        )

        self.assertNotIn("Post-Eval Recommendation Status", absent_html)
        self.assertIn("post-eval recommendation payload is unavailable or malformed.", malformed_html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually", malformed_html)
        self.assertEqual(malformed_html.lower().count("<script"), 1)


if __name__ == "__main__":
    unittest.main()
