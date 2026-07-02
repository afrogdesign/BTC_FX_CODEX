from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import build_summary_body  # noqa: E402
from src.notification.detail_page import build_notification_detail_html  # noqa: E402


_FORBIDDEN_PATTERNS = (
    "api_key",
    "smtp_password",
    "source_uid_hash",
    "uid-",
    "uid_",
    "account_",
    "account-",
    "private/order",
    "gmail",
    "smtp",
    "send_email",
    "<script",
    "fetch(",
)


def _synthetic_post_eval_payload() -> dict[str, Any]:
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
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
        "note": "report-only render-only smoke",
        "human_approval_required": True,
    }


def _synthetic_result_payload(post_eval_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timestamp_jst": "2026-03-15T06:05:00+09:00",
        "signal_id": "20260315_060500",
        "summary_subject": "notification no-send smoke",
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
        "post_eval_recommendations": post_eval_payload or _synthetic_post_eval_payload(),
    }
    return payload


def _find_forbidden_tokens(text: str) -> list[str]:
    lowered = text.lower()
    return [token for token in _FORBIDDEN_PATTERNS if token in lowered]


def _render_no_send_render_only_smoke(result_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = _synthetic_result_payload(result_payload)
    summary_body, _provider = build_summary_body(
        provider="api",
        api_key="",
        model="",
        cli_command="",
        timeout_sec=1,
        retry_count=1,
        base_dir=BASE_DIR,
        result_payload=payload,
    )
    detail_html = build_notification_detail_html(payload, base_dir=BASE_DIR)
    combined = "\n".join([summary_body, detail_html])
    leaks = _find_forbidden_tokens(combined)
    sensitive_leak_detected = bool(leaks)
    status = "fail" if sensitive_leak_detected else "pass"
    return {
        "status": status,
        "mode": "no_send_render_only",
        "real_mail_sent": False,
        "report_only": True,
        "not_formal_go": True,
        "no_automatic_order": True,
        "human_decides_manually": True,
        "summary_body_rendered": bool(summary_body),
        "detail_html_rendered": bool(detail_html),
        "post_eval_recommendations_present": True,
        "sensitive_leak_detected": sensitive_leak_detected,
        "forbidden_tokens": leaks,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render notification surfaces without sending mail.")
    parser.add_argument("--stdout-json", action="store_true", help="Print compact JSON to stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    report = _render_no_send_render_only_smoke()
    exit_code = 0 if report["status"] == "pass" else 1
    if args.stdout_json:
        sys.stdout.write(json.dumps(report, ensure_ascii=False, sort_keys=True) + "\n")
    else:
        sys.stdout.write(
            "status={status} mode={mode} real_mail_sent={real_mail_sent} report_only={report_only}\n".format(
                **report,
            )
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
