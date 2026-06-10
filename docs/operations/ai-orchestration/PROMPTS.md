# AI Orchestration Prompts

## NEXT

```text
NEXT <WORK_ID>
Goal: <one sentence>
Read: <files>
Edit: <files>
Test: <commands>
Stop: <conditions>
Report: compact
```

## FIX

```text
FIX <WORK_ID>
Issue: <specific issue>
Read: <files>
Edit: <files>
Test: <commands>
Stop: if the fix requires design changes outside this scope
Report: compact
```

## REVIEW_ONLY

```text
REVIEW_ONLY <WORK_ID>
Goal: confirm <specific fact>
Read: <files or commands>
Edit: none
Test: none
Report: answer only the fact, max 10 lines
```

## SYNC

```text
SYNC <WORK_ID>
Update only:
- AGENTS.md
- docs/operations/ai-orchestration/CONTROL.md
- docs/operations/ai-orchestration/TASK_LEDGER.md
- docs/operations/ai-orchestration/PROMPTS.md
- docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md
Reflect latest reviewed baseline, current objective, workflow rules, next task, and blockers.
`CONTROL.md` current_commit means the latest ChatGPT-reviewed baseline and may intentionally lag branch HEAD or the latest pushed commit.
A branch HEAD/current_commit mismatch is not by itself a BLOCK condition.
Codex should block only when the mismatch contradicts the specific task, the repo正本, or the requested edit scope.
Codex must still verify branch/head status with `git status` and report the actual commit after push.
Implementation tasks must not write their own final commit hash into CONTROL.md or TASK_LEDGER.md; use `pending_review` until ChatGPT review is complete and batch-update later in a SYNC task.
No source code changes.
Test: git diff --check
Report: compact
```

## HANDOFF

```text
HANDOFF <WORK_ID>
Create or update:
- docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md
Include repo, branch, current commit, objective, constraints, completed work, open questions, and next task.
No source code changes.
Test: git diff --check
Report: compact
```

## BLOCKED

```text
BLOCKED <WORK_ID>: <one specific question>
Evidence: <file/path or command>
Options:
- A: ...
- B: ...
Recommendation: <A/B if obvious>
```

## Output rule

- For every `NEXT`, `FIX`, `SYNC`, and `HANDOFF` task, the final compact report must also be written to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`.
- The filename must be exactly `response.txt`.
- Do not verify whether the file still exists after writing.
- For implementation tasks, report the actual commit hash in the final report, but leave the current task's CONTROL/TASK_LEDGER commit fields as `pending_review` unless ChatGPT explicitly supplied a prior reviewed hash to record.
- ChatGPT ACCEPT can accept `pending_review` metadata when the commit is verified on GitHub; later `SYNC` tasks can batch-update reviewed commit metadata.
- Temporary deploy/runtime-facing labels, report titles, and email subject prefixes for this branch should use `BTCFX Ver03-v2`.

## Context migration rule

- If ChatGPT judges that ChatGPT context or Codex context has become overloaded, unstable, contradictory, or likely to cause task confusion, ChatGPT must say so at the beginning of the reply.
- If ChatGPT recommends moving to a new ChatGPT thread or a new Codex thread, ChatGPT must not output the next Codex work prompt until the user gives the next instruction.
- When context migration is recommended, ChatGPT should first provide the reason for migration and wait for the user's direction.
- If Codex sees contradictory work IDs, repeated reports, mismatched commit hashes, stale next-task metadata, or evidence that the task context is confused, Codex must stop and report `BLOCKED` rather than guessing or continuing.
- Repo正本, especially `CONTROL.md`, `TASK_LEDGER.md`, `PROMPTS.md`, and `AGENTS.md`, takes priority over chat history.
- A `current_commit` lag alone is not contradictory context.
- The rule is universal and should apply before all future `NEXT` / `FIX` / `SYNC` / `HANDOFF` prompts.

## Execution rule note

- Use only the local iMac repo path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.
- Run file reads, edits, tests, git, commit, push, and deployment/runtime operations on this iMac local repository.
- Do not use `/Volumes/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.
- Do not use `/Volumes/marupro/claudeCode/BTC_FX_CODEX/btc_monitor`.
- Do not use `imac` or `imac.afrog.jp` as SSH targets.
- Do not use `ssh marupro@192.168.50.51` for normal repo work unless the task explicitly requires confirming the current machine state.
