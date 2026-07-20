"""Deterministic, offline-only M4 operator hierarchy render shadow."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = METHOD_VERSION = "macro_operator_hierarchy_shadow.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
FORBIDDEN = ("outcome_", "mfe_atr", "mae_atr", "upward_excursion", "downward_excursion", "target_touch", "adverse_before_target", "whipsaw", "large_move_side", "first_material_move_timestamp")
BASELINE_ORDER = ["operator action wording", "tactical execution", "chart", "macro structure", "next-regime comparison"]
CHALLENGER_ORDER = ["chart", "macro strip", "next-regime card", "tactical execution map", "operator action detail"]


def _dt(value: Any) -> datetime:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError("malformed_timestamp") from exc
    if result.tzinfo is None:
        raise ValueError("malformed_timestamp")
    return result.astimezone(timezone.utc)


def _csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError("input_file_missing")
    with path.open(encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("input_schema_invalid")
        return [dict(row) for row in reader]


def _unique(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        value = str(row.get(key, "")).strip()
        if not value or value in result:
            raise ValueError("duplicate_or_missing_identifier")
        result[value] = row
    return result


def _fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _level_safe(row: dict[str, str], event_at: datetime) -> bool:
    if _dt(row["last_confirmed_at"]) > event_at:
        return False
    confirmations = [item.strip() for item in row.get("member_confirmation_timestamps", "").split(",") if item.strip()]
    return bool(confirmations) and all(_dt(item) <= event_at for item in confirmations)


def _ohlcv(rows: list[dict[str, str]], interval: str, event_at: datetime) -> list[dict[str, Any]]:
    previous: datetime | None = None; result = []
    hours = 1 if interval == "1h" else 4
    for row in rows:
        if row.get("interval") != interval:
            raise ValueError("ohlcv_interval_invalid")
        at = _dt(row["timestamp_utc"])
        if previous is not None and at <= previous:
            raise ValueError("ohlcv_timestamp_invalid")
        previous = at
        try:
            values = {key: float(row[key]) for key in ("open", "high", "low", "close")}
        except (TypeError, ValueError) as exc:
            raise ValueError("ohlcv_numeric_invalid") from exc
        if at + timedelta(hours=hours) <= event_at:
            result.append({"timestamp_utc": at.isoformat(), **values})
    return result


def _safe_text(value: Any) -> str:
    return str(value or "")


def _svg(candles: list[dict[str, Any]], event_price: float, levels: list[dict[str, Any]], tactical: list[dict[str, Any]], event_at: str) -> str:
    width, height, pad = 960, 420, 42
    prices = [event_price] + [value for candle in candles for value in (candle["high"], candle["low"])]
    for row in levels:
        prices += [row["low"], row["high"]]
    for row in tactical:
        for key in ("entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2"):
            try: prices.append(float(row.get(key, "")))
            except ValueError: pass
    low, high = min(prices), max(prices)
    span = max(high - low, 1.0); low -= span * .08; high += span * .08
    y = lambda value: pad + (high - value) / (high - low) * (height - 2 * pad)
    x = lambda index: pad + (index + .5) * (width - 2 * pad) / max(len(candles), 1)
    body = []
    for index, candle in enumerate(candles):
        cx, yo, yc, yh, yl = x(index), y(candle["open"]), y(candle["close"]), y(candle["high"]), y(candle["low"])
        color = "#1f9d55" if candle["close"] >= candle["open"] else "#c0392b"
        body.append(f'<line x1="{cx:.2f}" y1="{yh:.2f}" x2="{cx:.2f}" y2="{yl:.2f}" stroke="{color}"/><rect x="{cx-2.5:.2f}" y="{min(yo,yc):.2f}" width="5" height="{max(abs(yo-yc),1):.2f}" fill="{color}"/>')
    bands = [f'<rect x="{pad}" y="{y(row["high"]):.2f}" width="{width-2*pad}" height="{max(y(row["low"])-y(row["high"]),1):.2f}" fill="#5b6ee1" opacity=".16"/><text x="{pad+4}" y="{y(row["center"]):.2f}" font-size="10">macro {html.escape(row["label"])}</text>' for row in levels]
    overlays = [f'<line x1="{pad}" y1="{y(event_price):.2f}" x2="{width-pad}" y2="{y(event_price):.2f}" stroke="#111" stroke-dasharray="4 3"/><text x="{width-pad-120}" y="{y(event_price)-4:.2f}" font-size="10">event price</text>']
    for index, row in enumerate(tactical):
        for key, color in (("entry_price", "#0f766e"), ("stop_loss", "#b91c1c"), ("tp1", "#2563eb"), ("tp2", "#7c3aed")):
            try: price = float(row.get(key, ""))
            except ValueError: continue
            yy = y(price); overlays.append(f'<line x1="{pad}" y1="{yy:.2f}" x2="{width-pad}" y2="{yy:.2f}" stroke="{color}" opacity=".55"/><text x="{pad+8}" y="{yy-2:.2f}" fill="{color}" font-size="10">tactical {index+1} {key}</text>')
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="1 hour event-time chart"><rect width="{width}" height="{height}" fill="#fff"/><text x="{pad}" y="20" font-size="14">1H event-time chart — {html.escape(event_at)}</text>{"".join(bands)}{"".join(body)}{"".join(overlays)}</svg>'


def _atomic(outputs: dict[Path, bytes], replace_output: bool) -> None:
    if any(path.exists() for path in outputs) and not replace_output:
        raise ValueError("output_exists_use_replace")
    parent = next(iter(outputs)).parent; parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="macro-hierarchy-", dir=str(parent))); backup = stage / "backup"; backup.mkdir(); promoted: list[Path] = []
    try:
        staged = {path: stage / path.name for path in outputs}
        for path, temp in staged.items(): temp.write_bytes(outputs[path])
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


def render_macro_operator_hierarchy_shadow(*, signal_context_csv: Path, tactical_candidates_csv: Path, macro_events_csv: Path, macro_levels_csv: Path, next_regime_events_csv: Path, ohlcv_1h_csv: Path, signal_id: str, output_html: Path, output_json: Path, output_md: Path, replace_output: bool = False, ohlcv_4h_csv: Path | None = None) -> dict[str, Any]:
    signal_rows = _csv(signal_context_csv, {"signal_id", "timestamp_jst", "current_price", "primary_setup_side", "primary_setup_status"})
    tactical_rows = _csv(tactical_candidates_csv, {"candidate_id", "source_signal_id", "candidate_type", "candidate_status", "side"})
    macro_rows = _csv(macro_events_csv, {"schema_version", "method_version", "event_id", "signal_id", "event_timestamp_utc", "event_price", "nearest_support_id", "nearest_resistance_id", "first_reliable_target", "intervening_obstruction"})
    level_rows = _csv(macro_levels_csv, {"schema_version", "method_version", "level_id", "low", "high", "center", "last_confirmed_at", "member_confirmation_timestamps", "reliability_band", "role", "lifecycle"})
    m3_rows = _csv(next_regime_events_csv, {"schema_version", "method_version", "record_id", "event_id", "signal_id", "event_timestamp_utc", "current_tactical_side", "current_structural_thesis", "weakening_thesis", "next_regime_side", "status", "first_reliable_target", "intervening_obstruction"})
    signals, macros, m3s, levels = _unique(signal_rows, "signal_id"), _unique(macro_rows, "signal_id"), _unique(m3_rows, "signal_id"), _unique(level_rows, "level_id")
    _unique(macro_rows, "event_id"); _unique(m3_rows, "event_id"); _unique(m3_rows, "record_id"); _unique(tactical_rows, "candidate_id")
    if signal_id not in signals or signal_id not in macros or signal_id not in m3s: raise ValueError("selected_signal_missing")
    signal, macro, m3 = signals[signal_id], macros[signal_id], m3s[signal_id]
    if macro["schema_version"] != "macro_structure_volatility_replay.v1" or macro["method_version"] != "macro_structure_volatility_replay.v1": raise ValueError("macro_version_invalid")
    if m3["schema_version"] != "macro_next_regime_replay.v1" or m3["method_version"] != "macro_next_regime_replay.v1": raise ValueError("m3_version_invalid")
    if any(row["schema_version"] != "level_reliability.v1" or row["method_version"] != "macro_structure_volatility_replay.v1" for row in level_rows): raise ValueError("level_version_invalid")
    event_at = _dt(macro["event_timestamp_utc"])
    if abs((_dt(m3["event_timestamp_utc"]) - event_at).total_seconds()) > 1 or abs((_dt(signal["timestamp_jst"]) - event_at).total_seconds()) > 1: raise ValueError("selected_timestamp_mismatch")
    target = _safe_text(m3["first_reliable_target"] or macro["first_reliable_target"]); obstruction = _safe_text(m3["intervening_obstruction"] or macro["intervening_obstruction"]).lower()
    for reference, code in ((target, "target_reference_invalid"), (obstruction, "obstruction_reference_invalid")):
        if reference and reference not in {"none", "insufficient", "unavailable"} and reference not in levels: raise ValueError(code)
        if reference and reference not in {"none", "insufficient", "unavailable"} and not _level_safe(levels[reference], event_at): raise ValueError("required_level_not_event_time_safe")
    candles = _ohlcv(_csv(ohlcv_1h_csv, {"timestamp_utc", "open", "high", "low", "close", "interval"}), "1h", event_at)[-72:]
    if not candles: raise ValueError("no_closed_1h_candle")
    if ohlcv_4h_csv: _ohlcv(_csv(ohlcv_4h_csv, {"timestamp_utc", "open", "high", "low", "close", "interval"}), "4h", event_at)
    flags, trace, overlays = [], {}, []
    for label, reference in (("target", target), ("obstruction", obstruction), ("nearest_support", macro.get("nearest_support_id", "")), ("nearest_resistance", macro.get("nearest_resistance_id", ""))):
        if not reference or reference in {"none", "insufficient", "unavailable"}: continue
        if reference not in levels or not _level_safe(levels[reference], event_at):
            flags.append(f"{label}:referenced ID / event-time geometry unavailable"); trace[label] = {"level_id": reference, "included": False, "reason": "not_event_time_safe"}; continue
        row = levels[reference]; geometry = {"level_id": reference, "low": float(row["low"]), "high": float(row["high"]), "center": float(row["center"]), "reliability_band": row["reliability_band"], "role": row["role"], "lifecycle": row["lifecycle"], "label": label}; trace[label] = {"level_id": reference, "included": True}; overlays.append(geometry)
    tactical = [{key: row.get(key, "") for key in ("candidate_id", "side", "candidate_type", "candidate_status", "entry_mode", "entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2", "market_entry_status", "limit_entry_status", "counter_scalp_status", "breakout_status", "active_headline", "next_condition")} for row in tactical_rows if row.get("source_signal_id") == signal_id]
    if not tactical: flags.append("no tactical candidate rows")
    event_price = float(macro["event_price"])
    manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "selected_signal_id": signal_id, "selected_event_timestamp_utc": event_at.isoformat(), "selected_event_timestamp_jst": signal.get("timestamp_jst", ""), "logical_sources": ["signal_context", "tactical_candidates", "macro_events", "macro_levels", "next_regime_events", "ohlcv_1h"], "input_fingerprints": {name: _fingerprint(path) for name, path in (("signal_context", signal_context_csv), ("tactical_candidates", tactical_candidates_csv), ("macro_events", macro_events_csv), ("macro_levels", macro_levels_csv), ("next_regime_events", next_regime_events_csv), ("ohlcv_1h", ohlcv_1h_csv))}, "source_versions": {"macro": macro["schema_version"], "m3": m3["schema_version"], "levels": "level_reliability.v1"}, "baseline_section_order": BASELINE_ORDER, "challenger_section_order": CHALLENGER_ORDER, "chart_first_confirmation": True, "chart_model": {"timeframe": "1h", "candles": candles, "event_price": event_price, "macro_overlays": overlays}, "macro_strip_model": {key: macro.get(key, "") for key in ("structural_state", "structural_direction", "price_location", "volatility_state", "expansion_risk", "first_reliable_target", "intervening_obstruction")}, "next_regime_card_model": {key: m3.get(key, "") for key in ("current_tactical_side", "current_structural_thesis", "weakening_thesis", "next_regime_side", "status", "activation_families", "reason_codes", "invalidation_reason_codes", "first_reliable_target", "baseline_side", "baseline_status", "baseline_grade", "baseline_type", "comparison_category")}, "tactical_execution_map_model": tactical, "secondary_operator_detail_model": {"action": signal.get("primary_setup_side", ""), "status": signal.get("primary_setup_status", ""), "wording": signal.get("prelabel", "")}, "missing_data_flags": sorted(flags), "source_trace_map": trace, "forbidden_field_audit": {"passed": True, "checked": "future-derived fields excluded"}, "safety_boundary": SAFETY}
    serialized = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if any(token in serialized for token in FORBIDDEN): raise ValueError("forbidden_future_field_detected")
    chart = _svg(candles, event_price, overlays, tactical, event_at.isoformat())
    card = manifest["next_regime_card_model"]; disagreement = card["current_tactical_side"] != card["next_regime_side"] and card["next_regime_side"] != "NONE"
    def rows(values: dict[str, Any]) -> str: return "".join(f"<li><b>{html.escape(key)}</b>: {html.escape(_safe_text(value))}</li>" for key, value in values.items())
    html_text = f"<!doctype html><html><head><meta charset=\"utf-8\"><style>body{{font:14px sans-serif;margin:20px;color:#172033}}section{{margin:18px 0;padding:12px;border:1px solid #d8deea}}.warn{{color:#a11}}</style></head><body><h1>Macro Operator Hierarchy Shadow</h1><p>report-only · human decides manually · evidence confidence, not execution permission</p><section id=\"chart\">{chart}</section><section id=\"macro\"><h2>Macro strip</h2><ul>{rows(manifest['macro_strip_model'])}</ul></section><section id=\"next-regime\"><h2>Next-regime card</h2><ul>{rows(card)}</ul><p class=\"warn\">{'tactical and next-regime sides disagree; no winner selected.' if disagreement else 'no execution permission.'}</p></section><section id=\"tactical\"><h2>Tactical execution price map</h2>{''.join('<ul>'+rows(row)+'</ul>' for row in tactical) or '<p>no tactical candidate rows</p>'}</section><details><summary>Operator action detail</summary><ul>{rows(manifest['secondary_operator_detail_model'])}</ul></details><section><h2>Missing data</h2><ul>{''.join('<li>'+html.escape(flag)+'</li>' for flag in flags) or '<li>none</li>'}</ul></section></body></html>"
    md = f"# Macro Operator Hierarchy Shadow\n\n## Selected event facts\n\n- signal: {signal_id}\n- timestamp: {event_at.isoformat()}\n\n## Section orders\n\n- baseline: {' > '.join(BASELINE_ORDER)}\n- challenger: {' > '.join(CHALLENGER_ORDER)}\n\n## Missing-data flags\n\n- {'; '.join(flags) or 'none'}\n\n## Future-field audit\n\n- passed\n\n## Source trace summary\n\n- {json.dumps(trace, sort_keys=True)}\n\n## Event-time level exclusions\n\n- {sum(not item['included'] for item in trace.values())}\n\n## Visual review checklist\n\n- chart first; macro/tactical overlays separate; operator detail last\n\n## Limitations\n\n- local hierarchy artifact only\n\n## Safety boundary\n\n- {SAFETY}\n"
    _atomic({output_html: html_text.encode(), output_json: (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode(), output_md: md.encode()}, replace_output)
    return {"ok": True, "exit_code": 0, "selected_signal": signal_id, "challenger_section_order": CHALLENGER_ORDER, "chart_first_confirmation": True, "missing_data_flags": sorted(flags), "closed_1h_candle_count": len(candles), "tactical_candidate_count": len(tactical), "event_time_safe_macro_overlay_count": len(overlays), "excluded_future_confirmed_reference_count": sum(not item["included"] for item in trace.values()), "output_count": 3}
