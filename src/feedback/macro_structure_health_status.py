"""Deterministic, read-only health status for the macro structure service."""

from __future__ import annotations

import hashlib
import json
import os
import plistlib
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SCHEMA_VERSION = "macro_structure_health_status.v1"
METHOD_VERSION = "macro_structure_health_status.v1"
RUNTIME_SCHEMA_VERSION = "macro_structure_runtime_service.v1"
RUNTIME_METHOD_VERSION = "macro_structure_runtime_service.v1"
SNAPSHOT_VERSION = "macro_structure_daily_operation.v1"
HISTORY_VERSION = "macro_structure_history_operation.v2"
OPERATOR_VERSION = "macro_structure_operator_artifact.v2"
JST = ZoneInfo("Asia/Tokyo")
SCHEDULE = ((1, 10), (5, 10), (9, 10), (13, 10), (17, 10), (21, 10))
GRACE_MINUTES = 60
BASE_DIR = Path(__file__).resolve().parents[2]


class HealthError(ValueError):
    def __init__(self, code: str, category: str = "unavailable") -> None:
        super().__init__(code)
        self.code = code
        self.category = category


def _json(path: Path, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise HealthError(code) from exc
    if not isinstance(value, dict):
        raise HealthError(code)
    return value


def _aware(value: Any, code: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise HealthError(code)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HealthError(code) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HealthError(code)
    return parsed.astimezone(timezone.utc)


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _iso_jst(value: datetime) -> str:
    return value.astimezone(JST).isoformat()


def _evaluation_time(value: str | None) -> datetime:
    if value is None:
        now = datetime.now(timezone.utc)
    else:
        now = _aware(value, "evaluation_time_invalid")
    return now.astimezone(timezone.utc).replace(second=0, microsecond=0)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(BASE_DIR.resolve()).as_posix()
    except ValueError:
        return path.name


def _require(condition: bool, code: str, category: str = "inconsistent") -> None:
    if not condition:
        raise HealthError(code, category)


def _read_plist(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            value = plistlib.load(handle)
    except (OSError, ValueError, plistlib.InvalidFileException) as exc:
        raise HealthError("plist_unavailable") from exc
    if not isinstance(value, dict):
        raise HealthError("plist_malformed")
    return value


def _scheduled(eval_utc: datetime) -> tuple[datetime, datetime]:
    local = eval_utc.astimezone(JST)
    candidates = [datetime(local.year, local.month, local.day, hour, minute, tzinfo=JST)
                  for hour, minute in SCHEDULE]
    previous = [item for item in candidates if item <= local]
    if previous:
        last = previous[-1]
    else:
        prior_day = local.date() - timedelta(days=1)
        last = datetime(prior_day.year, prior_day.month, prior_day.day, *SCHEDULE[-1], tzinfo=JST)
    following = [item for item in candidates if item > local]
    if following:
        upcoming = following[0]
    else:
        next_day = local.date() + timedelta(days=1)
        upcoming = datetime(next_day.year, next_day.month, next_day.day, *SCHEDULE[0], tzinfo=JST)
    return last.astimezone(timezone.utc), upcoming.astimezone(timezone.utc)


def _validate_plist(path: Path) -> dict[str, Any]:
    plist = _read_plist(path)
    _require(plist.get("Label") == "com.afrog.btc-macro-structure", "plist_label_mismatch")
    args = plist.get("ProgramArguments")
    _require(args == [
        "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/.venv312/bin/python",
        "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/tools/run_macro_structure_service.py",
    ], "plist_program_mismatch")
    _require(plist.get("WorkingDirectory") == "/Users/marupro/CODEX/100_MCP_Server/btc_monitor", "plist_working_directory_mismatch")
    _require(plist.get("StandardOutPath") == "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/logs/runtime/macro_structure_service.launchd.out", "plist_stdout_mismatch")
    _require(plist.get("StandardErrorPath") == "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/logs/runtime/macro_structure_service.launchd.err", "plist_stderr_mismatch")
    _require("RunAtLoad" not in plist and "KeepAlive" not in plist, "plist_persistent_trigger_forbidden")
    entries = plist.get("StartCalendarInterval")
    try:
        actual = tuple(sorted((int(item.get("Hour")), int(item.get("Minute"))) for item in entries or [] if isinstance(item, dict)))
    except (TypeError, ValueError) as exc:
        raise HealthError("plist_schedule_malformed") from exc
    _require(actual == SCHEDULE, "plist_schedule_mismatch")
    return plist


def _boundary(value: dict[str, Any], prefix: str) -> None:
    _require(value.get("report_only") is True, f"{prefix}_report_only_mismatch")
    _require(value.get("private_actual_trade_input") is False, f"{prefix}_private_input_mismatch")
    _require(value.get("automatic_order_allowed") is False, f"{prefix}_automatic_order_mismatch")


def _artifact(root: Path, latest_name: str, identity: str, files: tuple[str, ...], schema: str, method: str, symbol: str, prefix: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path, dict[str, str]]:
    latest = _json(root / "latest.json", f"{prefix}_latest_unavailable")
    artifact_dir_name = latest.get("artifact_dir")
    _require(isinstance(artifact_dir_name, str) and artifact_dir_name == identity, f"{prefix}_latest_id_mismatch")
    artifact = root / artifact_dir_name
    _require(artifact.parent.resolve() == root.resolve() and artifact.resolve().parent == root.resolve() and artifact.name == artifact_dir_name and artifact.is_dir(), f"{prefix}_path_invalid")
    for filename in files:
        _require((artifact / filename).is_file(), f"{prefix}_incomplete")
    main_name = {"snapshot": "macro_structure_snapshot.json", "history": "macro_structure_history.json", "operator": "macro_structure_operator.json"}[prefix]
    main = _json(artifact / main_name, f"{prefix}_json_invalid")
    manifest = _json(artifact / "run_manifest.json", f"{prefix}_manifest_invalid")
    _require(main.get("schema_version") == schema and main.get("method_version") == method, f"{prefix}_version_mismatch")
    _require(manifest.get("schema_version") == schema and manifest.get("method_version") == method, f"{prefix}_manifest_version_mismatch")
    _boundary(manifest, prefix)
    for payload in (main, manifest):
        if payload.get("symbol") is not None:
            _require(payload.get("symbol") == symbol, f"{prefix}_symbol_mismatch")
    _require(identity in {main.get("artifact_dir"), main.get("run_id"), main.get("history_id"), main.get("operator_artifact_id"), main.get("snapshot_id")}, f"{prefix}_identity_missing")
    fingerprints = {f"{prefix}:latest.json": _sha256(root / "latest.json")}
    fingerprints.update({f"{prefix}:{name}": _sha256(artifact / name) for name in files})
    return latest, main, manifest, artifact, fingerprints


def _validate_runtime(path: Path, symbol: str | None = None) -> tuple[dict[str, Any], dict[str, str]]:
    status = _json(path, "runtime_status_unavailable")
    _require(status.get("service_schema_version") == RUNTIME_SCHEMA_VERSION and status.get("service_method_version") == RUNTIME_METHOD_VERSION, "runtime_version_mismatch")
    for field in ("started_at_utc", "finished_at_utc", "evaluation_utc"):
        _aware(status.get(field), "runtime_timestamp_invalid")
    for utc_field, jst_field in (("started_at_utc", "started_at_jst"), ("finished_at_utc", "finished_at_jst"), ("evaluation_utc", "evaluation_jst")):
        if status.get(jst_field) is not None:
            utc_value = _aware(status[utc_field], "runtime_timestamp_invalid")
            try:
                jst_value = datetime.fromisoformat(str(status[jst_field]).replace("Z", "+00:00"))
            except ValueError as exc:
                raise HealthError("runtime_timestamp_invalid") from exc
            _require(jst_value.tzinfo is not None and jst_value.utcoffset() is not None and jst_value == utc_value.astimezone(JST), "runtime_timestamp_timezone_mismatch", "unavailable")
    _require(isinstance(status.get("symbol"), str) and bool(status.get("symbol")), "runtime_symbol_missing")
    if symbol is not None:
        _require(status.get("symbol") == symbol, "runtime_symbol_mismatch")
    _require(status.get("status") in {"success", "failed", "already_running"}, "runtime_status_invalid")
    _boundary(status, "runtime")
    steps = status.get("steps")
    _require(isinstance(steps, list), "runtime_steps_invalid")
    if status.get("status") == "success":
        _require(status.get("ok") is True, "runtime_success_ok_missing")
        _require(len(steps) == 3 and [item.get("name") for item in steps] == ["snapshot", "history", "operator"], "runtime_step_order")
        _require(all(item.get("status") == "success" for item in steps), "runtime_success_step_failed")
    elif status.get("status") == "failed":
        _require(status.get("ok") is not True, "runtime_failed_ok_true")
        _require(isinstance(status.get("error_code"), str) and bool(status["error_code"]), "runtime_error_missing")
        if steps:
            names = [item.get("name") for item in steps]
            _require(names == ["snapshot", "history", "operator"][:len(steps)], "runtime_step_order")
            _require(steps[-1].get("status") == "failed", "runtime_failed_step_missing")
            _require(all(item.get("status") == "success" for item in steps[:-1]), "runtime_step_after_failure")
    else:
        _require(not steps, "runtime_already_running_steps")
    for item in steps:
        _require(isinstance(item, dict) and item.get("status") in {"success", "failed"} and isinstance(item.get("return_code"), int), "runtime_step_invalid")
    fingerprints = status.get("public_input_fingerprints")
    if steps:
        _require(isinstance(fingerprints, dict) and set(fingerprints) == {"15m", "1h", "4h"} and all(isinstance(fingerprints.get(key), str) and fingerprints[key] for key in ("15m", "1h", "4h")), "runtime_public_inputs_invalid")
    elif fingerprints not in (None, {}):
        _require(isinstance(fingerprints, dict) and set(fingerprints) == {"15m", "1h", "4h"}, "runtime_public_inputs_invalid")
    for field in ("snapshot_result_status", "history_result_status", "stale_status", "continuity_status", "data_quality_status"):
        if status.get("status") == "success":
            _require(status.get(field) not in (None, ""), f"runtime_{field}_missing")
    return status, {f"input:public:{key}": value for key, value in (fingerprints or {}).items()}


def _validate_snapshot_fields(snapshot: dict[str, Any], manifest: dict[str, Any]) -> None:
    for field in ("as_of_utc", "evaluated_at_utc"):
        _aware(snapshot.get(field), "snapshot_timestamp_missing")
        _aware(manifest.get(field), "snapshot_manifest_timestamp_missing")
        _require(_aware(snapshot[field], "snapshot_timestamp_invalid") == _aware(manifest[field], "snapshot_manifest_timestamp_mismatch"), "snapshot_manifest_timestamp_mismatch")
    for utc_field, jst_field in (("as_of_utc", "as_of_jst"), ("evaluated_at_utc", "evaluated_at_jst")):
        _require(isinstance(snapshot.get(jst_field), str), "snapshot_jst_missing", "unavailable")
        try:
            jst_value = datetime.fromisoformat(snapshot[jst_field].replace("Z", "+00:00"))
        except ValueError as exc:
            raise HealthError("snapshot_jst_invalid", "unavailable") from exc
        _require(jst_value.tzinfo is not None and jst_value.utcoffset() is not None, "snapshot_jst_invalid", "unavailable")
        _require(jst_value == _aware(snapshot[utc_field], "snapshot_timestamp_invalid").astimezone(JST), "snapshot_jst_mismatch")
    _require(snapshot.get("result_status") in {"ok", "insufficient"}, "snapshot_result_status_missing", "unavailable")
    _require(isinstance(snapshot.get("freshness"), dict) and all(isinstance(snapshot["freshness"].get(key), dict) for key in ("15m", "1h", "4h")), "snapshot_freshness_missing", "unavailable")
    _require(isinstance(snapshot.get("reliability_band_counts"), dict), "snapshot_reliability_counts_missing", "unavailable")
    _require(isinstance(snapshot.get("stale_status"), str) and isinstance(snapshot.get("continuity_status"), str), "snapshot_operator_status_missing", "unavailable")


def _validate_coherence(status: dict[str, Any], snapshot_root: Path, history_root: Path, operator_root: Path, symbol: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    _require(status.get("status") == "success", "runtime_not_success")
    snapshot_latest, snapshot, snapshot_manifest, snapshot_dir, snapshot_fp = _artifact(snapshot_root, "latest.json", status.get("snapshot_run_id", ""), ("macro_structure_snapshot.json", "macro_structure_snapshot.md", "macro_level_reliability.csv", "run_manifest.json"), SNAPSHOT_VERSION, SNAPSHOT_VERSION, symbol, "snapshot")
    history_latest, history, history_manifest, history_dir, history_fp = _artifact(history_root, "latest.json", status.get("history_id", ""), ("macro_structure_history.json", "macro_structure_history.md", "macro_snapshot_history.csv", "macro_level_history.csv", "macro_structure_changes.csv", "run_manifest.json"), HISTORY_VERSION, HISTORY_VERSION, symbol, "history")
    operator_latest, operator, operator_manifest, operator_dir, operator_fp = _artifact(operator_root, "latest.json", status.get("operator_artifact_id", ""), ("macro_structure_operator.html", "macro_structure_operator.json", "macro_structure_operator.md", "run_manifest.json"), OPERATOR_VERSION, OPERATOR_VERSION, symbol, "operator")
    _require(snapshot.get("run_id") == status.get("snapshot_run_id") and snapshot.get("snapshot_id") == status.get("snapshot_id"), "snapshot_runtime_identity_mismatch")
    _validate_snapshot_fields(snapshot, snapshot_manifest)
    _require(history.get("history_id") == status.get("history_id"), "history_runtime_identity_mismatch")
    _require(operator.get("operator_artifact_id") == status.get("operator_artifact_id"), "operator_runtime_identity_mismatch")
    _require(operator.get("selected_snapshot_run_id") == status.get("snapshot_run_id") and operator.get("selected_snapshot_id") == status.get("snapshot_id"), "operator_selected_snapshot_mismatch")
    _require(operator.get("selected_history_id") == status.get("history_id"), "operator_selected_history_mismatch")
    _require(snapshot.get("result_status") == status.get("snapshot_result_status"), "snapshot_result_status_mismatch")
    _require(history.get("result_status") == status.get("history_result_status"), "history_result_status_mismatch")
    _require(snapshot_latest.get("artifact_dir") == snapshot_dir.name and history_latest.get("artifact_dir") == history_dir.name and operator_latest.get("artifact_dir") == operator_dir.name, "latest_pointer_mismatch")
    operator = dict(operator)
    operator["_validated_artifact_dir"] = operator_dir.name
    fingerprints = {**snapshot_fp, **history_fp, **operator_fp}
    return snapshot, history, operator, {**fingerprints}


def _validate_partial_coherence(status: dict[str, Any], snapshot_root: Path, history_root: Path, operator_root: Path, symbol: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    """Validate identities for steps that completed before a later failure."""
    completed = {item.get("name") for item in status.get("steps", []) if item.get("status") == "success"}
    snapshot = history = operator = {}
    fingerprints: dict[str, str] = {}
    if "snapshot" in completed:
        for field in ("snapshot_run_id", "snapshot_id", "snapshot_result_status", "stale_status", "continuity_status", "data_quality_status"):
            _require(status.get(field) not in (None, ""), f"runtime_{field}_missing")
        _, snapshot, snapshot_manifest, _, fp = _artifact(snapshot_root, "latest.json", status.get("snapshot_run_id", ""), ("macro_structure_snapshot.json", "macro_structure_snapshot.md", "macro_level_reliability.csv", "run_manifest.json"), SNAPSHOT_VERSION, SNAPSHOT_VERSION, symbol, "snapshot")
        _validate_snapshot_fields(snapshot, snapshot_manifest)
        _require(snapshot.get("snapshot_id") == status.get("snapshot_id"), "snapshot_runtime_identity_mismatch")
        _require(snapshot.get("result_status") == status.get("snapshot_result_status"), "snapshot_result_status_mismatch")
        fingerprints.update(fp)
    if "history" in completed:
        for field in ("history_id", "history_result_status"):
            _require(status.get(field) not in (None, ""), f"runtime_{field}_missing")
        _, history, _, _, fp = _artifact(history_root, "latest.json", status.get("history_id", ""), ("macro_structure_history.json", "macro_structure_history.md", "macro_snapshot_history.csv", "macro_level_history.csv", "macro_structure_changes.csv", "run_manifest.json"), HISTORY_VERSION, HISTORY_VERSION, symbol, "history")
        _require(history.get("result_status") == status.get("history_result_status"), "history_result_status_mismatch")
        fingerprints.update(fp)
    if "operator" in completed:
        _require(status.get("operator_artifact_id") not in (None, ""), "runtime_operator_artifact_id_missing")
        _, operator, _, _, fp = _artifact(operator_root, "latest.json", status.get("operator_artifact_id", ""), ("macro_structure_operator.html", "macro_structure_operator.json", "macro_structure_operator.md", "run_manifest.json"), OPERATOR_VERSION, OPERATOR_VERSION, symbol, "operator")
        _require(operator.get("operator_artifact_id") == status.get("operator_artifact_id"), "operator_runtime_identity_mismatch")
        _require(operator.get("selected_snapshot_id") == status.get("snapshot_id") and operator.get("selected_history_id") == status.get("history_id"), "operator_selected_source_mismatch")
        operator = dict(operator)
        operator["_validated_artifact_dir"] = (operator_root / status["operator_artifact_id"]).name
        fingerprints.update(fp)
    return snapshot, history, operator, fingerprints


def _health_id(symbol: str, evaluation: datetime, source_fingerprints: dict[str, str]) -> str:
    raw = json.dumps({"schema": SCHEMA_VERSION, "method": METHOD_VERSION, "symbol": symbol, "evaluation": _iso_utc(evaluation), "sources": source_fingerprints}, sort_keys=True, separators=(",", ":"))
    return "health_" + hashlib.sha256(raw.encode()).hexdigest()[:20]


def _operation_result_status(status: dict[str, Any], name: str) -> str:
    for step in status.get("steps", []):
        if step.get("name") == name:
            return "ok" if step.get("status") == "success" else "failed"
    return "not_run"


def _publish(output_root: Path, health_id: str, payload: dict[str, Any], markdown: str, manifest: dict[str, Any]) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    files = {"macro_structure_health.json": json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", "macro_structure_health.md": markdown, "run_manifest.json": json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    with tempfile.TemporaryDirectory(prefix=".health-stage-", dir=output_root) as stage_name:
        stage = Path(stage_name) / health_id
        stage.mkdir()
        for name, text in files.items():
            (stage / name).write_text(text, encoding="utf-8")
        target = output_root / health_id
        if target.exists():
            if not target.is_dir() or any(not (target / name).is_file() or (target / name).read_bytes() != (stage / name).read_bytes() for name in files):
                raise HealthError("existing_health_conflict", "inconsistent")
        else:
            os.replace(stage, target)
    latest = {"artifact_dir": health_id, "health_artifact_id": health_id, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "health_state": payload["health_state"], "severity": payload["severity"], "evaluation_utc": payload["evaluation_utc"], "evaluation_jst": payload.get("evaluation_jst"), "last_scheduled_utc": payload.get("last_scheduled_utc"), "next_scheduled_utc": payload.get("next_scheduled_utc"), "runtime_status": payload.get("runtime_status"), "runtime_age_minutes": payload.get("runtime_age_minutes"), "overdue": payload.get("overdue"), "symbol": payload.get("symbol"), "snapshot_run_id": payload.get("snapshot_run_id"), "snapshot_id": payload.get("snapshot_id"), "history_id": payload.get("history_id"), "operator_artifact_id": payload.get("operator_artifact_id"), "snapshot_result_status": payload.get("snapshot_result_status"), "history_result_status": payload.get("history_result_status"), "operator_result_status": payload.get("operator_result_status"), "latest_as_of_utc": payload.get("latest_as_of_utc"), "latest_evaluated_at_utc": payload.get("latest_evaluated_at_utc"), "latest_evaluated_at_jst": payload.get("latest_evaluated_at_jst"), "stale_status": payload.get("stale_status"), "continuity_status": payload.get("continuity_status"), "data_quality_status": payload.get("data_quality_status"), "displayed_zone_counts": payload.get("displayed_zone_counts", {}), "operator_html_path": payload.get("operator_html_path"), "runtime_stdout_path": payload.get("runtime_stdout_path"), "runtime_stderr_path": payload.get("runtime_stderr_path"), "runtime_status_path": payload.get("runtime_status_path"), "report_only": True, "private_actual_trade_input": False, "automatic_order_allowed": False, "source_fingerprints": payload.get("source_fingerprints", {})}
    if latest.get("operator_html_path") is None:
        latest.pop("operator_html_path", None)
    latest_text = json.dumps(latest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=".latest-", dir=output_root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(latest_text)
        os.replace(temp_name, output_root / "latest.json")
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return target


def _markdown(payload: dict[str, Any]) -> str:
    return "\n".join([
        "# Macro Structure Health",
        "",
        f"- service health: {payload['health_state']} ({payload['severity']})",
        f"- last expected run: {payload.get('last_scheduled_jst', 'unavailable')}",
        f"- next expected run: {payload.get('next_scheduled_jst', 'unavailable')}",
        f"- runtime result age minutes: {payload.get('runtime_age_minutes', 'unavailable')}",
        f"- latest evidence cutoff: {payload.get('latest_as_of_utc', 'unavailable')}",
        f"- latest evaluation: {payload.get('latest_evaluated_at_utc', payload['evaluation_utc'])}",
        f"- warning: stale={payload.get('stale_status', 'unavailable')}, continuity={payload.get('continuity_status', 'unavailable')}, data_quality={payload.get('data_quality_status', 'unavailable')}, snapshot={payload.get('snapshot_result_status', 'unavailable')}, operator={payload.get('operator_result_status', 'not_run')}",
        f"- operator HTML: {payload.get('operator_html_path', 'unavailable')}",
        f"- runtime logs: {payload.get('runtime_stdout_path', 'unavailable')}; {payload.get('runtime_stderr_path', 'unavailable')}; {payload.get('runtime_status_path', 'unavailable')}",
        "- report-only: true; automatic order: false; human decides manually",
        "",
        "## Contract checks",
        "",
        *[f"- {key}: {value}" for key, value in sorted(payload.get("contract_checks", {}).items())],
        "",
        "## Safety boundary",
        "",
        "- report-only / no private or actual-trade input / no automatic order",
        "",
    ])


def check_macro_structure_health(*, runtime_status: Path = Path("logs/runtime/macro_structure_service_last_result.json"), snapshot_root: Path = Path("local/reports/macro_structure"), history_root: Path = Path("local/reports/macro_structure/history"), operator_root: Path = Path("local/reports/macro_structure/operator"), plist: Path = Path("deploy/com.afrog.btc-macro-structure.plist"), output_root: Path = Path("local/reports/macro_structure/health"), evaluation_time_utc: str | None = None) -> dict[str, Any]:
    evaluation = _evaluation_time(evaluation_time_utc)
    symbol = ""
    source_fingerprints: dict[str, str] = {}
    try:
        if runtime_status.is_file():
            source_fingerprints["input:runtime_status"] = _sha256(runtime_status)
        if plist.is_file():
            source_fingerprints["input:plist"] = _sha256(plist)
        status, runtime_fp = _validate_runtime(runtime_status)
        symbol = status["symbol"]
        source_fingerprints.update(runtime_fp)
        _validate_plist(plist)
        snapshot = history = operator = {}
        artifact_fp: dict[str, str] = {}
        if status.get("status") == "success":
            snapshot, history, operator, artifact_fp = _validate_coherence(status, snapshot_root, history_root, operator_root, symbol)
            source_fingerprints.update(artifact_fp)
        else:
            snapshot, history, operator, artifact_fp = _validate_partial_coherence(status, snapshot_root, history_root, operator_root, symbol)
            source_fingerprints.update(artifact_fp)
        last_scheduled, next_scheduled = _scheduled(evaluation)
        finished = _aware(status.get("finished_at_utc"), "runtime_timestamp_invalid")
        age = max(0.0, round((evaluation - finished).total_seconds() / 60.0, 3))
        overdue = evaluation > last_scheduled + timedelta(minutes=GRACE_MINUTES) and finished < last_scheduled
        if overdue:
            state = "overdue"
        elif status.get("status") == "failed":
            state = "failed"
        elif status.get("stale_status") != "current" or status.get("continuity_status") != "continuous" or status.get("data_quality_status") != "ok":
            state = "degraded"
        elif status.get("snapshot_result_status") == "insufficient":
            state = "healthy_insufficient"
        else:
            state = "healthy"
        severity = "ok" if state in {"healthy", "healthy_insufficient"} else ("warning" if state in {"degraded", "overdue"} else "error")
        snapshot_result_status = snapshot.get("result_status") if snapshot else ("failed" if _operation_result_status(status, "snapshot") == "failed" else status.get("snapshot_result_status") or "not_run")
        history_result_status = history.get("result_status") if history else ("failed" if _operation_result_status(status, "history") == "failed" else status.get("history_result_status") or "not_run")
        operator_result_status = _operation_result_status(status, "operator")
        operator_dir = operator.get("_validated_artifact_dir") if operator else None
        operator_root_relative = _relative(operator_root)
        operator_html_path = f"{operator_root_relative}/{operator_dir}/macro_structure_operator.html" if operator_dir else None
        _require(operator_html_path is None or Path(operator_html_path).name == "macro_structure_operator.html", "operator_html_path_invalid")
        latest_evaluated_at_utc = snapshot.get("evaluated_at_utc") if snapshot else None
        latest_evaluated_at_jst = snapshot.get("evaluated_at_jst") if snapshot else None
        plist_value = _validate_plist(plist)
        payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "health_state": state, "severity": severity,
            "evaluation_utc": _iso_utc(evaluation), "evaluation_jst": _iso_jst(evaluation),
            "last_scheduled_utc": _iso_utc(last_scheduled), "last_scheduled_jst": _iso_jst(last_scheduled),
            "next_scheduled_utc": _iso_utc(next_scheduled), "next_scheduled_jst": _iso_jst(next_scheduled), "grace_minutes": GRACE_MINUTES,
            "runtime_started_at_utc": status.get("started_at_utc"), "runtime_started_at_jst": status.get("started_at_jst"), "runtime_finished_at_utc": status.get("finished_at_utc"), "runtime_finished_at_jst": status.get("finished_at_jst"), "runtime_evaluation_utc": status.get("evaluation_utc"), "runtime_evaluation_jst": status.get("evaluation_jst"),
            "runtime_status": status.get("status"), "runtime_status_path": _relative(runtime_status), "runtime_age_minutes": age, "overdue": overdue, "symbol": symbol, "first_failed_step": next((item.get("name") for item in status.get("steps", []) if item.get("status") == "failed"), None), "runtime_error_code": status.get("error_code"),
            "snapshot_run_id": status.get("snapshot_run_id"), "snapshot_id": status.get("snapshot_id"), "history_id": status.get("history_id"), "operator_artifact_id": status.get("operator_artifact_id"),
            "snapshot_result_status": snapshot_result_status, "history_result_status": history_result_status, "operator_result_status": operator_result_status,
            "stale_status": status.get("stale_status"), "continuity_status": status.get("continuity_status"), "data_quality_status": status.get("data_quality_status"),
            "stale_timeframes": (snapshot.get("stale_timeframes") if snapshot else []), "latest_as_of_utc": snapshot.get("as_of_utc") if snapshot else None, "latest_evaluated_at_utc": latest_evaluated_at_utc, "latest_evaluated_at_jst": latest_evaluated_at_jst,
            "displayed_support_count": operator.get("displayed_support_count", operator.get("zones", {}).get("displayed_support_count", 0)), "displayed_resistance_count": operator.get("displayed_resistance_count", operator.get("zones", {}).get("displayed_resistance_count", 0)),
            "displayed_zone_counts": operator.get("displayed_zone_counts", operator.get("zones", {}).get("counts_by_role_and_band", {})), "public_input_fingerprints": status.get("public_input_fingerprints", {}),
            "snapshot_artifact_root": "local/reports/macro_structure", "history_artifact_root": "local/reports/macro_structure/history", "operator_artifact_root": "local/reports/macro_structure/operator",
            "runtime_status_path": _relative(runtime_status), "runtime_stdout_path": _relative(Path(plist_value["StandardOutPath"])), "runtime_stderr_path": _relative(Path(plist_value["StandardErrorPath"])), "operator_html_path": operator_html_path,
            "contract_checks": {"plist": True, "runtime": True, "snapshot": bool(snapshot), "history": bool(history), "operator": bool(operator), "safety": True},
            "reason_codes": sorted(set((snapshot.get("reason_codes") or []) if snapshot else [])), "source_fingerprints": source_fingerprints,
            "report_only": True, "private_actual_trade_input": False, "automatic_order_allowed": False, "safety_boundary": "report-only / no private or actual-trade input / no automatic order",
        }
    except HealthError as exc:
        state = exc.category if exc.category in {"inconsistent", "unavailable"} else "unavailable"
        symbol = symbol or "BTC_USDT"
        last_scheduled, next_scheduled = _scheduled(evaluation)
        payload = {
            "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "health_state": state, "severity": "error",
            "evaluation_utc": _iso_utc(evaluation), "evaluation_jst": _iso_jst(evaluation), "last_scheduled_utc": _iso_utc(last_scheduled), "last_scheduled_jst": _iso_jst(last_scheduled), "next_scheduled_utc": _iso_utc(next_scheduled), "next_scheduled_jst": _iso_jst(next_scheduled), "grace_minutes": GRACE_MINUTES,
            "symbol": symbol, "error_code": exc.code, "reason_codes": [exc.code], "source_fingerprints": source_fingerprints, "operator_result_status": "not_run", "runtime_status_path": _relative(runtime_status), "runtime_stdout_path": "logs/runtime/macro_structure_service.launchd.out", "runtime_stderr_path": "logs/runtime/macro_structure_service.launchd.err",
            "report_only": True, "private_actual_trade_input": False, "automatic_order_allowed": False, "safety_boundary": "report-only / no private or actual-trade input / no automatic order", "contract_checks": {},
        }
        status = {}
    health_id = _health_id(symbol, evaluation, source_fingerprints)
    payload["health_artifact_id"] = health_id
    payload["artifact_dir"] = health_id
    manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "health_artifact_id": health_id, "symbol": symbol, "evaluation_utc": payload["evaluation_utc"], "report_only": True, "private_actual_trade_input": False, "automatic_order_allowed": False, "safety_boundary": payload["safety_boundary"], "source_fingerprints": payload.get("source_fingerprints", {})}
    try:
        artifact = _publish(output_root, health_id, payload, _markdown(payload), manifest)
    except HealthError as exc:
        return {"ok": False, "exit_code": 3, "error_code": exc.code, "health_state": "inconsistent", "health_artifact_id": health_id, "report_written": False}
    exit_code = 0 if payload["health_state"] in {"healthy", "healthy_insufficient"} else (2 if payload["health_state"] in {"degraded", "overdue"} else 3)
    result = {"ok": exit_code == 0, "exit_code": exit_code, "report_written": True, "health_state": payload["health_state"], "severity": payload["severity"], "health_artifact_id": health_id, "artifact_dir": _relative(artifact), "evaluation_utc": payload["evaluation_utc"], "evaluation_jst": payload["evaluation_jst"], "symbol": symbol, "runtime_status": payload.get("runtime_status"), "snapshot_run_id": payload.get("snapshot_run_id"), "snapshot_id": payload.get("snapshot_id"), "history_id": payload.get("history_id"), "operator_artifact_id": payload.get("operator_artifact_id"), "snapshot_result_status": payload.get("snapshot_result_status"), "history_result_status": payload.get("history_result_status"), "operator_result_status": payload.get("operator_result_status"), "latest_evaluated_at_utc": payload.get("latest_evaluated_at_utc"), "latest_evaluated_at_jst": payload.get("latest_evaluated_at_jst"), "runtime_stdout_path": payload.get("runtime_stdout_path"), "runtime_stderr_path": payload.get("runtime_stderr_path"), "runtime_status_path": payload.get("runtime_status_path"), "stale_status": payload.get("stale_status"), "continuity_status": payload.get("continuity_status"), "data_quality_status": payload.get("data_quality_status"), "report_only": True, "private_actual_trade_input": False, "automatic_order_allowed": False}
    if payload.get("operator_html_path") is not None:
        result["operator_html_path"] = payload["operator_html_path"]
    return result
