# AI Orchestration Prompts

## Operation Modes

- `CHATGPT_ONLY`: use when ChatGPT should handle repo review, scope selection, or design judgment without spending Codex credits.
- `LIGHT_CODEX`: use when the scope is fixed and only a small local edit is needed; local commit optional, no push by default.
- `NORMAL_CODEX`: use for fixed-scope edit/test work; local commit if checks pass, no push unless explicit checkpoint.
- `CHECKPOINT_PUSH`: the only mode that pushes.
- `SYNC`: use only at checkpoints to batch-update reviewed metadata; do not run after every task.
- `HANDOFF`: use at thread migration, context overload, major milestone, or explicit handoff; do not update `CURRENT_HANDOFF.md` for every task.
- Keep orchestration metadata lightweight: normal tasks should not update `CONTROL.md`, `TASK_LEDGER.md`, or `CURRENT_HANDOFF.md`.
- `CONTROL.md` should describe the current state, current objective, safety boundary, validation rules, and next action; it should not become a full task history.
- `TASK_LEDGER.md` is a human-facing work index, not the source of truth for commit history; git/GitHub and compact reports remain the commit evidence.
- `CURRENT_HANDOFF.md` should be updated only for active handoff conditions such as partial, blocked, thread migration, context overload, major milestone, or explicit handoff.
- Keep the logical separation intact without physically splitting the repo: orchestration operations stay under `docs/operations/ai-orchestration/`, while project source stays under `src/`, `tools/`, `tests/`, `scripts/`, and related runtime directories.

## MCP_PRIMARY_OPERATION

- default working dir: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- do not edit the old runtime execution repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- do not run runtime execution during normal orchestration tasks
- use AFROG_MCP as the primary repo inspection path
- use GitHub for checkpoint/history/sync, not as the default read path for every review
- normal task default is local edit + local validation + local commit + compact report
- do not automatically push to GitHub unless `CHECKPOINT_PUSH` is explicitly requested or clearly authorized
- compact report is still written to `response.txt` exactly once
- browser-side `AUTO_SEND` / `HUMAN_CHECK` concepts stay unchanged by these prompt rules

## Ver03-v4 Integrated Surface Guard

- For future `NEXT` / `FIX` prompts, check whether the task affects the public HTML report, notification mail, or local dashboard / app surface.
- Keep those three surfaces aligned to one source of truth; do not create a separate decision path for any one of them.
- If a task changes trading meaning, safety wording, or actionability, verify the impact on all three surfaces together.
- Prefer the authoritative roadmap at `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` when product direction needs to be explained.

## LOW_COST_RESUME

```text
RESUME <WORK_ID>
Goal: restart from the repo-local baseline with minimal reading.
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
Read: AGENTS.md, docs/operations/ai-orchestration/START_HERE.md, docs/operations/ai-orchestration/RESUME.md, docs/operations/ai-orchestration/CURRENT_STATE.md, docs/operations/ai-orchestration/NEXT_ACTION.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/PROMPTS.md, docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md
Inspect: docs/operations/ai-orchestration/TASK_LEDGER.md only as needed, preferably the latest rows
Report: READY | BLOCKED | NEEDS_REVIEW
Stop: if repo正本 and chat history conflict, or if the scope is not fixed yet
Do not start implementation until the user explicitly asks.
Do not edit or run the old runtime execution repo.
```

## NEXT

```text
NEXT <WORK_ID>
Goal: <one sentence>
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
Read: <files>
Edit: <files>
Test: <commands>
Stop: <conditions>
Report: compact
Do not edit or run the old runtime execution repo.
Local commit is optional.
Do not push by default.
```

## FIX

```text
FIX <WORK_ID>
Issue: <specific issue>
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
Read: <files>
Edit: <files>
Test: <commands>
Stop: if the fix requires design changes outside this scope
Report: compact
Do not edit or run the old runtime execution repo.
Commit locally if checks pass.
Do not push unless explicit `CHECKPOINT_PUSH`.
```

