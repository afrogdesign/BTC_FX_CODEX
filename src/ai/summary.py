from __future__ import annotations

from pathlib import Path
from typing import Any
import re

from src.presentation.sanitize import (
    CONFIDENCE_METRIC_LABELS,
    build_display_context,
    build_notification_context,
    sanitize_flag_list,
    sanitize_user_text,
)
from src.notification.followup import (
    FOLLOWUP_HUMAN_MESSAGE,
    FOLLOWUP_PUBLIC_LABEL,
    build_followup_notification_context,
)


STABLE_PUBLIC_PRODUCT_LABEL = "BTCFX Manual Trading Report"
CURRENT_PRODUCT_VERSION_LABEL = STABLE_PUBLIC_PRODUCT_LABEL
CURRENT_EMAIL_SUBJECT_PREFIX = f"[{STABLE_PUBLIC_PRODUCT_LABEL}]"
VER03_V4_EMAIL_SUBJECT_PREFIX = CURRENT_EMAIL_SUBJECT_PREFIX
_LEGACY_PRODUCT_VERSION_PATTERN = re.compile(r"^ver0(?:2|3)", re.IGNORECASE)
_ANY_VERSION_PATTERN = re.compile(r"^ver\d", re.IGNORECASE)


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


_POST_EVAL_PAYLOAD_KEYS = ("post_eval_recommendations", "post_eval_recommendation_summary")
_POST_EVAL_CONTAINER_KEYS = (
    "app_surface_validation_data",
    "app_surface_validation",
    "current_manual_delivery_app_surface_validation",
    "manual_delivery_app_surface_validation",
)
_POST_EVAL_SAFE_BOUNDARY_MARKERS = ("report-only", "no automatic order")
_POST_EVAL_UNSAFE_SUBSTRINGS = (
    "<script",
    "fetch(",
    "smtp",
    "gmail",
    "send_email",
    "openai_api_key",
    "smtp_password",
    "private/order",
    "uid",
    "account",
    "password",
)
_POST_EVAL_SAFE_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")


def _post_eval_payload_from_node(node: Any, seen: set[int]) -> dict[str, Any] | None:
    if isinstance(node, list):
        for item in node:
            found = _post_eval_payload_from_node(item, seen)
            if found is not None:
                return found
        return None
    if not isinstance(node, dict):
        return None
    node_id = id(node)
    if node_id in seen:
        return None
    seen.add(node_id)
    for key in _POST_EVAL_PAYLOAD_KEYS:
        value = node.get(key)
        if isinstance(value, dict):
            return value
    for key in _POST_EVAL_CONTAINER_KEYS:
        found = _post_eval_payload_from_node(node.get(key), seen)
        if found is not None:
            return found
    for value in node.values():
        found = _post_eval_payload_from_node(value, seen)
        if found is not None:
            return found
    return None


def _resolve_post_eval_payload(
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
) -> dict[str, Any] | None:
    for container in (result, display_context, notification_context):
        found = _post_eval_payload_from_node(container, set())
        if found is not None:
            return found
    return None


def _is_truthy_post_eval_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return False


def _safe_post_eval_reference(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    name = Path(text).name.strip()
    if not name or any(marker in name.lower() for marker in _POST_EVAL_UNSAFE_SUBSTRINGS):
        return ""
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,120}", name):
        return ""
    return name


def _safe_post_eval_codes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    codes: list[str] = []
    for item in value:
        code = str(item or "").strip()
        if not code:
            continue
        lowered = code.lower()
        if any(marker in lowered for marker in _POST_EVAL_UNSAFE_SUBSTRINGS):
            continue
        if not _POST_EVAL_SAFE_CODE_PATTERN.fullmatch(code):
            continue
        codes.append(code)
    return codes[:2]


def _post_eval_contract_is_ready(payload: dict[str, Any]) -> bool:
    schema_version = str(payload.get("schema_version", "")).strip()
    candidate_count = payload.get("candidate_count")
    safety_boundary = str(payload.get("safety_boundary", "")).strip().lower()
    human_approved = _is_truthy_post_eval_flag(payload.get("human_approval_required")) or _is_truthy_post_eval_flag(
        payload.get("required_human_approval")
    )
    if schema_version != "post_eval_recommendations.v1":
        return False
    if not isinstance(candidate_count, int) or isinstance(candidate_count, bool) or candidate_count < 0:
        return False
    if not human_approved:
        return False
    return all(marker in safety_boundary for marker in _POST_EVAL_SAFE_BOUNDARY_MARKERS)


