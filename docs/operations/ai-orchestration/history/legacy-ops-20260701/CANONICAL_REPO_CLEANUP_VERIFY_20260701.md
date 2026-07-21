# CANONICAL_REPO_CLEANUP_VERIFY_20260701

## Purpose
`_archive/cleanup_20260701/` への cleanup archive の後で、canonical repo が安全に動作し、report-only surface も壊れていないことを確認した記録である。

## Canonical repo
- `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

## Cleanup archive accepted
- `docs/operations/ai-orchestration/legacy/chatgpt_AGENT_GITHUB_LEGACY.md`
- `docs/operations/deploy/Ver02_6_v2_MBP2020_FROZEN_RUNNER_20260609.md`
- `運用資料/参考資料/旧構想/`
- `運用資料/参考資料/SNS向け情報整理/`

## Archive contents verified
- `_archive/cleanup_20260701/docs/operations/ai-orchestration/legacy/chatgpt_AGENT_GITHUB_LEGACY.md`
- `_archive/cleanup_20260701/docs/operations/deploy/Ver02_6_v2_MBP2020_FROZEN_RUNNER_20260609.md`
- `_archive/cleanup_20260701/運用資料/参考資料/旧構想/`
- `_archive/cleanup_20260701/運用資料/参考資料/SNS向け情報整理/`

## Active entrypoints verified
- `AGENTS.md`
- `README.md`
- `main.py`
- `src/`
- `tools/`
- `tests/`
- `deploy/`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/RESUME.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/PROMPTS.md`

## Report-only smoke result
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json` は成功した
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json` は成功した
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface` も成功した

## Evidence/safety fields confirmed
- `evidence_quality_summary`
- `ohlcv_source_coverage_summary`
- `ohlcv_range_freshness_status`
- `candidate_max_after_ohlcv_end_hours`
- `report-only`
- `not FORMAL_GO`
- `no automatic order`
- `human decides manually`

## Deploy plist canonical path confirmation
- 4 本の repo-owned deploy plist は lint 成功
- `plutil -p` で `WorkingDirectory` / `ProgramArguments` / `StandardOutPath` / `StandardErrorPath` が canonical repo `\/Users/marupro/CODEX/100_MCP_Server/btc_monitor` を指すことを確認した
- `\/Users/marupro/CODEX/01_active/BTC_FX_CODEX` を指す active deploy plist は残っていない

## Remaining local/untracked files classification
- 3 つの pre-existing progress files は未追跡のまま残している
- それ以外の追加未追跡物はこの verify では新規に残していない

## Additional cleanup candidates
- なし

## Needs user decision
- なし

## Safety boundary
- no trading logic change
- no OHLCV fetch
- no private/account/order endpoint
- no runtime restart
- no frozen old runtime modification
- no progress HTML update

## Final recommendation
- cleanup archive は verify 済み
- ここで止めて `USER_DECISION_REQUIRED` に進むのが妥当である