## CHECKPOINT_PUSH

```text
CHECKPOINT_PUSH <WORK_ID>
Goal: prepare and publish a meaningful checkpoint branch/push.
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
Read: docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md, <files>
Edit: <files>
Test: <commands>
Stop: if branch/remote target is ambiguous or push is not explicitly approved
Report: compact
Do not edit or run the old runtime execution repo.
Push only after local checks pass and checkpoint target is explicit.
```

## RUNTIME_PULL_HANDOFF

```text
RUNTIME_PULL_HANDOFF <WORK_ID>
Goal: define or execute the handoff from checkpoint push to old runtime repo pull.
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
Read: docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md, <files>
Edit: <files>
Test: <commands>
Stop: if the handoff target is ambiguous or human confirmation is missing
Report: compact
Use only when explicitly requested.
Old runtime execution repo may be involved only in that task.
No runtime restart.
No execution.
No secret reading.
No trading behavior changes.
Do not edit or run the old runtime execution repo by default.
```

## REVIEW_ONLY

```text
REVIEW_ONLY <WORK_ID>
Goal: confirm <specific fact>
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
Read: <files or commands>
Edit: none
Test: none
Report: answer only the fact, max 10 lines
Do not edit or run the old runtime execution repo.
```

## SYNC

```text
SYNC <WORK_ID>
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
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
Do not edit or run the old runtime execution repo.
Test: git diff --check
Report: compact
```

## HANDOFF

```text
HANDOFF <WORK_ID>
Working dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
Create or update:
- docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md
Include repo, branch, current commit, objective, constraints, completed work, open questions, and next task.
Update `CURRENT_HANDOFF.md` only at thread migration, context overload, major milestone, or explicit handoff; do not update it for every task.
No source code changes.
Do not edit or run the old runtime execution repo.
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

- The final compact report must be written to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` whenever Codex has local filesystem access.
- This applies to every Codex task type and outcome, including `NEXT`, `FIX`, `SYNC`, `HANDOFF`, `REVIEW_ONLY`, `BLOCKED`, `READY`, `NEEDS_REVIEW`, resume checks, branch checks, metadata checks, docs-only work, no-commit review work, `done`, `partial`, `failed`, and `not run`.
- If the thread is ChatGPT-only and does not have local filesystem access, this file write is not required.

```text
Report: compact

Also write the final compact report to:
/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt
```

- The filename must be exactly `response.txt`.
- Do not verify whether the file still exists after writing.
- For implementation tasks, report the actual commit hash in the final report, but leave the current task's CONTROL/TASK_LEDGER commit fields as `pending_review` unless ChatGPT explicitly supplied a prior reviewed hash to record.
- ChatGPT ACCEPT can accept `pending_review` metadata when the commit is verified on GitHub; later `SYNC` tasks can batch-update reviewed commit metadata.
- Temporary deploy/runtime-facing labels, report titles, and email subject prefixes for this branch should use `BTCFX Ver03-v4` unless superseded by a newer reviewed roadmap.

## Context migration rule

- If ChatGPT judges that ChatGPT context or Codex context has become overloaded, unstable, contradictory, or likely to cause task confusion, ChatGPT must say so at the beginning of the reply.
- If ChatGPT recommends moving to a new ChatGPT thread or a new Codex thread, ChatGPT must not output the next Codex work prompt until the user gives the next instruction.
- When context migration is recommended, ChatGPT should first provide the reason for migration and wait for the user's direction.
- If Codex sees contradictory work IDs, repeated reports, mismatched commit hashes, stale next-task metadata, or evidence that the task context is confused, Codex must stop and report `BLOCKED` rather than guessing or continuing.
- Repo正本, especially `START_HERE.md`, `CONTROL.md`, `TASK_LEDGER.md`, `PROMPTS.md`, and `AGENTS.md`, takes priority over chat history.
- A `current_commit` lag alone is not contradictory context.
- The rule is universal and should apply before all future `NEXT` / `FIX` / `SYNC` / `HANDOFF` prompts.
