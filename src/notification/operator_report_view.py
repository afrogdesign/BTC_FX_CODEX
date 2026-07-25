"""Pure display conversion for the human-facing operator report."""

from __future__ import annotations

from typing import Any


ACTION_LABELS = {
    "A_FORMAL": "正式条件に近い",
    "B_CHECK_15M": "15分足の確認待ち",
    "C_WATCH_ZONE": "価格帯を監視",
    "STOP_OR_EXIT": "新規見送り・保護確認",
    "NONE": "新規見送り・保護確認",
}
STATE_LABELS = {
    "follow_through": "継続確認",
    "triggered": "条件成立",
    "late": "追いかけ禁止",
    "armed": "条件待ち",
    "watch": "監視中",
    "invalidated": "無効化",
    "wait": "様子見",
    "dormant": "判定材料不足",
}
SIGNAL_LABELS = {
    "long": "Long方向",
    "short": "Short方向",
    "up": "上方向",
    "down": "下方向",
    "wait": "中立・様子見",
    "neutral": "中立・様子見",
}
ALIGNMENT_LABELS = {
    "aligned": "時間軸は同方向",
    "countertrend": "15分足が中期と逆方向",
    "turning_candidate": "転換候補を監視",
    "neutral": "方向感は中立",
    "conflict": "時間軸が競合",
    "conflicts": "時間軸が競合",
    "insufficient_evidence": "証拠不足",
    "malformed": "データ不備のため判定保留",
    "missing": "証拠不足のため判定保留",
}


def _token(value: Any) -> str:
    return str(value or "").strip().lower()


def _signal(value: Any) -> str:
    return SIGNAL_LABELS.get(_token(value), "判定材料不足")


def _valid_signal(value: Any) -> bool:
    return _token(value) in {"long", "short", "up", "down", "wait", "neutral"}


def _direction(value: Any) -> str | None:
    normalized = _token(value)
    if normalized in {"long", "up"}:
        return "Long"
    if normalized in {"short", "down"}:
        return "Short"
    return None


def _join_timeframes(items: list[tuple[str, str]]) -> str:
    grouped: list[str] = []
    index = 0
    while index < len(items):
        direction = items[index][1]
        names = [items[index][0]]
        index += 1
        while index < len(items) and items[index][1] == direction:
            names.append(items[index][0])
            index += 1
        grouped.append(f"・".join(names) + f"は{direction}")
    return "、".join(grouped)


def _timeframe_summary(signals: dict[str, Any], alignment: str, blocked: bool = False) -> str:
    names = ("4H", "1H", "15M")
    directions = [_direction(signals.get(name)) for name in names]
    known = [(name, value) for name, value in zip(names, directions) if value is not None]
    state = _token(alignment)

    if state == "turning_candidate" and known:
        if len(known) == 3 and len({value for _, value in known}) == 1:
            direction_text = f"4H・1H・15Mが{known[0][1]}で一致"
        else:
            direction_text = _join_timeframes(known)
        return f"{direction_text} — 反対方向への転換候補"

    conflict_state = blocked or state in {"conflict", "conflicts", "direction_conflict", "blocked"}
    if conflict_state and len(known) >= 2:
        return f"{_join_timeframes(known)} — 4H・1H・15Mの方向が競合しているため新規見送り"

    if len(known) == 3:
        values = [value for _, value in known]
        if len(set(values)) == 1:
            return f"4H・1H・15Mが{values[0]}で一致"
        if values[0] == values[1] and values[2] != values[0]:
            return f"4H・1Hは{values[0]}、15Mは{values[2]}のため短期は逆行"
        return f"{_join_timeframes(known)} — 4H・1H・15Mの方向が競合しているため新規見送り"

    if not known:
        return "4H・1H・15Mの判定材料が不足"

    missing = [(name, "判定材料不足") for name in names if _direction(signals.get(name)) is None]
    return "、".join([_join_timeframes(known), "・".join(name for name, _ in missing) + "は判定材料不足"])


def _action(value: Any) -> str:
    return ACTION_LABELS.get(str(value or "").strip().upper(), "新規見送り・保護確認")


def _state(value: Any) -> str:
    return STATE_LABELS.get(_token(value), "判定材料不足")


def _zone(setup: Any) -> tuple[Any, Any]:
    setup = setup if isinstance(setup, dict) else {}
    layer = setup.get("value_defense_entry_layer")
    layer = layer if isinstance(layer, dict) else {}
    zone = layer.get("shallow_retest_zone") or setup.get("entry_zone")
    zone = zone if isinstance(zone, dict) else {}
    return zone.get("low"), zone.get("high")


