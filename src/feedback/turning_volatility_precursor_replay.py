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
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    return {part.strip() for part in text.replace("|", ",").split(",") if part.strip()}


def _has(row: dict[str, str], *values: str) -> bool:
    tokens = _tokens(row.get("market_map_flags")) | _tokens(row.get("warning_flags")) | _tokens(row.get("risk_flags")) | _tokens(row.get("notify_reason_codes")) | _tokens(row.get("suppress_reason_codes"))
    tokens |= _tokens(row.get("active_level_role")) | _tokens(row.get("level_flip_state")) | _tokens(row.get("failed_breakout_state")) | _tokens(row.get("trend_flip_state"))
    return any(value in tokens or value in str(row.get("primary_setup_reason", "")) for value in values)


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


def _classify(row: dict[str, str]) -> dict[str, dict[str, Any]]:
    bias = _bias(row)
    down_location = bias in {"long", "both"} and _has(row, "long_into_major_resistance")
    up_location = bias in {"short", "both"} and _has(row, "short_into_major_support")
    down_rejection = _has(row, "major_resistance_rejection", "failed_breakout_down_reversal")
    up_rejection = _has(row, "major_support_rejection", "failed_breakout_up_reversal")
    flip_down = _has(row, "resistance_to_support_flip", "resistance_to_support_retest_confirmed")
    flip_up = _has(row, "support_to_resistance_flip", "support_to_resistance_retest_confirmed")
    down_groups = sum((down_location, down_rejection, _has(row, "early_down", "confirmed_down", "down_reversal"), _stress(row, "DOWN")))
    up_groups = sum((up_location, up_rejection, _has(row, "early_up", "confirmed_up", "up_reversal"), _stress(row, "UP")))
    level = "BOTH" if down_location and down_rejection and up_location and up_rejection else "DOWN" if down_location and down_rejection else "UP" if up_location and up_rejection else None
    failed = "DOWN" if bias == "long" and flip_down and down_rejection and _stress(row, "DOWN") else "UP" if bias == "short" and flip_up and up_rejection and _stress(row, "UP") else None
    stress = "DOWN" if bias == "long" and down_groups >= 2 else "UP" if bias == "short" and up_groups >= 2 else None
    current = None
    if _truth(row.get("was_notified")):
        current = "DOWN" if bias == "long" else "UP" if bias == "short" else None
    combined_sides = [side for side in ("DOWN", "UP") if side in {level, failed, stress}]
    combined = "BOTH" if "BOTH" in {level, failed, stress} or len(set(combined_sides)) > 1 else combined_sides[0] if combined_sides else None
    return {
        "POLICY_CURRENT_NOTIFICATION": {"side": current, "reasons": ["dominant_long_under_stress" if current == "DOWN" else "dominant_short_under_stress"] if current else []},
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
        if len(window) < bars:
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
    lines = ["# Turning / Volatility Precursor Replay", "", "## Executive result", str(summary.get("recommendation_status")), "", "## Current baseline versus policies", json.dumps(metrics, ensure_ascii=False, sort_keys=True), "", "## Long / Short split", json.dumps(summary.get("side_metrics", {}), ensure_ascii=False, sort_keys=True), "", "## Regime / phase split", json.dumps(summary.get("regime_phase_metrics", {}), ensure_ascii=False, sort_keys=True), "", "## Pinned 07:05 case", json.dumps(summary.get("pinned_case", {}), ensure_ascii=False, sort_keys=True), "", "## Data limitations", "Proxy OHLCV only; unresolved and whipsaw rows are excluded from clean directional precision.", "", "## Recommendation status", str(summary.get("recommendation_status")), "", "## Safety boundary", SAFETY, "No production scoring, market-map, gate, notification, mail, runtime, API, account, or order behavior changed.", ""]
    return "\n".join(lines)


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
        normalized: list[dict[str, Any]] = []
        for row in rows:
            timestamp = _dt(row.get("timestamp_utc"))
            if timestamp is None or (cutoff and timestamp > cutoff):
                continue
            policies = _classify(row)
            for policy, result in policies.items():
                side = result.get("side")
                if side not in {"UP", "DOWN", "BOTH"}:
                    continue
                normalized.append({"row": row, "policy": policy, "side": side, "reasons": result.get("reasons", [])})
        normalized.sort(key=lambda item: (_dt(item["row"].get("timestamp_utc")) or datetime.min.replace(tzinfo=timezone.utc), item["policy"], item["row"].get("signal_id", "")))
        candles = []
        for item in frame.to_dict(orient="records"):
            timestamp = _dt(item.get("timestamp_utc") or item.get("timestamp_jst"))
            if timestamp is None: continue
            candles.append({"timestamp": timestamp, "high": _number(item.get("high")) or 0, "low": _number(item.get("low")) or 0})
        episodes: list[dict[str, Any]] = []
        last: dict[tuple[str, str], dict[str, Any]] = {}
        for item in normalized:
            row = item["row"]; key = (item["policy"], item["side"])
            timestamp = _dt(row.get("timestamp_utc")); previous = last.get(key)
            if previous and timestamp and (timestamp - previous["timestamp"]).total_seconds() < 3 * 3600:
                previous["source_signal_count"] += 1; continue
            episode = {"row": row, "policy": item["policy"], "side": item["side"], "reasons": item["reasons"], "timestamp": timestamp, "source_signal_count": 1}
            episodes.append(episode); last[key] = episode
        output_rows: list[dict[str, Any]] = []
        for index, episode in enumerate(episodes, 1):
            row = episode["row"]; event = {**row, "precursor_side": episode["side"]}; outcome = _outcome(event, candles); label = outcome.get("outcome_4h", "unresolved")
            output_rows.append({"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "episode_id": f"TVP-{index:05d}", "policy": episode["policy"], "precursor_side": episode["side"], "first_signal_id": row.get("signal_id", ""), "first_timestamp_utc": row.get("timestamp_utc", ""), "first_timestamp_jst": row.get("timestamp_jst", ""), "current_bias": row.get("bias", ""), "current_was_notified": row.get("was_notified", ""), "event_price": row.get("current_price", ""), "event_atr_15m": row.get("atr_15m_value", ""), "phase": row.get("phase", ""), "regime": row.get("market_regime", ""), "reason_codes": ",".join(sorted(episode["reasons"])), "source_signal_count": episode["source_signal_count"], **outcome, "comparison_status": _comparison(episode["side"], label), "data_quality_status": "resolved" if label not in {"unresolved"} else "unresolved"})
        metrics: dict[str, Any] = {}
        for policy in POLICIES:
            subset = [row for row in output_rows if row["policy"] == policy]
            resolved = [row for row in subset if row["comparison_status"] != "unresolved"]
            clean = [row for row in resolved if row["comparison_status"] == "caught_before_move"]
            metrics[policy] = {"precursor_episodes": len(subset), "resolved_episodes": len(resolved), "matching_large_moves": len(clean), "clean_directional_precision": round(len(clean) / len(resolved), 6) if resolved else None, "false_precursor_rate": round(sum(row["comparison_status"] == "false_precursor" for row in resolved) / len(resolved), 6) if resolved else None, "opposite_move_rate": round(sum(row["comparison_status"] == "opposite_move" for row in resolved) / len(resolved), 6) if resolved else None, "whipsaw_rate": round(sum(row["comparison_status"] == "whipsaw" for row in resolved) / len(resolved), 6) if resolved else None, "unresolved_rate": round((len(subset) - len(resolved)) / len(subset), 6) if subset else None, "median_lead_minutes": median([float(row["lead_minutes_to_material_move"]) for row in clean if row.get("lead_minutes_to_material_move") not in (None, "")]) if clean else None}
        side_metrics = {side: {"episodes": sum(row["precursor_side"] == side for row in output_rows), "resolved": sum(row["precursor_side"] == side and row["comparison_status"] != "unresolved" for row in output_rows)} for side in ("UP", "DOWN", "BOTH")}
        resolved_event_rows = [row for row in output_rows if row.get("comparison_status") != "unresolved"]
        validation_status = "established" if len(resolved_event_rows) >= 20 and len({str(row.get("first_timestamp_jst", ""))[:10] for row in resolved_event_rows}) >= 2 else "not_established"
        pinned = next((row for row in output_rows if row.get("first_signal_id") == "20260711_220501"), None)
        recommendation = "eligible_for_notification_proposal" if validation_status == "established" and any((metric.get("resolved_episodes", 0) >= 10 and (metric.get("false_precursor_rate") or 1) <= .6 and (metric.get("opposite_move_rate") or 1) <= .25) for metric in metrics.values()) else "continue_shadow_collection"
        summary = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "input_fingerprints": {"signals": _sha256(signals), "ohlcv": _sha256(ohlcv_path)}, "evaluation_cutoff": cutoff.isoformat() if cutoff else ohlcv_meta.get("max_timestamp"), "method_parameters": {"horizons_bars": {"1h": 4, "2h": 8, "4h": 16}, "material_move_multiplier_atr": 2.0, "material_move_percent": .005}, "signal_rows": len(rows), "episode_rows": len(output_rows), "metrics": metrics, "side_metrics": side_metrics, "regime_phase_metrics": {"regime": dict(Counter(row.get("regime", "") for row in output_rows)), "phase": dict(Counter(row.get("phase", "") for row in output_rows))}, "unresolved_counts": dict(Counter(row.get("outcome_4h", "") for row in output_rows)), "pinned_case": {"status": "caught_before_move" if pinned and pinned.get("comparison_status") == "caught_before_move" else "failed" if pinned else "unavailable", "signal_id": "20260711_220501"}, "validation_status": validation_status, "actual_backed_count": 0 if actual_episodes is None else 0, "recommendation_status": recommendation, "no_automatic_tuning": True, "safety_boundary": SAFETY}
        _atomic_outputs(output_rows, summary, output_csv, output_json, output_md, replace_output)
        return {"ok": True, "exit_code": 0, "report_written": True, "signal_rows": len(rows), "episode_rows": len(output_rows), "metrics": metrics, "side_metrics": side_metrics, "validation_status": validation_status, "pinned_case": summary["pinned_case"], "recommendation_status": recommendation, "safety_boundary": SAFETY}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "exit_code": 2, "error_codes": [str(exc) or "input_invalid"], "report_written": False}
    finally:
        if fetch_public_ohlcv:
            try: ohlcv_path.unlink(missing_ok=True)
            except OSError: pass
