from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.data.provider_client.binance_market import (
    BinanceConfig,
    collect_liquidation_events,
    fetch_open_interest,
    fetch_open_interest_stats,
    fetch_orderbook,
    fetch_taker_volume,
)


@dataclass
class MarketStructureSnapshot:
    oi_value: float | None = None
    oi_change_pct: float | None = None
    oi_trend_values: list[float] | None = None
    cvd_series: list[float] | None = None
    buy_volume: float | None = None
    sell_volume: float | None = None
    orderbook_bids: list[list[str]] | None = None
    orderbook_asks: list[list[str]] | None = None
    liquidation_events: list[dict[str, Any]] | None = None
    missing_fields: list[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "oi_value": self.oi_value,
            "oi_change_pct": self.oi_change_pct,
            "oi_trend_values": self.oi_trend_values,
            "cvd_series": self.cvd_series,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "orderbook_bids": self.orderbook_bids,
            "orderbook_asks": self.orderbook_asks,
            "liquidation_events": self.liquidation_events,
            "missing_fields": self.missing_fields or [],
        }


def build_binance_cfg(cfg: Any) -> BinanceConfig:
    return BinanceConfig(
        base_url=cfg.BINANCE_BASE_URL,
        ws_url=cfg.BINANCE_WS_URL,
        symbol=cfg.BINANCE_SYMBOL,
        timeout_sec=cfg.API_TIMEOUT_SEC,
        retry_count=cfg.API_RETRY_COUNT,
        request_interval_sec=cfg.REQUEST_INTERVAL_SEC,
        oi_period=cfg.BINANCE_OI_PERIOD,
        oi_limit=cfg.BINANCE_OI_LIMIT,
        taker_period=cfg.BINANCE_TAKER_PERIOD,
        taker_limit=cfg.BINANCE_TAKER_LIMIT,
        orderbook_limit=cfg.BINANCE_ORDERBOOK_LIMIT,
        liquidation_lookback_sec=cfg.BINANCE_LIQUIDATION_LOOKBACK_SEC,
        liquidation_max_events=cfg.BINANCE_LIQUIDATION_MAX_EVENTS,
    )


def _liquidation_cache_path(base_dir: Path, symbol: str) -> Path:
    safe_symbol = "".join(ch for ch in symbol.upper() if ch.isalnum() or ch in {"_", "-"})
    return base_dir / "logs" / "cache" / f"binance_liquidations_{safe_symbol}.json"


def _normalize_liquidation_event(event: dict[str, Any]) -> dict[str, Any] | None:
    try:
        price = float(event.get("price", 0.0) or 0.0)
        qty = float(event.get("qty", 0.0) or 0.0)
        timestamp_ms = int(event.get("timestamp_ms", 0) or 0)
    except Exception:  # noqa: BLE001
        return None
    if price <= 0 or qty <= 0 or timestamp_ms <= 0:
        return None
    side = str(event.get("side", "")).lower()
    if side not in {"buy", "sell"}:
        side = "buy"
    return {"price": price, "qty": qty, "side": side, "timestamp_ms": timestamp_ms}


def _load_liquidation_cache(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    if not isinstance(payload, list):
        return []
    events: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_liquidation_event(item)
        if normalized:
            events.append(normalized)
    return events


def _save_liquidation_cache(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(events, ensure_ascii=False), encoding="utf-8")


def _merge_recent_liquidations(
    *,
    cached_events: list[dict[str, Any]],
    live_events: list[dict[str, Any]],
    now_ms: int,
    ttl_sec: float,
    max_events: int,
) -> list[dict[str, Any]]:
    ttl_ms = int(max(ttl_sec, 1.0) * 1000)
    floor_ms = now_ms - ttl_ms
    merged: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int, str]] = set()
    for event in cached_events + live_events:
        normalized = _normalize_liquidation_event(event)
        if not normalized:
            continue
        if normalized["timestamp_ms"] < floor_ms:
            continue
        dedupe_key = (
            normalized["timestamp_ms"],
            int(normalized["price"] * 100),
            int(normalized["qty"] * 10000),
            normalized["side"],
        )
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        merged.append(normalized)
    merged.sort(key=lambda item: int(item["timestamp_ms"]))
    if max_events > 0 and len(merged) > max_events:
        merged = merged[-max_events:]
    return merged


def fetch_market_structure(cfg: Any, *, base_dir: Path | None = None) -> MarketStructureSnapshot:
    client_cfg = build_binance_cfg(cfg)
    snapshot = MarketStructureSnapshot(missing_fields=[])

    try:
        oi_now = fetch_open_interest(client_cfg)
        snapshot.oi_value = oi_now["oi_value"]
    except Exception:  # noqa: BLE001
        snapshot.missing_fields.append("oi_value")

    try:
        oi_hist = fetch_open_interest_stats(client_cfg)
        snapshot.oi_change_pct = oi_hist["oi_change_pct"]
        snapshot.oi_trend_values = oi_hist["oi_trend_values"]
    except Exception:  # noqa: BLE001
        snapshot.missing_fields.extend(["oi_change_pct", "oi_trend_values"])

    try:
        taker = fetch_taker_volume(client_cfg)
        snapshot.buy_volume = taker["buy_volume"]
        snapshot.sell_volume = taker["sell_volume"]
        snapshot.cvd_series = taker["cvd_series"]
    except Exception:  # noqa: BLE001
        snapshot.missing_fields.extend(["buy_volume", "sell_volume", "cvd_series"])

    try:
        orderbook = fetch_orderbook(client_cfg)
        snapshot.orderbook_bids = orderbook["bids"]
        snapshot.orderbook_asks = orderbook["asks"]
    except Exception:  # noqa: BLE001
        snapshot.missing_fields.extend(["orderbook_bids", "orderbook_asks"])

    liquidation_error = False
    live_events: list[dict[str, Any]] = []
    try:
        live_events = collect_liquidation_events(client_cfg)
    except Exception:  # noqa: BLE001
        liquidation_error = True

    if base_dir is None:
        snapshot.liquidation_events = live_events
    else:
        now_ms = int(time.time() * 1000)
        cache_path = _liquidation_cache_path(base_dir, client_cfg.symbol)
        cached_events = _load_liquidation_cache(cache_path)
        merged = _merge_recent_liquidations(
            cached_events=cached_events,
            live_events=live_events,
            now_ms=now_ms,
            ttl_sec=float(getattr(cfg, "BINANCE_LIQUIDATION_CACHE_SEC", 1800.0)),
            max_events=int(getattr(cfg, "BINANCE_LIQUIDATION_CACHE_MAX", 500)),
        )
        snapshot.liquidation_events = merged
        _save_liquidation_cache(cache_path, merged)

    if liquidation_error and not snapshot.liquidation_events:
        snapshot.missing_fields.append("liquidation_events")

    snapshot.missing_fields = sorted(set(snapshot.missing_fields))
    return snapshot
