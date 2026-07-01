# NEXT_ACTION

- current_work_id: `BTCFX-20260702-POST-EVAL-ASSET-HEALTH-AUDIT`
- mode: `REVIEW_ONLY`

## Current goal

既存の事後評価資産を安全に棚卸しし、Ver04-v1 self-improvement loop の first implementation step を迷わず開始できる状態にする。

この task は evaluator 実装ではない。まず、既存資産・ログ・CSV・レポート・AI post review health を read-only / docs-only で整理し、何を再利用し、何を主系から外すかを明確にする。Ver04-v1 の first implementation task である。

## Product objective reminder

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading is out of scope.

## Required read

- `AGENTS.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/RESUME.md`
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`

## Narrow audit targets

Inspect only as needed and summarize, do not dump large files.

- `tools/run_ai_post_reviews.sh`
- `deploy/com.afrog.btc-ai-post-reviews.plist`
- `config.py` AI post review related keys only
- `logs/runtime/ai_post_reviews.out` summary only
- `logs/runtime/feedback_daily_sync.out` summary only if needed
- `logs/csv/user_reviews.csv` header/sample/schema only
- `logs/csv/signal_outcomes.csv` header/sample/schema only
- `logs/csv/active_plan_candidate_outcomes.csv` header/sample/schema only
- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv` header/sample/schema only
- latest `運用資料/reports/feedback_daily_sync_*.md` relevant AI health / improvement sections only

## Edit

Create:

```text
docs/operations/ai-orchestration/POST_EVAL_ASSET_HEALTH_AUDIT_20260702.md
```

Do not edit source code in this task.

## Required audit questions

1. What existing assets can feed the Daily Proxy Loop?
2. What existing assets can feed the Weekly Review Loop?
3. What existing assets can later support Biweekly Ground Truth Loop?
4. Which existing AI post review components are reusable as optional qualitative enrichment?
5. Which components are stale, old-purpose, old-path, stopped, or unsafe for the new main route?
6. What is the smallest next implementation task after the audit?
7. What files should Codex touch next, and what files should it avoid?

## Do not

- Do not call APIs.
- Do not read or print secrets.
- Do not restart runtime.
- Do not modify launchd state.
- Do not change notification sending behavior.
- Do not fetch OHLCV or exchange data.
- Do not access private/account/order endpoints.
- Do not edit trading logic.
- Do not edit source code.
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

- Commit docs-only audit if validation passes.
- No push.

## Stop conditions

Stop with `BLOCKED BTCFX-20260702-POST-EVAL-ASSET-HEALTH-AUDIT: <one specific question>` if:

- current directory is not `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- required source-of-truth docs are missing
- audit would require API calls, secrets, runtime restart, notification sending changes, exchange fetch, private/account/order endpoints, trading logic changes, or old runtime repo access
- generated/log/raw private data would need to be committed
- validation fails

## Report

Compact report with:

- WORK_ID
- STATUS
- CHANGED
- AUDIT_SUMMARY
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
