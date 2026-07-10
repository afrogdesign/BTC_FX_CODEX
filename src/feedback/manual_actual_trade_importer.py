from __future__ import annotations

import csv
import hashlib
import json
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parents[2]
JST = ZoneInfo("Asia/Tokyo")
SCHEMA_VERSION = "manual_actual_trade.v2"
SAFETY_BOUNDARY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
}

TRADE_HEADERS = [
    "schema_version", "actual_trade_id", "source_row_id", "logical_key", "row_fingerprint",
    "source_uid_hash", "source_file", "source_file_sha256", "import_batch_id", "imported_at_utc",
    "timestamp_utc", "timestamp_jst", "symbol", "side", "transaction_side", "position_action",
    "order_type", "fill_qty_contract", "fill_qty_token", "fill_qty_value", "fill_price", "fee",
    "fee_asset", "role", "realized_pnl", "status", "import_status",
]
ORDER_HEADERS = [
    "schema_version", "actual_order_id", "source_row_id", "logical_key", "row_fingerprint",
    "source_uid_hash", "source_file", "source_file_sha256", "import_batch_id", "imported_at_utc",
    "timestamp_utc", "timestamp_jst", "symbol", "side", "transaction_side", "position_action",
    "leverage", "order_type", "filled_qty", "avg_fill_price", "realized_pnl", "fee", "fee_asset",
    "status", "source_status", "import_status",
]
POSITION_HEADERS = [
    "schema_version", "actual_position_id", "source_row_id", "logical_key", "row_fingerprint",
    "source_uid_hash", "source_file", "source_file_sha256", "import_batch_id", "imported_at_utc",
    "opened_at_utc", "opened_at_jst", "closed_at_utc", "closed_at_jst", "symbol", "side",
    "realized_pnl", "status", "source_status", "import_status",
]
ISSUE_HEADERS = [
    "import_batch_id", "category", "source_file", "sheet_name", "source_row_number", "issue_type",
    "reason_code", "field_name", "logical_key", "existing_normalized_id", "incoming_row_fingerprint",
]

