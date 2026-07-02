# NEXT_ACTION

- current_work_id: `BTCFX-20260702-VER04-V1-MOMENTUM-CONFIRMATION-LAYER`
- mode: `BOUNDED_CODEX`

## Current goal

Breakout / inversion zones の report-only momentum confirmation layer を整え、notification sending behavior を変えずに public detail page の counter-bias 可視性を上げる。

Next normal generated HTML should confirm the momentum card reads naturally and still keeps safety boundaries visible.

## Product backlog next candidate

- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`
- `BTCFX-20260702-VER04-V1-INTRAPERIOD-BREAKOUT-ALERT-DESIGN`

## Completed history

- Ver04-v1 runtime deployment complete
- blocked version-label fix attempt requiring detail-page scope expansion
- notification version-label fix complete
- breakout / inversion warning layer complete

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
- MACD is not in the current pipeline; separate scoped task if the user wants MACD work.

## Resume rule

After this momentum pass, the next recommended task is `BTCFX-20260702-VER04-V1-INTRAPERIOD-BREAKOUT-ALERT-DESIGN`.

Future Codex prompts should use task-specific minimal validation and must not include `git diff --name-only` unless changed-file list confirmation is needed.
