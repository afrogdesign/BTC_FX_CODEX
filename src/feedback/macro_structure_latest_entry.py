"""Deterministic atomic fixed HTML entry for the accepted macro operator."""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

METHOD_VERSION = "macro_structure_latest_entry.v1"
SCHEMA_VERSION = METHOD_VERSION
OPERATOR_HTML = "macro_structure_operator.html"
REQUIRED_MARKERS = (
    "4H Macro Structure Chart",
    "Reliable support/resistance evidence",
    "Diagonal structure",
    "Structural events",
    "Scenario hypotheses",
    "Supplemental 15m manual-confirmation view",
    "report-only",
    "no automatic order",
    "human decides manually",
)
UNAVAILABLE_TITLE = "Macro Structure Latest Entry Unavailable"
FRESHNESS_NOTE = "fixed entry availability does not imply current market freshness; verify cutoff and status"
HISTORICAL_NOTE = "historical only; not the current successful result"
REQUIRED_SECTION_IDS = (
    'id="status"',
    'id="chart-4h"',
    'id="diagonal-evidence"',
    'id="structural-events"',
    'id="scenario-hypotheses"',
    'id="zones"',
    'id="chart"',
)
PROHIBITED_SOURCE_PATTERNS = (
    re.compile(r"<script\b", re.IGNORECASE),
    re.compile(r"<iframe\b", re.IGNORECASE),
    re.compile(r"<object\b", re.IGNORECASE),
    re.compile(r"<embed\b", re.IGNORECASE),
    re.compile(r"<meta\b[^>]*http-equiv\s*=\s*[\"']?refresh\b", re.IGNORECASE),
    re.compile(r"fetch\(", re.IGNORECASE),
    re.compile(r"window\.location", re.IGNORECASE),
    re.compile(r"location\.href", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"\b(?:src|href)\s*=\s*(?:[\"']\s*)?(?:https?://|//)", re.IGNORECASE),
)


class LatestEntryPublicationError(Exception):
    """Stable signal for fixed-entry filesystem publication failures."""


def _utc(value: Any, code: str) -> str:
    if not isinstance(value, str):
        raise ValueError(code)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(code) from exc
    if parsed.tzinfo is None:
        raise ValueError(code)
    return parsed.isoformat()


def _entry_id_available(artifact_id: str, source_digest: str) -> str:
    raw = f"{METHOD_VERSION}|available|{artifact_id}|{source_digest}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _entry_id_unavailable(error_code: str, artifact_id: str, source_digest: str) -> str:
    raw = f"{METHOD_VERSION}|unavailable|{error_code}|{artifact_id}|{source_digest}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _atomic_write(path: Path, content: bytes) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise LatestEntryPublicationError from exc
    if path.is_symlink():
        raise ValueError("latest_entry_path_unsafe")
    temporary: Path | None = None
    try:
        fd, temporary_name = tempfile.mkstemp(prefix=".latest-entry-", dir=path.parent)
        temporary = Path(temporary_name)
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except LatestEntryPublicationError:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise LatestEntryPublicationError from exc


