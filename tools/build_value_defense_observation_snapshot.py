from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


PUBLIC_DETAIL_TITLE = "BTCFX Manual Trading Report"
PUBLIC_PATH_SLUG = "manual-trading"
PHASE4_STATUS = "blocked_until_observation_review_and_human_approval"
LEGACY_OPERATOR_LABEL_TOKENS = (
    "Ver02",
    "Ver03",
    "Ver04",
    "[CLI]",
    "[API]",
    "[機械判定のみ]",
)
DEFAULT_OBSERVATION_CHECKLIST = {
    "shallow_retest_touched_first": "unknown_pending_followup",
    "value_defense_zone_touched": "unknown_pending_followup",
    "reclaim_trigger_met": "unknown_pending_followup",
    "continuation_trigger_met": "unknown_pending_followup",
    "invalidation_zone_reached": "unknown_pending_followup",
    "wait_or_enter_hindsight": "unknown_pending_followup",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_repo_root(source_file: Path) -> Path:
    resolved = source_file.resolve()
    if resolved.parent.name == "logs":
        return resolved.parent.parent
    return resolved.parent


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _zone_bounds(zone: dict[str, Any] | None) -> tuple[float | None, float | None]:
    if not isinstance(zone, dict):
        return None, None
    low = _as_float(zone.get("low"))
    high = _as_float(zone.get("high"))
    if low is None or high is None:
        return None, None
    if low > high:
        low, high = high, low
    return low, high


def _zone_contains(price: float, zone: dict[str, Any] | None) -> bool:
    low, high = _zone_bounds(zone)
    return low is not None and high is not None and low <= price <= high


def _zone_center(zone: dict[str, Any] | None) -> float | None:
    low, high = _zone_bounds(zone)
    if low is None or high is None:
        return None
    return (low + high) / 2.0


def _classify_price_position(
    price: float | None,
    shallow_zone: dict[str, Any] | None,
    value_zone: dict[str, Any] | None,
    invalidation_zone: dict[str, Any] | None,
) -> str:
    if price is None:
        return "outside_known_zones"

    for label, zone in (
        ("inside_invalidation_zone", invalidation_zone),
        ("inside_value_defense_zone", value_zone),
        ("inside_shallow_retest_zone", shallow_zone),
    ):
        if _zone_contains(price, zone):
            return label

    all_bounds: list[tuple[float, float]] = []
    for zone in (shallow_zone, value_zone, invalidation_zone):
        low, high = _zone_bounds(zone)
        if low is not None and high is not None:
            all_bounds.append((low, high))

    if not all_bounds:
        return "outside_known_zones"

    lows = [low for low, _high in all_bounds]
    highs = [high for _low, high in all_bounds]
    if price > max(highs):
        return "above_zones"
    if price < min(lows):
        return "below_zones"

    ordered = [zone for zone in (shallow_zone, value_zone) if isinstance(zone, dict)]
    centers = [(_zone_center(zone), zone) for zone in ordered]
    centers = [(center, zone) for center, zone in centers if center is not None]
    if len(centers) == 2:
        centers.sort(key=lambda item: item[0])
        lower_zone = centers[0][1]
        upper_zone = centers[1][1]
        lower_high = _zone_bounds(lower_zone)[1]
        upper_low = _zone_bounds(upper_zone)[0]
        if lower_high is not None and upper_low is not None and lower_high < price < upper_low:
            return "between_shallow_and_value_defense"

    return "outside_known_zones"


def _operator_label_status(result: dict[str, Any]) -> dict[str, Any]:
    checked_fields = ["summary_subject", "detail_page_url", "detail_page_local_path"]
    checked_text = " ".join(str(result.get(field, "") or "") for field in checked_fields)
    lowered = checked_text.lower()
    leak_tokens = [
        token
        for token in LEGACY_OPERATOR_LABEL_TOKENS
        if token.lower() in lowered
    ]
    return {
        "html_title_expected": PUBLIC_DETAIL_TITLE,
        "path_slug_expected": PUBLIC_PATH_SLUG,
        "legacy_operator_label_leak_visible": bool(leak_tokens),
        "checked_fields": checked_fields,
    }


def _notification_observation_is_eligible(result: dict[str, Any]) -> bool:
    was_notified = result.get("was_notified") is True
    notification_kind = str(result.get("notification_kind", "")).strip().lower()
    detail_page_status = str(result.get("detail_page_status", "")).strip().lower()
    return was_notified and bool(notification_kind) and notification_kind != "none" and detail_page_status != "disabled"


def _compact_self_review_readiness(source_file: Path) -> dict[str, Any] | None:
    artifact_path = _source_repo_root(source_file) / "local" / "self_review_current_check" / "self_review_current.json"
    if not artifact_path.exists():
        return None
    try:
        payload = _read_json(artifact_path)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    change_readiness = payload.get("change_readiness")
    change_readiness = change_readiness if isinstance(change_readiness, dict) else {}
    run_metadata = payload.get("run_metadata")
    run_metadata = run_metadata if isinstance(run_metadata, dict) else {}
    return {
        "schema_version": payload.get("schema_version"),
        "report_fingerprint": payload.get("report_fingerprint"),
        "run_metadata_fingerprint": run_metadata.get("report_fingerprint") or payload.get("run_metadata_fingerprint"),
        "review_queue_count": payload.get("review_queue_count"),
        "change_readiness_status": change_readiness.get("change_readiness_status"),
        "change_readiness_level": change_readiness.get("change_readiness_level"),
        "human_approval_required": change_readiness.get("human_approval_required"),
        "tuning_review_allowed": change_readiness.get("tuning_review_allowed"),
        "safety_boundary": change_readiness.get("safety_boundary") or payload.get("safety_boundary"),
    }


def _iter_text_values(node: Any) -> list[str]:
    values: list[str] = []
    if isinstance(node, dict):
        for value in node.values():
            values.extend(_iter_text_values(value))
    elif isinstance(node, list):
        for value in node:
            values.extend(_iter_text_values(value))
    elif node is not None:
        values.append(str(node))
    return values


def _attack_review_flags(
    result: dict[str, Any],
    *,
    long_value_defense: dict[str, Any],
    short_value_defense: dict[str, Any],
    current_price_position_long: str,
    current_price_position_short: str,
) -> dict[str, Any]:
    market_map_flags = _iter_text_values(result.get("market_map_flags"))
    market_map_primary_state = " ".join(_iter_text_values(result.get("market_map_primary_state"))).strip().lower()
    active_level_role = " ".join(_iter_text_values(result.get("active_level_role"))).strip().lower()
    level_flip_state = " ".join(_iter_text_values(result.get("level_flip_state"))).strip().lower()
    failed_breakout_state = " ".join(_iter_text_values(result.get("failed_breakout_state"))).strip().lower()
    trend_flip_state = " ".join(_iter_text_values(result.get("trend_flip_state"))).strip().lower()
    transition_direction = str(result.get("transition_direction", "")).strip().lower()
    bias = str(result.get("bias", "")).strip().lower()
    long_state = str((long_value_defense or {}).get("lifecycle_state", "")).strip().lower()
    short_state = str((short_value_defense or {}).get("lifecycle_state", "")).strip().lower()
    current_price_position_long = str(current_price_position_long or "").strip().lower()
    current_price_position_short = str(current_price_position_short or "").strip().lower()

    watch_tags = [
        "trend_transition_candidate",
        "higher_timeframe_reclaim",
        "breakout_extension_candidate",
        "tp_too_conservative",
        "short_invalidated_by_reclaim",
        "runner_should_have_been_considered",
        "micro_profit_trap_risk",
    ]
    matched_tags: list[str] = []
    evidence = {
        "market_map_primary_state": market_map_primary_state or None,
        "active_level_role": active_level_role or None,
        "level_flip_state": level_flip_state or None,
        "failed_breakout_state": failed_breakout_state or None,
        "trend_flip_state": trend_flip_state or None,
        "transition_direction": transition_direction or None,
        "bias": bias or None,
        "long_value_defense_lifecycle_state": long_state or None,
        "short_value_defense_lifecycle_state": short_state or None,
        "current_price_position_long": current_price_position_long or None,
        "current_price_position_short": current_price_position_short or None,
        "market_map_flags": market_map_flags[:5],
    }

    def _has_transition_token(text: str) -> bool:
        lowered = text.lower()
        return any(token in lowered for token in ("early_up", "early_down", "transition", "trend_flip"))

    if any(_has_transition_token(text) for text in (market_map_primary_state, trend_flip_state, failed_breakout_state, active_level_role)):
        matched_tags.append("trend_transition_candidate")
    if "resistance_to_support" in level_flip_state or any(
        flag in {"resistance_to_support_flip", "resistance_to_support_retest_confirmed"} for flag in market_map_flags
    ):
        matched_tags.append("higher_timeframe_reclaim")
    if "trend_transition_candidate" in matched_tags and (
        current_price_position_long == "above_zones" or current_price_position_short == "below_zones"
    ):
        matched_tags.append("breakout_extension_candidate")
    if "higher_timeframe_reclaim" in matched_tags and (bias == "long" or transition_direction == "up"):
        matched_tags.append("short_invalidated_by_reclaim")
    if "breakout_extension_candidate" in matched_tags:
        matched_tags.extend(["runner_should_have_been_considered", "micro_profit_trap_risk"])

    matched_tags = list(dict.fromkeys(matched_tags))
    return {
        "schema_version": "value_defense_attack_review_flags.v1",
        "review_only": True,
        "phase4_tuning_allowed": "no",
        "human_approval_required": "yes",
        "matched_tags": matched_tags,
        "watch_tags": watch_tags,
        "evidence": evidence,
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }


def _extract_value_defense(setup: dict[str, Any] | None) -> dict[str, Any]:
    setup = setup or {}
    vd = setup.get("value_defense_entry_layer") if isinstance(setup, dict) else {}
    vd = vd if isinstance(vd, dict) else {}
    return {
        "side": vd.get("side"),
        "lifecycle_state": vd.get("lifecycle_state"),
        "market_entry_status": vd.get("market_entry_status"),
        "shallow_retest_zone": vd.get("shallow_retest_zone"),
        "shallow_retest_risk": vd.get("shallow_retest_risk"),
        "value_defense_zone": vd.get("value_defense_zone"),
        "defense_zone_basis": vd.get("defense_zone_basis"),
        "invalidation_zone": vd.get("invalidation_zone"),
        "reclaim_trigger": vd.get("reclaim_trigger"),
        "continuation_trigger": vd.get("continuation_trigger"),
        "operator_guidance": vd.get("operator_guidance"),
        "safety_boundary": vd.get("safety_boundary"),
    }


def build_value_defense_observation_snapshot(result: dict[str, Any], *, source_file: Path) -> dict[str, Any]:
    long_setup = result.get("long_setup") if isinstance(result.get("long_setup"), dict) else {}
    short_setup = result.get("short_setup") if isinstance(result.get("short_setup"), dict) else {}
    long_vd = _extract_value_defense(long_setup)
    short_vd = _extract_value_defense(short_setup)
    current_price = _as_float(result.get("current_price"))
    long_position = _classify_price_position(
        current_price,
        long_vd.get("shallow_retest_zone") or long_setup.get("entry_zone"),
        long_vd.get("value_defense_zone"),
        long_vd.get("invalidation_zone"),
    )
    short_position = _classify_price_position(
        current_price,
        short_vd.get("shallow_retest_zone") or short_setup.get("entry_zone"),
        short_vd.get("value_defense_zone"),
        short_vd.get("invalidation_zone"),
    )
    notification_kind = str(result.get("notification_kind", "")).strip()
    detail_page_status = str(result.get("detail_page_status", "")).strip()
    detail_page_url = result.get("detail_page_url")
    detail_page_local_path = result.get("detail_page_local_path")
    summary_subject = str(result.get("summary_subject", "")).strip()
    self_review_readiness = _compact_self_review_readiness(source_file)
    attack_review_flags = _attack_review_flags(
        result,
        long_value_defense=long_vd,
        short_value_defense=short_vd,
        current_price_position_long=long_position,
        current_price_position_short=short_position,
    )
    observation = {
        "schema_version": "value_defense_observation_snapshot.v1",
        "source_file": str(source_file),
        "signal_id": str(result.get("signal_id", "")).strip(),
        "timestamp_jst": result.get("timestamp_jst"),
        "notification_kind": notification_kind,
        "detail_page_status": detail_page_status,
        "detail_page_url": detail_page_url,
        "detail_page_local_path": detail_page_local_path,
        "summary_subject": summary_subject,
        "current_price": current_price,
        "bias": result.get("bias"),
        "primary_setup_side": result.get("primary_setup_side"),
        "primary_setup_status": result.get("primary_setup_status"),
        "primary_setup_reason": result.get("primary_setup_reason"),
        "actionability_label": "watch_only",
        "human_action": "次の通常通知で Value Defense Entry Layer を再確認し、浅い再検討帯と本命防衛ゾーンの位置関係を観察する。",
        "actionability_safety": "report-only / not_FORMAL_GO / no automatic order / human decides manually",
        "phase4_status": PHASE4_STATUS,
        "operator_label_status": _operator_label_status(result),
        "long_value_defense": long_vd,
        "short_value_defense": short_vd,
        "self_review_readiness": self_review_readiness,
        "attack_review_flags": attack_review_flags,
        "observation_checklist": dict(DEFAULT_OBSERVATION_CHECKLIST),
        "current_price_position_long": long_position,
        "current_price_position_short": short_position,
    }
    return observation


def render_observation_markdown(snapshot: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Value Defense Observation Snapshot")
    lines.append("")
    lines.append(
        f"- source signal/time: {snapshot.get('signal_id')} / {snapshot.get('timestamp_jst')}"
    )
    lines.append(f"- public/detail page status: {snapshot.get('detail_page_status')}")
    lines.append(f"- detail page URL: {snapshot.get('detail_page_url')}")
    lines.append(f"- detail page local path: {snapshot.get('detail_page_local_path')}")
    lines.append(f"- summary subject: {snapshot.get('summary_subject')}")
    op = snapshot.get("operator_label_status") or {}
    lines.append(
        f"- operator label check: {op.get('html_title_expected')} / {op.get('path_slug_expected')} / legacy leak={op.get('legacy_operator_label_leak_visible')}"
    )
    lines.append(f"- current price: {snapshot.get('current_price')}")
    lines.append(f"- actionability: {snapshot.get('actionability_label')}")
    lines.append(f"- human action: {snapshot.get('human_action')}")
    lines.append(f"- safety: {snapshot.get('actionability_safety')}")
    lines.append(f"- Phase4: {snapshot.get('phase4_status')}")
    lines.append("")
    lines.append("## Long / Short Value Defense")
    for title, data in (
        ("Long", snapshot.get("long_value_defense") or {}),
        ("Short", snapshot.get("short_value_defense") or {}),
    ):
        lines.append(f"| {title} | value |")
        lines.append("|---|---|")
        for key in (
            "side",
            "lifecycle_state",
            "market_entry_status",
            "shallow_retest_zone",
            "shallow_retest_risk",
            "value_defense_zone",
            "defense_zone_basis",
            "invalidation_zone",
            "reclaim_trigger",
            "continuation_trigger",
            "operator_guidance",
            "safety_boundary",
        ):
            lines.append(f"| {key} | {data.get(key)} |")
        lines.append("")
    lines.append("## Current Price Position")
    lines.append(f"- long: {snapshot.get('current_price_position_long')}")
    lines.append(f"- short: {snapshot.get('current_price_position_short')}")
    lines.append("")
    lines.append("## Observation Checklist")
    for key, value in (snapshot.get("observation_checklist") or {}).items():
        lines.append(f"- {key}: {value}")
    self_review_readiness = snapshot.get("self_review_readiness")
    if isinstance(self_review_readiness, dict):
        lines.append("")
        lines.append("## Self Review Readiness")
        for key in (
            "schema_version",
            "report_fingerprint",
            "run_metadata_fingerprint",
            "review_queue_count",
            "change_readiness_status",
            "change_readiness_level",
            "human_approval_required",
            "tuning_review_allowed",
            "safety_boundary",
        ):
            if key in self_review_readiness:
                lines.append(f"- {key}: {self_review_readiness.get(key)}")
    attack_review_flags = snapshot.get("attack_review_flags")
    if isinstance(attack_review_flags, dict):
        lines.append("")
        lines.append("## Attack Review Flags")
        for key in (
            "review_only",
            "phase4_tuning_allowed",
            "human_approval_required",
            "matched_tags",
            "watch_tags",
            "safety_boundary",
        ):
            if key in attack_review_flags:
                lines.append(f"- {key}: {attack_review_flags.get(key)}")
    lines.append("")
    lines.append("Phase4 tuning remains blocked until observation evidence is reviewed and human approval is explicit.")
    lines.append("report-only / not_FORMAL_GO / no automatic order / human decides manually")
    return "\n".join(lines) + "\n"


def write_snapshot(snapshot: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    signal_id = str(snapshot.get("signal_id", "")).strip() or "unknown"
    json_text = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    md_text = render_observation_markdown(snapshot)
    (out_dir / f"{signal_id}.json").write_text(json_text, encoding="utf-8")
    (out_dir / f"{signal_id}.md").write_text(md_text, encoding="utf-8")
    (out_dir / "latest.json").write_text(json_text, encoding="utf-8")
    (out_dir / "latest.md").write_text(md_text, encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a report-only Value Defense observation snapshot.")
    parser.add_argument("--input", default="logs/last_result.json", help="Result JSON to inspect.")
    parser.add_argument("--out-dir", default="local/value_defense_observation", help="Output directory for snapshot files.")
    parser.add_argument("--signal-id", default="", help="Optional guard: fail if input signal_id differs.")
    parser.add_argument("--stdout-json", action="store_true", help="Print the generated JSON snapshot to stdout.")
    parser.add_argument("--dry-run", action="store_true", help="Build only in memory unless stdout-json is set.")
    parser.add_argument(
        "--allow-non-notified",
        action="store_true",
        help="Allow non-dry-run snapshot writing even when the input is not a real notified observation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    input_path = Path(args.input)
    result = _read_json(input_path)
    signal_id = str(result.get("signal_id", "")).strip()
    if args.signal_id and signal_id != args.signal_id:
        parser.error(f"signal_id mismatch: expected {args.signal_id!r}, got {signal_id!r}")
    if not args.dry_run and not args.allow_non_notified and not _notification_observation_is_eligible(result):
        parser.error(
            "input is not an eligible notified observation; use --allow-non-notified to override for manual debug",
        )
    snapshot = build_value_defense_observation_snapshot(result, source_file=input_path.resolve())
    if not args.dry_run:
        write_snapshot(snapshot, Path(args.out_dir))
    if args.stdout_json:
        sys.stdout.write(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
