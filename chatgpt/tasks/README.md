# A1 task manifest and acceptance gate

The A1 v1 manifest is strict UTF-8 JSON with `schema_version: "1.0"`. Its canonical SHA-256 is calculated from parsed JSON with sorted keys, compact separators, UTF-8, and `ensure_ascii=false`. Every contract-ref object names a repo-relative `path` and explicit `clauses`; `allowed` contains `read`, `edit`, and bounded `inspect` values. Autonomy uses only the six parent-contract booleans.

Validation shape is `unit_tests`, `fixture_e2e`, `diff_check_files`, and `heavy`. Implementation is non-heavy; acceptance has no edit scope and one authorized full run. The commit shape is `{enabled, message, push}` and push is valid only for checkpoint stage. Reports align Work ID, revision, task SHA, branch, base commit, changed files, requirements, tests, heavy evidence, commit, and push. Partial, blocked, and failed reports may honestly carry a subset of evidence; `done` requires the applicable commands and evidence to pass.

Commands use only the Python standard library:

```text
./.venv312/bin/python tools/ai_task_contract.py validate-task --task <path>
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context fresh
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context delta
./.venv312/bin/python tools/ai_task_contract.py validate-report --task <path> --report <path>
```

The fixed outbox is `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`. The final JSON report is written exactly once: no read-back, existence check, retry, recreation, polling, loop, or watcher. Immediate move or deletion is normal, and the validator never writes the outbox.

The manual prompt route remains available until A3. A1 does not activate canonical startup routing and does not include CWT, worktree automation, replay/cache redesign, automatic execution or acceptance, M6, or product/runtime/mail/API/account/position/order work.