def _source_bytes(source_dir: Path, artifact_id: str, source_digest: str) -> bytes:
    if source_dir.name != artifact_id or not artifact_id.startswith("operator_"):
        raise ValueError("latest_entry_source_artifact_mismatch")
    if not source_dir.is_dir() or source_dir.is_symlink():
        raise ValueError("latest_entry_source_artifact_invalid")
    html_path = source_dir / OPERATOR_HTML
    if not html_path.is_file() or html_path.is_symlink():
        raise ValueError("latest_entry_source_missing")
    try:
        content = html_path.read_bytes()
        text = content.decode("utf-8")
        model = json.loads((source_dir / "macro_structure_operator.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("latest_entry_source_invalid") from exc
    if not isinstance(model, dict) or model.get("operator_artifact_id") != artifact_id:
        raise ValueError("latest_entry_source_artifact_mismatch")
    if not isinstance(source_digest, str) or not source_digest or artifact_id != "operator_" + source_digest[:20]:
        raise ValueError("latest_entry_source_digest_mismatch")
    if "<body>" not in text or any(marker not in text for marker in REQUIRED_SECTION_IDS) or any(marker not in text for marker in REQUIRED_MARKERS):
        raise ValueError("latest_entry_source_incomplete")
    if any(pattern.search(text) for pattern in PROHIBITED_SOURCE_PATTERNS):
        raise ValueError("latest_entry_source_not_self_contained")
    return content


def _available_html(source: bytes, *, entry_id: str, artifact_id: str, source_digest: str, metadata: dict[str, Any]) -> bytes:
    try:
        source_text = source.decode("utf-8")
    except UnicodeError as exc:
        raise ValueError("latest_entry_source_not_utf8") from exc
    fields = (
        ("entry method version", METHOD_VERSION),
        ("entry ID", entry_id),
        ("entry_status", "available"),
        ("source operator artifact ID", artifact_id),
        ("source digest", source_digest),
        ("source cutoff UTC", metadata["as_of_utc"]),
        ("source cutoff JST", metadata["as_of_jst"]),
        ("source evaluation UTC", metadata["evaluated_at_utc"]),
        ("source evaluation JST", metadata["evaluated_at_jst"]),
        ("source stale status", metadata["stale_status"]),
        ("source continuity status", metadata["continuity_status"]),
        ("source data-quality status", metadata["data_quality_status"]),
        ("safety boundary", metadata["safety_boundary"]),
    )
    banner = '<section id="fixed-latest-entry" aria-label="fixed latest entry"><h2>Fixed latest operator entry</h2><ul>' + "".join(f"<li><b>{html.escape(str(label))}</b>: {html.escape(str(value))}</li>" for label, value in fields) + f"</ul><p>{html.escape(FRESHNESS_NOTE)}</p></section>"
    return source_text.replace("<body>", "<body>" + banner, 1).encode("utf-8")


def publish_available_entry(*, output_root: Path, source_dir: Path, artifact_id: str, source_digest: str, metadata: dict[str, Any]) -> dict[str, Any]:
    source = _source_bytes(source_dir, artifact_id, source_digest)
    for field in ("as_of_utc", "as_of_jst", "evaluated_at_utc", "evaluated_at_jst"):
        _utc(metadata.get(field), "latest_entry_source_timestamp_invalid")
    entry_id = _entry_id_available(artifact_id, source_digest)
    content = _available_html(source, entry_id=entry_id, artifact_id=artifact_id, source_digest=source_digest, metadata=metadata)
    path = output_root / "latest.html"
    _atomic_write(path, content)
    return {"latest_entry_path": str(path), "latest_entry_status": "available", "latest_entry_id": entry_id, "latest_entry_method_version": METHOD_VERSION, "latest_entry_source_artifact_id": artifact_id}


def _previous_success(output_root: Path) -> dict[str, str]:
    try:
        latest = json.loads((output_root / "latest.json").read_text(encoding="utf-8"))
        if not isinstance(latest, dict):
            return {}
        artifact_id = latest.get("operator_artifact_id")
        artifact_dir = latest.get("artifact_dir")
        source_digest = latest.get("source_digest")
        if not isinstance(artifact_id, str) or artifact_dir != artifact_id or not artifact_id.startswith("operator_") or Path(artifact_id).name != artifact_id or not isinstance(source_digest, str) or artifact_id != "operator_" + source_digest[:20]:
            return {}
        directory = output_root / artifact_id
        source = directory / OPERATOR_HTML
        if not directory.is_dir() or directory.parent != output_root or directory.is_symlink() or not source.is_file() or source.is_symlink():
            return {}
        return {"artifact_id": artifact_id, "source_digest": source_digest, "as_of_utc": str(latest.get("as_of_utc", "")), "as_of_jst": str(latest.get("as_of_jst", "")), "html_href": f"{artifact_id}/{OPERATOR_HTML}"}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def _unavailable_html(*, entry_id: str, error_code: str, previous: dict[str, str]) -> bytes:
    previous_html = ""
    if previous:
        previous_html = f'<h3>Last successful operator artifact</h3><p>artifact ID={html.escape(previous["artifact_id"])} · source digest={html.escape(previous["source_digest"])} · cutoff UTC={html.escape(previous["as_of_utc"])} · cutoff JST={html.escape(previous["as_of_jst"])}</p><p>{html.escape(HISTORICAL_NOTE)}</p><p><a href="{html.escape(previous["html_href"])}">historical operator artifact</a></p>'
    text = f'<!doctype html><html><head><meta charset="utf-8"><title>{UNAVAILABLE_TITLE}</title></head><body><section id="fixed-latest-entry-unavailable"><h1>{UNAVAILABLE_TITLE}</h1><p>entry method version={html.escape(METHOD_VERSION)}</p><p>entry ID={html.escape(entry_id)}</p><p>entry_status=unavailable</p><p>error_code={html.escape(error_code)}</p>{previous_html}<p>report-only / no automatic order / human decides manually</p><p>no complete current entry was published for this attempt</p></section></body></html>'
    return text.encode("utf-8")


def publish_unavailable_entry(*, output_root: Path, error_code: str) -> dict[str, Any]:
    previous = _previous_success(output_root)
    entry_id = _entry_id_unavailable(error_code, previous.get("artifact_id", ""), previous.get("source_digest", ""))
    _atomic_write(output_root / "latest.html", _unavailable_html(entry_id=entry_id, error_code=error_code, previous=previous))
    return {"latest_entry_path": str(output_root / "latest.html"), "latest_entry_status": "unavailable", "latest_entry_id": entry_id, "latest_entry_method_version": METHOD_VERSION}
