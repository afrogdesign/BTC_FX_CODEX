# NEXT_ACTION

- current_work_id: `BTCFX-20260703-VER04-V2-VALUE-DEFENSE-ENTRY-LAYER-DOC-SYNC`
- mode: `REVIEW_ONLY`

## Current goal

Ver04-v1 self-review / run-fingerprint checkpoint is complete. Source working branch has moved to Ver04-v2. VALUE-DEFENSE-ENTRY-LAYER Phase1-3 are complete; next posture is observation / review only.

## Product backlog next candidate

- `BTCFX-20260703-VER04-V2-VALUE-DEFENSE-ENTRY-LAYER-PHASE4` only after observation evidence exists and the human explicitly approves tuning review.
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
- judgment self-review explicit late label pass complete
- judgment self-review run metadata / fingerprint complete
- Ver04-v1 self-review / run-fingerprint checkpoint complete
- source working branch moved to Ver04-v2
- VALUE-DEFENSE-ENTRY-LAYER design doc created
- VALUE-DEFENSE-ENTRY-LAYER Phase1 complete
- VALUE-DEFENSE-ENTRY-LAYER Phase2 complete
- VALUE-DEFENSE-ENTRY-LAYER Phase3 complete

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

## Resume rule

Next recommended task is observation / review only:

- observe generated notifications / detail HTML / self-review rows
- do not tune scores or gates yet

`BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER` remains the later ground-truth candidate.
`BTCFX-20260703-VER04-V2-VALUE-DEFENSE-ENTRY-LAYER-PHASE4` stays gated behind observation evidence and explicit human approval.

Ver04-v2 is the new source working branch. Future Codex prompts should use task-specific minimal validation and must not include `git diff --name-only` unless changed-file list confirmation is needed.