_CATEGORY = {
    "trade_history": {
        "fragments": ("trade history", "futures_trade_history"),
        "output": "manual_actual_trades.csv",
        "headers": TRADE_HEADERS,
    },
    "order_history": {
        "fragments": ("order history", "futures_order_history"),
        "output": "manual_actual_orders.csv",
        "headers": ORDER_HEADERS,
    },
    "position_history": {
        "fragments": ("position history", "futures_position_history"),
        "output": "manual_actual_positions.csv",
        "headers": POSITION_HEADERS,
    },
}
_REQUIRED = {
    "trade_history": (
        "UID", "時間(UTC+09:00)", "先物取引ペア", "方向", "注文の種類", "約定価格",
        "取引手数料", "手数料支払い暗号資産", "役割", "決済損益",
    ),
    "order_history": (
        "UID", "時間(UTC+09:00)", "先物取引ペア", "方向", "レバレッジ", "注文の種類",
        "約定数量", "平均約定価格", "決済損益", "手数料", "ステータス",
    ),
    "position_history": (
        "UID", "取引ペア", "オープン時間(UTC+09:00)", "決済時刻", "方向", "実現損益", "ステータス",
    ),
}
_QUANTITY_HEADERS = ("約定数量 (枚)", "約定数量 (トークン)", "約定数量 (金額)")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_parts(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def _uid_hash(uid: str) -> str:
    return _hash_parts("mexc:" + uid.strip())


def _safe_basename(name: str, category: str, source_hash: str) -> str:
    basename = Path(name).name
    if (
        re.search(r"\d{6,}", basename)
        or re.search(r"[^@\s]+@[^@\s]+", basename)
        or re.search(r"(?:uid|account)[-_]", basename, re.IGNORECASE)
    ):
        return f"mexc_{category}_{source_hash[:16]}.xlsx"
    return basename


def _safe_unsupported_name(name: str) -> str:
    return f"unsupported_{_hash_parts(Path(name).name)[:16]}{Path(name).suffix.casefold()}"


def _sheet_rows(path: Path) -> tuple[str, list[dict[str, str]], list[str]]:
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for item in root.findall("main:si", _NS):
                shared.append("".join(x.text or "" for x in item.findall(".//main:t", _NS)))
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_targets = {r.attrib.get("Id"): r.attrib.get("Target", "") for r in rels}
        visible: list[tuple[str, str]] = []
        for sheet in workbook.findall("main:sheets/main:sheet", _NS):
            if sheet.attrib.get("state", "visible") == "hidden":
                continue
            target = rel_targets.get(sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"), "")
            target = target.lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            visible.append((sheet.attrib.get("name", ""), target))
        if not visible:
            raise ValueError("unreadable_workbook")
        selected = next((item for item in visible if item[0].casefold() == "sheet1"), None)
        if selected is None:
            if len(visible) != 1:
                raise ValueError("ambiguous_sheet")
            selected = visible[0]
        sheet_name, target = selected
        if target not in names:
            raise ValueError("unreadable_workbook")
        root = ET.fromstring(zf.read(target))
    sheet_data = root.find("main:sheetData", _NS)
    if sheet_data is None:
        raise ValueError("empty_sheet")
    raw_rows: list[tuple[int, dict[int, str]]] = []
    for row_el in sheet_data.findall("main:row", _NS):
        values: dict[int, str] = {}
        for cell in row_el.findall("main:c", _NS):
            ref = cell.attrib.get("r", "")
            letters = re.match(r"[A-Za-z]+", ref)
            if not letters:
                continue
            col = 0
            for char in letters.group(0).upper():
                col = col * 26 + ord(char) - 64
            value = cell.find("main:v", _NS)
            if cell.attrib.get("t") == "inlineStr":
                text = "".join(x.text or "" for x in cell.findall("main:is/main:t", _NS))
            elif value is None or value.text is None:
                text = ""
            else:
                text = shared[int(value.text)] if cell.attrib.get("t") == "s" else value.text
            values[col] = text.strip()
        if values:
            raw_rows.append((int(row_el.attrib.get("r", len(raw_rows) + 1)), values))
    if not raw_rows:
        raise ValueError("empty_sheet")
    max_col = max(max(values) for _, values in raw_rows)
    headers = [raw_rows[0][1].get(index, "").strip() for index in range(1, max_col + 1)]
    if not any(headers):
        raise ValueError("empty_sheet")
    rows: list[dict[str, str]] = []
    for source_row_number, values in raw_rows[1:]:
        row = {header: values.get(index, "") for index, header in enumerate(headers, start=1) if header}
        if any(value.strip() for value in row.values()):
            row["__source_row_number"] = str(source_row_number)
            rows.append(row)
    if not rows:
        raise ValueError("empty_sheet")
    return sheet_name, rows, headers


def _parse_datetime(value: str) -> tuple[str, str]:
    text = value.strip()
    if not text:
        raise ValueError("malformed_date")
    candidate = text.replace("/", "-").replace(" ", "T")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError("malformed_date") from exc
    if parsed.tzinfo is not None:
        offset = parsed.utcoffset()
        if offset != JST.utcoffset(parsed):
            raise ValueError("conflicting_timezone")
        aware = parsed
    else:
        aware = parsed.replace(tzinfo=JST)
    utc = aware.astimezone(timezone.utc).replace(microsecond=0)
    jst = aware.astimezone(JST).replace(microsecond=0)
    return utc.isoformat().replace("+00:00", "Z"), jst.isoformat()


def _decimal(value: str, *, required: bool = False, non_negative: bool = False) -> str:
    text = value.strip().replace(",", "").replace("＋", "+").replace("－", "-")
    if not text:
        if required:
            raise ValueError("malformed_numeric")
        return ""
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError("malformed_numeric") from exc
    if non_negative:
        number = abs(number)
    return format(number, "f")


def _symbol(value: str) -> str:
    normalized = value.strip().replace("-", "_").replace("/", "_").replace(" ", "").upper()
    if normalized == "BTCUSDT" or normalized == "BTC_USDT":
        return "BTCUSDT"
    raise ValueError("unsupported_symbol")


def _direction(value: str) -> tuple[str, str, str]:
    text = value.strip().casefold()
    mappings = {
        "long": ("long", "unknown", "unknown"), "ロング": ("long", "unknown", "unknown"),
        "short": ("short", "unknown", "unknown"), "ショート": ("short", "unknown", "unknown"),
        "buy": ("unknown", "buy", "unknown"), "買い": ("unknown", "buy", "unknown"),
        "sell": ("unknown", "sell", "unknown"), "売り": ("unknown", "sell", "unknown"),
        "open long": ("long", "buy", "open"), "ロングを開く": ("long", "buy", "open"),
        "close long": ("long", "sell", "close"), "ロングを決済": ("long", "sell", "close"),
        "open short": ("short", "sell", "open"), "ショートを開く": ("short", "sell", "open"),
        "close short": ("short", "buy", "close"), "ショートを決済": ("short", "buy", "close"),
    }
    if text not in mappings:
        raise ValueError("unknown_direction")
    return mappings[text]


def _status(value: str, *, position: bool = False) -> tuple[str, str]:
    source = value.strip()
    text = source.casefold().replace(" ", "_")
    if position:
        mapping = {"open": "open", "opened": "open", "closed": "closed", "close": "closed"}
        return mapping.get(text, "unknown"), source
    mapping = {
        "filled": "filled", "fill": "filled", "partially_filled": "partially_filled",
        "partial": "partially_filled", "canceled": "canceled", "cancelled": "canceled",
        "open": "open",
    }
    return mapping.get(text, "unknown"), source


def _required_check(category: str, headers: list[str]) -> None:
    missing = [header for header in _REQUIRED[category] if header not in headers]
    if category == "trade_history" and not any(header in headers for header in _QUANTITY_HEADERS):
        missing.append("quantity")
    if missing:
        raise ValueError("missing_required_column")


def _source_files(input_dir: Path) -> tuple[dict[str, list[Path]], list[str], list[str]]:
    found = {category: [] for category in _CATEGORY}
    unsupported: list[str] = []
    errors: list[str] = []
    if not input_dir.exists():
        return found, unsupported, errors
    for path in sorted(input_dir.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        suffix = path.suffix.casefold()
        if suffix != ".xlsx":
            if suffix in {".xls", ".xlsm", ".csv", ".pdf"}:
                unsupported.append(_safe_unsupported_name(name))
            continue
        matches = [category for category, spec in _CATEGORY.items() if any(fragment in name.casefold() for fragment in spec["fragments"])]
        if len(matches) == 1:
            found[matches[0]].append(path)
        elif len(matches) > 1:
            errors.append("ambiguous_source_category")
        else:
            unsupported.append(_safe_unsupported_name(name))
    return found, unsupported, errors


def _base_row(category: str, raw: dict[str, str], *, path: Path, sheet: str, source_hash: str, batch_id: str) -> dict[str, str]:
    uid = raw.get("UID", "").strip()
    if not uid:
        raise ValueError("missing_uid")
    source_uid_hash = _uid_hash(uid)
    source_file = _safe_basename(path.name, category, source_hash)
    source_row_id = _hash_parts(source_hash, sheet, raw.get("__source_row_number", ""))
    imported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": SCHEMA_VERSION, "source_row_id": source_row_id, "source_uid_hash": source_uid_hash,
        "source_file": source_file, "source_file_sha256": source_hash, "import_batch_id": batch_id,
        "imported_at_utc": imported_at, "import_status": "active",
    }


def _normalize_row(category: str, raw: dict[str, str], *, path: Path, sheet: str, source_hash: str, batch_id: str) -> dict[str, str]:
    row = _base_row(category, raw, path=path, sheet=sheet, source_hash=source_hash, batch_id=batch_id)
    if category == "trade_history":
        timestamp_utc, timestamp_jst = _parse_datetime(raw.get("時間(UTC+09:00)", ""))
        side, transaction_side, position_action = _direction(raw.get("方向", ""))
        symbol = _symbol(raw.get("先物取引ペア", ""))
        quantities = {key: _decimal(raw.get(key, ""), required=False) for key in _QUANTITY_HEADERS}
        if not any(quantities.values()):
            raise ValueError("missing_quantity")
        row.update({
            "timestamp_utc": timestamp_utc, "timestamp_jst": timestamp_jst, "symbol": symbol,
            "side": side, "transaction_side": transaction_side, "position_action": position_action,
            "order_type": raw.get("注文の種類", "").strip(), "fill_qty_contract": quantities[_QUANTITY_HEADERS[0]],
            "fill_qty_token": quantities[_QUANTITY_HEADERS[1]], "fill_qty_value": quantities[_QUANTITY_HEADERS[2]],
            "fill_price": _decimal(raw.get("約定価格", ""), required=True),
            "fee": _decimal(raw.get("取引手数料", ""), non_negative=True),
            "fee_asset": raw.get("手数料支払い暗号資産", "").strip().upper(), "role": raw.get("役割", "").strip(),
            "realized_pnl": _decimal(raw.get("決済損益", "")), "status": "filled",
        })
        logical_values = (category, row["source_uid_hash"], row["timestamp_utc"], symbol, side, transaction_side, position_action, row["order_type"], row["fill_qty_contract"], row["fill_qty_token"], row["fill_qty_value"], row["fill_price"])
    elif category == "order_history":
        timestamp_utc, timestamp_jst = _parse_datetime(raw.get("時間(UTC+09:00)", ""))
        side, transaction_side, position_action = _direction(raw.get("方向", ""))
        symbol = _symbol(raw.get("先物取引ペア", ""))
        normalized_status, source_status = _status(raw.get("ステータス", ""))
        row.update({
            "timestamp_utc": timestamp_utc, "timestamp_jst": timestamp_jst, "symbol": symbol,
            "side": side, "transaction_side": transaction_side, "position_action": position_action,
            "leverage": _decimal(raw.get("レバレッジ", "")), "order_type": raw.get("注文の種類", "").strip(),
            "filled_qty": _decimal(raw.get("約定数量", "")), "avg_fill_price": _decimal(raw.get("平均約定価格", ""), required=True),
            "realized_pnl": _decimal(raw.get("決済損益", "")), "fee": _decimal(raw.get("手数料", ""), non_negative=True),
            "fee_asset": "", "status": normalized_status, "source_status": source_status,
        })
        logical_values = (category, row["source_uid_hash"], row["timestamp_utc"], symbol, side, transaction_side, position_action, row["order_type"], row["filled_qty"], row["avg_fill_price"])
    else:
        opened_utc, opened_jst = _parse_datetime(raw.get("オープン時間(UTC+09:00)", ""))
        closed_raw = raw.get("決済時刻", "").strip()
        closed_utc = closed_jst = ""
        if closed_raw:
            closed_utc, closed_jst = _parse_datetime(closed_raw)
        side, transaction_side, position_action = _direction(raw.get("方向", ""))
        symbol = _symbol(raw.get("取引ペア", ""))
        normalized_status, source_status = _status(raw.get("ステータス", ""), position=True)
        if normalized_status == "closed" and not closed_utc:
            raise ValueError("closed_position_missing_close_time")
        if normalized_status == "open" and closed_utc:
            raise ValueError("open_position_has_close_time")
        if closed_utc and closed_utc < opened_utc:
            raise ValueError("close_before_open")
        row.update({
            "opened_at_utc": opened_utc, "opened_at_jst": opened_jst, "closed_at_utc": closed_utc,
            "closed_at_jst": closed_jst, "symbol": symbol, "side": side,
            "realized_pnl": _decimal(raw.get("実現損益", "")), "status": normalized_status,
            "source_status": source_status,
        })
        logical_values = (category, row["source_uid_hash"], opened_utc, symbol, side)
    row["logical_key"] = _hash_parts(*logical_values)
    business = {key: value for key, value in row.items() if key not in {"source_file", "source_file_sha256", "import_batch_id", "imported_at_utc", "source_row_id", "logical_key", "row_fingerprint", "actual_trade_id", "actual_order_id", "actual_position_id", "import_status", "schema_version"}}
    row["row_fingerprint"] = _hash_parts(*[f"{key}={business[key]}" for key in sorted(business)])
    id_key = {"trade_history": "actual_trade_id", "order_history": "actual_order_id", "position_history": "actual_position_id"}[category]
    row[id_key] = {"trade_history": "tra_", "order_history": "ord_", "position_history": "pos_"}[category] + row["row_fingerprint"][:24]
    return {field: row.get(field, "") for field in _CATEGORY[category]["headers"]}


def _normalize_rows_legacy(rows: list[dict[str, Any]], category: str, source_file: str) -> list[dict[str, str]]:
    path = Path(source_file)
    source_hash = _sha256_bytes(source_file.encode())
    batch_id = "batch_" + _hash_parts(category, source_hash)[:24]
    result = []
    for index, raw in enumerate(rows, start=2):
        raw = {**{str(k): str(v) for k, v in raw.items()}, "__source_row_number": str(index)}
        result.append(_normalize_row(category, raw, path=path, sheet="Sheet1", source_hash=source_hash, batch_id=batch_id))
    return result


def normalize_mexc_trade_history(rows: list[dict[str, Any]], *, source_file: str) -> list[dict[str, str]]:
    return _normalize_rows_legacy(rows, "trade_history", source_file)


def normalize_mexc_order_history(rows: list[dict[str, Any]], *, source_file: str) -> list[dict[str, str]]:
    return _normalize_rows_legacy(rows, "order_history", source_file)


def normalize_mexc_position_history(rows: list[dict[str, Any]], *, source_file: str) -> list[dict[str, str]]:
    return _normalize_rows_legacy(rows, "position_history", source_file)


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(BASE_DIR.resolve()))
    except ValueError:
        return path.name


def _read_existing(path: Path, headers: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        if reader.fieldnames != headers:
            raise ValueError("existing_output_schema_mismatch")
        return [{field: row.get(field, "") for field in headers} for row in reader]


def _write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=headers)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in headers} for row in rows)


