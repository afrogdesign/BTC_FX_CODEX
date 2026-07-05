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
        "self_review_readiness": None,
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    input_path = Path(args.input)
    result = _read_json(input_path)
    signal_id = str(result.get("signal_id", "")).strip()
    if args.signal_id and signal_id != args.signal_id:
        parser.error(f"signal_id mismatch: expected {args.signal_id!r}, got {signal_id!r}")
    snapshot = build_value_defense_observation_snapshot(result, source_file=input_path.resolve())
    if not args.dry_run:
        write_snapshot(snapshot, Path(args.out_dir))
    if args.stdout_json:
        sys.stdout.write(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
