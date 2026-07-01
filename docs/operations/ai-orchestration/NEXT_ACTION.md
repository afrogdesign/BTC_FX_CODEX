# NEXT_ACTION

- current_work_id: `BTCFX-20260702-DAILY-PROXY-EVALUATOR`
- mode: `NORMAL_CODEX`

## Current goal

既存 CSV / report 資産だけを使う deterministic な Daily Proxy Evaluator を実装する。

MEXC 生データの import はまだやらない。まずは既存の proxy 資産から report-only の daily summary を安定生成する。

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
- `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
- `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- `docs/operations/ai-orchestration/POST_EVAL_ASSET_HEALTH_AUDIT_20260702.md`

## Narrow implementation scope

Inspect only as needed and summarize, do not dump large files.

- `tools/log_feedback.py`
- `tests/test_log_feedback.py`
- any narrow support docs needed for the daily proxy output contract

## Do not

- Do not call APIs.
- Do not read or print secrets.
- Do not restart runtime.
- Do not modify launchd state.
- Do not change notification sending behavior.
- Do not fetch OHLCV or exchange data.
- Do not access private/account/order endpoints.
- Do not edit trading logic.
- Do not import MEXC raw exports yet.
- Do not commit raw exchange exports.
- Do not mix actual human trades into `paper_positions.csv`.
- Do not touch `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.

## Validation

- `pwd -P`
- `git status --short --branch`
- `git diff --check`
- targeted unit tests for the new report builder / CLI path
- `git diff --name-only`
- `git status --short --branch`

## Commit policy

- Commit docs/code only if validation passes.
- No push.

## Next recommended task

- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORT-SCHEMA`
- Goal: MEXC actual trade export の schema / import / normalization 設計を docs で固める。API integration はまだやらない。

## Stop conditions

Stop with `BLOCKED BTCFX-20260702-DAILY-PROXY-EVALUATOR: <one specific question>` if:

- current directory is not `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- required source-of-truth docs are missing
- implementation would require API calls, secrets, runtime restart, notification sending changes, exchange fetch, private/account/order endpoints, trading logic changes, or old runtime repo access
- raw MEXC exports would need to be committed
- generated/log/raw private data would need to be committed
- validation fails

## Report

Compact report with:

- WORK_ID
- STATUS
- CHANGED
- SUMMARY
- REUSE_ASSETS
- STALE_OR_RISKY_ASSETS
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
