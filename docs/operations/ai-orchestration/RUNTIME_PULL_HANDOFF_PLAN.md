# RUNTIME_PULL_HANDOFF_PLAN

## Purpose

old runtime execution repo への実 pull 前提を、実行なしで整理する plan-only 文書。
This file is kept as a prior/stale baseline for the earlier Ver03-v4 handoff path.

## Handoff source

- source repo is MCP-primary repo
- source path is `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- source branch is `Ver03-v4`
- checkpoint push was reported successful
- upstream was reported as `origin/Ver03-v4`
- dashboard parity is `dashboard_parity_complete`

## Handoff target

- target repo is old runtime execution repo
- target path is `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- target access is not executed in this task
- target inspection is not executed in this task
- target pull is not executed in this task

## Preconditions

- user explicitly authorizes runtime repo access for the execution task
- execution task confirms current directory is exactly `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- execution task checks current branch
- execution task checks remote and upstream
- execution task checks worktree is clean before pull
- execution task checks no generated/log/runtime files are unexpectedly dirty
- execution task confirms pull target is `origin/Ver03-v4` or stops if ambiguous
- execution task does not restart runtime
- execution task does not send notifications
- execution task does not perform trading actions
- execution task does not use private/account/order endpoints

## Planned pull task shape

1. verify target repo path
2. verify branch
3. verify remote/upstream
4. verify clean worktree
5. fetch or pull only from explicit target if authorized
6. verify post-pull status
7. run only explicitly listed read-only validations
8. report compactly

この skeleton は今は実行しない。

## Validation after pull

- `git status --short --branch`
- confirm branch/upstream after pull
- read-only doc/status checks if explicitly listed in the future task
- no runtime restart
- no app launch
- no notification sending
- no generated file commit unless explicitly authorized

## Explicitly not included

- no pull
- no push
- no old runtime repo access
- no runtime restart
- no app launch
- no notification sending
- no trading action
- no private/account/order endpoint work
- no source edit
- no generated file commit
- no profitability claim

## Stop conditions for execution task

- target path mismatch
- branch mismatch
- remote/upstream ambiguity
- dirty worktree
- unexpected generated/log/runtime changes
- pull requires merge/conflict resolution
- pull target is not `origin/Ver03-v4`
- runtime restart would be needed
- notification sending would be needed
- trading action would be needed
- private/account/order endpoint would be needed

## Next recommendation

- This is a prior baseline only.
- Use `docs/operations/ai-orchestration/VER04_V1_RUNTIME_DEPLOYMENT_PLAN_20260702.md` for the current Ver04-v1 deployment path.
- Do not infer that any pull or runtime action has been executed from this file.

## Out of scope

- runtime execution
- notification sending
- trading action
- automation design
- profitability judgment
