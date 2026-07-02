# NEXT_ACTION

- current_work_id: `BTCFX-20260702-VER04-V1-RUNTIME-PREFLIGHT-FIX-REVIEW`
- mode: `NORMAL_CODEX`

## Current goal

Runtime preflight の blocker を review し、明示的な source path/ref/commit を使う Ver04-v1 runtime reflection method を docs-only で確定する。

この task では runtime access は read-only の確認と分類のみを行い、pull / sync / branch switch / restart / launchd / notification sending / order execution は行わない。

## Completed history

- MEXC actual trade importer
- Actual trade to signal linker
- Biweekly ground truth report
- Post-eval recommendation engine
- Public HTML Post-Eval Recommendation Status section
- Surface alignment plan
- Dashboard Post-Eval Recommendation Status
- App-ready ready-gate contract validation
- Surface docs sync
- Mail surface plan
- Compact Post-Eval mail surface reflection
- End-to-end wiring plan
- Payload handoff contract
- Export wiring
- Post-Eval surface smoke
- Ver04-v1 runtime deployment plan
- Runtime preflight
- Runtime preflight fix

## Product objective reminder

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading is later-stage only.

## Required read

- `AGENTS.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/RESUME.md`
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- `docs/operations/ai-orchestration/VER04_V1_IMPLEMENTATION_READINESS_PACKAGE_20260702.md`
- `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
- `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`

## Narrow implementation scope

Inspect only as needed and summarize, do not dump large files.

- `docs/operations/ai-orchestration/VER04_V1_RUNTIME_DEPLOYMENT_PLAN_20260702.md`
- `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF_PLAN.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`

## Do not

- Do not call APIs.
- Do not read or print secrets.
- Do not restart runtime.
- Do not modify launchd state.
- Do not change notification sending behavior.
- Do not change mail body implementation.
- Do not fetch OHLCV or exchange data.
- Do not access private/account/order endpoints.
- Do not edit trading logic.
- Do not implement order execution or API integration.
- Do not commit raw exchange exports.
- Do not mix actual human trades into `paper_positions.csv`.
- Do not touch `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.

## Validation

- `pwd -P`
- `git status --short --branch`
- `git diff --check`
- `git diff --name-only`
- `git status --short --branch`

## Commit policy

- Commit docs/code only if validation passes.
- No push.

## Stop conditions

Stop with `BLOCKED BTCFX-20260702-VER04-V1-RUNTIME-PREFLIGHT-FIX-REVIEW: <one specific question>` if:

- current directory is not `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- runtime deployment plan is missing
- required source-of-truth docs are missing
- runtime target is not accessible read-only
- runtime branch/upstream is ambiguous or missing
- runtime worktree is dirty in a way that blocks reflection
- implementation would require API calls, secrets, runtime restart, notification sending changes, exchange fetch, private/account/order endpoints, trading logic changes, or old runtime repo access beyond this read-only preflight
- raw MEXC exports would need to be committed
- generated/log/raw private data would need to be committed
- validation fails

## Report

Compact report with:

- WORK_ID
- STATUS
- CHANGED
- SUMMARY
- NEXT_RECOMMENDED_TASK
- TESTS
- COMMIT
- PUSH
- NOTES

Also write the final compact report exactly once to:

```text
/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt
```

response.txt rules:

- Perform exactly one write operation.
- Do not check whether the file exists after writing.
- Do not read it back after writing.
- Do not watch or poll it.
- Do not retry the write.
- Do not recreate it.
- Do not use loops or file watchers.
- Immediate move or deletion by another process is expected and normal.
- A missing file after the write is not an error.

## Next recommended task

- `BTCFX-20260702-VER04-V1-RUNTIME-REFLECTION`
- Use the recorded explicit source path/ref/commit handoff method from the Ver04-v1 source repo; runtime upstream is not required for this method because the target worktree is now clean and the source ref is unambiguous.
