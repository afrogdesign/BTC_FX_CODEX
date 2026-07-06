from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


BIG_CHANCE_SCHEMA_VERSION = "big_chance_failed_thesis.v1"
BIG_CHANCE_ARTIFACT_SCHEMA_VERSION = "big_chance_artifact.v1"
SAFETY_BOUNDARY = "report-only / not FORMAL_GO / no automatic order / human decides manually"


def _to_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed == 0.0:
        return None
    return parsed


def _round2(value: Any) -> float | None:
    parsed = _to_float(value)
    if parsed is None:
        return None
    return round(parsed, 2)


def _normalize_side(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"long", "buy"}:
        return "long"
    if text in {"short", "sell"}:
        return "short"
    return ""


def _iter_text_values(node: Any) -> list[str]:
    values: list[str] = []
    if isinstance(node, dict):
        for value in node.values():
            values.extend(_iter_text_values(value))
    elif isinstance(node, list):
        for value in node:
            values.extend(_iter_text_values(value))
    elif node is not None:
        values.append(str(node))
    return values


def _zone_bounds(zone: dict[str, Any] | None) -> tuple[float | None, float | None]:
    if not isinstance(zone, dict):
        return None, None
    low = _round2(zone.get("low"))
    high = _round2(zone.get("high"))
    if low is None or high is None:
        return None, None
    if low > high:
        low, high = high, low
    return low, high


def _zone_contains(price: float | None, zone: dict[str, Any] | None) -> bool:
    if price is None:
        return False
    low, high = _zone_bounds(zone)
    return low is not None and high is not None and low <= price <= high


def _zone_center(zone: dict[str, Any] | None) -> float | None:
    low, high = _zone_bounds(zone)
    if low is None or high is None:
        return None
    return (low + high) / 2.0


def _classify_price_position(
    price: float | None,
    shallow_zone: dict[str, Any] | None,
    value_zone: dict[str, Any] | None,
    invalidation_zone: dict[str, Any] | None,
) -> str:
    if price is None:
        return "outside_known_zones"

    for label, zone in (
        ("inside_invalidation_zone", invalidation_zone),
        ("inside_value_defense_zone", value_zone),
        ("inside_shallow_retest_zone", shallow_zone),
    ):
        if _zone_contains(price, zone):
            return label

    all_bounds: list[tuple[float, float]] = []
    for zone in (shallow_zone, value_zone, invalidation_zone):
        low, high = _zone_bounds(zone)
        if low is not None and high is not None:
            all_bounds.append((low, high))

    if not all_bounds:
        return "outside_known_zones"

    lows = [low for low, _high in all_bounds]
    highs = [high for _low, high in all_bounds]
    if price > max(highs):
        return "above_zones"
    if price < min(lows):
        return "below_zones"

    ordered = [zone for zone in (shallow_zone, value_zone) if isinstance(zone, dict)]
    centers = [(_zone_center(zone), zone) for zone in ordered]
    centers = [(center, zone) for center, zone in centers if center is not None]
    if len(centers) == 2:
        centers.sort(key=lambda item: item[0])
        lower_zone = centers[0][1]
        upper_zone = centers[1][1]
        lower_high = _zone_bounds(lower_zone)[1]
        upper_low = _zone_bounds(upper_zone)[0]
        if lower_high is not None and upper_low is not None and lower_high < price < upper_low:
            return "between_shallow_and_value_defense"

    return "outside_known_zones"


def _extract_value_defense(setup: dict[str, Any] | None) -> dict[str, Any]:
    setup = setup or {}
    vd = setup.get("value_defense_entry_layer") if isinstance(setup, dict) else {}
    vd = vd if isinstance(vd, dict) else {}
    return {
        "side": vd.get("side"),
        "lifecycle_state": vd.get("lifecycle_state"),
        "market_entry_status": vd.get("market_entry_status"),
        "shallow_retest_zone": vd.get("shallow_retest_zone"),
        "shallow_retest_risk": vd.get("shallow_retest_risk"),
        "value_defense_zone": vd.get("value_defense_zone"),
        "defense_zone_basis": vd.get("defense_zone_basis"),
        "invalidation_zone": vd.get("invalidation_zone"),
        "reclaim_trigger": vd.get("reclaim_trigger"),
        "continuation_trigger": vd.get("continuation_trigger"),
        "operator_guidance": vd.get("operator_guidance"),
        "safety_boundary": vd.get("safety_boundary"),
    }


