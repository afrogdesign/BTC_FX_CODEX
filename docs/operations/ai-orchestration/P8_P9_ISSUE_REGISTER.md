# P8 / P9 Issue Register

last_updated: 2026-07-11
status: active
source_of_truth: `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`

## Rules

- 会話だけで問題を管理しない。
- 単一例は`open hypothesis`として記録し、production tuningの根拠にしない。
- deterministic evidence、actual-backed evidence、人間のUI観察を分離する。
- unresolved / no_ohlcvを勝敗へ混ぜない。
- issueの解決は実装完了ではなく、再評価で改善が確認された時点とする。

## Status values

- `open hypothesis`
- `confirmed usability issue`
- `confirmed data/logic issue`
- `collecting evidence`
- `eligible for P9 proposal`
- `approved for implementation`
- `shadow validation`
- `resolved`
- `rejected`

## Issues

### P8-ISSUE-001 — Global STOP masks side-specific opportunity

- category: classifier logic / over-suppression
- status: open hypothesis
- first_seen: 2026-07-11
- evidence:
  - source inspection: global `no_trade_flags` returns `STOP_OR_EXIT` before side-specific B/C evaluation
  - one observed Short-zone case where market later moved down
- risk: valid opposite-side manual-review opportunity may be hidden
- required evidence:
  - occurrence count
  - opposite-side zone outcome
  - side/regime/setup split
  - actual-backed count
  - current-B/C-without-global-STOP counterfactual
- first baseline (2026-07-11): 364 STOP rows, 449 opposite-side candidates, 0 counterfactual B, 0 counterfactual C, 0 qualified rows; no actual evidence supplied
- baseline status remains `open hypothesis`; a single baseline does not establish tuning eligibility
- corrected baseline (2026-07-11): 45 qualified proxy rows, counterfactual B 10, counterfactual C 35, not eligible 46, and no actual evidence; status remains `open hypothesis`
- next action: P8 evidence pipeline measures; P9 may propose side-aware STOP only after adequate evidence
- production change: prohibited until P9 approval

### P8-ISSUE-002 — Main decision and Big Chance hierarchy is unclear

- category: UI / operator comprehension
- status: confirmed usability issue
- first_seen: 2026-07-11
- evidence: user interpreted auxiliary Long hypothesis as the primary prediction despite main WAIT and STOP
- risk: operator may act on a lower-priority hypothesis
- next action: P9 UI proposal should separate primary action, auxiliary hypothesis, and invalidation state

### P8-ISSUE-003 — Raw classifier payload is exposed

- category: UI / explainability
- status: confirmed usability issue
- first_seen: 2026-07-11
- evidence: slash-separated internal fields are displayed in operator cards
- risk: next action, side, and reason are difficult to understand
- next action: human summary first; technical details under a collapsed diagnostic section

### P8-ISSUE-004 — STOP card side identity is unclear

- category: UI / actionability
- status: confirmed usability issue
- first_seen: 2026-07-11
- evidence: two STOP cards do not make Long/Short identity sufficiently prominent
- risk: operator cannot quickly determine which thesis is stopped
- next action: explicit `LONG` / `SHORT` card header and side-specific action sentence

### P8-ISSUE-005 — Manual trial was incorrectly described as full manual logging

- category: documentation / operations
- status: resolved
- first_seen: 2026-07-11
- correction:
  - market outcomes are deterministic and automatic
  - actual trades are imported and linked from local exports
  - human input is limited to ambiguous intent and exceptional cases
- resolution source: `P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`

### P8-ISSUE-006 — P5 structured major-level contract mismatch

- category: evidence validation / identity
- status: resolved
- first_seen: 2026-07-11
- evidence: `trades.csv` intentionally stores `nearest_major_support` and `nearest_major_resistance` as JSON level objects, but P5 initially validated them as scalar Decimals
- safe blocked behavior: the first corrected run refused silent coercion of 108 relevant signal rows
- resolution: commits `00c227d` and `0bd5d76` accept canonical structured objects and legacy finite scalars for validation and fingerprint identity only
- corrected baseline: the unmodified 108-row signal context completed P4/P5/P8 with no no-OHLCV rows
- production change: none; A/B/C/STOP decisions, thresholds, gates, scoring, notification, and runtime behavior are unchanged

