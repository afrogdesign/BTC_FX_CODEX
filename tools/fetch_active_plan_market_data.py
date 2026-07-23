from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.data.fetcher import FetchConfig, fetch_klines, fetch_klines_historical


JST = ZoneInfo("Asia/Tokyo")
DEFAULT_INTERVAL = "15m"
DEFAULT_LIMIT = 500
DEFAULT_OUTPUT_CSV = Path("logs/csv/active_plan_intraperiod_ohlcv.csv")
DEFAULT_SYMBOL = "BTC_USDT"
DEFAULT_BASE_URL = "https://contract.mexc.com"
DEFAULT_SOURCE_LABEL = "exchange-auto-public"
DEFAULT_TIMEOUT_SEC = 5
DEFAULT_RETRY_COUNT = 3
DEFAULT_REQUEST_INTERVAL_SEC = 0.3
OUTPUT_COLUMNS = [
    "timestamp_jst",
    "timestamp_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
    "interval",
    "symbol",
]


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid positive integer: {value!r}") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"must be a positive integer: {value!r}")
    return parsed


def _non_negative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid float: {value!r}") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError(f"must be non-negative: {value!r}")
    return parsed


def _parse_utc_ms(value: str) -> int:
    text = value.strip()
    if not (text.endswith("Z") or text.endswith("+00:00")):
        raise argparse.ArgumentTypeError("timestamp must use UTC Z or +00:00")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid UTC timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("UTC timestamp requires timezone")
    if parsed.utcoffset() != timezone.utc.utcoffset(None):
        raise argparse.ArgumentTypeError("timestamp must be UTC")
    return int(parsed.astimezone(timezone.utc).timestamp() * 1000)


def _format_timestamp(timestamp_ms: int) -> tuple[str, str]:
    utc_dt = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
    jst_dt = utc_dt.astimezone(JST)
    return utc_dt.isoformat(), jst_dt.isoformat()


def convert_ohlcv_to_diagnostic_rows(
    ohlcv_df,
    *,
    source_label: str,
    interval: str,
    symbol: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if ohlcv_df is None or getattr(ohlcv_df, "empty", True):
        return rows

    records = ohlcv_df.to_dict(orient="records")
    records.sort(key=lambda row: int(row["timestamp"]))
    for record in records:
        timestamp_ms = int(record["timestamp"])
        timestamp_utc, timestamp_jst = _format_timestamp(timestamp_ms)
        rows.append(
            {
                "timestamp_jst": timestamp_jst,
                "timestamp_utc": timestamp_utc,
                "open": float(record["open"]),
                "high": float(record["high"]),
                "low": float(record["low"]),
                "close": float(record["close"]),
                "volume": float(record["volume"]),
                "source": source_label,
                "interval": interval,
                "symbol": symbol,
            }
        )
    return rows


def write_diagnostic_csv(output_csv: Path, rows: list[dict[str, object]]) -> Path:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_csv


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch public 15m OHLCV and write a local diagnostic CSV.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--interval", default=DEFAULT_INTERVAL, choices=[DEFAULT_INTERVAL])
    parser.add_argument("--limit", type=_positive_int, default=DEFAULT_LIMIT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--source-label", default=DEFAULT_SOURCE_LABEL)
    parser.add_argument("--timeout-sec", type=_positive_int, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument("--retry-count", type=_positive_int, default=DEFAULT_RETRY_COUNT)
    parser.add_argument("--request-interval-sec", type=_non_negative_float, default=DEFAULT_REQUEST_INTERVAL_SEC)
    parser.add_argument("--start-utc", type=_parse_utc_ms)
    parser.add_argument("--end-utc", type=_parse_utc_ms)
    parser.add_argument("--max-rows-per-request", type=_positive_int, default=2000)
    return parser


def _print_summary(output_csv: Path, rows: list[dict[str, object]], *, source_label: str, interval: str, symbol: str, fetch_mode: str, requested_start_utc: int | None = None, requested_end_utc: int | None = None, expected_row_count: int | None = None) -> None:
    print(f"output_path={output_csv}")
    print(f"fetch_mode={fetch_mode}")
    print(f"row_count={len(rows)}")
    if rows:
        print(f"timestamp_min_utc={rows[0]['timestamp_utc']}")
        print(f"timestamp_max_utc={rows[-1]['timestamp_utc']}")
    print(f"source={source_label}")
    print(f"interval={interval}")
    print(f"symbol={symbol}")
    if fetch_mode == "historical":
        print(f"requested_start_utc={_format_timestamp(requested_start_utc)[0] if requested_start_utc is not None else ''}")
        print(f"requested_end_utc={_format_timestamp(requested_end_utc)[0] if requested_end_utc is not None else ''}")
        print(f"expected_row_count={expected_row_count}")
        print(f"actual_row_count={len(rows)}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    cfg = FetchConfig(
        base_url=args.base_url,
        symbol=args.symbol,
        timeout_sec=args.timeout_sec,
        retry_count=args.retry_count,
        request_interval_sec=args.request_interval_sec,
    )
    if (args.start_utc is None) != (args.end_utc is None):
        parser.error("--start-utc and --end-utc must be provided together")
    if args.start_utc is not None:
        ohlcv_df = fetch_klines_historical(
            cfg,
            interval=args.interval,
            start_utc_ms=args.start_utc,
            end_utc_ms=args.end_utc,
            max_rows_per_request=args.max_rows_per_request,
        )
    else:
        ohlcv_df = fetch_klines(cfg, interval=args.interval, limit=args.limit)
    rows = convert_ohlcv_to_diagnostic_rows(
        ohlcv_df,
        source_label=args.source_label,
        interval=args.interval,
        symbol=args.symbol,
    )
    write_diagnostic_csv(args.output_csv, rows)
    _print_summary(
        args.output_csv,
        rows,
        source_label=args.source_label,
        interval=args.interval,
        symbol=args.symbol,
        fetch_mode="historical" if args.start_utc is not None else "latest",
        requested_start_utc=args.start_utc,
        requested_end_utc=args.end_utc,
        expected_row_count=((args.end_utc - args.start_utc) // (15 * 60 * 1000) + 1) if args.start_utc is not None else None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
