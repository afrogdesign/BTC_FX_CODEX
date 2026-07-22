from __future__ import annotations

import csv
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import mock
from xml.sax.saxutils import escape

import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from tools.log_feedback import (  # noqa: E402
    import_mexc_actual_trades,
    normalize_mexc_order_history,
    normalize_mexc_position_history,
    normalize_mexc_trade_history,
)
from src.feedback.manual_actual_trade_importer import (  # noqa: E402
    import_manual_actual_trades,
    ORDER_HEADERS as CANONICAL_ORDER_HEADERS,
    POSITION_HEADERS as CANONICAL_POSITION_HEADERS,
    TRADE_HEADERS as CANONICAL_TRADE_HEADERS,
)
import src.feedback.manual_actual_trade_importer as importer  # noqa: E402


TRADE_HEADERS = [
    "UID",
    "時間(UTC+09:00)",
    "先物取引ペア",
    "方向",
    "注文の種類",
    "約定数量 (枚)",
    "約定数量 (トークン)",
    "約定数量 (金額)",
    "約定価格",
    "取引手数料",
    "手数料支払い暗号資産",
    "役割",
    "決済損益",
]
ORDER_HEADERS = [
    "UID",
    "時間(UTC+09:00)",
    "先物取引ペア",
    "方向",
    "レバレッジ",
    "注文の種類",
    "約定数量",
    "平均約定価格",
    "決済損益",
    "手数料",
    "ステータス",
]
POSITION_HEADERS = [
    "UID",
    "取引ペア",
    "オープン時間(UTC+09:00)",
    "決済時刻",
    "方向",
    "実現損益",
    "ステータス",
]

EXPECTED_TRADE_OUTPUT_HEADERS = CANONICAL_TRADE_HEADERS
EXPECTED_ORDER_OUTPUT_HEADERS = CANONICAL_ORDER_HEADERS
EXPECTED_POSITION_OUTPUT_HEADERS = CANONICAL_POSITION_HEADERS


def _col_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(ord("A") + remainder) + name
    return name


def _write_minimal_xlsx(path: Path, headers: list[str], rows: list[dict[str, Any]]) -> None:
    sheet_rows = [headers, *[[row.get(header, "") for header in headers] for row in rows]]
    sheet_xml_rows = []
    for row_index, row_values in enumerate(sheet_rows, start=1):
        cells = []
        for col_index, value in enumerate(row_values, start=1):
            cell_ref = f"{_col_name(col_index)}{row_index}"
            text = escape("" if value is None else str(value))
            cells.append(f'<c r="{cell_ref}" t="inlineStr"><is><t>{text}</t></is></c>')
        sheet_xml_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(sheet_xml_rows)}</sheetData>"
        "</worksheet>"
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets><sheet name=\"Sheet1\" sheetId=\"1\" r:id=\"rId1\"/></sheets>"
        "</workbook>"
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    )
    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", root_rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def _write_broken_xlsx(path: Path, *, missing_workbook: bool = False, malformed_sheet: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if not missing_workbook:
            zf.writestr(
                "xl/workbook.xml",
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>',
            )
            zf.writestr(
                "xl/_rels/workbook.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>',
            )
        zf.writestr("xl/worksheets/sheet1.xml", "<worksheet>" if malformed_sheet else '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>')


def _write_ambiguous_xlsx(path: Path, headers: list[str], rows: list[dict[str, Any]]) -> None:
    _write_minimal_xlsx(path, headers, rows)
    with zipfile.ZipFile(path, "r") as source:
        members = {name: source.read(name) for name in source.namelist()}
    members["xl/workbook.xml"] = (
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="First" sheetId="1" r:id="rId1"/><sheet name="Second" sheetId="2" r:id="rId2"/></sheets></workbook>'
    ).encode()
    members["xl/_rels/workbook.xml.rels"] = (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="worksheets/sheet1.xml"/></Relationships>'
    ).encode()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in members.items():
            target.writestr(name, data)