### P8-ISSUE-007 — Manual operating-cycle lineage drift

- category: evidence operations / lineage
- status: resolved
- first_seen: 2026-07-11
- evidence: the first baseline mixed an unsuitable candidate source with stale OHLCV, and the corrected baseline required manual reconstruction of candidate, signal, outcome, P4, P5, and P8 paths
- resolution: `run-p8-operating-cycle` now performs deterministic slicing, freshness validation, accepted stage calls, cross-stage identity checks, manifest fingerprints, and atomic promotion in one report-only cycle
- resolution commit: `9bee53a`
- validation: local no-fetch smoke passed with the accepted corrected inputs (206 candidates, 108 signals, 97 trial facts, 84 resolved, no-OHLCV 0)
- production change: none; no trading logic, notification, runtime, or automatic tuning behavior changed

## P9 proposal eligibility

An issue may become `eligible for P9 proposal` only when:

- evidence cutoff and versions are reproducible
- unresolved/no_ohlcv are separated
- candidate rows are scenario-deduplicated
- Long/Short and relevant regime/setup splits are available
- the issue has more than a single anecdotal example unless it is a deterministic bug or safety defect
- actual-backed evidence is included where the claim concerns actual trading performance
- a validation window can be reserved

## Change-class separation

Never combine these in one tuning task without explicit approval:

1. data/identity defect
2. UI/wording/hierarchy
3. shadow classifier logic
4. comparison threshold
5. production gate
6. notification behavior
7. runtime behavior


### P8-ISSUE-008 — Turning / volatility precursor alert is late or absent

- category: direction-state interpretation / notification behavior / missed opportunity
- status: collecting evidence
- first_seen: 2026-07-12
- observed case:
  - signal `20260711_220501` at 2026-07-12 07:05 JST
  - primary bias remained Long with display score 81 / 19
  - phase was `reversal_risk`
  - major-resistance rejection, conflicting bullish role-flip evidence, high wait pressure, and high location risk were present
  - current notification was suppressed by low confidence, invalid setup, and multiple no-trade flags
  - the market subsequently moved materially downward before the later Short attention
- risk:
  - a correct no-entry decision can still hide an important opposite-side chart-check opportunity
  - the operator may receive the warning only after most of the high-volatility move has occurred
- required evidence:
  - large-move recall and false-warning rate
  - Long/Short symmetry
  - lead time before 1h/2h/4h expansion
  - regime and phase split
  - notification burden after episode deduplication
  - separation of market-map interpretation errors from notification-trigger gaps
  - validation-window performance
- active evidence spec:
  - `chatgpt/specs/archive/20260712_turning_volatility_precursor_replay.md`
- current action:
  - HUMAN_CHECK / ChatGPT review of corrected replay evidence
  - preserve current scoring, gates, and notification behavior
- production change:
  - prohibited until replay evidence is reviewed and a separate human-approved proposal is created

#### Corrected replay result — 2026-07-12

- all pre-correction replay metrics are invalid and discarded
- corrected input: `2,872` signal rows, `28` independent realized-move opportunities, `2,194` deduplicated precursor episodes
- current notification baseline: `637` episodes, independent large-move recall `0.392857`
- Combined precursor: `238` episodes, `26` resolved, all precision `0.307692`, independent recall `0.214286`, false rate `0.384615`, opposite rate `0.192308`, whipsaw `0.115385`, median lead `69.9885` minutes
- Combined validation: `6` resolved (`UP=0`, `DOWN=6`), precision `0.333333`, recall `0.5`, false rate `0.666667`, opposite rate `0`, median lead `77.4875` minutes; validation established but proposal gate failed
- pinned `20260711_220501`: caught before move; exclusion gate pass
- actual-backed precursor count: `0`
- recommendation: `continue_shadow_collection`
- policy direction, Combined agreement, independent evidence groups, state transitions, stable IDs, continuity, opportunity denominator, validation and malformed-list fail-closed contracts were corrected
- production change: none; no pre-correction conclusion is retained


#### ChatGPT acceptance decision — 2026-07-12

- replay implementation commit `9f4f6a1` is accepted
- the 07:05 pinned case confirms that an opposite-side chart-check precursor can exist while the formal setup remains invalid
- the current Combined policy is not eligible for a live notification proposal
- reasons:
  - overall Combined recall `0.214286` is below current notification recall `0.392857`
  - validation has only `6` resolved Combined episodes
  - validation side split is `UP=0`, `DOWN=6`
  - validation false rate is `0.666667`
  - actual-backed count is `0`
