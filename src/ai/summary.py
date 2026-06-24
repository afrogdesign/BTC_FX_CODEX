from __future__ import annotations

from typing import Any

from src.presentation.sanitize import (
    CONFIDENCE_METRIC_LABELS,
    build_display_context,
    build_notification_context,
    sanitize_flag_list,
    sanitize_user_text,
)


VER03_V4_EMAIL_SUBJECT_PREFIX = "[BTCFX Ver03-v4]"


def _format_price(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _format_subject_price(value: Any) -> str:
    try:
        return f"{round(float(value)):,.0f}"
    except (TypeError, ValueError):
        return str(value)


def _format_pct(value: Any) -> str:
    try:
        return f"{float(value):+.4f}%"
    except (TypeError, ValueError):
        return str(value)


def _subject_status_emoji(status_code: str) -> str:
    mapping = {
        "attention": "👀",
        "actionable": "✅",
        "monitor": "👀",
        "invalid": "⛔️",
        "neutral": "🧭",
    }
    return mapping.get(str(status_code or "").lower(), "🧭")


def _label_bias(value: Any) -> str:
    mapping = {"long": "ロング寄り", "short": "ショート寄り", "wait": "様子見", "no_trade": "見送り"}
    return mapping.get(str(value).lower(), str(value))


def _label_phase(value: Any) -> str:
    mapping = {
        "trend_following": "トレンド継続",
        "pullback": "押し目・戻り待ち",
        "breakout": "ブレイク局面",
        "range": "レンジ局面",
        "reversal_risk": "反転注意",
    }
    return mapping.get(str(value).lower(), str(value))


def _label_signal(value: Any) -> str:
    mapping = {"long": "ロング優勢", "short": "ショート優勢", "wait": "様子見"}
    return mapping.get(str(value).lower(), str(value))


def _label_regime(value: Any) -> str:
    mapping = {
        "uptrend": "上昇基調",
        "downtrend": "下降基調",
        "range": "レンジ",
        "volatile": "値動きが荒い状態",
        "transition": "転換帯",
    }
    return mapping.get(str(value).lower(), str(value))


def _format_zone_summary(name: str, zones: list[dict[str, Any]]) -> str:
    if not zones:
        return f"{name}: 目立つ価格帯は抽出なし"
    parts: list[str] = []
    for zone in zones[:2]:
        low = _format_price(zone.get("low"))
        high = _format_price(zone.get("high"))
        distance = _format_price(zone.get("distance_from_price"))
        parts.append(f"{low} - {high}（現在値から {distance} ドル）")
    return f"{name}: " + " / ".join(parts)


def _normalize_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def _active_subject_detail(notification_context: dict[str, Any]) -> str:
    headline = str(notification_context.get("active_headline", "")).strip()
    if headline:
        return headline
    reasons = notification_context.get("reason_labels") or ["理由未整理"]
    return str(reasons[0])


def _apply_ver03_v4_subject_prefix(subject: str) -> str:
    normalized = str(subject or "").strip()
    if normalized.startswith(VER03_V4_EMAIL_SUBJECT_PREFIX):
        return normalized
    if not normalized:
        return VER03_V4_EMAIL_SUBJECT_PREFIX
    return f"{VER03_V4_EMAIL_SUBJECT_PREFIX} {normalized}"


def _extend_gate_lines(lines: list[str], result: dict[str, Any]) -> None:
    trade_gate = str(result.get("trade_execution_gate", "blocked")).strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).strip()
    observation_gate = str(result.get("phase1_observation_gate", "blocked")).strip() or "blocked"
    observation_type = str(result.get("phase1_observation_type", "")).strip()
    trade_blockers = _normalize_text_list(result.get("trade_execution_blockers", []))
    observation_reasons = _normalize_text_list(result.get("phase1_observation_reasons", []))

    lines.extend(["", "【実行ゲート】", f"判定: {trade_gate}"])
    if paper_order_status:
        lines.append(f"paper_order_status: {paper_order_status}")
    if trade_blockers:
        lines.append("理由:")
        lines.extend(f"- {blocker}" for blocker in trade_blockers)

    lines.extend(["", "【観測ゲート】", f"判定: {observation_gate}"])
    if observation_type:
        lines.append(f"観測タイプ: {observation_type}")
    if observation_reasons:
        lines.append("理由:")
        lines.extend(f"- {reason}" for reason in observation_reasons)


