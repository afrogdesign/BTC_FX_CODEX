from __future__ import annotations

import hashlib
import html
import os
import re
import shlex
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import urlsplit


SCHEMA_VERSION = "macro_structure_public_delivery.v1"
METHOD_VERSION = "macro_structure_public_delivery.v1"
DEFAULT_SOURCE_PATH = "local/reports/macro_structure/operator/latest.html"
PUBLIC_SUFFIX = "/macro-structure/latest.html"
SAFETY_BOUNDARY = "report-only / no automatic order / human decides manually"
MAX_SOURCE_BYTES = 5 * 1024 * 1024

_AVAILABLE_MARKERS = (
    'id="fixed-latest-entry"',
    "entry_status</b>: available",
    "macro_structure_latest_entry.v1",
    "source operator artifact ID",
    "source digest",
    "source cutoff UTC",
    "source cutoff JST",
    "source stale status",
    "source continuity status",
    "source data-quality status",
    "fixed entry availability does not imply current market freshness; verify cutoff and status",
    'id="chart-4h"',
    'id="structural-events"',
    'id="scenario-hypotheses"',
    'id="chart"',
    "report-only",
    "no automatic order",
    "human decides manually",
)
_UNAVAILABLE_MARKERS = (
    'id="fixed-latest-entry-unavailable"',
    "Macro Structure Latest Entry Unavailable",
    "entry_status=unavailable",
    "macro_structure_latest_entry.v1",
    "no complete current entry was published for this attempt",
    "report-only",
    "no automatic order",
    "human decides manually",
)
_SECRET_PATTERNS = (
    re.compile(r"OPENAI_API_KEY", re.IGNORECASE),
    re.compile(r"SMTP_PASSWORD", re.IGNORECASE),
    re.compile(r"-----BEGIN(?: [^-]+)? PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"Authorization:\s*Bearer\b", re.IGNORECASE),
)
_LABEL_PATTERNS = {
    "source_artifact_id": re.compile(r"source operator artifact ID</b>:\s*([^<]+)", re.IGNORECASE),
    "source_digest": re.compile(r"source digest</b>:\s*([^<]+)", re.IGNORECASE),
    "cutoff_utc": re.compile(r"source cutoff UTC</b>:\s*([^<]+)", re.IGNORECASE),
    "cutoff_jst": re.compile(r"source cutoff JST</b>:\s*([^<]+)", re.IGNORECASE),
    "stale_status": re.compile(r"source stale status</b>:\s*([^<]+)", re.IGNORECASE),
    "continuity_status": re.compile(r"source continuity status</b>:\s*([^<]+)", re.IGNORECASE),
    "data_quality_status": re.compile(r"source data-quality status</b>:\s*([^<]+)", re.IGNORECASE),
}
_SECTION_PATTERNS = {
    "available": re.compile(r'<section\b[^>]*\bid="fixed-latest-entry"[^>]*>.*?</section\s*>', re.IGNORECASE | re.DOTALL),
    "unavailable": re.compile(r'<section\b[^>]*\bid="fixed-latest-entry-unavailable"[^>]*>.*?</section\s*>', re.IGNORECASE | re.DOTALL),
}
_AVAILABLE_ENTRY_ID = re.compile(r"<b>entry ID</b>\s*:\s*([^<\s]+)", re.IGNORECASE)
_UNAVAILABLE_ENTRY_ID = re.compile(r"entry ID\s*=\s*([^<\s]+)", re.IGNORECASE)
_SAFE_SSH_HOST = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:@[A-Za-z0-9][A-Za-z0-9._-]*)?\Z")
_SAFE_REMOTE_ROOT = re.compile(r"/[A-Za-z0-9._/-]+\Z")


class MacroPublicDeliveryError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _clean_value(value: str) -> str:
    value = html.unescape(str(value)).strip()
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise MacroPublicDeliveryError("macro_public_source_invalid")
    return value


def _extract(text: str, key: str, *, required: bool = False) -> str:
    match = _LABEL_PATTERNS[key].search(text)
    if not match:
        if required:
            raise MacroPublicDeliveryError("macro_public_source_invalid")
        return ""
    value = _clean_value(match.group(1))
    if required and not value:
        raise MacroPublicDeliveryError("macro_public_source_invalid")
    return value


def _current_section(text: str, state: str) -> str:
    pattern = _SECTION_PATTERNS[state]
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise MacroPublicDeliveryError("macro_public_source_invalid")
    return matches[0]


def _current_entry_id(section: str, state: str) -> str:
    pattern = _AVAILABLE_ENTRY_ID if state == "available" else _UNAVAILABLE_ENTRY_ID
    values = [_clean_value(match) for match in pattern.findall(section) if _clean_value(match)]
    if len(values) != 1:
        raise MacroPublicDeliveryError("macro_public_source_invalid")
    return values[0]


def resolve_source_path(base_dir: Path, cfg: Any) -> Path:
    configured = str(getattr(cfg, "MACRO_STRUCTURE_FIXED_ENTRY_PATH", DEFAULT_SOURCE_PATH)).strip()
    if not configured:
        configured = DEFAULT_SOURCE_PATH
    path = Path(configured)
    return path if path.is_absolute() else base_dir / path


