"""Report-only current macro structure operation.

This adapter reuses the accepted M1 event-time level and volatility helpers.
It has no signal, account, actual-trade, notification, runtime, or order
inputs and publishes only local operator evidence.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from src.data.fetcher import FetchConfig, fetch_klines
from tools.fetch_active_plan_market_data import convert_ohlcv_to_diagnostic_rows, write_diagnostic_csv

from src.feedback.macro_structure_volatility_replay import (
    EXPECTED_INTERVALS,
    LEVEL_SCHEMA_VERSION,
    METHOD_VERSION as M1_METHOD_VERSION,
    _dt,
    _level_events,
    _level_state,
    _load_ohlcv,
    _reliability,
    _structure,
    _volatility,
    build_levels,
    confirmed_pivots,
)

METHOD_VERSION = "macro_structure_daily_operation.v1"
SCHEMA_VERSION = "macro_structure_daily_operation.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
TIMEFRAMES = ("15m", "1h", "4h")
JST = ZoneInfo("Asia/Tokyo")
OUTPUT_NAMES = (
    "macro_structure_snapshot.json",
    "macro_structure_snapshot.md",
    "macro_level_reliability.csv",
    "run_manifest.json",
)
LEVEL_OUTPUT_FIELDS = (
    "schema_version", "method_version", "level_id", "side", "role", "low", "high", "center",
    "source_timeframes", "first_seen_at", "last_confirmed_at", "touch_count", "clean_rejection_count",
    "break_count", "false_break_reclaim_count", "median_reaction_atr", "median_hold_hours",
    "recency_score", "cross_timeframe_confluence", "reliability_score", "reliability_band", "lifecycle",
    "distance_from_price_pct", "distance_from_price_atr", "reason_codes",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iso(value: Any) -> str:
    return value.isoformat() if isinstance(value, datetime) else str(value or "")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _compact_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _input_symbols(path: Path) -> set[str]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if "symbol" not in (reader.fieldnames or []):
                return set()
            return {str(row.get("symbol") or "").strip() for row in reader if str(row.get("symbol") or "").strip()}
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValueError("invalid_input") from exc


def _validate_symbol_identity(paths: dict[str, Path], requested_symbol: str) -> None:
    observed: set[str] = set()
    for path in paths.values():
        symbols = _input_symbols(path)
        if any(symbol != requested_symbol for symbol in symbols):
            raise ValueError("ohlcv_symbol_mismatch")
        observed.update(symbols)
    if len(observed) > 1:
        raise ValueError("ohlcv_symbol_mismatch")


def _fetch_public_ohlcv(path: Path, limit: int, interval: str, symbol: str) -> None:
    frame = fetch_klines(
        FetchConfig(
            base_url="https://contract.mexc.com",
            symbol=symbol,
            timeout_sec=5,
            retry_count=3,
            request_interval_sec=0.3,
        ),
        interval=interval,
        limit=limit,
    )
    if frame is None or frame.empty:
        raise ValueError("public_ohlcv_empty")
    rows = convert_ohlcv_to_diagnostic_rows(frame, source_label="exchange-auto-public", interval=interval, symbol=symbol)
    if not rows or any(str(row.get("symbol") or "") != symbol for row in rows):
        raise ValueError("ohlcv_symbol_mismatch")
    write_diagnostic_csv(path, rows)


def _csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    from io import StringIO

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(LEVEL_OUTPUT_FIELDS), lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in LEVEL_OUTPUT_FIELDS} for row in rows)
    return output.getvalue().encode("utf-8")


def _latest_common_closed_cutoff(candles: dict[str, list[dict[str, Any]]]) -> datetime:
    latest = []
    for interval in TIMEFRAMES:
        if not candles[interval]:
            raise ValueError("public_ohlcv_empty")
        latest.append(candles[interval][-1]["timestamp"] + EXPECTED_INTERVALS[interval])
    return min(latest)


def _zone_summary(level: dict[str, Any], price: float, atr: float) -> dict[str, Any]:
    distance = abs(level["center"] - price)
    return {
        "level_id": level["level_id"],
        "side": level.get("side", ""),
        "role": level.get("role", ""),
        "low": level["low"],
        "high": level["high"],
        "center": level["center"],
        "source_timeframes": level.get("source_timeframes", ""),
        "first_seen_at": level.get("first_seen_at", ""),
        "last_confirmed_at": level.get("last_confirmed_at", ""),
        "touch_count": level.get("touch_count", 0),
        "clean_rejection_count": level.get("clean_rejection_count", 0),
        "break_count": level.get("break_count", 0),
        "false_break_reclaim_count": level.get("false_break_reclaim_count", 0),
        "lifecycle": level.get("lifecycle", ""),
        "reliability_score": level.get("reliability_score", 0),
        "reliability_band": level.get("reliability_band", "insufficient"),
        "distance_from_price_pct": round(distance / price * 100, 8) if price else "",
        "distance_from_price_atr": round(distance / atr, 8) if atr else "",
        "reason_codes": level.get("reason_codes", ""),
    }


def _intervening_obstruction(price: float, target: dict[str, Any] | None, levels: list[dict[str, Any]]) -> str:
    if target is None:
        return "insufficient"
    target_center = target["center"]
    if target_center > price:
        between = (level for level in levels if price < level["center"] < target_center and level["level_id"] != target["level_id"])
    else:
        between = (level for level in levels if target_center < level["center"] < price and level["level_id"] != target["level_id"])
    obstruction = min(between, key=lambda level: (abs(level["center"] - price), level["level_id"]), default=None)
    return obstruction["level_id"] if obstruction else "none"


def _markdown(snapshot: dict[str, Any]) -> str:
    structure = snapshot["structure_state"]
    location = snapshot["price_location"]
    support = snapshot["support_zones"]
    resistance = snapshot["resistance_zones"]
    lines = [
        "# Macro Structure Daily Snapshot",
        "",
        f"- snapshot time: `{snapshot['as_of_utc']}` / `{snapshot['as_of_jst']}`",
        f"- current structure: `{structure}`; location: `{location}`",
        f"- high/medium support: {json.dumps(support, ensure_ascii=False, sort_keys=True)}",
        f"- high/medium resistance: {json.dumps(resistance, ensure_ascii=False, sort_keys=True)}",
        f"- first upside target: `{snapshot['next_upside_target'].get('level_id', '')}`; obstruction: `{snapshot['upside_obstruction']}`",
        f"- first downside target: `{snapshot['next_downside_target'].get('level_id', '')}`; obstruction: `{snapshot['downside_obstruction']}`",
        f"- volatility: `{snapshot['volatility_state']}`; activation: `{snapshot['directional_activation']}`",
        f"- stale/insufficient warning: stale=`{snapshot['stale_status']}`; data_quality=`{snapshot['data_quality_status']}`; result=`{snapshot['result_status']}`",
        "- evidence confidence, not execution permission",
        "- report-only",
        "- human decides manually",
        "",
        "## Snapshot evidence",
        "",
        f"- current price: `{snapshot['current_price']}`",
        f"- cutoff: `{snapshot['snapshot_cutoff_utc']}`",
        f"- reason codes: `{','.join(snapshot['reason_codes'])}`",
        f"- input coverage: `{json.dumps(snapshot['input_coverage'], ensure_ascii=False, sort_keys=True)}`",
        "",
        "## Limitations",
        "",
        "This artifact describes public-market structure evidence. It is not a signal, execution permission, profitability claim, or production policy recommendation.",
        "",
        "## Safety boundary",
        "",
        SAFETY,
        "",
    ]
    return "\n".join(lines)


def _publish(root: Path, run_id: str, files: dict[str, bytes], latest: dict[str, Any]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    run_dir = root / run_id
    if run_dir.exists() and not all((run_dir / name).is_file() for name in OUTPUT_NAMES):
        raise OSError("incomplete_existing_run")
    stage = Path(tempfile.mkdtemp(prefix=".macro-structure-", dir=root))
    try:
        for name, content in files.items():
            (stage / name).write_bytes(content)
        if not run_dir.exists():
            stage.replace(run_dir)
        else:
            for name in OUTPUT_NAMES:
                if (run_dir / name).read_bytes() != (stage / name).read_bytes():
                    raise OSError("existing_output_conflict")
            shutil.rmtree(stage)
        latest_stage = root / ".latest.json.tmp"
        latest_stage.write_bytes(_compact_json_bytes(latest))
        latest_stage.replace(root / "latest.json")
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def build_macro_structure_daily(
    *,
    ohlcv_15m: Path | None = None,
    ohlcv_1h: Path | None = None,
    ohlcv_4h: Path | None = None,
    output_root: Path = Path("local/reports/macro_structure"),
    symbol: str = "BTC_USDT",
    ohlcv_limit: int = 500,
    fetch_public_ohlcv: bool = False,
    cutoff_utc: str | None = None,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    """Build and atomically publish one deterministic current snapshot."""
    temporary_root: Path | None = None
    try:
        now = (now_utc or datetime.now(timezone.utc))
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        now = now.astimezone(timezone.utc)
        paths = {"15m": ohlcv_15m, "1h": ohlcv_1h, "4h": ohlcv_4h}
        if fetch_public_ohlcv:
            temporary_root = Path(tempfile.mkdtemp(prefix="macro-structure-inputs-"))
            paths = {}
            for interval in TIMEFRAMES:
                path = temporary_root / f"ohlcv_{interval}.csv"
                _fetch_public_ohlcv(path, int(ohlcv_limit), interval, symbol)
                paths[interval] = path
        if any(path is None for path in paths.values()):
            raise ValueError("public_ohlcv_paths_required")
        explicit_paths = {interval: path for interval, path in paths.items() if path is not None}
        if len(explicit_paths) == len(TIMEFRAMES):
            _validate_symbol_identity(explicit_paths, symbol)
        candles: dict[str, list[dict[str, Any]]] = {}
        metadata: dict[str, dict[str, Any]] = {}
        fingerprints = {}
        for interval in TIMEFRAMES:
            path = paths[interval]
            assert path is not None
            candles[interval], metadata[interval] = _load_ohlcv(path, interval)
            fingerprints[interval] = _sha256(path)
        cutoff = min(_latest_common_closed_cutoff(candles), now).astimezone(timezone.utc)
        requested = _dt(cutoff_utc) if cutoff_utc else None
        if requested is not None:
            cutoff = min(cutoff, requested.astimezone(timezone.utc)).astimezone(timezone.utc)
        closed = {interval: [c for c in candles[interval] if c["timestamp"] + EXPECTED_INTERVALS[interval] <= cutoff] for interval in TIMEFRAMES}
        if any(not closed[interval] for interval in TIMEFRAMES):
            raise ValueError("common_closed_candle_cutoff_missing")
        price = closed["15m"][-1]["close"]
        pivots = confirmed_pivots(closed["1h"], "1h") + confirmed_pivots(closed["4h"], "4h")
        pivots = [pivot for pivot in pivots if pivot["confirmation_timestamp"] <= cutoff]
        levels = build_levels(pivots)
        atr = _volatility(closed["15m"], cutoff).get("atr", 0) or 0
        reliability_rows: list[dict[str, Any]] = []
        level_objects: list[dict[str, Any]] = []
        for level in levels:
            state = _level_state(level, closed["1h"], cutoff)
            reliability = _reliability(level, state, cutoff)
            level.update(reliability)
            level["role"] = state["role"]
            level_objects.append(level)
            row = dict(reliability)
            row.update({"role": state["role"], "distance_from_price_pct": round(abs(level["center"] - price) / price * 100, 8) if price else "", "distance_from_price_atr": round(abs(level["center"] - price) / atr, 8) if atr else ""})
            reliability_rows.append(row)
        structure = _structure(price, level_objects, closed["4h"], cutoff, [p for p in pivots if p["source_timeframe"] == "4h"])
        volatility = _volatility(closed["15m"], cutoff)
        reliable = [level for level in level_objects if level.get("reliability_band") in {"high", "medium"}]
        nearest = min(reliable, key=lambda level: (abs(level["center"] - price), level["level_id"])) if reliable else None
        lifecycle = _level_events(nearest, closed["1h"], cutoff) if nearest else {}
        activation = lifecycle.get("activation") or "NONE"
        freshness_cap = min(now, requested.astimezone(timezone.utc)) if requested is not None else now
        freshness: dict[str, dict[str, Any]] = {}
        stale_timeframes: list[str] = []
        for interval in TIMEFRAMES:
            endpoints = [
                candle["timestamp"] + EXPECTED_INTERVALS[interval]
                for candle in candles[interval]
                if candle["timestamp"] + EXPECTED_INTERVALS[interval] <= freshness_cap
            ]
            endpoint = max(endpoints) if endpoints else None
            age_minutes = round(max(0.0, (now - endpoint).total_seconds() / 60), 6) if endpoint else None
            threshold_minutes = int(EXPECTED_INTERVALS[interval].total_seconds() / 60 + 30)
            timeframe_stale = endpoint is None or age_minutes > threshold_minutes
            if timeframe_stale:
                stale_timeframes.append(interval)
            freshness[interval] = {
                "latest_closed_endpoint_utc": endpoint.isoformat() if endpoint else "",
                "age_minutes": age_minutes,
                "stale_threshold_minutes": threshold_minutes,
                "status": "stale" if timeframe_stale else "current",
            }
        stale = bool(stale_timeframes)
        discontinuous = any(metadata[interval].get("gap_count", 0) for interval in TIMEFRAMES)
        support_zones = sorted((_zone_summary(level, price, atr) for level in reliable if level.get("role") == "support"), key=lambda item: (-({"high": 2, "medium": 1}.get(item["reliability_band"], 0)), item["distance_from_price_pct"], item["level_id"]))[:5]
        resistance_zones = sorted((_zone_summary(level, price, atr) for level in reliable if level.get("role") == "resistance"), key=lambda item: (-({"high": 2, "medium": 1}.get(item["reliability_band"], 0)), item["distance_from_price_pct"], item["level_id"]))[:5]
        next_up = _zone_summary(structure["target_up"], price, atr) if structure.get("target_up") else {}
        next_down = _zone_summary(structure["target_down"], price, atr) if structure.get("target_down") else {}
        nearest_support = _zone_summary(structure["support"], price, atr) if structure.get("support") else {}
        nearest_resistance = _zone_summary(structure["resistance"], price, atr) if structure.get("resistance") else {}
        upside_obstruction = _intervening_obstruction(price, structure.get("target_up"), reliable)
        downside_obstruction = _intervening_obstruction(price, structure.get("target_down"), reliable)
        reason_codes = ["prior_only", "public_ohlcv_only"]
        if structure["state"] == "insufficient": reason_codes.append("insufficient_structure")
        if not support_zones: reason_codes.append("no_reliable_support")
        if not resistance_zones: reason_codes.append("no_reliable_resistance")
        if discontinuous: reason_codes.append("discontinuous_ohlcv")
        if stale:
            reason_codes.append("stale_ohlcv")
            reason_codes.extend(f"stale_ohlcv_{interval}" for interval in stale_timeframes)
        result_status = "insufficient" if structure["state"] == "insufficient" else "ok"
        data_quality = "discontinuous" if discontinuous else "stale" if stale else "ok"
        snapshot_cutoff = cutoff.isoformat()
        run_id = "run_" + hashlib.sha256(f"{SCHEMA_VERSION}|{METHOD_VERSION}|{symbol}|{snapshot_cutoff}|{json.dumps(fingerprints, sort_keys=True)}".encode()).hexdigest()[:20]
        snapshot = {
            "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "m1_method_version": M1_METHOD_VERSION,
            "snapshot_id": "macro_snapshot_" + run_id[4:], "run_id": run_id, "as_of_utc": snapshot_cutoff,
            "as_of_jst": cutoff.astimezone(JST).isoformat(), "snapshot_cutoff_utc": snapshot_cutoff,
            "symbol": symbol, "current_price": round(price, 10), "input_coverage": metadata,
            "input_fingerprints": fingerprints, "structure_state": structure["state"], "price_location": structure["location"],
            "location_percentile": structure.get("percentile", ""), "support_zones": support_zones,
            "resistance_zones": resistance_zones, "nearest_reliable_support": nearest_support,
            "nearest_reliable_resistance": nearest_resistance,
            "next_upside_target": next_up, "next_downside_target": next_down,
            "upside_obstruction": upside_obstruction,
            "downside_obstruction": downside_obstruction,
            "volatility_state": volatility.get("state", "insufficient"), "volatility": volatility,
            "expansion_risk": volatility.get("expansion_risk", "insufficient"), "directional_activation": activation,
            "stale_status": "stale" if stale else "current", "stale_timeframes": stale_timeframes,
            "freshness": freshness, "data_quality_status": data_quality,
            "continuity_status": "discontinuous" if discontinuous else "continuous", "result_status": result_status,
            "reason_codes": sorted(set(reason_codes)), "reliability_band_counts": {band: sum(row.get("reliability_band") == band for row in reliability_rows) for band in ("high", "medium", "low", "insufficient")},
            "safety_boundary": SAFETY,
        }
        manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "run_id": run_id, "snapshot_id": snapshot["snapshot_id"], "outputs": list(OUTPUT_NAMES), "input_fingerprints": fingerprints, "source": "public_ohlcv_only", "private_actual_trade_input": False, "report_only": True, "automatic_order_allowed": False, "safety_boundary": SAFETY}
        files = {"macro_structure_snapshot.json": _json_bytes(snapshot), "macro_structure_snapshot.md": _markdown(snapshot).encode("utf-8"), "macro_level_reliability.csv": _csv_bytes(reliability_rows), "run_manifest.json": _json_bytes(manifest)}
        latest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "run_id": run_id, "snapshot_id": snapshot["snapshot_id"], "artifact_dir": run_id, "as_of_utc": snapshot_cutoff, "result_status": result_status, "structure_state": snapshot["structure_state"], "price_location": snapshot["price_location"], "reliability_band_counts": snapshot["reliability_band_counts"], "stale_status": snapshot["stale_status"], "stale_timeframes": snapshot["stale_timeframes"], "freshness": snapshot["freshness"], "continuity_status": snapshot["continuity_status"], "safety_boundary": SAFETY}
        _publish(output_root, run_id, files, latest)
        return {"ok": True, "exit_code": 0, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "run_id": run_id, "snapshot_id": snapshot["snapshot_id"], "artifact_dir": run_id, "result_status": result_status, "structure_state": snapshot["structure_state"], "price_location": snapshot["price_location"], "reliability_band_counts": snapshot["reliability_band_counts"], "stale_status": snapshot["stale_status"], "stale_timeframes": snapshot["stale_timeframes"], "freshness": snapshot["freshness"], "data_quality_status": snapshot["data_quality_status"], "continuity_status": snapshot["continuity_status"], "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
    except (OSError, ValueError) as exc:
        return {"ok": False, "exit_code": 2, "error_code": str(exc), "report_written": False, "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
    finally:
        if temporary_root is not None:
            shutil.rmtree(temporary_root, ignore_errors=True)
