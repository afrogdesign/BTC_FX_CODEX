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
        "BREAKOUT_LOOKBACK_BARS",
        "WINDOW_MACRO_4H_BARS",
        "WINDOW_STRUCTURE_1H_BARS",
        "WINDOW_TRIGGER_15M_BARS",
        "WINDOW_MICRO_15M_BARS",
        "PATTERN_CONSOLIDATION_BARS_MIN",
        "PATTERN_CONSOLIDATION_BARS_MAX",
        "PATTERN_FAILED_BREAKOUT_RETURN_BARS",
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
        "TRIGGER_VOLUME_RATIO",
        "PHASE1_ACCOUNT_BALANCE_USD",
        "PHASE1_BASE_RISK_PCT",
        "PHASE1_MIN_RISK_PCT",
        "PHASE1_LOSS_STREAK_STEP_PCT",
        "PHASE1_MAX_POSITION_SIZE_USD",
        "PHASE1_TP1_RR_MULTIPLE",
        "PHASE1_TP2_RR_MULTIPLE",
        "PHASE1_TRAIL_ATR_MULTIPLIER",
        "PATTERN_FLAG_IMPULSE_ATR_MIN",
        "PATTERN_FLAG_PULLBACK_MIN_RATIO",
        "PATTERN_FLAG_PULLBACK_MAX_RATIO",
        "PATTERN_CONTRACTION_RATIO_MAX",
        "PATTERN_EXPANSION_RATIO_MIN",
        "PATTERN_TRIANGLE_FLAT_VARIANCE_ATR_MAX",
        "PATTERN_TRIANGLE_STEP_ATR_MIN",
        "PATTERN_FAILED_BREAKOUT_EXCESS_ATR_MIN",
        "PATTERN_FAILED_BREAKOUT_WICK_RATIO_MIN",
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
        "LONG_SHORT_DIFF_THRESHOLD": 8,
        "SHORT_LONG_DIFF_THRESHOLD": 9,
        "CONFIDENCE_LONG_MIN": 45,
        "CONFIDENCE_SHORT_MIN": 55,
        "CONFIDENCE_ALERT_CHANGE": 10,
        "ATTENTION_ALERT_SCORE_MIN": 55,
        "ATTENTION_ALERT_GAP_MIN": 15,
        "ATTENTION_ALERT_COOLDOWN_MINUTES": 60,
        "MAX_ACCEPTABLE_ATR_RATIO": 2.4,
        "MIN_ACCEPTABLE_ATR_RATIO": 0.25,
        "MIN_RR_RATIO": 1.10,
        "SL_ATR_MULTIPLIER": 1.5,
        "FUNDING_SHORT_WARNING": -0.04,
        "FUNDING_SHORT_PROHIBITED": -0.07,
        "FUNDING_LONG_WARNING": 0.06,
        "FUNDING_LONG_PROHIBITED": 0.10,
        "SWING_N_4H": 3,
        "SWING_N_1H": 2,
        "SWING_N_15M": 2,
        "WINDOW_MACRO_4H_BARS": 240,
        "WINDOW_STRUCTURE_1H_BARS": 120,
        "WINDOW_TRIGGER_15M_BARS": 24,
        "WINDOW_MICRO_15M_BARS": 96,
        "BREAKOUT_LOOKBACK_BARS": 20,
        "TRIGGER_VOLUME_RATIO": 1.15,
        "PATTERN_FLAG_IMPULSE_ATR_MIN": 2.2,
        "PATTERN_FLAG_PULLBACK_MIN_RATIO": 0.25,
        "PATTERN_FLAG_PULLBACK_MAX_RATIO": 0.55,
        "PATTERN_CONSOLIDATION_BARS_MIN": 6,
        "PATTERN_CONSOLIDATION_BARS_MAX": 20,
        "PATTERN_CONTRACTION_RATIO_MAX": 0.85,
        "PATTERN_EXPANSION_RATIO_MIN": 1.15,
        "PATTERN_TRIANGLE_FLAT_VARIANCE_ATR_MAX": 0.35,
        "PATTERN_TRIANGLE_STEP_ATR_MIN": 0.15,
        "PATTERN_FAILED_BREAKOUT_RETURN_BARS": 4,
        "PATTERN_FAILED_BREAKOUT_EXCESS_ATR_MIN": 0.15,
        "PATTERN_FAILED_BREAKOUT_WICK_RATIO_MIN": 0.35,
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
        "POSITION_RISK_HIGH_THRESHOLD": 80.0,
        "POSITION_RISK_MEDIUM_THRESHOLD": 55.0,
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