def _post_eval_mail_line(
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
) -> list[str]:
    payload = _resolve_post_eval_payload(result, display_context, notification_context)
    if payload is None:
        return []
    if not _post_eval_contract_is_ready(payload):
        return ["【Post-Eval】not ready / report-only / not FORMAL_GO / no automatic order / human decides manually"]
    candidate_count = int(payload.get("candidate_count", 0))
    pieces: list[str] = []
    report_date = str(payload.get("report_date", "")).strip()
    if report_date:
        pieces.append(sanitize_user_text(report_date))
    pieces.append(f"候補: {candidate_count}件")
    top_codes = _safe_post_eval_codes(payload.get("top_recommendation_codes"))
    if top_codes:
        pieces.append(f"top: {', '.join(top_codes)}")
    pieces.extend(["report-only", "not FORMAL_GO", "no automatic order", "human decides manually", "human approval required"])
    report_ref = _safe_post_eval_reference(payload.get("report_path"))
    if report_ref:
        pieces.append(f"report: {report_ref}")
    return [f"【Post-Eval】{' / '.join(pieces)}"]


def _active_subject_detail(notification_context: dict[str, Any]) -> str:
    headline = str(notification_context.get("active_headline", "")).strip()
    if headline:
        return headline
    reasons = notification_context.get("reason_labels") or ["理由未整理"]
    return str(reasons[0])


def _normalize_product_version_label(value: Any) -> str:
    normalized = str(value or "").strip()
    if not normalized or _LEGACY_PRODUCT_VERSION_PATTERN.match(normalized):
        return CURRENT_PRODUCT_VERSION_LABEL
    return normalized


def _is_version_like_label(value: Any) -> bool:
    normalized = str(value or "").strip()
    if not normalized:
        return False
    return bool(_ANY_VERSION_PATTERN.match(normalized))


def _should_include_subject_mode_label(value: Any) -> bool:
    normalized = str(value or "").strip()
    if not normalized:
        return False
    if normalized.lower() == "cli":
        return False
    return not _is_version_like_label(normalized)


def _apply_current_email_subject_prefix(subject: str) -> str:
    normalized = str(subject or "").strip()
    if normalized.startswith(CURRENT_EMAIL_SUBJECT_PREFIX):
        return normalized
    if not normalized:
        return CURRENT_EMAIL_SUBJECT_PREFIX
    return f"{CURRENT_EMAIL_SUBJECT_PREFIX} {normalized}"


def _apply_ver03_v4_subject_prefix(subject: str) -> str:
    return _apply_current_email_subject_prefix(subject)


def _compact_direction_text(result: dict[str, Any], display_context: dict[str, Any]) -> str:
    bias = str(result.get("bias", "")).strip().lower()
    if bias == "long":
        return "上方向"
    if bias == "short":
        return "下方向"
    if bias == "wait":
        return "中立"
    direction_label = str(display_context.get("direction_label", "")).strip()
    if "上方向" in direction_label:
        return "上方向"
    if "下方向" in direction_label:
        return "下方向"
    return direction_label or "中立"


def _compact_handling_line(
    *,
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
) -> str:
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()
    if notification_kind == "followup":
        return "前回通知は失効。新規根拠として使わない。"
    if trade_gate == "pass" and paper_order_status == "planned":
        return "紙実行候補。実弾不可。最終判断は人間。"
    if notification_kind == "attention":
        return "実行候補ではない。高優先で監視。"
    execution_label = str(notification_context.get("execution_label", "")).strip()
    if execution_label and execution_label != "見送り":
        return f"実行候補ではない。{execution_label}でHTML確認。"
    direction = _compact_direction_text(result, display_context)
    if direction == "中立":
        return "実行候補ではない。HTMLで条件確認。"
    return f"実行候補ではない。HTMLで条件確認。"


