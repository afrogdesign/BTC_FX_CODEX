from __future__ import annotations

from dataclasses import dataclass
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


def fetch_market_structure(cfg: Any) -> MarketStructureSnapshot:
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

    try:
        snapshot.liquidation_events = collect_liquidation_events(client_cfg)
    except Exception:  # noqa: BLE001
        snapshot.missing_fields.append("liquidation_events")

    snapshot.missing_fields = sorted(set(snapshot.missing_fields))
    return snapshot
