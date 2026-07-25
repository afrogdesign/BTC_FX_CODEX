"""Pure semantic ownership for operator no-trade tokens."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

SEMANTICS_SCHEMA_VERSION = "operator_no_trade_semantics.v1"

HARD_NO_TRADE_TOKENS = frozenset({"volatile_regime"})
ADVISORY_NO_TRADE_TOKENS = frozenset({
    "short_at_major_support_wait_only",
    "long_at_major_resistance_wait_only",
    "breakout_follow_candidate",
    "upside_breakout_follow_watch",
    "downside_breakdown_follow_watch",
    "short_invalidated_by_up_break",
    "long_invalidated_by_down_break",
    "short_invalidation_watch",
    "long_invalidation_watch",
})

_TOKEN_DELIMITER = re.compile(r"[;,|]")


def _token_values(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set, frozenset)):
        return list(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
            except (TypeError, ValueError, json.JSONDecodeError):
                parsed = None
            if isinstance(parsed, list):
                return parsed
        return _TOKEN_DELIMITER.split(text)
    return [value]


def normalize_no_trade_tokens(value: object) -> tuple[str, ...]:
    """Normalize a no-trade value without mutating or consulting external state."""
    normalized = {
        str(token).strip().lower()
        for token in _token_values(value)
        if str(token).strip()
    }
    return tuple(sorted(normalized))


@dataclass(frozen=True)
class NoTradeSemanticResult:
    schema_version: str
    normalized_tokens: tuple[str, ...]
    hard_tokens: tuple[str, ...]
    advisory_tokens: tuple[str, ...]
    unknown_tokens: tuple[str, ...]
    has_tokens: bool
    all_advisory: bool
    fail_closed: bool


def classify_no_trade_tokens(value: object) -> NoTradeSemanticResult:
    normalized = normalize_no_trade_tokens(value)
    hard = tuple(sorted(set(normalized) & HARD_NO_TRADE_TOKENS))
    advisory = tuple(sorted(set(normalized) & ADVISORY_NO_TRADE_TOKENS))
    unknown = tuple(sorted(set(normalized) - HARD_NO_TRADE_TOKENS - ADVISORY_NO_TRADE_TOKENS))
    has_tokens = bool(normalized)
    return NoTradeSemanticResult(
        schema_version=SEMANTICS_SCHEMA_VERSION,
        normalized_tokens=normalized,
        hard_tokens=hard,
        advisory_tokens=advisory,
        unknown_tokens=unknown,
        has_tokens=has_tokens,
        all_advisory=has_tokens and len(advisory) == len(normalized),
        fail_closed=bool(hard or unknown),
    )


def formal_execution_blocks_no_trade(value: object) -> bool:
    return classify_no_trade_tokens(value).has_tokens


def offline_classifier_stops_for_no_trade(value: object) -> bool:
    return classify_no_trade_tokens(value).fail_closed
