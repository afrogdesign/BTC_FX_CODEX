# NEXT_ACTION

- current_work_id: `BTCFX-20260702-VER04-V1-DETAIL-UI-READABILITY-PASS`
- mode: `BOUNDED_CODEX`

## Current goal

公開 detail page の人向けラベルと chart label 配置を見やすくし、notification sending behavior を変えずに Ver04-v1 の操作画面として読みやすくする。

Next normal generated HTML should confirm labels read naturally and chart labels do not overlap.

## Product backlog next candidate

- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`

## Completed history

- Ver04-v1 runtime deployment complete
- blocked version-label fix attempt requiring detail-page scope expansion
- notification version-label fix complete

## Hard boundary

- no runtime restart
- no launchd modification
- no real mail sending test
- no API / secrets / private / account / order endpoints
- no trading logic change
- no raw export commit

## Validation

- `pwd -P`
- `git status --short --branch`
- `git diff --check`
- `git diff --name-only`
- `git status --short --branch`

## Resume rule

After this fix, the next recommended task is `BTCFX-20260702-VER04-V1-POST-DEPLOYMENT-OBSERVATION`.