def _atomic_write(paths_rows: list[tuple[Path, list[str], list[dict[str, str]]]]) -> None:
    parent = paths_rows[0][0].parent
    parent.mkdir(parents=True, exist_ok=True)
    temp_paths: list[tuple[Path, Path]] = []
    backup_paths: dict[Path, Path] = {}
    replaced_paths: list[Path] = []
    try:
        for path, headers, rows in paths_rows:
            with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", dir=parent, delete=False) as fp:
                writer = csv.DictWriter(fp, fieldnames=headers)
                writer.writeheader()
                writer.writerows({field: row.get(field, "") for field in headers} for row in rows)
                temp_paths.append((path, Path(fp.name)))
        for path, temp_path in temp_paths:
            if path.exists():
                with tempfile.NamedTemporaryFile(dir=parent, delete=False) as backup_fp:
                    backup_path = Path(backup_fp.name)
                backup_path.unlink(missing_ok=True)
                path.replace(backup_path)
                backup_paths[path] = backup_path
            temp_path.replace(path)
            replaced_paths.append(path)
    except Exception:
        for path in reversed(replaced_paths):
            path.unlink(missing_ok=True)
            backup_path = backup_paths.get(path)
            if backup_path is not None and backup_path.exists():
                backup_path.replace(path)
        for path, backup_path in backup_paths.items():
            if path not in replaced_paths and backup_path.exists():
                backup_path.replace(path)
        for _, temp_path in temp_paths:
            temp_path.unlink(missing_ok=True)
        for backup_path in backup_paths.values():
            backup_path.unlink(missing_ok=True)
        raise
    for _, temp_path in temp_paths:
        temp_path.unlink(missing_ok=True)
    for backup_path in backup_paths.values():
        backup_path.unlink(missing_ok=True)


