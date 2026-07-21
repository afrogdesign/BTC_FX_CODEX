# A1 task manifest and acceptance gate

This directory contains the standalone v1 contract foundation. A manifest is strict UTF-8 JSON, versioned by `schema_version` and `revision`, and its canonical SHA-256 is calculated from sorted-key, compact UTF-8 JSON with `ensure_ascii=false`.

Use the standard-library CLI:

```text
./.venv312/bin/python tools/ai_task_contract.py validate-task --task <path>
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context fresh
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context delta
./.venv312/bin/python tools/ai_task_contract.py validate-report --task <path> --report <path>
```

Implementation manifests are bounded and non-heavy; acceptance manifests have no edit scope and exactly one authorized full run. Reports align work ID, revision, SHA, branch, base commit, changed files, requirements, commands, heavy evidence, commit, and push with the manifest. Unknown fields, unsafe paths/commands, duplicate JSON keys, non-finite numbers, and obvious sensitive material fail closed.

The canonical outbox is fixed. The final JSON report uses exactly one write operation: no read-back or existence check, retry or recreation, polling, loop, or watcher. Immediate move or deletion by another process is normal. The validator never writes the outbox.

This A1 route does not activate canonical startup routing: the manual prompt route remains available until A3. A1 also excludes CWT, worktree automation, replay/cache redesign, automatic execution or acceptance, M6, and product/runtime/mail/API/account/position/order work.
