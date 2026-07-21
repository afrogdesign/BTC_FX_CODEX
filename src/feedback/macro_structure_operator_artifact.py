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
from typing import Any

SCHEMA_VERSION = "macro_structure_operator_artifact.v1"
METHOD_VERSION = "macro_structure_operator_artifact.v1"
M1_SCHEMA_VERSION = "macro_structure_daily_operation.v1"
M2_SCHEMA_VERSION = "macro_structure_history_operation.v2"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
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
    if _utc(manifest.get("as_of_utc"), "snapshot_manifest_timestamp_invalid") != as_of or _utc(manifest.get("evaluated_at_utc"), "snapshot_manifest_timestamp_invalid") != evaluated:
        raise ValueError("snapshot_timestamp_mismatch")
    required = ("structure_state", "price_location", "current_price", "stale_status", "continuity_status", "data_quality_status", "reason_codes", "support_zones", "resistance_zones", "nearest_reliable_support", "nearest_reliable_resistance", "next_upside_target", "next_downside_target", "upside_obstruction", "downside_obstruction", "volatility_state", "expansion_risk", "directional_activation", "safety_boundary")
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
    checkpoints = [item for item in history.get("structural_checkpoints", []) if item.get("checkpoint_id") == checkpoint_id]
    if not checkpoints:
        raise ValueError("history_checkpoint_missing")
    checkpoint = checkpoints[0]
    latest_checkpoint_evaluation = checkpoint.get("latest_evaluation", {}) if isinstance(checkpoint.get("latest_evaluation"), dict) else {}
    if _text(checkpoint.get("latest_evaluation_run_id") or latest_checkpoint_evaluation.get("run_id")) != run_id:
        raise ValueError("history_current_snapshot_not_latest_evaluation")
    fingerprints = {"history": _fingerprint(history_dir / "macro_structure_history.json"), "history_snapshots": _fingerprint(history_dir / "macro_snapshot_history.csv"), "history_levels": _fingerprint(history_dir / "macro_level_history.csv"), "history_changes": _fingerprint(history_dir / "macro_structure_changes.csv"), "history_manifest": _fingerprint(history_dir / "run_manifest.json")}
    return history, manifest, history_dir, fingerprints


def _read_ohlcv(path: Path, symbol: str, cutoff: datetime, expected_close: float) -> tuple[list[dict[str, Any]], str]:
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
        if _text(raw.get("interval")) and _text(raw.get("interval")) != "15m":
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
        endpoint = at + timedelta(minutes=15)
        if endpoint <= cutoff:
            eligible.append({"timestamp_utc": at.isoformat(), "endpoint_utc": endpoint.isoformat(), **values})
    if not eligible:
        raise ValueError("ohlcv_no_closed_candle")
    if abs(eligible[-1]["close"] - expected_close) > max(1e-8, abs(expected_close) * 1e-8):
        raise ValueError("snapshot_price_ohlcv_mismatch")
    return eligible[-96:], _fingerprint(path)


def _zone(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict) or not _text(value.get("level_id")):
        return None
    return {field: value.get(field, "") for field in ZONE_FIELDS}


