"""Deterministic, report-only chart-first M-OPS3 operator artifact."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from src.feedback.macro_structure_trendline_channel import METHOD_VERSION as TRENDLINE_METHOD_VERSION, build_trendline_model
from src.feedback.macro_structure_structural_events import METHOD_VERSION as STRUCTURAL_EVENT_METHOD_VERSION, build_structural_event_model
from src.feedback.macro_structure_scenarios import METHOD_VERSION as SCENARIO_METHOD_VERSION, build_scenario_model
from src.feedback.macro_structure_latest_entry import LatestEntryPublicationError, publish_available_entry, publish_unavailable_entry

SCHEMA_VERSION = "macro_structure_operator_artifact.v2"
METHOD_VERSION = "macro_structure_operator_artifact.v2"
M1_SCHEMA_VERSION = "macro_structure_daily_operation.v1"
M2_SCHEMA_VERSION = "macro_structure_history_operation.v2"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
JST = ZoneInfo("Asia/Tokyo")
OUTPUT_NAMES = ("macro_structure_operator.html", "macro_structure_operator.json", "macro_structure_operator.md", "run_manifest.json")
OHLCV_FIELDS = ("timestamp_utc", "open", "high", "low", "close")
ZONE_FIELDS = (
    "level_id", "side", "role", "low", "high", "center", "source_timeframes", "first_seen_at",
    "last_confirmed_at", "touch_count", "clean_rejection_count", "break_count", "false_break_reclaim_count",
    "lifecycle", "reliability_score", "reliability_band", "distance_from_price_pct", "distance_from_price_atr", "reason_codes",
)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _compact_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _utc(value: Any, code: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(code)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(code) from exc
    if parsed.tzinfo is None:
        raise ValueError(code)
    return parsed.astimezone(timezone.utc)


def _number(value: Any, code: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(code) from exc
    if not math.isfinite(number):
        raise ValueError(code)
    return number


def _fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value


def _direct_artifact(root: Path, latest_name: str, prefix: str, code: str) -> tuple[Path, dict[str, Any]]:
    latest = _load_json(root / "latest.json", code)
    artifact = _text(latest.get("artifact_dir"))
    identity = _text(latest.get("run_id")) if prefix == "run_" else _text(latest.get("history_id"))
    if not artifact or artifact != identity or not artifact.startswith(prefix) or Path(artifact).name != artifact:
        raise ValueError("latest_identity_mismatch")
    directory = root / artifact
    if not directory.is_dir() or directory.parent != root:
        raise ValueError("latest_artifact_not_direct_child")
    return directory, latest


def _validate_snapshot(root: Path, symbol: str) -> tuple[dict[str, Any], dict[str, Any], Path, dict[str, str]]:
    run_dir, latest = _direct_artifact(root, "latest.json", "run_", "snapshot_latest_invalid")
    if not all((run_dir / name).is_file() for name in ("macro_structure_snapshot.json", "macro_structure_snapshot.md", "macro_level_reliability.csv", "run_manifest.json")):
        raise ValueError("incomplete_snapshot_artifact")
    snapshot = _load_json(run_dir / "macro_structure_snapshot.json", "snapshot_invalid")
    manifest = _load_json(run_dir / "run_manifest.json", "snapshot_manifest_invalid")
    if snapshot.get("run_id") != run_dir.name or manifest.get("run_id") != run_dir.name:
        raise ValueError("snapshot_identity_mismatch")
    if snapshot.get("snapshot_id") != manifest.get("snapshot_id") or latest.get("snapshot_id") != snapshot.get("snapshot_id"):
        raise ValueError("snapshot_identity_mismatch")
    if snapshot.get("symbol") != symbol or manifest.get("symbol", symbol) != symbol or latest.get("symbol", symbol) != symbol:
        raise ValueError("snapshot_symbol_mismatch")
    if snapshot.get("schema_version") != M1_SCHEMA_VERSION or snapshot.get("method_version") != M1_SCHEMA_VERSION:
        raise ValueError("snapshot_version_invalid")
    if manifest.get("source") != "public_ohlcv_only" or manifest.get("report_only") is not True or manifest.get("automatic_order_allowed") is not False or manifest.get("private_actual_trade_input") is not False:
        raise ValueError("snapshot_source_boundary_invalid")
    as_of = _utc(snapshot.get("as_of_utc"), "snapshot_timestamp_invalid")
    evaluated = _utc(snapshot.get("evaluated_at_utc"), "snapshot_timestamp_invalid")
    if _text(snapshot.get("as_of_jst")) != as_of.astimezone(JST).isoformat() or _text(snapshot.get("evaluated_at_jst")) != evaluated.astimezone(JST).isoformat():
        raise ValueError("snapshot_jst_mismatch")
    if _utc(manifest.get("as_of_utc"), "snapshot_manifest_timestamp_invalid") != as_of or _utc(manifest.get("evaluated_at_utc"), "snapshot_manifest_timestamp_invalid") != evaluated:
        raise ValueError("snapshot_timestamp_mismatch")
    required = ("result_status", "freshness", "as_of_jst", "evaluated_at_jst", "reliability_band_counts", "structure_state", "price_location", "current_price", "stale_status", "continuity_status", "data_quality_status", "reason_codes", "support_zones", "resistance_zones", "nearest_reliable_support", "nearest_reliable_resistance", "next_upside_target", "next_downside_target", "upside_obstruction", "downside_obstruction", "volatility_state", "expansion_risk", "directional_activation", "safety_boundary")
    if any(field not in snapshot for field in required):
        raise ValueError("snapshot_fields_missing")
    try:
        with (run_dir / "macro_level_reliability.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not {"level_id", "side", "role", "low", "high", "center", "lifecycle", "reliability_band", "reliability_score"}.issubset(reader.fieldnames):
                raise ValueError("snapshot_level_schema_invalid")
            levels = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValueError("snapshot_level_schema_invalid") from exc
    if any(not _text(row.get("level_id")) for row in levels):
        raise ValueError("snapshot_level_id_invalid")
    fingerprints = {"snapshot": _fingerprint(run_dir / "macro_structure_snapshot.json"), "snapshot_levels": _fingerprint(run_dir / "macro_level_reliability.csv"), "snapshot_manifest": _fingerprint(run_dir / "run_manifest.json")}
    snapshot["_as_of"] = as_of
    snapshot["_evaluated"] = evaluated
    snapshot["_levels"] = levels
    return snapshot, manifest, run_dir, fingerprints


def _validate_history(root: Path, symbol: str, snapshot: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Path, dict[str, str]]:
    history_dir, latest = _direct_artifact(root, "latest.json", "history_", "history_latest_invalid")
    if not all((history_dir / name).is_file() for name in ("macro_structure_history.json", "macro_structure_history.md", "macro_snapshot_history.csv", "macro_level_history.csv", "macro_structure_changes.csv", "run_manifest.json")):
        raise ValueError("incomplete_history_artifact")
    history = _load_json(history_dir / "macro_structure_history.json", "history_invalid")
    manifest = _load_json(history_dir / "run_manifest.json", "history_manifest_invalid")
    if history.get("schema_version") != M2_SCHEMA_VERSION or history.get("method_version") != M2_SCHEMA_VERSION or manifest.get("schema_version") != M2_SCHEMA_VERSION or manifest.get("method_version") != M2_SCHEMA_VERSION:
        raise ValueError("history_version_invalid")
    if history.get("history_id") != history_dir.name or manifest.get("history_id") != history_dir.name or latest.get("history_id") != history_dir.name or latest.get("artifact_dir") != history_dir.name:
        raise ValueError("history_identity_mismatch")
    if history.get("symbol") != symbol or manifest.get("symbol") != symbol or latest.get("symbol") != symbol:
        raise ValueError("history_symbol_mismatch")
    if manifest.get("source") != "public_mops1_artifacts_only" or manifest.get("report_only") is not True or manifest.get("automatic_order_allowed") is not False or manifest.get("private_actual_trade_input") is not False:
        raise ValueError("history_source_boundary_invalid")
    run_id = _text(snapshot.get("run_id"))
    evaluation_run_ids = [item.get("run_id") for item in history.get("evaluation_history", []) if isinstance(item, dict)]
    if run_id not in manifest.get("source_runs", []) or run_id not in evaluation_run_ids:
        raise ValueError("history_missing_current_snapshot")
    if _text(history.get("latest_as_of_utc")) != snapshot["_as_of"].isoformat():
        raise ValueError("history_snapshot_cutoff_mismatch")
    evaluations = [item for item in history.get("evaluation_history", []) if item.get("run_id") == run_id]
    if not evaluations:
        raise ValueError("history_missing_current_snapshot")
    checkpoint_id = evaluations[0].get("checkpoint_id")
    structural_checkpoints = history.get("structural_checkpoints")
    if not isinstance(structural_checkpoints, list) or not structural_checkpoints:
        raise ValueError("history_checkpoint_missing")
    if not _text(structural_checkpoints[-1].get("checkpoint_id")) or checkpoint_id != structural_checkpoints[-1].get("checkpoint_id"):
        raise ValueError("history_current_snapshot_not_latest_checkpoint")
    checkpoints = [item for item in structural_checkpoints if item.get("checkpoint_id") == checkpoint_id]
    if not checkpoints:
        raise ValueError("history_checkpoint_missing")
    checkpoint = checkpoints[0]
    latest_checkpoint_evaluation = checkpoint.get("latest_evaluation", {}) if isinstance(checkpoint.get("latest_evaluation"), dict) else {}
    if _text(checkpoint.get("latest_evaluation_run_id") or latest_checkpoint_evaluation.get("run_id")) != run_id:
        raise ValueError("history_current_snapshot_not_latest_checkpoint")
    snapshot["_checkpoint_id"] = checkpoint_id
    fingerprints = {"history": _fingerprint(history_dir / "macro_structure_history.json"), "history_snapshots": _fingerprint(history_dir / "macro_snapshot_history.csv"), "history_levels": _fingerprint(history_dir / "macro_level_history.csv"), "history_changes": _fingerprint(history_dir / "macro_structure_changes.csv"), "history_manifest": _fingerprint(history_dir / "run_manifest.json")}
    return history, manifest, history_dir, fingerprints


def _read_ohlcv(path: Path, symbol: str, cutoff: datetime, expected_close: float, *, interval: str = "15m", limit: int = 96, match_close: bool = True) -> tuple[list[dict[str, Any]], str]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not set(OHLCV_FIELDS).issubset(reader.fieldnames):
                raise ValueError("ohlcv_schema_invalid")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValueError("ohlcv_schema_invalid") from exc
    previous: datetime | None = None
    eligible: list[dict[str, Any]] = []
    for raw in rows:
        if _text(raw.get("interval")) and _text(raw.get("interval")) != interval:
            raise ValueError("ohlcv_interval_invalid")
        if _text(raw.get("symbol")) and _text(raw.get("symbol")) != symbol:
            raise ValueError("ohlcv_symbol_mismatch")
        at = _utc(raw.get("timestamp_utc"), "ohlcv_timestamp_invalid")
        if previous is not None and at <= previous:
            raise ValueError("ohlcv_timestamp_order_invalid")
        previous = at
        values = {field: _number(raw.get(field), "ohlcv_numeric_invalid") for field in ("open", "high", "low", "close")}
        if values["high"] < max(values["open"], values["close"]) or values["low"] > min(values["open"], values["close"]) or values["low"] > values["high"]:
            raise ValueError("ohlcv_ohlc_invalid")
        endpoint = at + timedelta(minutes=15 if interval == "15m" else 4 * 60)
        if endpoint <= cutoff:
            eligible.append({"timestamp_utc": at.isoformat(), "endpoint_utc": endpoint.isoformat(), **values})
    if not eligible:
        raise ValueError("ohlcv_no_closed_candle")
    if match_close and abs(eligible[-1]["close"] - expected_close) > max(1e-8, abs(expected_close) * 1e-8):
        raise ValueError("snapshot_price_ohlcv_mismatch")
    return eligible[-limit:], _fingerprint(path)


def _validated_zone(value: Any, code: str = "zone_evidence_invalid") -> dict[str, Any] | None:
    if not isinstance(value, dict) or not value:
        raise ValueError(code)
    if not _text(value.get("level_id")):
        raise ValueError(code)
    if _text(value.get("role")) not in {"support", "resistance"} or not _text(value.get("side")):
        raise ValueError(code)
    for field in ("low", "center", "high", "reliability_score", "distance_from_price_pct", "distance_from_price_atr"):
        _number(value.get(field), code)
    if not (_number(value["low"], code) <= _number(value["center"], code) <= _number(value["high"], code)):
        raise ValueError(code)
    for field in ("source_timeframes", "first_seen_at", "last_confirmed_at", "lifecycle", "reason_codes"):
        if value.get(field) in (None, ""):
            raise ValueError(code)
    for field in ("touch_count", "clean_rejection_count", "break_count", "false_break_reclaim_count"):
        if value.get(field) in (None, ""):
            raise ValueError(code)
        _number(value.get(field), code)
    if _text(value.get("reliability_band")) not in {"high", "medium"}:
        return None
    return {field: value.get(field, "") for field in ZONE_FIELDS}


def _zones(snapshot: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    def ordered(values: Any) -> list[dict[str, Any]]:
        if not isinstance(values, list):
            raise ValueError("zone_evidence_invalid")
        items = [item for item in (_validated_zone(value) for value in values) if item is not None]
        return sorted(items, key=lambda item: (-{"high": 2, "medium": 1}.get(_text(item["reliability_band"]), 0), _number(item["distance_from_price_pct"] or 0, "zone_distance_invalid"), _text(item["level_id"])))
    support = ordered(snapshot.get("support_zones"))
    resistance = ordered(snapshot.get("resistance_zones"))
    support = [item for item in support if _text(item["reliability_band"]) in {"high", "medium"}]
    resistance = [item for item in resistance if _text(item["reliability_band"]) in {"high", "medium"}]
    return support, resistance, support + resistance


def _optional_reference(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in {"", "none", "insufficient"}:
        return None
    if isinstance(value, dict) and not value:
        return None
    return _validated_zone(value)


def _references(snapshot: dict[str, Any], shown: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["level_id"]: {**item, "semantic_labels": []} for item in shown}
    for semantic, field in (("nearest_support", "nearest_reliable_support"), ("nearest_resistance", "nearest_reliable_resistance"), ("upside_target", "next_upside_target"), ("downside_target", "next_downside_target"), ("upside_obstruction", "upside_obstruction"), ("downside_obstruction", "downside_obstruction")):
        value = snapshot.get(field)
        item = _optional_reference(value)
        if item is not None:
            by_id.setdefault(item["level_id"], {**item, "semantic_labels": []})
            by_id[item["level_id"]]["semantic_labels"].append(semantic)
    for item in by_id.values():
        item["semantic_labels"] = sorted(item["semantic_labels"])
    return [by_id[key] for key in sorted(by_id)]


def _source_label(value: Any) -> str:
    parts = {part.strip().lower() for part in _text(value).replace(" ", "").split(",") if part.strip()}
    if "1h" in parts and "4h" in parts:
        return "1H+4H"
    if "4h" in parts:
        return "4H"
    return "1H"


def _svg(candles: list[dict[str, Any]], price: float, overlays: list[dict[str, Any]], cutoff: str, *, timeframe: str = "15m", trendline_model: dict[str, Any] | None = None, structural_event_model: dict[str, Any] | None = None) -> str:
    width, height, pad = 1100, 480, 46
    numbers = [price] + [n for candle in candles for n in (candle["low"], candle["high"])] + [n for item in overlays for n in (float(item["low"]), float(item["high"]))]
    diagonal_lines = [] if not trendline_model else [line for line in trendline_model.get("lines", []) if line.get("line_id") in trendline_model.get("displayed_line_ids", [])]
    diagonal_channels = [] if not trendline_model else [channel for channel in trendline_model.get("channels", []) if channel.get("channel_id") in trendline_model.get("displayed_channel_ids", [])]
    line_by_id = {line.get("line_id"): line for line in (trendline_model or {}).get("lines", [])}
    displayed_event_ids = (structural_event_model or {}).get("displayed_event_ids", [])
    events_by_id = {event.get("event_id"): event for event in (structural_event_model or {}).get("events", [])}
    event_markers = [events_by_id[event_id] for event_id in displayed_event_ids[:8] if event_id in events_by_id]
    event_positions: list[tuple[dict[str, Any], int]] = []
    for event in event_markers:
        event_time = event.get("event_timestamp_utc")
        marker_index = next((index for index, candle in enumerate(candles) if candle.get("endpoint_utc") == event_time), None)
        if marker_index is not None:
            event_positions.append((event, marker_index))
            numbers.append(float(event["price"]))
    for line in diagonal_lines:
        anchor_index = next((index for index, candle in enumerate(candles) if candle["timestamp_utc"] == line.get("anchor_1_timestamp")), None)
        if anchor_index is not None:
            numbers.extend(line["anchor_1_price"] + line["slope_per_4h_bar"] * (index - anchor_index) for index in range(anchor_index, len(candles)))
    for channel in diagonal_channels:
        base = line_by_id.get(channel.get("base_line_id"))
        if base is not None:
            anchor_index = next((index for index, candle in enumerate(candles) if candle["timestamp_utc"] == base.get("anchor_1_timestamp")), None)
            if anchor_index is not None:
                offset = channel["width_at_cutoff"] if base["kind"] == "ascending_support" else -channel["width_at_cutoff"]
                numbers.extend(base["anchor_1_price"] + base["slope_per_4h_bar"] * (index - anchor_index) + delta for index in range(anchor_index, len(candles)) for delta in (0, offset))
    low, high = min(numbers), max(numbers)
    span = max(high - low, 1.0)
    low -= span * 0.08; high += span * 0.08
    x = lambda index: pad + (index + 0.5) * (width - 2 * pad) / max(len(candles), 1)
    y = lambda value: pad + (high - value) / (high - low) * (height - 2 * pad)
    candle_svg: list[str] = []
    for index, candle in enumerate(candles):
        color = "#168253" if candle["close"] >= candle["open"] else "#b3261e"
        cx = x(index); yo, yc = y(candle["open"]), y(candle["close"])
        candle_svg.append(f'<line x1="{cx:.2f}" y1="{y(candle["high"]):.2f}" x2="{cx:.2f}" y2="{y(candle["low"]):.2f}" stroke="{color}"/><rect x="{cx-2.5:.2f}" y="{min(yo,yc):.2f}" width="5" height="{max(abs(yo-yc),1):.2f}" fill="{color}"/>')
    bands: list[str] = []
    for item in overlays:
        color = "#2563eb" if item["role"] == "support" else "#dc2626"
        source = item.get("source_label") or _source_label(item.get("source_timeframes"))
        label = html.escape(f'{source} {item["level_id"]} [{item["role"]}, {item["reliability_band"]}, {item["lifecycle"]}] ({", ".join(item["semantic_labels"]) or "zone"})')
        high_y = y(float(item["high"]))
        low_y = y(float(item["low"]))
        bands.append(f'<rect x="{pad}" y="{high_y:.2f}" width="{width-2*pad}" height="{max(low_y-high_y, 1):.2f}" fill="{color}" opacity=".16"/><text x="{pad+5}" y="{y(float(item["center"])):.2f}" font-size="10" fill="{color}">{label}</text>')
    diagonal_svg: list[str] = []
    for line in diagonal_lines:
        anchor_index = next((index for index, candle in enumerate(candles) if candle["timestamp_utc"] == line.get("anchor_1_timestamp")), None)
        if anchor_index is None:
            continue
        end_index = len(candles) - 1
        start_value = float(line["anchor_1_price"])
        end_value = start_value + float(line["slope_per_4h_bar"]) * (end_index - anchor_index)
        color = "#15803d" if line["kind"] == "ascending_support" else "#c2410c"
        dash = ' stroke-dasharray="8 5"' if line["state"] == "broken" else ""
        diagonal_svg.append(f'<line x1="{x(anchor_index):.2f}" y1="{y(start_value):.2f}" x2="{x(end_index):.2f}" y2="{y(end_value):.2f}" stroke="{color}" stroke-width="2"{dash}/><text x="{x(anchor_index)+4:.2f}" y="{y(start_value)-5:.2f}" font-size="10" fill="{color}">{html.escape(line["kind"])} [{html.escape(line["state"])}] anchors={html.escape(line["anchor_1_pivot_id"])}→{html.escape(line["anchor_2_pivot_id"])} touches={line["touch_count"]}</text>')
    for channel in diagonal_channels:
        base = line_by_id.get(channel.get("base_line_id"))
        if base is None:
            continue
        anchor_index = next((index for index, candle in enumerate(candles) if candle["timestamp_utc"] == base.get("anchor_1_timestamp")), None)
        if anchor_index is None:
            continue
        end_index = len(candles) - 1
        base_start = float(base["anchor_1_price"])
        base_end = base_start + float(base["slope_per_4h_bar"]) * (end_index - anchor_index)
        offset = float(channel["width_at_cutoff"]) if base["kind"] == "ascending_support" else -float(channel["width_at_cutoff"])
        color = "#64748b"
        diagonal_svg.append(f'<line x1="{x(anchor_index):.2f}" y1="{y(base_start + offset):.2f}" x2="{x(end_index):.2f}" y2="{y(base_end + offset):.2f}" stroke="{color}" stroke-width="1"/><text x="{x(anchor_index)+4:.2f}" y="{y(base_start + offset)-5:.2f}" font-size="10" fill="{color}">{html.escape(channel["kind"])} [{html.escape(channel["state"])}] position={channel["current_position_percent"]:.1f}%</text>')
    price_line = f'<line x1="{pad}" y1="{y(price):.2f}" x2="{width-pad}" y2="{y(price):.2f}" stroke="#111" stroke-dasharray="5 4"/><text x="{width-pad-145}" y="{y(price)-4:.2f}" font-size="10">current price={price:g}</text>'
    markers = "".join(f'<circle cx="{x(index):.2f}" cy="{y(float(event["price"])):.2f}" r="4" fill="#7c3aed"/><text x="{x(index)+5:.2f}" y="{y(float(event["price"]))-6:.2f}" font-size="9" fill="#5b21b6">{html.escape(str(event["event_type"]))} {html.escape(str(event["event_id"])[:8])}</text>' for event, index in event_positions)
    first_at = candles[0]["timestamp_utc"] if candles else "none"
    last_at = candles[-1]["timestamp_utc"] if candles else "none"
    context = f'<text x="{pad}" y="{height-20}" font-size="10">min={low:.4f} max={high:.4f} · candles={len(candles)} · first={html.escape(first_at)} · last={html.escape(last_at)} · cutoff={html.escape(cutoff)}</text>'
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(timeframe)} macro structure candlestick chart"><rect width="{width}" height="{height}" fill="#fff"/> <text x="{pad}" y="22" font-size="15">{html.escape(timeframe)} macro structure chart · cutoff {html.escape(cutoff)}</text><text x="5" y="{pad}" font-size="10">{high:.4f}</text><text x="5" y="{height-pad}" font-size="10">{low:.4f}</text>{"".join(bands)}{"".join(diagonal_svg)}{"".join(candle_svg)}{markers}{price_line}{context}</svg>'


def _diagonal_evidence_html(model: dict[str, Any]) -> str:
    rows = []
    for line in model.get("lines", []):
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(line.get(field, '')))}</td>" for field in ("line_id", "kind", "state", "anchor_1_pivot_id", "anchor_2_pivot_id", "confirmation_timestamp", "slope_per_4h_bar", "touch_count", "break_timestamp", "distance_from_price_atr")) + "</tr>")
    for channel in model.get("channels", []):
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(channel.get(field, '')))}</td>" for field in ("channel_id", "kind", "state", "base_line_id", "opposite_anchor_pivot_id", "confirmation_timestamp", "", "", "", "current_position_percent")) + "</tr>")
    headers = ("id", "kind", "state", "anchor 1/base", "anchor 2/opposite", "confirmation", "slope", "touch count", "break time", "distance ATR")
    body = "".join(rows) or '<tr><td colspan="10">none</td></tr>'
    status = "" if model.get("status") == "ok" else "<p>Diagonal structure: insufficient confirmed 4H evidence</p>"
    return f'<section id="diagonal-evidence"><h2>Diagonal structure evidence</h2><p>status={html.escape(str(model.get("status", "")))} · method={html.escape(str(model.get("method_version", "")))}</p>{status}<table><thead><tr>{"".join(f"<th>{html.escape(field)}</th>" for field in headers)}</tr></thead><tbody>{body}</tbody></table></section>'


def _structural_event_html(model: dict[str, Any]) -> str:
    displayed = set(model.get("displayed_event_ids", []))
    events = [event for event in model.get("events", []) if event.get("event_id") in displayed]
    rows = []
    for event in events:
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(event.get(field, '')))}</td>" for field in ("event_id", "event_type", "event_timestamp_utc", "event_status", "object_kind", "object_id", "direction", "sequence_status", "parent_event_id", "interaction_count")) + "</tr>")
    body = "".join(rows) or '<tr><td colspan="10">none</td></tr>'
    headers = ("event id", "type", "event time", "status", "object kind", "object id", "direction", "sequence", "parent", "touch count")
    return f'<section id="structural-events"><h2>Structural events</h2><p>status={html.escape(str(model.get("status", "")))} · method={html.escape(str(model.get("method_version", "")))} · evidence is retained only at or before cutoff.</p><p class="safety">structural event is evidence, not execution permission. Report-only; no automatic order; human decides manually.</p><table><thead><tr>{"".join(f"<th>{html.escape(field)}</th>" for field in headers)}</tr></thead><tbody>{body}</tbody></table></section>'


def _scenario_html(model: dict[str, Any]) -> str:
    rows = []
    for scenario in model.get("scenarios", []):
        rows.append(f'<article><h3>{html.escape(str(scenario.get("scenario_type", "")))} · {html.escape(str(scenario.get("scenario_status", "")))} · {html.escape(str(scenario.get("direction", "")))}</h3><p>primary={html.escape(str(scenario.get("primary_object_kind", "")))}:{html.escape(str(scenario.get("primary_object_id", "")))} · trigger={html.escape(str(scenario.get("trigger_timestamp_utc", "")))}</p><p>condition: {html.escape(str(scenario.get("condition_text", "")))}</p><p>next confirmation: {html.escape(str(scenario.get("next_confirmation_text", "")))}</p><p>invalidation: {html.escape(str(scenario.get("invalidation_text", "")))}</p><p>supporting event IDs: {html.escape(", ".join(scenario.get("supporting_event_ids", [])))}</p></article>')
    if not rows:
        rows.append('<p>Scenario hypotheses: insufficient current structural evidence</p>')
    return f'<section id="scenario-hypotheses"><h2>Scenario hypotheses</h2><p>status={html.escape(str(model.get("status", "")))} · dominant direction={html.escape(str(model.get("dominant_direction", "")))} · suppressed opposite-direction candidates={html.escape(str(model.get("suppressed_candidate_count", 0)))}</p>{"".join(rows)}<p class="safety">scenario is conditional evidence, not execution permission</p><p class="safety">report-only / no automatic order / human decides manually</p></section>'


EVENT_CATEGORIES = (
    "structure_location_changes", "reliability_changes", "role_changes", "lifecycle_changes",
    "geometry_changes", "absent_from_latest", "reappearances", "stale_or_discontinuous_evaluations",
)


def _categorized_events(history: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result = {category: [] for category in EVENT_CATEGORIES}
    for row in history.get("structure_changes", []):
        if row.get("change_type") == "no_previous_transition":
            continue
        field = _text(row.get("field"))
        change_type = _text(row.get("change_type"))
        if change_type in {"absent_from_latest"}:
            category = "absent_from_latest"
        elif change_type == "reappeared":
            category = "reappearances"
        elif field == "reliability_band":
            category = "reliability_changes"
        elif field == "role":
            category = "role_changes"
        elif field == "lifecycle":
            category = "lifecycle_changes"
        elif field == "geometry":
            category = "geometry_changes"
        elif change_type == "snapshot_transition" and field in {"structure_state", "price_location", "location_percentile", "current_price"}:
            category = "structure_location_changes"
        else:
            continue
        result[category].append({"source": "macro_structure_changes.csv", **row})
    for row in history.get("evaluation_history", []):
        if row.get("stale_status") == "stale" or row.get("continuity_status") == "discontinuous":
            result["stale_or_discontinuous_evaluations"].append({"source": "evaluation_history", **row})
    for category in result:
        result[category] = result[category][-10:]
    return result


def _event_text(row: dict[str, Any]) -> str:
    if row.get("source") == "evaluation_history":
        return f'run={row.get("run_id", "")} evaluated={row.get("evaluated_at_utc", "")} stale={row.get("stale_status", "")} continuity={row.get("continuity_status", "")} data_quality={row.get("data_quality_status", "")}'
    return f'checkpoint={row.get("checkpoint_id", "")} level={row.get("level_id") or "snapshot"} {row.get("field", row.get("change_type", "change"))}: {row.get("previous_value", "")} -> {row.get("current_value", "")}'


def _render_markdown(model: dict[str, Any]) -> str:
    structure = model["structure_panel"]
    zone_lines = [f'- {item["role"]} `{item["level_id"]}`: {item["reliability_band"]}, lifecycle={item["lifecycle"]}' for item in model["zones"]["support_zones"] + model["zones"]["resistance_zones"]] or ["- none"]
    event_lines: list[str] = []
    for category in EVENT_CATEGORIES:
        event_lines.append(f"### {category}")
        event_lines.extend(f'- {_event_text(row)}' for row in model["chronological_changes"]["categories"].get(category, []))
        if not model["chronological_changes"]["categories"].get(category):
            event_lines.append("- none")
    return "\n".join([
        "# Macro Structure Chart-First Operator Artifact", "", "## Source identities", "",
        f'- snapshot run: `{model["selected_snapshot_run_id"]}`', f'- snapshot ID: `{model["selected_snapshot_id"]}`', f'- history ID: `{model["selected_history_id"]}`', "",
        "## Visible status", "", f'- {model["symbol"]} / cutoff `{model["as_of_utc"]}` / evaluation `{model["evaluated_at_utc"]}`', f'- structure: `{structure["structure_state"]}` / location: `{structure["price_location"]}`', f'- stale: `{model["freshness"]["stale_status"]}` / continuity: `{model["source_status"]["continuity_status"]}`', f'- snapshot result: `{model["source_status"]["snapshot_result_status"]}` / history result: `{model["source_status"]["history_result_status"]}`', "",
        "## Chart-first hierarchy", "", "status and safety banner > primary 15m candlestick chart > reliable zones > current structure/location > targets/obstruction > volatility/freshness/continuity > chronological changes > evidence/limitations", "",
        "## Displayed zones", "", *zone_lines, "",
        "## Recent history", "", *event_lines, "",
        "## Limitations", "", "- macro evidence only; tactical Entry / SL / TP overlays are not included.", "- no live fetch, private inputs, future candles, or execution permission.", "",
        "## Safety boundary", "", SAFETY, "",
    ])


def _zone_evidence_html(zones: list[dict[str, Any]]) -> str:
    headers = ("level_id", "side", "role", "low", "high", "center", "source_timeframes", "first_seen_at", "last_confirmed_at", "touch_count", "clean_rejection_count", "break_count", "false_break_reclaim_count", "lifecycle", "reliability_score", "reliability_band", "distance_from_price_pct", "distance_from_price_atr", "reason_codes")
    rows = []
    for item in zones:
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in headers) + "</tr>")
    return "<table><thead><tr>" + "".join(f"<th>{html.escape(field)}</th>" for field in headers) + "</tr></thead><tbody>" + ("".join(rows) or "<tr><td colspan=19>none</td></tr>") + "</tbody></table>"


def _publish(output_root: Path, artifact_id: str, files: dict[str, bytes], latest: dict[str, Any], before_latest: Callable[[Path], None] | None = None) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    target = output_root / artifact_id
    stage = Path(tempfile.mkdtemp(prefix=".macro-operator-", dir=output_root))
    try:
        for name, content in files.items():
            (stage / name).write_bytes(content)
        if target.exists():
            if not target.is_dir() or not all((target / name).is_file() for name in OUTPUT_NAMES):
                raise OSError("incomplete_existing_operator")
            if any((target / name).read_bytes() != (stage / name).read_bytes() for name in OUTPUT_NAMES):
                raise OSError("existing_operator_conflict")
            shutil.rmtree(stage)
        else:
            stage.replace(target)
        if before_latest is not None:
            before_latest(target)
        latest_stage = output_root / ".latest.json.tmp"
        latest_stage.write_bytes(_compact_json_bytes(latest))
        latest_stage.replace(output_root / "latest.json")
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def render_macro_structure_operator(*, snapshot_root: Path = Path("local/reports/macro_structure"), history_root: Path = Path("local/reports/macro_structure/history"), ohlcv_15m_csv: Path, ohlcv_4h_csv: Path | None = None, output_root: Path = Path("local/reports/macro_structure/operator"), symbol: str = "BTC_USDT") -> dict[str, Any]:
    has_4h_input = ohlcv_4h_csv is not None
    latest_entry_info: dict[str, Any] = {}
    try:
        snapshot, snapshot_manifest, snapshot_dir, snapshot_fingerprints = _validate_snapshot(snapshot_root, symbol)
        history, history_manifest, history_dir, history_fingerprints = _validate_history(history_root, symbol, snapshot)
        candles, ohlcv_fingerprint = _read_ohlcv(ohlcv_15m_csv, symbol, snapshot["_as_of"], _number(snapshot["current_price"], "snapshot_price_invalid"))
        candles_4h: list[dict[str, Any]] = []
        ohlcv_4h_fingerprint: str | None = None
        if ohlcv_4h_csv is not None:
            candles_4h, ohlcv_4h_fingerprint = _read_ohlcv(ohlcv_4h_csv, symbol, snapshot["_as_of"], _number(snapshot["current_price"], "snapshot_price_invalid"), interval="4h", limit=240, match_close=False)
        trendline_model = build_trendline_model(candles_4h, cutoff=snapshot["_as_of"], current_price=_number(snapshot["current_price"], "snapshot_price_invalid")) if candles_4h else None
        support, resistance, shown = _zones(snapshot)
        structural_event_model = build_structural_event_model(candles_4h, cutoff=snapshot["_as_of"], current_price=_number(snapshot["current_price"], "snapshot_price_invalid"), zones=shown, trendline_model=trendline_model) if candles_4h else None
        scenario_model = build_scenario_model(cutoff=snapshot["_as_of"], current_price=_number(snapshot["current_price"], "snapshot_price_invalid"), structure_state=str(snapshot.get("structure_state", "")), price_location=str(snapshot.get("price_location", "")), zones=shown, trendline_model=trendline_model, structural_event_model=structural_event_model) if candles_4h else None
        references = _references(snapshot, shown)
        categories = _categorized_events(history)
        trace: dict[str, Any] = {
            "status": {field: {"source": "M-OPS1 macro_structure_snapshot.json", "field": field} for field in ("symbol", "as_of_utc", "as_of_jst", "evaluated_at_utc", "evaluated_at_jst", "current_price", "structure_state", "price_location", "result_status", "stale_status", "continuity_status", "data_quality_status", "safety_boundary")},
            "candles": {"source": "explicit local public 15m OHLCV CSV", "rule": "timestamp plus 15m endpoint <= snapshot as_of_utc; latest 96 eligible closed candles", "cutoff": snapshot["_as_of"].isoformat()},
            "zones": {item["level_id"]: {"source": "M-OPS1 macro_structure_snapshot.json", "field": "support_zones/resistance_zones", "level_id": item["level_id"]} for item in shown},
            "references": {item["level_id"]: {"source": "M-OPS1 macro_structure_snapshot.json", "field": item["semantic_labels"], "level_id": item["level_id"]} for item in references if item["semantic_labels"]},
            "events": {category: [{"source": "macro_structure_history.json.structure_changes" if row.get("source") == "macro_structure_changes.csv" else row.get("source", ""), "checkpoint_id": row.get("checkpoint_id", ""), "run_id": row.get("run_id", ""), "level_id": row.get("level_id", "")} for row in rows] for category, rows in categories.items()},
            "presentation_rules": {"geometry": "deduplicate by level_id and annotate accepted semantic labels", "zones": "display only high/medium accepted reliability bands", "events": "accepted M-OPS2 v2 rows, latest ten per category"},
        }
        if candles_4h:
            trace["candles_4h"] = {"source": "explicit local public 4h OHLCV CSV", "rule": "timestamp plus 4h endpoint <= snapshot as_of_utc; latest 240 eligible closed candles", "cutoff": snapshot["_as_of"].isoformat()}
        chart = {"timeframe": "15m", "candle_count": len(candles), "candles": candles, "current_price": snapshot["current_price"], "cutoff_utc": snapshot["_as_of"].isoformat(), "first_displayed_timestamp_utc": candles[0]["timestamp_utc"], "last_displayed_timestamp_utc": candles[-1]["timestamp_utc"], "overlays": references}
        chart_4h = {"timeframe": "4H", "model": "mvis1_4h_candlestick_operator", "candle_count": len(candles_4h), "candles": candles_4h, "current_price": snapshot["current_price"], "cutoff_utc": snapshot["_as_of"].isoformat(), "first_displayed_timestamp_utc": candles_4h[0]["timestamp_utc"], "last_displayed_timestamp_utc": candles_4h[-1]["timestamp_utc"], "overlays": references, "trendline_model": trendline_model} if candles_4h else None
        counts = {f"{role}_{band}": sum(1 for item in zones if item["role"] == role and item["reliability_band"] == band) for role, zones in (("support", support), ("resistance", resistance)) for band in ("high", "medium")}
        counts.update({"total_displayed_support": len(support), "total_displayed_resistance": len(resistance)})
        model = {
            "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "symbol": symbol,
            "operator_artifact_id": "", "selected_snapshot_run_id": snapshot["run_id"], "selected_snapshot_id": snapshot["snapshot_id"], "selected_history_id": history["history_id"], "selected_structural_checkpoint_id": snapshot["_checkpoint_id"],
            "snapshot_fingerprint": snapshot_fingerprints, "history_fingerprint": history_fingerprints, "ohlcv_15m_fingerprint": ohlcv_fingerprint, **({"ohlcv_4h_fingerprint": ohlcv_4h_fingerprint} if ohlcv_4h_fingerprint else {}),
            "as_of_utc": snapshot["_as_of"].isoformat(), "as_of_jst": snapshot.get("as_of_jst", ""), "evaluated_at_utc": snapshot["_evaluated"].isoformat(), "evaluated_at_jst": snapshot.get("evaluated_at_jst", ""),
            "chart_model": chart, **({"chart_model_4h": chart_4h, "trendline_model": trendline_model, "structural_event_model": structural_event_model, "scenario_model": scenario_model} if chart_4h else {}), "zones": {"support_zones": support, "resistance_zones": resistance, "displayed_support_count": len(support), "displayed_resistance_count": len(resistance), "counts_by_role_and_band": counts},
            "structure_panel": {field: snapshot.get(field, "") for field in ("structure_state", "price_location", "location_percentile", "current_price", "nearest_reliable_support", "nearest_reliable_resistance", "next_upside_target", "next_downside_target", "upside_obstruction", "downside_obstruction", "volatility_state", "expansion_risk", "directional_activation")},
            "freshness": {"stale_status": snapshot.get("stale_status", ""), "stale_timeframes": snapshot.get("stale_timeframes", []), "freshness": snapshot.get("freshness", {})},
            "source_status": {"snapshot_result_status": snapshot.get("result_status", ""), "history_result_status": history.get("result_status", ""), "continuity_status": snapshot.get("continuity_status", ""), "data_quality_status": snapshot.get("data_quality_status", ""), "reason_codes": snapshot.get("reason_codes", [])},
            "chronological_changes": {"categories": categories, "source": "macro_structure_changes.csv and evaluation_history", "limit": 10},
            "missing_or_insufficient_flags": sorted(set(snapshot.get("reason_codes", [])) | ({"insufficient_snapshot"} if snapshot.get("result_status") == "insufficient" else set()) | ({"insufficient_history"} if history.get("result_status") == "insufficient_history" else set())),
            "source_trace_map": trace,
            "safety_boundary": SAFETY,
        }
        digest_payload = {"snapshot": snapshot_fingerprints, "history": history_fingerprints, "ohlcv_15m": ohlcv_fingerprint, "ohlcv_4h": ohlcv_4h_fingerprint}
        if trendline_model is not None:
            digest_payload["trendline_method_version"] = TRENDLINE_METHOD_VERSION
        if structural_event_model is not None:
            digest_payload["structural_event_method_version"] = STRUCTURAL_EVENT_METHOD_VERSION
        if scenario_model is not None:
            digest_payload["scenario_method_version"] = SCENARIO_METHOD_VERSION
        digest = hashlib.sha256((SCHEMA_VERSION + "|" + METHOD_VERSION + "|" + symbol + "|" + json.dumps(digest_payload, sort_keys=True)).encode()).hexdigest()
        artifact_id = "operator_" + digest[:20]
        model["operator_artifact_id"] = artifact_id
        svg = _svg(candles, float(snapshot["current_price"]), references, model["as_of_utc"])
        svg_4h = _svg(candles_4h, float(snapshot["current_price"]), references, model["as_of_utc"], timeframe="4H", trendline_model=trendline_model, structural_event_model=structural_event_model) if candles_4h else ""
        banner = f'<section id="status"><h1>Macro Structure Chart-First Operator</h1><p class="safety">{html.escape(SAFETY)}</p><p>symbol={html.escape(symbol)} · checkpoint={html.escape(snapshot["_checkpoint_id"])} · cutoff UTC={html.escape(model["as_of_utc"])} · cutoff JST={html.escape(model["as_of_jst"])} · evaluation UTC={html.escape(model["evaluated_at_utc"])} · evaluation JST={html.escape(model["evaluated_at_jst"])}</p><p>price={html.escape(str(snapshot["current_price"]))} · structure={html.escape(str(snapshot["structure_state"]))} · location={html.escape(str(snapshot["price_location"]))} · stale={html.escape(str(snapshot["stale_status"]))} · continuity={html.escape(str(snapshot["continuity_status"]))} · data_quality={html.escape(str(snapshot["data_quality_status"]))} · snapshot={html.escape(str(snapshot.get("result_status", "")))} · history={html.escape(str(history.get("result_status", "")))}</p></section>'
        evidence_by_id = {item["level_id"]: item for item in support + resistance}
        evidence_by_id.update({item["level_id"]: item for item in references})
        zones_html = _zone_evidence_html([evidence_by_id[key] for key in sorted(evidence_by_id)])
        structure_html = "<ul>" + "".join(f"<li><b>{html.escape(key)}</b>: {html.escape(json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict,list)) else str(value))}</li>" for key, value in model["structure_panel"].items()) + "</ul>"
        event_html = "".join(f'<h3>{html.escape(category)}</h3><ul>{("".join(f"<li>{html.escape(_event_text(row))}</li>" for row in rows) or "<li>none</li>")}</ul>' for category, rows in categories.items())
        primary = f'<section id="chart-4h"><h2>4H Macro Structure Chart</h2><p>current price={html.escape(str(snapshot["current_price"]))} · cutoff={html.escape(model["as_of_utc"])} · displayed candles={len(candles_4h)} · range={html.escape(candles_4h[0]["timestamp_utc"])} → {html.escape(candles_4h[-1]["endpoint_utc"])}</p>{svg_4h}</section>{_diagonal_evidence_html(trendline_model)}' if candles_4h else ''
        structural_events_html = _structural_event_html(structural_event_model) if structural_event_model is not None else ''
        scenario_html = _scenario_html(scenario_model) if scenario_model is not None else ''
        supplemental = f'<section id="chart"><h2>Supplemental 15m manual-confirmation view</h2>{svg}</section>'
        html_text = f'<!doctype html><html><head><meta charset="utf-8"><style>body{{font:14px sans-serif;margin:20px;color:#172033}}section{{margin:16px 0;padding:12px;border:1px solid #d8deea}}article{{margin:8px 0;padding:8px;background:#f5f7fb}}.safety{{color:#7a1520;font-weight:600}}svg{{width:100%;height:auto}}table{{border-collapse:collapse;display:block;overflow:auto;font-size:11px}}th,td{{border:1px solid #ccd3df;padding:3px;white-space:nowrap}}</style></head><body>{banner}{primary}{structural_events_html}{scenario_html}<section id="zones"><h2>Reliable support/resistance evidence</h2>{zones_html}</section><section id="structure"><h2>Current structure and location</h2>{structure_html}<p class="safety">directional activation is evidence confidence, not execution permission.</p></section>{supplemental}<section id="status-detail"><h2>Volatility, activation, freshness, continuity</h2><pre>{html.escape(json.dumps({**model["freshness"], "volatility_state": snapshot.get("volatility_state"), "expansion_risk": snapshot.get("expansion_risk"), "directional_activation": snapshot.get("directional_activation")}, ensure_ascii=False, sort_keys=True, indent=2))}</pre></section><section id="changes"><h2>Recent chronological changes</h2>{event_html}</section><section id="evidence"><h2>Evidence details and limitations</h2><p>tactical Entry / SL / TP overlays are not included. No live fetch, private inputs, or execution permission.</p></section></body></html>'
        markdown = _render_markdown(model)
        files = {"macro_structure_operator.html": html_text.encode("utf-8"), "macro_structure_operator.json": _json_bytes(model), "macro_structure_operator.md": markdown.encode("utf-8")}
        model_identity = {"trendline_method_version": TRENDLINE_METHOD_VERSION, "structural_event_method_version": STRUCTURAL_EVENT_METHOD_VERSION, "scenario_method_version": SCENARIO_METHOD_VERSION} if trendline_model is not None else {}
        manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "operator_artifact_id": artifact_id, "symbol": symbol, "selected_snapshot_run_id": snapshot["run_id"], "selected_snapshot_id": snapshot["snapshot_id"], "selected_structural_checkpoint_id": snapshot["_checkpoint_id"], "selected_history_id": history["history_id"], "input_fingerprints": {"snapshot": snapshot_fingerprints, "history": history_fingerprints, "ohlcv_15m": ohlcv_fingerprint, **({"ohlcv_4h": ohlcv_4h_fingerprint} if ohlcv_4h_fingerprint else {})}, "model_identity": model_identity, "outputs": list(OUTPUT_NAMES), "source": "accepted_mops1_snapshot_mops2_v2_history_and_explicit_public_ohlcv", "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
        files["run_manifest.json"] = _json_bytes(manifest)
        latest_snapshot_result = snapshot.get("result_status", "")
        latest_history_result = history.get("result_status", "")
        latest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "operator_artifact_id": artifact_id, "artifact_dir": artifact_id, "symbol": symbol, "selected_snapshot_run_id": snapshot["run_id"], "selected_snapshot_id": snapshot["snapshot_id"], "selected_history_id": history["history_id"], "selected_structural_checkpoint_id": snapshot["_checkpoint_id"], "as_of_utc": model["as_of_utc"], "as_of_jst": model["as_of_jst"], "evaluated_at_utc": model["evaluated_at_utc"], "evaluated_at_jst": model["evaluated_at_jst"], "structure_state": snapshot["structure_state"], "price_location": snapshot["price_location"], "snapshot_result_status": latest_snapshot_result, "history_result_status": latest_history_result, "latest_snapshot_result_status": latest_snapshot_result, "latest_history_result_status": latest_history_result, "data_quality_status": snapshot.get("data_quality_status", ""), "displayed_support_count": len(support), "displayed_resistance_count": len(resistance), "displayed_zone_counts": counts, "stale_status": snapshot.get("stale_status", ""), "continuity_status": snapshot.get("continuity_status", ""), "source_digest": digest, "safety_boundary": SAFETY}
        def _publish_entry(source_dir: Path) -> None:
            latest_entry_info.update(publish_available_entry(output_root=output_root, source_dir=source_dir, artifact_id=artifact_id, source_digest=digest, metadata={"as_of_utc": model["as_of_utc"], "as_of_jst": model["as_of_jst"], "evaluated_at_utc": model["evaluated_at_utc"], "evaluated_at_jst": model["evaluated_at_jst"], "stale_status": snapshot.get("stale_status", ""), "continuity_status": snapshot.get("continuity_status", ""), "data_quality_status": snapshot.get("data_quality_status", ""), "safety_boundary": SAFETY}))
        _publish(output_root, artifact_id, files, latest, before_latest=_publish_entry if has_4h_input else None)
        return {"ok": True, "exit_code": 0, **latest, **latest_entry_info, "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False}
    except LatestEntryPublicationError:
        return {"ok": False, "exit_code": 2, "error_code": "latest_entry_publication_failed", "report_written": False, "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
    except (OSError, ValueError) as exc:
        result = {"ok": False, "exit_code": 2, "error_code": str(exc), "report_written": False, "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
        if has_4h_input:
            try:
                result.update(publish_unavailable_entry(output_root=output_root, error_code=str(exc)))
            except LatestEntryPublicationError:
                result["error_code"] = "latest_entry_publication_failed"
            except (OSError, ValueError):
                pass
        return result
