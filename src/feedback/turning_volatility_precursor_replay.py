"""Offline, report-only replay for turning and volatility precursor hypotheses."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

from src.feedback.manual_operator_operating_cycle import _fetch_ohlcv, _read_csv, _validate_ohlcv

METHOD_VERSION = "turning_volatility_precursor_replay.v1"
SCHEMA_VERSION = "turning_volatility_precursor_replay.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
POLICIES = (
    "POLICY_CURRENT_NOTIFICATION",
    "POLICY_LEVEL_REJECTION",
    "POLICY_FAILED_FLIP_GUARD",
    "POLICY_THESIS_STRESS",
    "POLICY_COMBINED_PRECURSOR",
)
EVENT_FIELDS = (
    "schema_version", "method_version", "episode_id", "policy", "precursor_side",
    "first_signal_id", "first_timestamp_utc", "first_timestamp_jst", "current_bias",
    "current_was_notified", "event_price", "event_atr_15m", "phase", "regime",
    "reason_codes", "source_signal_count", "outcome_1h", "outcome_2h", "outcome_4h",
    "matching_move_distance", "opposing_move_distance", "matching_move_atr",
    "opposing_move_atr", "first_match_timestamp", "lead_minutes_to_material_move",
    "comparison_status", "data_quality_status",
)
STRUCTURED_LIST_FIELDS = ("market_map_flags", "warning_flags", "risk_flags", "notify_reason_codes", "suppress_reason_codes", "active_level_role", "level_flip_state", "failed_breakout_state", "trend_flip_state")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace("Z", "+00:00")
    if not text:
        return None
    try:
        result = datetime.fromisoformat(text)
    except ValueError:
        return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def _number(value: Any) -> float | None:
    try:
        result = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _truth(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _tokens(value: Any) -> set[str]:
    if value in (None, ""):
        return set()
    text = str(value).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return {str(item).strip() for item in parsed if str(item).strip()}
        if isinstance(parsed, dict):
            return {str(key).strip() for key, item in parsed.items() if item and str(key).strip()}
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        if text.startswith(("[", "{")):
            raise ValueError("malformed_structured_list") from exc
    return {part.strip() for part in text.replace("|", ",").split(",") if part.strip()}


def _has(row: dict[str, str], *values: str) -> bool:
    tokens = _tokens(row.get("market_map_flags")) | _tokens(row.get("warning_flags")) | _tokens(row.get("risk_flags")) | _tokens(row.get("notify_reason_codes")) | _tokens(row.get("suppress_reason_codes"))
    tokens |= _tokens(row.get("active_level_role")) | _tokens(row.get("level_flip_state")) | _tokens(row.get("failed_breakout_state")) | _tokens(row.get("trend_flip_state"))
    return any(value in tokens or value in str(row.get("primary_setup_reason", "")) for value in values)


def _validate_structured_fields(row: dict[str, str]) -> None:
    for field in STRUCTURED_LIST_FIELDS:
        text = str(row.get(field) or "").strip()
        if text.startswith(("[", "{")):
            try:
                parsed = json.loads(text)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError("malformed_structured_list") from exc
            if not isinstance(parsed, (list, dict)):
                raise ValueError("malformed_structured_list")


def _phase(row: dict[str, str]) -> str:
    return str(row.get("phase") or "unknown").strip().lower()


def _bias(row: dict[str, str]) -> str:
    return str(row.get("bias") or "").strip().lower()


def _stress(row: dict[str, str], side: str) -> bool:
    phase = _phase(row)
    location = _number(row.get("location_risk")) or 0
    wait = _number(row.get("confidence_wait_shadow")) or 0
    divergence = str(row.get("cvd_price_divergence") or "").lower()
    orderbook = str(row.get("orderbook_bias") or "").lower()
    setup_invalid = str(row.get("primary_setup_status") or "").lower() == "invalid"
    if side == "DOWN":
        return phase == "reversal_risk" or location >= 70 or wait >= 70 or divergence == "bearish" or orderbook == "ask_heavy" or setup_invalid
    return phase == "reversal_risk" or location >= 70 or wait >= 70 or divergence == "bullish" or orderbook == "bid_heavy" or setup_invalid


def _evidence_groups(row: dict[str, str], side: str) -> dict[str, bool]:
    down = side == "DOWN"
    location = _has(row, "long_into_major_resistance") if down else _has(row, "short_into_major_support")
    rejection = _has(row, "major_resistance_rejection", "failed_breakout_down_reversal") if down else _has(row, "major_support_rejection", "failed_breakout_up_reversal")
    transition = _phase(row) == "reversal_risk"
    transition = transition or (_has(row, "early_down", "confirmed_down", "down_reversal") if down else _has(row, "early_up", "confirmed_up", "up_reversal"))
    transition = transition or str(row.get("market_map_primary_state") or "").lower() in (("early_down", "confirmed_down", "down_reversal") if down else ("early_up", "confirmed_up", "up_reversal"))
    divergence = str(row.get("cvd_price_divergence") or "").lower()
    orderbook = str(row.get("orderbook_bias") or "").lower()
    cvd_slope = _number(row.get("cvd_slope"))
    oi_change = _number(row.get("oi_change_pct"))
    micro = (divergence == ("bearish" if down else "bullish")) or orderbook == ("ask_heavy" if down else "bid_heavy")
    if down:
        micro = micro or (oi_change is not None and cvd_slope is not None and oi_change < 0 and cvd_slope < 0)
    else:
        micro = micro or (oi_change is not None and cvd_slope is not None and oi_change > 0 and cvd_slope > 0)
    fragility = str(row.get("primary_setup_status") or "").lower() == "invalid" or (_number(row.get("confidence_wait_shadow")) or 0) >= 70 or (_number(row.get("location_risk")) or 0) >= 70
    return {"location": location, "rejection": rejection, "transition": transition, "microstructure": micro, "fragility": fragility}


def _classify(row: dict[str, str]) -> dict[str, dict[str, Any]]:
    bias = _bias(row)
    down_location = bias in {"long", "both"} and _has(row, "long_into_major_resistance")
    up_location = bias in {"short", "both"} and _has(row, "short_into_major_support")
    down_rejection = _has(row, "major_resistance_rejection", "failed_breakout_down_reversal")
    up_rejection = _has(row, "major_support_rejection", "failed_breakout_up_reversal")
    flip_down = _has(row, "resistance_to_support_flip", "resistance_to_support_retest_confirmed")
    flip_up = _has(row, "support_to_resistance_flip", "support_to_resistance_retest_confirmed")
    down_groups = _evidence_groups(row, "DOWN")
    up_groups = _evidence_groups(row, "UP")
    level = "BOTH" if down_location and down_rejection and up_location and up_rejection else "DOWN" if down_location and down_rejection else "UP" if up_location and up_rejection else None
    failed_down = bias in {"long", "both"} and flip_down and down_rejection and _stress(row, "DOWN")
    failed_up = bias in {"short", "both"} and flip_up and up_rejection and _stress(row, "UP")
    failed = "BOTH" if failed_down and failed_up else "DOWN" if failed_down else "UP" if failed_up else None
    stress_down = bias in {"long", "both"} and sum(down_groups.values()) >= 2 and any(down_groups[name] for name in ("transition", "microstructure", "fragility"))
    stress_up = bias in {"short", "both"} and sum(up_groups.values()) >= 2 and any(up_groups[name] for name in ("transition", "microstructure", "fragility"))
    stress = "BOTH" if stress_down and stress_up else "DOWN" if stress_down else "UP" if stress_up else None
    current = None
    if _truth(row.get("was_notified")):
        current = "UP" if bias == "long" else "DOWN" if bias == "short" else None
    families = {"DOWN": {name for name, value in (("level", level), ("failed", failed), ("stress", stress)) if value == "DOWN"}, "UP": {name for name, value in (("level", level), ("failed", failed), ("stress", stress)) if value == "UP"}}
    if level == "BOTH":
        families["DOWN"].add("level"); families["UP"].add("level")
    if failed == "BOTH":
        families["DOWN"].add("failed"); families["UP"].add("failed")
    if stress == "BOTH":
        families["DOWN"].add("stress"); families["UP"].add("stress")
    if failed == "DOWN" and down_rejection and _phase(row) == "reversal_risk": families["DOWN"].add("failed_exception")
    if failed == "UP" and up_rejection and _phase(row) == "reversal_risk": families["UP"].add("failed_exception")
    combined_sides = [side for side in ("DOWN", "UP") if len(families[side]) >= 2]
    combined = "BOTH" if len(combined_sides) == 2 else combined_sides[0] if combined_sides else None
    return {
        "POLICY_CURRENT_NOTIFICATION": {"side": current, "reasons": ["dominant_long_under_stress" if current == "UP" else "dominant_short_under_stress"] if current else []},
        "POLICY_LEVEL_REJECTION": {"side": level, "reasons": _reasons(row, level, "level")},
        "POLICY_FAILED_FLIP_GUARD": {"side": failed, "reasons": _reasons(row, failed, "failed")},
        "POLICY_THESIS_STRESS": {"side": stress, "reasons": _reasons(row, stress, "stress")},
        "POLICY_COMBINED_PRECURSOR": {"side": combined, "reasons": sorted(set(sum((_reasons(row, side, "combined") for side in ("DOWN", "UP") if side in combined_sides), [])))},
    }


def _reasons(row: dict[str, str], side: str | None, kind: str) -> list[str]:
    if not side:
        return []
    result: list[str] = []
    if side == "DOWN":
        result += ["dominant_long_under_stress", "at_major_resistance"] if _has(row, "long_into_major_resistance") else []
        result += ["major_resistance_rejection"] if _has(row, "major_resistance_rejection") else []
        result += ["failed_breakout_down_reversal"] if _has(row, "failed_breakout_down_reversal") else []
        result += ["bullish_flip_conflicted"] if _has(row, "resistance_to_support_flip", "resistance_to_support_retest_confirmed") else []
        result += ["reversal_risk_phase"] if _phase(row) == "reversal_risk" else []
        result += ["high_location_risk"] if (_number(row.get("location_risk")) or 0) >= 70 else []
        result += ["high_wait_pressure"] if (_number(row.get("confidence_wait_shadow")) or 0) >= 70 else []
        result += ["bearish_microstructure_pressure"] if str(row.get("cvd_price_divergence") or "").lower() == "bearish" or str(row.get("orderbook_bias") or "").lower() == "ask_heavy" else []
    else:
        result += ["dominant_short_under_stress", "at_major_support"] if _has(row, "short_into_major_support") else []
        result += ["major_support_rejection"] if _has(row, "major_support_rejection") else []
        result += ["failed_breakout_up_reversal"] if _has(row, "failed_breakout_up_reversal") else []
        result += ["bearish_flip_conflicted"] if _has(row, "support_to_resistance_flip", "support_to_resistance_retest_confirmed") else []
        result += ["reversal_risk_phase"] if _phase(row) == "reversal_risk" else []
        result += ["high_location_risk"] if (_number(row.get("location_risk")) or 0) >= 70 else []
        result += ["high_wait_pressure"] if (_number(row.get("confidence_wait_shadow")) or 0) >= 70 else []
        result += ["bullish_microstructure_pressure"] if str(row.get("cvd_price_divergence") or "").lower() == "bullish" or str(row.get("orderbook_bias") or "").lower() == "bid_heavy" else []
    if str(row.get("primary_setup_status") or "").lower() == "invalid":
        result.append("primary_setup_invalid")
    return sorted(set(result))


def classify_precursor_row(row: dict[str, str]) -> dict[str, dict[str, Any]]:
    """Pure event-time classification entry point for tests and callers."""
    return _classify(dict(row))


def _outcome(event: dict[str, Any], candles: list[dict[str, Any]]) -> dict[str, Any]:
    event_time = _dt(event.get("timestamp_utc"))
    price = _number(event.get("current_price"))
    atr = _number(event.get("atr_15m_value")) or 0
    if event_time is None or price is None:
        return {"outcome_1h": "unresolved", "outcome_2h": "unresolved", "outcome_4h": "unresolved"}
    threshold = max(2 * atr, price * 0.005)
    future = [c for c in candles if c["timestamp"] > event_time]
    # A distant first candle means the event has no contiguous OHLCV coverage.
    if not future or (future[0]["timestamp"] - event_time).total_seconds() > 30 * 60:
        return {"outcome_1h": "unresolved", "outcome_2h": "unresolved", "outcome_4h": "unresolved"}
    result: dict[str, Any] = {"matching_move_distance": "", "opposing_move_distance": "", "matching_move_atr": "", "opposing_move_atr": "", "first_match_timestamp": "", "lead_minutes_to_material_move": ""}
    side = event.get("precursor_side")
    for hours, bars in ((1, 4), (2, 8), (4, 16)):
        window = future[:bars]
        if len(window) < bars or any((right["timestamp"] - left["timestamp"]).total_seconds() > 20 * 60 for left, right in zip(window, window[1:])):
            result[f"outcome_{hours}h"] = "unresolved"
            continue
        up = [c["high"] - price for c in window]
        down = [price - c["low"] for c in window]
        up_hit = next((c for c, distance in zip(window, up) if distance >= threshold), None)
        down_hit = next((c for c, distance in zip(window, down) if distance >= threshold), None)
        if up_hit and down_hit:
            label = "whipsaw_both"
        elif up_hit or down_hit:
            first = up_hit if up_hit and (not down_hit or up_hit["timestamp"] <= down_hit["timestamp"]) else down_hit
            label = "large_up" if first is up_hit else "large_down"
        else:
            label = "no_large_move"
        result[f"outcome_{hours}h"] = label
        if hours == 4:
            matching = max(up) if side == "UP" else max(down) if side == "DOWN" else max(max(up), max(down))
            opposing = max(down) if side == "UP" else max(up) if side == "DOWN" else 0
            result.update(matching_move_distance=round(matching, 6), opposing_move_distance=round(opposing, 6), matching_move_atr=round(matching / atr, 6) if atr else "", opposing_move_atr=round(opposing / atr, 6) if atr else "")
            target = up_hit if side == "UP" else down_hit if side == "DOWN" else None
            if target:
                result["first_match_timestamp"] = target["timestamp"].isoformat()
                result["lead_minutes_to_material_move"] = round((target["timestamp"] - event_time).total_seconds() / 60, 3)
    return result


def _comparison(side: str | None, outcome: str) -> str:
    if outcome == "unresolved":
        return "unresolved"
    if outcome == "whipsaw_both":
        return "whipsaw"
    if not side:
        return "false_precursor"
    if (side == "DOWN" and outcome == "large_down") or (side == "UP" and outcome == "large_up"):
        return "caught_before_move"
    if outcome in {"large_up", "large_down"}:
        return "opposite_move"
    return "false_precursor"


def _atomic_outputs(rows: list[dict[str, Any]], summary: dict[str, Any], output_csv: Path, output_json: Path, output_md: Path, replace: bool) -> None:
    targets = (output_csv, output_json, output_md)
    if any(path.exists() for path in targets) and not replace:
        raise ValueError("existing_output_requires_replace")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".turning-replay-", dir=str(output_csv.parent)))
    try:
        csv_path = temp / output_csv.name
        with csv_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(EVENT_FIELDS), lineterminator="\n")
            writer.writeheader(); writer.writerows({key: row.get(key, "") for key in EVENT_FIELDS} for row in rows)
        json_path = temp / output_json.name
        json_path.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        md_path = temp / output_md.name
        md_path.write_text(_markdown(summary), encoding="utf-8")
        backups: list[tuple[Path, Path]] = []
        moved: list[Path] = []
        try:
            for target, source in zip(targets, (csv_path, json_path, md_path)):
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    backup = target.with_name("." + target.name + ".turning-backup")
                    backup.unlink(missing_ok=True); target.replace(backup); backups.append((target, backup))
                source.replace(target); moved.append(target)
        except Exception as exc:
            for target in moved: target.unlink(missing_ok=True)
            for target, backup in backups:
                if backup.exists(): backup.replace(target)
            raise OSError("output_transaction_failed") from exc
        finally:
            for _, backup in backups: backup.unlink(missing_ok=True)
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def _markdown(summary: dict[str, Any]) -> str:
    metrics = summary.get("metrics", {})
    lines = ["# Turning / Volatility Precursor Replay", "", "## Executive result", str(summary.get("recommendation_status")), "", "## Current baseline versus each policy", json.dumps(metrics, ensure_ascii=False, sort_keys=True), "", "## Long / Short split", json.dumps(summary.get("side_metrics", {}), ensure_ascii=False, sort_keys=True), "", "## Regime / phase split", json.dumps(summary.get("regime_phase_metrics", {}), ensure_ascii=False, sort_keys=True), "", "## Lead-time distribution", json.dumps({key: value.get("median_lead_minutes") for key, value in metrics.items() if isinstance(value, dict)}, ensure_ascii=False, sort_keys=True), "", "## False-warning and whipsaw burden", json.dumps({key: {metric: value.get(metric) for metric in ("false_precursor_rate", "opposite_move_rate", "whipsaw_rate")} for key, value in metrics.items() if isinstance(value, dict)}, ensure_ascii=False, sort_keys=True), "", "## Pinned 07:05 case", json.dumps(summary.get("pinned_case", {}), ensure_ascii=False, sort_keys=True), "", "## Top missed large moves", "Reported as diagnostics only; no production proposal is applied.", "", "## Top false precursors", "Reported as diagnostics only; no production proposal is applied.", "", "## Data limitations", "Proxy OHLCV only; unresolved, BOTH, and whipsaw rows are excluded from clean directional precision. Actual evidence is separate.", "", "## Recommendation status", str(summary.get("recommendation_status")), "", "## Safety boundary", SAFETY, "No production scoring, market-map, gate, notification, mail, runtime, API, account, or order behavior changed.", ""]
    return "\n".join(lines)


def _realized_opportunities(rows: list[dict[str, str]], candles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    opportunities: list[dict[str, Any]] = []
    active: dict[str, Any] | None = None
    ordered = sorted((row for row in rows if _dt(row.get("timestamp_utc"))), key=lambda row: _dt(row["timestamp_utc"]))
    for row in ordered:
        timestamp = _dt(row["timestamp_utc"])
        down = _outcome({**row, "precursor_side": "DOWN"}, candles)
        up = _outcome({**row, "precursor_side": "UP"}, candles)
        down_label, up_label = down.get("outcome_4h"), up.get("outcome_4h")
        side = "DOWN" if down_label == "large_down" and up_label not in {"large_up", "whipsaw_both"} else "UP" if up_label == "large_up" and down_label not in {"large_down", "whipsaw_both"} else None
        if side is None:
            active = None
            continue
        if active is None or active["side"] != side or (timestamp - active["start"]).total_seconds() >= 3 * 3600:
            first = down if side == "DOWN" else up
            active = {"side": side, "start": timestamp, "end": timestamp, "threshold": _dt(first.get("first_match_timestamp")), "signal_ids": [row.get("signal_id", "")]}
            opportunities.append(active)
        else:
            active["end"] = timestamp; active["signal_ids"].append(row.get("signal_id", ""))
    for opportunity in opportunities:
        identity = f"{METHOD_VERSION}|opportunity|{opportunity['side']}|{opportunity['signal_ids'][0]}|{opportunity['start'].isoformat()}"
        opportunity["opportunity_id"] = "OPP-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return opportunities


def _metric(rows: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("comparison_status") != "unresolved"]
    clean = [row for row in resolved if row.get("comparison_status") == "caught_before_move"]
    leads = [float(row["lead_minutes_to_material_move"]) for row in clean if row.get("lead_minutes_to_material_move") not in (None, "")]
    matching_atr = [float(row["matching_move_atr"]) for row in clean if row.get("matching_move_atr") not in (None, "")]
    adverse_atr = [float(row["opposing_move_atr"]) for row in clean if row.get("opposing_move_atr") not in (None, "")]
    denominator = len(opportunities)
    captured = sum(1 for opportunity in opportunities if any(row.get("precursor_side") == opportunity["side"] and _dt(row.get("first_timestamp_utc")) and _dt(row.get("first_timestamp_utc")) <= (opportunity.get("threshold") or datetime.min.replace(tzinfo=timezone.utc)) and (opportunity["start"] <= _dt(row.get("first_timestamp_utc")) <= opportunity["end"]) for row in rows))
    return {"precursor_episodes": len(rows), "resolved_episodes": len(resolved), "matching_large_moves": len(clean), "clean_directional_precision": round(len(clean) / len(resolved), 6) if resolved else None, "independent_realized_opportunities": denominator, "independent_large_move_captures": captured, "large_move_recall": round(captured / denominator, 6) if denominator else None, "false_precursor_rate": round(sum(row.get("comparison_status") == "false_precursor" for row in resolved) / len(resolved), 6) if resolved else None, "opposite_move_rate": round(sum(row.get("comparison_status") == "opposite_move" for row in resolved) / len(resolved), 6) if resolved else None, "whipsaw_rate": round(sum(row.get("comparison_status") == "whipsaw" for row in resolved) / len(resolved), 6) if resolved else None, "unresolved_rate": round((len(rows) - len(resolved)) / len(rows), 6) if rows else None, "episodes_per_jst_day": round(len(rows) / max(1, len({str(row.get("first_timestamp_jst", ""))[:10] for row in rows})), 6) if rows else 0, "median_lead_minutes": median(leads) if leads else None, "q1_lead_minutes": sorted(leads)[len(leads) // 4] if leads else None, "q3_lead_minutes": sorted(leads)[(len(leads) * 3) // 4] if leads else None, "median_matching_excursion_atr": median(matching_atr) if matching_atr else None, "median_adverse_excursion_atr": median(adverse_atr) if adverse_atr else None, "duplicate_compression_ratio": round(sum(int(row.get("source_signal_count") or 1) for row in rows) / len(rows), 6) if rows else None, "UP": sum(row.get("precursor_side") == "UP" for row in rows), "DOWN": sum(row.get("precursor_side") == "DOWN" for row in rows), "BOTH": sum(row.get("precursor_side") == "BOTH" for row in rows)}


def _actual_summary(episodes: Path | None, links: Path | None) -> dict[str, Any]:
    if episodes is None:
        return {"status": "absent", "actual_backed_count": 0, "unique_trade_episodes": 0}
    episode_rows, episode_headers, error = _read_csv(episodes)
    link_rows, link_headers, link_error = _read_csv(links)  # type: ignore[arg-type]
    if error or link_error:
        raise ValueError("actual_pair_invalid")
    episode_key = next((key for key in ("episode_id", "trade_episode_id", "actual_episode_id") if key in episode_headers), None)
    link_key = next((key for key in ("episode_id", "trade_episode_id", "actual_episode_id") if key in link_headers), None)
    confidence_key = next((key for key in ("link_confidence", "confidence", "actual_link_confidence") if key in link_headers), None)
    if not episode_key or not link_key or not confidence_key:
        raise ValueError("actual_pair_schema_mismatch")
    episode_ids = {row.get(episode_key, "") for row in episode_rows if row.get(episode_key, "")}
    eligible = {row.get(link_key, "") for row in link_rows if row.get(link_key, "") in episode_ids and str(row.get(confidence_key, "")).lower() in {"high", "medium", "manual_confirmed", "manual-confirmed"}}
    return {"status": "paired", "actual_backed_count": len(eligible), "unique_trade_episodes": len(episode_ids), "eligible_linked_episodes": len(eligible)}


def replay_turning_volatility_precursors(*, signals: Path, ohlcv: Path | None, output_csv: Path, output_json: Path, output_md: Path, fetch_public_ohlcv: bool = False, ohlcv_limit: int = 500, actual_episodes: Path | None = None, actual_links: Path | None = None, cutoff_utc: str | None = None, replace_output: bool = False) -> dict[str, Any]:
    if (actual_episodes is None) != (actual_links is None):
        return {"ok": False, "exit_code": 2, "error_codes": ["actual_pair_incomplete"], "report_written": False}
    if actual_episodes is not None and (not actual_episodes.exists() or not actual_links.exists()):
        return {"ok": False, "exit_code": 2, "error_codes": ["actual_pair_missing"], "report_written": False}
    if fetch_public_ohlcv:
        temp_ohlcv = Path(tempfile.mkstemp(prefix="turning-ohlcv-", suffix=".csv")[1])
        try:
            _fetch_ohlcv(temp_ohlcv, int(ohlcv_limit)); ohlcv_path = temp_ohlcv
        except Exception:
            temp_ohlcv.unlink(missing_ok=True)
            return {"ok": False, "exit_code": 2, "error_codes": ["public_ohlcv_fetch_failed"], "report_written": False}
    else:
        if ohlcv is None:
            return {"ok": False, "exit_code": 2, "error_codes": ["ohlcv_required"], "report_written": False}
        ohlcv_path = ohlcv
    try:
        rows, headers, error = _read_csv(signals)
        required = {"signal_id", "timestamp_utc", "timestamp_jst", "bias", "current_price"}
        if error or not required.issubset(headers):
            return {"ok": False, "exit_code": 2, "error_codes": [error or "signals_schema_mismatch"], "report_written": False}
        frame, ohlcv_meta, error = _validate_ohlcv(ohlcv_path)
        if error or frame is None:
            return {"ok": False, "exit_code": 2, "error_codes": [error or "ohlcv_invalid"], "report_written": False}
        cutoff = _dt(cutoff_utc) if cutoff_utc else None
        ordered_rows = sorted((row for row in rows if _dt(row.get("timestamp_utc")) and (not cutoff or _dt(row.get("timestamp_utc")) <= cutoff)), key=lambda row: (_dt(row.get("timestamp_utc")) or datetime.min.replace(tzinfo=timezone.utc), row.get("signal_id", "")))
        for row in ordered_rows:
            _validate_structured_fields(row)
        normalized: list[dict[str, Any]] = []
        # Walk every snapshot so absence ends an episode and later re-entry starts one.
        for policy in POLICIES:
            active: dict[str, Any] | None = None
            for row in ordered_rows:
                result = _classify(row)[policy]
                side = result.get("side")
                timestamp = _dt(row.get("timestamp_utc"))
                if side not in {"UP", "DOWN", "BOTH"}:
                    active = None
                    continue
                if active is None or active["side"] != side or (timestamp and (timestamp - active["timestamp"]).total_seconds() >= 3 * 3600):
                    active = {"row": row, "policy": policy, "side": side, "reasons": result.get("reasons", []), "timestamp": timestamp, "source_signal_count": 1}
                    normalized.append(active)
                else:
                    active["source_signal_count"] += 1
        normalized.sort(key=lambda item: (_dt(item["row"].get("timestamp_utc")) or datetime.min.replace(tzinfo=timezone.utc), item["policy"], item["row"].get("signal_id", "")))
        candles = []
        for item in frame.to_dict(orient="records"):
            timestamp = _dt(item.get("timestamp_utc") or item.get("timestamp_jst"))
            if timestamp is None: continue
            candles.append({"timestamp": timestamp, "high": _number(item.get("high")) or 0, "low": _number(item.get("low")) or 0})
        episodes = normalized
        output_rows: list[dict[str, Any]] = []
        for episode in episodes:
            row = episode["row"]; event = {**row, "precursor_side": episode["side"]}; outcome = _outcome(event, candles); label = outcome.get("outcome_4h", "unresolved")
            identity = f"{METHOD_VERSION}|{episode['policy']}|{episode['side']}|{row.get('signal_id','')}|{row.get('timestamp_utc','')}"
            episode_id = "TVP-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
            output_rows.append({"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "episode_id": episode_id, "policy": episode["policy"], "precursor_side": episode["side"], "first_signal_id": row.get("signal_id", ""), "first_timestamp_utc": row.get("timestamp_utc", ""), "first_timestamp_jst": row.get("timestamp_jst", ""), "current_bias": row.get("bias", ""), "current_was_notified": row.get("was_notified", ""), "event_price": row.get("current_price", ""), "event_atr_15m": row.get("atr_15m_value", ""), "phase": row.get("phase", ""), "regime": row.get("market_regime", ""), "reason_codes": ",".join(sorted(episode["reasons"])), "source_signal_count": episode["source_signal_count"], **outcome, "comparison_status": _comparison(episode["side"], label), "data_quality_status": "resolved" if label not in {"unresolved"} else "unresolved"})
        opportunities = _realized_opportunities(ordered_rows, candles)
        metrics: dict[str, Any] = {}
        for policy in POLICIES:
            subset = [row for row in output_rows if row["policy"] == policy]
            resolved = [row for row in subset if row.get("comparison_status") != "unresolved"]
            split_at = max(1, int(len(resolved) * .8)) if resolved else 0
            calibration = resolved[:split_at]
            validation = resolved[split_at:]
            cal_opps = [opp for opp in opportunities if opp["start"] <= (_dt(calibration[-1].get("first_timestamp_utc")) if calibration else datetime.min.replace(tzinfo=timezone.utc))]
            val_start = _dt(validation[0].get("first_timestamp_utc")) if validation else None
            val_opps = [opp for opp in opportunities if val_start and opp["start"] >= val_start]
            all_metrics = _metric(subset, opportunities)
            metrics[policy] = {**all_metrics, "all": all_metrics, "calibration": _metric(calibration, cal_opps), "validation": _metric(validation, val_opps)}
        side_metrics = {side: {"episodes": sum(row["precursor_side"] == side for row in output_rows), "resolved": sum(row["precursor_side"] == side and row["comparison_status"] != "unresolved" for row in output_rows)} for side in ("UP", "DOWN", "BOTH")}
        combined_validation = metrics["POLICY_COMBINED_PRECURSOR"]["validation"]
        resolved_event_rows = [row for row in output_rows if row.get("comparison_status") != "unresolved"]
        validation_status = "established" if len(resolved_event_rows) >= 20 and len({str(row.get("first_timestamp_jst", ""))[:10] for row in resolved_event_rows}) >= 2 else "not_established"
        pinned = next((row for row in output_rows if row.get("first_signal_id") == "20260711_220501"), None)
        pinned_exclusion = [row for row in output_rows if row.get("first_signal_id") != "20260711_220501"]
        combined_excl = _metric([row for row in pinned_exclusion if row["policy"] == "POLICY_COMBINED_PRECURSOR"], opportunities)
        eligible = validation_status == "established" and combined_validation.get("UP", 0) >= 10 and combined_validation.get("DOWN", 0) >= 10 and (combined_validation.get("false_precursor_rate") or 1) <= .6 and (combined_validation.get("opposite_move_rate") or 1) <= .25 and (combined_validation.get("median_lead_minutes") or 0) > 0 and combined_validation.get("UP", 0) > 0 and combined_validation.get("DOWN", 0) > 0 and combined_excl.get("resolved_episodes", 0) >= 20
        recommendation = "eligible_for_notification_proposal" if eligible else "continue_shadow_collection" if validation_status == "established" else "insufficient_evidence"
        actual = _actual_summary(actual_episodes, actual_links)
        notification_rows = [row for row in rows if _truth(row.get("was_notified"))]
        notification_none = sum(_classify(row)["POLICY_CURRENT_NOTIFICATION"].get("side") is None for row in notification_rows)
        summary = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "input_fingerprints": {"signals": _sha256(signals), "ohlcv": _sha256(ohlcv_path)}, "evaluation_cutoff": cutoff.isoformat() if cutoff else ohlcv_meta.get("max_timestamp"), "method_parameters": {"horizons_bars": {"1h": 4, "2h": 8, "4h": 16}, "material_move_multiplier_atr": 2.0, "material_move_percent": .005, "calibration_fraction": .8}, "signal_rows": len(rows), "realized_move_opportunities": len(opportunities), "episode_rows": len(output_rows), "metrics": metrics, "side_metrics": side_metrics, "regime_phase_metrics": {"regime": dict(Counter(row.get("regime", "") for row in output_rows)), "phase": dict(Counter(row.get("phase", "") for row in output_rows))}, "unresolved_counts": dict(Counter(row.get("outcome_4h", "") for row in output_rows)), "current_notification_burden": {"notified_rows": len(notification_rows), "nondirectional_rows": notification_none}, "pinned_case": {"status": "caught_before_move" if pinned and pinned.get("comparison_status") == "caught_before_move" else "failed" if pinned else "unavailable", "signal_id": "20260711_220501", "exclusion_gate": "pass" if combined_excl.get("resolved_episodes", 0) >= 20 else "fail"}, "validation_status": validation_status, "actual_evidence": actual, "recommendation_status": recommendation, "no_automatic_tuning": True, "safety_boundary": SAFETY}
        _atomic_outputs(output_rows, summary, output_csv, output_json, output_md, replace_output)
        return {"ok": True, "exit_code": 0, "report_written": True, "signal_rows": len(rows), "episode_rows": len(output_rows), "metrics": metrics, "side_metrics": side_metrics, "validation_status": validation_status, "pinned_case": summary["pinned_case"], "recommendation_status": recommendation, "safety_boundary": SAFETY}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "exit_code": 2, "error_codes": [str(exc) or "input_invalid"], "report_written": False}
    finally:
        if fetch_public_ohlcv:
            try: ohlcv_path.unlink(missing_ok=True)
            except OSError: pass
