from __future__ import annotations

import re
from typing import Any


SUMMARY_VARIANT = "direction_execution_split_v2"
ADVICE_VARIANT = "direction_execution_split_v2"
PROMPT_VARIANT = "summary_template_split_v2+advice_prompt_split_v2"
EVALUATION_TRACE_VERSION = "v0.2"
CONFIDENCE_METRIC_LABELS = {
    "direction": "方向の強さ",
    "execution": "実行しやすさ",
    "wait": "待機圧力",
}


_DIRECTION_LABELS = {
    "long": "相場は上方向バイアスです",
    "short": "相場は下方向バイアスです",
    "wait": "相場は中立です",
    "no_trade": "相場は中立です",
    "range": "相場は中立です",
}

_DIRECTION_COMPACT = {
    "long": "上方向バイアス",
    "short": "下方向バイアス",
    "wait": "中立",
    "no_trade": "中立",
    "range": "中立",
}

_PRELABEL_LABELS = {
    "ENTRY_OK": "位置条件は悪くない",
    "RISKY_ENTRY": "位置はやや注意",
    "SWEEP_WAIT": "流動性回収待ち",
    "NO_TRADE_CANDIDATE": "現状は見送り",
}

_SETUP_LABELS = {
    "ready": "条件付きで検討",
    "watch": "監視継続",
    "invalid": "現状は見送り",
    "none": "未形成",
}

_CODE_LABELS = {
    "RR_insufficient": "利益幅に対して損切り幅のバランスが弱い",
    "RR_insufficient_long": "ロング側の利益幅が不足気味",
    "RR_insufficient_short": "ショート側の利益幅が不足気味",
    "Critical_zone_warning": "重要な価格帯の近くで短期ノイズが出やすい",
    "Funding_prohibited": "Funding 条件が悪く逆行リスクに注意",
    "Funding_prohibited_long": "Funding 条件がロングに不利",
    "Funding_prohibited_short": "Funding 条件がショートに不利",
    "Funding_warning": "Funding に偏りがあり追いかけは慎重",
    "Funding_warning_long": "Funding がロング寄りに過熱",
    "Funding_warning_short": "Funding がショート寄りに過熱",
    "ATR_extreme": "ボラティリティが極端で値動きが荒い",
    "ATR_warning": "ボラティリティが平常より荒い",
    "volatile_regime": "値動きが荒く方向の継続性が弱い",
    "upper_liquidity_close": "上側流動性が近く先に振られやすい",
    "lower_liquidity_close": "下側流動性が近く先に振られやすい",
    "bid_wall_close": "近い買い板があり短期ノイズに注意",
    "ask_wall_close": "近い売り板があり短期ノイズに注意",
    "sweep_wait": "まだ流動性回収待ち",
    "sweep_incomplete": "流動性回収が未完了",
    "liquidation_cluster_above": "上側の清算クラスターが近い",
    "liquidation_cluster_below": "下側の清算クラスターが近い",
    "orderbook_ask_heavy": "売り板が厚く上値が重い",
    "orderbook_bid_heavy": "買い板が厚く下値が固い",
    "cvd_bearish_divergence": "売り圧はあるが位置の改善待ち",
    "cvd_bullish_divergence": "買い圧はあるが位置の改善待ち",
    "short_cover_risk": "ショートの買い戻しで上振れしやすい",
    "long_flush_exhaustion": "ロング投げの一巡後で反発に注意",
    "rr_below_min": "RR 条件が基準未満",
    "atr_out_of_range": "ATR 条件が基準外",
    "funding_long_prohibited": "Funding 条件がロング禁止域",
    "funding_short_prohibited": "Funding 条件がショート禁止域",
    "confidence_below_min": "総合強度が基準未満",
    "warning_cluster": "警戒要因が重なっている",
    "inside_entry_zone_with_trigger": "再検討帯と発火条件が揃っている",
    "near_entry_zone_with_trigger": "再検討帯に近く発火条件も確認済み",
    "near_entry_zone_waiting_trigger": "再検討帯は近いが発火条件待ち",
    "entry_zone_not_reached": "まだ再検討帯に届いていない",
    "invalid_empty_setup": "セットアップ算出に必要な条件が不足",
    "balanced_location": "位置評価は中立",
    "lower_liquidity_distance": "下側流動性までの余地が小さい",
    "upper_liquidity_distance": "上側流動性までの余地が小さい",
    "ask_wall_distance": "近い売り板が抵抗になりやすい",
    "bid_wall_distance": "近い買い板が支持になりやすい",
    "liquidation_cluster_distance": "清算クラスターが近く乱高下に注意",
    "direction_strength": "方向の強さ",
    "execution_readiness": "実行しやすさ",
    "wait_pressure": "待機圧力",
}

