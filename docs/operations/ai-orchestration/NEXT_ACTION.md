# NEXT_ACTION

- current_work_id: `BTCFX-20260703-VER04-V1-POST-DEPLOYMENT-OBSERVATION`
- mode: `REVIEW_ONLY`

## Current goal

self-review stability buildout は反映済みで、controlled restart も完了。次の normal notification から observation / review を再開する。

## Product backlog next candidate

- `BTCFX-20260703-VER04-V1-POST-DEPLOYMENT-OBSERVATION`
- `BTCFX-20260702-VER04-V1-INTRAPERIOD-LIVE-SEND-DECISION` only if the user explicitly approves live extra notification sending behavior.
- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER` remains the candidate for actual-trade evaluation.

## Completed history

- Ver04-v1 runtime deployment complete
- blocked version-label fix attempt requiring detail-page scope expansion
- notification version-label fix complete
- breakout / inversion warning layer complete
- momentum confirmation layer complete
- intraperiod MACD buildout complete
- required post-deployment observation gate for intraperiod / MACD buildout
- judgment self-review link complete
- controlled runtime restart for stale-process issue complete
- human UI subject / chart cleanup complete
- judgment self-review stability buildout complete
- judgment self-review queue surface complete
- judgment self-review rollup digest complete
- judgment self-review change-readiness gate complete

## Hard boundary

- no runtime restart during normal product work
- no launchd modification
- no real mail sending test
- no API / secrets / private / account / order endpoints
- no trading logic change
- no raw export commit

## Validation

- task-specific minimal validation only
- docs-only: `git diff --check`
- source/test: changed-file compile/test only
- next normal notification should confirm the simplified subject, current-price label, internal diagnostics demotion, and self-review evidence alignment in the live process.

## Resume rule

Next recommended task is `BTCFX-20260702-VER04-V1-POST-DEPLOYMENT-OBSERVATION`.

Live extra 15-minute sending remains later as `BTCFX-20260702-VER04-V1-INTRAPERIOD-LIVE-SEND-DECISION`, and only after explicit user approval.

Future Codex prompts should use task-specific minimal validation and must not include `git diff --name-only` unless changed-file list confirmation is needed.
