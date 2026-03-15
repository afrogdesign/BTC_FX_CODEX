from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "MAIL_FROM",
    "MAIL_TO",
]

MASKED_KEYS = {"OPENAI_API_KEY", "SMTP_PASSWORD", "SMTP_USER"}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _coerce_value(key: str, value: str) -> Any:
    int_keys = {
        "SMTP_PORT",
        "EMA_FAST",
        "EMA_MID",
        "EMA_SLOW",
        "RSI_LENGTH",
        "ATR_LENGTH",
        "FETCH_LIMIT_4H",
        "FETCH_LIMIT_1H",
        "FETCH_LIMIT_15M",
        "LONG_SHORT_DIFF_THRESHOLD",
        "SHORT_LONG_DIFF_THRESHOLD",
        "CONFIDENCE_LONG_MIN",
        "CONFIDENCE_SHORT_MIN",
        "CONFIDENCE_ALERT_CHANGE",
        "ATTENTION_ALERT_SCORE_MIN",
        "ATTENTION_ALERT_GAP_MIN",
        "ATTENTION_ALERT_COOLDOWN_MINUTES",
        "SWING_N_4H",
        "SWING_N_1H",
        "SWING_N_15M",
        "API_TIMEOUT_SEC",
        "API_RETRY_COUNT",
        "AI_TIMEOUT_SEC",
        "AI_SUMMARY_TIMEOUT_SEC",
        "AI_RETRY_COUNT",
        "LOG_RETENTION_SIGNALS_DAYS",
        "LOG_RETENTION_NOTIFICATIONS_DAYS",
        "LOG_RETENTION_ERRORS_DAYS",
        "ALERT_COOLDOWN_MINUTES",
        "HEALTH_CHECK_MAX_HOURS",
        "SERVER_TIME_TOLERANCE_SEC",
        "BINANCE_OI_LIMIT",
        "BINANCE_TAKER_LIMIT",
        "BINANCE_ORDERBOOK_LIMIT",
        "BINANCE_LIQUIDATION_MAX_EVENTS",
        "BINANCE_LIQUIDATION_CACHE_MAX",
        "PHASE1_TIMEOUT_HOURS",
        "PHASE1_LOSS_STREAK",
    }
    float_keys = {
        "REQUEST_INTERVAL_SEC",
        "MAX_ACCEPTABLE_ATR_RATIO",
        "MIN_ACCEPTABLE_ATR_RATIO",
        "MIN_RR_RATIO",
        "SL_ATR_MULTIPLIER",
        "FUNDING_SHORT_WARNING",
        "FUNDING_SHORT_PROHIBITED",
        "FUNDING_LONG_WARNING",
        "FUNDING_LONG_PROHIBITED",
        "BINANCE_LIQUIDATION_LOOKBACK_SEC",
        "BINANCE_LIQUIDATION_CACHE_SEC",
        "LIQUIDITY_EQUAL_THRESHOLD_PCT",
        "POSITION_RISK_HIGH_THRESHOLD",
        "POSITION_RISK_MEDIUM_THRESHOLD",
        "PHASE1_ACCOUNT_BALANCE_USD",
        "PHASE1_BASE_RISK_PCT",
        "PHASE1_MIN_RISK_PCT",
        "PHASE1_LOSS_STREAK_STEP_PCT",
        "PHASE1_MAX_POSITION_SIZE_USD",
        "PHASE1_TP1_RR_MULTIPLE",
        "PHASE1_TP2_RR_MULTIPLE",
        "PHASE1_TRAIL_ATR_MULTIPLIER",
    }
    bool_keys = {"AI_CACHE_ENABLED", "DRYRUN_MODE"}

    if key in int_keys:
        return int(value)
    if key in float_keys:
        return float(value)
    if key in bool_keys:
        return _parse_bool(value)
    if key == "REPORT_TIMES":
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


