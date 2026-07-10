from __future__ import annotations

import csv
import hashlib
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from src.feedback.manual_trade_episode_builder import EPISODE_HEADERS


SCHEMA_VERSION = "manual_trade_signal_link.v2"
LINK_METHOD_VERSION = "manual_trade_signal_link.v2"
LINK_HEADERS = [
    "schema_version", "link_id", "episode_id", "position_id", "signal_id", "entry_timestamp_jst",
    "mail_timestamp_jst", "time_delta_minutes", "position_side", "priority_direction", "side_compatibility",
    "symbol_compatibility", "notification_class", "link_score", "link_confidence", "link_status", "link_reason",
    "link_method_version", "created_at_utc",
]


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode()).hexdigest()


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace(" ", "T")
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    from zoneinfo import ZoneInfo
    return parsed.replace(tzinfo=ZoneInfo("Asia/Tokyo")) if parsed.tzinfo is None else parsed


def _read(path: Path, headers: list[str] | tuple[str, ...], *, version: str | None = None) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            if list(headers) != (reader.fieldnames or []):
                return [], "input_schema_mismatch"
            rows = [dict(row) for row in reader]
            if version and any(row.get("schema_version") != version for row in rows):
                return [], "input_schema_mismatch"
            return rows, None
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"


def _read_signal_input(path: Path) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            headers = reader.fieldnames or []
            if "signal_id" not in headers:
                return [], "input_schema_mismatch"
            return [dict(row) for row in reader], None
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"


def _signal_class(row: dict[str, Any]) -> str:
    text = " ".join(str(row.get(key, "")) for key in ("notification_class", "notification_kind", "kind", "subject", "action_kind")).lower()
    if any(token in text for token in ("followup", "follow-up", "management", "追跡", "保有")):
        return "followup_management"
    if any(token in text for token in ("defensive", "wait", "watch", "skip", "見送り", "監視", "様子見")):
        return "defensive"
    if any(token in text for token in ("entry", "attention", "candidate", "エントリー", "注意", "候補")):
        return "entry_like"
    return "unknown"


