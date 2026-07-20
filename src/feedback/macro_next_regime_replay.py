"""Deterministic, offline-only M3 macro next-regime shadow replay."""
from __future__ import annotations

import csv
import copy
import hashlib
import json
import math
import os
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any

from src.analysis.big_chance import evaluate_big_chance

SCHEMA_VERSION = "macro_next_regime_replay.v1"
METHOD_VERSION = "macro_next_regime_replay.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
EVENT_FIELDS = ("schema_version", "method_version", "record_id", "signal_id", "event_id", "event_timestamp_utc", "event_timestamp_jst", "current_tactical_side", "current_structural_thesis", "weakening_thesis", "next_regime_side", "status", "activation_families", "reason_codes", "invalidation_reason_codes", "first_reliable_target", "intervening_obstruction", "price_location", "volatility_state", "expansion_risk", "level_reliability_band", "baseline_present", "baseline_side", "baseline_status", "baseline_grade", "comparison_category", "forecast_evidence_json", "outcome_3h", "outcome_6h", "outcome_12h", "outcome_24h", "first_material_move_timestamp", "data_quality_status", "safety_boundary")
EPISODE_FIELDS = ("schema_version", "method_version", "episode_id", "policy", "signal_id", "event_id", "start_timestamp_utc", "side", "status", "evidence_key", "outcome_3h", "outcome_6h", "outcome_12h", "outcome_24h", "first_material_move_timestamp", "data_quality_status")
COMPATIBLE_PREFIXES = ("RELIABLE_LEVEL_REJECTION_", "LEVEL_BREAK_ACCEPTANCE_", "FALSE_BREAK_RECLAIM_", "ORDER_FLOW_PRESSURE_", "OPEN_TRAVEL_CORRIDOR_")