def build_operator_report_view(result: dict[str, Any]) -> dict[str, Any]:
    """Return only human-facing labels and values; producer semantics are untouched."""
    action = result.get("side_aware_mtf_action")
    action = action if isinstance(action, dict) else {}
    execution = action.get("execution_context") if isinstance(action.get("execution_context"), dict) else {}
    structural = action.get("structural_context") if isinstance(action.get("structural_context"), dict) else {}
    tactical = action.get("tactical_context") if isinstance(action.get("tactical_context"), dict) else {}
    decision = result.get("operator_decision") if isinstance(result.get("operator_decision"), dict) else {}
    structural_priority = result.get("structural_priority")
    structural_priority = structural_priority if isinstance(structural_priority, dict) else {}
    primary = _token(decision.get("primary_side") or execution.get("primary_side"))
    primary = primary if primary in {"long", "short"} else ""
    raw_15m = result.get("signals_15m")
    signals = {
        "4H": result.get("signals_4h") or structural.get("signals_4h"),
        "1H": result.get("signals_1h") or tactical.get("signals_1h"),
        "15M": raw_15m if _valid_signal(raw_15m) else None,
    }
    normalized = [_token(value) for value in signals.values()]
    alignment = _token(
        structural_priority.get("alignment_state")
        or structural.get("alignment_state")
        or decision.get("alignment_state")
        or result.get("alignment_state")
    )
    if not alignment:
        known = [value for value in normalized if value in {"long", "short"}]
        if len(known) < 2:
            alignment = "insufficient_evidence"
        elif len(set(known)) == 1:
            alignment = "aligned"
        elif normalized[0] in {"long", "short"} and normalized[-1] in {"long", "short"}:
            alignment = "countertrend"
        else:
            alignment = "conflicts"
    blocked = bool(decision.get("new_entry_blocked")) or _token(decision.get("state")) in {"blocked", "direction_conflict"}
    alignment_summary = _timeframe_summary(signals, alignment, blocked=blocked)
    rows = []
    for side in ("long", "short"):
        raw = action.get(side) if isinstance(action.get(side), dict) else {}
        setup = result.get(f"{side}_setup") if isinstance(result.get(f"{side}_setup"), dict) else {}
        low, high = _zone(setup)
        higher = signals["4H"] or signals["1H"]
        rows.append(
            {
                "side": side,
                "label": "Long" if side == "long" else "Short",
                "priority": side == primary,
                "stage": _action(raw.get("action_class")),
                "state": _state(raw.get("state")),
                "next_condition": raw.get("next_condition") or "価格反応と15分足の確認を待ちます。",
                "entry_low": low,
                "entry_high": high,
                "invalidation": setup.get("stop_loss"),
                "no_chase": _token(raw.get("chase_status") or execution.get("chase_status")) in {"late_no_chase", "tp1_reached_no_chase"}
                or _token(raw.get("state")) == "late",
                "higher": f"4H {_signal(signals['4H'])} / 1H {_signal(signals['1H'])}",
                "raw": {"action_class": raw.get("action_class"), "state": raw.get("state"), "chase_status": raw.get("chase_status")},
            }
        )
    candidate = result.get("big_chance_candidate")
    candidate = candidate if isinstance(candidate, dict) and candidate.get("present") else None
    candidate_side = _token(candidate.get("side") or candidate.get("direction")) if candidate else ""
    auxiliary_note = ""
    if candidate and candidate_side and primary and candidate_side != primary:
        auxiliary_note = "現在の優先方向とは反対側の補助候補です。現在の判断を上書きしません。"
    elif candidate:
        auxiliary_note = "補助監視です。現在の判断を上書きしません。"
    return {
        "primary_side": primary,
        "signals": {key: {"raw": value, "label": _signal(value)} for key, value in signals.items()},
        "alignment": ALIGNMENT_LABELS.get(alignment, "判定材料不足"),
        "alignment_summary": alignment_summary,
        "alignment_raw": alignment,
        "rows": rows,
        "new_entry_blocked": blocked,
        "candidate": candidate,
        "auxiliary_note": auxiliary_note,
        "structural": {
            "present": bool(structural_priority.get("present")),
            "long_points": structural_priority.get("long_points"),
            "short_points": structural_priority.get("short_points"),
            "long_share": structural_priority.get("long_share"),
            "short_share": structural_priority.get("short_share"),
        },
        "next_condition": next(
            (row["next_condition"] for row in rows if row["priority"] and row.get("next_condition")),
            "",
        ),
        "diagnostic": {"alignment": alignment, "primary_side": primary, "signals": signals},
    }
