from __future__ import annotations

import csv
import hashlib
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from src.feedback.manual_actual_trade_importer import ORDER_HEADERS, POSITION_HEADERS, TRADE_HEADERS


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


def _max_provenance(rows: list[dict[str, Any]]) -> str:
    values = [_parse_dt(row.get("imported_at_utc")) for row in rows]
    valid = [value for value in values if value is not None]
    if not valid:
        return ""
    return max(valid).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_csv(path: Path, headers: list[str]) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            headers = reader.fieldnames or []
            if headers != reader.fieldnames:
                return [], "input_schema_mismatch"
            rows = [dict(row) for row in reader]
            if any(row.get("schema_version") != "manual_actual_trade.v2" for row in rows):
                return [], "input_schema_mismatch"
            return rows, None
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
    with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", dir=path.parent, delete=False) as fp:
        temp_path = Path(fp.name)
        writer = csv.DictWriter(fp, fieldnames=EPISODE_HEADERS)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in EPISODE_HEADERS} for row in rows)
    try:
        temp_path.replace(path)
    except OSError:
        temp_path.unlink(missing_ok=True)
        raise


def _association_counts(rows: list[dict[str, Any]], positions: list[dict[str, Any]], timestamp_keys: tuple[str, ...]) -> tuple[int, int, int]:
    unresolved = ambiguous = associated = 0
    windows = []
    for position in positions:
        opened = _timestamp(position, "opened_at_utc", "opened_at_jst")
        closed = _timestamp(position, "closed_at_utc", "closed_at_jst")
        windows.append((opened - timedelta(minutes=15) if opened else None, closed + timedelta(minutes=15) if closed else None, str(position.get("symbol", "")).strip().upper()))
    for row in rows:
        timestamp = _timestamp(row, *timestamp_keys)
        candidates = []
        for index, (start, end, symbol) in enumerate(windows):
            if timestamp is None or str(row.get("symbol", "")).strip().upper() != symbol or (start and timestamp < start) or (end and timestamp > end):
                continue
            candidates.append(index)
        if len(candidates) == 0:
            unresolved += 1
        elif len(candidates) == 1:
            associated += 1
        else:
            ambiguous += 1
    return unresolved, ambiguous, associated


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
        explicit_sides = set()
        for row in selected_fills + selected_orders:
            if str(row.get("position_action", "")).strip().lower() in {"open", "close", "reduce"} and _side(row) in {"long", "short"}:
                explicit_sides.add(_side(row))
        conflict = len(explicit_sides) > 1
        if side == "unknown" and len(explicit_sides) == 1:
            side = next(iter(explicit_sides))
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
        provenance = _max_provenance([position, *selected_fills, *selected_orders])
        rows.append({
            "schema_version": SCHEMA_VERSION, "episode_id": episode_id, "episode_source": "position_backed",
            "position_id": position_id, "symbol": str(position.get("symbol", "")).strip(), "side": side,
            "opened_at_utc": opened_utc, "opened_at_jst": opened_jst, "closed_at_utc": closed_utc,
            "closed_at_jst": closed_jst, "status": str(position.get("status", "unknown")).strip().lower() or "unknown",
            "realized_pnl": "" if pnl is None else format(pnl, "f"), "fee_total": "" if fee_total is None else format(fee_total, "f"),
            "fill_count": str(len(selected_fills)), "order_count": str(len(selected_orders)),
            "association_method_version": method, "association_status": association_status,
            "association_reason_codes": ";".join(reasons), "created_at_utc": provenance,
        })
    return sorted(rows, key=lambda row: (row.get("opened_at_utc", ""), row["episode_id"]))


def build_manual_trade_episodes(
    *, trades: Path, orders: Path, positions: Path, output_csv: Path | None = None,
    dry_run: bool = False, replace_output: bool = False,
) -> dict[str, Any]:
    output = output_csv or Path("logs/csv/manual_trade_episodes.csv")
    trade_rows, trade_error = _read_csv(trades, TRADE_HEADERS)
    order_rows, order_error = _read_csv(orders, ORDER_HEADERS)
    position_rows, position_error = _read_csv(positions, POSITION_HEADERS)
    errors = [error for error in (trade_error, order_error, position_error) if error]
    if not errors:
        for row in trade_rows + order_rows:
            if not str(row.get("actual_trade_id") or row.get("actual_order_id") or "").strip() or not str(row.get("symbol", "")).strip() or _timestamp(row, "timestamp_utc", "timestamp_jst") is None:
                errors.append("invalid_input")
        for row in position_rows:
            opened = _timestamp(row, "opened_at_utc", "opened_at_jst")
            closed = _timestamp(row, "closed_at_utc", "closed_at_jst")
            status = str(row.get("status", "")).strip().lower()
            if not str(row.get("actual_position_id", "")).strip() or not str(row.get("symbol", "")).strip() or opened is None:
                errors.append("invalid_input")
            elif status == "closed" and closed is None:
                errors.append("invalid_input")
            elif status == "open" and closed is not None:
                errors.append("invalid_input")
            elif closed is not None and closed < opened:
                errors.append("invalid_input")
    summary = {"ok": False, "schema_version": SCHEMA_VERSION, "association_method_version": ASSOCIATION_METHOD_VERSION, "dry_run": dry_run, "episode_count": 0, "position_count": len(position_rows), "matched_episode_count": 0, "ambiguous_episode_count": 0, "unmatched_episode_count": 0, "unresolved_fill_count": len(trade_rows), "unresolved_order_count": len(order_rows), "ambiguous_fill_count": 0, "ambiguous_order_count": 0, "associated_fill_count": 0, "associated_order_count": 0, "output_csv": output.name, "errors": errors, "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"}
    if errors:
        summary["exit_code"] = 2
        return summary
    valid, error = _safe_output(output, replace_output)
    if not valid:
        summary.update(errors=[error], exit_code=4)
        return summary
    rows = build_manual_trade_episode_rows(trade_rows=trade_rows, order_rows=order_rows, position_rows=position_rows)
    summary["episode_count"] = len(rows)
    summary["matched_episode_count"] = sum(row["association_status"] == "matched" for row in rows)
    summary["ambiguous_episode_count"] = sum(row["association_status"] == "ambiguous" for row in rows)
    summary["unmatched_episode_count"] = sum(row["association_status"] == "unmatched" for row in rows)
    summary["unresolved_fill_count"], summary["ambiguous_fill_count"], summary["associated_fill_count"] = _association_counts(trade_rows, position_rows, ("timestamp_utc", "timestamp_jst"))
    summary["unresolved_order_count"], summary["ambiguous_order_count"], summary["associated_order_count"] = _association_counts(order_rows, position_rows, ("timestamp_utc", "timestamp_jst"))
    summary["output_written"] = not dry_run
    summary["exit_code"] = 0
    summary["ok"] = True
    if not dry_run:
        try:
            _write(output, rows)
        except OSError:
            summary.update(ok=False, output_written=False, errors=["output_io_failure"], exit_code=4)
    return summary
