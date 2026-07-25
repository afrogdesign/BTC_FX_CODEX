"""Report-only comparison of current and hard/unknown no-trade semantics."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.contracts.operator_semantics import classify_no_trade_tokens

SCHEMA_VERSION = "formal_gate_semantic_impact.v1"
METHOD_VERSION = "formal_gate_semantic_impact.v1"
SAFETY_STATEMENTS = (
    "counterfactual only",
    "execution_gate.py unchanged",
    "no production authorization",
    "human approval required before any gate change",
)


def _s(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _tokens(row: Mapping[str, Any]) -> Any:
    return row.get("no_trade_flags", row.get("formal_blockers", ""))


def _other_reasons(row: Mapping[str, Any], semantic: Any) -> list[str]:
    values = []
    for key in ("formal_blockers", "trade_execution_blockers", "formal_reasons", "other_formal_reasons"):
        value = _s(row.get(key))
        if value:
            values.extend(part.strip() for part in value.replace("|", ";").replace(",", ";").split(";") if part.strip())
    token_values = set(semantic.normalized_tokens) | {"no_trade_flags_present"}
    return sorted(set(value for value in values if value.lower() not in token_values))


def build_impact(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    breakdown: dict[str, Counter[str]] = {key: Counter() for key in ("side", "operator_class", "notification_kind", "formal_execution_gate", "actual_link_confidence", "actual_position_side")}
    missing_fields: set[str] = set()
    for row in rows:
        semantic = classify_no_trade_tokens(_tokens(row))
        has = semantic.has_tokens
        advisory_only = has and semantic.all_advisory
        hard = bool(semantic.hard_tokens)
        unknown = bool(semantic.unknown_tokens)
        mixed = bool(semantic.hard_tokens and semantic.advisory_tokens)
        other = _other_reasons(row, semantic)
        if "no_trade_flags" not in row and "formal_blockers" not in row:
            missing_fields.add("no_trade_flags")
        if "formal_execution_gate" not in row and "trade_execution_gate" not in row:
            missing_fields.add("formal_execution_gate")
        counts["total_rows"] += 1
        counts["rows_with_no_trade_flags"] += has
        counts["advisory_only_rows"] += advisory_only
        counts["hard_token_rows"] += hard
        counts["unknown_token_rows"] += unknown
        counts["mixed_hard_advisory_rows"] += mixed
        counts["current_no_trade_blocked_rows"] += has
        counts["counterfactual_no_trade_blocked_rows"] += hard or unknown
        removal = advisory_only
        counts["rows_where_no_trade_blocker_would_be_removed"] += removal
        if removal and other:
            counts["rows_still_blocked_by_other_formal_reasons"] += 1
        if removal and not other:
            counts["rows_potentially_changed_to_pass"] += 1
        for field, counter in breakdown.items():
            value = _s(row.get(field))
            if value:
                counter[value] += 1
    return {
        "schema_version": SCHEMA_VERSION,
        "method_version": METHOD_VERSION,
        "counts": {key: int(value) for key, value in sorted(counts.items())},
        "breakdown": {key: dict(sorted(value.items())) for key, value in sorted(breakdown.items())},
        "missing_source_fields": sorted(missing_fields),
        "statements": list(SAFETY_STATEMENTS),
        "safety_boundary": "report-only / counterfactual only / execution_gate.py unchanged / no production authorization",
    }


def build_markdown(report: Mapping[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = ["# Formal gate semantic impact", ""]
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    lines += ["", "- Missing source fields: " + (", ".join(report.get("missing_source_fields", [])) or "none"), "", *[f"- {statement}" for statement in SAFETY_STATEMENTS], ""]
    return "\n".join(lines)


def build_outputs(rows: Sequence[Mapping[str, Any]]) -> dict[str, bytes]:
    report = build_impact(rows)
    return {
        "formal_gate_semantic_impact.json": (json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "formal_gate_semantic_impact.md": build_markdown(report).encode(),
    }


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
