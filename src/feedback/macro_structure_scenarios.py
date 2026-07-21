"""Deterministic, report-only M-HYP1 structural scenario hypotheses."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

METHOD_VERSION = "macro_structure_scenarios.v1"
SCHEMA_VERSION = METHOD_VERSION
BAR_INTERVAL = timedelta(hours=4)
INTERACTION_WINDOW = timedelta(hours=48)
PIVOT_WINDOW = timedelta(hours=96)
MAX_SCENARIOS = 3

FAMILY_PRIORITY = {
    "break_resolution_watch": 0,
    "accepted_break_continuation": 1,
    "failed_break_reversal": 2,
    "boundary_reaction_watch": 3,
    "pivot_structure_continuation": 4,
}
STATE_PRIORITY = {
    "retest_hold": 5,
    "retest_failure": 5,
    "false_break_reclaim": 5,
    "retest": 4,
    "closed_candle_acceptance": 4,
    "break": 3,
    "clean_rejection": 2,
    "touch": 1,
    "approach": 0,
}
EVENT_SEQUENCE_TYPES = {"break", "closed_candle_acceptance", "retest", "retest_hold", "retest_failure", "false_break_reclaim"}
INTERACTION_TYPES = {"approach", "touch", "clean_rejection"}
FORBIDDEN_WORDS = ("probability", "確率", "win rate", "勝率", "confidence percentage", "buy", "sell", "long", "short", "entry", "stop loss", "sl", "take profit", "tp", "order permission")


def _utc(value: Any, code: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(code) from exc
    else:
        raise ValueError(code)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _payload(value: dict[str, Any]) -> str:
    return json.dumps({key: item for key, item in value.items() if key not in {"scenario_id", "event_id"}}, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _event_sort_key(event: dict[str, Any]) -> tuple[datetime, int, str]:
    return (_utc(event["event_timestamp_utc"], "scenario_event_timestamp_invalid"), STATE_PRIORITY.get(event["event_type"], 99), str(event["event_id"]))


def _scenario_id(scenario_type: str, direction: str, object_kind: str, object_id: str, timestamp: str, supporting_ids: list[str]) -> str:
    raw = f"{METHOD_VERSION}|{scenario_type}|{direction}|{object_kind}|{object_id}|{timestamp}|{','.join(sorted(supporting_ids))}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _direction(value: Any) -> str:
    if value not in {"UP", "DOWN"}:
        raise ValueError("scenario_direction_invalid")
    return str(value)


def _validate_events(event_model: dict[str, Any], cutoff: datetime) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(event_model, dict) or event_model.get("method_version") != "macro_structure_structural_events.v1":
        raise ValueError("scenario_event_model_invalid")
    events = event_model.get("events")
    if not isinstance(events, list):
        raise ValueError("scenario_event_model_invalid")
    by_id: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict) or not event.get("event_id") or not event.get("event_type"):
            raise ValueError("scenario_event_invalid")
        event_id = str(event["event_id"])
        _direction(event.get("direction"))
        timestamp = _utc(event.get("event_timestamp_utc"), "scenario_event_timestamp_invalid")
        if timestamp > cutoff:
            raise ValueError("scenario_future_event")
        if event_id in by_id and _payload(by_id[event_id]) != _payload(event):
            raise ValueError("scenario_event_id_collision")
        by_id[event_id] = event
    for event in events:
        cursor = event
        seen: set[str] = set()
        while cursor.get("parent_event_id"):
            event_id = str(cursor["event_id"])
            if event_id in seen:
                raise ValueError("scenario_parent_cycle")
            seen.add(event_id)
            parent = str(cursor["parent_event_id"])
            if parent not in by_id:
                raise ValueError("scenario_parent_missing")
            cursor = by_id[parent]
    return events, by_id


def _object_ids(zones: list[dict[str, Any]], trendline_model: dict[str, Any]) -> set[tuple[str, str]]:
    if not isinstance(zones, list) or not isinstance(trendline_model, dict):
        raise ValueError("scenario_object_model_invalid")
    objects: set[tuple[str, str]] = set()
    for zone in zones:
        if not isinstance(zone, dict) or not zone.get("level_id"):
            raise ValueError("scenario_zone_reference_invalid")
        objects.add(("horizontal_zone", str(zone["level_id"])))
    lines = trendline_model.get("lines")
    displayed = trendline_model.get("displayed_line_ids")
    if not isinstance(lines, list) or not isinstance(displayed, list):
        raise ValueError("scenario_line_model_invalid")
    by_id = {str(line.get("line_id")): line for line in lines if isinstance(line, dict) and line.get("line_id")}
    for line_id in displayed:
        line = by_id.get(str(line_id))
        if line is None or line.get("state") in {"invalidated", "insufficient"}:
            raise ValueError("scenario_line_reference_invalid")
        objects.add(("trendline", str(line_id)))
    return objects


def _root_break(event: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    cursor = event
    seen: set[str] = set()
    while cursor.get("parent_event_id"):
        event_id = str(cursor["event_id"])
        if event_id in seen:
            raise ValueError("scenario_parent_cycle")
        seen.add(event_id)
        parent_id = str(cursor["parent_event_id"])
        if parent_id not in by_id:
            raise ValueError("scenario_parent_missing")
        cursor = by_id[parent_id]
    if cursor.get("event_type") != "break":
        raise ValueError("scenario_root_break_missing")
    _direction(cursor.get("direction"))
    return cursor


def _text(code: str, scenario_type: str, direction: str, object_kind: str, object_id: str) -> str:
    return f"{scenario_type} {direction} {object_kind} {object_id}: {code}."


def _candidate(scenario_type: str, status: str, direction: str, event: dict[str, Any], object_kind: str, object_id: str, related: list[str], supporting: list[str], condition: str, next_confirmation: str, invalidation: str) -> dict[str, Any]:
    timestamp = str(event["event_timestamp_utc"])
    values = {
        "scenario_type": scenario_type, "scenario_status": status, "direction": direction,
        "trigger_timestamp_utc": timestamp, "primary_object_kind": object_kind, "primary_object_id": object_id,
        "related_object_ids": sorted(set(related)), "supporting_event_ids": sorted(set(supporting)),
        "condition_code": condition, "condition_text": _text(condition, scenario_type, direction, object_kind, object_id),
        "next_confirmation_code": next_confirmation, "next_confirmation_text": _text(next_confirmation, scenario_type, direction, object_kind, object_id),
        "invalidation_code": invalidation, "invalidation_text": _text(invalidation, scenario_type, direction, object_kind, object_id),
        "reason_codes": [],
    }
    values["scenario_id"] = _scenario_id(scenario_type, direction, object_kind, object_id, timestamp, values["supporting_event_ids"])
    return values


def _latest_by_object(events: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for event in events:
        kind = str(event.get("object_kind", ""))
        object_id = str(event.get("object_id", ""))
        if kind in {"horizontal_zone", "trendline"}:
            grouped.setdefault((kind, object_id), []).append(event)
    for values in grouped.values():
        values.sort(key=_event_sort_key)
    return grouped


def _within(event: dict[str, Any], cutoff: datetime, window: timedelta) -> bool:
    timestamp = _utc(event["event_timestamp_utc"], "scenario_event_timestamp_invalid")
    return cutoff - window <= timestamp <= cutoff


def _build_candidates(cutoff: datetime, objects: set[tuple[str, str]], events: list[dict[str, Any]], by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = _latest_by_object(events)
    candidates: list[dict[str, Any]] = []
    for object_key, values in grouped.items():
        object_kind, object_id = object_key
        sequence = [event for event in values if event.get("event_type") in EVENT_SEQUENCE_TYPES and _within(event, cutoff, INTERACTION_WINDOW)]
        interactions = [event for event in values if event.get("event_type") in INTERACTION_TYPES and _within(event, cutoff, INTERACTION_WINDOW)]
        latest_sequence = sequence[-1] if sequence else None
        latest_interaction = interactions[-1] if interactions else None
        if latest_sequence is not None:
            event_type = latest_sequence["event_type"]
            if event_type == "break" and latest_sequence.get("sequence_status") == "pending":
                root = _root_break(latest_sequence, by_id)
                candidates.append(_candidate("break_resolution_watch", "watch", root["direction"], latest_sequence, object_kind, object_id, [], [root["event_id"]], "maintain_break_side_close", "closed_candle_acceptance", "false_break_reclaim_or_original_side_return"))
            elif event_type in {"closed_candle_acceptance", "retest", "retest_hold"}:
                root = _root_break(latest_sequence, by_id)
                candidates.append(_candidate("accepted_break_continuation", "active", root["direction"], latest_sequence, object_kind, object_id, [], [root["event_id"], latest_sequence["event_id"]], "maintain_accepted_side_close", "retest_hold_or_same_direction_pivot", "retest_failure_reclaim_or_opposite_acceptance"))
            elif event_type in {"false_break_reclaim", "retest_failure"}:
                candidates.append(_candidate("failed_break_reversal", "active", latest_sequence["direction"], latest_sequence, object_kind, object_id, [], [latest_sequence["event_id"]], "maintain_reclaimed_side_close", "clean_rejection_or_same_direction_pivot", "new_acceptance_in_original_break_direction"))
        if latest_interaction is not None and (latest_sequence is None or _event_sort_key(latest_interaction) > _event_sort_key(latest_sequence)):
            scenario_status = "active" if latest_interaction["event_type"] == "clean_rejection" else "watch"
            candidates.append(_candidate("boundary_reaction_watch", scenario_status, latest_interaction["direction"], latest_interaction, object_kind, object_id, [], [latest_interaction["event_id"]], "object_holds_expected_side", "clean_rejection_or_same_direction_pivot", "wrong_side_break_or_acceptance"))

    pivots = [event for event in events if event.get("object_kind") == "pivot_structure" and event.get("event_type") in {"higher_high", "higher_low", "lower_high", "lower_low"} and _within(event, cutoff, PIVOT_WINDOW)]
    for direction, first_type, second_type in (("UP", "higher_high", "higher_low"), ("DOWN", "lower_high", "lower_low")):
        first = [event for event in pivots if event["event_type"] == first_type]
        second = [event for event in pivots if event["event_type"] == second_type]
        if first and second:
            pair = sorted([first[-1], second[-1]], key=_event_sort_key)
            trigger = pair[-1]
            candidates.append(_candidate("pivot_structure_continuation", "active", direction, trigger, "pivot_structure", str(trigger["object_id"]), [str(pair[0]["object_id"])], [str(pair[0]["event_id"]), str(pair[1]["event_id"])], "preserve_confirmed_pivot_sequence", "next_same_direction_pivot", "opposite_confirmed_pivot_pair"))
    for candidate in candidates:
        if (candidate["primary_object_kind"], candidate["primary_object_id"]) not in objects and candidate["primary_object_kind"] != "pivot_structure":
            raise ValueError("scenario_primary_object_missing")
    return candidates


def _select(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, str]:
    dedup: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for candidate in candidates:
        key = (candidate["scenario_type"], candidate["primary_object_kind"], candidate["primary_object_id"], candidate["direction"])
        prior = dedup.get(key)
        if prior is None or _candidate_sort_key(candidate) < _candidate_sort_key(prior):
            dedup[key] = candidate
    ranked = sorted(dedup.values(), key=_candidate_sort_key)
    if not ranked:
        return [], 0, ""
    dominant = ranked[0]["direction"]
    selected: list[dict[str, Any]] = []
    selected_types: set[str] = set()
    selected_support: set[str] = set()
    suppressed_opposite = 0
    for candidate in ranked:
        if candidate["direction"] != dominant:
            suppressed_opposite += 1
            continue
        if candidate["scenario_type"] in selected_types or selected_support.intersection(candidate["supporting_event_ids"]):
            continue
        if len(selected) >= MAX_SCENARIOS:
            continue
        selected.append(candidate)
        selected_types.add(candidate["scenario_type"])
        selected_support.update(candidate["supporting_event_ids"])
    return selected, suppressed_opposite, dominant


def _candidate_sort_key(candidate: dict[str, Any]) -> tuple[int, float, int, str, str, str]:
    return (FAMILY_PRIORITY[candidate["scenario_type"]], -_utc(candidate["trigger_timestamp_utc"], "scenario_timestamp_invalid").timestamp(), 0 if candidate["scenario_status"] == "active" else 1, candidate["primary_object_kind"], candidate["primary_object_id"], candidate["scenario_id"])


def build_scenario_model(*, cutoff: datetime, current_price: float, structure_state: str, price_location: str, zones: list[dict[str, Any]], trendline_model: dict[str, Any], structural_event_model: dict[str, Any]) -> dict[str, Any]:
    cutoff = _utc(cutoff, "scenario_cutoff_invalid")
    try:
        if not isinstance(current_price, (int, float)) or current_price != current_price:
            raise ValueError("scenario_current_price_invalid")
    except TypeError as exc:
        raise ValueError("scenario_current_price_invalid") from exc
    if not isinstance(structure_state, str) or not isinstance(price_location, str):
        raise ValueError("scenario_context_invalid")
    events, by_id = _validate_events(structural_event_model, cutoff)
    objects = _object_ids(zones, trendline_model)
    for event in events:
        kind = str(event.get("object_kind", ""))
        if kind in {"horizontal_zone", "trendline"} and (kind, str(event.get("object_id", ""))) not in objects:
            raise ValueError("scenario_event_object_missing")
        if kind not in {"horizontal_zone", "trendline", "pivot_structure"}:
            raise ValueError("scenario_event_object_kind_invalid")
    candidates = _build_candidates(cutoff, objects, events, by_id)
    seen: dict[str, str] = {}
    for candidate in candidates:
        payload = _payload(candidate)
        prior = seen.get(candidate["scenario_id"])
        if prior is not None and prior != payload:
            raise ValueError("scenario_id_collision")
        if any(word in payload.lower() for word in FORBIDDEN_WORDS):
            raise ValueError("scenario_forbidden_word")
        seen[candidate["scenario_id"]] = payload
    selected, suppressed, dominant = _select(candidates)
    status = "ok" if selected else "insufficient"
    return {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "cutoff_utc": cutoff.isoformat(), "status": status, "dominant_direction": dominant, "scenarios": selected, "suppressed_candidate_count": suppressed, "reason_codes": [] if selected else ["insufficient_current_structural_evidence"]}