def _actionability_lines(result: dict[str, Any]) -> list[str]:
    label = str(result.get("actionability_label", "")).strip()
    human_action = str(result.get("human_action", "")).strip()
    safety = str(result.get("actionability_safety", "")).strip()
    reasons = result.get("actionability_reasons", [])
    if not label and not human_action and not safety and not reasons:
        return []
    label_text = {
        "ACTIONABLE_COPY_READY": "手動確認すれば行動候補",
        "REVIEW_REQUIRED": "要確認。すぐ行動せず内容確認",
        "AUTO_REJECT": "行動候補から除外。今回は見送り",
        "NO_ACTION": "行動なし",
    }.get(label, "判定未確定")
    human_action_text = {
        "manual_copy_review": "内容を確認して、手動で判断",
        "review_only": "すぐ行動せず、確認だけ行う",
        "do_nothing": "何もしない",
    }.get(human_action, "人間確認")
    if isinstance(reasons, list):
        normalized_reasons = [str(item).strip() for item in reasons if str(item).strip()]
    else:
        normalized_reasons = [str(reasons).strip()] if str(reasons).strip() else []
    reason_lines = []
    for reason in normalized_reasons:
        if reason == "deterministic_checks_passed":
            reason_lines.append("決定的チェックを通過")
        elif reason.startswith("source_not_ready:"):
            reason_lines.append("データ鮮度または入力状態が不十分")
        elif reason == "no_intraperiod_evidence":
            reason_lines.append("intraperiod根拠が不足")
        elif reason == "no_action_review_required":
            reason_lines.append("見送りだが確認推奨")
        elif reason == "manual_context_review_required":
            reason_lines.append("手動確認が必要な文脈あり")
        elif reason == "pending_coverage_review_required":
            reason_lines.append("pending比率または未確定要素の確認が必要")
        elif reason == "active_plan_no_action":
            reason_lines.append("Active Planは行動なし")
        elif reason == "unknown_active_plan_label":
            reason_lines.append("Active Planラベルが未対応")
        else:
            reason_lines.append(reason)
    if not reason_lines:
        reason_lines = ["理由なし"]
    reason_text = ", ".join(normalized_reasons) or "none"
    return [
        "",
        "【行動判定】",
        f"判定: {label_text}",
        f"次の行動: {human_action_text}",
        "理由:",
        *reason_lines,
        "安全:",
        "これは正式GOではありません",
        "自動発注はしません",
        "最終判断は人間が行います",
        "機械判定:",
        f"actionability_label: {label or 'none'}",
        f"human_action: {human_action or 'none'}",
        f"actionability_reasons: {reason_text}",
        f"actionability_safety: {safety or 'none'}",
    ]


def _manual_action_checklist_lines(
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
) -> list[str]:
    entry_mode = str(notification_context.get("execution_label", "見送り")).strip() or "見送り"
    entry_window = str(notification_context.get("entry_window_label", "不可")).strip() or "不可"
    entry_quality = str(display_context.get("entry_quality_label", "位置評価なし")).strip() or "位置評価なし"
    active_headline = str(notification_context.get("active_headline", "")).strip()
    entry_condition_parts = [entry_window, entry_quality]
    if active_headline:
        entry_condition_parts.append(active_headline)
    invalidation = str(notification_context.get("invalidation_label", "主要価格帯の反応崩れで無効寄り")).strip() or "主要価格帯の反応崩れで無効寄り"
    next_condition = str(notification_context.get("next_condition_label", "次回更新で再評価")).strip() or "次回更新で再評価"
    wait_reason_labels = display_context.get("wait_reason_labels", [])
    normalized_wait_reasons = []
    if isinstance(wait_reason_labels, list):
        normalized_wait_reasons = [str(reason).strip() for reason in wait_reason_labels if str(reason).strip()]
    elif str(wait_reason_labels).strip():
        normalized_wait_reasons = [str(wait_reason_labels).strip()]
    invalidation_parts = [invalidation, next_condition, *normalized_wait_reasons]
    validity = str(notification_context.get("validity_label", "次回更新までを目安")).strip() or "次回更新までを目安"
    safety = "report-only / not FORMAL_GO / no automatic order / human decides manually"
    return [
        "",
        "【手動アクション確認】",
        f"Entry mode: {entry_mode}",
        f"Entry condition: {' / '.join(entry_condition_parts)}",
        "TP / SL",
        f"- {_format_setup_levels(result.get('long_setup', {}), 'long')}",
        f"- {_format_setup_levels(result.get('short_setup', {}), 'short')}",
        f"Invalidation / wait: {' / '.join(invalidation_parts)}",
        f"Timeout / validity: {validity}",
        f"Safety: {safety}",
    ]


