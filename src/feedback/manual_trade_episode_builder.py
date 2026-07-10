from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "manual_trade_episode.v1"
ASSOCIATION_METHOD_VERSION = "manual_trade_association.v1"
EPISODE_HEADERS = [
    "schema_version", "episode_id", "episode_source", "position_id", "symbol", "side",
    "opened_at_utc", "opened_at_jst", "closed_at_utc", "closed_at_jst", "status", "realized_pnl",
    "fee_total", "fill_count", "order_count", "association_method_version", "association_status",
    "association_reason_codes", "created_at_utc",
]


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def _parse_dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace(" ", "T")
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        from zoneinfo import ZoneInfo
        parsed = parsed.replace(tzinfo=ZoneInfo("Asia/Tokyo"))
    return parsed


def _dec(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _side(row: dict[str, Any]) -> str:
    value = str(row.get("side", "")).strip().lower()
    return value if value in {"long", "short"} else "unknown"


def _action_side(row: dict[str, Any]) -> str:
    action = str(row.get("position_action", "")).strip().lower()
    side = _side(row)
    if side in {"long", "short"} and action in {"open", "close", "reduce"}:
        return side
    return "unknown"


def _timestamp(row: dict[str, Any], *keys: str) -> datetime | None:
    for key in keys:
        parsed = _parse_dt(row.get(key))
        if parsed is not None:
            return parsed
    return None


def _read_csv(path: Path, required: tuple[str, ...]) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            headers = reader.fieldnames or []
            if not set(required).issubset(headers):
                return [], "invalid_input"
            return [dict(row) for row in reader], None
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"


def _safe_output(path: Path, replace_output: bool) -> tuple[bool, str | None]:
    if not path.exists():
        return True, None
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            headers = csv.DictReader(fp).fieldnames or []
    except (OSError, UnicodeError, csv.Error):
        return False, "existing_output_schema_mismatch"
    if headers != EPISODE_HEADERS and not replace_output:
        return False, "existing_output_schema_mismatch"
    return True, None


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=EPISODE_HEADERS)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in EPISODE_HEADERS} for row in rows)


