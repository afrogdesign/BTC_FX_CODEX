# NEXT_ACTION

- current_work_id: `BTCFX-20260702-VER04-V1-POST-DEPLOYMENT-OBSERVATION`
- mode: `REVIEW_ONLY`

## Current goal

Ver04-v1 runtime deployment reflected active の観測を続け、notification sending behavior を変えずに post-deployment observation を続ける。

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

- task-specific minimal validation only
- docs-only: `git diff --check`
- source/test: changed-file compile/test only

## Resume rule

After this observation, the next recommended task is `BTCFX-20260702-VER04-V1-POST-DEPLOYMENT-OBSERVATION`.

Future Codex prompts should use task-specific minimal validation and must not include `git diff --name-only` unless changed-file list confirmation is needed.