def _major_turning_point_opportunity_lines(
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
) -> list[str]:
    wait_reasons = [str(reason).strip() for reason in display_context.get("wait_reason_labels", []) if str(reason).strip()]
    return [
        "",
        "【大転換チャンス確認】",
        "大転換は「方向」だけではなく、4h→1h→15m の順に根拠を確認します。15分足だけの反応で大転換と決めません。",
        "スコア差が小さいときは大転換候補とダマシを取り違えやすいので、決め打ちしません。",
        "主要サポート / レジスタンス付近では、反転・ブレイク・失敗の3択を確認します。",
        "entry condition / invalidation / next condition を満たすまでは、転換を決め打ちしません。",
        "大転換候補 / 転換確認 / ダマシ注意 / 決め打ち禁止 / 条件成立まで人間確認",
        f"market_regime: {_label_regime(result.get('market_regime'))}",
        f"phase: {_label_phase(result.get('phase'))}",
        f"4時間足: {_label_signal(result.get('signals_4h'))}",
        f"1時間足: {_label_signal(result.get('signals_1h'))}",
        f"15分足: {_label_signal(result.get('signals_15m'))}",
        f"スコア差: ロング {result.get('long_display_score')} / ショート {result.get('short_display_score')} / 差 {result.get('score_gap')}",
        f"Entry condition: {notification_context.get('entry_window_label', '未記録')} / {display_context.get('entry_quality_label', '未記録')} / {str(notification_context.get('execution_label', '')).strip() or '未記録'}",
        f"Invalidation / wait: {notification_context.get('invalidation_label', '未記録')} / {notification_context.get('next_condition_label', '未記録')} / {', '.join(wait_reasons) or '未記録'}",
        f"Price context: 現在価格 {_format_price(result.get('current_price'))}",
        f"Price context: {_format_zone_summary('近いサポート帯', result.get('support_zones', []))}",
        f"Price context: {_format_zone_summary('近いレジスタンス帯', result.get('resistance_zones', []))}",
        f"Price context: {_format_setup_levels(result.get('long_setup', {}), 'long')}",
        f"Price context: {_format_setup_levels(result.get('short_setup', {}), 'short')}",
        "Safety: report-only / not FORMAL_GO / no automatic order / human decides manually",
    ]


def _local_confirmation_lines() -> list[str]:
    return [
        "",
        "【ローカル確認】",
        "事前生成/検証: scripts/refresh_current_manual_delivery_app_surface.command",
        "ready gate: refresh-and-check-current-manual-delivery-app-surface --stdout-json",
        "確認入口: local/manual_delivery_app_surface/index.html",
        "Dashboard: local/manual_delivery_app_surface/app-dashboard.html",
        "Ready JSON: local/manual_delivery_app_surface/app-ready.json",
        "Snapshot: local/manual_delivery_app_surface/app-snapshot.json",
        "Manifest: local/manual_delivery_app_surface/app-surface-manifest.json",
        "自動発注なし / 通知送信追加なし / 最終判断は人間",
    ]


def _safe_config_schema_audit_evidence(result: dict[str, Any]) -> dict[str, Any] | None:
    direct_evidence = result.get("safe_config_schema_audit")
    if isinstance(direct_evidence, dict):
        return direct_evidence
    for container_key in ("app_contract_data", "app_contract"):
        container = result.get(container_key)
        if not isinstance(container, dict):
            continue
        evidence = container.get("safe_config_schema_audit")
        if isinstance(evidence, dict):
            return evidence
    return None


def _safe_config_schema_audit_value(value: Any) -> str:
    if value is None:
        return "not recorded"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        text = value.strip()
        return text or "not recorded"
    return "not recorded"


def _safe_config_schema_audit_lines(result: dict[str, Any]) -> list[str]:
    evidence = _safe_config_schema_audit_evidence(result)
    if not isinstance(evidence, dict):
        return []

    lines = [
        "",
        "【Safe Config Schema Audit】",
        "local/report-only の静的監査サポートです。tools/safe_config_schema_audit.py は実行しません。",
        "安全境界: local/report-only / no load_config / no .env read / no os.environ value read / no secret/API key exposure / no exchange/private/account/order endpoint access / no FORMAL_GO / no automatic order",
    ]
    for label, key in (
        ("command", "command"),
        ("stdout_json_command", "stdout_json_command"),
        ("schema_version", "schema_version"),
        ("contract_only", "contract_only"),
        ("command_executed_by_app", "command_executed_by_app"),
        ("reads_env_values", "reads_env_values"),
        ("reads_dotenv_values", "reads_dotenv_values"),
        ("calls_private_endpoints", "calls_private_endpoints"),
        ("calls_order_endpoints", "calls_order_endpoints"),
        ("live_trading_allowed", "live_trading_allowed"),
        ("secret_values_exposed", "secret_values_exposed"),
        ("safety_boundary", "safety_boundary"),
    ):
        lines.append(f"{label}: {_safe_config_schema_audit_value(evidence.get(key))}")
    return lines


