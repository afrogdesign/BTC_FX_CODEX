# AGENTS.md

## Role

You are Codex acting as the implementation worker for this repository.

ChatGPT is the commander, planner, and reviewer.
Do not take over planning unless explicitly asked.

## Machine roles and paths

- Canonical working directory: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- All file reading and editing must use the local iMac repository path.
- All tests, git commands, commit, push, and deployment/runtime operations must run on this iMac local repository.
- Do not use `/Volumes/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.
- Do not use `/Volumes/marupro/claudeCode/BTC_FX_CODEX/btc_monitor`.
- Do not use `imac` or `imac.afrog.jp` as SSH targets.
- Do not use `ssh marupro@192.168.50.51` for normal repo work unless a task explicitly requires confirming the current machine state.
- Do not run runtime processes unless explicitly instructed.

## Cost policy

- Prefer narrow file reads over broad repository exploration.
- Do not summarize the whole repository unless explicitly requested.
- Do not repeat stable project context in reports.
- Use the shortest sufficient report format.
- If the task is unclear, stop and return `BLOCKED` with one specific question.

## Source of truth

Before doing non-trivial work, check:

- `docs/operations/ai-orchestration/RESUME.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/TASK_LEDGER.md` when updating task status

After starting in the repo root, read `docs/operations/ai-orchestration/RESUME.md` first as the low-cost fixed entrypoint, then rely on `CONTROL.md`, `PROMPTS.md`, and `CURRENT_HANDOFF.md` instead of chat history.

Use these files as the current operating context.
Do not rely only on chat history.

## Context migration and overload

- If the local orchestration context appears overloaded, unstable, contradictory, or likely to cause task confusion, stop and report `BLOCKED` rather than guessing or continuing.
- If contradictory work IDs, repeated reports, mismatched commit hashes, stale next-task metadata, or other confused context appears, trust the repo正本 first, especially `CONTROL.md`, `TASK_LEDGER.md`, `PROMPTS.md`, and `AGENTS.md`.
- This rule applies before future `NEXT` / `FIX` / `SYNC` / `HANDOFF` prompts.

## AI orchestration metadata

- `CONTROL.md` の `current_commit` は、最新の ChatGPT-reviewed baseline を意味する。
- `current_commit` は実際の branch HEAD より意図的に遅れることがある。
- branch HEAD と `current_commit` の不一致だけでは `BLOCKED` にはしない。
- `BLOCKED` にするのは、その不一致が個別 task、repo正本、または依頼された編集範囲と矛盾するときだけにする。
- `git status` で branch/head 状態を確認し、push 後は実際の commit を報告する。
- implementation task は、自分自身の最終 commit hash を `CONTROL.md` や `TASK_LEDGER.md` に書き込まない。
- 進行中の implementation task の `TASK_LEDGER.md` の `Commit` は `pending_review` を使う。
- `TASK_LEDGER.md` の `Push` は、push 後に `reported` を使ってよい。
- ChatGPT は Codex の報告後に GitHub を確認し、後続の `SYNC` task で reviewed metadata をまとめて更新する。
- `pending_review` を同じ task の commit hash で置き換えるだけの `FIX` task は作らない。
- `pending_review` は期待された中間状態であり、実際の誤記だけを `FIX` する。
- 一時的な deploy / runtime 向けラベル、report title、email subject prefix は `BTCFX Ver03-v2` を使う。
- Also write the final compact report to: `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` whenever Codex has local filesystem access, regardless of result or task type. Web-only で local filesystem に触れない ChatGPT thread はこの限りではない。

## Standard workflow

For each task:

1. Run `git status --short --branch`.
2. Read only the files named in the task, plus necessary nearby files.
3. Modify only the files required by the task.
4. Run the specified validation command first.
5. Run broader validation only when requested or clearly necessary.
6. Check `git diff --check` before commit.
7. Commit and push only when validation passes and the diff is intentional.
8. Return the compact report format.

## Stop conditions

Stop without commit/push if:

- tests fail and the fix is not obvious within the task scope
- secrets or credentials appear in the diff
- unrelated files changed
- the requested change conflicts with existing design
- more than 5 files need modification but the task did not authorize that
- a product/design decision is required
- runtime process restart is needed but not explicitly requested

Report as:

```text
BLOCKED <WORK_ID>: <one specific question>
Evidence: <file/path or command>
```

## Compact report format

```text
WORK_ID: <id>
STATUS: done | partial | blocked | failed
CHANGED:
- <file>
TESTS:
- <command> => pass | fail | not run (<reason>)
COMMIT: <hash or none>
PUSH: origin/<branch> | none
NOTES: <one line only if needed>
```

- Also write the final compact report to: `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` for every task type and outcome when Codex has local filesystem access, including resume checks and no-commit review work.
- The filename must be exactly `response.txt`.
- Do not verify whether the file still exists after writing.

## Project-specific prohibitions

- Do not add live order APIs.
- Do not access exchange API keys or secrets.
- Do not send real orders.
- Do not treat `ACTIVE_*` as `FORMAL_GO`.
- Do not mix Active Plan candidates into `paper_positions.csv` unless explicitly requested.
