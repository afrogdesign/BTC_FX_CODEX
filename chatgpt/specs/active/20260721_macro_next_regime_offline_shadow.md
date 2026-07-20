# M3 Macro Next-Regime Offline Shadow — Active Specification

## Metadata

- work_id: `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW`
- status: approved for bounded source implementation
- phase: M3 Big Chance next-regime contract
- branch: `Ver04-v2`
- accepted_m2_commit: `8aee427`
- accepted_m2_docs_commit: `c2eed44`
- accepted_m2_spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Decision

M2 is accepted as an optional macro evidence shadow. Its current evidence recommendation is `continue_shadow_collection`, so M3 must remain offline and fail closed.

M3 defines and replays a separate next-regime contract. It does not modify the current production Big Chance evaluator, HTML, notification, mail, scoring, gates, thresholds, runtime, or launchd.

## 2. Objective

Create a deterministic offline replay that separates:

- current tactical side
- current structural thesis
- explicitly weakening thesis
- candidate next-regime side
- activation evidence
- invalidation evidence
- first reliable structural target

Compare this contract with the existing `evaluate_big_chance` result as a frozen baseline without changing that function.

## 3. Inputs

Required explicit local inputs:

- M2 `macro_signal_slice.csv`
- M1/M2 `macro_structure_volatility_events.csv`
- M1/M2 `macro_level_reliability.csv`
- M1/M2 `macro_structure_volatility_replay.json`

Join signal rows to macro events by `signal_id`. Resolve target and obstruction references to level records by `level_id`. Treat replay JSON as a schema/method/coverage metadata contract rather than a row join. Reject duplicates, malformed timestamps, incompatible schema/method versions, missing required columns, and event/signal mismatches.

Only published performance events are eligible. Context-only rows must not re-enter M3 metrics or outputs.

## 4. Event-time contract

Forecast fields may use only information available in the joined signal, macro event, and level records at that event timestamp.

Future outcome fields from the M1 event may be used only after the forecast record is fixed and only for replay evaluation.

Do not use future outcomes, later events, later levels, or retrospective resolution to choose:

- next-regime side
- status
- activation
- invalidation
- target
- episode boundary

## 5. Candidate semantics

Output one record per eligible macro event.

Minimum fields:

- schema and method version
- signal/event identifiers and UTC/JST timestamps
- current tactical side
- current structural thesis
- weakening thesis
- next-regime side: `UP`, `DOWN`, or `NONE`
- status: `none`, `watch`, `armed`, or `activated`
- activation event families and reason codes
- invalidation reason codes
- first reliable target ID
- intervening obstruction
- price location
- volatility state and expansion risk
- baseline Big Chance present/side/status/grade
- forecast evidence JSON
- M1 outcome fields used for evaluation
- safety boundary

Rules:

1. Weakening alone cannot create a directional next-regime candidate.
2. A directional candidate requires explicit event-time directional activation.
3. `activated` additionally requires a compatible structural event family, a reliable target, and no intervening obstruction.
4. `armed` may represent explicit activation with incomplete target/corridor confirmation.
5. `watch` may represent an explicitly weakening thesis without directional activation.
6. Missing, conflicting, or unavailable evidence yields `NONE` or a lower status; never infer favorable evidence.
7. Tactical side, structural thesis, and next-regime side remain independent and may disagree.
8. Midpoint/equilibrium proximity alone cannot create direction or activation.

Compatible directional families are limited to the accepted M1 event families for reliable-level rejection, level-break acceptance, false-break reclaim, order-flow pressure, and open travel corridor. Do not add new production policy semantics in M3.

## 6. Baseline comparison

Call the existing `src.analysis.big_chance.evaluate_big_chance` only as a frozen baseline adapter using the current and previous signal rows in event-time order.

Do not edit `src/analysis/big_chance.py` or reinterpret its score/grade as execution permission.

Record baseline/candidate agreement, disagreement, and candidate-only or baseline-only observations.

## 7. Episodes and evaluation

Deduplicate baseline and candidate policy episodes independently using observable fired-state reset, side/status/evidence transition, or the accepted three-hour separation. Future outcome changes cannot split an episode.

Evaluate 3H, 6H, 12H, and 24H outcomes using the already-resolved M1 event fields.

Report separately for baseline and candidate:

