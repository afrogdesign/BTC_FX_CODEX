# CLEANUP_CANDIDATES

このファイルは audit 用です。削除 task ではありません。

| Candidate | Why it may be stale | Risk | Recommended action |
|---|---|---|---|
| `docs/operations/deploy/Ver03-v2_*` | Ver03-v2 era deploy/run review docs で、current MCP-primary orchestration の active entrypoint ではない | medium | review later |
| `chatgpt/analysis/*` | 旧 ChatGPT analysis notes。設計参考には使えるが active orchestration 正本ではない | low | keep |
| `chatgpt/specs/archive/*` | すでに archive 済み specs | low | keep |
| `.venv312/` | generated-heavy local environment で AI reading 対象ではない | low | never auto-delete |
| `logs/` | generated runtime logs で大きくなりやすい | medium | never auto-delete |
| generated CSV / report / HTML outputs | generated-heavy で current source-of-truth ではない | medium | review later |
| `chatgpt/README.md` and legacy ChatGPT prompts | 現在は reference material。repo-local orchestration entrypoint は `START_HERE.md` | low | keep |
| `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` old repo-path references | active handoff file なので今は直接 cleanup しない | high | review later |
| `docs/operations/ai-orchestration/TASK_LEDGER.md` full-history usage | full scan は高コストで current entrypoint ではない | medium | keep |

## Notes

- old runtime execution repo は cleanup candidate ではない。別用途の live execution side として残る
- delete はこの task の対象外
- generated files, logs, `.venv312/` は avoid-by-default として扱う
