# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-IMPLEMENT`
- mode: `BOUNDED CODEX IMPLEMENTATION`
- task_type: `DOCS-ONLY / VALIDATE / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-FIX-2`
- previous_status: `P6 SPEC CHECKPOINT COMMITTED / PUSH NONE`

## Goal

P6 active specに従うhistorical replay実装を開始する。

## Source of truth

`chatgpt/specs/active/20260710_manual_operator_historical_replay.md`

実装契約はactive specを参照し、ここへ重複記載しない。

## Known state

- P5 classifier source/test契約はChatGPTがAFROG_MCPでreview済み。
- reported targeted validation: 123 tests pass / task diff check pass。
- P5 specはarchive済み。
- P6 active specは作成済み。
- P6 source implementationはまだ開始しない。

Archived P5 spec:

```text
chatgpt/specs/archive/20260710_manual_operator_classifier_offline.md
```

Active P6 spec:

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

## Allowed read

```text
AGENTS.md
docs/operations/ai-orchestration/START_HERE.md
docs/operations/ai-orchestration/CURRENT_STATE.md
docs/operations/ai-orchestration/NEXT_ACTION.md
chatgpt/specs/archive/20260710_manual_operator_classifier_offline.md
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

## Allowed edit

```text
docs/operations/ai-orchestration/CURRENT_STATE.md
docs/operations/ai-orchestration/NEXT_ACTION.md
chatgpt/specs/archive/20260710_manual_operator_classifier_offline.md
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Only correct an objective docs inconsistency. Do not redesign P6.

## Do

1. Confirm branch `Ver04-v2` and inspect only allowed files.
2. Confirm exactly one active phase spec exists and it is P6.
3. Add a compact P5 completion / P6 activation section to `CURRENT_STATE.md` if not already present.
4. After validation, transition `NEXT_ACTION.md` to:

```text
current_work_id: BTCFX-20260710-MTP-HISTORICAL-REPLAY-IMPLEMENT
mode: BOUNDED CODEX IMPLEMENTATION
previous_status: P6 SPEC CHECKPOINT COMMITTED / PUSH NONE
```

Reference the active P6 spec as the implementation source of truth. Do not duplicate its general contract.

## Validation

```bash
git diff --check -- \
  docs/operations/ai-orchestration/CURRENT_STATE.md \
  docs/operations/ai-orchestration/NEXT_ACTION.md \
  chatgpt/specs/archive/20260710_manual_operator_classifier_offline.md \
  chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Do not run Python tests for this docs-only task.

## Stop

- branch is not `Ver04-v2`
- P5 archive or P6 active spec is missing
- more than one non-placeholder active spec exists
- P6 requires product judgment or source changes
- unrelated changes overlap allowed files and cannot be safely integrated
- do not touch production, notification, runtime, API, order, secret, generated, raw-export, or frozen-runtime content
- do not reset, checkout, delete, or use stash apply/pop/drop

## Commit / Push

- commit: `docs: activate historical replay phase`
- stage only task files
- push: none

## Report

```text
WORK_ID: BTCFX-20260710-MTP-HISTORICAL-REPLAY-SPEC-CHECKPOINT
STATUS: done | partial | blocked | failed
BRANCH: Ver04-v2
CHANGED:
- <file or none>
TESTS:
- task-file git diff --check => pass | fail
COMMIT: <hash or none>
PUSH: none
IMPLEMENTED:
- P5 archived
- P6 active spec checkpointed
- state and next action aligned
REMAINING: none | <item>
NOTES: <必要な場合のみ>
```

Write the same compact report exactly once to:

`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`

Do not read, check, retry, recreate, watch, or poll it after writing.
