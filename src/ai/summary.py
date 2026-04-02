from __future__ import annotations

from typing import Any

from src.presentation.sanitize import (
    CONFIDENCE_METRIC_LABELS,
    build_display_context,
    build_notification_context,
    sanitize_flag_list,
    sanitize_user_text,
)


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
    lines = [
        "【結論】",
        f"ステータス: {notification_context.get('status_label', '中立')}（{notification_context.get('status_explanation', '方向優位なし')}）",
        f"方向判断: {display_context['direction_label']}",
        f"執行判断: {notification_context.get('execution_label', '見送り')}",
        f"現値帯の扱い: {notification_context.get('entry_window_label', '不可')}",
        f"有効目安: {notification_context.get('validity_label', '次回更新までを目安')}",
        "",
        "【いま重視する理由】",
    ]
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
        "これは売買推奨メールではなく、方向の変化を早めに共有する注意通知です。",
        "",
        "【今の見立て】",
        f"- ステータス: {notification_context.get('status_label', '注意報')}（{notification_context.get('status_explanation', '方向変化の早期共有')}）",
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
    subject = (
        f"[{notification_context.get('status_label', '中立')}] {notification_context.get('execution_label', '見送り')} | "
        f"{display_context['direction_compact_label']} | {headline_reason} "
        f"【BTC:{price_text}】 {jst_ts}{suffix}"
    ).strip()
    if result.get("ai_advice") is None:
        subject = f"[機械判定のみ] {subject}"
    return subject


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