def _load_dotenv(dotenv_path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not dotenv_path.exists():
        return env
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def mask_env(data: dict[str, Any]) -> dict[str, Any]:
    masked = {}
    for key, value in data.items():
        if key in MASKED_KEYS and value not in ("", None):
            masked[key] = "***MASKED***"
        else:
            masked[key] = value
    return masked


@dataclass(frozen=True)
class AppConfig:
    data: dict[str, Any]

    def __getattr__(self, item: str) -> Any:
        try:
            return self.data[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def as_dict(self) -> dict[str, Any]:
        return dict(self.data)


def load_config(base_dir: Path | None = None) -> AppConfig:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent

    dotenv_path = base_dir / ".env"
    file_env = _load_dotenv(dotenv_path)
    merged: dict[str, Any] = {}

    for key, value in file_env.items():
        merged[key] = _coerce_value(key, value)

    for key, value in os.environ.items():
        if (
            key in file_env
            or key in REQUIRED_KEYS
            or key.startswith("MEXC_")
            or key.startswith("OPENAI_")
            or key.startswith("BINANCE_")
        ):
            merged[key] = _coerce_value(key, value)

    missing = [key for key in REQUIRED_KEYS if not str(merged.get(key, "")).strip()]
    if missing:
        masked = ", ".join(f"{key}=***MASKED***" for key in missing)
        raise EnvironmentError(f"Missing required env keys: {masked}")

    defaults = {
        "MEXC_BASE_URL": "https://contract.mexc.com",
        "MEXC_SYMBOL": "BTC_USDT",
        "OPENAI_SUMMARY_MODEL": "gpt-4o-mini",
        "OPENAI_ADVICE_MODEL": "gpt-4o",
        "AI_ADVICE_PROVIDER": "api",
        "AI_SUMMARY_PROVIDER": "api",
        "AI_ADVICE_CLI_COMMAND": "",
        "AI_SUMMARY_CLI_COMMAND": "",
        "TIMEZONE": "Asia/Tokyo",
        "SYSTEM_LABEL": "",
        "REPORT_TIMES": [
            "00:05",
            "01:05",
            "02:05",
            "03:05",
            "04:05",
            "05:05",
            "06:05",
            "07:05",
            "08:05",
            "09:05",
            "10:05",
            "11:05",
            "12:05",
            "13:05",
            "14:05",
            "15:05",
            "16:05",
            "17:05",
            "18:05",
            "19:05",
            "20:05",
            "21:05",
            "22:05",
            "23:05",
        ],
        "EMA_FAST": 20,
        "EMA_MID": 50,
        "EMA_SLOW": 200,
        "RSI_LENGTH": 14,
        "ATR_LENGTH": 14,
        "FETCH_LIMIT_4H": 300,
        "FETCH_LIMIT_1H": 500,
        "FETCH_LIMIT_15M": 500,
        "LONG_SHORT_DIFF_THRESHOLD": 10,
        "SHORT_LONG_DIFF_THRESHOLD": 12,
        "CONFIDENCE_LONG_MIN": 40,
        "CONFIDENCE_SHORT_MIN": 70,
        "CONFIDENCE_ALERT_CHANGE": 10,
        "ATTENTION_ALERT_SCORE_MIN": 55,
        "ATTENTION_ALERT_GAP_MIN": 15,
        "ATTENTION_ALERT_COOLDOWN_MINUTES": 60,
        "MAX_ACCEPTABLE_ATR_RATIO": 2.0,
        "MIN_ACCEPTABLE_ATR_RATIO": 0.3,
        "MIN_RR_RATIO": 1.15,
        "SL_ATR_MULTIPLIER": 1.5,
        "FUNDING_SHORT_WARNING": -0.03,
        "FUNDING_SHORT_PROHIBITED": -0.05,
        "FUNDING_LONG_WARNING": 0.05,
        "FUNDING_LONG_PROHIBITED": 0.08,
        "SWING_N_4H": 3,
        "SWING_N_1H": 2,
        "SWING_N_15M": 2,
        "REQUEST_INTERVAL_SEC": 0.3,
        "API_TIMEOUT_SEC": 5,
        "API_RETRY_COUNT": 3,
        "AI_TIMEOUT_SEC": 5,
        "AI_SUMMARY_TIMEOUT_SEC": 10,
        "AI_RETRY_COUNT": 3,
        "AI_CACHE_ENABLED": False,
        "HEARTBEAT_FILE": "logs/heartbeat.txt",
        "HEALTH_CHECK_MAX_HOURS": 6,
        "LOG_RETENTION_SIGNALS_DAYS": 90,
        "LOG_RETENTION_NOTIFICATIONS_DAYS": 180,
        "LOG_RETENTION_ERRORS_DAYS": 180,
        "ALERT_COOLDOWN_MINUTES": 60,
        "DRYRUN_MODE": False,
        "SERVER_TIME_TOLERANCE_SEC": 2,
        "BINANCE_BASE_URL": "https://fapi.binance.com",
        "BINANCE_WS_URL": "wss://fstream.binance.com/ws",
        "BINANCE_SYMBOL": "BTCUSDT",
        "BINANCE_OI_PERIOD": "5m",
        "BINANCE_OI_LIMIT": 12,
        "BINANCE_TAKER_PERIOD": "5m",
        "BINANCE_TAKER_LIMIT": 12,
        "BINANCE_ORDERBOOK_LIMIT": 100,
        "BINANCE_LIQUIDATION_LOOKBACK_SEC": 4.0,
        "BINANCE_LIQUIDATION_MAX_EVENTS": 40,
        "BINANCE_LIQUIDATION_CACHE_SEC": 1800.0,
        "BINANCE_LIQUIDATION_CACHE_MAX": 500,
        "LIQUIDITY_EQUAL_THRESHOLD_PCT": 0.0008,
        "POSITION_RISK_HIGH_THRESHOLD": 70.0,
        "POSITION_RISK_MEDIUM_THRESHOLD": 45.0,
        "PHASE1_ACCOUNT_BALANCE_USD": 10000.0,
        "PHASE1_BASE_RISK_PCT": 0.5,
        "PHASE1_MIN_RISK_PCT": 0.2,
        "PHASE1_LOSS_STREAK_STEP_PCT": 0.1,
        "PHASE1_MAX_POSITION_SIZE_USD": 3000.0,
        "PHASE1_TP1_RR_MULTIPLE": 1.0,
        "PHASE1_TP2_RR_MULTIPLE": 2.0,
        "PHASE1_TRAIL_ATR_MULTIPLIER": 1.5,
        "PHASE1_TIMEOUT_HOURS": 12,
        "PHASE1_LOSS_STREAK": 0,
    }

    for key, value in defaults.items():
        merged.setdefault(key, value)

    return AppConfig(merged)
