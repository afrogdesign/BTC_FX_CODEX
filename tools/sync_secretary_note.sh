#!/bin/zsh

set -eu

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NEXT_TASK="${BTC_MONITOR_NEXT_TASK_PATH:-$BASE_DIR/運用資料/NEXT_TASK.md}"
SECRETARY_PATH="${BTC_MONITOR_SECRETARY_PATH:-/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_デジタルスキル/00_PROJECT/FX/トレード支援システム/👩‍⚖️秘書.md}"
QUEUE_PATH="${BTC_MONITOR_SECRETARY_QUEUE_PATH:-$BASE_DIR/運用資料/運用/秘書メモ更新待ち.md}"

python3 - "$NEXT_TASK" "$SECRETARY_PATH" "$QUEUE_PATH" <<'PY'
from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path

next_task = Path(sys.argv[1])
secretary = Path(sys.argv[2])
queue = Path(sys.argv[3])

jst = dt.timezone(dt.timedelta(hours=9), name="JST")
now = dt.datetime.now(jst)
updated = now.strftime("%Y-%m-%d %H:%M JST")
created = now.strftime("%Y-%m-%d")

if secretary.exists():
    text = secretary.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^created:\s*(.+)$", text, flags=re.MULTILINE)
    if m:
        created = m.group(1).strip()

src = next_task.read_text(encoding="utf-8", errors="ignore")

def extract_bullets(section: str, limit: int) -> list[str]:
    lines = src.splitlines()
    out: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            in_section = line.strip() == f"## {section}"
            continue
        if not in_section:
            continue
        if line.startswith("## "):
            break
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
        else:
            m_num = re.match(r"^\d+\.\s+(.*)$", s)
            if m_num:
                out.append(m_num.group(1).strip())
        if len(out) >= limit:
            break
    return out

current = extract_bullets("現在の状況", 4)
tasks = extract_bullets("次のタスク", 3)
blockers = extract_bullets("ブロッカー", 2)

if not current:
    current = ["NEXT_TASK の現在状況を参照してください。"]
if not tasks:
    tasks = ["NEXT_TASK の次タスクを参照してください。"]

content = [
    "---",
    "tags:",
    "  - BTC",
    "  - FX",
    "  - CODEX",
    "  - 秘書",
    f"created: {created}",
    f"updated: {updated}",
    "---",
    "",
    "## 今の状況",
    "",
]
content += [f"- {x}" for x in current]
content += [
    "",
    "## 次にやる",
    "",
]
content += [f"- {x}" for x in tasks]
content += [
    "",
    "## 次に見る",
    "",
    f"- [NEXT_TASK.md]({next_task})",
    f"- [progress.md]({next_task.parent / 'progress.md'})",
    f"- [cli_api定期比較レポート.md]({next_task.parent / 'reports' / 'cli_api定期比較レポート.md'})",
]

if blockers:
    content += ["", "## 重要メモ", ""]
    content += [f"- 未解決: {x}" for x in blockers]

body = "\n".join(content) + "\n"

def can_write(path: Path) -> bool:
    try:
        parent = path.parent
        if not parent.exists():
            return False
        if path.exists():
            return os.access(path, os.W_OK)
        return os.access(parent, os.W_OK)
    except Exception:
        return False

if can_write(secretary):
    secretary.write_text(body, encoding="utf-8")
    print(f"secretary_synced:{secretary}")
else:
    queue.parent.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y-%m-%d %H:%M JST")
    with queue.open("a", encoding="utf-8") as f:
        f.write(f"\n## {stamp}\n")
        f.write(f"- 理由: 秘書メモ書き込み不可 ({secretary})\n")
        f.write("- 退避内容:\n")
        f.write("```markdown\n")
        f.write(body)
        f.write("```\n")
    print(f"secretary_queued:{queue}")
PY
