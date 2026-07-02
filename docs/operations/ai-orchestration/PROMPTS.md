# AI Orchestration Prompts

## Operation Modes

- `CHATGPT_ONLY`: ChatGPT が repo review、state整理、scope確定、design judgment を行う
- `REVIEW_ONLY`: bounded read-only review で事実確認だけを行う
- `LIGHT_CODEX`: 極小の local edit を行う
- `BOUNDED_CODEX`: 既定の implementation mode。固定スコープの source / test / docs work に使う
- `NORMAL_CODEX`: `BOUNDED_CODEX` より少し広い local implementation / validation が必要なときに使う
- `CHECKPOINT_PUSH`: push を伴う唯一の mode
- `RUNTIME_PULL_HANDOFF`: checkpoint から runtime pull handoff を扱う明示 task 専用
- `SYNC`: reviewed metadata を checkpoint 単位で同期するときだけ使う
- `HANDOFF`: thread migration、context overload、major milestone、明示 handoff で使う

通常 task では orchestration metadata を重くしない。`CONTROL.md`、`TASK_LEDGER.md`、`CURRENT_HANDOFF.md` は毎回更新しない。

## MCP Primary Operation

- default working dir: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- frozen old runtime execution repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- normal task では old runtime repo を edit / run / inspect しない
- AFROG_MCP を ChatGPT の primary repo inspection path とする
- normal task default は local edit + local validation + local commit + compact report
- push は `CHECKPOINT_PUSH` だけ
- compact report は Codex が local filesystem access を持つときだけ `response.txt` に 1 回だけ書く

## BOUNDED_CODEX

- `BOUNDED_CODEX` は default implementation mode
- ChatGPT が product / safety / scope を先に固定する
- Codex は次を範囲として local implementation を進めてよい:
  - allowed read files
  - allowed edit files
  - current diff / status
  - nearby helpers inside scoped files
  - matching tests by function / CLI / module name
- Codex は次の場合に止まる:
  - broad repo exploration が必要
  - product judgment が必要
  - safety judgment が必要
  - runtime repo / mail behavior / API / secrets / private endpoint / order execution 変更が必要

## Compact Prompt Skeleton

```text
AUTO_SEND

WORK_ID: <task_id>
MODEL_ASSUMPTION: gpt-5.4-mini medium
MODE: BOUNDED_CODEX | LIGHT_CODEX | NORMAL_CODEX | REVIEW_ONLY | ...

Repo:
- cd /Users/marupro/CODEX/100_MCP_Server/btc_monitor
- Expected active branch: Ver04-v1
- Do not touch /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor
- Do not push

Goal:
- <one short goal>

Allowed read:
- <files>

Allowed edit:
- <files or none>

Allowed inspection:
- current diff/status
- nearby helpers inside allowed files
- matching tests by function/CLI name

Do:
- <bounded actions only>

Validation:
- pwd -P
- git status --short --branch
- <targeted validation only if needed>
- git diff --check
- git diff --name-only
- git status --short --branch

Stop:
- wrong cwd/branch
- required file missing
- edit outside allowed files would be needed
- product/safety judgment would be needed
- broad repo exploration would be needed
- runtime/mail/API/order/private endpoint changes would be needed
- validation fails and fix is not obvious

Commit:
- Commit only if validation passes.
- Commit message: <message>
- No push.

Report:
- compact final report
- write the same compact report exactly once to response.txt when Codex has local filesystem access
```

## LIGHT_CODEX

```text
Use the compact skeleton.
Keep edit scope tiny.
Prefer docs-only or single-purpose local changes.
Targeted validation only.
Local commit optional.
No push.
```

## NORMAL_CODEX

```text
Use the compact skeleton.
Allow a slightly wider local implementation/validation scope than BOUNDED_CODEX.
Still stop before broad repo exploration, product judgment, runtime repo work, or push.
```

## REVIEW_ONLY

```text
REVIEW_ONLY <WORK_ID>
Goal: confirm <specific fact>
Allowed read: <files or commands>
Allowed edit: none
Allowed inspection: current diff/status if needed
Do: answer the fact only
Validation: none unless explicitly needed
Stop: if implementation or product judgment would be required
Commit: none
Report: answer only the fact, max 10 lines
```

## CHECKPOINT_PUSH

```text
CHECKPOINT_PUSH <WORK_ID>
Goal: prepare and publish a meaningful checkpoint branch/push
Read: `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md` plus scoped files
Stop: if branch, remote, push approval, or checkpoint target is ambiguous
Push only after local checks pass and explicit approval
Do not use this mode for normal tasks
```

## RUNTIME_PULL_HANDOFF

```text
RUNTIME_PULL_HANDOFF <WORK_ID>
Goal: define or execute checkpoint-to-runtime pull handoff
Read: `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md` plus scoped files
Stop: if pull target, runtime target, or human confirmation is ambiguous
Use only when explicitly requested
No runtime restart, no execution, no secret reading, no trading behavior changes
```

## SYNC

```text
SYNC <WORK_ID>
Update reviewed metadata only at checkpoints.
No source code changes.
Do not edit or run the old runtime execution repo.
Test: git diff --check
Report: compact
```

## HANDOFF

```text
HANDOFF <WORK_ID>
Update `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` only for active handoff conditions.
No source code changes.
Do not edit or run the old runtime execution repo.
Test: git diff --check
Report: compact
```

## Output Rule

- final compact report は Codex が local filesystem access を持つときだけ `response.txt` に書く
- filename は必ず `response.txt`
- 書き込みは 1 回だけ
- write 後に read/check/retry/watch/recreate しない

## Context Migration Rule

- context が overloaded、contradictory、unstable なら新しい thread を勧める
- ChatGPT は migration を勧めた時点で次の Codex prompt を出さない
- Codex は contradictory work IDs、stale metadata、scope confusion を見たら `BLOCKED`
- repo正本を chat history より優先する
