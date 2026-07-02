# NEXT_ACTION

- current_work_id: `BTCFX-20260702-VER04-V1-JUDGMENT-SELF-REVIEW-LINK`
- mode: `REVIEW_ONLY`

## Current goal

Deterministic report-only self-review link を使って、intraperiod outcomes から predicted position / TP accuracy を judge する。

## Product backlog next candidate

- `BTCFX-20260702-VER04-V1-POST-DEPLOYMENT-OBSERVATION`
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
- observation fields to capture: notification time, price at notification, displayed bias / active plan, early-warning card presence, MACD wording presence, actual 15m/30m/60m chart outcome, whether warning would have prevented a bad manual entry, and whether self-review should mark it as good / late / false alarm / missed.

## Resume rule

Next recommended task is `BTCFX-20260702-VER04-V1-POST-DEPLOYMENT-OBSERVATION`.

Live extra 15-minute sending remains later as `BTCFX-20260702-VER04-V1-INTRAPERIOD-LIVE-SEND-DECISION`, and only after explicit user approval.

Future Codex prompts should use task-specific minimal validation and must not include `git diff --name-only` unless changed-file list confirmation is needed.