def _max_provenance(rows: list[dict[str, Any]]) -> str:
    values = [_dt(row.get(key)) for row in rows for key in ("created_at_utc", "reviewed_at_utc", "evaluated_at_utc")]
    values = [value for value in values if value is not None]
    return max(values).astimezone(__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z") if values else ""


def _side(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if text in {"long", "short"} else "unknown"


def _direction(row: dict[str, Any]) -> str:
    return _side(row.get("priority_direction") or row.get("bias"))


def _symbol_compatibility(episode: dict[str, Any], signal: dict[str, Any]) -> str:
    signal_symbol = str(signal.get("symbol", "")).strip().upper()
    episode_symbol = str(episode.get("symbol", "")).strip().upper()
    if not signal_symbol or not episode_symbol:
        return "unknown"
    return "match" if signal_symbol.replace("_", "") == episode_symbol.replace("_", "") else "conflict"


def build_manual_trade_signal_link_rows(*, episodes: list[dict[str, Any]], signal_rows: list[dict[str, Any]], signal_outcome_rows: list[dict[str, Any]], max_lookback_minutes: int = 240) -> list[dict[str, str]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in signal_outcome_rows + signal_rows:
        signal_id = str(row.get("signal_id", "")).strip()
        if signal_id:
            target = merged.setdefault(signal_id, {})
            for key, value in row.items():
                if str(value or "").strip() != "":
                    target[key] = value
    signals = list(merged.values())
    output: list[dict[str, str]] = []
    for episode in episodes:
        episode_id = str(episode.get("episode_id", "")).strip()
        entry_text = str(episode.get("opened_at_jst") or episode.get("opened_at_utc", "")).strip()
        entry_dt = _dt(entry_text)
        position_side = _side(episode.get("side"))
        candidates: list[dict[str, Any]] = []
        disqualifying_reasons: set[str] = set()
        followup_seen = False
        for signal in signals:
            signal_id = str(signal.get("signal_id", "")).strip()
            signal_dt = _dt(signal.get("mail_timestamp_jst") or signal.get("timestamp_jst"))
            if not signal_id or entry_dt is None or signal_dt is None:
                continue
            delta = (entry_dt - signal_dt).total_seconds() / 60.0
            if delta < 0 or delta > max_lookback_minutes:
                continue
            signal_side = _direction(signal)
            side_compatibility = "unknown"
            if position_side in {"long", "short"} and signal_side in {"long", "short"}:
                side_compatibility = "match" if position_side == signal_side else "conflict"
            if side_compatibility == "conflict":
                disqualifying_reasons.add("side_conflict")
                continue
            notification_class = _signal_class(signal)
            if notification_class == "followup_management":
                followup_seen = True
                continue
            symbol_compatibility = _symbol_compatibility(episode, signal)
            if symbol_compatibility == "conflict":
                disqualifying_reasons.add("symbol_conflict")
                continue
            score = 4 if delta <= 30 else (3 if delta <= 90 else 1)
            score += 4 if side_compatibility == "match" else 1
            score += 2 if symbol_compatibility == "match" else 0
            score += 2 if notification_class == "entry_like" else 0
            candidates.append({"signal": signal, "delta": delta, "score": score, "side": signal_side, "side_compatibility": side_compatibility, "symbol_compatibility": symbol_compatibility, "notification_class": notification_class})
        reason = "no_candidate"
        winner: dict[str, Any] | None = None
        status = "no_candidate"
        confidence = "ambiguous"
        score = 0
        if candidates:
            score = max(int(candidate["score"]) for candidate in candidates)
            top = [candidate for candidate in candidates if int(candidate["score"]) == score]
            if len(top) > 1:
                reason, status = "competing_candidate_tie", "ambiguous"
            else:
                winner = top[0]
                reason, status = "matched_unique_top_candidate", "linked"
                confidence = "high" if score >= 10 else ("medium" if score >= 7 else ("low" if score >= 4 else "ambiguous"))
        elif disqualifying_reasons:
            reason, status = sorted(disqualifying_reasons)[0], "ambiguous"
        elif followup_seen:
            reason, status = "followup_management_notification", "no_candidate"
        signal = winner["signal"] if winner else {}
        signal_id = str(signal.get("signal_id", "")).strip()
        link_id = "lnk_" + _hash(episode_id, signal_id, LINK_METHOD_VERSION)[:24]
        output.append({
            "schema_version": SCHEMA_VERSION, "link_id": link_id, "episode_id": episode_id,
            "position_id": str(episode.get("position_id", "")).strip(), "signal_id": signal_id,
            "entry_timestamp_jst": entry_text, "mail_timestamp_jst": str(signal.get("mail_timestamp_jst") or signal.get("timestamp_jst", "")).strip(),
            "time_delta_minutes": "" if not winner else f"{winner['delta']:.1f}", "position_side": position_side,
            "priority_direction": "" if not winner else winner["side"], "side_compatibility": "" if not winner else winner["side_compatibility"],
            "symbol_compatibility": "" if not winner else winner["symbol_compatibility"], "notification_class": "" if not winner else winner["notification_class"],
            "link_score": str(score), "link_confidence": confidence, "link_status": status, "link_reason": reason,
            "link_method_version": LINK_METHOD_VERSION, "created_at_utc": _max_provenance([episode, signal]),
        })
    return sorted(output, key=lambda row: (row["episode_id"], row["link_id"]))


def link_manual_trade_episodes_to_signals(*, episodes: Path, signals: Path, signal_outcomes: Path, output_csv: Path | None = None, max_lookback_minutes: int = 240, dry_run: bool = False, replace_output: bool = False) -> dict[str, Any]:
    output = output_csv or Path("logs/csv/manual_trade_signal_links.csv")
    episode_rows, episode_error = _read(episodes, EPISODE_HEADERS, version="manual_trade_episode.v1")
    signal_rows, signal_error = _read_signal_input(signals)
    outcome_rows, outcome_error = _read_signal_input(signal_outcomes)
    errors = [error for error in (episode_error, signal_error, outcome_error) if error]
    summary = {"ok": False, "exit_code": 2, "schema_version": SCHEMA_VERSION, "link_method_version": LINK_METHOD_VERSION, "dry_run": dry_run, "episode_count": len(episode_rows), "linked_count": 0, "output_csv": output.name, "errors": errors, "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"}
    if errors:
        return summary
    if max_lookback_minutes <= 0:
        summary["errors"] = ["invalid_max_lookback_minutes"]
        return summary
    if any(not str(row.get("episode_id", "")).strip() or _dt(row.get("opened_at_jst") or row.get("opened_at_utc")) is None for row in episode_rows):
        summary["errors"] = ["invalid_input"]
        return summary
    merged_input: dict[str, dict[str, Any]] = {}
    for row in outcome_rows + signal_rows:
        signal_id = str(row.get("signal_id", "")).strip()
        target = merged_input.setdefault(signal_id, {})
        for key, value in row.items():
            if str(value or "").strip():
                target[key] = value
    for row in merged_input.values():
        if not str(row.get("signal_id", "")).strip() or _dt(row.get("mail_timestamp_jst") or row.get("timestamp_jst")) is None:
            summary["errors"] = ["invalid_signal_timestamp"]
            return summary
    if output.exists() and not replace_output:
        try:
            with output.open(newline="", encoding="utf-8") as fp:
                if (csv.DictReader(fp).fieldnames or []) != LINK_HEADERS:
                    summary.update(errors=["existing_output_schema_mismatch"], exit_code=4)
                    return summary
        except (OSError, UnicodeError, csv.Error):
            summary.update(errors=["existing_output_schema_mismatch"], exit_code=4)
            return summary
    rows = build_manual_trade_signal_link_rows(episodes=episode_rows, signal_rows=signal_rows, signal_outcome_rows=outcome_rows, max_lookback_minutes=max_lookback_minutes)
    summary["linked_count"] = sum(1 for row in rows if row["link_status"] == "linked")
    summary["confidence_counts"] = dict(Counter(row["link_confidence"] for row in rows))
    summary["max_lookback_minutes"] = max_lookback_minutes
    summary["output_written"] = not dry_run
    summary["exit_code"] = 0
    summary["ok"] = True
    if not dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", dir=output.parent, delete=False) as fp:
                temp_path = Path(fp.name)
                writer = csv.DictWriter(fp, fieldnames=LINK_HEADERS)
                writer.writeheader()
                writer.writerows(rows)
            temp_path.replace(output)
        except (OSError, RuntimeError):
            if "temp_path" in locals():
                temp_path.unlink(missing_ok=True)
            summary.update(ok=False, output_written=False, errors=["output_io_failure"], exit_code=4)
            return summary
    return summary