def _mexc_trade_rows() -> list[dict[str, str]]:
    return [
        {
            "UID": "trade-uid-001",
            "時間(UTC+09:00)": "2026-07-01 09:15:00",
            "先物取引ペア": "BTC_USDT",
            "方向": "BUY",
            "注文の種類": "Limit",
            "約定数量 (枚)": "2",
            "約定数量 (トークン)": "0.020",
            "約定数量 (金額)": "2500",
            "約定価格": "125000",
            "取引手数料": "1.25",
            "手数料支払い暗号資産": "USDT",
            "役割": "Maker",
            "決済損益": "12.5",
        }
    ]


def _mexc_order_rows() -> list[dict[str, str]]:
    return [
        {
            "UID": "order-uid-001",
            "時間(UTC+09:00)": "2026-07-01 09:15:00",
            "先物取引ペア": "BTC_USDT",
            "方向": "SELL",
            "レバレッジ": "20",
            "注文の種類": "Market",
            "約定数量": "2",
            "平均約定価格": "124800",
            "決済損益": "-3.25",
            "手数料": "0.88",
            "ステータス": "Filled",
        }
    ]


def _mexc_position_rows() -> list[dict[str, str]]:
    return [
        {
            "UID": "position-uid-001",
            "取引ペア": "BTC_USDT",
            "オープン時間(UTC+09:00)": "2026-07-01 08:00:00",
            "決済時刻": "2026-07-01 09:30:00",
            "方向": "LONG",
            "実現損益": "9.75",
            "ステータス": "Closed",
        }
    ]


def _run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BASE_DIR / "tools" / "log_feedback.py"), *args],
        cwd=BASE_DIR,
        check=check,
        capture_output=True,
        text=True,
    )