def _compact_holding_lines(notification_kind: str) -> list[str]:
    if notification_kind == "followup":
        return [
            "保有中: 撤退 / 建値 / 損切り確認",
            "未保有: 追いかけず、HTMLで条件確認",
        ]
    return [
        "保有中: 根拠維持 / 無効化ライン確認",
        "未保有: 追いかけず、HTMLで条件確認",
    ]


def _compact_big_chance_side_label(candidate_type: str) -> str:
    mapping = {
        "long_failed_to_short": "ロング失敗 → ショート候補",
        "short_failed_to_long": "ショート失敗 → ロング候補",
    }
    return mapping.get(candidate_type, "失敗仮説チャンス")


def _compact_big_chance_line(result: dict[str, Any]) -> str:
    candidate = result.get("big_chance_candidate")
    if not isinstance(candidate, dict) or not candidate.get("present"):
        return "Big Chance: なし"
    status = str(candidate.get("status", "")).strip().lower() or "none"
    if status == "invalidated":
        return "Big Chance: 候補失効 / 再評価済み"
    side_type = _compact_big_chance_side_label(str(candidate.get("type", "")).strip().lower())
    grade = str(candidate.get("grade", "")).strip() or "?"
    return f"Big Chance: {side_type} / {status} / {grade}"


def _compact_price_zones(result: dict[str, Any], notification_context: dict[str, Any]) -> list[str]:
    def _zone_range_text(zones: Any) -> str:
        if not isinstance(zones, list) or not zones:
            return "なし"
        zone = zones[0] if isinstance(zones[0], dict) else {}
        low = _format_price(zone.get("low"))
        high = _format_price(zone.get("high"))
        if low == "None" or high == "None":
            return "なし"
        return f"{low} - {high}"

    support = _zone_range_text(result.get("support_zones"))
    resistance = _zone_range_text(result.get("resistance_zones"))
    price_map = notification_context.get("price_map") if isinstance(notification_context.get("price_map"), dict) else {}
    if support == "なし":
        support_label = str(price_map.get("support_label", "")).strip()
        if support_label:
            support = support_label.replace("サポート: ", "")
    if resistance == "なし":
        resistance_label = str(price_map.get("resistance_label", "")).strip()
        if resistance_label:
            resistance = resistance_label.replace("レジスタンス: ", "")
    return [f"上: {resistance}", f"下: {support}"]


def _compact_detail_url_line(result: dict[str, Any]) -> str:
    url = str(result.get("detail_page_url", "")).strip()
    if not url.startswith("https://server.afrog.jp/btc-monitor/notifications/manual-trading/"):
        return ""
    return f"詳細:\n{url}"


_COMPACT_SAFETY_BOUNDARY_CANONICAL = "report-only / not FORMAL_GO / no automatic order / human decides manually"