- fired episodes
- resolved episodes
- directional precision
- opposite-move rate
- balanced/no-expansion rate
- whipsaw rate
- unresolved rate
- median lead minutes when `first_material_move_timestamp` exists
- burden per JST day
- UP/DOWN split
- structural-state, price-location, volatility-state, and reliability split

Do not claim independent large-move recall unless an explicit independent-opportunity denominator is available in the supplied accepted artifact. Label event-based coverage separately from recall.

## 8. Proposal gate

The replay recommendation is one of:

- `continue_shadow_collection`
- `eligible_for_m4_render_shadow`

Eligibility requires all declared conditions:

- chronological validation is established
- both UP and DOWN have at least 10 resolved candidate episodes in validation
- candidate directional precision exceeds the frozen baseline
- candidate opposite-move and false/balanced warning rates do not materially degrade
- results are not concentrated in one JST date
- required source coverage and continuity pass
- no unresolved schema or data-quality issue

This gate authorizes only M4 render-shadow design. It never authorizes production Big Chance, notification, runtime, or order changes.

## 9. Outputs

Publish atomically and deterministically:

- `macro_next_regime_events.csv`
- `macro_next_regime_policy_episodes.csv`
- `macro_next_regime_replay.json`
- `macro_next_regime_replay.md`

Existing outputs must require explicit replace behavior. A failed transaction must preserve the complete prior set.

## 10. CLI

Add one explicit offline CLI route in `tools/log_feedback.py`:

```text
replay-macro-next-regime
```

It accepts the four required inputs, four output paths, and explicit replace behavior. Return compact JSON only; do not print raw rows.

M3 does not integrate into the daily P8 wrapper or installed runtime.

## 11. Required tests

Add only missing focused coverage:

- weakening without activation remains non-directional
- compatible activation plus target/clear corridor can activate
- missing target, obstruction, conflicting direction, and unavailable evidence fail closed
- tactical, structural, and next-regime fields remain separate
- existing Big Chance evaluator is used without mutation
- future outcome changes do not change forecast fields or episode boundaries
- baseline and candidate episode dedup use the three-hour rule
- context-only input is rejected or excluded from performance outputs
- validation gate fails closed for inadequate or one-sided evidence
- four-output transaction is deterministic and rolls back on failure
- actual CLI parser/dispatch coverage
- existing `tests.test_big_chance` remains passing

Do not duplicate equivalent existing coverage.

## 12. Allowed implementation files

- new `src/feedback/macro_next_regime_replay.py`
- new `tests/test_macro_next_regime_replay.py`
- `tools/log_feedback.py`
- `tests/test_log_feedback.py`
- this active spec only for factual implementation notes; do not archive it during implementation

Do not edit production Big Chance, analysis, notification, UI, mail, scoring, gates, thresholds, classifiers, deploy, plist, launchd, runtime, APIs, accounts, positions, or orders.

## 13. Validation

Run once after implementation:

```bash
./.venv312/bin/python -m unittest tests.test_macro_next_regime_replay
./.venv312/bin/python -m unittest tests.test_big_chance
./.venv312/bin/python -m unittest tests.test_log_feedback.MacroNextRegimeCliTests
```

Run one bounded offline replay against the accepted M2 local artifact set when available. Generated outputs remain local and uncommitted.

Finally run:

```bash
git diff --check
```

Do not run the full test suite or unrelated operating-cycle tests.

## 14. Completion condition

M3 source completion requires:

- focused tests pass
- one bounded offline replay succeeds
- outputs are complete and deterministic
- recommendation is reported without production claims
- no production or runtime behavior changes

After ChatGPT acceptance, proceed directly to a separate M4 active spec for render-only operator hierarchy shadow. M3 acceptance does not itself change live UI or runtime.


---

## 15. ChatGPT acceptance — 2026-07-21

M3 is accepted as an offline, report-only next-regime comparison layer.

Accepted implementation commits:

- initial implementation: `04d205a`
- evaluation completion: `8639162`
- episode identity completion: `1f4ea67`
- family conflict boundary completion: `4f97a55`

Accepted evidence:

- focused M3 tests: 8 passing
- fresh bounded replay: 124 performance events and 58 policy episodes
- candidate and frozen Big Chance baseline remain independent
- explicit obstruction and directional-family conflicts fail closed
- candidate and baseline episode identities use complete pre-outcome evidence keys and three-hour separation from episode start
- 3H, 6H, 12H, and 24H metrics and required performance-only splits are present
- chronological validation compares candidate and baseline on the same dates
- input schema, version, identifier, target, obstruction, and event-family boundaries are checked
- four outputs publish deterministically and roll back as a complete set