class MexcActualTradeImporterTest(unittest.TestCase):
    def test_normalizers_map_fields_and_mask_uids(self) -> None:
        trade_rows = normalize_mexc_trade_history(_mexc_trade_rows(), source_file="Trade History sample.xlsx")
        order_rows = normalize_mexc_order_history(_mexc_order_rows(), source_file="Order History sample.xlsx")
        position_rows = normalize_mexc_position_history(_mexc_position_rows(), source_file="Position History sample.xlsx")

        self.assertEqual(trade_rows[0]["source_file"], "Trade History sample.xlsx")
        self.assertEqual(trade_rows[0]["timestamp_jst"], "2026-07-01T09:15:00+09:00")
        self.assertEqual(trade_rows[0]["timestamp_utc"], "2026-07-01T00:15:00Z")
        self.assertEqual(trade_rows[0]["symbol"], "BTCUSDT")
        self.assertEqual(trade_rows[0]["fee_asset"], "USDT")
        self.assertTrue(trade_rows[0]["actual_trade_id"].startswith("tra_"))
        self.assertEqual(len(trade_rows[0]["source_uid_hash"]), 64)
        self.assertNotIn("trade-uid-001", json.dumps(trade_rows, ensure_ascii=False))

        self.assertEqual(order_rows[0]["source_file"], "Order History sample.xlsx")
        self.assertEqual(order_rows[0]["leverage"], "20")
        self.assertEqual(order_rows[0]["status"], "filled")
        self.assertTrue(order_rows[0]["actual_order_id"].startswith("ord_"))
        self.assertNotIn("order-uid-001", json.dumps(order_rows, ensure_ascii=False))

        self.assertEqual(position_rows[0]["source_file"], "Position History sample.xlsx")
        self.assertEqual(position_rows[0]["opened_at_jst"], "2026-07-01T08:00:00+09:00")
        self.assertEqual(position_rows[0]["status"], "closed")
        self.assertTrue(position_rows[0]["actual_position_id"].startswith("pos_"))
        self.assertNotIn("position-uid-001", json.dumps(position_rows, ensure_ascii=False))

    def test_cli_imports_xlsx_and_writes_expected_headers(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir(parents=True)

            _write_minimal_xlsx(input_dir / "MEXC Trade History 20260701.xlsx", TRADE_HEADERS, _mexc_trade_rows())
            _write_minimal_xlsx(input_dir / "MEXC Order History 20260701.xlsx", ORDER_HEADERS, _mexc_order_rows())
            _write_minimal_xlsx(input_dir / "MEXC Position History 20260701.xlsx", POSITION_HEADERS, _mexc_position_rows())

            result = _run_cli(
                "import-mexc-actual-trades",
                "--input-dir",
                str(input_dir),
                "--output-dir",
                str(output_dir),
                "--stdout-json",
            )
            summary = json.loads(result.stdout)
            self.assertEqual(summary["total_rows"], 3)
            self.assertEqual(summary["missing_categories"], [])
            self.assertEqual(summary["sheets_read"], {"trade_history": 1, "order_history": 1, "position_history": 1})
            self.assertNotIn("trade-uid-001", result.stdout)
            self.assertNotIn("order-uid-001", result.stdout)
            self.assertNotIn("position-uid-001", result.stdout)

            trade_csv = output_dir / "manual_actual_trades.csv"
            order_csv = output_dir / "manual_actual_orders.csv"
            position_csv = output_dir / "manual_actual_positions.csv"
            self.assertTrue(trade_csv.exists())
            self.assertTrue(order_csv.exists())
            self.assertTrue(position_csv.exists())

            with trade_csv.open("r", newline="", encoding="utf-8") as fp:
                self.assertEqual(next(csv.reader(fp)), EXPECTED_TRADE_OUTPUT_HEADERS)
            with order_csv.open("r", newline="", encoding="utf-8") as fp:
                self.assertEqual(next(csv.reader(fp)), EXPECTED_ORDER_OUTPUT_HEADERS)
            with position_csv.open("r", newline="", encoding="utf-8") as fp:
                self.assertEqual(next(csv.reader(fp)), EXPECTED_POSITION_OUTPUT_HEADERS)

    def test_dry_run_writes_no_csv_and_reports_missing_category(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir(parents=True)

            _write_minimal_xlsx(input_dir / "MEXC Trade History 20260701.xlsx", TRADE_HEADERS, _mexc_trade_rows())
            _write_minimal_xlsx(input_dir / "MEXC Order History 20260701.xlsx", ORDER_HEADERS, _mexc_order_rows())

            result = _run_cli(
                "import-mexc-actual-trades",
                "--input-dir",
                str(input_dir),
                "--output-dir",
                str(output_dir),
                "--dry-run",
                "--stdout-json",
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout.strip().count("\n"), 0)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["dry_run"], True)
            self.assertEqual(summary["missing_categories"], ["position_history"])
            self.assertEqual(summary["sheets_read"], {"trade_history": 0, "order_history": 0, "position_history": 0})
            self.assertEqual(summary["would_write_outputs"], [])
            self.assertFalse(summary["would_write_issues_file"])
            self.assertFalse(output_dir.exists())

    def test_dry_run_planning_fields_cover_new_duplicate_and_issue_only_batches(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            fresh = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertEqual(fresh["would_write_outputs"], ["manual_actual_trades.csv", "manual_actual_orders.csv", "manual_actual_positions.csv"])
            self.assertFalse(fresh["would_write_issues_file"])
            self.assertFalse(output_dir.exists())
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            duplicate = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertEqual(duplicate["would_write_outputs"], [])
            self.assertFalse(duplicate["would_write_issues_file"])
            bad = {**_mexc_trade_rows()[0], "UID": "bad-uid", "約定価格": "not-number"}
            _write_minimal_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS, [_mexc_trade_rows()[0], bad])
            issue_only = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertEqual(issue_only["would_write_outputs"], [])
            self.assertTrue(issue_only["would_write_issues_file"])

    def test_import_function_handles_missing_category_without_crashing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir(parents=True)

            _write_minimal_xlsx(input_dir / "MEXC Position History 20260701.xlsx", POSITION_HEADERS, _mexc_position_rows())

            summary = import_mexc_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=False)
            self.assertEqual(summary["missing_categories"], ["trade_history", "order_history"])
            self.assertEqual(summary["exit_code"], 2)
            self.assertFalse(output_dir.exists())

    def _complete_batch(self, root: Path, *, trade_rows: list[dict[str, str]] | None = None) -> tuple[Path, Path]:
        input_dir = root / "input"
        output_dir = root / "output"
        input_dir.mkdir(parents=True, exist_ok=True)
        _write_minimal_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS, trade_rows or _mexc_trade_rows())
        _write_minimal_xlsx(input_dir / "Order History.xlsx", ORDER_HEADERS, _mexc_order_rows())
        _write_minimal_xlsx(input_dir / "Position History.xlsx", POSITION_HEADERS, _mexc_position_rows())
        return input_dir, output_dir

    def test_canonical_cli_and_legacy_alias_share_implementation(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            canonical = _run_cli("import-manual-actual-trades", "--input-dir", str(input_dir), "--output-dir", str(output_dir), "--stdout-json")
            legacy = _run_cli("import-mexc-actual-trades", "--input-dir", str(input_dir), "--output-dir", str(root / "alias-output"), "--dry-run", "--stdout-json")
            self.assertFalse(json.loads(canonical.stdout)["cli_alias_used"])
            self.assertTrue(json.loads(legacy.stdout)["cli_alias_used"])

    def test_same_file_reimport_is_duplicate_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            first = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            second = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(first["rows_inserted"], 3)
            self.assertEqual(second["duplicate_rows_skipped"], 3)
            self.assertEqual(second["rows_inserted"], 0)

    def test_overlapping_export_merges_only_new_logical_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            rows = _mexc_trade_rows() + [{**_mexc_trade_rows()[0], "UID": "trade-uid-002", "時間(UTC+09:00)": "2026-07-01 10:15:00"}]
            _write_minimal_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS, rows)
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["duplicate_rows_skipped"], 3)
            self.assertEqual(summary["rows_inserted"], 1)
            with (output_dir / "manual_actual_trades.csv").open(newline="", encoding="utf-8") as fp:
                self.assertEqual(len(list(csv.DictReader(fp))), 2)

    def test_corrected_export_rejects_without_mutation_and_replace_audits(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            before = (output_dir / "manual_actual_trades.csv").read_bytes()
            corrected = [{**_mexc_trade_rows()[0], "取引手数料": "2.00"}]
            _write_minimal_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS, corrected)
            rejected = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, conflict_policy="reject")
            self.assertEqual(rejected["exit_code"], 3)
            self.assertEqual((output_dir / "manual_actual_trades.csv").read_bytes(), before)
            replaced = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, conflict_policy="replace")
            self.assertEqual(replaced["rows_replaced"], 1)
            self.assertTrue((output_dir / "manual_actual_trade_import_issues.csv").exists())

    def test_malformed_date_and_numeric_are_rejected_not_zero(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            bad_trade = {**_mexc_trade_rows()[0], "時間(UTC+09:00)": "not-a-date", "約定価格": "not-a-number"}
            input_dir, output_dir = self._complete_batch(root, trade_rows=[bad_trade])
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["rows_rejected"], 1)
            self.assertEqual(summary["rows_accepted"], 2)
            with (output_dir / "manual_actual_orders.csv").open(newline="", encoding="utf-8") as fp:
                self.assertEqual(len(list(csv.DictReader(fp))), 1)
            self.assertTrue((output_dir / "manual_actual_trade_import_issues.csv").exists())

    def test_comma_numeric_fee_and_pnl_sign_are_normalized(self) -> None:
        row = {**_mexc_trade_rows()[0], "約定価格": "125,000.50", "取引手数料": "-1.25", "決済損益": "-12.50"}
        normalized = normalize_mexc_trade_history([row], source_file="Trade History.xlsx")[0]
        self.assertEqual(normalized["fill_price"], "125000.50")
        self.assertEqual(normalized["fee"], "1.25")
        self.assertEqual(normalized["realized_pnl"], "-12.50")

    def test_non_finite_numeric_values_are_rejected(self) -> None:
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "malformed_numeric"):
                    normalize_mexc_trade_history([{**_mexc_trade_rows()[0], "約定価格": value}], source_file="Trade History.xlsx")
        for value in ("NaN USDT", "Infinity USDT"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "malformed_numeric"):
                    normalize_mexc_position_history([{**_mexc_position_rows()[0], "実現損益": value}], source_file="Position History.xlsx")
        finite = normalize_mexc_position_history([{**_mexc_position_rows()[0], "実現損益": "-9.75 USDT"}], source_file="Position History.xlsx")[0]
        self.assertEqual(finite["realized_pnl"], "-9.75")

    def test_symbol_alias_and_direction_mapping(self) -> None:
        row = {**_mexc_trade_rows()[0], "先物取引ペア": "BTC/USDT", "方向": "Open Long"}
        normalized = normalize_mexc_trade_history([row], source_file="Trade History.xlsx")[0]
        self.assertEqual(normalized["symbol"], "BTCUSDT")
        self.assertEqual(normalized["side"], "long")
        self.assertEqual(normalized["transaction_side"], "buy")
        self.assertEqual(normalized["position_action"], "open")

    def test_latest_direction_and_numeric_presentation_aliases_are_exact(self) -> None:
        expected = {
            "Long Buy": ("long", "buy", "open"),
            "Long Sell": ("long", "sell", "close"),
            "Short Sell": ("short", "sell", "open"),
            "Short Buy": ("short", "buy", "close"),
        }
        for token, semantics in expected.items():
            with self.subTest(token=token):
                row = {**_mexc_trade_rows()[0], "方向": token}
                normalized = normalize_mexc_trade_history([row], source_file="Trade History.xlsx")[0]
                self.assertEqual((normalized["side"], normalized["transaction_side"], normalized["position_action"]), semantics)
        position = {**_mexc_position_rows()[0], "実現損益": "9.75 USDT"}
        self.assertEqual(normalize_mexc_position_history([position], source_file="Position History.xlsx")[0]["realized_pnl"], "9.75")

    def test_order_header_aliases_and_ambiguous_alias_fail_closed(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir()
            alias_headers = ["約定数量 (枚)" if h == "約定数量" else "取引手数料" if h == "手数料" else h for h in ORDER_HEADERS]
            _write_minimal_xlsx(input_dir / "MEXC Trade History.xlsx", TRADE_HEADERS, _mexc_trade_rows())
            _write_minimal_xlsx(input_dir / "MEXC Order History.xlsx", alias_headers, [{**_mexc_order_rows()[0], "約定数量 (枚)": "2", "取引手数料": "0.88"}])
            _write_minimal_xlsx(input_dir / "MEXC Position History.xlsx", POSITION_HEADERS, _mexc_position_rows())
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertTrue(summary["ok"])
            self.assertEqual(summary["rows_accepted"], 3)

            ambiguous = [*ORDER_HEADERS, "約定数量 (枚)"]
            _write_minimal_xlsx(input_dir / "MEXC Order History.xlsx", ambiguous, [{**_mexc_order_rows()[0], "約定数量 (枚)": "2"}])
            rejected = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertFalse(rejected["ok"])
            self.assertIn("ambiguous_header_alias", rejected["errors"])

    def test_unknown_direction_and_symbol_are_rejected(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            bad_direction = {**_mexc_trade_rows()[0], "方向": "sideways"}
            input_dir, output_dir = self._complete_batch(root, trade_rows=[bad_direction])
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["rows_rejected"], 1)
        with self.assertRaisesRegex(ValueError, "unsupported_symbol"):
            normalize_mexc_trade_history([{**_mexc_trade_rows()[0], "先物取引ペア": "ETH_USDT"}], source_file="Trade History.xlsx")

    def test_fee_absent_and_open_closed_position_consistency(self) -> None:
        row = {**_mexc_trade_rows()[0], "取引手数料": ""}
        normalized = normalize_mexc_trade_history([row], source_file="Trade History.xlsx")[0]
        self.assertEqual(normalized["fee"], "")
        open_row = {**_mexc_position_rows()[0], "決済時刻": "", "ステータス": "Open"}
        self.assertEqual(normalize_mexc_position_history([open_row], source_file="Position History.xlsx")[0]["status"], "open")
        with self.assertRaisesRegex(ValueError, "open_position_has_close_time"):
            normalize_mexc_position_history([_mexc_position_rows()[0] | {"ステータス": "Open"}], source_file="Position History.xlsx")

    def test_uid_and_full_path_never_leak(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            result = _run_cli("import-manual-actual-trades", "--input-dir", str(input_dir), "--output-dir", str(output_dir), "--stdout-json")
            self.assertNotIn("trade-uid-001", result.stdout)
            self.assertNotIn(str(root), result.stdout)
            self.assertNotIn("trade-uid-001", json.dumps([path.read_text(encoding="utf-8") for path in output_dir.glob("*.csv")]))

    def test_filename_with_sensitive_digits_is_sanitized(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            source = input_dir / "Trade History account@example.com 20260701.xlsx"
            (input_dir / "Trade History.xlsx").rename(source)
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertTrue(summary["ok"])
            with (output_dir / "manual_actual_trades.csv").open(newline="", encoding="utf-8") as fp:
                row = next(csv.DictReader(fp))
            self.assertTrue(row["source_file"].startswith("mexc_trade_history_"))
            self.assertNotIn("account@example.com", row["source_file"])

    def test_existing_schema_mismatch_returns_four(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            output_dir.mkdir()
            (output_dir / "manual_actual_trades.csv").write_text("wrong,header\n", encoding="utf-8")
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["exit_code"], 4)
            self.assertIn("existing_output_schema_mismatch", summary["errors"])

    def test_unsupported_files_are_reported_without_private_data(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            (input_dir / "legacy.xls").write_bytes(b"unsupported")
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertEqual(len(summary["unsupported_files"]), 1)
            self.assertNotIn("legacy.xls", json.dumps(summary))
            self.assertTrue(summary["ok"])

    def test_malformed_zip_workbook_failure_is_safe(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            (input_dir / "Trade History.xlsx").write_bytes(b"not-a-zip")
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["exit_code"], 2)
            self.assertEqual(summary["errors"], ["unreadable_workbook"])
            self.assertFalse(output_dir.exists())

    def test_missing_workbook_xml_and_malformed_sheet_are_safe(self) -> None:
        for broken in ("missing_workbook", "malformed_sheet"):
            with self.subTest(broken=broken), TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                input_dir, output_dir = self._complete_batch(root)
                _write_broken_xlsx(input_dir / "Trade History.xlsx", missing_workbook=broken == "missing_workbook", malformed_sheet=broken == "malformed_sheet")
                summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
                self.assertEqual(summary["exit_code"], 2)
                self.assertEqual(summary["errors"], ["unreadable_workbook"])
                self.assertFalse(output_dir.exists())

    def test_missing_column_empty_sheet_and_ambiguous_sheet_are_input_errors(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            _write_minimal_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS[:-1], _mexc_trade_rows())
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["exit_code"], 2)
            self.assertIn("missing_required_column", summary["errors"])
            self.assertFalse(output_dir.exists())
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            _write_minimal_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS, [])
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["exit_code"], 2)
            self.assertIn("empty_sheet", summary["errors"])
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            _write_ambiguous_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS, _mexc_trade_rows())
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["exit_code"], 2)
            self.assertIn("ambiguous_sheet", summary["errors"])

    def test_unrelated_unsupported_file_warns_but_missing_required_xlsx_stops(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            (input_dir / "unrelated.csv").write_text("not imported", encoding="utf-8")
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertTrue(summary["ok"])
            self.assertEqual(len(summary["unsupported_files"]), 1)
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            (input_dir / "Trade History.xlsx").unlink()
            (input_dir / "Trade History.xls").write_bytes(b"legacy")
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertEqual(summary["exit_code"], 2)
            self.assertIn("trade_history", summary["missing_categories"])
            self.assertFalse(output_dir.exists())

    def test_transaction_rolls_back_existing_and_new_targets(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            original = {path.name: path.read_bytes() for path in output_dir.glob("manual_actual_*.csv")}
            issue_path = output_dir / "manual_actual_trade_import_issues.csv"
            replace = Path.replace
            failed = False

            def fail_orders(path: Path, target: Path) -> Path:
                nonlocal failed
                if target.name == "manual_actual_orders.csv" and not failed:
                    failed = True
                    raise OSError("intentional second-target failure")
                return replace(path, target)

            with mock.patch.object(Path, "replace", new=fail_orders):
                with self.assertRaises(OSError):
                    importer._atomic_write([
                        (output_dir / "manual_actual_trades.csv", CANONICAL_TRADE_HEADERS, []),
                        (output_dir / "manual_actual_orders.csv", CANONICAL_ORDER_HEADERS, []),
                        (output_dir / "manual_actual_positions.csv", CANONICAL_POSITION_HEADERS, []),
                    ])
            self.assertEqual({path.name: path.read_bytes() for path in output_dir.glob("manual_actual_*.csv")}, original)
            self.assertFalse(issue_path.exists())

    def test_transaction_removes_new_targets_after_failure(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "output"
            replace = Path.replace
            failed = False

            def fail_orders(path: Path, target: Path) -> Path:
                nonlocal failed
                if target.name == "manual_actual_orders.csv" and not failed:
                    failed = True
                    raise OSError("intentional second-target failure")
                return replace(path, target)

            with mock.patch.object(Path, "replace", new=fail_orders):
                with self.assertRaises(OSError):
                    importer._atomic_write([
                        (output_dir / "manual_actual_trades.csv", CANONICAL_TRADE_HEADERS, []),
                        (output_dir / "manual_actual_orders.csv", CANONICAL_ORDER_HEADERS, []),
                        (output_dir / "manual_actual_positions.csv", CANONICAL_POSITION_HEADERS, []),
                    ])
            self.assertFalse(output_dir.exists() and list(output_dir.glob("manual_actual_*.csv")))

    def test_duplicate_only_plus_rejection_updates_only_issues(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir, output_dir = self._complete_batch(root)
            import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            canonical_names = {"manual_actual_trades.csv", "manual_actual_orders.csv", "manual_actual_positions.csv"}
            before = {path.name: path.read_bytes() for path in output_dir.iterdir() if path.name in canonical_names}
            bad = {**_mexc_trade_rows()[0], "UID": "bad-uid", "約定価格": "not-number"}
            _write_minimal_xlsx(input_dir / "Trade History.xlsx", TRADE_HEADERS, [_mexc_trade_rows()[0], bad])
            summary = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir)
            self.assertTrue(summary["ok"])
            self.assertEqual(summary["rows_rejected"], 1)
            self.assertEqual(summary["outputs_unchanged"], ["manual_actual_trades.csv", "manual_actual_orders.csv", "manual_actual_positions.csv"])
            self.assertEqual({path.name: path.read_bytes() for path in output_dir.iterdir() if path.name in canonical_names}, before)
            self.assertEqual(summary["issues_file"], "manual_actual_trade_import_issues.csv")
            issue_path = output_dir / summary["issues_file"]
            issue_before = issue_path.read_bytes()
            issue_path.unlink()
            dry = import_manual_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=True)
            self.assertTrue(dry["ok"])
            self.assertFalse(issue_path.exists())
            self.assertNotEqual(issue_before, b"")

    def test_position_and_partial_order_semantics(self) -> None:
        partial = {**_mexc_order_rows()[0], "ステータス": "Partially Filled"}
        self.assertEqual(normalize_mexc_order_history([partial], source_file="Order History.xlsx")[0]["status"], "partially_filled")
        partial_close = {**_mexc_trade_rows()[0], "方向": "Close Short"}
        normalized = normalize_mexc_trade_history([partial_close], source_file="Trade History.xlsx")[0]
        self.assertEqual(normalized["side"], "short")
        self.assertEqual(normalized["transaction_side"], "buy")
        self.assertEqual(normalized["position_action"], "close")
        with self.assertRaisesRegex(ValueError, "closed_position_missing_close_time"):
            normalize_mexc_position_history([{**_mexc_position_rows()[0], "決済時刻": "", "ステータス": "Closed"}], source_file="Position History.xlsx")
        with self.assertRaisesRegex(ValueError, "close_before_open"):
            normalize_mexc_position_history([{**_mexc_position_rows()[0], "オープン時間(UTC+09:00)": "2026-07-01 10:00:00", "決済時刻": "2026-07-01 09:00:00"}], source_file="Position History.xlsx")


if __name__ == "__main__":
    unittest.main()