def _read_source(path: Path) -> tuple[bytes, str]:
    if path.is_symlink():
        raise MacroPublicDeliveryError("macro_public_source_unsafe")
    if not path.exists():
        raise MacroPublicDeliveryError("macro_public_source_missing")
    if not path.is_file():
        raise MacroPublicDeliveryError("macro_public_source_unsafe")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise MacroPublicDeliveryError("macro_public_source_unsafe") from exc
    if size > MAX_SOURCE_BYTES:
        raise MacroPublicDeliveryError("macro_public_source_too_large")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise MacroPublicDeliveryError("macro_public_source_unsafe") from exc
    if not data:
        raise MacroPublicDeliveryError("macro_public_source_invalid")
    if len(data) > MAX_SOURCE_BYTES:
        raise MacroPublicDeliveryError("macro_public_source_too_large")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MacroPublicDeliveryError("macro_public_source_invalid_utf8") from exc
    return data, text


def validate_fixed_entry_source(path: Path) -> dict[str, Any]:
    data, text = _read_source(path)
    if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
        raise MacroPublicDeliveryError("macro_public_source_unsafe")
    has_available = all(marker in text for marker in _AVAILABLE_MARKERS)
    has_unavailable = all(marker in text for marker in _UNAVAILABLE_MARKERS)
    if has_available == has_unavailable:
        raise MacroPublicDeliveryError("macro_public_source_invalid")
    if has_available and 'id="fixed-latest-entry-unavailable"' in text:
        raise MacroPublicDeliveryError("macro_public_source_invalid")
    if has_unavailable and 'id="fixed-latest-entry"' in text:
        raise MacroPublicDeliveryError("macro_public_source_invalid")

    source_sha256 = hashlib.sha256(data).hexdigest()
    state = "available" if has_available else "unavailable"
    current_section = _current_section(text, state)
    entry_id = _current_entry_id(current_section, state)
    model: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "method_version": METHOD_VERSION,
        "entry_status": state,
        "entry_id": entry_id,
        "source_sha256": source_sha256,
        "source_size_bytes": len(data),
        "source_artifact_id": "",
        "source_digest": "",
        "cutoff_utc": "",
        "cutoff_jst": "",
        "stale_status": "",
        "continuity_status": "",
        "data_quality_status": "",
        "source_bytes": data,
        "source_path": path,
        "safety_boundary": SAFETY_BOUNDARY,
    }
    if has_available:
        model.update(
            {
                "source_artifact_id": _extract(text, "source_artifact_id", required=True),
                "source_digest": _extract(text, "source_digest", required=True),
                "cutoff_utc": _extract(text, "cutoff_utc", required=True),
                "cutoff_jst": _extract(text, "cutoff_jst", required=True),
                "stale_status": _extract(text, "stale_status", required=True),
                "continuity_status": _extract(text, "continuity_status", required=True),
                "data_quality_status": _extract(text, "data_quality_status", required=True),
            }
        )
    return model


def _validated_public_url(cfg: Any) -> str:
    raw = str(getattr(cfg, "NOTIFICATION_HTML_PUBLIC_BASE_URL", "")).strip()
    if not raw or any(ord(char) < 32 or ord(char) == 127 for char in raw):
        raise MacroPublicDeliveryError("macro_public_url_invalid")
    parsed = urlsplit(raw)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise MacroPublicDeliveryError("macro_public_url_invalid")
    return raw.rstrip("/") + PUBLIC_SUFFIX


def _validated_transport(cfg: Any) -> tuple[str, str, str]:
    host = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_SSH_HOST", "")).strip()
    key = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_SSH_KEY", "")).strip()
    remote_root = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_DIR", "")).strip()
    values = (host, key, remote_root)
    if any(not value or "\x00" in value or "\n" in value or "\r" in value for value in values):
        raise MacroPublicDeliveryError("macro_public_transport_config_invalid")
    if host.startswith("-") or not _SAFE_SSH_HOST.fullmatch(host):
        raise MacroPublicDeliveryError("macro_public_transport_config_invalid")
    if not remote_root.startswith("/"):
        raise MacroPublicDeliveryError("macro_public_transport_config_invalid")
    if ".." in PurePosixPath(remote_root).parts:
        raise MacroPublicDeliveryError("macro_public_transport_config_invalid")
    if not _SAFE_REMOTE_ROOT.fullmatch(remote_root):
        raise MacroPublicDeliveryError("macro_public_transport_config_invalid")
    return host, key, remote_root.rstrip("/")