def _normal_score_context(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "bias": result.get("bias"),
        "signals_4h": result.get("signals_4h"),
        "signals_1h": result.get("signals_1h"),
        "signals_15m": result.get("signals_15m"),
        "long_display_score": result.get("long_display_score"),
        "short_display_score": result.get("short_display_score"),
        "score_gap": result.get("score_gap"),
        "confidence": result.get("confidence"),
        "primary_setup_status": result.get("primary_setup_status"),
        "primary_setup_reason": result.get("primary_setup_reason"),
        "signal_tier": result.get("signal_tier"),
        "trade_execution_gate": result.get("trade_execution_gate"),
    }


def _macro_context(result: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "market_regime": result.get("market_regime"),
        "phase": result.get("phase"),
        "signals_4h": result.get("signals_4h"),
        "signals_1h": result.get("signals_1h"),
        "signals_15m": result.get("signals_15m"),
        "market_map_primary_state": result.get("market_map_primary_state"),
        "level_flip_state": result.get("level_flip_state"),
        "trend_flip_state": result.get("trend_flip_state"),
        "failed_breakout_state": result.get("failed_breakout_state"),
        "transition_direction": result.get("transition_direction"),
        "active_level_role": result.get("active_level_role"),
        "previous_signal_id": (previous or {}).get("signal_id"),
        "previous_notification_kind": (previous or {}).get("notification_kind"),
        "previous_bias": (previous or {}).get("bias"),
    }


def _failed_thesis_labels(target_side: str) -> tuple[str, str, list[str]]:
    if target_side == "short":
        return (
            "long_failed_to_short",
            "ロング失敗→ショート候補",
            [
                "failed_long_thesis",
                "support_to_resistance_flip",
                "trend_flip_early_down",
                "short_side_activation",
            ],
        )
    if target_side == "long":
        return (
            "short_failed_to_long",
            "ショート失敗→ロング候補",
            [
                "failed_short_thesis",
                "resistance_to_support_flip",
                "trend_flip_early_up",
                "long_side_activation",
            ],
        )
    return "none", "", []


def _reason_labels(reason_codes: list[str], target_side: str) -> list[str]:
    labels: list[str] = []
    mapping = {
        "failed_long_thesis": "ロング仮説が崩れた",
        "failed_short_thesis": "ショート仮説が崩れた",
        "support_to_resistance_flip": "サポート→レジスタンス反転",
        "resistance_to_support_flip": "レジスタンス→サポート反転",
        "trend_flip_early_down": "早期下方向転換",
        "trend_flip_early_up": "早期上方向転換",
        "1h_wait_pressure": "1時間足は様子見",
        "1h_side_alignment": "1時間足が候補側に寄っている",
        "15m_side_activation": "15分足が候補側で起動",
        "price_position_extension": "価格が拡張余地に入っている",
        "previous_side_failed": "前回仮説が崩れた流れ",
    }
    for code in reason_codes:
        label = mapping.get(code)
        if label and label not in labels:
            labels.append(label)
    if not labels:
        labels.append("Failed thesis の反対側で機会候補")
    if target_side == "short" and "ショート" not in "".join(labels):
        labels.append("ショート候補")
    if target_side == "long" and "ロング" not in "".join(labels):
        labels.append("ロング候補")
    return labels


def _activation_summary(target_side: str, positions: dict[str, str], result: dict[str, Any]) -> dict[str, Any]:
    side_signal = "short" if target_side == "short" else "long"
    signal_15m = str(result.get("signals_15m", "")).strip().lower()
    signal_1h = str(result.get("signals_1h", "")).strip().lower()
    signal_4h = str(result.get("signals_4h", "")).strip().lower()
    price_position = positions.get("short" if target_side == "short" else "long", "outside_known_zones")
    return {
        "activation_tf": "15m",
        "activation_condition": f"signals_15m == {side_signal}",
        "activation_state": "confirmed" if signal_15m == side_signal else "watch",
        "tf_alignment": {
            "4h": signal_4h,
            "1h": signal_1h,
            "15m": signal_15m,
        },
        "price_position": price_position,
        "price_position_trigger": "above_zones" if target_side == "short" else "below_zones",
    }


