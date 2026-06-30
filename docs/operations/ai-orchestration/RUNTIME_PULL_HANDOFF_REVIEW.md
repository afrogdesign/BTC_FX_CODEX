# RUNTIME_PULL_HANDOFF_REVIEW

## Purpose

checkpoint push 済みの状態で、old runtime execution repo に pull 計画へ進むべきかを review-only で判定する。

## Evidence reviewed

- `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md`
- `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md`
- `docs/operations/ai-orchestration/DASHBOARD_PARITY_SMOKE_TEST.md`
- `docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`
- `docs/operations/ai-orchestration/MILESTONES.md`
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`
- `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`
- `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`

## Current checkpoint status

- dashboard parity is `dashboard_parity_complete`
- dashboard parity issues found are `none`
- checkpoint push was reported successful on branch `Ver03-v4`
- upstream was reported as `origin/Ver03-v4`
- runtime repo reflection is not complete

## Runtime handoff decision

- `ready_for_runtime_pull_plan`

## Preconditions for actual pull

- actual pull must be a separate explicit task
- old runtime repo path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- branch/remote/upstream must be checked before pull
- worktree must be clean before pull
- no runtime restart in the pull task unless separately authorized
- no notification sending
- no trading action
- no private/account/order endpoints
- no generated file commit unless explicitly authorized
- post-pull validation must be read-only or explicitly listed

## Explicitly not executed

- no pull
- no push
- no old runtime repo access
- no runtime restart
- no app launch
- no notification sending
- no trading action
- no source edit
- no generated file commit

## Risks

- confusing MCP primary repo with old runtime repo
- pulling into dirty runtime worktree
- accidentally restarting runtime
- generated files changing during validation
- assuming dashboard parity means trading profitability
- moving to automation before evidence / win-rate diagnostics

## Next recommendation

- `BTCFX-20260630-RUNTIME-PULL-HANDOFF-PLAN`
- Goal: 実 pull の前に、old runtime execution repo の pull 手順と確認点を別 task で整える。

## Out of scope

- runtime execution
- notification sending
- trading action
- automation design
- profitability judgment