def _operator_triage_summary_evidence(result: dict[str, Any]) -> dict[str, Any] | None:
    direct_evidence = result.get("operator_triage_summary")
    if isinstance(direct_evidence, dict):
        return direct_evidence
    for container_key in (
        "app_contract_data",
        "app_contract",
        "notification_context",
        "display_context",
        "app_surface_validation",
        "app_surface_validation_data",
        "manual_delivery_app_surface_validation",
        "current_manual_delivery_app_surface_validation",
    ):
        container = result.get(container_key)
        if not isinstance(container, dict):
            continue
        evidence = container.get("operator_triage_summary")
        if isinstance(evidence, dict):
            return evidence
    return None


def _operator_triage_summary_value(value: Any) -> str:
    if value is None:
        return "not recorded"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        text = value.strip()
        return text or "not recorded"
    return "not recorded"


def _operator_triage_summary_field_value(
    evidence: dict[str, Any],
    field: str,
    subfield: str | None = None,
) -> Any:
    direct_key = f"{field}_{subfield}" if subfield else field
    direct_value = evidence.get(direct_key)
    if direct_value is not None:
        return direct_value
    if subfield is None:
        return evidence.get(field)
    nested_value = evidence.get(field)
    if isinstance(nested_value, dict):
        return nested_value.get(subfield)
    nested_container = evidence.get("evidence")
    if isinstance(nested_container, dict):
        nested_value = nested_container.get(field)
        if isinstance(nested_value, dict):
            return nested_value.get(subfield)
    return None


def _operator_triage_summary_lines(result: dict[str, Any]) -> list[str]:
    evidence = _operator_triage_summary_evidence(result)
    if not isinstance(evidence, dict):
        return []

    lines = [
        "",
        "【Operator Triage Summary】",
        "local/report-only の表示です。tools/log_feedback.py の既存契約データだけを使います。",
        "安全境界: report-only / not FORMAL_GO / no automatic order / human decides manually",
    ]
    for label, key in (
        ("summary_status", "summary_status"),
        ("all_evidence_present", "all_evidence_present"),
        ("all_evidence_ready", "all_evidence_ready"),
        ("operator_status_diagnostic present", ("operator_status_diagnostic", "present")),
        ("operator_status_diagnostic ready", ("operator_status_diagnostic", "ready")),
        ("safe_config_schema_audit present", ("safe_config_schema_audit", "present")),
        ("safe_config_schema_audit ready", ("safe_config_schema_audit", "ready")),
        ("intraperiod_review_stdout_json present", ("intraperiod_review_stdout_json", "present")),
        ("intraperiod_review_stdout_json ready", ("intraperiod_review_stdout_json", "ready")),
        ("manual_action_checklist_surface present", ("manual_action_checklist_surface", "present")),
        ("manual_action_checklist_surface ready", ("manual_action_checklist_surface", "ready")),
        ("safety_boundary", "safety_boundary"),
        ("note", "note"),
    ):
        if isinstance(key, tuple):
            value = _operator_triage_summary_field_value(evidence, key[0], key[1])
        else:
            value = evidence.get(key)
        lines.append(f"{label}: {_operator_triage_summary_value(value)}")
    return lines


def _integrated_evidence_overview_evidence(result: dict[str, Any]) -> dict[str, Any] | None:
    direct_evidence = result.get("integrated_evidence_overview")
    if isinstance(direct_evidence, dict):
        return direct_evidence
    for container_key in (
        "app_surface_validation",
        "app_surface_validation_data",
        "manual_delivery_app_surface_validation",
        "current_manual_delivery_app_surface_validation",
    ):
        container = result.get(container_key)
        if not isinstance(container, dict):
            continue
        evidence = container.get("integrated_evidence_overview")
        if isinstance(evidence, dict):
            return evidence
    return None


