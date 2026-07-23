from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests


INTERVAL_MAP = {
    "4h": ("Hour4", 4 * 60 * 60 * 1000),
    "1h": ("Min60", 60 * 60 * 1000),
    "15m": ("Min15", 15 * 60 * 1000),
}
MAX_HISTORICAL_ROWS_PER_REQUEST = 2000


class DataFetchError(Exception):
    pass


@dataclass
class FetchConfig:
    base_url: str
    symbol: str
    timeout_sec: int
    retry_count: int
    request_interval_sec: float


def _request_json(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None,
    timeout_sec: int,
    retry_count: int,
    request_interval_sec: float,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retry_count):
        try:
            response = requests.request(method, url, params=params, timeout=timeout_sec)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                if payload.get("success") is False:
                    message = payload.get("message", "api error")
                    raise DataFetchError(str(message))
                return payload
            raise DataFetchError(f"Unexpected response type: {type(payload)!r}")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retry_count - 1:
                time.sleep(request_interval_sec)
    raise DataFetchError(str(last_error) if last_error else "request failed")


def get_server_time_ms(cfg: FetchConfig) -> int:
    url = f"{cfg.base_url}/api/v1/contract/ping"
    payload = _request_json(
        "GET",
        url,
        params=None,
        timeout_sec=cfg.timeout_sec,
        retry_count=cfg.retry_count,
        request_interval_sec=cfg.request_interval_sec,
    )
    data = payload.get("data")
    if isinstance(data, (int, float)):
        return int(data)
    if isinstance(data, dict):
        for key in ("serverTime", "server_time", "ts", "timestamp"):
            if key in data:
                return int(data[key])
    if "serverTime" in payload:
        return int(payload["serverTime"])
    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)


def _parse_kline_payload(payload: dict[str, Any]) -> pd.DataFrame:
    def _normalize_ts(value: Any) -> int:
        ts = int(value)
        if ts < 10_000_000_000:  # seconds
            return ts * 1000
        return ts

    data = payload.get("data")
    if not data:
        raise DataFetchError("Empty kline payload")

    if isinstance(data, list):
        rows = data
        if not rows:
            raise DataFetchError("Empty kline rows")
        parsed = []
        for row in rows:
            if isinstance(row, dict):
                ts = int(row.get("time", row.get("timestamp", 0)))
                parsed.append(
                    {
                        "timestamp": _normalize_ts(ts),
                        "open": float(row.get("open", 0)),
                        "high": float(row.get("high", 0)),
                        "low": float(row.get("low", 0)),
                        "close": float(row.get("close", 0)),
                        "volume": float(row.get("vol", row.get("volume", 0))),
                    }
                )
            elif isinstance(row, list) and len(row) >= 6:
                parsed.append(
                    {
                        "timestamp": _normalize_ts(row[0]),
                        "open": float(row[1]),
                        "high": float(row[2]),
                        "low": float(row[3]),
                        "close": float(row[4]),
                        "volume": float(row[5]),
                    }
                )
        return pd.DataFrame(parsed)

    if isinstance(data, dict):
        time_col = data.get("time") or data.get("timestamp") or []
        open_col = data.get("open") or []
        high_col = data.get("high") or []
        low_col = data.get("low") or []
        close_col = data.get("close") or []
        vol_col = data.get("vol") or data.get("volume") or []
        size = min(len(time_col), len(open_col), len(high_col), len(low_col), len(close_col), len(vol_col))
        if size == 0:
            raise DataFetchError("No kline values")
        df = pd.DataFrame(
            {
                "timestamp": [_normalize_ts(x) for x in time_col[:size]],
                "open": [float(x) for x in open_col[:size]],
                "high": [float(x) for x in high_col[:size]],
                "low": [float(x) for x in low_col[:size]],
                "close": [float(x) for x in close_col[:size]],
                "volume": [float(x) for x in vol_col[:size]],
            }
        )
        return df

    raise DataFetchError("Unsupported kline payload")


