#!/usr/bin/env python3
"""Standard-library validator and renderer for the A1 task contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIMARY_REPO = "/Users/marupro/CODEX/100_MCP_Server/btc_monitor"
FROZEN_REPO = "/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor"
OUTBOX = "/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SENSITIVE_KEYS = re.compile(r"(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential|private[_-]?key|account[_-]?id|order[_-]?id|position[_-]?id|raw_rows?)", re.I)
SENSITIVE_VALUE = re.compile(r"(?:^|\b)(?:sk-|xoxb-|AKIA)[A-Za-z0-9_\-/+=.]+|-----BEGIN .*PRIVATE KEY-----|\b[^\s@]+@[^ @]+\.[^ @]+\b")
UNSAFE_COMMAND = re.compile(r"[\n\r;&|`]|\$\(|\b(?:nohup|disown|setsid|tmux|screen)\b")
INSPECT_VALUES = {"git_status", "task_diff", "target_definition", "direct_callers", "nearby_helpers", "matching_tests"}
AUTONOMY_KEYS = {"helper_design", "cache_design", "fixture_design", "execution_order", "obvious_in_scope_bugfix", "remove_redundant_validation"}
STAGES = {"implementation", "acceptance", "review", "checkpoint", "runtime"}
MODES = {"BOUNDED_CODEX", "REVIEW_ONLY", "CHECKPOINT_PUSH", "RUNTIME_TASK"}


class ContractError(ValueError):
    """A concise fail-closed contract error."""


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
        value = json.loads(Path(path).read_bytes().decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("JSON root must be an object")
    _scan_sensitive(value)
    return value


def _scan_sensitive(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractError("non-finite number")
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_KEYS.search(str(key)):
                raise ContractError(f"sensitive key rejected: {key}")
            _scan_sensitive(child)
    elif isinstance(value, list):
        for child in value:
            _scan_sensitive(child)
    elif isinstance(value, str) and SENSITIVE_VALUE.search(value):
        raise ContractError("sensitive value rejected")


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
        raise ContractError(f"{name} must be a {'non-empty ' if nonempty else ''}string")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"{name} must be boolean")
    return value


def _path(value: Any, name: str) -> str:
    value = _string(value, name)
    if value.startswith(("/", "~")) or "\\" in value:
        raise ContractError(f"{name} must be a repo-relative POSIX path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ContractError(f"{name} must be normalized")
    return value


def _paths(value: Any, name: str) -> list[str]:
    if not isinstance(value, list):
        raise ContractError(f"{name} must be an array")
    result = [_path(item, f"{name}[]") for item in value]
    if len(result) != len(set(result)):
        raise ContractError(f"{name} contains duplicates")
    return result


def _commands(value: Any, name: str) -> list[str]:
    if not isinstance(value, list):
        raise ContractError(f"{name} must be an array")
    result = []
    for item in value:
        command = _string(item, f"{name}[]")
        if command != command.strip() or UNSAFE_COMMAND.search(command):
            raise ContractError(f"unsafe foreground command: {command}")
        result.append(command)
    if len(result) != len(set(result)):
        raise ContractError(f"{name} contains duplicates")
    return result


def _clauses(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ContractError("contract_refs must be a non-empty array")
    seen: set[str] = set()
    result = []
    for index, item in enumerate(value):
        item = _object(item, f"contract_refs[{index}]", {"path", "clauses"})
        _required(item, {"path", "clauses"}, f"contract_refs[{index}]")
        path = _path(item["path"], f"contract_refs[{index}].path")
        clauses = item["clauses"]
        if not isinstance(clauses, list) or not clauses or any(not isinstance(c, str) or not c for c in clauses):
            raise ContractError("contract reference clauses must be non-empty strings")
        if len(clauses) != len(set(clauses)) or path in seen:
            raise ContractError("contract references must be unique")
        seen.add(path)
        result.append({"path": path, "clauses": clauses})
    return result


def _fixture(value: Any) -> dict[str, Any]:
    value = _object(value, "validation.fixture_e2e", {"required", "location"})
    _required(value, {"required", "location"}, "validation.fixture_e2e")
    required = _bool(value["required"], "validation.fixture_e2e.required")
    if value["location"] is not None:
        _string(value["location"], "validation.fixture_e2e.location")
    elif required:
        raise ContractError("required fixture_e2e needs a location")
    return value


def validate_task(task: dict[str, Any]) -> str:
    _scan_sensitive(task)
    top = {"schema_version", "work_id", "revision", "stage", "mode", "goal", "repo", "contract_refs", "allowed", "autonomy", "requirements", "validation", "commit", "stop_codes", "report"}
    task = _object(task, "task", top)
    _required(task, top, "task")
    if task["schema_version"] != "1.0":
        raise ContractError("schema_version must be the string 1.0")
    if isinstance(task["revision"], bool) or not isinstance(task["revision"], int) or task["revision"] < 1:
        raise ContractError("revision must be an integer >= 1")
    _string(task["work_id"], "work_id")
    stage = _string(task["stage"], "stage")
    mode = _string(task["mode"], "mode")
    if stage not in STAGES or mode not in MODES or {"implementation": "BOUNDED_CODEX", "acceptance": "BOUNDED_CODEX", "review": "REVIEW_ONLY", "checkpoint": "CHECKPOINT_PUSH", "runtime": "RUNTIME_TASK"}[stage] != mode:
        raise ContractError("invalid stage/mode pair")
    _string(task["goal"], "goal")

    repo = _object(task["repo"], "repo", {"working_dir", "expected_branch", "expected_base_commit"})
    _required(repo, {"working_dir", "expected_branch", "expected_base_commit"}, "repo")
    working_dir = _string(repo["working_dir"], "repo.working_dir")
    if working_dir not in {PRIMARY_REPO, FROZEN_REPO} or (working_dir == FROZEN_REPO and stage != "runtime"):
        raise ContractError("invalid working_dir for stage")
    _string(repo["expected_branch"], "repo.expected_branch")
    if repo["expected_base_commit"] is not None and (not isinstance(repo["expected_base_commit"], str) or not HEX40.fullmatch(repo["expected_base_commit"])):
        raise ContractError("expected_base_commit must be null or lowercase SHA-1")
    _clauses(task["contract_refs"])

    allowed = _object(task["allowed"], "allowed", {"read", "edit", "inspect"})
    _required(allowed, {"read", "edit", "inspect"}, "allowed")
    reads = _paths(allowed["read"], "allowed.read")
    edits = _paths(allowed["edit"], "allowed.edit")
    inspect = allowed["inspect"]
    if not isinstance(inspect, list) or any(item not in INSPECT_VALUES for item in inspect) or len(inspect) != len(set(inspect)):
        raise ContractError("allowed.inspect contains an invalid or duplicate value")
    if stage == "implementation" and not edits:
        raise ContractError("implementation requires non-empty allowed.edit")
    if stage in {"acceptance", "review"} and edits:
        raise ContractError(f"{stage} requires empty allowed.edit")
    if not reads and not inspect:
        raise ContractError("allowed.read or allowed.inspect is required")

    autonomy = _object(task["autonomy"], "autonomy", AUTONOMY_KEYS)
    for key, value in autonomy.items():
        _bool(value, f"autonomy.{key}")
    requirements = task["requirements"]
    if not isinstance(requirements, list) or not requirements:
        raise ContractError("requirements must be a non-empty array")
    ids: list[str] = []
    for index, item in enumerate(requirements):
        item = _object(item, f"requirements[{index}]", {"id", "description"})
        _required(item, {"id", "description"}, f"requirements[{index}]")
        ids.append(_string(item["id"], "requirement.id"))
        _string(item["description"], "requirement.description")
    if len(ids) != len(set(ids)):
        raise ContractError("requirement IDs must be unique")

    validation = _object(task["validation"], "validation", {"unit_tests", "fixture_e2e", "diff_check_files", "heavy"})
    _required(validation, {"unit_tests", "fixture_e2e", "diff_check_files", "heavy"}, "validation")
    unit_tests = _commands(validation["unit_tests"], "validation.unit_tests")
    fixture = _fixture(validation["fixture_e2e"])
    diff_files = _paths(validation["diff_check_files"], "validation.diff_check_files")
    heavy = _object(validation["heavy"], "validation.heavy", {"authorized", "planned_work_units", "max_full_runs", "commands"})
    _required(heavy, {"authorized", "planned_work_units", "max_full_runs", "commands"}, "validation.heavy")
    authorized = _bool(heavy["authorized"], "validation.heavy.authorized")
    for key in ("planned_work_units", "max_full_runs"):
        if isinstance(heavy[key], bool) or not isinstance(heavy[key], int) or heavy[key] < 0:
            raise ContractError(f"validation.heavy.{key} must be a non-negative integer")
    heavy_commands = _commands(heavy["commands"], "validation.heavy.commands")
    if stage == "implementation" and (authorized or heavy["planned_work_units"] != 0 or heavy["max_full_runs"] != 0 or heavy_commands):
        raise ContractError("implementation cannot authorize heavy validation")
    if stage == "acceptance" and (not authorized or heavy["planned_work_units"] <= 0 or heavy["max_full_runs"] != 1 or len(heavy_commands) != 1):
        raise ContractError("acceptance requires exactly one authorized heavy run")
    if stage == "acceptance" and unit_tests:
        raise ContractError("acceptance uses the exact heavy command only")
    if stage == "acceptance" and edits:
        raise ContractError("acceptance cannot edit tracked files")
    commit = _object(task["commit"], "commit", {"enabled", "message", "push"})
    _required(commit, {"enabled", "message", "push"}, "commit")
    _bool(commit["enabled"], "commit.enabled")
    _string(commit["message"], "commit.message")
    _bool(commit["push"], "commit.push")
    if stage == "checkpoint" and not commit["push"]:
        raise ContractError("checkpoint requires commit.push=true")
    if stage != "checkpoint" and commit["push"]:
        raise ContractError("push is valid only for checkpoint stage")
    stop_codes = task["stop_codes"]
    if not isinstance(stop_codes, list) or any(not isinstance(item, str) or not item for item in stop_codes) or len(stop_codes) != len(set(stop_codes)):
        raise ContractError("stop_codes must be unique non-empty strings")
    report = _object(task["report"], "report", {"format", "outbox", "write_once"})
    _required(report, {"format", "outbox", "write_once"}, "report")
    if report["format"] != "json_v1" or report["outbox"] != OUTBOX or report["write_once"] is not True:
        raise ContractError("invalid report output contract")
    return canonical_sha(task)


def canonical_sha(task: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(task, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def canonical_diff_command(files: list[str]) -> str:
    return "git diff --check -- " + " ".join(files)


def render_prompt(task: dict[str, Any], task_path: str | Path, context: str) -> str:
    if context not in {"fresh", "delta"}:
        raise ContractError("context must be fresh or delta")
    sha = validate_task(task)
    rel = Path(task_path).resolve().relative_to(REPO_ROOT).as_posix()
    lines = ["AUTO_SEND", f"WORK_ID: {task['work_id']}", f"MODE: {task['mode']}", f"MANIFEST: {rel}", f"REVISION: {task['revision']}", f"TASK_SHA256: {sha}", f"CONTEXT: {context}"]
    lines.append("READ: AGENTS.md, START_HERE.md, and the manifest." if context == "fresh" else "READ: only the changed manifest and named files.")
    lines += ["VALIDATE: use the listed focused commands and the v1 contract.", "EXECUTE: only the bounded allowed task; preserve manual prompt routing.", "NO_EXPANSION: no runtime, production, mail, API, account, position, order, replay, CWT, or M6 work.", "REPORT: return json_v1 and write it once to the canonical outbox without read-back, retry, recreation, polling, loops, or watchers."]
    limit = 20 if context == "fresh" else 14
    if len(lines) > limit:
        raise ContractError("prompt line limit exceeded")
    return "\n".join(lines)


def _evidence(item: Any, name: str) -> dict[str, Any]:
    item = _object(item, name, {"command", "status", "evidence"})
    _required(item, {"command", "status", "evidence"}, name)
    _string(item["command"], f"{name}.command")
    if item["status"] not in {"pass", "fail", "not_run"}:
        raise ContractError(f"{name}.status invalid")
    _string(item["evidence"], f"{name}.evidence")
    return item


def validate_report(task: dict[str, Any], report: dict[str, Any]) -> None:
    task_sha = validate_task(task)
    keys = {"schema_version", "work_id", "task_revision", "task_sha256", "status", "branch", "base_commit", "changed_files", "requirements", "tests", "heavy_validation", "commit", "push", "notes"}
    report = _object(report, "report", keys)
    _required(report, keys, "report")
    if report["schema_version"] != "1.0" or report["work_id"] != task["work_id"] or report["task_revision"] != task["revision"] or report["task_sha256"] != task_sha:
        raise ContractError("report identity mismatch")
    if report["status"] not in {"done", "partial", "blocked", "failed"}:
        raise ContractError("report.status invalid")
    branch = _string(report["branch"], "report.branch")
    if branch != task["repo"]["expected_branch"]:
        raise ContractError("report branch mismatch")
    if not isinstance(report["base_commit"], str) or not HEX40.fullmatch(report["base_commit"]):
        raise ContractError("report.base_commit invalid")
    if task["repo"]["expected_base_commit"] is not None and report["base_commit"] != task["repo"]["expected_base_commit"]:
        raise ContractError("report base commit mismatch")
    changed = _paths(report["changed_files"], "report.changed_files")
    if not set(changed) <= set(task["allowed"]["edit"]):
        raise ContractError("report changed_files outside allowed.edit")
    reqs = _object(report["requirements"], "report.requirements", set(item["id"] for item in task["requirements"]))
    if set(reqs) != set(item["id"] for item in task["requirements"]):
        raise ContractError("report requirements mismatch")
    for key, value in reqs.items():
        value = _object(value, f"requirements.{key}", {"status", "evidence"})
        _required(value, {"status", "evidence"}, f"requirements.{key}")
        if value["status"] not in {"pass", "fail", "not_run"}:
            raise ContractError("requirement status invalid")
        _string(value["evidence"], "requirement evidence")

    expected_tests = list(task["validation"]["unit_tests"])
    if task["validation"]["diff_check_files"]:
        expected_tests.append(canonical_diff_command(task["validation"]["diff_check_files"]))
    tests = report["tests"]
    if not isinstance(tests, list):
        raise ContractError("report.tests must be an array")
    actual = [_evidence(item, f"tests[{i}]")["command"] for i, item in enumerate(tests)]
    if len(actual) != len(set(actual)) or not set(actual) <= set(expected_tests):
        raise ContractError("report tests contain an unlisted or duplicate command")
    if report["status"] == "done" and actual != expected_tests:
        raise ContractError("done report requires every development command once")
    if task["validation"]["fixture_e2e"]["required"] and report["status"] == "done" and not any(task["validation"]["fixture_e2e"]["location"] in item["command"] or task["validation"]["fixture_e2e"]["location"] in item["evidence"] for item in tests):
        raise ContractError("required fixture evidence missing")

    heavy = _object(report["heavy_validation"], "report.heavy_validation", {"authorized", "planned_work_units", "full_runs", "commands"})
    _required(heavy, {"authorized", "planned_work_units", "full_runs", "commands"}, "report.heavy_validation")
    manifest_heavy = task["validation"]["heavy"]
    if heavy["authorized"] != manifest_heavy["authorized"] or isinstance(heavy["planned_work_units"], bool) or not isinstance(heavy["planned_work_units"], int) or heavy["planned_work_units"] != manifest_heavy["planned_work_units"] or isinstance(heavy["full_runs"], bool) or not isinstance(heavy["full_runs"], int) or heavy["full_runs"] < 0 or heavy["full_runs"] > manifest_heavy["max_full_runs"]:
        raise ContractError("heavy evidence exceeds manifest")
    heavy_items = heavy["commands"]
    if not isinstance(heavy_items, list):
        raise ContractError("heavy commands must be an array")
    heavy_commands = manifest_heavy["commands"]
    actual_heavy = [_evidence(item, f"heavy[{i}")["command"] for i, item in enumerate(heavy_items)]
    if len(actual_heavy) != len(set(actual_heavy)) or not set(actual_heavy) <= set(heavy_commands):
        raise ContractError("heavy evidence command mismatch")
    executed_runs = sum(item["status"] in {"pass", "fail"} for item in heavy_items)
    if heavy["full_runs"] != executed_runs:
        raise ContractError("full_runs must equal executed heavy command evidence")
    if report["status"] == "done" and task["stage"] == "acceptance" and (heavy["full_runs"] != 1 or actual_heavy != heavy_commands or any(item["status"] != "pass" for item in heavy_items)):
        raise ContractError("done acceptance requires exact passing heavy command once")

    commit = report["commit"]
    if commit is not None:
        commit = _object(commit, "report.commit", {"hash", "message"})
        _required(commit, {"hash", "message"}, "report.commit")
        if not isinstance(commit["hash"], str) or not HEX40.fullmatch(commit["hash"]):
            raise ContractError("report commit hash invalid")
        _string(commit["message"], "report.commit.message")
        if not task["commit"]["enabled"]:
            raise ContractError("commit is disabled")
        if commit["message"] != task["commit"]["message"]:
            raise ContractError("report commit message mismatch")
    elif not task["commit"]["enabled"]:
        commit = None
    if report["status"] == "done":
        if any(value["status"] != "pass" for value in reqs.values()) or any(item["status"] != "pass" for item in tests):
            raise ContractError("done report requires passing evidence")
        if task["commit"]["enabled"] and (commit is None or commit["message"] != task["commit"]["message"]):
            raise ContractError("done report requires configured commit")
    push = report["push"]
    if push is not None:
        push = _object(push, "report.push", {"remote", "branch", "commit"})
        _required(push, {"remote", "branch", "commit"}, "report.push")
        _string(push["remote"], "report.push.remote")
        _string(push["branch"], "report.push.branch")
        if task["stage"] != "checkpoint" or not task["commit"]["push"] or commit is None or push["branch"] != branch or push["commit"] != commit["hash"] or not HEX40.fullmatch(push["commit"]):
            raise ContractError("unauthorized or mismatched push")
    elif task["commit"]["push"] and report["status"] == "done":
        raise ContractError("configured push is missing")
    if report["notes"] is not None:
        _string(report["notes"], "report.notes", nonempty=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai_task_contract")
    sub = parser.add_subparsers(dest="command", required=True)
    p_task = sub.add_parser("validate-task"); p_task.add_argument("--task", required=True)
    p_render = sub.add_parser("render-prompt"); p_render.add_argument("--task", required=True); p_render.add_argument("--context", choices=("fresh", "delta"), required=True)
    p_report = sub.add_parser("validate-report"); p_report.add_argument("--task", required=True); p_report.add_argument("--report", required=True)
    try:
        args = parser.parse_args(argv)
        task = load_json(args.task)
        if args.command == "validate-task":
            sha = validate_task(task)
            print(f"valid task {task['work_id']} {sha}")
        elif args.command == "render-prompt":
            print(render_prompt(task, args.task, args.context))
        else:
            report = load_json(args.report)
            validate_report(task, report)
            print(f"valid report {task['work_id']} {canonical_sha(task)}")
        return 0
    except (ContractError, OSError, TypeError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