def _integrated_evidence_overview_value(value: Any) -> str:
    if value is None:
        return "not recorded"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, (list, tuple)):
        if not value:
            return "none"
        return ", ".join(str(item) for item in value)
    if isinstance(value, str):
        text = value.strip()
        return text or "not recorded"
    return "not recorded"


def _integrated_evidence_overview_field_value(
    evidence: dict[str, Any],
    field: str,
    subfield: str | None = None,
) -> Any:
    direct_key = f"{field}_{subfield}" if subfield else field
    direct_value = evidence.get(direct_key)
    if direct_value is not None:
        return direct_value
    if subfield is None:
        return evidence.get(field)
    nested_value = evidence.get(field)
    if isinstance(nested_value, dict):
        direct_nested = nested_value.get(subfield)
        if direct_nested is not None:
            return direct_nested
    nested_container = evidence.get("evidence")
    if isinstance(nested_container, dict):
        nested_value = nested_container.get(field)
        if isinstance(nested_value, dict):
            return nested_value.get(subfield)
    return None


def _integrated_evidence_overview_list_field_value(
    result: dict[str, Any],
    evidence: dict[str, Any],
    field: str,
) -> Any:
    for candidate in (
        evidence.get(field),
        result.get(f"integrated_evidence_overview_{field}"),
        result.get(field),
    ):
        if isinstance(candidate, list):
            return candidate
        if isinstance(candidate, tuple):
            return list(candidate)
    return None


def _integrated_evidence_overview_hint_field_value(
    result: dict[str, Any],
    evidence: dict[str, Any],
    field: str,
) -> Any:
    for candidate in (
        evidence.get(field),
        result.get(f"integrated_evidence_overview_{field}"),
        result.get(field),
    ):
        if candidate is not None:
            return candidate
    return None


def _integrated_evidence_overview_lines(result: dict[str, Any]) -> list[str]:
    evidence = _integrated_evidence_overview_evidence(result)
    if not isinstance(evidence, dict):
        return []

    lines = [
        "",
        "【Integrated Evidence Overview】",
        "local/report-only の表示です。既存の契約/検証データだけを使い、実行はしません。",
        "安全境界: report-only / not FORMAL_GO / no automatic order / human decides manually",
    ]
    list_labels = {
        "evidence_keys",
        "missing_evidence_keys",
        "not_ready_evidence_keys",
        "execution_required_keys",
    }
    hint_labels = {
        "operator_hint_status",
        "operator_hint_reason",
        "operator_hint_next_action",
    }
    for label, key in (
        ("summary_status", "summary_status"),
        ("all_evidence_present", "all_evidence_present"),
        ("all_evidence_ready", "all_evidence_ready"),
        (
            "operator_hint_status",
            _integrated_evidence_overview_hint_field_value(result, evidence, "operator_hint_status"),
        ),
        (
            "operator_hint_reason",
            _integrated_evidence_overview_hint_field_value(result, evidence, "operator_hint_reason"),
        ),
        (
            "operator_hint_next_action",
            _integrated_evidence_overview_hint_field_value(result, evidence, "operator_hint_next_action"),
        ),
        ("evidence_keys", _integrated_evidence_overview_list_field_value(result, evidence, "evidence_keys")),
        (
            "missing_evidence_keys",
            _integrated_evidence_overview_list_field_value(result, evidence, "missing_evidence_keys"),
        ),
        (
            "not_ready_evidence_keys",
            _integrated_evidence_overview_list_field_value(result, evidence, "not_ready_evidence_keys"),
        ),
        (
            "execution_required_keys",
            _integrated_evidence_overview_list_field_value(result, evidence, "execution_required_keys"),
        ),
        ("intraperiod_review_stdout_json present", ("intraperiod_review_stdout_json", "present")),
        ("intraperiod_review_stdout_json ready_or_valid", ("intraperiod_review_stdout_json", "ready_or_valid")),
        ("intraperiod_review_stdout_json execution_required", ("intraperiod_review_stdout_json", "execution_required")),
        ("operator_status_diagnostic present", ("operator_status_diagnostic", "present")),
        ("operator_status_diagnostic ready_or_valid", ("operator_status_diagnostic", "ready_or_valid")),
        ("operator_status_diagnostic execution_required", ("operator_status_diagnostic", "execution_required")),
        ("safe_config_schema_audit present", ("safe_config_schema_audit", "present")),
        ("safe_config_schema_audit ready_or_valid", ("safe_config_schema_audit", "ready_or_valid")),
        ("safe_config_schema_audit execution_required", ("safe_config_schema_audit", "execution_required")),
        ("operator_triage_summary present", ("operator_triage_summary", "present")),
        ("operator_triage_summary ready_or_valid", ("operator_triage_summary", "ready_or_valid")),
        ("operator_triage_summary execution_required", ("operator_triage_summary", "execution_required")),
        ("manual_action_checklist_surface present", ("manual_action_checklist_surface", "present")),
        ("manual_action_checklist_surface ready_or_valid", ("manual_action_checklist_surface", "ready_or_valid")),
        ("manual_action_checklist_surface execution_required", ("manual_action_checklist_surface", "execution_required")),
        ("safety_boundary", "safety_boundary"),
        ("note", "note"),
    ):
        if isinstance(key, tuple):
            value = _integrated_evidence_overview_field_value(evidence, key[0], key[1])
        elif label in list_labels:
            value = key
        elif label in hint_labels:
            value = key
        else:
            value = evidence.get(key)
        lines.append(f"{label}: {_integrated_evidence_overview_value(value)}")
    return lines