- next evidence action:
  - implement opt-in daily shadow collection under `chatgpt/specs/active/20260712_turning_precursor_daily_shadow_collection.md`
  - reuse the existing daily public OHLCV fetch
  - keep the feature disabled in the installed schedule until separate approval
- status remains: `collecting evidence`
- no scoring, market-map, threshold, gate, notification, mail, runtime, API, account, or order change is authorized
#### Daily shadow integration — 2026-07-12

- opt-in `--include-turning-precursor-shadow` is implemented and bounded-validated
- core P8 and precursor shadow both succeeded in one wrapper cycle; the same validated public OHLCV path was reused
- signal slice: 127 rows; precursor episodes: 175; resolved: 26; realized opportunities: 28
- Combined recall 0.25, precision 0.307692, false rate 0.384615, opposite rate 0.192308, whipsaw 0.115385, median lead 69.9885 minutes
- validation established with UP=0 and DOWN=6; recommendation remains `continue_shadow_collection`
- actual-backed count: 0; no production conclusion is drawn from this bounded shadow run
- source integration status: resolved for the approved opt-in collection scope
- installed schedule remains disabled; runtime enablement requires separate HUMAN_CHECK approval

#### Runtime collection approval — 2026-07-12

- human approved enabling the opt-in daily shadow collector for `P8-ISSUE-008`
- approved target: `com.afrog.btc-p8-operating-cycle`
- approved argument: `--include-turning-precursor-shadow`
- purpose: collect additional Long/Short precursor evidence only
- this approval does not authorize notification, scoring, market-map, gate, threshold, mail, UI, or order changes
- production proposal status remains `continue_shadow_collection`
- first normal 11:30 JST cycle after apply is the runtime verification checkpoint

#### Runtime enable attempt 1 — rollback / diagnosis pending

- source commit `72d1733` is pushed and repository validation passed
- installed target bootstrap failed with `Input/output error`
- original installed plist was restored; installed shadow flag count is `0`
- target label remains unloaded
- runtime shadow collection is not enabled yet
- no manual P8 cycle or production behavior change occurred
- next action: target-only launchd registration diagnosis before any further bootstrap attempt
#### Runtime shadow collection enabled — 2026-07-12

- `com.afrog.btc-p8-operating-cycle` runtime shadow collection enabled with the committed flag exactly once
- root cause of the prior bootstrap failure: stale target registration in the GUI domain after rollback
- target-only repair and verification completed; installed plist uses primary repo paths and the unchanged 11:30 JST schedule
- first scheduled verification is pending; no production notification conclusion is drawn

#### Side-aware MTF operator action completion — 2026-07-12

- pinned `20260712_040500`: Long `STOP_OR_EXIT`; Short `B_CHECK_15M` / `armed`; primary Short; formal bias, scores and blocked gate preserved
- moved `20260712_050500`: prior-plan Short progress is `late_no_chase`
- result fields, future CSV evidence columns and public detail hierarchy are source-only additions
- no scoring, market-map, gate, notification, mail, runtime, API, account, order, or automatic-tuning behavior changed


---

## 2026-07-12 approved side-aware multi-timeframe implementation

The user approved bounded source implementation for the recurring over-suppression pattern where one side is safely stopped but an opposite-side Active Plan opportunity is hidden.

Active spec:

```text
chatgpt/specs/active/20260712_side_aware_multi_timeframe_operator_action.md
```

Work ID:

```text
BTCFX-20260712-P8-SIDE-AWARE-MTF-OPERATOR-ACTION
```

Related issues:

- `P8-ISSUE-001` global STOP masks side-specific opportunity
- `P8-ISSUE-008` turning / volatility precursor alert is late or absent

Pinned evidence signal `20260712_040500` already contained a Short limit-retest candidate and conditional Short counter-scalp candidate while the Long primary setup was invalid. The new layer must surface Long STOP and Short B-check independently.

This approval authorizes source, targeted tests, future-result evidence fields, and display hierarchy only. It does not authorize scoring, market-map, gate, notification trigger, mail sending, runtime restart, launchd, API, account, order, or automatic trading changes.
