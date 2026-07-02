# NEXT_ACTION

- current_work_id: `BTCFX-20260702-VER04-V1-NOTIFICATION-VERSION-LABEL-FIX-DETAIL-PAGE`
- mode: `BOUNDED_CODEX`

## Current goal

Ver04-v1 の通知 subject/header 表示ラベルを修正し、notification sending behavior を変えずに Ver04-v1 表示へ揃える。

Next normal notification cycle should confirm subject/header labels show Ver04-v1.

## Product backlog next candidate

- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`

## Completed history

- Ver04-v1 runtime deployment complete
- blocked version-label fix attempt requiring detail-page scope expansion

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