def _format_setup_levels(setup: dict[str, Any], side: str) -> str:
    status_mapping = {"ready": "条件付きで検討", "watch": "監視継続", "invalid": "現状は見送り", "none": "未形成"}
    raw_status = str(setup.get("status", "none")).lower()
    status = status_mapping.get(raw_status, "未形成")
    label = "ロング" if side == "long" else "ショート"
    return (
        f"・{label}: {status}。再検討帯は {_format_price((setup.get('entry_zone') or {}).get('low'))} - "
        f"{_format_price((setup.get('entry_zone') or {}).get('high'))}、損切り目安は {_format_price(setup.get('stop_loss'))}、"
        f"利確目安は TP1 {_format_price(setup.get('tp1'))} / TP2 {_format_price(setup.get('tp2'))}"
    )


def _root_summary_lines(
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
) -> list[str]:
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    lines = ["【結論】"]
    trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    observation_gate = str(result.get("phase1_observation_gate", "blocked")).lower().strip() or "blocked"
    if trade_gate == "pass":
        lines.extend(
            [
                "これは執行候補です。",
                "ただし自動売買ではなく、Phase 1 の紙トレード記録対象です。",
            ]
        )
    elif observation_gate == "pass":
        lines.extend(
            [
                "これは実行候補ではありません。",
                "方向・構造は強いため、高優先で監視する通知です。",
            ]
        )
    else:
        lines.extend(
            [
                "これは実行候補ではありません。",
                "通常監視と再評価のための通知です。",
            ]
    )
    lines.extend(_actionability_lines(result))
    lines.extend(_manual_action_checklist_lines(result, display_context, notification_context))
    lines.extend(_major_turning_point_opportunity_lines(result, display_context, notification_context))
    lines.extend(_local_confirmation_lines())
    lines.extend(_safe_config_schema_audit_lines(result))
    lines.extend(_operator_triage_summary_lines(result))
    lines.extend(_integrated_evidence_overview_lines(result))
    _extend_gate_lines(lines, result)
    lines.extend(
        [
            "",
            f"最終ランク: {notification_context.get('final_rank_emoji', '')} {notification_context.get('final_rank_label', '送信なし')}（{notification_context.get('final_rank_explanation', 'メール送信条件は未成立')}）",
            f"補足状態: {notification_context.get('status_label', '中立')}（{notification_context.get('status_explanation', '方向優位なし')}）",
            f"方向判断: {display_context['direction_label']}",
            f"執行判断: {notification_context.get('execution_label', '見送り')}",
            f"現値帯の扱い: {notification_context.get('entry_window_label', '不可')}",
            f"有効目安: {notification_context.get('validity_label', '次回更新までを目安')}",
            "",
            "【いま重視する理由】",
        ]
    )
    for reason in notification_context.get("reason_labels", []):
        lines.append(f"- {reason}")
    lines.extend(
        [
        f"- 次に見る条件: {notification_context.get('next_condition_label', '次回更新で再評価')}",
        f"- 無効化目安: {notification_context.get('invalidation_label', '主要価格帯の反応崩れで無効寄り')}",
        f"- {notification_context.get('price_map', {}).get('support_label', 'サポート: 抽出なし')}",
        f"- {notification_context.get('price_map', {}).get('resistance_label', 'レジスタンス: 抽出なし')}",
        f"- RR評価: {notification_context.get('rr_summary_label', 'RR評価は未計算')}",
        "",
        "【3つの判断指標】",
        f"{metric_labels['direction']}: {result.get('confidence_direction_shadow')}",
        f"{metric_labels['execution']}: {result.get('confidence_execution_shadow')}",
        f"{metric_labels['wait']}: {result.get('confidence_wait_shadow')}",
        f"位置評価: {display_context['entry_quality_label']}",
        "",
        "【根拠要約】",
        f"- 総合判断: {_label_bias(result.get('bias'))}",
        f"- スコア: ロング {result.get('long_display_score')} / ショート {result.get('short_display_score')} / 差 {result.get('score_gap')}",
        f"- 相場環境: {_label_regime(result.get('market_regime'))}",
        f"- 局面: {_label_phase(result.get('phase'))}",
        (
            f"- 時間軸: 4時間足 {_label_signal(result.get('signals_4h'))} / "
            f"1時間足 {_label_signal(result.get('signals_1h'))} / 15分足 {_label_signal(result.get('signals_15m'))}"
        ),
        "",
        "【近い価格帯】",
        f"- 現在価格: {_format_price(result.get('current_price'))}",
        f"- Funding: {str(result.get('funding_rate_display') or '').strip() or f'{result.get('funding_rate_label', 'ほぼ中立')} ({_format_pct(result.get('funding_rate_pct', 0.0))})'}",
        f"- ATR比 / 出来高比: {result.get('atr_ratio')} / {result.get('volume_ratio')}",
        f"- {_format_zone_summary('近いサポート帯', result.get('support_zones', []))}",
        f"- {_format_zone_summary('近いレジスタンス帯', result.get('resistance_zones', []))}",
        "",
        "【ロング/ショートのセットアップ状況】",
        _format_setup_levels(result.get("long_setup", {}), "long"),
        _format_setup_levels(result.get("short_setup", {}), "short"),
        "",
        "【待機理由または注意点】",
        ]
    )
    for reason in display_context["wait_reason_labels"]:
        lines.append(f"- {reason}")
    return lines