def _zones(snapshot: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    def ordered(values: Any) -> list[dict[str, Any]]:
        items = [item for item in (_zone(value) for value in values or []) if item is not None]
        return sorted(items, key=lambda item: (-{"high": 2, "medium": 1}.get(_text(item["reliability_band"]), 0), _number(item["distance_from_price_pct"] or 0, "zone_distance_invalid"), _text(item["level_id"])))
    support = ordered(snapshot.get("support_zones"))
    resistance = ordered(snapshot.get("resistance_zones"))
    support = [item for item in support if _text(item["reliability_band"]) in {"high", "medium"}]
    resistance = [item for item in resistance if _text(item["reliability_band"]) in {"high", "medium"}]
    return support, resistance, support + resistance


def _references(snapshot: dict[str, Any], shown: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["level_id"]: item for item in shown}
    references: list[dict[str, Any]] = []
    for semantic, field in (("nearest_support", "nearest_reliable_support"), ("nearest_resistance", "nearest_reliable_resistance"), ("upside_target", "next_upside_target"), ("downside_target", "next_downside_target"), ("upside_obstruction", "upside_obstruction"), ("downside_obstruction", "downside_obstruction")):
        value = snapshot.get(field)
        item = _zone(value)
        if item and item["level_id"] in by_id:
            references.append({"level_id": item["level_id"], "semantic": semantic, "low": item["low"], "high": item["high"], "center": item["center"]})
    unique: dict[str, dict[str, Any]] = {}
    for item in references:
        unique.setdefault(item["level_id"], {**item, "semantic_labels": []})["semantic_labels"].append(item["semantic"])
    for item in unique.values():
        item["semantic_labels"] = sorted(item["semantic_labels"])
    return [unique[key] for key in sorted(unique)]


def _svg(candles: list[dict[str, Any]], price: float, overlays: list[dict[str, Any]]) -> str:
    width, height, pad = 1100, 480, 46
    numbers = [price] + [n for candle in candles for n in (candle["low"], candle["high"])] + [n for item in overlays for n in (float(item["low"]), float(item["high"]))]
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
        color = "#2563eb" if "support" in item["semantic_labels"] else "#dc2626"
        label = html.escape(f'{item["level_id"]} ({", ".join(item["semantic_labels"])})')
        high_y = y(float(item["high"]))
        low_y = y(float(item["low"]))
        bands.append(f'<rect x="{pad}" y="{high_y:.2f}" width="{width-2*pad}" height="{max(low_y-high_y, 1):.2f}" fill="{color}" opacity=".16"/><text x="{pad+5}" y="{y(float(item["center"])):.2f}" font-size="10" fill="{color}">{label}</text>')
    price_line = f'<line x1="{pad}" y1="{y(price):.2f}" x2="{width-pad}" y2="{y(price):.2f}" stroke="#111" stroke-dasharray="5 4"/><text x="{width-pad-90}" y="{y(price)-4:.2f}" font-size="10">current price</text>'
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="15 minute macro structure candlestick chart"><rect width="{width}" height="{height}" fill="#fff"/> <text x="{pad}" y="22" font-size="15">15m macro structure chart</text>{"".join(bands)}{"".join(candle_svg)}{price_line}</svg>'


def _event_lines(history: dict[str, Any]) -> list[str]:
    changes = history.get("structure_changes", [])
    selected = [row for row in changes if row.get("change_type") != "no_previous_transition"][-10:]
    evaluations = [row for row in history.get("evaluation_history", []) if row.get("stale_status") == "stale" or row.get("continuity_status") == "discontinuous"][-10:]
    lines = [f'{row.get("change_type", "change")}: {row.get("level_id") or row.get("field", "snapshot")} ({row.get("previous_value", "")} -> {row.get("current_value", "")})' for row in selected]
    lines.extend(f'evaluation {row.get("run_id", "")}: stale={row.get("stale_status", "")}, continuity={row.get("continuity_status", "")}' for row in evaluations)
    return lines[-10:]


def _render_markdown(model: dict[str, Any]) -> str:
    structure = model["structure_panel"]
    events = model["chronological_changes"]["events"]
    zone_lines = [f'- {item["role"]} `{item["level_id"]}`: {item["reliability_band"]}, lifecycle={item["lifecycle"]}' for item in model["zones"]["support_zones"] + model["zones"]["resistance_zones"]] or ["- none"]
    event_lines = [f'- {line}' for line in events] or ["- none"]
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


def _publish(output_root: Path, artifact_id: str, files: dict[str, bytes], latest: dict[str, Any]) -> None:
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
        latest_stage = output_root / ".latest.json.tmp"
        latest_stage.write_bytes(_compact_json_bytes(latest))
        latest_stage.replace(output_root / "latest.json")
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def render_macro_structure_operator(*, snapshot_root: Path = Path("local/reports/macro_structure"), history_root: Path = Path("local/reports/macro_structure/history"), ohlcv_15m_csv: Path, output_root: Path = Path("local/reports/macro_structure/operator"), symbol: str = "BTC_USDT") -> dict[str, Any]:
    try:
        snapshot, snapshot_manifest, snapshot_dir, snapshot_fingerprints = _validate_snapshot(snapshot_root, symbol)
        history, history_manifest, history_dir, history_fingerprints = _validate_history(history_root, symbol, snapshot)
        candles, ohlcv_fingerprint = _read_ohlcv(ohlcv_15m_csv, symbol, snapshot["_as_of"], _number(snapshot["current_price"], "snapshot_price_invalid"))
        support, resistance, shown = _zones(snapshot)
        references = _references(snapshot, shown)
        chart = {"timeframe": "15m", "candle_count": len(candles), "candles": candles, "current_price": snapshot["current_price"], "overlays": references}
        model = {
            "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "symbol": symbol,
            "operator_artifact_id": "", "selected_snapshot_run_id": snapshot["run_id"], "selected_snapshot_id": snapshot["snapshot_id"], "selected_history_id": history["history_id"],
            "snapshot_fingerprint": snapshot_fingerprints, "history_fingerprint": history_fingerprints, "ohlcv_15m_fingerprint": ohlcv_fingerprint,
            "as_of_utc": snapshot["_as_of"].isoformat(), "as_of_jst": snapshot.get("as_of_jst", ""), "evaluated_at_utc": snapshot["_evaluated"].isoformat(), "evaluated_at_jst": snapshot.get("evaluated_at_jst", ""),
            "chart_model": chart, "zones": {"support_zones": support, "resistance_zones": resistance, "displayed_support_count": len(support), "displayed_resistance_count": len(resistance)},
            "structure_panel": {field: snapshot.get(field, "") for field in ("structure_state", "price_location", "location_percentile", "current_price", "nearest_reliable_support", "nearest_reliable_resistance", "next_upside_target", "next_downside_target", "upside_obstruction", "downside_obstruction", "volatility_state", "expansion_risk", "directional_activation")},
            "freshness": {"stale_status": snapshot.get("stale_status", ""), "stale_timeframes": snapshot.get("stale_timeframes", []), "freshness": snapshot.get("freshness", {})},
            "source_status": {"snapshot_result_status": snapshot.get("result_status", ""), "history_result_status": history.get("result_status", ""), "continuity_status": snapshot.get("continuity_status", ""), "data_quality_status": snapshot.get("data_quality_status", ""), "reason_codes": snapshot.get("reason_codes", [])},
            "chronological_changes": {"events": _event_lines(history), "source": "macro_structure_changes.csv and evaluation_history", "limit": 10},
            "missing_or_insufficient_flags": sorted(set(snapshot.get("reason_codes", [])) | ({"insufficient_snapshot"} if snapshot.get("result_status") == "insufficient" else set()) | ({"insufficient_history"} if history.get("result_status") == "insufficient_history" else set())),
            "source_trace_map": {"snapshot": "M-OPS1 snapshot JSON and level CSV", "history": "M-OPS2 v2 history JSON and changes CSV", "ohlcv_15m": "explicit local public OHLCV CSV", "presentation": "deterministic M-OPS3 chart-first rules"},
            "safety_boundary": SAFETY,
        }
        digest = hashlib.sha256((SCHEMA_VERSION + "|" + METHOD_VERSION + "|" + symbol + "|" + json.dumps({"snapshot": snapshot_fingerprints, "history": history_fingerprints, "ohlcv": ohlcv_fingerprint}, sort_keys=True)).encode()).hexdigest()
        artifact_id = "operator_" + digest[:20]
        model["operator_artifact_id"] = artifact_id
        svg = _svg(candles, float(snapshot["current_price"]), references)
        banner = f'<section id="status"><h1>Macro Structure Chart-First Operator</h1><p class="safety">{html.escape(SAFETY)}</p><p>symbol={html.escape(symbol)} · cutoff UTC={html.escape(model["as_of_utc"])} · cutoff JST={html.escape(model["as_of_jst"])} · evaluation UTC={html.escape(model["evaluated_at_utc"])} · evaluation JST={html.escape(model["evaluated_at_jst"])}</p><p>price={html.escape(str(snapshot["current_price"]))} · structure={html.escape(str(snapshot["structure_state"]))} · location={html.escape(str(snapshot["price_location"]))} · stale={html.escape(str(snapshot["stale_status"]))} · continuity={html.escape(str(snapshot["continuity_status"]))} · snapshot={html.escape(str(snapshot.get("result_status", "")))} · history={html.escape(str(history.get("result_status", "")))}</p></section>'
        zones_html = "".join(f'<li>{html.escape(item["role"])} <code>{html.escape(item["level_id"])}</code> · band={html.escape(str(item["reliability_band"]))} · lifecycle={html.escape(str(item["lifecycle"]))}</li>' for item in support + resistance) or "<li>none</li>"
        structure_html = "<ul>" + "".join(f"<li><b>{html.escape(key)}</b>: {html.escape(json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict,list)) else str(value))}</li>" for key, value in model["structure_panel"].items()) + "</ul>"
        html_text = f'<!doctype html><html><head><meta charset="utf-8"><style>body{{font:14px sans-serif;margin:20px;color:#172033}}section{{margin:16px 0;padding:12px;border:1px solid #d8deea}}.safety{{color:#7a1520;font-weight:600}}svg{{width:100%;height:auto}}</style></head><body>{banner}<section id="chart"><h2>Primary 15m chart</h2>{svg}</section><section id="zones"><h2>Reliable support/resistance zones</h2><ul>{zones_html}</ul></section><section id="structure"><h2>Current structure and location</h2>{structure_html}<p class="safety">directional activation is evidence confidence, not execution permission.</p></section><section id="status-detail"><h2>Volatility, activation, freshness, continuity</h2><pre>{html.escape(json.dumps({**model["freshness"], "volatility_state": snapshot.get("volatility_state"), "expansion_risk": snapshot.get("expansion_risk"), "directional_activation": snapshot.get("directional_activation")}, ensure_ascii=False, sort_keys=True, indent=2))}</pre></section><section id="changes"><h2>Recent chronological changes</h2><ul>{"".join(f"<li>{html.escape(line)}</li>" for line in model["chronological_changes"]["events"]) or "<li>none</li>"}</ul></section><section id="evidence"><h2>Evidence details and limitations</h2><p>tactical Entry / SL / TP overlays are not included. No live fetch, private inputs, or execution permission.</p></section></body></html>'
        markdown = _render_markdown(model)
        files = {"macro_structure_operator.html": html_text.encode("utf-8"), "macro_structure_operator.json": _json_bytes(model), "macro_structure_operator.md": markdown.encode("utf-8")}
        manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "operator_artifact_id": artifact_id, "symbol": symbol, "selected_snapshot_run_id": snapshot["run_id"], "selected_snapshot_id": snapshot["snapshot_id"], "selected_history_id": history["history_id"], "input_fingerprints": {"snapshot": snapshot_fingerprints, "history": history_fingerprints, "ohlcv_15m": ohlcv_fingerprint}, "outputs": list(OUTPUT_NAMES), "source": "accepted_mops1_snapshot_mops2_v2_history_and_explicit_public_ohlcv", "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
        files["run_manifest.json"] = _json_bytes(manifest)
        latest_snapshot_result = snapshot.get("result_status", "")
        latest_history_result = history.get("result_status", "")
        latest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "operator_artifact_id": artifact_id, "artifact_dir": artifact_id, "symbol": symbol, "selected_snapshot_run_id": snapshot["run_id"], "selected_snapshot_id": snapshot["snapshot_id"], "selected_history_id": history["history_id"], "as_of_utc": model["as_of_utc"], "as_of_jst": model["as_of_jst"], "evaluated_at_utc": model["evaluated_at_utc"], "evaluated_at_jst": model["evaluated_at_jst"], "structure_state": snapshot["structure_state"], "price_location": snapshot["price_location"], "snapshot_result_status": latest_snapshot_result, "history_result_status": latest_history_result, "latest_snapshot_result_status": latest_snapshot_result, "latest_history_result_status": latest_history_result, "displayed_support_count": len(support), "displayed_resistance_count": len(resistance), "stale_status": snapshot.get("stale_status", ""), "continuity_status": snapshot.get("continuity_status", ""), "source_digest": digest, "safety_boundary": SAFETY}
        _publish(output_root, artifact_id, files, latest)
        return {"ok": True, "exit_code": 0, **latest, "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False}
    except (OSError, ValueError) as exc:
        return {"ok": False, "exit_code": 2, "error_code": str(exc), "report_written": False, "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
