# CLEANUP_CANDIDATES

監査用ファイルです。削除計画ではありません。

| Candidate | Current role | Risk | Recommended action | Reason | Next safe step |
|---|---|---|---|---|---|
| `docs/operations/deploy/Ver03-v2_*` | historical deploy docs | medium | review_later | historical deploy docs may still contain useful runtime context | keep reference only, no deletion |
| `chatgpt/analysis/*` | old analysis notes | low | keep_as_reference | old analysis notes, not current entrypoint | keep as reference |
| `chatgpt/specs/archive/*` | archived specs | low | keep_as_reference | already archived specs | keep as reference |
| `.venv312/` | local environment | low | never_auto_delete | local environment, avoid reading; deletion requires human/system-level decision | do not read by default |
| `logs/` | runtime logs | medium | never_auto_delete | runtime evidence may be useful; avoid reading by default | do not read by default |
| generated CSV/report/HTML outputs | generated outputs | medium | review_later | generated-heavy, but may be evidence | review later if evidence is needed |
| `docs/operations/ai-orchestration/legacy/*` | legacy prompts / docs | low | archive_later | already marked legacy | archive only if human asks |
| `docs/operations/ai-orchestration/TASK_LEDGER.md` | human work index | medium | keep_as_reference | large but still human work index | keep as reference, read only as needed |
| `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | active handoff anchor | high | review_later | active handoff anchor may contain stale paths but should not be casually rewritten | review only in handoff tasks |

## Notes

- old runtime execution repo is out of scope for cleanup classification
- do not delete or move anything in this task
- if a candidate is uncertain, keep it as `review_later`
