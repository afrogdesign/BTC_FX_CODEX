from __future__ import annotations

import csv
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "manual_trade_ground_truth.v2"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"


def _read(path: Path) -> tuple[list[dict[str, str]], str]:
    if not path.exists():
        return [], "missing"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            return [dict(row) for row in csv.DictReader(fp)], "ok"
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid"


def _dec(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def build_manual_trade_ground_truth_report_v2(*, trades: Path, orders: Path, positions: Path, episodes: Path, links: Path, signal_outcomes: Path | None = None, output_md: Path | None = None, dry_run: bool = False) -> tuple[str, dict[str, Any]]:
    fills, fill_status = _read(trades)
    order_rows, order_status = _read(orders)
    position_rows, position_status = _read(positions)
    episode_rows, episode_status = _read(episodes)
    link_rows, link_status = _read(links)
    signal_rows, signal_status = _read(signal_outcomes) if signal_outcomes else ([], "missing")
    fee_values = [_dec(row.get("fee")) for row in fills]
    pnl_values = [_dec(row.get("realized_pnl")) for row in fills]
    fee_total = sum((value for value in fee_values if value is not None), Decimal("0"))
    pnl_total = sum((value for value in pnl_values if value is not None), Decimal("0"))
    closed = [row for row in episode_rows if str(row.get("status", "")).lower() == "closed"]
    open_rows = [row for row in episode_rows if str(row.get("status", "")).lower() == "open"]
    episode_pnl = [_dec(row.get("realized_pnl")) for row in closed]
    wins = sum(1 for value in episode_pnl if value is not None and value > 0)
    losses = sum(1 for value in episode_pnl if value is not None and value < 0)
    breakeven = sum(1 for value in episode_pnl if value is not None and value == 0)
    episode_gross = sum((value for value in episode_pnl if value is not None), Decimal("0"))
    high_medium = [row for row in link_rows if row.get("link_confidence") in {"high", "medium"} and row.get("link_status") == "linked"]
    categories = Counter()
    for link in high_medium:
        episode = next((row for row in episode_rows if row.get("episode_id") == link.get("episode_id")), {})
        pnl = _dec(episode.get("realized_pnl"))
        notification_class = str(link.get("notification_class", ""))
        if pnl is None:
            categories["ambiguous_needs_review"] += 1
        elif pnl >= 0 and notification_class == "entry_like":
            categories["actual_positive_with_entry_like_signal"] += 1
        elif pnl < 0 and notification_class == "entry_like":
            categories["actual_negative_with_entry_like_signal"] += 1
        elif pnl >= 0:
            categories["actual_positive_with_defensive_signal"] += 1
        else:
            categories["actual_negative_with_direction_conflict"] += 1
    coverage = {"fills": len(fills), "orders": len(order_rows), "positions": len(position_rows), "episodes": len(episode_rows), "links": len(link_rows), "signals": len(signal_rows)}
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "input_coverage": coverage, "fill_row_count": len(fills),
        "fee_total": float(fee_total), "realized_pnl_source_sum": float(pnl_total),
        "missing_fee_count": sum(value is None for value in fee_values), "missing_pnl_count": sum(value is None for value in pnl_values),
        "episode_count": len(episode_rows), "closed_episode_count": len(closed), "open_episode_count": len(open_rows),
        "episode_wins": wins, "episode_losses": losses, "episode_breakeven": breakeven,
        "episode_win_rate": round(wins / len(closed), 4) if closed else 0.0, "episode_gross_pnl": float(episode_gross),
        "episode_net_pnl": float(episode_gross - fee_total), "long_episode_count": sum(row.get("side") == "long" for row in episode_rows),
        "short_episode_count": sum(row.get("side") == "short" for row in episode_rows),
        "link_confidence_counts": dict(Counter(row.get("link_confidence", "ambiguous") for row in link_rows)),
        "link_reason_counts": dict(Counter(row.get("link_reason", "") for row in link_rows)),
        "actual_backed_categories": dict(categories), "safety_boundary": SAFETY,
        "input_status": {"fills": fill_status, "orders": order_status, "positions": position_status, "episodes": episode_status, "links": link_status, "signals": signal_status},
    }
    lines = [
        "# Manual Trade Ground-Truth Report v2", "", "## Input Coverage", json_line(coverage),
        "", "## Fill-Level Monetary Evidence", f"- fill_row_count: {len(fills)}", f"- fee_total: {fee_total}", f"- realized_pnl_source_sum: {pnl_total}", f"- missing_fee_count: {payload['missing_fee_count']}", f"- missing_pnl_count: {payload['missing_pnl_count']}",
        "", "## Position/Episode-Level Performance", f"- episode_count: {len(episode_rows)}", f"- closed_episode_count: {len(closed)}", f"- open_episode_count: {len(open_rows)}", f"- wins/losses/breakeven: {wins}/{losses}/{breakeven}", f"- episode_win_rate: {payload['episode_win_rate']}", f"- long/short_episode_counts: {payload['long_episode_count']}/{payload['short_episode_count']}", f"- episode_gross_pnl: {episode_gross}", f"- episode_net_pnl: {payload['episode_net_pnl']}",
        "", "## Signal Link Coverage", f"- total_links: {len(link_rows)}", f"- confidence_counts: {payload['link_confidence_counts']}", f"- reason_counts: {payload['link_reason_counts']}",
        "", "## Actual-Backed Comparison", "- Only high and medium confidence links are included.", f"- descriptive_categories: {dict(categories)}", "- These categories are calibration evidence, not causal proof.",
        "", "## Safety Boundary", f"- {SAFETY}",
        "", "## Limitations", "- Exchange exports provide execution and monetary evidence only; they do not establish human intent or decision rationale.", "- Fill rows are not human trade counts, and episode metrics are kept separate from fill-level totals.",
    ]
    report = "\n".join(lines) + "\n"
    payload["report_path"] = "" if output_md is None else output_md.name
    payload["dry_run"] = dry_run
    if output_md is not None and not dry_run:
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(report, encoding="utf-8")
    return report, payload


def json_line(value: Any) -> str:
    import json
    return "- coverage: " + json.dumps(value, ensure_ascii=False, sort_keys=True)