def _ai_audit_lines(result: dict[str, Any]) -> list[str]:
    ai_audit = result.get("ai_audit")
    if not isinstance(ai_audit, dict):
        return []
    agreement = str(ai_audit.get("agreement", "")).strip().lower()
    unique_risks = sanitize_flag_list(ai_audit.get("unique_risks", []))
    if agreement in {"", "agree"} and not unique_risks:
        return []
    reason = sanitize_user_text(ai_audit.get("reason", ""))
    next_review_focus = sanitize_user_text(ai_audit.get("next_review_focus", ""))
    headline = {
        "disagree": "【AI監査メモ】 通知判断の再確認を推奨",
        "caution": "【AI監査メモ】 通知は妥当だが注意点あり",
    }.get(agreement, "【AI監査メモ】")
    lines = ["", headline]
    if reason:
        lines.append(f"- 監査理由: {reason}")
    for risk in unique_risks:
        lines.append(f"- 追加リスク: {risk}")
    if next_review_focus:
        lines.append(f"- 次の確認観点: {next_review_focus}")
    return lines


def _attention_summary(result: dict[str, Any], display_context: dict[str, Any], notification_context: dict[str, Any]) -> str:
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    lines = [
        "【注意報】",
        "これは売買推奨メールではありません。",
        "方向変化や初動を早めに共有する注意通知です。",
    ]
    lines.extend(_actionability_lines(result))
    lines.extend(_manual_action_checklist_lines(result, display_context, notification_context))
    lines.extend(_major_turning_point_opportunity_lines(result, display_context, notification_context))
    lines.extend(_local_confirmation_lines())
    lines.extend(_safe_config_schema_audit_lines(result))
    lines.extend(_operator_triage_summary_lines(result))
    lines.extend(_integrated_evidence_overview_lines(result))
    _extend_gate_lines(lines, result)
    lines.extend(
        [
        "",
        "【今の見立て】",
        f"- 最終ランク: {notification_context.get('final_rank_emoji', '👀')} {notification_context.get('final_rank_label', '注意報')}（{notification_context.get('final_rank_explanation', '方向変化の早期共有')}）",
        f"- 補足状態: {notification_context.get('status_label', '注意報')}（{notification_context.get('status_explanation', '方向変化の早期共有')}）",
        f"- 方向判断: {display_context['direction_label']}",
        f"- 執行判断: {notification_context.get('execution_label', '見送り')}",
        f"- 現値帯の扱い: {notification_context.get('entry_window_label', '不可')}",
        f"- 有効目安: {notification_context.get('validity_label', '次の1時間足確定までを目安')}",
        f"- {metric_labels['direction']}: {result.get('confidence_direction_shadow')}",
        f"- {metric_labels['execution']}: {result.get('confidence_execution_shadow')}",
        f"- {metric_labels['wait']}: {result.get('confidence_wait_shadow')}",
        f"- 現在価格: {_format_price(result.get('current_price'))}",
        "",
        "【まだ本命通知でない理由】",
        ]
    )
    for reason in notification_context.get("reason_labels", []):
        lines.append(f"- {reason}")
    lines.extend(
        [
            "",
            "【次に見る条件】",
            f"- {notification_context.get('next_condition_label', '次回更新で再評価')}",
            f"- 無効化目安: {notification_context.get('invalidation_label', '主要価格帯の反応崩れで無効寄り')}",
            f"- {notification_context.get('price_map', {}).get('support_label', 'サポート: 抽出なし')}",
            f"- {notification_context.get('price_map', {}).get('resistance_label', 'レジスタンス: 抽出なし')}",
            f"- RR評価: {notification_context.get('rr_summary_label', 'RR評価は未計算')}",
            "",
            "【観測要点】",
            f"- スコア: ロング {result.get('long_display_score')} / ショート {result.get('short_display_score')} / 差 {abs(int(result.get('score_gap', 0) or 0))}",
            (
                f"- 時間軸: 4時間足 {_label_signal(result.get('signals_4h'))} / "
                f"1時間足 {_label_signal(result.get('signals_1h'))} / 15分足 {_label_signal(result.get('signals_15m'))}"
            ),
        ]
    )
    return "\n".join(lines)


