# NEXT_ACTION

- current_work_id: `BTCFX-20260712-P8-TURNING-PRECURSOR-DAILY-SHADOW`
- mode: `BOUNDED_CODEX`
- task_type: `P8 REPORT-ONLY DAILY SHADOW INTEGRATION`
- previous_work_id: `BTCFX-20260712-P8-TURNING-PRECURSOR-REPLAY-CORRECTION`
- previous_status: `DONE / ACCEPTED / ARCHIVED`

## Current state

The corrected turning / volatility precursor replay is implemented and accepted at commit `9f4f6a1`.

Corrected evidence:

- signal rows: 2,872
- independent realized-move opportunities: 28
- current notification recall: 0.392857
- Combined precursor recall: 0.214286
- Combined precision: 0.307692
- Combined false rate: 0.384615
- Combined opposite rate: 0.192308
- Combined median lead: about 70 minutes
- Combined validation resolved: 6
- validation UP resolved: 0
- validation DOWN resolved: 6
- validation false rate: 0.666667
- pinned 07:05 case: caught before move
- actual-backed count: 0
- recommendation: `continue_shadow_collection`

The result does not authorize live notification behavior or production tuning.

## Current exact next action

Implement the active opt-in daily shadow collection specification:

```text
chatgpt/specs/active/20260712_turning_precursor_daily_shadow_collection.md
```

Goal:

- connect the accepted precursor replay to the existing daily P8 operating cycle
- reuse the same public OHLCV fetch
- use a bounded signal slice matching OHLCV coverage
- write date-scoped generated shadow evidence
- expose compact status in the daily result
- keep the feature disabled by default
- do not edit or enable the installed launchd job

## Runtime boundary

This source task must not enable the feature in the scheduled runtime.

The installed daily invocation remains unchanged because the new integration requires an explicit opt-in flag.

After bounded source validation, runtime enablement requires a separate human-approved task.

## P9 entry rule

P9 remains blocked.

No production proposal is authorized because:

- Combined validation is one-sided
- validation UP resolved count is zero
- validation false rate is above the proposal-quality limit
- actual-backed count is zero

## Active sources of truth

- `chatgpt/specs/active/20260712_turning_precursor_daily_shadow_collection.md`
- `chatgpt/specs/archive/20260712_turning_volatility_precursor_replay.md`
- `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md`

## Prohibited

- no scoring or market-map tuning
- no threshold or gate change
- no notification trigger or mail behavior change
- no HTML production integration
- no launchd or schedule change
- no runtime restart
- no automatic tuning
- no exchange private/account/order endpoint
- no raw export commit
- no `paper_positions.csv` integration
- no automatic order

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually
# Current next action — 2026-07-12

- mode: `HUMAN_CHECK`
- next task: runtime-enable proposal review for opt-in turning precursor shadow collection
- bounded source integration is complete; archived spec: `chatgpt/specs/archive/20260712_turning_precursor_daily_shadow_collection.md`
- installed schedule remains unchanged and does not pass `--include-turning-precursor-shadow`
- any runtime enablement requires explicit approval; future review must use the date-scoped shadow status and preserve report-only behavior
- P9 remains blocked and no production notification proposal is authorized
