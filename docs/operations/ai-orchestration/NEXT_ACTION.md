# NEXT_ACTION

- current_work_id: `BTCFX-20260702-VER04-V1-INTRAPERIOD-MACD-BUILDOUT`
- mode: `REVIEW_ONLY`

## Current goal

Completed intraperiod MACD / early-warning buildout の state を観察し、次の generated HTML で `15分足 早期注意` と MACD 文言が自然に見えるか確認する。

Next normal generated HTML should confirm the early-warning card reads naturally and still keeps safety boundaries visible.

## Product backlog next candidate

- `BTCFX-20260702-VER04-V1-INTRAPERIOD-LIVE-SEND-DECISION` only if the user explicitly approves live extra notification sending behavior.
- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER` remains the candidate for actual-trade evaluation.

## Completed history

- Ver04-v1 runtime deployment complete
- blocked version-label fix attempt requiring detail-page scope expansion
- notification version-label fix complete
- breakout / inversion warning layer complete
- momentum confirmation layer complete
- intraperiod MACD buildout complete

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
- MACD support is now implemented in the report-only pipeline; live extra mail sending is still not enabled.

## Resume rule

After this buildout, the next recommended task is `BTCFX-20260702-VER04-V1-POST-DEPLOYMENT-OBSERVATION` unless the user explicitly approves live extra notification sending behavior.

Future Codex prompts should use task-specific minimal validation and must not include `git diff --name-only` unless changed-file list confirmation is needed.
