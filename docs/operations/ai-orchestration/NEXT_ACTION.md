# NEXT_ACTION

- current_work_id: `BTCFX-20260721-M5-EVIDENCE-REFRESH-TRIGGER`
- mode: `WAIT_FOR_EVIDENCE`
- branch: `Ver04-v3` documentation line; confirm from local git before the next Codex task
- active_spec: none
- status: waiting for a gate-relevant input change
- push: none

## Current action

Do not rerun or rewrite the accepted M5 proposal engine now.

Wait until at least one M5 refresh trigger becomes true:

1. at least seven new eligible JST dates exist after the accepted 2026-07-21 M5 cutoff;
2. the P-route actual episode/link pair becomes available and changes P8 actual evidence status;
3. an accepted M1 or M3 source change materially changes the comparison basis;
4. the user explicitly requests an earlier bounded refresh.

The seven-date rule is a replay-cost scheduling rule, not a proposal-eligibility threshold.

## Next task when triggered

Create one active M5 refresh spec and run one bounded operations task:

- use the accepted champion manifest unchanged
- use the accepted four-challenger proposal space unchanged
- use fresh explicit M1/M3 inputs
- include P8 evidence only when the accepted actual episode/link route has produced it
- execute `run-macro-p9-proposal-engine` exactly once
- produce exactly four fresh local outputs
- do not commit generated artifacts or private inputs
- return to ChatGPT before any M6 task

## Decision after refresh

- no eligible challenger: record `continue_shadow_collection` and park again
- material engine defect: create one bounded M5 FIX spec
- exactly one proposal-eligible challenger: create one M6 proposal package and request explicit human approval
- multiple eligible challengers: do not combine them; select one through ChatGPT/human judgment

## P-route handoff

P1–P8 and the actual-evidence readiness review are accepted. P9 remains blocked by the absent complete private MEXC Trade History / Order History / Position History batch.

Do not repeat the accepted P importer/linker/readiness review unless a reopening trigger in `CURRENT_STATE.md` or `DEC-20260721-012` is true.

## M6 boundary

M6 is not authorized by this `NEXT_ACTION`.

M6 requires:

- one proposal-eligible M5 challenger
- one bounded proposal
- explicit human approval
- source-only shadow before any runtime apply
- separate validation and adoption decisions

Canonical plan:

- `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md`

## Safety

- report-only
- no automatic order
- no automatic production mutation
- no raw exchange export or generated actual CSV commit
- no gate, threshold, scoring, classifier, notification, mail, runtime, schedule, API, account, position, or order change
- no frozen runtime repo access without an explicit `RUNTIME_TASK`