def _normalize_safety_boundary_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = text.replace("_", " ").replace("-", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    if "report only" in normalized and "automatic order" in normalized and "human decides manually" in normalized:
        return _COMPACT_SAFETY_BOUNDARY_CANONICAL
    if "_" in text and " " not in text:
        return text.replace("_", " ")
    return text


def _compact_email_body(
    *,
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
) -> str:
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    if notification_kind == "followup":
        heading = "【期限切れ・再評価】"
    elif notification_kind == "attention":
        heading = "【注意報】"
    else:
        trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
        paper_order_status = str(result.get("paper_order_status", "")).lower().strip()
        if trade_gate == "pass" and paper_order_status == "planned":
            heading = "【紙実行候補】"
        else:
            heading = "【結論】"

    lines = [heading, _compact_handling_line(result=result, display_context=display_context, notification_context=notification_context)]
    lines.extend(_compact_holding_lines(notification_kind))
    lines.append(_compact_big_chance_line(result))
    operator_decision = result.get("operator_decision") if isinstance(result.get("operator_decision"), dict) else {}
    if bool(operator_decision.get("direction_conflict")) and bool(operator_decision.get("new_entry_blocked")):
        side = str(operator_decision.get("primary_side", "none")).lower()
        score_bias = str(operator_decision.get("score_bias", "wait")).lower()
        side_label = "ショート" if side == "short" else ("ロング" if side == "long" else "なし")
        score_label = "ロング" if score_bias == "long" else ("ショート" if score_bias == "short" else "中立")
        lines.extend(["実行判断: 方向競合・新規見送り", f"監視方向: {side_label}", f"方向スコア上の傾き: {score_label}"])
    else:
        lines.append(
            f"通常バイアス: {_compact_direction_text(result, display_context)} / 実行判断: {str(notification_context.get('execution_label', '見送り')).strip() or '見送り'}"
        )
    lines.append(f"現在: {_format_price(result.get('current_price'))}")
    lines.extend(_compact_price_zones(result, notification_context))
    detail_line = _compact_detail_url_line(result)
    if detail_line:
        lines.append(detail_line)
    if notification_kind == "followup":
        safety_boundary = _normalize_safety_boundary_text(
            notification_context.get("followup_safety_boundary")
            or notification_context.get("safety_boundary")
            or _COMPACT_SAFETY_BOUNDARY_CANONICAL
        )
    else:
        safety_boundary = _normalize_safety_boundary_text(
            result.get("actionability_safety")
            or notification_context.get("safety_boundary")
            or _COMPACT_SAFETY_BOUNDARY_CANONICAL
        )
    lines.append(f"※ {safety_boundary or _COMPACT_SAFETY_BOUNDARY_CANONICAL}")
    return "\n".join(lines)


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
        f"今の扱い: {entry_mode}",
        f"確認条件: {' / '.join(entry_condition_parts)}",
        "TP / SL",
        f"- {_format_setup_levels(result.get('long_setup', {}), 'long')}",
        f"- {_format_setup_levels(result.get('short_setup', {}), 'short')}",
        f"見送り・無効化条件: {' / '.join(invalidation_parts)}",
        f"有効期限: {validity}",
        f"安全境界: {safety}",
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
        "確認条件 / 見送り・無効化条件 / 次の確認条件を満たすまでは、転換を決め打ちしません。",
        "大転換候補 / 転換確認 / ダマシ注意 / 決め打ち禁止 / 条件成立まで人間確認",
        f"相場の状態: {_label_regime(result.get('market_regime'))}",
        f"局面: {_label_phase(result.get('phase'))}",
        f"4時間足: {_label_signal(result.get('signals_4h'))}",
        f"1時間足: {_label_signal(result.get('signals_1h'))}",
        f"15分足: {_label_signal(result.get('signals_15m'))}",
        f"ロング/ショートの強さ: ロング {result.get('long_display_score')} / ショート {result.get('short_display_score')} / 差 {result.get('score_gap')}",
        f"確認条件: {notification_context.get('entry_window_label', '未記録')} / {display_context.get('entry_quality_label', '未記録')} / {str(notification_context.get('execution_label', '')).strip() or '未記録'}",
        f"見送り・無効化条件: {notification_context.get('invalidation_label', '未記録')} / {notification_context.get('next_condition_label', '未記録')} / {', '.join(wait_reasons) or '未記録'}",
        f"価格位置: 現在価格 {_format_price(result.get('current_price'))}",
        f"価格位置: {_format_zone_summary('近いサポート帯', result.get('support_zones', []))}",
        f"価格位置: {_format_zone_summary('近いレジスタンス帯', result.get('resistance_zones', []))}",
        f"価格位置: {_format_setup_levels(result.get('long_setup', {}), 'long')}",
        f"価格位置: {_format_setup_levels(result.get('short_setup', {}), 'short')}",
        "安全境界: report-only / not FORMAL_GO / no automatic order / human decides manually",
    ]