def import_manual_actual_trades(*, input_dir: Path, output_dir: Path | None = None, dry_run: bool = False, conflict_policy: str = "reject", cli_alias_used: bool = False) -> dict[str, Any]:
    output_root = output_dir or (BASE_DIR / "logs" / "csv")
    files_by_category, unsupported_files, collection_errors = _source_files(input_dir)
    category_counts = {category: len(paths) for category, paths in files_by_category.items()}
    source_paths = [path for paths in files_by_category.values() for path in paths]
    try:
        hashes = {path: _sha256_bytes(path.read_bytes()) for path in source_paths}
    except (OSError, RuntimeError, NotImplementedError, ValueError):
        return {
            "ok": False,
            "schema_version": SCHEMA_VERSION,
            "dry_run": bool(dry_run),
            "cli_command": "import-manual-actual-trades",
            "cli_alias_used": bool(cli_alias_used),
            "input_dir": _repo_relative(input_dir),
            "output_dir": _repo_relative(output_root),
            "import_batch_id": "",
            "source_file_count": len(source_paths),
            "category_file_counts": category_counts,
            "sheets_read": {category: 0 for category in _CATEGORY},
            "rows_read": 0,
            "rows_accepted": 0,
            "total_rows": 0,
            "rows_rejected": 0,
            "duplicate_rows_skipped": 0,
            "conflicts_found": 0,
            "rows_inserted": 0,
            "rows_replaced": 0,
            "outputs_written": [],
            "outputs_unchanged": [],
            "would_write_outputs": [],
            "would_write_issues_file": False,
            "issues_file": "",
            "symbols": [],
            "date_range_utc": {"min": "", "max": ""},
            "date_range_jst": {"min": "", "max": ""},
            "missing_categories": [category for category, count in category_counts.items() if count == 0],
            "unsupported_files": unsupported_files,
            "errors": ["unreadable_workbook"],
            "safety_boundary": SAFETY_BOUNDARY,
            "exit_code": 2,
        }
    batch_id = "batch_" + _hash_parts(*sorted(f"{category}:{hashes[path]}" for category, paths in files_by_category.items() for path in paths))[:24]
    summary: dict[str, Any] = {
        "ok": False, "schema_version": SCHEMA_VERSION, "dry_run": bool(dry_run),
        "cli_command": "import-manual-actual-trades", "cli_alias_used": bool(cli_alias_used),
        "input_dir": _repo_relative(input_dir), "output_dir": _repo_relative(output_root),
        "import_batch_id": batch_id, "source_file_count": len(source_paths), "category_file_counts": category_counts,
        "sheets_read": {category: 0 for category in _CATEGORY},
        "rows_read": 0, "rows_accepted": 0, "total_rows": 0, "rows_rejected": 0, "duplicate_rows_skipped": 0,
        "conflicts_found": 0, "rows_inserted": 0, "rows_replaced": 0, "outputs_written": [], "outputs_unchanged": [],
        "would_write_outputs": [], "would_write_issues_file": False,
        "issues_file": "", "symbols": [], "date_range_utc": {"min": "", "max": ""}, "date_range_jst": {"min": "", "max": ""},
        "missing_categories": [category for category, count in category_counts.items() if count == 0],
        "unsupported_files": unsupported_files, "errors": list(collection_errors), "safety_boundary": SAFETY_BOUNDARY,
        "exit_code": 0,
    }
    if not source_paths:
        summary.update(ok=False, errors=["no_input_files"], exit_code=2)
        return summary
    if summary["missing_categories"]:
        summary.update(ok=False, errors=["missing_category"], exit_code=2)
        return summary
    accepted: dict[str, list[dict[str, str]]] = {category: [] for category in _CATEGORY}
    issues: list[dict[str, str]] = []
    for category, paths in files_by_category.items():
        for path in paths:
            try:
                sheet, raw_rows, headers = _sheet_rows(path)
                _required_check(category, headers)
            except (zipfile.BadZipFile, KeyError, ET.ParseError, OSError, RuntimeError, NotImplementedError, IndexError):
                summary["errors"].append("unreadable_workbook")
                continue
            except ValueError as exc:
                reason = str(exc)
                if reason not in {"ambiguous_sheet", "empty_sheet", "missing_required_column", "unreadable_workbook"}:
                    reason = "unreadable_workbook"
                summary["errors"].append(reason)
                continue
            summary["rows_read"] += len(raw_rows)
            summary["sheets_read"][category] += 1
            for raw in raw_rows:
                try:
                    accepted[category].append(_normalize_row(category, raw, path=path, sheet=sheet, source_hash=hashes[path], batch_id=batch_id))
                except ValueError as exc:
                    summary["rows_rejected"] += 1
                    issues.append({"import_batch_id": batch_id, "category": category, "source_file": _safe_basename(path.name, category, hashes[path]), "sheet_name": sheet, "source_row_number": raw.get("__source_row_number", ""), "issue_type": "rejected", "reason_code": str(exc), "field_name": "", "logical_key": "", "existing_normalized_id": "", "incoming_row_fingerprint": ""})
    if summary["errors"]:
        summary["exit_code"] = 2
        return summary
    summary["rows_accepted"] = sum(len(rows) for rows in accepted.values())
    summary["total_rows"] = summary["rows_accepted"]
    if summary["rows_accepted"] == 0:
        summary.update(ok=False, errors=["all_rows_rejected"], exit_code=2)
        return summary
    existing: dict[str, list[dict[str, str]]] = {}
    try:
        for category, spec in _CATEGORY.items():
            existing[category] = _read_existing(output_root / spec["output"], spec["headers"])
    except ValueError as exc:
        summary.update(errors=[str(exc)], exit_code=4)
        return summary
    merged: dict[str, list[dict[str, str]]] = {category: list(rows) for category, rows in existing.items()}
    for category, rows in accepted.items():
        by_logical = {row["logical_key"]: row for row in merged[category]}
        by_fp = {row["row_fingerprint"] for row in merged[category]}
        for row in rows:
            if row["row_fingerprint"] in by_fp:
                summary["duplicate_rows_skipped"] += 1
            elif row["logical_key"] in by_logical:
                summary["conflicts_found"] += 1
                issues.append({"import_batch_id": batch_id, "category": category, "source_file": row["source_file"], "sheet_name": "", "source_row_number": "", "issue_type": "conflict", "reason_code": "logical_key_changed", "field_name": "", "logical_key": row["logical_key"], "existing_normalized_id": by_logical[row["logical_key"]].get({"trade_history": "actual_trade_id", "order_history": "actual_order_id", "position_history": "actual_position_id"}[category], ""), "incoming_row_fingerprint": row["row_fingerprint"]})
                if conflict_policy == "replace":
                    merged[category] = [old for old in merged[category] if old["logical_key"] != row["logical_key"]]
                    merged[category].append(row)
                    by_logical = {item["logical_key"]: item for item in merged[category]}
                    by_fp.add(row["row_fingerprint"])
                    summary["rows_replaced"] += 1
            else:
                merged[category].append(row)
                by_logical[row["logical_key"]] = row
                by_fp.add(row["row_fingerprint"])
                summary["rows_inserted"] += 1
    if summary["conflicts_found"] and conflict_policy == "reject":
        summary.update(errors=["conflict_rejected"], exit_code=3)
        return summary
    for category, spec in _CATEGORY.items():
        key = "timestamp_utc" if category != "position_history" else "opened_at_utc"
        id_key = {"trade_history": "actual_trade_id", "order_history": "actual_order_id", "position_history": "actual_position_id"}[category]
        merged[category].sort(key=lambda row: (row.get(key, ""), row.get(id_key, "")))
    all_rows = [row for rows in accepted.values() for row in rows]
    summary["symbols"] = sorted({row.get("symbol", "") for row in all_rows if row.get("symbol")})
    for source_key, output_key in (("timestamp_utc", "date_range_utc"), ("timestamp_jst", "date_range_jst")):
        values = [row[source_key] for row in accepted["trade_history"] + accepted["order_history"] if row.get(source_key)]
        if values:
            summary[output_key] = {"min": min(values), "max": max(values)}
    canonical_outputs = [spec["output"] for spec in _CATEGORY.values()]
    summary["would_write_outputs"] = canonical_outputs if summary["rows_inserted"] or summary["rows_replaced"] else []
    summary["would_write_issues_file"] = bool(issues)
    if dry_run:
        summary["ok"] = True
        summary["outputs_unchanged"] = [spec["output"] for spec in _CATEGORY.values()]
        return summary
    if summary["rows_inserted"] == 0 and summary["rows_replaced"] == 0:
        if issues:
            issue_path = output_root / "manual_actual_trade_import_issues.csv"
            try:
                _atomic_write([(issue_path, ISSUE_HEADERS, issues)])
            except (OSError, RuntimeError, NotImplementedError):
                summary.update(errors=["output_io_failure"], exit_code=4)
                return summary
            summary["issues_file"] = issue_path.name
        summary["ok"] = True
        summary["outputs_unchanged"] = [spec["output"] for spec in _CATEGORY.values()]
        return summary
    try:
        paths_rows = [(output_root / spec["output"], spec["headers"], merged[category]) for category, spec in _CATEGORY.items()]
        issue_path = output_root / "manual_actual_trade_import_issues.csv"
        if issues:
            paths_rows.append((issue_path, ISSUE_HEADERS, issues))
        _atomic_write(paths_rows)
        summary["outputs_written"] = [spec["output"] for spec in _CATEGORY.values()]
        if issues:
            summary["issues_file"] = issue_path.name
    except (OSError, RuntimeError, NotImplementedError):
        summary.update(errors=["output_io_failure"], exit_code=4)
        return summary
    summary["ok"] = True
    return summary


def import_mexc_actual_trades(*, input_dir: Path, output_dir: Path | None = None, dry_run: bool = False, conflict_policy: str = "reject", cli_alias_used: bool = True) -> dict[str, Any]:
    return import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=dry_run, conflict_policy=conflict_policy, cli_alias_used=cli_alias_used)
