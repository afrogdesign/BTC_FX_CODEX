from __future__ import annotations

import json
import ssl
import time
from dataclasses import dataclass
from typing import Any

import certifi
import requests


class BinanceDataError(Exception):
    pass


@dataclass
class BinanceConfig:
    base_url: str
    ws_url: str
    symbol: str
    timeout_sec: int
    retry_count: int
    request_interval_sec: float
    oi_period: str
    oi_limit: int
    taker_period: str
    taker_limit: int
    orderbook_limit: int
    liquidation_lookback_sec: float
    liquidation_max_events: int


def _request_json(
    cfg: BinanceConfig,
    path: str,
    *,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any]:
    last_error: Exception | None = None
    url = f"{cfg.base_url}{path}"
    for attempt in range(cfg.retry_count):
        try:
            response = requests.get(url, params=params, timeout=cfg.timeout_sec)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < cfg.retry_count - 1:
                time.sleep(cfg.request_interval_sec)
    raise BinanceDataError(str(last_error) if last_error else f"request failed: {path}")


def fetch_open_interest(cfg: BinanceConfig) -> dict[str, Any]:
    payload = _request_json(cfg, "/fapi/v1/openInterest", params={"symbol": cfg.symbol})
    if not isinstance(payload, dict):
        raise BinanceDataError("open interest payload invalid")
    return {
        "oi_value": float(payload.get("openInterest", 0.0)),
        "oi_timestamp_ms": int(payload.get("time", 0) or 0),
    }


def fetch_open_interest_stats(cfg: BinanceConfig) -> dict[str, Any]:
    payload = _request_json(
        cfg,
        "/futures/data/openInterestHist",
        params={"symbol": cfg.symbol, "period": cfg.oi_period, "limit": cfg.oi_limit},
    )
    if not isinstance(payload, list) or not payload:
        raise BinanceDataError("open interest history payload invalid")
    values = [float(item.get("sumOpenInterest", 0.0)) for item in payload if isinstance(item, dict)]
    if not values:
        raise BinanceDataError("open interest history empty")
    first = values[0]
    last = values[-1]
    change_pct = ((last - first) / first * 100.0) if abs(first) > 1e-9 else 0.0
    return {
        "oi_change_pct": change_pct,
        "oi_trend_values": values[-5:],
    }


def fetch_taker_volume(cfg: BinanceConfig) -> dict[str, Any]:
    payload = _request_json(
        cfg,
        "/futures/data/takerlongshortRatio",
        params={"symbol": cfg.symbol, "period": cfg.taker_period, "limit": cfg.taker_limit},
    )
    if not isinstance(payload, list) or not payload:
        raise BinanceDataError("taker volume payload invalid")
    buy_values: list[float] = []
    sell_values: list[float] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        buy_values.append(float(item.get("buyVol", 0.0)))
        sell_values.append(float(item.get("sellVol", 0.0)))
    if not buy_values or not sell_values:
        raise BinanceDataError("taker volume empty")
    cvd_series = []
    cumulative = 0.0
    for buy, sell in zip(buy_values, sell_values, strict=False):
        cumulative += buy - sell
        cvd_series.append(cumulative)
    return {
        "buy_volume": buy_values[-1],
        "sell_volume": sell_values[-1],
        "cvd_series": cvd_series,
    }


def fetch_orderbook(cfg: BinanceConfig) -> dict[str, Any]:
    payload = _request_json(
        cfg,
        "/fapi/v1/depth",
        params={"symbol": cfg.symbol, "limit": cfg.orderbook_limit},
    )
    if not isinstance(payload, dict):
        raise BinanceDataError("orderbook payload invalid")
    bids = payload.get("bids", [])
    asks = payload.get("asks", [])
    if not isinstance(bids, list) or not isinstance(asks, list):
        raise BinanceDataError("orderbook arrays missing")
    return {
        "bids": bids,
        "asks": asks,
        "last_update_id": int(payload.get("lastUpdateId", 0) or 0),
    }


def _extract_force_order(payload: dict[str, Any], target_symbol: str) -> dict[str, Any] | None:
    order = payload.get("o")
    if not isinstance(order, dict):
        return None
    symbol = str(order.get("s", "")).upper()
    if symbol and symbol != target_symbol.upper():
        return None
    price = float(order.get("ap", order.get("p", 0.0)) or 0.0)
    qty = float(order.get("q", 0.0) or 0.0)
    side = str(order.get("S", "")).upper()
    if price <= 0 or qty <= 0:
        return None
    return {
        "price": price,
        "qty": qty,
        "side": "sell" if side == "SELL" else "buy",
        "timestamp_ms": int(order.get("T", payload.get("E", 0)) or 0),
    }


def _collect_from_ws_url(
    *,
    ws_url: str,
    target_symbol: str,
    timeout_sec: int,
    deadline: float,
    max_events: int,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    try:
        from websocket import create_connection
    except Exception:
        return events

    try:
        ws = create_connection(
            ws_url,
            timeout=timeout_sec,
            sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": certifi.where()},
        )
    except Exception:
        # Some environments terminate TLS with custom cert chains.
        try:
            ws = create_connection(
                ws_url,
                timeout=timeout_sec,
                sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False},
            )
        except Exception:
            return events

    try:
        while time.monotonic() < deadline and len(events) < max_events:
            try:
                raw = ws.recv()
            except Exception:
                break
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, list):
                for item in payload:
                    if not isinstance(item, dict):
                        continue
                    parsed = _extract_force_order(item, target_symbol)
                    if parsed:
                        events.append(parsed)
                        if len(events) >= max_events:
                            break
                continue
            parsed = _extract_force_order(payload, target_symbol)
            if parsed:
                events.append(parsed)
    finally:
        ws.close()
    return events


def collect_liquidation_events(cfg: BinanceConfig) -> list[dict[str, Any]]:
    symbol = cfg.symbol.upper()
    deadline = time.monotonic() + max(cfg.liquidation_lookback_sec, 0.5)
    symbol_stream = f"{cfg.ws_url}/{cfg.symbol.lower()}@forceOrder"
    events = _collect_from_ws_url(
        ws_url=symbol_stream,
        target_symbol=symbol,
        timeout_sec=cfg.timeout_sec,
        deadline=deadline,
        max_events=cfg.liquidation_max_events,
    )
    if events:
        return events

    # Fallback: all-market stream tends to emit more frequently.
    all_market_stream = f"{cfg.ws_url}/!forceOrder@arr"
    return _collect_from_ws_url(
        ws_url=all_market_stream,
        target_symbol=symbol,
        timeout_sec=cfg.timeout_sec,
        deadline=deadline,
        max_events=cfg.liquidation_max_events,
    )
