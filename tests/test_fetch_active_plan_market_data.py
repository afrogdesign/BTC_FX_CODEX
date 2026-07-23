from __future__ import annotations

import csv
import io
import math
import sys
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.fetch_active_plan_market_data import (  # noqa: E402
    OUTPUT_COLUMNS,
    convert_ohlcv_to_diagnostic_rows,
    main,
)
from src.data.fetcher import DataFetchError, FetchConfig, fetch_klines_historical  # noqa: E402


class FetchActivePlanMarketDataTest(unittest.TestCase):
    def test_historical_fetch_chunks_in_forward_non_overlapping_ranges(self) -> None:
        start = datetime(2024, 6, 8, 0, 0, tzinfo=timezone.utc)
        timestamps = [int((start + timedelta(minutes=15 * i)).timestamp() * 1000) for i in range(5)]
        requests = []

        def request(_method, _url, *, params, **_kwargs):
            requests.append(params)
            first = int(params["start"] * 1000)
            last = int(params["end"] * 1000)
            rows = []
            for timestamp in timestamps:
                if first <= timestamp <= last:
                    rows.append([timestamp, 1, 2, 0, 1.5, 10])
            return {"data": rows}

        cfg = FetchConfig("https://example.test", "BTC_USDT", 1, 1, 0)
        with patch("src.data.fetcher._request_json", side_effect=request):
            frame = fetch_klines_historical(
                cfg,
                "15m",
                timestamps[0],
                timestamps[-1],
                max_rows_per_request=2,
            )

        self.assertEqual(len(frame), 5)
        self.assertEqual(frame["timestamp"].tolist(), timestamps)
        self.assertEqual([(item["start"], item["end"], set(item)) for item in requests], [
            (timestamps[0] // 1000, timestamps[1] // 1000, {"interval", "start", "end"}),
            (timestamps[2] // 1000, timestamps[3] // 1000, {"interval", "start", "end"}),
            (timestamps[4] // 1000, timestamps[4] // 1000, {"interval", "start", "end"}),
        ])

    def test_historical_fetch_deduplicates_identical_rows_and_rejects_conflicts(self) -> None:
        start = int(datetime(2024, 6, 8, tzinfo=timezone.utc).timestamp() * 1000)
        rows = [[start, 1, 2, 0, 1, 10], [start, 1, 2, 0, 1, 10], [start + 900000, 1, 2, 0, 1, 10]]
        cfg = FetchConfig("https://example.test", "BTC_USDT", 1, 1, 0)
        with patch("src.data.fetcher._request_json", return_value={"data": rows}):
            frame = fetch_klines_historical(cfg, "15m", start, start + 900000, max_rows_per_request=10)
        self.assertEqual(len(frame), 2)

        conflict = [[start, 1, 2, 0, 1, 10], [start, 1, 3, 0, 1, 10], [start + 900000, 1, 2, 0, 1, 10]]
        with patch("src.data.fetcher._request_json", return_value={"data": conflict}):
            with self.assertRaisesRegex(DataFetchError, "historical_ohlcv_conflict"):
                fetch_klines_historical(cfg, "15m", start, start + 900000, max_rows_per_request=10)

    def test_historical_validation_fails_before_request(self) -> None:
        start = 1717804800000
        cfg = FetchConfig("https://example.test", "BTC_USDT", 1, 1, 0)
        with patch("src.data.fetcher._request_json") as request:
            with self.assertRaisesRegex(ValueError, "historical_range_reversed"):
                fetch_klines_historical(cfg, "15m", start + 900000, start)
            with self.assertRaisesRegex(ValueError, "historical_range_not_aligned"):
                fetch_klines_historical(cfg, "15m", start + 1, start + 900000)
            for value in (0, 2001, True, 2.0, "2"):
                with self.subTest(page_size=value):
                    with self.assertRaises((ValueError, TypeError)):
                        fetch_klines_historical(cfg, "15m", start, start, max_rows_per_request=value)
            for value in (True, 1.0, "1717804800000"):
                with self.subTest(start=value):
                    with self.assertRaises(TypeError):
                        fetch_klines_historical(cfg, "15m", value, start)
            for value in (True, 1.0, "1717804800000"):
                with self.subTest(end=value):
                    with self.assertRaises(TypeError):
                        fetch_klines_historical(cfg, "15m", start, value)
        request.assert_not_called()

    def test_historical_rejects_non_finite_and_out_of_range_values(self) -> None:
        start = 1717804800000
        cfg = FetchConfig("https://example.test", "BTC_USDT", 1, 1, 0)
        fields = {"timestamp": start, "open": 1, "high": 2, "low": 0, "close": 1.5, "volume": 10}
        for field, value in [("timestamp", math.nan), ("timestamp", math.inf), ("open", math.nan), ("high", -math.inf), ("low", math.inf), ("close", math.nan), ("volume", -math.inf)]:
            row = dict(fields); row[field] = value
            with self.subTest(field=field, value=value):
                with patch("src.data.fetcher._request_json", return_value={"data": [row]}):
                    with self.assertRaises(DataFetchError):
                        fetch_klines_historical(cfg, "15m", start, start)
        for row in ([fields, {**fields, "timestamp": start + 1800000}], [{**fields, "timestamp": start - 900000}]):
            with patch("src.data.fetcher._request_json", return_value={"data": row}):
                with self.assertRaises(DataFetchError):
                    fetch_klines_historical(cfg, "15m", start, start + 900000)

    def test_cli_utc_pairing_and_offsets_fail_before_fetch(self) -> None:
        invalid_pairs = [
            ["--start-utc", "2024-06-08T00:00:00", "--end-utc", "2024-06-08T00:15:00Z"],
            ["--start-utc", "2024-06-08T09:00:00+09:00", "--end-utc", "2024-06-08T00:15:00Z"],
            ["--start-utc", "2024-06-08T00:00:00-05:00", "--end-utc", "2024-06-08T00:15:00Z"],
            ["--start-utc", "2024-06-08T00:00:00Z"],
            ["--end-utc", "2024-06-08T00:15:00Z"],
        ]
        with patch("tools.fetch_active_plan_market_data.fetch_klines_historical") as historical:
            for args in invalid_pairs:
                with self.subTest(args=args), self.assertRaises(SystemExit):
                    main(args)
        historical.assert_not_called()

    def test_cli_accepts_z_and_explicit_utc_and_prints_mode_summary(self) -> None:
        sample = pd.DataFrame([{"timestamp": 1717804800000, "open": 1, "high": 2, "low": 0, "close": 1.5, "volume": 10}])
        with TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "hist.csv"
            with patch("tools.fetch_active_plan_market_data.fetch_klines_historical", return_value=sample):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    main(["--output-csv", str(out), "--start-utc", "2024-06-08T00:00:00+00:00", "--end-utc", "2024-06-08T00:00:00Z"])
            text = stdout.getvalue()
            self.assertIn("fetch_mode=historical", text)
            self.assertIn("requested_start_utc=2024-06-08T00:00:00+00:00", text)
            self.assertIn("expected_row_count=1", text)

    def test_latest_summary_keeps_latest_fetch_and_adds_mode(self) -> None:
        sample = pd.DataFrame([{"timestamp": 1717804800000, "open": 1, "high": 2, "low": 0, "close": 1.5, "volume": 10}])
        with TemporaryDirectory() as tmpdir, patch("tools.fetch_active_plan_market_data.fetch_klines", return_value=sample):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                main(["--output-csv", str(Path(tmpdir) / "latest.csv")])
        self.assertIn("fetch_mode=latest", stdout.getvalue())

    def test_historical_cli_uses_bounded_fetch_without_changing_schema(self) -> None:
        sample_df = pd.DataFrame([{"timestamp": 1717804800000, "open": 1, "high": 2, "low": 0, "close": 1.5, "volume": 10}])
        with TemporaryDirectory() as tmpdir:
            output_csv = Path(tmpdir) / "ohlcv.csv"
            with patch("tools.fetch_active_plan_market_data.fetch_klines_historical", return_value=sample_df) as mock_fetch:
                with redirect_stdout(io.StringIO()):
                    result = main([
                        "--output-csv", str(output_csv), "--start-utc", "2024-06-08T00:00:00Z",
                        "--end-utc", "2024-06-08T00:15:00Z", "--max-rows-per-request", "2000",
                    ])
            self.assertEqual(result, 0)
            mock_fetch.assert_called_once()
            args, kwargs = mock_fetch.call_args
            self.assertEqual(args[0].symbol, "BTC_USDT")
            self.assertEqual(kwargs["start_utc_ms"], 1717804800000)
            self.assertEqual(kwargs["end_utc_ms"], 1717805700000)
            self.assertEqual(kwargs["max_rows_per_request"], 2000)
            with output_csv.open(newline="", encoding="utf-8") as fp:
                self.assertEqual(csv.DictReader(fp).fieldnames, OUTPUT_COLUMNS)
    def test_convert_ohlcv_to_diagnostic_rows_exact_schema_and_sorting(self) -> None:
        first_utc = datetime(2024, 6, 8, 0, 0, tzinfo=timezone.utc)
        second_utc = datetime(2024, 6, 8, 0, 15, tzinfo=timezone.utc)
        df = pd.DataFrame(
            [
                {
                    "timestamp": int(second_utc.timestamp() * 1000),
                    "open": 101.0,
                    "high": 111.0,
                    "low": 99.5,
                    "close": 107.5,
                    "volume": 23.0,
                },
                {
                    "timestamp": int(first_utc.timestamp() * 1000),
                    "open": 100.0,
                    "high": 110.0,
                    "low": 98.5,
                    "close": 106.5,
                    "volume": 22.0,
                },
            ]
        )

        rows = convert_ohlcv_to_diagnostic_rows(
            df,
            source_label="exchange-auto-public",
            interval="15m",
            symbol="BTC_USDT",
        )

        self.assertEqual(
            rows,
            [
                {
                    "timestamp_jst": first_utc.astimezone(timezone(timedelta(hours=9))).isoformat(),
                    "timestamp_utc": first_utc.isoformat(),
                    "open": 100.0,
                    "high": 110.0,
                    "low": 98.5,
                    "close": 106.5,
                    "volume": 22.0,
                    "source": "exchange-auto-public",
                    "interval": "15m",
                    "symbol": "BTC_USDT",
                },
                {
                    "timestamp_jst": second_utc.astimezone(timezone(timedelta(hours=9))).isoformat(),
                    "timestamp_utc": second_utc.isoformat(),
                    "open": 101.0,
                    "high": 111.0,
                    "low": 99.5,
                    "close": 107.5,
                    "volume": 23.0,
                    "source": "exchange-auto-public",
                    "interval": "15m",
                    "symbol": "BTC_USDT",
                },
            ],
        )
        self.assertEqual(list(rows[0].keys()), OUTPUT_COLUMNS)

    def test_main_writes_csv_with_required_columns_and_creates_parent_dir(self) -> None:
        utc_dt = datetime(2024, 6, 8, 0, 0, tzinfo=timezone.utc)
        sample_df = pd.DataFrame(
            [
                {
                    "timestamp": int(utc_dt.timestamp() * 1000),
                    "open": 100.0,
                    "high": 110.0,
                    "low": 98.0,
                    "close": 106.0,
                    "volume": 21.5,
                }
            ]
        )

        with TemporaryDirectory() as tmpdir:
            output_csv = Path(tmpdir) / "nested" / "diagnostic" / "active_plan_intraperiod_ohlcv.csv"
            with patch("tools.fetch_active_plan_market_data.fetch_klines", return_value=sample_df) as mock_fetch:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    result = main(
                        [
                            "--output-csv",
                            str(output_csv),
                            "--symbol",
                            "BTC_USDT",
                            "--source-label",
                            "exchange-auto-public",
                        ]
                    )

            self.assertEqual(result, 0)
            self.assertTrue(output_csv.exists())
            self.assertTrue(output_csv.parent.exists())
            mock_fetch.assert_called_once()
            args, kwargs = mock_fetch.call_args
            self.assertEqual(kwargs, {"interval": "15m", "limit": 500})
            self.assertEqual(args[0].symbol, "BTC_USDT")
            self.assertEqual(args[0].base_url, "https://contract.mexc.com")
            self.assertEqual(args[0].timeout_sec, 5)
            self.assertEqual(args[0].retry_count, 3)
            self.assertEqual(args[0].request_interval_sec, 0.3)

            with output_csv.open("r", newline="", encoding="utf-8") as fp:
                reader = csv.DictReader(fp)
                self.assertEqual(reader.fieldnames, OUTPUT_COLUMNS)
                rows = list(reader)

            self.assertEqual(len(rows), 1)
            self.assertEqual(
                rows[0],
                {
                    "timestamp_jst": "2024-06-08T09:00:00+09:00",
                    "timestamp_utc": "2024-06-08T00:00:00+00:00",
                    "open": "100.0",
                    "high": "110.0",
                    "low": "98.0",
                    "close": "106.0",
                    "volume": "21.5",
                    "source": "exchange-auto-public",
                    "interval": "15m",
                    "symbol": "BTC_USDT",
                },
            )


if __name__ == "__main__":
    unittest.main()