def fetch_klines(
    cfg: FetchConfig,
    interval: str,
    limit: int,
    *,
    server_time_ms: int | None = None,
) -> pd.DataFrame:
    if interval not in INTERVAL_MAP:
        raise ValueError(f"Unsupported interval: {interval}")
    mexc_interval, interval_ms = INTERVAL_MAP[interval]
    url = f"{cfg.base_url}/api/v1/contract/kline/{cfg.symbol}"
    payload = _request_json(
        "GET",
        url,
        params={"interval": mexc_interval, "limit": limit},
        timeout_sec=cfg.timeout_sec,
        retry_count=cfg.retry_count,
        request_interval_sec=cfg.request_interval_sec,
    )
    df = _parse_kline_payload(payload)
    df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="last")
    if server_time_ms is None:
        server_time_ms = get_server_time_ms(cfg)
    if not df.empty:
        last_ts = int(df.iloc[-1]["timestamp"])
        if last_ts + interval_ms > server_time_ms:
            df = df.iloc[:-1]
    df = df.reset_index(drop=True)
    return df


def fetch_klines_historical(
    cfg: FetchConfig,
    interval: str,
    start_utc_ms: int,
    end_utc_ms: int,
    *,
    max_rows_per_request: int = MAX_HISTORICAL_ROWS_PER_REQUEST,
) -> pd.DataFrame:
    """Fetch one bounded, continuous historical range in deterministic chunks."""
    if interval not in INTERVAL_MAP:
        raise ValueError("Unsupported interval: %s" % interval)
    if not 0 < max_rows_per_request <= MAX_HISTORICAL_ROWS_PER_REQUEST:
        raise ValueError("historical_request_limit_invalid")
    _, interval_ms = INTERVAL_MAP[interval]
    if start_utc_ms > end_utc_ms or start_utc_ms % interval_ms or end_utc_ms % interval_ms:
        raise ValueError("historical_range_not_aligned")

    url = f"{cfg.base_url}/api/v1/contract/kline/{cfg.symbol}"
    expected_total = ((end_utc_ms - start_utc_ms) // interval_ms) + 1
    collected: list[pd.DataFrame] = []
    chunk_start = start_utc_ms
    while chunk_start <= end_utc_ms:
        chunk_size = min(max_rows_per_request, ((end_utc_ms - chunk_start) // interval_ms) + 1)
        chunk_end = chunk_start + (chunk_size - 1) * interval_ms
        payload = _request_json(
            "GET",
            url,
            params={
                "interval": INTERVAL_MAP[interval][0],
                "start": chunk_start // 1000,
                "end": chunk_end // 1000,
                "limit": chunk_size,
            },
            timeout_sec=cfg.timeout_sec,
            retry_count=cfg.retry_count,
            request_interval_sec=cfg.request_interval_sec,
        )
        frame = _parse_kline_payload(payload)
        if frame.empty:
            raise DataFetchError("historical_ohlcv_truncated_chunk")
        frame = frame.sort_values("timestamp", kind="mergesort").reset_index(drop=True)
        if frame["timestamp"].duplicated(keep=False).any():
            for timestamp, group in frame.groupby("timestamp", sort=False):
                values = group[["open", "high", "low", "close", "volume"]].drop_duplicates()
                if len(values) > 1:
                    raise DataFetchError("historical_ohlcv_conflict")
            frame = frame.drop_duplicates(subset=["timestamp"], keep="first")
        timestamps = [int(value) for value in frame["timestamp"]]
        expected = list(range(chunk_start, chunk_end + interval_ms, interval_ms))
        if timestamps != expected:
            raise DataFetchError("historical_ohlcv_missing_or_out_of_range")
        collected.append(frame)
        chunk_start = chunk_end + interval_ms

    result = pd.concat(collected, ignore_index=True).sort_values("timestamp", kind="mergesort").reset_index(drop=True)
    if len(result) != expected_total or result["timestamp"].duplicated().any():
        raise DataFetchError("historical_ohlcv_continuity_invalid")
    return result


def fetch_funding_rate(cfg: FetchConfig) -> float:
    url = f"{cfg.base_url}/api/v1/contract/funding_rate/{cfg.symbol}"
    payload = _request_json(
        "GET",
        url,
        params=None,
        timeout_sec=cfg.timeout_sec,
        retry_count=cfg.retry_count,
        request_interval_sec=cfg.request_interval_sec,
    )
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("fundingRate", "funding_rate"):
            if key in data:
                return float(data[key])
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            for key in ("fundingRate", "funding_rate"):
                if key in first:
                    return float(first[key])
    raise DataFetchError("Funding rate not found")
