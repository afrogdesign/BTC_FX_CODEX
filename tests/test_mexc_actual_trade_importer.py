from __future__ import annotations

import csv
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
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

EXPECTED_TRADE_OUTPUT_HEADERS = [
    "actual_trade_id",
    "source_uid_hash",
    "source_file",
    "timestamp_jst",
    "symbol",
    "side",
    "order_type",
    "fill_qty_contract",
    "fill_qty_token",
    "fill_qty_value",
    "fill_price",
    "fee",
    "fee_asset",
    "role",
    "realized_pnl",
    "import_status",
]
EXPECTED_ORDER_OUTPUT_HEADERS = [
    "actual_order_id",
    "source_uid_hash",
    "source_file",
    "timestamp_jst",
    "symbol",
    "side",
    "leverage",
    "order_type",
    "filled_qty",
    "avg_fill_price",
    "realized_pnl",
    "fee",
    "status",
    "import_status",
]
EXPECTED_POSITION_OUTPUT_HEADERS = [
    "actual_position_id",
    "source_uid_hash",
    "source_file",
    "opened_at_jst",
    "closed_at_jst",
    "symbol",
    "side",
    "realized_pnl",
    "status",
    "import_status",
]


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


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BASE_DIR / "tools" / "log_feedback.py"), *args],
        cwd=BASE_DIR,
        check=True,
        capture_output=True,
        text=True,
    )


class MexcActualTradeImporterTest(unittest.TestCase):
    def test_normalizers_map_fields_and_mask_uids(self) -> None:
        trade_rows = normalize_mexc_trade_history(_mexc_trade_rows(), source_file="Trade History sample.xlsx")
        order_rows = normalize_mexc_order_history(_mexc_order_rows(), source_file="Order History sample.xlsx")
        position_rows = normalize_mexc_position_history(_mexc_position_rows(), source_file="Position History sample.xlsx")

        self.assertEqual(trade_rows[0]["source_file"], "Trade History sample.xlsx")
        self.assertEqual(trade_rows[0]["timestamp_jst"], "2026-07-01 09:15:00")
        self.assertEqual(trade_rows[0]["symbol"], "BTC_USDT")
        self.assertEqual(trade_rows[0]["fee_asset"], "USDT")
        self.assertTrue(trade_rows[0]["actual_trade_id"].startswith("tra_"))
        self.assertTrue(trade_rows[0]["source_uid_hash"].startswith("uid_"))
        self.assertNotIn("trade-uid-001", json.dumps(trade_rows, ensure_ascii=False))

        self.assertEqual(order_rows[0]["source_file"], "Order History sample.xlsx")
        self.assertEqual(order_rows[0]["leverage"], "20")
        self.assertEqual(order_rows[0]["status"], "Filled")
        self.assertTrue(order_rows[0]["actual_order_id"].startswith("ord_"))
        self.assertNotIn("order-uid-001", json.dumps(order_rows, ensure_ascii=False))

        self.assertEqual(position_rows[0]["source_file"], "Position History sample.xlsx")
        self.assertEqual(position_rows[0]["opened_at_jst"], "2026-07-01 08:00:00")
        self.assertEqual(position_rows[0]["status"], "Closed")
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
            )
            self.assertEqual(result.stdout.strip().count("\n"), 0)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["dry_run"], True)
            self.assertEqual(summary["missing_categories"], ["position_history"])
            self.assertFalse(output_dir.exists())
            self.assertNotIn("trade-uid-001", result.stdout)
            self.assertNotIn("order-uid-001", result.stdout)

    def test_import_function_handles_missing_category_without_crashing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir(parents=True)

            _write_minimal_xlsx(input_dir / "MEXC Position History 20260701.xlsx", POSITION_HEADERS, _mexc_position_rows())

            summary = import_mexc_actual_trades(input_dir=input_dir, output_dir=output_dir, dry_run=False)
            self.assertEqual(summary["missing_categories"], ["trade_history", "order_history"])
            self.assertTrue((output_dir / "manual_actual_trades.csv").exists())
            self.assertTrue((output_dir / "manual_actual_orders.csv").exists())
            self.assertTrue((output_dir / "manual_actual_positions.csv").exists())
            with (output_dir / "manual_actual_positions.csv").open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(len(rows), 1)
            self.assertNotIn("position-uid-001", json.dumps(rows, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
