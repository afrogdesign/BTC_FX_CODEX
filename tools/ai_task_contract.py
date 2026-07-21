#!/usr/bin/env python3
"""A1 task-manifest, prompt-rendering, and acceptance-report contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIMARY_REPO = "/Users/marupro/CODEX/100_MCP_Server/btc_monitor"
FROZEN_REPO = "/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor"
OUTBOX = "/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SENSITIVE_KEYS = re.compile(
    r"(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential|private[_-]?key|account[_-]?id|order[_-]?id|position[_-]?id)",
    re.I,
)
SENSITIVE_VALUE = re.compile(r"(?:^|\b)(?:sk-|xoxb-|AKIA)[A-Za-z0-9_\-/+=.]+|-----BEGIN .*PRIVATE KEY-----|\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
FORBIDDEN_COMMAND = re.compile(r"[\n\r;&|`]|\$\(|\b(?:nohup|disown|setsid|tmux|screen)\b")
STAGES = {"implementation", "acceptance", "review", "checkpoint", "runtime"}
MODES = {"BOUNDED_CODEX", "REVIEW_ONLY", "CHECKPOINT_PUSH", "RUNTIME_TASK"}
AUTONOMY_KEYS = {"edit_helpers", "add_fixtures", "add_regressions", "remove_duplicate_calculations", "add_semantics_preserving_cache", "choose_bounded_order"}


class ContractError(ValueError):
    pass


def _reject_constant(value: str) -> None:
    raise ContractError(f"non-finite number: {value}")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate key: {key}")
        result[key] = value
    return result


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        raw = Path(path).read_bytes()
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("JSON root must be an object")
    _scan_values(value)
    return value


def _scan_values(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractError("non-finite number")
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_KEYS.search(key) or (isinstance(child, str) and SENSITIVE_VALUE.search(child)):
                raise ContractError(f"sensitive material rejected near {key}")
            _scan_values(child)
    elif isinstance(value, list):
        for child in value:
            if isinstance(child, str) and SENSITIVE_VALUE.search(child):
                raise ContractError("sensitive material rejected")
            _scan_values(child)
    elif isinstance(value, str) and SENSITIVE_VALUE.search(value):
        raise ContractError("sensitive material rejected")


def canonical_sha(task: dict[str, Any]) -> str:
    encoded = json.dumps(task, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _object(value: Any, name: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{name} must be an object")
    unknown = set(value) - keys
    if unknown:
        raise ContractError(f"{name} has unknown fields: {sorted(unknown)}")
    return value


def _required(value: dict[str, Any], keys: set[str], name: str) -> None:
    missing = keys - set(value)
    if missing:
        raise ContractError(f"{name} missing fields: {sorted(missing)}")


def _string(value: Any, name: str, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        raise ContractError(f"{name} must be a non-empty string")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"{name} must be boolean")
    return value


def _path(value: Any, name: str) -> str:
    value = _string(value, name)
    if value.startswith(("/", "~")) or "\\" in value or value in {".", ".."}:
        raise ContractError(f"{name} must be a repo-relative POSIX path")
    parts = value.split("/")
    if any(not part or part in {".", ".."} for part in parts):
        raise ContractError(f"{name} must be normalized")
    return value


def _unique_paths(values: Any, name: str) -> list[str]:
    if not isinstance(values, list):
        raise ContractError(f"{name} must be an array")
    result = [_path(item, f"{name}[]") for item in values]
    if len(result) != len(set(result)):
        raise ContractError(f"{name} contains duplicate paths")
    return result


def _commands(values: Any, name: str) -> list[str]:
    if not isinstance(values, list):
        raise ContractError(f"{name} must be an array")
    result = []
    for item in values:
        command = _string(item, f"{name}[]")
        if FORBIDDEN_COMMAND.search(command):
            raise ContractError(f"unsafe foreground command: {command}")
        result.append(command)
    if len(result) != len(set(result)):
        raise ContractError(f"{name} contains duplicate commands")
    return result


def validate_task(task: dict[str, Any]) -> str:
    _scan_values(task)
    top_keys = {"schema_version", "work_id", "revision", "stage", "mode", "goal", "repo", "contract_refs", "allowed", "autonomy", "requirements", "validation", "commit", "stop_codes", "report"}
    _required(task, top_keys, "task")
    _object(task, "task", top_keys)
    if task["schema_version"] != 1.0:
        raise ContractError("schema_version must be exactly 1.0")
    if isinstance(task["revision"], bool) or not isinstance(task["revision"], int) or task["revision"] < 1:
        raise ContractError("revision must be an integer >= 1")
    for name in ("work_id", "goal"):
        _string(task[name], name)
    stage = _string(task["stage"], "stage")
    mode = _string(task["mode"], "mode")
    if stage not in STAGES or mode not in MODES:
        raise ContractError("invalid stage or mode")
    valid_pair = {"implementation": "BOUNDED_CODEX", "acceptance": "BOUNDED_CODEX", "review": "REVIEW_ONLY", "checkpoint": "CHECKPOINT_PUSH", "runtime": "RUNTIME_TASK"}
    if valid_pair[stage] != mode:
        raise ContractError("invalid stage/mode pair")

    repo = _object(task["repo"], "repo", {"expected_branch", "expected_base_commit", "working_dir", "frozen_runtime_repo"})
    _required(repo, {"expected_branch", "expected_base_commit", "working_dir", "frozen_runtime_repo"}, "repo")
    _string(repo["expected_branch"], "repo.expected_branch")
    if repo["expected_base_commit"] is not None and (not isinstance(repo["expected_base_commit"], str) or not HEX40.fullmatch(repo["expected_base_commit"])):
        raise ContractError("repo.expected_base_commit must be null or lowercase SHA-1")
    if repo["working_dir"] != PRIMARY_REPO:
        raise ContractError("repo.working_dir must be the primary repo")
    if stage != "runtime" and repo["frozen_runtime_repo"] not in (None, ""):
        raise ContractError("frozen runtime repo is valid only for runtime stage")
    if stage == "runtime" and repo["frozen_runtime_repo"] != FROZEN_REPO:
        raise ContractError("runtime stage requires the frozen runtime repo")

    _unique_paths(task["contract_refs"], "contract_refs")
    allowed = _object(task["allowed"], "allowed", {"read", "edit", "diff_check"})
    _required(allowed, {"read", "edit", "diff_check"}, "allowed")
    _unique_paths(allowed["read"], "allowed.read")
    edits = _unique_paths(allowed["edit"], "allowed.edit")
    diffs = _unique_paths(allowed["diff_check"], "allowed.diff_check")
    if not diffs:
        raise ContractError("allowed.diff_check must not be empty")
    autonomy = _object(task["autonomy"], "autonomy", AUTONOMY_KEYS)
    for key, value in autonomy.items():
        _bool(value, f"autonomy.{key}")
    requirements = task["requirements"]
    if not isinstance(requirements, list) or not requirements:
        raise ContractError("requirements must be a non-empty array")
    requirement_ids: list[str] = []
    for index, item in enumerate(requirements):
        item = _object(item, f"requirements[{index}]", {"id", "description"})
        _required(item, {"id", "description"}, f"requirements[{index}]")
        requirement_ids.append(_string(item["id"], f"requirements[{index}].id"))
        _string(item["description"], f"requirements[{index}].description")
    if len(requirement_ids) != len(set(requirement_ids)):
        raise ContractError("requirements IDs must be unique")

    validation = _object(task["validation"], "validation", {"unit_tests", "heavy"})
    _required(validation, {"unit_tests", "heavy"}, "validation")
    unit_tests = _commands(validation["unit_tests"], "validation.unit_tests")
    heavy = _object(validation["heavy"], "validation.heavy", {"authorized", "planned_work_units", "max_full_runs", "commands"})
    _required(heavy, {"authorized", "planned_work_units", "max_full_runs", "commands"}, "validation.heavy")
    authorized = _bool(heavy["authorized"], "validation.heavy.authorized")
    for key in ("planned_work_units", "max_full_runs"):
        if isinstance(heavy[key], bool) or not isinstance(heavy[key], int) or heavy[key] < 0:
            raise ContractError(f"validation.heavy.{key} must be a non-negative integer")
    heavy_commands = _commands(heavy["commands"], "validation.heavy.commands")
    if stage == "implementation" and (edits == [] or authorized or heavy["planned_work_units"] != 0 or heavy["max_full_runs"] != 0 or heavy_commands):
        raise ContractError("implementation must be bounded and non-heavy")
    if stage == "acceptance" and (edits or not authorized or heavy["planned_work_units"] <= 0 or heavy["max_full_runs"] != 1 or len(heavy_commands) != 1):
        raise ContractError("acceptance requires one authorized heavy command and no edits")
    if stage == "review" and edits:
        raise ContractError("review cannot edit files")
    if stage != "checkpoint" and task["commit"].get("enabled") is True and mode == "CHECKPOINT_PUSH":
        raise ContractError("checkpoint mode is only valid for checkpoint stage")
    if stage == "acceptance" and heavy["max_full_runs"] > 1:
        raise ContractError("A1 rejects more than one acceptance full run")
    for command in unit_tests:
        if command != command.strip():
            raise ContractError("commands must not have surrounding whitespace")
    commit = _object(task["commit"], "commit", {"enabled", "message"})
    _required(commit, {"enabled", "message"}, "commit")
    _bool(commit["enabled"], "commit.enabled")
    _string(commit["message"], "commit.message")
    stop_codes = task["stop_codes"]
    if not isinstance(stop_codes, list) or any(not isinstance(item, str) or not item for item in stop_codes) or len(stop_codes) != len(set(stop_codes)):
        raise ContractError("stop_codes must be unique non-empty strings")
    report = _object(task["report"], "report", {"format", "outbox", "write_once"})
    _required(report, {"format", "outbox", "write_once"}, "report")
    if report["format"] != "json_v1" or report["outbox"] != OUTBOX or report["write_once"] is not True:
        raise ContractError("report must use the canonical json_v1 outbox contract")
    return canonical_sha(task)


def canonical_diff_command(diff_paths: list[str]) -> str:
    return "git diff --check -- " + " ".join(diff_paths)


def _manifest_path(path: str | Path) -> str:
    return Path(path).resolve().relative_to(REPO_ROOT).as_posix()


def render_prompt(task: dict[str, Any], task_path: str | Path, context: str) -> str:
    if context not in {"fresh", "delta"}:
        raise ContractError("context must be fresh or delta")
    sha = validate_task(task)
    read_line = "read AGENTS.md, START_HERE.md, and the manifest" if context == "fresh" else "read only the changed manifest and named files"
    lines = [
        "AUTO_SEND",
        f"WORK_ID: {task['work_id']}",
        f"MODE: {task['mode']}",
        f"MANIFEST: {_manifest_path(task_path)}",
        f"REVISION: {task['revision']}",
        f"TASK_SHA256: {sha}",
        f"CONTEXT: {context}",
        f"READ: {read_line}.",
        "VALIDATE: use the task contract and the listed focused commands.",
        "EXECUTE: perform only the allowed bounded task; preserve safety boundaries and manual prompt routing.",
        "NO_EXPANSION: do not add runtime, production, mail, API, account, position, order, replay, CWT, or M6 work.",
        "REPORT: produce the configured json_v1 report and write it once to the canonical outbox without read-back, retry, polling, or recreation.",
    ]
    limit = 20 if context == "fresh" else 14
    if len(lines) > limit:
        raise ContractError("rendered prompt exceeds context line limit")
    return "\n".join(lines)


def validate_report(task: dict[str, Any], report: dict[str, Any], task_path: str | Path) -> None:
    task_sha = validate_task(task)
    keys = {"schema_version", "work_id", "task_revision", "task_sha256", "status", "branch", "base_commit", "changed_files", "requirements", "tests", "heavy_validation", "commit", "push", "notes"}
    _required(report, keys, "report")
    _object(report, "report", keys)
    if report["schema_version"] != 1.0 or report["work_id"] != task["work_id"] or report["task_revision"] != task["revision"] or report["task_sha256"] != task_sha:
        raise ContractError("report task identity does not match manifest")
    if report["status"] not in {"done", "partial", "blocked", "failed"}:
        raise ContractError("invalid report status")
    _string(report["branch"], "report.branch")
    if not isinstance(report["base_commit"], str) or not HEX40.fullmatch(report["base_commit"]):
        raise ContractError("report.base_commit must be a lowercase 40-character hash")
    repo = task["repo"]
    if report["branch"] != repo["expected_branch"] or (repo["expected_base_commit"] is not None and report["base_commit"] != repo["expected_base_commit"]):
        raise ContractError("report branch or base commit does not match manifest")
    changed = _unique_paths(report["changed_files"], "report.changed_files")
    allowed_edit = set(task["allowed"]["edit"])
    if not set(changed) <= allowed_edit:
        raise ContractError("report contains changed files outside allowed.edit")
    req_ids = [item["id"] for item in task["requirements"]]
    req_evidence = _object(report["requirements"], "report.requirements", set(req_ids))
    if set(req_evidence) != set(req_ids):
        raise ContractError("report requirement keys do not match manifest")
    for key, item in req_evidence.items():
        item = _object(item, f"report.requirements.{key}", {"status", "evidence"})
        _required(item, {"status", "evidence"}, f"report.requirements.{key}")
        if item["status"] not in {"pass", "fail", "not_run"}:
            raise ContractError("invalid requirement evidence status")
        _string(item["evidence"], f"report.requirements.{key}.evidence")
    tests = report["tests"]
    if not isinstance(tests, list):
        raise ContractError("report.tests must be an array")
    expected_commands = list(task["validation"]["unit_tests"]) + [canonical_diff_command(task["allowed"]["diff_check"])]
    actual_commands = []
    for index, item in enumerate(tests):
        item = _object(item, f"report.tests[{index}]", {"command", "status", "evidence"})
        _required(item, {"command", "status", "evidence"}, f"report.tests[{index}]")
        command = _string(item["command"], "test command")
        if item["status"] not in {"pass", "fail", "not_run"}:
            raise ContractError("invalid test evidence status")
        _string(item["evidence"], "test evidence")
        actual_commands.append(command)
    if actual_commands != expected_commands or len(actual_commands) != len(set(actual_commands)):
        raise ContractError("report test commands do not exactly match the manifest")
    heavy = _object(report["heavy_validation"], "report.heavy_validation", {"authorized", "planned_work_units", "full_runs", "commands"})
    _required(heavy, {"authorized", "planned_work_units", "full_runs", "commands"}, "report.heavy_validation")
    if heavy["authorized"] != task["validation"]["heavy"]["authorized"] or heavy["planned_work_units"] != task["validation"]["heavy"]["planned_work_units"] or heavy["full_runs"] != task["validation"]["heavy"]["max_full_runs"]:
        raise ContractError("heavy validation does not match manifest")
    heavy_items = heavy["commands"]
    if not isinstance(heavy_items, list) or len(heavy_items) != len(task["validation"]["heavy"]["commands"]):
        raise ContractError("heavy command evidence does not match manifest")
    for index, item in enumerate(heavy_items):
        item = _object(item, f"heavy command {index}", {"command", "status", "evidence"})
        _required(item, {"command", "status", "evidence"}, "heavy command")
        if item["command"] != task["validation"]["heavy"]["commands"][index] or item["status"] not in {"pass", "fail", "not_run"}:
            raise ContractError("heavy command mismatch")
        _string(item["evidence"], "heavy evidence")
    commit = report["commit"]
    if commit is not None:
        commit = _object(commit, "report.commit", {"hash", "message"})
        _required(commit, {"hash", "message"}, "report.commit")
        if not HEX40.fullmatch(commit["hash"]):
            raise ContractError("commit hash must be lowercase hexadecimal")
        _string(commit["message"], "commit.message")
    push = report["push"]
    if push is not None:
        push = _object(push, "report.push", {"remote", "branch", "commit"})
        _required(push, {"remote", "branch", "commit"}, "report.push")
        if task["mode"] != "CHECKPOINT_PUSH":
            raise ContractError("push is not authorized")
        if not HEX40.fullmatch(push["commit"]):
            raise ContractError("push commit must be lowercase hexadecimal")
    _string(report["notes"], "report.notes", nonempty=False)
    if report["status"] == "done":
        if any(item["status"] != "pass" for item in req_evidence.values()) or any(item["status"] != "pass" for item in tests):
            raise ContractError("done report requires all evidence to pass")
        if task["stage"] == "acceptance" and (heavy["full_runs"] != 1 or any(item["status"] != "pass" for item in heavy_items)):
            raise ContractError("done acceptance report requires one passing heavy run")
        if task["commit"]["enabled"]:
            if commit is None or commit["message"] != task["commit"]["message"]:
                raise ContractError("done report requires the configured commit")
        elif commit is not None:
            raise ContractError("commit must be null when disabled")


def _success(message: str) -> int:
    print(message)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai_task_contract")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-task")
    validate.add_argument("--task", required=True)
    render = sub.add_parser("render-prompt")
    render.add_argument("--task", required=True)
    render.add_argument("--context", required=True, choices=("fresh", "delta"))
    report = sub.add_parser("validate-report")
    report.add_argument("--task", required=True)
    report.add_argument("--report", required=True)
    try:
        if argv is None:
            argv = sys.argv[1:]
        args = parser.parse_args(argv)
        task = load_json(args.task)
        if args.command == "validate-task":
            return _success(f"valid task {canonical_sha(task)}") if validate_task(task) else 1
        if args.command == "render-prompt":
            print(render_prompt(task, args.task, args.context))
            return 0
        report_data = load_json(args.report)
        validate_report(task, report_data, args.task)
        return _success("valid report")
    except (ContractError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
