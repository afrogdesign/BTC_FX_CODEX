# NEXT_ACTION

- current_work_id: `BTCFX-20260706-FOLLOWUP-NOTIFICATION-DOCS-CLEANUP`
- mode: `REVIEW_ONLY`

## Current goal

Ver04-v2 is production-applied and the followup notification lifecycle is operational. The next posture is observation / review only. Phase4 tuning is still blocked until future notified observation evidence exists and the human explicitly approves it.
Next strategic review target is the Big Chance / Failed Thesis Layer. The guiding principle is: failed thesis is opportunity.

## Observation queue

- verify the next followup only fires after expiry or thesis weakening
- verify no repeated followup is sent for the same baseline signal
- verify `logs/last_followup_notified.json` is written after the first natural followup
- verify the subject and detail HTML render the followup section correctly
- verify notification frequency does not become noisy
- verify no scoring, gate, or threshold tuning occurred
- verify the next notified snapshot still includes the observation schema fields:
  - `self_review_readiness`
  - `attack_review_flags`
- if the next notified snapshot still lacks the observation schema, inspect the runtime hook / import path
- continue reviewing the latest snapshot plus HTML manually
- accumulate enough observations before any Phase4 tuning proposal
- run snapshot builder:
  `./.venv312/bin/python tools/build_value_defense_observation_snapshot.py --input logs/last_result.json --out-dir local/value_defense_observation --signal-id <signal_id>`
- dry-run check:
  `./.venv312/bin/python tools/build_value_defense_observation_snapshot.py --input logs/last_result.json --signal-id <signal_id> --dry-run --stdout-json`

## Design review queue

- review the Big Chance / Failed Thesis Layer design before any implementation
- keep the first implementation candidate local artifact / replay only
- do not add live notification behavior yet
- do not tune scoring, gates, or thresholds yet
- verify failed long to short / failed short to long symmetry
- verify HTF context comes first and 15m is activation / invalidation only
- keep Phase4 blocked until future observation evidence and explicit human approval

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
- VALUE-DEFENSE-ENTRY-LAYER runtime apply complete via local MCP source fallback after GitHub DNS/SSH reachability issue

## Hard boundary

- no runtime restart during normal product work
- no launchd modification
- no real mail sending test
- no API / secrets / private / account / order endpoints
- no trading logic change
- no raw export commit

## Later candidates

- `BTCFX-20260703-VER04-V2-VALUE-DEFENSE-ENTRY-LAYER-PHASE4` only after observation evidence exists and the human explicitly approves tuning review.
- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER` remains the candidate for actual-trade evaluation.
- live extra intraperiod sending decision remains explicit-approval-only.

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
Phase4 tuning remains blocked.

Ver04-v2 is the new source working branch. Future Codex prompts should use task-specific minimal validation and must not include `git diff --name-only` unless changed-file list confirmation is needed.

## High-priority human review note

- Preserve `docs/operations/ai-orchestration/VALUE_DEFENSE_TREND_TRANSITION_ATTACK_REVIEW_20260706.md` as a Phase4 review candidate.
- Key lesson: safety must not become passivity; BTC trend-transition setups need evidence-backed aggression.
- Review future notified observations for `trend_transition_candidate`, `breakout_extension_candidate`, `tp_too_conservative`, `short_invalidated_by_reclaim`, and `runner_should_have_been_considered`.
- Do not tune from this single example. Accumulate observations first, then review with explicit human approval.
