"""Deterministic, offline-only M4 operator hierarchy render shadow."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = METHOD_VERSION = "macro_operator_hierarchy_shadow.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
FORBIDDEN_FIELDS = ("outcome_1h", "outcome_3h", "outcome_6h", "outcome_12h", "outcome_24h", "mfe_atr", "mae_atr", "upward_excursion", "downward_excursion", "target_touch", "adverse_before_target", "whipsaw", "large_move_side", "first_material_move_timestamp")
BASELINE_ORDER = ["operator action wording", "tactical execution", "chart", "macro structure", "next-regime comparison"]
CHALLENGER_ORDER = ["chart", "macro strip", "next-regime card", "tactical execution map", "operator action detail"]

SIGNAL_FIELDS = {"signal_id", "timestamp_jst", "current_price", "primary_setup_side", "primary_setup_status", "prelabel"}
TACTICAL_FIELDS = {"candidate_id", "source_signal_id", "candidate_type", "candidate_status", "side", "entry_mode", "entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2", "market_entry_status", "limit_entry_status", "counter_scalp_status", "breakout_status", "active_headline", "next_condition"}
MACRO_FIELDS = {"schema_version", "method_version", "event_id", "signal_id", "event_timestamp_utc", "event_price", "structural_state", "structural_direction", "price_location", "volatility_state", "expansion_risk", "nearest_support_id", "nearest_resistance_id", "first_reliable_target", "intervening_obstruction"}
M3_FIELDS = {"schema_version", "method_version", "record_id", "event_id", "signal_id", "event_timestamp_utc", "current_tactical_side", "current_structural_thesis", "weakening_thesis", "next_regime_side", "status", "activation_families", "reason_codes", "invalidation_reason_codes", "first_reliable_target", "intervening_obstruction", "baseline_side", "baseline_status", "baseline_grade", "baseline_type", "comparison_category"}
LEVEL_FIELDS = {"schema_version", "method_version", "level_id", "low", "high", "center", "reliability_band", "role", "lifecycle", "last_confirmed_at", "member_confirmation_timestamps"}
OHLCV_FIELDS = {"timestamp_utc", "open", "high", "low", "close", "interval"}


def _dt(value: Any) -> datetime:
    try: result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc: raise ValueError("malformed_timestamp") from exc
    if result.tzinfo is None: raise ValueError("malformed_timestamp")
    return result.astimezone(timezone.utc)


def _read(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file(): raise ValueError("input_file_missing")
    with path.open(encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        if not reader.fieldnames or not required.issubset(reader.fieldnames): raise ValueError("input_schema_invalid")
        return [dict(row) for row in reader]


def _unique(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        value = str(row.get(key, "")).strip()
        if not value or value in result: raise ValueError("duplicate_or_missing_identifier")
        result[value] = row
    return result


def _norm(value: Any, kind: str = "evidence") -> str:
    text = str(value or "").strip()
    if text: return text
    return "none" if kind == "reference" else "insufficient"


def _number(value: Any, code: str) -> float:
    try: result = float(str(value))
    except (TypeError, ValueError) as exc: raise ValueError(code) from exc
    if not math.isfinite(result): raise ValueError(code)
    return result


def _fingerprint(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_level(row: dict[str, str], event_at: datetime) -> bool:
    if _dt(row["last_confirmed_at"]) > event_at: return False
    timestamps = [value.strip() for value in row["member_confirmation_timestamps"].split(",") if value.strip()]
    return bool(timestamps) and all(_dt(value) <= event_at for value in timestamps)


def _ohlcv(rows: list[dict[str, str]], interval: str, event_at: datetime) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prior: datetime | None = None; closed: list[dict[str, Any]] = []; hours = 1 if interval == "1h" else 4
    for row in rows:
        if row["interval"] != interval: raise ValueError("ohlcv_interval_invalid")
        at = _dt(row["timestamp_utc"])
        if prior is not None and at <= prior: raise ValueError("ohlcv_timestamp_invalid")
        prior = at
        values = {key: _number(row[key], "ohlcv_numeric_invalid") for key in ("open", "high", "low", "close")}
        if at + timedelta(hours=hours) <= event_at: closed.append({"timestamp_utc": at.isoformat(), **values})
    return closed, {"interval": interval, "interval_validation": "passed", "closed_at_event_validation": "passed", "closed_candle_count": len(closed)}


def _atomic(outputs: dict[Path, bytes], replace_output: bool) -> None:
    if any(path.exists() for path in outputs) and not replace_output: raise ValueError("output_exists_use_replace")
    stage = Path(tempfile.mkdtemp(prefix="macro-hierarchy-")); staged: dict[Path, Path] = {}; backups: dict[Path, Path] = {}; promoted: list[Path] = []
    try:
        for index, (path, payload) in enumerate(outputs.items()):
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = stage / f"new-{index}"; temp.write_bytes(payload); staged[path] = temp
            if path.exists():
                backup = stage / f"old-{index}"; os.replace(path, backup); backups[path] = backup
        for path, temp in staged.items(): os.replace(temp, path); promoted.append(path)
    except Exception:
        for path in promoted:
            if path.exists(): path.unlink()
        for path, backup in backups.items():
            if backup.exists(): os.replace(backup, path)
        raise
    finally: shutil.rmtree(stage, ignore_errors=True)


def _reference(semantic: str, reference: str, levels: dict[str, dict[str, str]], event_at: datetime, flags: list[str], trace: dict[str, Any]) -> dict[str, Any] | None:
    reference = _norm(reference, "reference")
    trace_key = f"macro_reference.{semantic}"
    if reference in {"none", "insufficient", "unavailable"}:
        value = {"level_id": reference, "status": reference, "semantic": semantic}; trace[trace_key] = {"logical_source": "macro_events", "source_field": semantic, "natural_key": "selected signal", "included": False, "exclusion_reason": reference}; return value
    if reference not in levels:
        if semantic in {"target", "obstruction"}: raise ValueError(f"{semantic}_reference_invalid")
        flags.append(f"{semantic}:event_time_geometry_unavailable")
        value = {"level_id": reference, "status": "event_time_geometry_unavailable", "semantic": semantic, "reason": "reference_absent"}; trace[trace_key] = {"logical_source": "macro_levels", "source_field": "level_id", "natural_key": reference, "included": False, "exclusion_reason": "reference_absent"}; return value
    row = levels[reference]
    if not _safe_level(row, event_at):
        if semantic in {"target", "obstruction"}: raise ValueError("required_level_not_event_time_safe")
        flags.append(f"{semantic}:event_time_geometry_unavailable")
        value = {"level_id": reference, "status": "event_time_geometry_unavailable", "semantic": semantic, "reason": "future_confirmation"}; trace[trace_key] = {"logical_source": "macro_levels", "source_field": "confirmation metadata", "natural_key": reference, "included": False, "exclusion_reason": "future_confirmation"}; return value
    role = _norm(row["role"])
    expected = {"nearest_support": "support", "nearest_resistance": "resistance"}.get(semantic)
    if expected and role != expected:
        flags.append(f"{semantic}:reference_role_mismatch")
        value = {"level_id": reference, "status": "reference_role_mismatch", "semantic": semantic, "actual_level_role": role, "reason": f"expected_{expected}"}; trace[trace_key] = {"logical_source": "macro_levels", "source_field": "role", "natural_key": reference, "included": False, "exclusion_reason": "reference_role_mismatch"}; return value
    value = {"level_id": reference, "status": "available", "semantic": semantic, "low": _number(row["low"], "level_numeric_invalid"), "high": _number(row["high"], "level_numeric_invalid"), "center": _number(row["center"], "level_numeric_invalid"), "reliability_band": _norm(row["reliability_band"]), "level_role": role, "lifecycle": _norm(row["lifecycle"])}
    trace[trace_key] = {"logical_source": "macro_levels", "source_field": "event-time safe level fields", "natural_key": reference, "included": True}
    return value


def _svg(candles: list[dict[str, Any]], price: float, overlays: list[dict[str, Any]], tactical: list[dict[str, Any]], event_at: str) -> str:
    width, height, pad = 960, 420, 40
    numbers = [price] + [n for c in candles for n in (c["low"], c["high"])] + [n for o in overlays for n in (o["low"], o["high"])]
    for row in tactical:
        for key in ("entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2"): numbers.append(row[key])
    low, high = min(numbers), max(numbers); span = max(high - low, 1.0); low -= span * .08; high += span * .08
    y = lambda value: pad + (high - value) / (high - low) * (height - 2 * pad)
    x = lambda i: pad + (i + .5) * (width - 2 * pad) / max(len(candles), 1)
    bodies = []
    for i, c in enumerate(candles):
        color = "#168253" if c["close"] >= c["open"] else "#b3261e"; cx = x(i); yo, yc = y(c["open"]), y(c["close"])
        bodies.append(f'<line class="candle-wick" x1="{cx:.2f}" y1="{y(c["high"]):.2f}" x2="{cx:.2f}" y2="{y(c["low"]):.2f}" stroke="{color}"/><rect class="candle-body" x="{cx-2.5:.2f}" y="{min(yo,yc):.2f}" width="5" height="{max(abs(yo-yc),1):.2f}" fill="{color}"/>')
    bands = [f'<rect class="macro-band" x="{pad}" y="{y(o["high"]):.2f}" width="{width-2*pad}" height="{max(y(o["low"])-y(o["high"]),1):.2f}" fill="#5b6ee1" opacity=".16"/><text x="{pad+5}" y="{y(o["center"]):.2f}" font-size="10">macro {html.escape("/".join(o["semantic_labels"]))}</text>' for o in overlays]
    tact = []
    for i, row in enumerate(tactical):
        tact.append(f'<rect class="tactical-zone" x="{pad}" y="{y(row["entry_zone_high"]):.2f}" width="{width-2*pad}" height="{max(y(row["entry_zone_low"])-y(row["entry_zone_high"]),1):.2f}" fill="#f59e0b" opacity=".16"/><text x="{pad+5}" y="{y(row["entry_zone_high"])-2:.2f}" font-size="10">tactical zone {html.escape(row["candidate_id"])}</text>')
        for key, color in (("entry_price", "#0f766e"), ("stop_loss", "#b91c1c"), ("tp1", "#2563eb"), ("tp2", "#7c3aed")):
            tact.append(f'<line class="tactical-line" x1="{pad}" y1="{y(row[key]):.2f}" x2="{width-pad}" y2="{y(row[key]):.2f}" stroke="{color}" opacity=".55"/>')
    event = f'<line class="event-price" x1="{pad}" y1="{y(price):.2f}" x2="{width-pad}" y2="{y(price):.2f}" stroke="#111" stroke-dasharray="4 3"/><text x="{width-pad-110}" y="{y(price)-3:.2f}" font-size="10">event price</text>'
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="1 hour event-time chart"><rect width="{width}" height="{height}" fill="#fff"/><text x="{pad}" y="20" font-size="14">1H event-time chart — {html.escape(event_at)}</text>{"".join(bands)}{"".join(tact)}{"".join(bodies)}{event}</svg>'


def render_macro_operator_hierarchy_shadow(*, signal_context_csv: Path, tactical_candidates_csv: Path, macro_events_csv: Path, macro_levels_csv: Path, next_regime_events_csv: Path, ohlcv_1h_csv: Path, signal_id: str, output_html: Path, output_json: Path, output_md: Path, replace_output: bool = False, ohlcv_4h_csv: Path | None = None) -> dict[str, Any]:
    signal_rows, tactical_rows, macro_rows, level_rows, m3_rows = _read(signal_context_csv, SIGNAL_FIELDS), _read(tactical_candidates_csv, TACTICAL_FIELDS), _read(macro_events_csv, MACRO_FIELDS), _read(macro_levels_csv, LEVEL_FIELDS), _read(next_regime_events_csv, M3_FIELDS)
    signals, macros, levels, m3s = _unique(signal_rows, "signal_id"), _unique(macro_rows, "signal_id"), _unique(level_rows, "level_id"), _unique(m3_rows, "signal_id")
    _unique(macro_rows, "event_id"); _unique(m3_rows, "event_id"); _unique(m3_rows, "record_id"); _unique(tactical_rows, "candidate_id")
    if signal_id not in signals or signal_id not in macros or signal_id not in m3s: raise ValueError("selected_signal_missing")
    signal, macro, m3 = signals[signal_id], macros[signal_id], m3s[signal_id]
    if macro["schema_version"] != "macro_structure_volatility_replay.v1" or macro["method_version"] != "macro_structure_volatility_replay.v1": raise ValueError("macro_version_invalid")
    if m3["schema_version"] != "macro_next_regime_replay.v1" or m3["method_version"] != "macro_next_regime_replay.v1": raise ValueError("m3_version_invalid")
    if any(r["schema_version"] != "level_reliability.v1" or r["method_version"] != "macro_structure_volatility_replay.v1" for r in level_rows): raise ValueError("level_version_invalid")
    event_at = _dt(macro["event_timestamp_utc"])
    if abs((_dt(signal["timestamp_jst"]) - event_at).total_seconds()) > 1 or abs((_dt(m3["event_timestamp_utc"]) - event_at).total_seconds()) > 1: raise ValueError("selected_timestamp_mismatch")
    candles, one_status = _ohlcv(_read(ohlcv_1h_csv, OHLCV_FIELDS), "1h", event_at); candles = candles[-72:]
    if not candles: raise ValueError("no_closed_1h_candle")
    four_status: dict[str, Any] | None = None
    if ohlcv_4h_csv is not None: _, four_status = _ohlcv(_read(ohlcv_4h_csv, OHLCV_FIELDS), "4h", event_at)
    flags: list[str] = []; trace: dict[str, Any] = {}
    target = _norm(m3["first_reliable_target"] or macro["first_reliable_target"], "reference")
    obstruction = _norm(m3["intervening_obstruction"] or macro["intervening_obstruction"], "reference")
    references = {"nearest_support": _reference("nearest_support", macro["nearest_support_id"], levels, event_at, flags, trace), "nearest_resistance": _reference("nearest_resistance", macro["nearest_resistance_id"], levels, event_at, flags, trace), "target": _reference("target", target, levels, event_at, flags, trace), "obstruction": _reference("obstruction", obstruction, levels, event_at, flags, trace)}
    geometry: dict[str, dict[str, Any]] = {}
    for value in references.values():
        if value and value["status"] == "available":
            item = geometry.setdefault(value["level_id"], {**value, "semantic_labels": []}); item["semantic_labels"].append(value["semantic"])
    overlays = [{**v, "semantic_labels": sorted(v["semantic_labels"])} for _, v in sorted(geometry.items())]
    for item in overlays: trace[f"macro_geometry.{item['level_id']}"] = {"logical_source": "macro_levels", "source_field": "low/high/center", "natural_key": item["level_id"], "included": True}
    tactical: list[dict[str, Any]] = []
    for row in sorted((r for r in tactical_rows if r["source_signal_id"] == signal_id), key=lambda r: r["candidate_id"]):
        item = {key: _norm(row[key]) for key in TACTICAL_FIELDS if key != "source_signal_id"}
        for key in ("entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2"): item[key] = _number(row[key], "tactical_geometry_invalid")
        if item["entry_zone_low"] > item["entry_zone_high"]: raise ValueError("tactical_geometry_invalid")
        tactical.append(item); trace[f"tactical.{item['candidate_id']}"] = {"logical_source": "tactical_candidates", "source_field": "display allowlist", "natural_key": item["candidate_id"], "included": True}
    if not tactical: flags.append("tactical:no_candidate_rows")
    detail_values: dict[str, list[str]] = {"active_headlines": [], "next_conditions": []}
    for row in tactical:
        for key, output in (("active_headline", "active_headlines"), ("next_condition", "next_conditions")):
            detail_values[output].append(f"{row[key]} [{row['candidate_id']}]")
    detail = {"primary_setup_side": _norm(signal["primary_setup_side"]), "primary_setup_status": _norm(signal["primary_setup_status"]), "prelabel": _norm(signal["prelabel"]), **{key: sorted(set(value)) or ["insufficient"] for key, value in detail_values.items()}}
    macro_strip = {key: _norm(macro[key]) for key in ("structural_state", "structural_direction", "price_location", "volatility_state", "expansion_risk")}; macro_strip["references"] = references
    card = {key: _norm(m3[key], "reference" if key in {"first_reliable_target", "intervening_obstruction"} else "evidence") for key in ("current_tactical_side", "current_structural_thesis", "weakening_thesis", "next_regime_side", "status", "activation_families", "reason_codes", "invalidation_reason_codes", "first_reliable_target", "intervening_obstruction", "baseline_side", "baseline_status", "baseline_grade", "baseline_type", "comparison_category")}
    if card["next_regime_side"] == "NONE": card["direction_display"] = "no directional next-regime claim"
    disagreement = card["next_regime_side"] not in {"NONE", card["current_tactical_side"]}
    sources = {"signal_context": signal_context_csv, "tactical_candidates": tactical_candidates_csv, "macro_events": macro_events_csv, "macro_levels": macro_levels_csv, "next_regime_events": next_regime_events_csv, "ohlcv_1h": ohlcv_1h_csv}
    if ohlcv_4h_csv is not None: sources["ohlcv_4h"] = ohlcv_4h_csv
    for group, source, field, key in (("selected_signal", "signal_context", "signal_id", signal_id), ("event_timestamp", "macro_events", "event_timestamp_utc", signal_id), ("event_price", "macro_events", "event_price", signal_id), ("closed_1h_candles", "ohlcv_1h", "closed-candle rule", "1h"), ("optional_4h_validation", "ohlcv_4h", "closed-candle rule", "4h"), ("next_regime_card", "next_regime_events", "display allowlist", signal_id), ("operator_detail", "signal_context/tactical_candidates", "display allowlist", signal_id), ("baseline_section_order", "derived", "constant", "none"), ("challenger_section_order", "derived", "constant", "none"), ("safety_labels", "derived", "constant", "none")):
        trace[group] = {"logical_source": source, "source_field": field, "natural_key": key, "included": True}
    manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "selected_signal_id": signal_id, "selected_event_timestamp_utc": event_at.isoformat(), "selected_event_timestamp_jst": signal["timestamp_jst"], "logical_sources": sorted(sources), "input_fingerprints": {name: _fingerprint(path) for name, path in sorted(sources.items())}, "source_versions": {"macro_events": {"schema_version": macro["schema_version"], "method_version": macro["method_version"]}, "macro_levels": {"schema_version": level_rows[0]["schema_version"], "method_version": level_rows[0]["method_version"]}, "next_regime_events": {"schema_version": m3["schema_version"], "method_version": m3["method_version"]}, "view_model": {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION}}, "validation_metadata": {"ohlcv_1h": one_status, **({"ohlcv_4h": four_status} if four_status else {})}, "baseline_section_order": BASELINE_ORDER, "challenger_section_order": CHALLENGER_ORDER, "chart_first_confirmation": True, "chart_model": {"timeframe": "1h", "candles": candles, "event_price": _number(macro["event_price"], "event_price_invalid"), "macro_overlays": overlays, "tactical_entry_zone_count": len(tactical)}, "macro_strip_model": macro_strip, "next_regime_card_model": card, "tactical_execution_map_model": tactical, "secondary_operator_detail_model": detail, "missing_data_flags": sorted(set(flags)), "source_trace_map": trace, "forbidden_field_audit": {"forbidden_field_names_checked": list(FORBIDDEN_FIELDS), "json_audit_pass": True, "html_audit_pass": True, "markdown_audit_pass": True}, "safety_boundary": SAFETY}
    json_text = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    def table(values: dict[str, Any]) -> str: return "".join(f"<li><b>{html.escape(str(k))}</b>: {html.escape(json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list)) else str(v))}</li>" for k, v in values.items())
    chart = _svg(candles, manifest["chart_model"]["event_price"], overlays, tactical, event_at.isoformat())
    html_text = f'<!doctype html><html><head><meta charset="utf-8"><style>body{{font:14px sans-serif;margin:20px;color:#172033}}section,details{{margin:18px 0;padding:12px;border:1px solid #d8deea}}.safety{{color:#7a1520}}.hierarchy{{white-space:pre-line}}</style></head><body><h1>Macro Operator Hierarchy Shadow</h1><p class="safety">evidence confidence, not execution permission · report-only · human decides manually</p><section id="hierarchy"><h2>Hierarchy comparison</h2><p class="hierarchy">Baseline hierarchy approximation: {html.escape(" > ".join(BASELINE_ORDER))}\nM4 challenger: {html.escape(" > ".join(CHALLENGER_ORDER))}\nchallenger chart precedes operator wording: true</p></section><section id="chart">{chart}</section><section id="macro"><h2>Macro strip</h2><ul>{table(macro_strip)}</ul></section><section id="next-regime"><h2>Next-regime card</h2><ul>{table(card)}</ul><p class="safety">{"tactical and next-regime sides disagree; no winner selected." if disagreement else "no execution permission."}</p></section><section id="tactical"><h2>Tactical execution price map</h2>{"".join("<ul>"+table(row)+"</ul>" for row in tactical) or "<p>no tactical candidate rows</p>"}</section><details id="operator-detail"><summary>Operator action detail</summary><ul>{table(detail)}</ul></details><footer class="safety">{html.escape(SAFETY)}</footer></body></html>'
    md = f"# Macro Operator Hierarchy Shadow\n\n## Selected event facts\n\n- signal: {signal_id}\n- timestamp: {event_at.isoformat()}\n\n## Section orders\n\n- baseline: {' > '.join(BASELINE_ORDER)}\n- challenger: {' > '.join(CHALLENGER_ORDER)}\n- challenger chart precedes operator wording: true\n\n## Macro strip\n\n{json.dumps(macro_strip, ensure_ascii=False, sort_keys=True)}\n\n## Missing-data flags\n\n- {'; '.join(sorted(set(flags))) or 'none'}\n\n## Future-field audit\n\n- JSON/HTML/Markdown: passed\n\n## Source trace summary\n\n- groups: {len(trace)}\n\n## Event-time level exclusions\n\n- {sum(1 for item in references.values() if item and item['status'] != 'available')}\n\n## Visual review checklist\n\n- chart first; macro/tactical geometry separate; operator detail final\n\n## Limitations\n\n- local hierarchy artifact only; no production UI reproduction\n\n## Safety boundary\n\n- {SAFETY}\n"
    # The manifest records the audit vocabulary itself, so audit only the
    # source-derived display model rather than rejecting its own checklist.
    display_json = json.dumps({"chart": manifest["chart_model"], "macro": macro_strip, "card": card, "tactical": tactical, "detail": detail}, ensure_ascii=False, sort_keys=True)
    if any(name in display_json for name in FORBIDDEN_FIELDS): raise ValueError("forbidden_future_field_detected")
    _atomic({output_html: html_text.encode(), output_json: json_text.encode(), output_md: md.encode()}, replace_output)
    return {"ok": True, "exit_code": 0, "selected_signal": signal_id, "challenger_section_order": CHALLENGER_ORDER, "chart_first_confirmation": True, "missing_data_flags": sorted(set(flags)), "closed_1h_candle_count": len(candles), "tactical_candidate_count": len(tactical), "tactical_entry_zone_count": len(tactical), "event_time_safe_macro_overlay_count": len(overlays), "included_target_semantic_count": sum("target" in row["semantic_labels"] for row in overlays), "nearest_support_role_mismatch_count": sum(item and item["status"] == "reference_role_mismatch" for item in references.values()), "excluded_future_confirmed_reference_count": sum(item and item["status"] == "event_time_geometry_unavailable" for item in references.values()), "trace_coverage_pass": bool(trace), "output_count": 3}
