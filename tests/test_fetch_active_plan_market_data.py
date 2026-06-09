from __future__ import annotations

import csv
import io
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


class FetchActivePlanMarketDataTest(unittest.TestCase):
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