def build_summary_subject(result: dict[str, Any]) -> str:
    display_context = build_display_context(result)
    notification_context = build_notification_context(result)
    jst_ts = str(result.get("timestamp_jst", ""))[:16].replace("T", " ")
    label = str(result.get("system_label", "")).strip()
    mode_label = str(result.get("system_mode_label", "")).strip()
    labels: list[str] = []
    if label:
        labels.append(f"[{label}]")
    if mode_label:
        labels.append(f"[{mode_label}]")
    suffix = f" {' '.join(labels)}" if labels else ""
    price_text = _format_subject_price(result.get("current_price"))
    headline_reason = (notification_context.get("reason_labels") or ["理由未整理"])[0]
    rank_emoji = str(notification_context.get("final_rank_emoji", "")).strip()
    rank_label = str(notification_context.get("final_rank_label", "送信なし")).strip()
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()
    use_existing_subject = (
        notification_kind == "attention"
        or (trade_gate == "pass" and paper_order_status == "planned")
    )
    active_plan_present = any(
        key in result for key in ("active_primary_action", "active_headline", "active_trade_plan")
    )
    legacy_subject = (
        f"{rank_emoji} [{rank_label}] "
        f"{display_context['direction_compact_label']} | {headline_reason} "
        f"【BTC:{price_text}】 {jst_ts}{suffix}"
    ).strip()
    active_label = str(notification_context.get("active_subject_label", "")).strip()
    active_detail = _active_subject_detail(notification_context)
    if use_existing_subject or not active_plan_present or not active_label:
        subject = legacy_subject
    else:
        subject = (
            f"{rank_emoji} [{rank_label}] "
            f"{active_label} / 実弾不可・行動計画 | {active_detail} "
            f"【BTC:{price_text}】 {jst_ts}{suffix}"
        ).strip()
    if result.get("ai_advice") is None:
        subject = f"[機械判定のみ] {subject}"
    return _apply_ver03_v4_subject_prefix(subject)


def build_summary_body(
    *,
    provider: str,
    api_key: str,
    model: str,
    cli_command: str,
    timeout_sec: int,
    retry_count: int,
    base_dir: Any,
    result_payload: dict[str, Any],
) -> tuple[str, str]:
    del api_key, model, cli_command, timeout_sec, retry_count, base_dir
    provider_name = str(provider or "api").strip().lower()
    display_context = build_display_context(result_payload)
    notification_context = build_notification_context(result_payload)
    if str(result_payload.get("notification_kind", "main")).lower() == "attention":
        return _attention_summary(result_payload, display_context, notification_context), provider_name
    lines = _root_summary_lines(result_payload, display_context, notification_context)
    lines.extend(_ai_audit_lines(result_payload))
    return "\n".join(lines), provider_name
