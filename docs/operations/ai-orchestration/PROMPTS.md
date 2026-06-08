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
- docs/operations/ai-orchestration/CONTROL.md
- docs/operations/ai-orchestration/TASK_LEDGER.md
Reflect latest commit, current objective, next task, and blockers.
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

## Execution rule note

- Use the MBAM4 SMB path only for direct file reading and editing.
- Run git, tests, commit, and push on the iMac via `ssh marupro@192.168.50.51` unless the task explicitly says otherwise.
- Do not run local git commands on the SMB-mounted repository path unless explicitly instructed.
- Do not switch to `/Volumes/marupro/claudeCode/BTC_FX_CODEX/btc_monitor`.