_UNKNOWN_CODE_PATTERN = re.compile(r"\b[A-Za-z]+(?:_[A-Za-z0-9]+)+\b")


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def _split_raw_text(text: str) -> list[str]:
    parts = re.split(r"[\n,;/]+| \| |\s/\s", text)
    return [part.strip() for part in parts if part.strip()]


def direction_label(value: Any) -> str:
    return _DIRECTION_LABELS.get(str(value).lower(), "相場は中立です")


def direction_compact_label(value: Any) -> str:
    return _DIRECTION_COMPACT.get(str(value).lower(), "中立")


def prelabel_label(value: Any) -> str:
    return _PRELABEL_LABELS.get(str(value).upper(), "内部評価あり")


def setup_status_label(value: Any) -> str:
    return _SETUP_LABELS.get(str(value).lower(), "未形成")


def sanitize_reason_codes(codes: list[Any]) -> list[str]:
    sanitized: list[str] = []
    for code in codes:
        raw = str(code or "").strip()
        if not raw:
            continue
        sanitized.append(_CODE_LABELS.get(raw, "内部要因のため詳細省略"))
    return _dedupe_preserve(sanitized)


def sanitize_flag_list(flags: list[Any]) -> list[str]:
    return sanitize_reason_codes(flags)


def sanitize_user_text(text: Any) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    replaced = raw
    for code, label in sorted(_CODE_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
        replaced = re.sub(rf"\b{re.escape(code)}\b", label, replaced)
    if _UNKNOWN_CODE_PATTERN.search(replaced):
        parts = []
        for part in _split_raw_text(replaced):
            if _UNKNOWN_CODE_PATTERN.fullmatch(part):
                parts.append("内部要因のため詳細省略")
            else:
                cleaned = _UNKNOWN_CODE_PATTERN.sub("内部要因のため詳細省略", part).strip()
                if cleaned:
                    parts.append(cleaned)
        replaced = " / ".join(_dedupe_preserve(parts))
    return replaced.strip()


def _primary_setup_status(result: dict[str, Any]) -> str:
    status = str(result.get("primary_setup_status", "")).strip().lower()
    if status:
        return status
    bias = str(result.get("bias", "")).lower()
    if bias == "long":
        return str((result.get("long_setup") or {}).get("status", "none")).strip().lower() or "none"
    if bias == "short":
        return str((result.get("short_setup") or {}).get("status", "none")).strip().lower() or "none"
    return "none"


def _primary_setup_reason(result: dict[str, Any]) -> str:
    reason = str(result.get("primary_setup_reason", "")).strip()
    if reason:
        return reason
    bias = str(result.get("bias", "")).lower()
    if bias == "long":
        return str((result.get("long_setup") or {}).get("status_reason_code", "")).strip()
    if bias == "short":
        return str((result.get("short_setup") or {}).get("status_reason_code", "")).strip()
    return ""


def _wait_label_for_long(result: dict[str, Any], risk_flags: list[str], reason_code: str, prelabel: str) -> str:
    if prelabel == "NO_TRADE_CANDIDATE":
        return "上目線だが現状は見送り"
    if "lower_liquidity_close" in risk_flags or prelabel == "SWEEP_WAIT":
        return "下側流動性回収待ち"
    if reason_code in {"near_entry_zone_waiting_trigger", "entry_zone_not_reached"}:
        return "押し目待ち"
    if "ask_wall_close" in risk_flags or "orderbook_ask_heavy" in risk_flags:
        return "反発確認待ち"
    return "上目線で待機"


def _wait_label_for_short(result: dict[str, Any], risk_flags: list[str], reason_code: str, prelabel: str) -> str:
    if prelabel == "NO_TRADE_CANDIDATE":
        return "下目線だが現状は見送り"
    if "upper_liquidity_close" in risk_flags or prelabel == "SWEEP_WAIT":
        return "上側流動性回収待ち"
    if reason_code in {"near_entry_zone_waiting_trigger", "entry_zone_not_reached"}:
        return "戻り売り待ち"
    if "bid_wall_close" in risk_flags or "orderbook_bid_heavy" in risk_flags:
        return "再失速確認待ち"
    return "下目線で待機"


def _action_label(result: dict[str, Any], status: str, prelabel: str, risk_flags: list[str], reason_code: str) -> str:
    bias = str(result.get("bias", "")).lower()
    if bias not in {"long", "short"}:
        return "見送り"
    if status == "ready":
        return "ロングは条件付きで検討" if bias == "long" else "ショートは条件付きで検討"
    if status == "invalid":
        return "上目線だが現状は見送り" if bias == "long" else "下目線だが現状は見送り"
    if bias == "long":
        return _wait_label_for_long(result, risk_flags, reason_code, prelabel)
    return _wait_label_for_short(result, risk_flags, reason_code, prelabel)


def _subject_action_label(action_label: str) -> str:
    return action_label.replace("は", "").replace("だが", "/").replace("現状", "").strip(" /")


def _reason_sources(result: dict[str, Any]) -> list[str]:
    setup = (result.get("long_setup") or {}) if str(result.get("bias", "")).lower() == "long" else (result.get("short_setup") or {})
    reasons: list[str] = []
    reasons.extend(str(flag) for flag in result.get("warning_flags", []) if str(flag).strip())
    reasons.extend(str(flag) for flag in result.get("risk_flags", []) if str(flag).strip())
    reasons.extend(str(flag) for flag in result.get("no_trade_flags", []) if str(flag).strip())
    reasons.extend(str(code) for code in setup.get("invalid_reason_codes", []) if str(code).strip())
    primary_reason = _primary_setup_reason(result)
    if primary_reason:
        reasons.append(primary_reason)
    invalid_reason = sanitize_user_text(result.get("invalid_reason", ""))
    if invalid_reason:
        reasons.append(invalid_reason)
    ai_advice = result.get("ai_advice")
    if isinstance(ai_advice, dict):
        reasons.extend(str(flag) for flag in ai_advice.get("warnings", []) if str(flag).strip())
    return reasons


def build_display_context(result: dict[str, Any]) -> dict[str, Any]:
    bias = str(result.get("bias", "")).lower()
    status = _primary_setup_status(result)
    prelabel = str(result.get("prelabel", "")).upper()
    risk_flags = [str(flag).strip() for flag in result.get("risk_flags", []) if str(flag).strip()]
    reason_code = _primary_setup_reason(result)
    action = _action_label(result, status, prelabel, risk_flags, reason_code)
    reason_labels = sanitize_reason_codes(_reason_sources(result))
    if not reason_labels:
        fallback_reason = sanitize_user_text(result.get("invalid_reason", "")) or "大きな待機理由は出ていません"
        reason_labels = [fallback_reason]
    return {
        "direction_label": direction_label(bias),
        "direction_compact_label": direction_compact_label(bias),
        "action_label": action,
        "action_compact_label": _subject_action_label(action),
        "entry_quality_label": prelabel_label(prelabel),
        "setup_status_label": setup_status_label(status),
        "confidence_metric_labels": dict(CONFIDENCE_METRIC_LABELS),
        "wait_reason_labels": _dedupe_preserve(reason_labels),
        "prelabel_display_label": prelabel_label(prelabel),
        "primary_setup_status": status,
    }