def _major_turning_point_diagnostic_evidence(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    direct_evidence = result.get("major_turning_point_diagnostic")
    if isinstance(direct_evidence, dict):
        return direct_evidence
    for container in (
        notification_context or {},
        display_context or {},
        result.get("app_contract_data") if isinstance(result.get("app_contract_data"), dict) else {},
        result.get("app_contract") if isinstance(result.get("app_contract"), dict) else {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict):
            evidence = container.get("major_turning_point_diagnostic")
            if isinstance(evidence, dict):
                return evidence
    return None


def _major_turning_point_diagnostic_value(value: Any) -> str:
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
    text = str(value).strip()
    return text or "not recorded"


def _major_turning_point_diagnostic_row_text(row: dict[str, Any]) -> str:
    fields = (
        ("diagnostic_label", "diagnostic_label"),
        ("candidate_id", "candidate_id"),
        ("signal_id", "signal_id"),
        ("timestamp_jst", "timestamp_jst"),
        ("candidate_type", "candidate_type"),
        ("active_primary_action", "active_primary_action"),
        ("side", "side"),
        ("entry_mode", "entry_mode"),
        ("outcome", "outcome"),
        ("first_exit_reason", "first_exit_reason"),
        ("entry_reached_time", "entry_reached_time"),
        ("mfe_r", "mfe_r"),
        ("mae_r", "mae_r"),
    )
    return " / ".join(f"{label}: {_major_turning_point_diagnostic_value(row.get(key))}" for label, key in fields)


def _major_turning_point_diagnostic_lines(
    result: dict[str, Any],
    notification_context: dict[str, Any],
    display_context: dict[str, Any],
) -> list[str]:
    evidence = _major_turning_point_diagnostic_evidence(result, notification_context, display_context)
    if not isinstance(evidence, dict) or not evidence:
        return []
    counts = evidence.get("counts") if isinstance(evidence.get("counts"), dict) else {}
    representative_rows = evidence.get("representative_rows")
    rows: list[dict[str, Any]] = [row for row in representative_rows if isinstance(row, dict)] if isinstance(
        representative_rows, list
    ) else []
    lines = [
        "",
        "【大転換チャンス診断】",
        "local/report-only の表示です。post-hoc diagnostic support であり、実行はしません。",
        "does not confirm a major turn / does not authorize manual or automatic entry です。",
        "安全境界: report-only / not FORMAL_GO / no automatic order / human decides manually",
        f"summary_status: {_major_turning_point_diagnostic_value(evidence.get('summary_status'))}",
        f"total_rows: {_major_turning_point_diagnostic_value(evidence.get('total_rows'))}",
        f"potential_missed_turn: {_major_turning_point_diagnostic_value(counts.get('potential_missed_turn'))}",
        f"potential_fakeout: {_major_turning_point_diagnostic_value(counts.get('potential_fakeout'))}",
        f"bad_entry_timing: {_major_turning_point_diagnostic_value(counts.get('bad_entry_timing'))}",
        f"inconclusive: {_major_turning_point_diagnostic_value(counts.get('inconclusive'))}",
    ]
    if rows:
        lines.append("Representative rows:")
        for idx, row in enumerate(rows[:5], 1):
            lines.append(f"- {idx}: {_major_turning_point_diagnostic_row_text(row)}")
    else:
        lines.append("Representative rows: none")
    lines.extend(
        [
            f"safety_boundary: {_major_turning_point_diagnostic_value(evidence.get('safety_boundary'))}",
            f"note: {_major_turning_point_diagnostic_value(evidence.get('note'))}",
        ]
    )
    return lines


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


def _evidence_quality_summary_evidence(
    result: dict[str, Any],
    notification_context: dict[str, Any],
    display_context: dict[str, Any],
) -> dict[str, Any] | None:
    direct_evidence = result.get("evidence_quality_summary")
    if isinstance(direct_evidence, dict):
        return direct_evidence
    for container in (notification_context, display_context):
        if not isinstance(container, dict):
            continue
        evidence = container.get("evidence_quality_summary")
        if isinstance(evidence, dict):
            return evidence
    for container in (
        result.get("app_contract_data") if isinstance(result.get("app_contract_data"), dict) else {},
        result.get("app_contract") if isinstance(result.get("app_contract"), dict) else {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict):
            evidence = container.get("evidence_quality_summary")
            if isinstance(evidence, dict):
                return evidence
    return None


def _evidence_quality_summary_value(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, (list, tuple)):
        if not value:
            return "n/a"
        return ", ".join(str(item) for item in value)
    if isinstance(value, str):
        text = value.strip()
        return text or "n/a"
    return "n/a"


def _evidence_quality_summary_lines(
    result: dict[str, Any],
    notification_context: dict[str, Any],
    display_context: dict[str, Any],
) -> list[str]:
    evidence = _evidence_quality_summary_evidence(result, notification_context, display_context)
    if not isinstance(evidence, dict):
        return []

    lines = [
        "",
        "【Evidence quality summary】",
        "local/report-only の表示です。既存の evidence quality 集計だけを使い、実行はしません。",
        "安全境界: report-only / not FORMAL_GO / no automatic order / human decides manually",
    ]
    for label, key in (
        ("valid_sample_definition", "valid_sample_definition"),
        ("total_rows", "total_rows"),
        ("no_ohlcv_rows", "no_ohlcv_rows"),
        ("valid_sample_rows", "valid_sample_rows"),
        ("entry_reached_rows", "entry_reached_rows"),
        ("win_like_rows", "win_like_rows"),
        ("loss_like_rows", "loss_like_rows"),
        ("unresolved_entry_rows", "unresolved_entry_rows"),
        ("potential_fakeout", "potential_fakeout"),
        ("potential_missed_turn", "potential_missed_turn"),
        ("bad_entry_timing", "bad_entry_timing"),
        ("safety_note", "safety_note"),
    ):
        lines.append(f"{label}: {_evidence_quality_summary_value(evidence.get(key))}")
    return lines


def _ohlcv_source_coverage_summary_evidence(
    result: dict[str, Any],
    notification_context: dict[str, Any],
    display_context: dict[str, Any],
) -> dict[str, Any] | None:
    direct_evidence = result.get("ohlcv_source_coverage_summary")
    if isinstance(direct_evidence, dict):
        return direct_evidence
    for container in (notification_context, display_context):
        if not isinstance(container, dict):
            continue
        evidence = container.get("ohlcv_source_coverage_summary")
        if isinstance(evidence, dict):
            return evidence
    for container in (
        result.get("app_contract_data") if isinstance(result.get("app_contract_data"), dict) else {},
        result.get("app_contract") if isinstance(result.get("app_contract"), dict) else {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict):
            evidence = container.get("ohlcv_source_coverage_summary")
            if isinstance(evidence, dict):
                return evidence
    return None


def _ohlcv_source_coverage_summary_lines(
    result: dict[str, Any],
    notification_context: dict[str, Any],
    display_context: dict[str, Any],
) -> list[str]:
    evidence = _ohlcv_source_coverage_summary_evidence(result, notification_context, display_context)
    if not isinstance(evidence, dict):
        return []

    lines = [
        "",
        "【OHLCV source coverage summary】",
        "local/report-only の表示です。candidate timestamp と OHLCV coverage だけを見て、実行はしません。",
        "安全境界: report-only / not FORMAL_GO / no automatic order / human decides manually",
    ]
    if str(evidence.get("ohlcv_range_freshness_status", "")).strip() == "stale_before_latest_candidate":
        lines.append(
            "OHLCV stale coverage warning: report-only / not FORMAL_GO / no automatic order / human decides manually; "
            "stale_before_latest_candidate; old OHLCV coverage can make no_ohlcv dominate; "
            f"candidate_max_after_ohlcv_end_hours: {_evidence_quality_summary_value(evidence.get('candidate_max_after_ohlcv_end_hours'))}"
        )
    for label, key in (
        ("candidate_rows", "candidate_rows"),
        ("ohlcv_input_rows", "ohlcv_input_rows"),
        ("ohlcv_valid_rows", "ohlcv_valid_rows"),
        ("candidate_timestamp_rows", "candidate_timestamp_rows"),
        ("missing_candidate_timestamp_rows", "missing_candidate_timestamp_rows"),
        ("window_covered_rows", "window_covered_rows"),
        ("window_missing_rows", "window_missing_rows"),
        ("no_global_ohlcv_risk_rows", "no_global_ohlcv_risk_rows"),
        ("window_missing_rate", "window_missing_rate"),
        ("ohlcv_start", "ohlcv_start"),
        ("ohlcv_end", "ohlcv_end"),
        ("candidate_timestamp_min", "candidate_timestamp_min"),
        ("candidate_timestamp_max", "candidate_timestamp_max"),
        ("candidate_max_after_ohlcv_end_hours", "candidate_max_after_ohlcv_end_hours"),
        ("stale_threshold_hours", "stale_threshold_hours"),
        ("ohlcv_range_freshness_status", "ohlcv_range_freshness_status"),
        ("freshness_note", "freshness_note"),
        ("coverage_note", "coverage_note"),
        ("safety_note", "safety_note"),
    ):
        lines.append(f"{label}: {_evidence_quality_summary_value(evidence.get(key))}")
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
    lines.extend(_major_turning_point_diagnostic_lines(result, notification_context, display_context))
    lines.extend(_local_confirmation_lines())
    lines.extend(_safe_config_schema_audit_lines(result))
    lines.extend(_operator_triage_summary_lines(result))
    lines.extend(_big_chance_summary_lines(result))
    lines.extend(_integrated_evidence_overview_lines(result))
    lines.extend(_evidence_quality_summary_lines(result, notification_context, display_context))
    lines.extend(_ohlcv_source_coverage_summary_lines(result, notification_context, display_context))
    lines.extend(_post_eval_mail_line(result, display_context, notification_context))
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


def _notification_context_for_result(result: dict[str, Any]) -> dict[str, Any]:
    notification_context = build_notification_context(result)
    override = result.get("notification_context")
    if isinstance(override, dict):
        notification_context.update(override)
    followup_context = result.get("followup_context")
    if str(result.get("notification_kind", "main")).lower().strip() == "followup" and isinstance(followup_context, dict):
        notification_context.update(build_followup_notification_context(followup_context))
    return notification_context


def _followup_summary(result: dict[str, Any], display_context: dict[str, Any], notification_context: dict[str, Any]) -> str:
    followup_context = result.get("followup_context") if isinstance(result.get("followup_context"), dict) else {}
    reason_labels = [str(label).strip() for label in followup_context.get("reason_labels", []) if str(label).strip()]
    previous_signal_id = str(followup_context.get("previous_signal_id", "")).strip() or "未記録"
    previous_kind = str(followup_context.get("previous_notification_kind", "")).strip() or "未記録"
    valid_until = str(followup_context.get("valid_until_utc", "")).strip() or "未記録"
    human_message = str(followup_context.get("human_message") or FOLLOWUP_HUMAN_MESSAGE).strip()
    safety_boundary = str(followup_context.get("safety_boundary") or "report-only / no automatic order / human decides manually").strip()
    lines = [
        "【期限切れ・再評価】",
        "これは売買推奨メールではありません。",
        "前回通知は有効期限切れです。",
        f"- 前回通知: {previous_signal_id} / {previous_kind}",
        f"- 有効期限: {valid_until}",
    ]
    if reason_labels:
        lines.append(f"- 理由: {' / '.join(reason_labels)}")
    else:
        lines.append("- 理由: 有効期限切れ")
    lines.extend(
        [
            f"- {human_message}",
            f"- 再確認の見方: {display_context.get('direction_label', '相場は中立です')}",
            f"- 安全境界: {safety_boundary}",
            f"- 現在価格: {_format_price(result.get('current_price'))}",
            f"- {notification_context.get('entry_window_label', '前回通知の期限切れを確認')}",
        ]
    )
    lines.extend(_big_chance_summary_lines(result))
    return "\n".join(lines)


def _big_chance_summary_lines(result: dict[str, Any]) -> list[str]:
    candidate = result.get("big_chance_candidate")
    if not isinstance(candidate, dict) or not candidate.get("present"):
        return []
    status = str(candidate.get("status", "")).strip().lower()

    if status == "invalidated":
        lines = [
            "",
            "【Big Chance / Failed Thesis】 候補失効 / 再評価済み",
            "これは既に失効した候補の記録です。active な最優先候補ではありません。",
            f"- 見出し: {candidate.get('headline', '')}",
            f"- 要約: {candidate.get('operator_summary', '')}",
            f"- 側: {candidate.get('side', 'none')} / 型: {candidate.get('type', 'none')} / 状態: {candidate.get('status', 'none')}",
            f"- スコア: {candidate.get('score', 0)} / グレード: {candidate.get('grade', 'none')}",
            f"- 安全境界: {candidate.get('safety_boundary', 'report-only / not FORMAL_GO / no automatic order / human decides manually')}",
        ]
    else:
        lines = [
            "",
            "【Big Chance / Failed Thesis】",
            "これは通常スコアとは別の report-only な失敗仮説チャンスです。",
            f"- 見出し: {candidate.get('headline', '')}",
            f"- 要約: {candidate.get('operator_summary', '')}",
            f"- 側: {candidate.get('side', 'none')} / 型: {candidate.get('type', 'none')} / 状態: {candidate.get('status', 'none')}",
            f"- スコア: {candidate.get('score', 0)} / グレード: {candidate.get('grade', 'none')}",
            f"- 安全境界: {candidate.get('safety_boundary', 'report-only / not FORMAL_GO / no automatic order / human decides manually')}",
        ]
    macro_context = candidate.get("macro_context") if isinstance(candidate.get("macro_context"), dict) else {}
    failed_thesis = candidate.get("failed_thesis") if isinstance(candidate.get("failed_thesis"), dict) else {}
    activation = candidate.get("activation") if isinstance(candidate.get("activation"), dict) else {}
    invalidation = candidate.get("invalidation") if isinstance(candidate.get("invalidation"), dict) else {}
    evidence = candidate.get("evidence") if isinstance(candidate.get("evidence"), dict) else {}
    lines.extend(
        [
            f"- Macro: HTF={macro_context.get('signals_4h')} / 1h={macro_context.get('signals_1h')} / 15m={macro_context.get('signals_15m')} / map={macro_context.get('market_map_primary_state')}",
            f"- Failed thesis: prior={failed_thesis.get('prior_side')} / reasons={failed_thesis.get('failure_reason_labels')}",
            f"- Core principle: {failed_thesis.get('thesis_summary', 'Failed thesis is opportunity')}",
            f"- Activation: tf={activation.get('activation_tf')} / condition={activation.get('activation_condition')} / state={activation.get('activation_state')}",
            f"- Invalidation: tf={invalidation.get('invalidation_tf')} / condition={invalidation.get('invalidation_condition')} / state={invalidation.get('invalidation_state')}",
            f"- Evidence: price={evidence.get('current_price')} / long_pos={evidence.get('current_price_position_long')} / short_pos={evidence.get('current_price_position_short')}",
        ]
    )
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
    lines.extend(_major_turning_point_diagnostic_lines(result, notification_context, display_context))
    lines.extend(_local_confirmation_lines())
    lines.extend(_safe_config_schema_audit_lines(result))
    lines.extend(_operator_triage_summary_lines(result))
    lines.extend(_big_chance_summary_lines(result))
    lines.extend(_integrated_evidence_overview_lines(result))
    lines.extend(_evidence_quality_summary_lines(result, notification_context, display_context))
    lines.extend(_ohlcv_source_coverage_summary_lines(result, notification_context, display_context))
    lines.extend(_post_eval_mail_line(result, display_context, notification_context))
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
    notification_context = _notification_context_for_result(result)
    jst_ts = str(result.get("timestamp_jst", ""))[:16].replace("T", " ")
    price_text = _format_subject_price(result.get("current_price"))
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    big_chance_line = _compact_big_chance_line(result)
    if notification_kind == "followup":
        compact_hint = "再評価"
        if big_chance_line not in {"Big Chance: なし", "Big Chance: 候補失効 / 再評価済み"}:
            compact_hint = big_chance_line.replace("Big Chance: ", "")
        subject = f"⏱期限切れ | {compact_hint} | BTC {price_text}"
        return _apply_current_email_subject_prefix(subject)
    if big_chance_line != "Big Chance: なし":
        subject = f"⚡BigChance | {big_chance_line.replace('Big Chance: ', '')} | BTC {price_text}"
        return _apply_current_email_subject_prefix(subject)
    trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()
    if notification_kind == "attention":
        subject = f"👀 注意報 | {display_context['direction_compact_label']} / {notification_context.get('execution_label', '見送り')} | BTC {price_text}"
        return _apply_current_email_subject_prefix(subject)
    if trade_gate == "pass" and paper_order_status == "planned":
        subject = f"🧪 紙実行候補 | 実弾不可 | BTC {price_text}"
    else:
        subject = f"📊 結論 | {display_context['direction_compact_label']} / {notification_context.get('execution_label', '見送り')} | BTC {price_text}"
    return _apply_current_email_subject_prefix(subject)


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
    notification_context = _notification_context_for_result(result_payload)
    return (
        _compact_email_body(
            result=result_payload,
            display_context=display_context,
            notification_context=notification_context,
        ),
        provider_name,
    )
