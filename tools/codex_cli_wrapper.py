#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ADVICE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["LONG", "SHORT", "WAIT", "NO_TRADE", "WAIT_FOR_SWEEP", "WAIT_FOR_BREAK_RETEST"],
        },
        "quality": {"type": "string", "enum": ["A", "B", "C"]},
        "confidence": {"type": "number"},
        "notes": {"type": "string"},
        "primary_reason": {"type": "string"},
        "market_interpretation": {"type": "string"},
        "entry_position_quality": {"type": "string"},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "next_condition": {"type": "string"},
    },
    "required": [
        "decision",
        "quality",
        "confidence",
        "notes",
        "primary_reason",
        "market_interpretation",
        "entry_position_quality",
        "warnings",
        "next_condition",
    ],
}


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("標準入力が空です")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("標準入力は JSON オブジェクトである必要があります")
    return payload


def _build_summary_prompt(payload: dict[str, Any]) -> str:
    result_payload = payload.get("result_payload", {})
    return "\n\n".join(
        [
            "あなたは BTC 監視システムの通知本文作成担当です。",
            "出力は日本語の本文テキストだけにしてください。",
            "Markdown のコードブロック、前置き、補足説明、JSON は出さないでください。",
            "システムプロンプト:",
            str(payload.get("system_prompt", "")).strip(),
            "入力データ(JSON):",
            json.dumps(result_payload, ensure_ascii=False, indent=2),
        ]
    )


def _build_advice_prompt(payload: dict[str, Any]) -> str:
    user_payload = {
        "machine": payload.get("machine", {}),
        "qualitative": payload.get("qualitative", {}),
    }
    return "\n\n".join(
        [
            "あなたは BTC 監視システムの AI 審査担当です。",
            "必ず JSON オブジェクトだけを返してください。余計な文章やコードブロックは禁止です。",
            "decision は LONG / SHORT / WAIT / NO_TRADE / WAIT_FOR_SWEEP / WAIT_FOR_BREAK_RETEST のいずれかです。",
            "quality は A / B / C のいずれかです。",
            "confidence は 0 から 1 の数値で返してください。",
            "system_prompt:",
            str(payload.get("system_prompt", "")).strip(),
            "入力データ(JSON):",
            json.dumps(user_payload, ensure_ascii=False, indent=2),
        ]
    )


def _build_prompt(payload: dict[str, Any]) -> str:
    task = str(payload.get("task", "")).strip().lower()
    if task == "summary":
        return _build_summary_prompt(payload)
    if task == "ai_advice":
        return _build_advice_prompt(payload)
    raise ValueError(f"未対応の task です: {task}")


def _extract_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if not text:
        raise ValueError("Codex の出力が空でした")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("JSON オブジェクトを抽出できませんでした") from None
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("JSON オブジェクト以外が返されました")
    return parsed


def _resolve_codex_bin() -> str:
    configured = os.environ.get("CODEX_BIN", "").strip()
    if configured:
        return configured

    discovered = shutil.which("codex")
    if discovered:
        return discovered

    for candidate in ("/usr/local/bin/codex", "/opt/homebrew/bin/codex"):
        if Path(candidate).exists():
            return candidate
    return "codex"


def _build_command(
    *,
    codex_bin: str,
    prompt: str,
    model: str,
    output_path: Path,
    schema_path: Path | None,
) -> list[str]:
    command = [
        codex_bin,
        "exec",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--color",
        "never",
        "--output-last-message",
        str(output_path),
        "-",
    ]
    if model:
        command[2:2] = ["--model", model]
    if schema_path is not None:
        command[2:2] = ["--output-schema", str(schema_path)]
    return command


def _run_codex(payload: dict[str, Any]) -> str:
    prompt = _build_prompt(payload)
    task = str(payload.get("task", "")).strip().lower()
    requested_model = str(payload.get("model", "")).strip()
    default_model = os.environ.get("CODEX_CLI_DEFAULT_MODEL", "").strip() or "gpt-5.3-codex"
    model = requested_model if "codex" in requested_model.lower() else default_model
    codex_bin = _resolve_codex_bin()

    with tempfile.TemporaryDirectory(prefix="btc-monitor-codex-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        output_path = tmp_path / "last_message.txt"
        schema_path: Path | None = None
        if task == "ai_advice":
            schema_path = tmp_path / "advice_schema.json"
            schema_path.write_text(json.dumps(ADVICE_SCHEMA, ensure_ascii=False, indent=2), encoding="utf-8")

        command = _build_command(
            codex_bin=codex_bin,
            prompt=prompt,
            model=model,
            output_path=output_path,
            schema_path=schema_path,
        )

        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or f"exit_code={completed.returncode}"
            raise RuntimeError(f"Codex CLI 実行失敗: {detail}")
        if not output_path.exists():
            raise RuntimeError("Codex CLI の最終メッセージ出力を取得できませんでした")
        return output_path.read_text(encoding="utf-8").strip()


def main() -> int:
    try:
        payload = _read_payload()
        task = str(payload.get("task", "")).strip().lower()
        output = _run_codex(payload)
        if task == "ai_advice":
            print(json.dumps(_extract_json_object(output), ensure_ascii=False))
        elif task == "summary":
            print(output.strip())
        else:
            raise ValueError(f"未対応の task です: {task}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