def _dt(value: Any) -> datetime:
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
    except (TypeError, ValueError) as exc:
        raise ValueError("malformed_timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("malformed_timestamp")
    return parsed.astimezone(timezone.utc)


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _side(value: Any) -> str:
    text = str(value or "").strip().upper()
    return {"LONG": "UP", "BUY": "UP", "UP": "UP", "SHORT": "DOWN", "SELL": "DOWN", "DOWN": "DOWN"}.get(text, "NONE")


def _read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError("input_file_missing")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("input_schema_invalid")
        rows = [dict(row) for row in reader]
    return rows


def _unique(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        value = str(row.get(key, "")).strip()
        if not value or value in result:
            raise ValueError("duplicate_or_missing_identifier")
        result[value] = row
    return result


def _families(raw: str) -> tuple[str, ...]:
    return tuple(sorted({part.strip() for part in str(raw or "").split("|") if part.strip()}))


def _matching_family(activation: str, families: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(item for item in families if item.startswith(COMPATIBLE_PREFIXES) and item.endswith("_" + activation))


def baseline_adapter(current: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    """Call the frozen evaluator on copies, keeping upstream signal rows immutable."""
    before_current, before_previous = copy.deepcopy(current), copy.deepcopy(previous)
    result = evaluate_big_chance(copy.deepcopy(current), copy.deepcopy(previous))
    if current != before_current or previous != before_previous:
        raise ValueError("baseline_mutated_input")
    return result if isinstance(result, dict) else {}


def _forecast(signal: dict[str, str], event: dict[str, str], levels: set[str], baseline: dict[str, Any]) -> dict[str, Any]:
    activation = _side(event.get("directional_activation"))
    families = _families(event.get("event_family", ""))
    matching = _matching_family(activation, families) if activation != "NONE" else ()
    target = str(event.get("first_reliable_target", "")).strip()
    obstruction = str(event.get("intervening_obstruction", "")).strip().lower()
    data_ok = str(event.get("data_quality_status", "")).strip().lower() == "ok"
    current = _side(event.get("current_tactical_side") or signal.get("bias"))
    structural = str(event.get("structural_direction") or event.get("structural_state") or "insufficient").upper()
    baseline_present = bool(baseline.get("present"))
    weakening = "baseline_failed_thesis" if baseline_present else "none"
    side, status, reasons = "NONE", "none", []
    if data_ok and activation != "NONE" and matching:
        side = activation
        reasons = list(matching)
        if target and target in levels and obstruction == "none":
            status = "activated"
        else:
            status = "armed"
    elif baseline_present and data_ok:
        status = "watch"
    invalidation: list[str] = []
    if activation == "NONE": invalidation.append("directional_activation_missing")
    if activation != "NONE" and not matching: invalidation.append("directional_family_conflict")
    if not data_ok: invalidation.append("data_quality_unavailable")
    if status == "activated" and not target: invalidation.append("target_missing")
    baseline_side = _side(baseline.get("side"))
    category = "neither"
    if side != "NONE" and baseline_present: category = "agreement" if side == baseline_side else "disagreement"
    elif side != "NONE": category = "candidate_only"
    elif baseline_present: category = "baseline_only"
    return {"current_tactical_side": current, "current_structural_thesis": structural, "weakening_thesis": weakening, "next_regime_side": side, "status": status, "activation_families": "|".join(matching), "reason_codes": "|".join(reasons), "invalidation_reason_codes": "|".join(sorted(set(invalidation))), "first_reliable_target": target, "intervening_obstruction": obstruction or "insufficient", "baseline_present": baseline_present, "baseline_side": baseline_side, "baseline_status": str(baseline.get("status", "none")), "baseline_grade": str(baseline.get("grade", "none")), "comparison_category": category, "forecast_evidence": {"activation": activation, "compatible_families": list(matching), "target_is_reliable": bool(target and target in levels), "obstruction": obstruction, "baseline_reason_codes": list(baseline.get("reason_codes", []))}}


def _episode_rows(records: list[dict[str, Any]], policy: str) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    previous_fired = False; previous_key = ""; previous_at: datetime | None = None
    for record in records:
        forecast = record["forecast"]
        if policy == "candidate":
            fired = forecast["status"] in {"armed", "activated"}; side = forecast["next_regime_side"]; status = forecast["status"]; evidence = forecast["activation_families"]
        else:
            fired = forecast["baseline_present"]; side = forecast["baseline_side"]; status = forecast["baseline_status"]; evidence = forecast["baseline_grade"]
        at = _dt(record["event"]["event_timestamp_utc"]); key = f"{side}|{status}|{evidence}"
        fresh = fired and (not previous_fired or key != previous_key or previous_at is None or at - previous_at >= timedelta(hours=3))
        if fresh:
            event = record["event"]
            eid = hashlib.sha256(f"{METHOD_VERSION}|{policy}|{event['signal_id']}|{at.isoformat()}|{key}".encode()).hexdigest()[:20]
            chosen.append({"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "episode_id": eid, "policy": policy, "signal_id": event["signal_id"], "event_id": event["event_id"], "start_timestamp_utc": at.isoformat(), "side": side, "status": status, "evidence_key": evidence, "outcome_3h": event.get("outcome_3h", ""), "outcome_6h": event.get("outcome_6h", ""), "outcome_12h": event.get("outcome_12h", ""), "outcome_24h": event.get("outcome_24h", ""), "first_material_move_timestamp": event.get("first_material_move_timestamp", ""), "data_quality_status": event.get("data_quality_status", "")})
        previous_fired, previous_key, previous_at = fired, key, at
    return chosen


def _metrics(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = [row for row in episodes if row["outcome_3h"] and row["outcome_3h"] != "unresolved"]
    directional = [row for row in resolved if row["side"] in {"UP", "DOWN"}]
    correct = [row for row in directional if (row["side"] == "UP" and row["outcome_3h"] == "large_up") or (row["side"] == "DOWN" and row["outcome_3h"] == "large_down")]
    opposite = [row for row in directional if (row["side"] == "UP" and row["outcome_3h"] == "large_down") or (row["side"] == "DOWN" and row["outcome_3h"] == "large_up")]
    dates = {(_dt(row["start_timestamp_utc"]) + timedelta(hours=9)).date().isoformat() for row in episodes}
    leads = []
    for row in resolved:
        if row["first_material_move_timestamp"]:
            leads.append((_dt(row["first_material_move_timestamp"]) - _dt(row["start_timestamp_utc"])).total_seconds() / 60)
    ratio = lambda n, d: round(n / d, 8) if d else None
    return {"fired_episodes": len(episodes), "resolved_episodes": len(resolved), "directional_precision": ratio(len(correct), len(directional)), "opposite_move_rate": ratio(len(opposite), len(directional)), "balanced_no_expansion_rate": ratio(sum(row["outcome_3h"] == "balanced_no_expansion" for row in resolved), len(resolved)), "whipsaw_rate": ratio(sum(row["outcome_3h"] == "whipsaw_both" for row in resolved), len(resolved)), "unresolved_rate": ratio(len(episodes) - len(resolved), len(episodes)), "median_lead_minutes": round(median(leads), 8) if leads else None, "burden_per_jst_day": ratio(len(episodes), len(dates)), "event_based_coverage": "not_independent_large_move_recall", "up_episodes": sum(row["side"] == "UP" for row in episodes), "down_episodes": sum(row["side"] == "DOWN" for row in episodes)}


def _gate(candidate: dict[str, Any], baseline: dict[str, Any], episodes: list[dict[str, Any]], source_ok: bool) -> dict[str, Any]:
    dates = sorted({(_dt(row["start_timestamp_utc"]) + timedelta(hours=9)).date().isoformat() for row in episodes if row["policy"] == "candidate"})
    validation = dates[math.floor(len(dates) * .6):] if len(dates) >= 5 else []
    validation_rows = [row for row in episodes if row["policy"] == "candidate" and (_dt(row["start_timestamp_utc"]) + timedelta(hours=9)).date().isoformat() in validation]
    counts = _metrics(validation_rows); reasons = []
    if not validation: reasons.append("validation_not_established")
    if counts["up_episodes"] < 10: reasons.append("validation_up_resolved_lt_10")
    if counts["down_episodes"] < 10: reasons.append("validation_down_resolved_lt_10")
    if candidate.get("directional_precision") is None or baseline.get("directional_precision") is None or candidate["directional_precision"] <= baseline["directional_precision"]: reasons.append("candidate_precision_not_above_baseline")
    if candidate.get("opposite_move_rate") is None or baseline.get("opposite_move_rate") is None or candidate["opposite_move_rate"] > baseline["opposite_move_rate"]: reasons.append("candidate_opposite_move_degraded")
    if candidate.get("balanced_no_expansion_rate") is None or baseline.get("balanced_no_expansion_rate") is None or candidate["balanced_no_expansion_rate"] > baseline["balanced_no_expansion_rate"]: reasons.append("candidate_balanced_warning_degraded")
    if not source_ok: reasons.append("source_coverage_or_continuity_failed")
    if validation_rows and max(Counter((_dt(row["start_timestamp_utc"]) + timedelta(hours=9)).date().isoformat() for row in validation_rows).values()) / len(validation_rows) > .5: reasons.append("single_jst_date_concentration")
    return {"status": "eligible_for_m4_render_shadow" if not reasons else "continue_shadow_collection", "reason_codes": sorted(set(reasons)), "validation_dates": validation, "validation_candidate_metrics": counts}


def _csv(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> bytes:
    from io import StringIO
    output = StringIO(); writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows({key: row.get(key, "") for key in fields} for row in rows); return output.getvalue().encode()


def _atomic(outputs: dict[Path, bytes], replace_output: bool) -> None:
    existing = [path for path in outputs if path.exists()]
    if existing and not replace_output: raise ValueError("output_exists_use_replace")
    parents = {path.parent for path in outputs}
    for parent in parents: parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="macro-next-regime-", dir=str(next(iter(parents)))))
    backup = stage / "backup"; backup.mkdir()
    promoted: list[Path] = []
    try:
        staged = {}
        for path, payload in outputs.items():
            temp = stage / path.name; temp.write_bytes(payload); staged[path] = temp
        for path in outputs:
            if path.exists(): os.replace(path, backup / path.name)
        for path, temp in staged.items(): os.replace(temp, path); promoted.append(path)
    except Exception:
        for path in promoted:
            if path.exists(): path.unlink()
        for path in outputs:
            old = backup / path.name
            if old.exists(): os.replace(old, path)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def replay_macro_next_regime(*, signals: Path, macro_events: Path, macro_levels: Path, macro_replay_json: Path, output_events_csv: Path, output_episodes_csv: Path, output_json: Path, output_md: Path, replace_output: bool = False) -> dict[str, Any]:
    signal_rows = _read_csv(signals, {"signal_id", "timestamp_utc", "current_price", "macro_context_only"})
    event_rows = _read_csv(macro_events, {"schema_version", "method_version", "event_id", "signal_id", "event_timestamp_utc", "directional_activation", "event_family", "first_reliable_target", "intervening_obstruction", "data_quality_status"})
    levels = _read_csv(macro_levels, {"schema_version", "method_version", "level_id", "reliability_band"})
    if not macro_replay_json.is_file(): raise ValueError("input_file_missing")
    try: summary = json.loads(macro_replay_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ValueError("input_schema_invalid") from exc
    if summary.get("schema_version") != "macro_structure_volatility_replay.v1" or summary.get("method_version") != "macro_structure_volatility_replay.v1": raise ValueError("incompatible_macro_replay_version")
    signal_map, event_map, level_map = _unique(signal_rows, "signal_id"), _unique(event_rows, "signal_id"), _unique(levels, "level_id")
    performance = {key: row for key, row in signal_map.items() if not _truthy(row.get("macro_context_only"))}
    if set(event_map) != set(performance): raise ValueError("signal_event_mismatch")
    records: list[dict[str, Any]] = []; previous: dict[str, str] | None = None
    for signal_id, signal in sorted(performance.items(), key=lambda item: (_dt(item[1]["timestamp_utc"]), item[0])):
        event = event_map[signal_id]
        if _dt(signal["timestamp_utc"]) != _dt(event["event_timestamp_utc"]): raise ValueError("signal_event_timestamp_mismatch")
        baseline = baseline_adapter(signal, previous); forecast = _forecast(signal, event, set(level_map), baseline)
        record_id = hashlib.sha256(f"{METHOD_VERSION}|{signal_id}|{event['event_id']}".encode()).hexdigest()[:20]
        record = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "record_id": record_id, "signal_id": signal_id, "event_id": event["event_id"], "event_timestamp_utc": event["event_timestamp_utc"], "event_timestamp_jst": event.get("event_timestamp_jst", ""), **forecast, "price_location": event.get("price_location", ""), "volatility_state": event.get("volatility_state", ""), "expansion_risk": event.get("expansion_risk", ""), "level_reliability_band": event.get("level_reliability_band", ""), "forecast_evidence_json": json.dumps(forecast.pop("forecast_evidence"), sort_keys=True, separators=(",", ":")), "outcome_3h": event.get("outcome_3h", ""), "outcome_6h": event.get("outcome_6h", ""), "outcome_12h": event.get("outcome_12h", ""), "outcome_24h": event.get("outcome_24h", ""), "first_material_move_timestamp": event.get("first_material_move_timestamp", ""), "data_quality_status": event.get("data_quality_status", ""), "safety_boundary": SAFETY}
        records.append({"event": event, "forecast": record}); previous = signal
    event_output = [record["forecast"] for record in records]
    episodes = sorted(_episode_rows(records, "baseline") + _episode_rows(records, "candidate"), key=lambda row: (row["start_timestamp_utc"], row["policy"], row["episode_id"]))
    candidate_metrics, baseline_metrics = _metrics([row for row in episodes if row["policy"] == "candidate"]), _metrics([row for row in episodes if row["policy"] == "baseline"])
    gate = _gate(candidate_metrics, baseline_metrics, episodes, bool(summary.get("coverage", {}).get("continuity_pass", False)))
    output = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "safety_boundary": SAFETY, "counts": {"events": len(event_output), "candidate_episodes": candidate_metrics["fired_episodes"], "baseline_episodes": baseline_metrics["fired_episodes"]}, "metrics": {"candidate": candidate_metrics, "baseline": baseline_metrics}, "recommendation": gate, "input_versions": {"macro_schema_version": summary.get("schema_version"), "macro_method_version": summary.get("method_version")}, "context_only_excluded": len(signal_rows) - len(performance)}
    markdown = "# Macro Next-Regime Offline Shadow\n\n## Result\n\n- recommendation: %s\n- events: %d\n- candidate episodes: %d\n- baseline episodes: %d\n\n## Safety Boundary\n\n- %s\n" % (gate["status"], len(event_output), candidate_metrics["fired_episodes"], baseline_metrics["fired_episodes"], SAFETY)
    _atomic({output_events_csv: _csv(event_output, EVENT_FIELDS), output_episodes_csv: _csv(episodes, EPISODE_FIELDS), output_json: (json.dumps(output, sort_keys=True, indent=2) + "\n").encode(), output_md: markdown.encode()}, replace_output)
    return {"ok": True, "exit_code": 0, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "counts": output["counts"], "recommendation": gate["status"]}
