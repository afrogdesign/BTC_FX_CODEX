# CANONICAL_REPO_SWITCH_20260701

## Purpose
`/Users/marupro/CODEX/100_MCP_Server/btc_monitor` を今後の唯一の正本・実行元として固定し、`/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` を frozen old runtime として扱う切り替え記録である。

## User decision
- Canonical repo from now: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- Frozen old runtime repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- old repo はこの task では modify しない
- 旧repo source / tests / docs / scripts / config 本体は持ってこない
- 旧repo からは runtime-generated data / logs / reports / state のみを必要最小限 rescue する

## New canonical repo
- From this point onward, `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` is the canonical repo.
- future development, validation, and repo-owned entrypoints are rooted here.
- the frozen old runtime repo is not the current editing target.

## Frozen old runtime repo
- `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- do not run development from the frozen old runtime
- do not copy old runtime source/test/docs/scripts/config into the canonical repo
- future runtime refresh is user-managed by manual GitHub pull at clean checkpoints

## Old frozen repo recent-file audit
Read-only audit window: last 12 hours.

| Path | Classification | Action |
|---|---|---|
| `.DS_Store` files under top-level / `Branch_Command/` / `docs/` / `src/` / `tests/` / `tools/` / `運用資料/` | `ignore_cache_env_generated` | ignored |
| `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260701.md` | `rescue_runtime_generated` | copied locally only |
| `運用資料/reports/analysis/active_plan_candidate_outcomes_20260701.md` | `rescue_runtime_generated` | copied locally only |
| `運用資料/reports/feedback_daily_sync_20260701.md` | `rescue_runtime_generated` | copied locally only |
| `運用資料/参考資料/旧構想/BTC判定システム改善案_0317/00_readme.md` | `do_not_copy_source` | not copied |

No `needs_user_decision` file was encountered in the recent-file audit.

## Rescued runtime-generated files
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260701.md`
- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260701.md`
- `運用資料/reports/feedback_daily_sync_20260701.md`

These were copied from the frozen old runtime repo into the same relative location under the canonical repo and left as local generated files. They were not staged or committed.

## Files intentionally not copied
- old repo source files
- old repo tests
- old repo docs
- old repo tools
- old repo scripts
- old repo config
- progress HTML
- `CURRENT_PROGRESS.md`
- cache / `.DS_Store`

## Ambiguous files
- none

## Execution entrypoints checked
- `.env.example`
- `deploy/com.afrog.btc-monitor.plist`
- `deploy/com.afrog.btc-review-form.plist`
- `deploy/com.afrog.btc-ai-post-reviews.plist`
- `deploy/com.afrog.btc-feedback-daily-sync.plist`
- `docs/operations/ai-orchestration/INITIAL_PROMPT.md`
- `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
- `docs/operations/ai-orchestration/README.md`

## Active path references changed
- `.env.example`
- `deploy/com.afrog.btc-monitor.plist`
- `deploy/com.afrog.btc-review-form.plist`
- `deploy/com.afrog.btc-ai-post-reviews.plist`
- `deploy/com.afrog.btc-feedback-daily-sync.plist`
- `docs/operations/ai-orchestration/INITIAL_PROMPT.md`
- `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`

## Remaining old path references and why they are allowed
- historical docs and handoff docs that document the frozen old runtime state
- `docs/operations/ai-orchestration/REPO_MAP.md`
- `docs/operations/ai-orchestration/RESUME.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/PROMPTS.md`
- `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md`
- `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF_PLAN.md`
- `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF_REVIEW.md`
- `docs/operations/ai-orchestration/CANONICAL_REPO_SWITCH_20260701.md`
- older historical reports and logs under `運用資料/`

These references are allowed because they are explicitly historical, frozen-old-runtime references, or part of this new canonical switch record.

## Manual follow-up for user
- If the frozen old runtime is still installed as launchd / alias / shell entrypoints outside the repo, refresh those external launchers manually from the updated canonical paths when convenient.
- Do not use the frozen old runtime as a development target.
- Use manual GitHub pull at a clean checkpoint if/when runtime refresh is explicitly requested later.

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no runtime restart
- no trading logic change
- no OHLCV fetch
- no automatic execution added

## Validation commands
```bash
pwd -P
git status --short --branch
git diff --check
rg -n --hidden --glob '!.git/**' --glob '!.venv*/**' --glob '!local/**' --glob '!logs/**' --glob '!outbox/**' --glob '!archive/**' --glob '!運用資料/進捗/*.html' '/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor|/Users/marupro/CODEX/01_active/BTC_FX_CODEX' .
plutil -lint deploy/com.afrog.btc-monitor.plist
plutil -lint deploy/com.afrog.btc-review-form.plist
plutil -lint deploy/com.afrog.btc-ai-post-reviews.plist
plutil -lint deploy/com.afrog.btc-feedback-daily-sync.plist
git diff --name-only
git status --short --branch
git diff --cached --check
git diff --cached --name-only
git diff --cached --stat
```

## Next action
- `BTCFX-20260701-CANONICAL-RUNTIME-SMOKE-CHECK`
- Goal: run safe report-only smoke checks from the canonical repo and confirm active surfaces work without touching frozen old runtime or live execution.