def _invalidation_summary(target_side: str, positions: dict[str, str], result: dict[str, Any]) -> dict[str, Any]:
    opposite = "long" if target_side == "short" else "short"
    signal_15m = str(result.get("signals_15m", "")).strip().lower()
    signal_1h = str(result.get("signals_1h", "")).strip().lower()
    price_position = positions.get(opposite, "outside_known_zones")
    return {
        "invalidation_tf": "15m",
        "invalidation_condition": f"signals_15m == {opposite} and signals_1h == {opposite}",
        "invalidation_state": "watch",
        "opposite_side_signal": {
            "4h": str(result.get("signals_4h", "")).strip().lower(),
            "1h": signal_1h,
            "15m": signal_15m,
        },
        "price_position": price_position,
        "price_position_trigger": "below_zones" if target_side == "short" else "above_zones",
    }


def _candidate_for_side(current: dict[str, Any], previous: dict[str, Any] | None, target_side: str) -> dict[str, Any]:
    opposite = "long" if target_side == "short" else "short"
    long_setup = current.get("long_setup") if isinstance(current.get("long_setup"), dict) else {}
    short_setup = current.get("short_setup") if isinstance(current.get("short_setup"), dict) else {}
    long_vd = _extract_value_defense(long_setup)
    short_vd = _extract_value_defense(short_setup)
    current_price = _to_float(current.get("current_price"))
    current_positions = {
        "long": _classify_price_position(
            current_price,
            long_vd.get("shallow_retest_zone") or long_setup.get("entry_zone"),
            long_vd.get("value_defense_zone"),
            long_vd.get("invalidation_zone"),
        ),
        "short": _classify_price_position(
            current_price,
            short_vd.get("shallow_retest_zone") or short_setup.get("entry_zone"),
            short_vd.get("value_defense_zone"),
            short_vd.get("invalidation_zone"),
        ),
    }
    bias = str(current.get("bias", "")).strip().lower()
    previous_bias = str((previous or {}).get("bias", "")).strip().lower()
    signals_4h = str(current.get("signals_4h", "")).strip().lower()
    signals_1h = str(current.get("signals_1h", "")).strip().lower()
    signals_15m = str(current.get("signals_15m", "")).strip().lower()
    market_map_primary_state = " ".join(_iter_text_values(current.get("market_map_primary_state"))).strip().lower()
    market_map_flags = [str(item).strip().lower() for item in _iter_text_values(current.get("market_map_flags")) if str(item).strip()]
    level_flip_state = " ".join(_iter_text_values(current.get("level_flip_state"))).strip().lower()
    failed_breakout_state = " ".join(_iter_text_values(current.get("failed_breakout_state"))).strip().lower()
    trend_flip_state = " ".join(_iter_text_values(current.get("trend_flip_state"))).strip().lower()
    transition_direction = str(current.get("transition_direction", "")).strip().lower()
    value_defense = long_vd if target_side == "short" else short_vd
    target_value_position = current_positions["long" if target_side == "short" else "short"]

    reason_codes: list[str] = []
    score = 0

    if previous_bias == opposite:
        reason_codes.append("previous_side_failed")
        score += 12
    if bias == opposite:
        reason_codes.append("failed_%s_thesis" % opposite)
        score += 15
    if target_side == "short":
        if "support_to_resistance" in level_flip_state or any(
            flag in {"support_to_resistance_flip", "support_to_resistance_retest_confirmed"} for flag in market_map_flags
        ):
            reason_codes.append("support_to_resistance_flip")
            score += 28
        if any(token in text for text in (market_map_primary_state, failed_breakout_state, trend_flip_state) for token in ("early_down", "trend_flip")):
            reason_codes.append("trend_flip_early_down")
            score += 24
        if signals_1h in {"wait", "short"}:
            reason_codes.append("1h_wait_pressure")
            score += 10
        if signals_15m == "short":
            reason_codes.append("15m_side_activation")
            score += 18
        if target_value_position == "below_zones":
            reason_codes.append("price_position_extension")
            score += 12
        if str(value_defense.get("lifecycle_state", "")).strip().lower() in {"invalidated", "reclaim_wait"}:
            reason_codes.append("failed_long_thesis")
            score += 12
    else:
        if "resistance_to_support" in level_flip_state or any(
            flag in {"resistance_to_support_flip", "resistance_to_support_retest_confirmed"} for flag in market_map_flags
        ):
            reason_codes.append("resistance_to_support_flip")
            score += 28
        if any(token in text for text in (market_map_primary_state, failed_breakout_state, trend_flip_state) for token in ("early_up", "trend_flip")):
            reason_codes.append("trend_flip_early_up")
            score += 24
        if signals_1h in {"wait", "long"}:
            reason_codes.append("1h_side_alignment")
            score += 10
        if signals_15m == "long":
            reason_codes.append("15m_side_activation")
            score += 18
        if target_value_position == "above_zones":
            reason_codes.append("price_position_extension")
            score += 12
        if str(value_defense.get("lifecycle_state", "")).strip().lower() in {"invalidated", "reclaim_wait"}:
            reason_codes.append("failed_short_thesis")
            score += 12

    if target_side == "short" and current_positions["long"] == "above_zones":
        score += 8
    if target_side == "long" and current_positions["short"] == "below_zones":
        score += 8

    reason_codes = list(dict.fromkeys(reason_codes))
    reason_labels = _reason_labels(reason_codes, target_side)

    status = "watch"
    if not reason_codes:
        score = 0
    else:
        if (target_side == "short" and signals_15m == "long") or (target_side == "long" and signals_15m == "short"):
            status = "invalidated"
        elif signals_4h == target_side and signals_1h == target_side and signals_15m == target_side:
            status = "follow_through"
            score += 18
        elif signals_15m == target_side and signals_1h == target_side:
            status = "triggered"
            score += 14
        elif signals_15m == target_side or signals_1h == target_side:
            status = "armed"
            score += 8
        elif any(position == ("below_zones" if target_side == "short" else "above_zones") for position in (current_positions["long"], current_positions["short"])):
            status = "armed"
            score += 5
        else:
            status = "watch"

    if status != "invalidated" and score >= 84:
        status = "follow_through"
    elif status != "invalidated" and score >= 70:
        status = "triggered"
    elif status != "invalidated" and score >= 45:
        status = "armed"
    elif status != "invalidated" and score < 35:
        status = "watch"

    if status == "invalidated" and score < 35:
        score = 35

    present = bool(reason_codes) and score >= 35 and status != "none"
    if not present:
        return {
            "schema_version": BIG_CHANCE_SCHEMA_VERSION,
            "present": False,
            "side": "none",
            "type": "none",
            "status": "none",
            "score": 0,
            "grade": "none",
            "headline": "",
            "operator_summary": "",
            "macro_context": _macro_context(current, previous),
            "failed_thesis": {},
            "activation": {},
            "invalidation": {},
            "reason_codes": [],
            "reason_labels": [],
            "evidence": {
                "current_price": current_price,
                "current_price_position_long": current_positions["long"],
                "current_price_position_short": current_positions["short"],
                "long_value_defense": long_vd,
                "short_value_defense": short_vd,
            },
            "normal_score_context": _normal_score_context(current),
            "safety_boundary": SAFETY_BOUNDARY,
        }

    grade = "none"
    if score >= 90:
        grade = "S"
    elif score >= 75:
        grade = "A"
    elif score >= 60:
        grade = "B"
    elif score >= 45:
        grade = "C"

    type_code, headline, base_reason_codes = _failed_thesis_labels(target_side)
    for reason_code in base_reason_codes:
        if reason_code not in reason_codes:
            reason_codes.append(reason_code)
    reason_labels = _reason_labels(reason_codes, target_side)
    if target_side == "short":
        operator_summary = "ロング仮説が崩れたため、ショート側の Big Chance を report-only で監視します。HTF の反転と 15m の起動を分けて見るのが要点です。"
    else:
        operator_summary = "ショート仮説が崩れたため、ロング側の Big Chance を report-only で監視します。HTF の reclaim と 15m の起動を分けて見るのが要点です。"

    activation = _activation_summary(target_side, current_positions, current)
    invalidation = _invalidation_summary(target_side, current_positions, current)

    return {
        "schema_version": BIG_CHANCE_SCHEMA_VERSION,
        "present": True,
        "side": target_side,
        "type": type_code,
        "status": status,
        "score": int(score),
        "grade": grade,
        "headline": headline,
        "operator_summary": operator_summary,
        "macro_context": _macro_context(current, previous),
        "failed_thesis": {
            "prior_side": opposite,
            "failure_reason": base_reason_codes,
            "failure_reason_labels": _reason_labels(base_reason_codes, target_side),
            "thesis_summary": "Failed thesis is opportunity",
        },
        "activation": activation,
        "invalidation": invalidation,
        "reason_codes": reason_codes,
        "reason_labels": reason_labels,
        "evidence": {
            "current_price": current_price,
            "current_price_position_long": current_positions["long"],
            "current_price_position_short": current_positions["short"],
            "market_map_primary_state": current.get("market_map_primary_state"),
            "market_map_flags": list(dict.fromkeys(market_map_flags)),
            "level_flip_state": current.get("level_flip_state"),
            "trend_flip_state": current.get("trend_flip_state"),
            "failed_breakout_state": current.get("failed_breakout_state"),
            "transition_direction": current.get("transition_direction"),
            "bias": current.get("bias"),
            "previous_bias": (previous or {}).get("bias"),
            "long_value_defense": long_vd,
            "short_value_defense": short_vd,
        },
        "normal_score_context": _normal_score_context(current),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def evaluate_big_chance(current: dict[str, Any], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    current = current if isinstance(current, dict) else {}
    previous = previous if isinstance(previous, dict) else None
    candidates = [
        _candidate_for_side(current, previous, "short"),
        _candidate_for_side(current, previous, "long"),
    ]
    best = max(candidates, key=lambda item: (int(item.get("score", 0) or 0), len(item.get("reason_codes", []))))
    if not best.get("present"):
        return best
    return best


def build_big_chance_markdown(candidate: dict[str, Any]) -> str:
    candidate = candidate if isinstance(candidate, dict) else {}
    lines: list[str] = ["## Big Chance / Failed Thesis", ""]
    if not candidate.get("present"):
        lines.extend(
            [
                "- present: false",
                f"- safety_boundary: {candidate.get('safety_boundary', SAFETY_BOUNDARY)}",
                "",
                "## Observation",
                "今回は Big Chance 候補は未検出です。",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            f"- schema_version: {candidate.get('schema_version', BIG_CHANCE_SCHEMA_VERSION)}",
            f"- present: true",
            f"- side: {candidate.get('side', 'none')}",
            f"- type: {candidate.get('type', 'none')}",
            f"- status: {candidate.get('status', 'none')}",
            f"- score: {candidate.get('score', 0)}",
            f"- grade: {candidate.get('grade', 'none')}",
            f"- headline: {candidate.get('headline', '')}",
            f"- operator_summary: {candidate.get('operator_summary', '')}",
            "",
            "## Macro Context",
        ]
    )
    macro_context = candidate.get("macro_context") if isinstance(candidate.get("macro_context"), dict) else {}
    for key in ("market_regime", "phase", "signals_4h", "signals_1h", "signals_15m", "market_map_primary_state", "level_flip_state", "trend_flip_state", "failed_breakout_state", "transition_direction", "active_level_role", "previous_signal_id", "previous_notification_kind", "previous_bias"):
        lines.append(f"- {key}: {macro_context.get(key)}")

    lines.extend(["", "## Failed Thesis"])
    failed_thesis = candidate.get("failed_thesis") if isinstance(candidate.get("failed_thesis"), dict) else {}
    for key in ("prior_side", "failure_reason", "failure_reason_labels", "thesis_summary"):
        lines.append(f"- {key}: {failed_thesis.get(key)}")

    lines.extend(["", "## Activation"])
    activation = candidate.get("activation") if isinstance(candidate.get("activation"), dict) else {}
    for key in ("activation_tf", "activation_condition", "activation_state", "price_position", "price_position_trigger"):
        lines.append(f"- {key}: {activation.get(key)}")

    lines.extend(["", "## Invalidation"])
    invalidation = candidate.get("invalidation") if isinstance(candidate.get("invalidation"), dict) else {}
    for key in ("invalidation_tf", "invalidation_condition", "invalidation_state", "price_position", "price_position_trigger"):
        lines.append(f"- {key}: {invalidation.get(key)}")

    lines.extend(["", "## Reason Codes"])
    for code in candidate.get("reason_codes", []) or []:
        lines.append(f"- {code}")
    lines.extend(["", "## Reason Labels"])
    for label in candidate.get("reason_labels", []) or []:
        lines.append(f"- {label}")

    lines.extend(["", "## Evidence"])
    evidence = candidate.get("evidence") if isinstance(candidate.get("evidence"), dict) else {}
    for key in (
        "current_price",
        "current_price_position_long",
        "current_price_position_short",
        "market_map_primary_state",
        "market_map_flags",
        "level_flip_state",
        "trend_flip_state",
        "failed_breakout_state",
        "transition_direction",
        "bias",
        "previous_bias",
        "long_value_defense",
        "short_value_defense",
    ):
        value = evidence.get(key)
        lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value}")

    lines.extend(["", "## Normal Score Context"])
    normal_score_context = candidate.get("normal_score_context") if isinstance(candidate.get("normal_score_context"), dict) else {}
    for key in ("bias", "signals_4h", "signals_1h", "signals_15m", "long_display_score", "short_display_score", "score_gap", "confidence", "primary_setup_status", "primary_setup_reason", "signal_tier", "trade_execution_gate"):
        lines.append(f"- {key}: {normal_score_context.get(key)}")

    lines.extend(
        [
            "",
            "## Safety Boundary",
            f"- {candidate.get('safety_boundary', SAFETY_BOUNDARY)}",
        ]
    )
    return "\n".join(lines)


def _artifact_prefix(artifact: dict[str, Any], replay_signal_id: str | None = None) -> str:
    if replay_signal_id:
        return f"replay_{replay_signal_id}"
    signal_id = str(artifact.get("signal_id", "")).strip()
    if signal_id:
        return signal_id
    return "latest"


def build_big_chance_artifact(
    current: dict[str, Any],
    *,
    previous: dict[str, Any] | None = None,
    source_file: Path | None = None,
    replay_signal_id: str | None = None,
) -> dict[str, Any]:
    candidate = evaluate_big_chance(current, previous)
    artifact = {
        "schema_version": BIG_CHANCE_ARTIFACT_SCHEMA_VERSION,
        "source_file": str(source_file) if source_file is not None else "",
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "signal_id": str(current.get("signal_id", "")).strip(),
        "timestamp_jst": current.get("timestamp_jst"),
        "previous_signal_id": (previous or {}).get("signal_id"),
        "previous_notification_kind": (previous or {}).get("notification_kind"),
        "replay_signal_id": replay_signal_id,
        "candidate": candidate,
    }
    return artifact


def write_big_chance_artifact(
    artifact: dict[str, Any],
    out_dir: Path,
    *,
    replay_signal_id: str | None = None,
) -> tuple[Path, Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = _artifact_prefix(artifact, replay_signal_id=replay_signal_id or artifact.get("replay_signal_id"))
    json_path = out_dir / f"{prefix}.json"
    md_path = out_dir / f"{prefix}.md"
    latest_json_path = out_dir / "latest.json"
    latest_md_path = out_dir / "latest.md"
    json_text = json.dumps(artifact, ensure_ascii=False, indent=2)
    markdown = build_big_chance_markdown(artifact.get("candidate") if isinstance(artifact.get("candidate"), dict) else {})
    for path, content in ((json_path, json_text), (md_path, markdown), (latest_json_path, json_text), (latest_md_path, markdown)):
        path.write_text(content, encoding="utf-8")
    return json_path, md_path, latest_json_path, latest_md_path
