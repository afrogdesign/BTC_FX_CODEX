"""Pure, reusable contract foundations."""

from .generation_identity import (
    GENERATION_IDENTITY_SCHEMA_VERSION,
    LEGACY_UNVERSIONED,
    GenerationComparison,
    GenerationIdentity,
    compare_generation_identities,
)
from .operator_semantics import (
    ADVISORY_NO_TRADE_TOKENS,
    HARD_NO_TRADE_TOKENS,
    SEMANTICS_SCHEMA_VERSION,
    NoTradeSemanticResult,
    classify_no_trade_tokens,
    formal_execution_blocks_no_trade,
    normalize_no_trade_tokens,
    offline_classifier_stops_for_no_trade,
)

__all__ = [
    "ADVISORY_NO_TRADE_TOKENS",
    "GENERATION_IDENTITY_SCHEMA_VERSION",
    "HARD_NO_TRADE_TOKENS",
    "LEGACY_UNVERSIONED",
    "GenerationComparison",
    "GenerationIdentity",
    "NoTradeSemanticResult",
    "SEMANTICS_SCHEMA_VERSION",
    "classify_no_trade_tokens",
    "compare_generation_identities",
    "formal_execution_blocks_no_trade",
    "normalize_no_trade_tokens",
    "offline_classifier_stops_for_no_trade",
]
