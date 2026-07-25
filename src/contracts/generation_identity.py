"""Pure generation identity and comparison contracts."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

GENERATION_IDENTITY_SCHEMA_VERSION = "p_generation_identity.v1"
LEGACY_UNVERSIONED = "legacy_unversioned"

_COMPONENT_FIELDS = (
    "score_version",
    "market_map_version",
    "active_plan_version",
    "side_aware_version",
    "structural_priority_version",
    "operator_decision_version",
    "notification_trigger_version",
    "classifier_version",
    "replay_version",
    "linker_version",
    "p8_evidence_version",
    "readiness_version",
)
_COMPARISON_STATUSES = {
    "comparable",
    "not_comparable_program",
    "not_comparable_runtime_generation",
    "not_comparable_schema_version",
    "baseline_reset_required_component_version",
    "baseline_reset_required_method_version",
    "not_comparable_legacy_unversioned",
}


def _required_text(name: str, value: object) -> str:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise ValueError(f"{name} cannot be blank")
    return text


def _cutoff_text(value: object) -> str:
    text = _required_text("cutoff_utc", value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("cutoff_utc must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("cutoff_utc must be timezone-aware")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class GenerationIdentity:
    program: str
    runtime_generation: str
    source_head: str
    schema_version: str
    method_version: str
    cutoff_utc: str
    identity_schema_version: str = GENERATION_IDENTITY_SCHEMA_VERSION
    score_version: str = LEGACY_UNVERSIONED
    market_map_version: str = LEGACY_UNVERSIONED
    active_plan_version: str = LEGACY_UNVERSIONED
    side_aware_version: str = LEGACY_UNVERSIONED
    structural_priority_version: str = LEGACY_UNVERSIONED
    operator_decision_version: str = LEGACY_UNVERSIONED
    notification_trigger_version: str = LEGACY_UNVERSIONED
    classifier_version: str = LEGACY_UNVERSIONED
    replay_version: str = LEGACY_UNVERSIONED
    linker_version: str = LEGACY_UNVERSIONED
    p8_evidence_version: str = LEGACY_UNVERSIONED
    readiness_version: str = LEGACY_UNVERSIONED

    def __post_init__(self) -> None:
        if self.identity_schema_version != GENERATION_IDENTITY_SCHEMA_VERSION:
            raise ValueError("identity_schema_version mismatch")
        if self.program not in {"P", "M"}:
            raise ValueError("program must be P or M")
        for name in ("runtime_generation", "source_head", "schema_version", "method_version"):
            object.__setattr__(self, name, _required_text(name, getattr(self, name)))
        object.__setattr__(self, "cutoff_utc", _cutoff_text(self.cutoff_utc))
        for name in _COMPONENT_FIELDS:
            value = str(getattr(self, name) or "").strip()
            object.__setattr__(self, name, value or LEGACY_UNVERSIONED)

    def to_dict(self) -> dict[str, str]:
        return {field.name: getattr(self, field.name) for field in fields(self)}

    def as_dict(self) -> dict[str, str]:
        return self.to_dict()


@dataclass(frozen=True)
class GenerationComparison:
    status: str
    comparable: bool
    baseline_reset_required: bool
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "comparable": self.comparable,
            "baseline_reset_required": self.baseline_reset_required,
            "reason_codes": self.reason_codes,
        }


def _component_field(value: str | None) -> str | None:
    if value is None:
        return None
    if value not in _COMPONENT_FIELDS:
        raise ValueError(f"unknown comparison component: {value}")
    return value


def compare_generation_identities(
    baseline: GenerationIdentity,
    candidate: GenerationIdentity,
    claim_component: str | None = None,
    *,
    component: str | None = None,
) -> GenerationComparison:
    if component is not None:
        if claim_component is not None and claim_component != component:
            raise ValueError("conflicting comparison component arguments")
        claim_component = component
    selected = _component_field(claim_component)
    if baseline.program != candidate.program:
        return GenerationComparison("not_comparable_program", False, False, ("program_mismatch",))
    if baseline.runtime_generation != candidate.runtime_generation:
        return GenerationComparison("not_comparable_runtime_generation", False, False, ("runtime_generation_mismatch",))
    if baseline.schema_version != candidate.schema_version:
        return GenerationComparison("not_comparable_schema_version", False, False, ("schema_version_mismatch",))
    if selected is not None and (getattr(baseline, selected) == LEGACY_UNVERSIONED or getattr(candidate, selected) == LEGACY_UNVERSIONED):
        return GenerationComparison("not_comparable_legacy_unversioned", False, False, ("claim_component_legacy_unversioned",))
    if selected is not None and getattr(baseline, selected) != getattr(candidate, selected):
        return GenerationComparison(
            "baseline_reset_required_component_version",
            False,
            True,
            (f"claim_component_version_mismatch:{selected}",),
        )
    if baseline.method_version != candidate.method_version:
        return GenerationComparison("baseline_reset_required_method_version", False, True, ("method_version_mismatch",))
    reasons = ("source_head_changed",) if baseline.source_head != candidate.source_head else ("generation_contract_match",)
    return GenerationComparison("comparable", True, False, reasons)


compare_generation_identity = compare_generation_identities