def _ssh_args(key: str) -> list[str]:
    return ["-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "-i", str(Path(key).expanduser())]


@contextmanager
def _stage_validated_source(model: dict[str, Any]):
    temporary: Path | None = None
    descriptor: int | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(prefix=".macro-public-")
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(model["source_bytes"])
            handle.flush()
            os.fsync(handle.fileno())
        yield temporary
    except Exception as exc:  # noqa: BLE001
        raise MacroPublicDeliveryError("macro_public_publish_failed") from exc
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


def _run_remote_publication(model: dict[str, Any], cfg: Any, runner: Callable[..., Any] = subprocess.run) -> None:
    host, key, remote_root = _validated_transport(cfg)
    remote_dir = f"{remote_root}/macro-structure"
    temp_name = f".latest.{model['source_sha256'][:20]}.tmp"
    remote_temp = f"{remote_dir}/{temp_name}"
    remote_latest = f"{remote_dir}/latest.html"
    ssh_args = _ssh_args(key)
    rsync_ssh = shlex.join(["ssh", *ssh_args])
    commands = [
        ["ssh", *ssh_args, host, "mkdir", "-p", remote_dir],
    ]
    try:
        with _stage_validated_source(model) as staged_source:
            commands.extend(
                [
                    ["rsync", "-a", "-e", rsync_ssh, str(staged_source), f"{host}:{remote_temp}"],
                    ["ssh", *ssh_args, host, "mv", "-f", remote_temp, remote_latest],
                ]
            )
            try:
                for command in commands:
                    runner(command, check=True, capture_output=True, text=True, timeout=20, shell=False)
            except Exception as exc:  # noqa: BLE001
                try:
                    runner(["ssh", *ssh_args, host, "rm", "-f", remote_temp], check=False, capture_output=True, text=True, timeout=20, shell=False)
                except Exception:
                    pass
                raise MacroPublicDeliveryError("macro_public_publish_failed") from exc
    except MacroPublicDeliveryError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise MacroPublicDeliveryError("macro_public_publish_failed") from exc


def _base_result(status: str, *, error_code: str = "") -> dict[str, Any]:
    return {
        "macro_structure_public_method_version": METHOD_VERSION,
        "macro_structure_public_status": status,
        "macro_structure_public_url": "",
        "macro_structure_public_entry_status": "",
        "macro_structure_public_entry_id": "",
        "macro_structure_public_source_sha256": "",
        "macro_structure_public_error_code": error_code,
    }


def publish_macro_structure_public(
    base_dir: Path,
    cfg: Any,
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    if not bool(getattr(cfg, "NOTIFICATION_HTML_ENABLED", False)):
        return _base_result("disabled")
    try:
        model = validate_fixed_entry_source(resolve_source_path(base_dir, cfg))
    except MacroPublicDeliveryError as exc:
        return _base_result("source_unavailable", error_code=exc.code)
    try:
        public_url = _validated_public_url(cfg)
        _run_remote_publication(model, cfg, runner=runner)
    except MacroPublicDeliveryError as exc:
        return _base_result("failed", error_code=exc.code)
    result = _base_result("published")
    result.update(
        {
            "macro_structure_public_url": public_url,
            "macro_structure_public_entry_status": model["entry_status"],
            "macro_structure_public_entry_id": model["entry_id"],
            "macro_structure_public_source_sha256": model["source_sha256"],
            "macro_structure_public_cutoff_jst": model.get("cutoff_jst", ""),
            "macro_structure_public_stale_status": model.get("stale_status", ""),
            "macro_structure_public_continuity_status": model.get("continuity_status", ""),
            "macro_structure_public_data_quality_status": model.get("data_quality_status", ""),
            "macro_structure_public_error_code": "",
        }
    )
    return result


publish_macro_structure_public_entry = publish_macro_structure_public


def format_macro_structure_email_block(delivery: dict[str, Any]) -> str:
    status = str(delivery.get("macro_structure_public_status", "")).strip()
    if status == "disabled":
        return ""
    if status == "published":
        url = str(delivery.get("macro_structure_public_url", "")).strip()
        if str(delivery.get("macro_structure_public_entry_status", "")) == "available":
            def value(key: str) -> str:
                return _clean_value(str(delivery.get(key) or "unknown")) or "unknown"

            return (
                "【4H大局チャート（公開URL）】\n"
                f"{url}\n"
                f"状態: available / cutoff JST={value('macro_structure_public_cutoff_jst')} / "
                f"stale={value('macro_structure_public_stale_status')} / "
                f"continuity={value('macro_structure_public_continuity_status')} / "
                f"data_quality={value('macro_structure_public_data_quality_status')}\n"
                "固定URLの存在は鮮度を保証しません。時刻と状態を確認してください。"
            )
        return (
            "【4H大局チャート（公開URL）】\n"
            f"{url}\n"
            "状態: unavailable\n"
            "今回の完全な最新画面は公開されていません。リンク先の利用不可表示を確認してください。"
        )
    code = str(delivery.get("macro_structure_public_error_code", "macro_public_source_invalid")).strip()
    return f"【4H大局チャート】利用不可（{code}）"


format_macro_structure_public_email_block = format_macro_structure_email_block


def enrich_delivery_email_result(delivery: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    if model.get("entry_status") != "available":
        return delivery
    delivery = dict(delivery)
    delivery.update(
        {
            "macro_structure_public_cutoff_jst": model.get("cutoff_jst", ""),
            "macro_structure_public_stale_status": model.get("stale_status", ""),
            "macro_structure_public_continuity_status": model.get("continuity_status", ""),
            "macro_structure_public_data_quality_status": model.get("data_quality_status", ""),
        }
    )
    return delivery