def build_manual_trade_episode_rows(
    *,
    trade_rows: list[dict[str, Any]],
    order_rows: list[dict[str, Any]],
    position_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    positions = [row for row in position_rows if row.get("actual_position_id") or row.get("position_id")]
    fills = list(trade_rows)
    orders = list(order_rows)
    fill_candidates: dict[int, list[int]] = defaultdict(list)
    order_candidates: dict[int, list[int]] = defaultdict(list)
    windows: list[tuple[datetime | None, datetime | None]] = []
    for position in positions:
        opened = _timestamp(position, "opened_at_utc", "opened_at_jst")
        closed = _timestamp(position, "closed_at_utc", "closed_at_jst")
        windows.append((opened - timedelta(minutes=15) if opened else None, closed + timedelta(minutes=15) if closed else None))
    for index, fill in enumerate(fills):
        timestamp = _timestamp(fill, "timestamp_utc", "timestamp_jst")
        symbol = str(fill.get("symbol", "")).strip().upper()
        for position_index, position in enumerate(positions):
            start, end = windows[position_index]
            position_symbol = str(position.get("symbol", "")).strip().upper()
            if timestamp is None or symbol != position_symbol or (start and timestamp < start) or (end and timestamp > end):
                continue
            fill_candidates[index].append(position_index)
    for index, order in enumerate(orders):
        timestamp = _timestamp(order, "timestamp_utc", "timestamp_jst")
        symbol = str(order.get("symbol", "")).strip().upper()
        for position_index, position in enumerate(positions):
            start, end = windows[position_index]
            if timestamp is None or symbol != str(position.get("symbol", "")).strip().upper() or (start and timestamp < start) or (end and timestamp > end):
                continue
            order_candidates[index].append(position_index)
    rows: list[dict[str, str]] = []
    for position_index, position in enumerate(positions):
        position_id = str(position.get("actual_position_id") or position.get("position_id", "")).strip()
        method = ASSOCIATION_METHOD_VERSION
        episode_id = "ep_" + _hash(position_id, method)[:24]
        side = _side(position)
        selected_fills = [fill for index, fill in enumerate(fills) if fill_candidates.get(index) == [position_index]]
        selected_orders = [order for index, order in enumerate(orders) if order_candidates.get(index) == [position_index]]
        ambiguous = any(position_index in candidates and len(candidates) > 1 for candidates in fill_candidates.values()) or any(position_index in candidates and len(candidates) > 1 for candidates in order_candidates.values())
        conflict = False
        for row in selected_fills + selected_orders:
            explicit = _action_side(row)
            if explicit == "unknown":
                explicit = _side(row)
            if side in {"long", "short"} and explicit in {"long", "short"} and explicit != side:
                conflict = True
        reasons: list[str] = []
        if ambiguous:
            reasons.append("competing_position_candidates")
        if conflict:
            reasons.append("side_conflict")
        association_status = "ambiguous" if reasons else "matched"
        if not selected_fills and not selected_orders and not reasons:
            association_status = "unmatched"
            reasons.append("no_associated_rows")
        pnl = _dec(position.get("realized_pnl"))
        if pnl is None:
            values = [_dec(row.get("realized_pnl")) for row in selected_fills]
            pnl = sum((value for value in values if value is not None), Decimal("0")) if any(value is not None for value in values) else None
        fees = [_dec(row.get("fee")) for row in selected_fills]
        fee_total = sum((value for value in fees if value is not None), Decimal("0")) if any(value is not None for value in fees) else None
        opened_utc = str(position.get("opened_at_utc", "")).strip()
        opened_jst = str(position.get("opened_at_jst", "")).strip()
        closed_utc = str(position.get("closed_at_utc", "")).strip()
        closed_jst = str(position.get("closed_at_jst", "")).strip()
        rows.append({
            "schema_version": SCHEMA_VERSION, "episode_id": episode_id, "episode_source": "position_backed",
            "position_id": position_id, "symbol": str(position.get("symbol", "")).strip(), "side": side,
            "opened_at_utc": opened_utc, "opened_at_jst": opened_jst, "closed_at_utc": closed_utc,
            "closed_at_jst": closed_jst, "status": str(position.get("status", "unknown")).strip().lower() or "unknown",
            "realized_pnl": "" if pnl is None else format(pnl, "f"), "fee_total": "" if fee_total is None else format(fee_total, "f"),
            "fill_count": str(len(selected_fills) if not reasons else 0), "order_count": str(len(selected_orders) if not reasons else 0),
            "association_method_version": method, "association_status": association_status,
            "association_reason_codes": ";".join(reasons), "created_at_utc": "1970-01-01T00:00:00Z",
        })
    if not positions and fills:
        groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for fill in fills:
            timestamp = _timestamp(fill, "timestamp_utc", "timestamp_jst")
            key = (str(fill.get("symbol", "")).strip(), _side(fill), timestamp.date().isoformat() if timestamp else "")
            groups[key].append(fill)
        for key, group in sorted(groups.items()):
            opened = _timestamp(group[0], "timestamp_utc", "timestamp_jst")
            episode_id = "ep_" + _hash(key, tuple(sorted(str(row.get("actual_trade_id", "")) for row in group)), ASSOCIATION_METHOD_VERSION)[:24]
            pnl_values = [_dec(row.get("realized_pnl")) for row in group]
            fee_values = [_dec(row.get("fee")) for row in group]
            rows.append({
                "schema_version": SCHEMA_VERSION, "episode_id": episode_id, "episode_source": "derived_without_position",
                "position_id": "", "symbol": key[0], "side": key[1], "opened_at_utc": str(group[0].get("timestamp_utc", "")),
                "opened_at_jst": str(group[0].get("timestamp_jst", "")), "closed_at_utc": "", "closed_at_jst": "",
                "status": "unknown", "realized_pnl": format(sum((v for v in pnl_values if v is not None), Decimal("0")), "f") if any(pnl_values) else "",
                "fee_total": format(sum((v for v in fee_values if v is not None), Decimal("0")), "f") if any(fee_values) else "",
                "fill_count": str(len(group)), "order_count": "0", "association_method_version": ASSOCIATION_METHOD_VERSION,
                "association_status": "derived", "association_reason_codes": "no_position_lifecycle", "created_at_utc": "1970-01-01T00:00:00Z",
            })
    return sorted(rows, key=lambda row: (row.get("opened_at_utc", ""), row["episode_id"]))


def build_manual_trade_episodes(
    *, trades: Path, orders: Path, positions: Path, output_csv: Path | None = None,
    dry_run: bool = False, replace_output: bool = False,
) -> dict[str, Any]:
    output = output_csv or Path("logs/csv/manual_trade_episodes.csv")
    trade_rows, trade_error = _read_csv(trades, ("symbol",))
    order_rows, order_error = _read_csv(orders, ("symbol",))
    position_rows, position_error = _read_csv(positions, ("symbol",))
    errors = [error for error in (trade_error, order_error, position_error) if error]
    if not errors:
        if any(row.get("opened_at_utc") or row.get("opened_at_jst") for row in position_rows):
            if any(_timestamp(row, "opened_at_utc", "opened_at_jst") is None for row in position_rows):
                errors.append("invalid_input")
        for row in trade_rows + order_rows:
            if any(row.get(key) for key in ("timestamp_utc", "timestamp_jst")) and _timestamp(row, "timestamp_utc", "timestamp_jst") is None:
                errors.append("invalid_input")
    summary = {"ok": False, "schema_version": SCHEMA_VERSION, "association_method_version": ASSOCIATION_METHOD_VERSION, "dry_run": dry_run, "episode_count": 0, "output_csv": output.name, "errors": errors, "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"}
    if errors:
        summary["exit_code"] = 2
        return summary
    valid, error = _safe_output(output, replace_output)
    if not valid:
        summary.update(errors=[error], exit_code=4)
        return summary
    rows = build_manual_trade_episode_rows(trade_rows=trade_rows, order_rows=order_rows, position_rows=position_rows)
    summary["episode_count"] = len(rows)
    summary["output_written"] = not dry_run
    summary["exit_code"] = 0
    summary["ok"] = True
    if not dry_run:
        _write(output, rows)
    return summary