The bounded recommendation remains `continue_shadow_collection`. This does not block M4 render-only hierarchy work, but it does block production adoption of the M3 policy.

M3 acceptance does not authorize changes to live Big Chance, notification, mail, scoring, thresholds, gates, runtime, APIs, accounts, positions, or orders.

---

## 16. Correction — validation-window review pending

The historical acceptance record above is withdrawn pending FIX-04 review. M3 remains the active offline, report-only specification; M4 implementation is not authorized.

FIX-04 corrects the chronological validation date basis to all eligible performance events (including dates with no policy episode), evaluates candidate and baseline on that same date set, and applies single-date concentration to candidate validation episodes only.

The M3 proposal gate uses `3h` as its explicit primary horizon. The `6h`, `12h`, and `24h` metrics and splits remain required descriptive diagnostics only. Any future eligibility remains render-only M4 design eligibility and never authorizes production behavior.

## 17. FIX-05 burden and validation-quality contract

`burden_per_jst_day` uses explicit eligible performance-event JST observation dates: common full-period dates, common validation dates, and common split-specific eligible-event dates. Dates with zero policy episodes remain in each applicable denominator.

Validation data quality is audited from every eligible validation event. Only `ok` passes; blank or non-`ok` values are normalized and fail closed. This correction does not change forecasts, episode identity, family policy, thresholds, or production behavior.

---

## 17. Final ChatGPT acceptance after FIX-04 — 2026-07-21

The validation-window correction is accepted. The withdrawal recorded in Section 16 is resolved by commit `3ae30f4`.

Final accepted M3 implementation chain:

- initial implementation: `04d205a`
- evaluation completion: `8639162`
- episode identity completion: `1f4ea67`
- family conflict boundary completion: `4f97a55`
- validation-window contract completion: `3ae30f4`

Final accepted evidence:

- focused M3 tests: 11 passing
- fresh bounded replay: 124 eligible performance events
- candidate episodes: 12
- frozen baseline episodes: 46
- eligible-event JST date basis: 7 dates
- chronological validation dates: `2026-07-19`, `2026-07-20`, `2026-07-21`
- validation candidate and baseline metrics use the same eligible-event-derived date set
- single-date concentration is calculated from candidate validation episodes only
- `3h` is explicit as the primary M3 proposal-gate horizon
- `6h`, `12h`, and `24h` remain descriptive diagnostic horizons
- candidate-owned failed-thesis evidence can produce a non-directional `watch` independently of the frozen baseline
- four bounded outputs are complete and consistent

The final bounded recommendation is `continue_shadow_collection`. M3 is accepted only as an offline, report-only comparison contract. It is not accepted for production Big Chance behavior, notification, mail, scoring, threshold, gate, classifier, runtime, API, account, position, or order changes.

M4 may proceed only as a local render-only hierarchy shadow. No live UI deployment is authorized.

---

## 18. Correction — FIX-05 burden denominator and validation quality review

The final acceptance recorded in Section 17 is withdrawn pending FIX-05 review. M3 is active again. M4 implementation commit `5574a2e` is preserved as unaccepted local render work, but M4 acceptance and M5 start are blocked until this correction is accepted.

FIX-05 requirements:

- `burden_per_jst_day` must use an explicit eligible-performance-event JST-date denominator for the relevant evaluation window, not only dates on which an episode fired.
- Candidate and frozen baseline metrics must use the same denominator date set.
- Overall metrics use all eligible performance-event JST dates.
- Chronological validation metrics use the common validation JST dates, including dates with zero candidate or baseline episodes.
- Split burden metrics use the same split-specific eligible-event date set for candidate and baseline.
- Output metrics must expose the denominator basis and denominator date count so the burden calculation is auditable.
- Validation data-quality checks must inspect all eligible performance events in the validation dates, including dates and rows with no policy episode.
- An unresolved validation event-quality issue must fail the render-eligibility gate without retroactively changing forecasts or episode identity.

The recommendation remains report-only. FIX-05 must not change candidate semantics, Big Chance baseline behavior, episode boundaries, thresholds, notifications, runtime, or orders.
