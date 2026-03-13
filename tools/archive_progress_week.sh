#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-$BASE_DIR/運用資料/progress_weekly/2026-W11.md}"

python3 - "$TARGET" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
lines = text.splitlines()

header: list[str] = []
body_start = 0
for i, line in enumerate(lines):
    header.append(line)
    if line.startswith("- 日時: "):
        body_start = i
        break

entries: list[list[str]] = []
current: list[str] = []
for line in lines[body_start:]:
    if line.startswith("- 日時: ") and current:
        entries.append(current)
        current = [line]
    else:
        current.append(line)
if current:
    entries.append(current)

def compress_entry(block: list[str]) -> list[str]:
    out: list[str] = []
    for line in block:
        if line.startswith("- 変更ファイル:"):
            continue
        if line.startswith("- メモ:"):
            continue
        if line.startswith("- 実施内容:"):
            body = line.split(":", 1)[1].strip()
            body = re.sub(r"\s+", " ", body)
            body = re.sub(r"`([^`]+)`", r"\1", body)
            if len(body) > 180:
                body = body[:180].rstrip() + "…"
            out.append(f"- 実施内容: {body}")
            continue
        if line.startswith("- 未解決事項:"):
            body = line.split(":", 1)[1].strip()
            body = re.sub(r"\s+", " ", body)
            body = re.sub(r"`([^`]+)`", r"\1", body)
            if len(body) > 120:
                body = body[:120].rstrip() + "…"
            out.append(f"- 未解決事項: {body}")
            continue
        out.append(line)
    return out

kept = [compress_entry(block) for block in entries if any(line.startswith("- 実施内容:") for line in block)]

result = "\n".join(header[:body_start]).rstrip() + "\n\n"
result += "\n\n".join("\n".join(block).rstrip() for block in kept) + "\n"
path.write_text(result, encoding="utf-8")
print(f"archived:{path}")
print(f"entries:{len(kept)}")
PY
