# M4 Macro Operator Hierarchy Render Shadow — Preserved Draft

## Metadata

- work_id: `BTCFX-20260721-MACRO-OPERATOR-HIERARCHY-RENDER-SHADOW`
- status: draft preserved / implementation not authorized
- phase: M4 operator hierarchy shadow UI
- branch: `Ver04-v2`
- m3_status: FIX-04 acceptance required before reactivation
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Decision

This draft is preserved for later design review only. M3 FIX-04 must be accepted before any M4 reactivation or implementation. The M3 recommendation remains `continue_shadow_collection`; this draft must not promote the M3 candidate into production behavior.

M4 creates a deterministic local HTML render shadow. It must not edit or call the live notification sender, mail builder, installed runtime, launchd, production Big Chance evaluator, scoring, thresholds, gates, or classifiers.

## 2. Objective

Test whether an operator can understand the same event-time facts in this order:

1. chart and price geometry
2. compact macro structure strip
3. explicit next-regime card
4. tactical 15-minute execution map
5. existing operator-action wording retained as secondary detail

The render must separate:

- macro structural evidence
- current tactical execution
- next-regime risk
- unavailable or unresolved evidence

No candidate grade, status, or visual emphasis may be presented as permission to enter a trade.

## 3. Explicit bounded inputs

Required local files:

- P8 signal context CSV
- P8 intraperiod tactical candidate/outcome CSV
- M2 macro event CSV
- M2 level reliability CSV
- M3 next-regime event CSV
- M2 1-hour public OHLCV CSV
- one explicit `signal_id`

Optional:

- M2 4-hour public OHLCV CSV for a compact context strip

The renderer must not discover files implicitly. Every input path and the selected `signal_id` are CLI arguments.

## 4. Event-time and leakage boundary

Join the selected record by `signal_id`.

The rendered HTML and its display manifest may use only event-time fields:

- signal context and current price
- tactical candidate Entry zone, SL, TP1, TP2, status, headline, and next condition
- macro structure state, structural direction, price location, reliable level IDs and bands, volatility state, expansion risk, target, obstruction, and event families
- M3 tactical side, structural thesis, weakening thesis, next-regime side, candidate status, activation/invalidation evidence, target, and baseline comparison fields
- OHLCV candles closed at or before the selected event timestamp
- level records available for the selected event and referenced IDs

The renderer must never expose or use for ordering, emphasis, labels, selection, or content:

- `outcome_1h`
- `outcome_3h`
- `outcome_6h`
- `outcome_12h`
- `outcome_24h`
- realized MFE or MAE
- target-touch result
- first material move timestamp
- replay recommendation performance
- future data-quality resolution

Future fields may be present in source CSV files, but must be ignored before view-model construction.

## 5. Deterministic view model

Create a versioned view model, for example `macro_operator_hierarchy_shadow.v1`.

Minimum top-level fields:

- schema and method version
- selected signal ID and event timestamp
- input fingerprints
- source schema/method versions
- chart model
- macro strip model
- next-regime card model
- tactical execution map model
- secondary operator detail model
- baseline/challenger section order
- missing-data flags
- trace map from each displayed fact to source file and source field
- safety boundary

The view model must contain display-ready values only. It must not retain future outcome fields.

All ordering must be explicit and deterministic.

## 6. Primary chart

Render one self-contained SVG chart inside the HTML.

Primary source:

- 1-hour public OHLCV candles closed at or before the selected event timestamp

Default visible window:

- latest 72 closed 1-hour candles at or before the event
- use all available prior candles when fewer than 72 exist

Chart requirements:

- candlestick bodies and wicks
- current event-price line
- macro support and resistance bands referenced by the selected macro event when present
- first reliable target when present
- explicit obstruction level when present
- tactical Entry zones, SL, TP1, and TP2 from selected tactical candidates
- visually and semantically separate macro overlays from tactical overlays
- labels must identify timeframe and evidence type
- no future candle after the event timestamp
- no client-side external JavaScript, fonts, images, or network resources

Do not fabricate 15-minute candles.

The tactical section is a 15-minute execution price map, not a candlestick chart, because the accepted M2 artifact set does not persist matching 15-minute OHLCV for this event window.

## 7. Compact macro strip

Place directly below or beside the primary chart.

Minimum content:

- structural state or thesis
- price location
- nearest/referenced reliable support and resistance with reliability bands
- volatility state
- expansion risk
- first reliable target
- intervening obstruction

Unavailable values must display as `insufficient` or `unavailable`; they must not be hidden or upgraded.

Midpoint/equilibrium is descriptive location only and may not be presented as an activation signal.

## 8. Explicit next-regime card

Minimum content:

- current tactical side
- current structural thesis
- weakening thesis
- next-regime side
- status: none / watch / armed / activated
- activation families
- invalidation reason codes
- first reliable target
- baseline Big Chance side/status/grade/type for comparison
- comparison category

Required labels:

- `evidence confidence, not execution permission`
- `report-only`
- `human decides manually`

When next-regime side is `NONE`, the card must not imply a directional trade.

When tactical and next-regime sides disagree, show the disagreement explicitly without selecting a winner.

## 9. Tactical 15-minute execution map

Use all tactical candidate rows for the selected signal.

For each candidate display:

- side
- candidate type
- entry mode
- entry zone
- SL
- TP1
- TP2
- market/limit/counter-scalp/breakout statuses
- current headline
- next 15-minute confirmation condition

The price map must distinguish tactical levels from macro levels.

Outcome, entry-reached, exit, MFE, and MAE fields must not enter the view model or HTML.

The map must not rewrite blocked/conditional status as actionable permission.

## 10. Secondary operator detail

Retain the existing event-time operator headline and next-condition wording as a visually secondary `<details>` or equivalent section below the chart, macro strip, next-regime card, and execution map.

Do not import or render the production detail page.

This shadow compares hierarchy, not pixel-identical production HTML.

## 11. Comparison contract

Render two section-order summaries in the same local artifact:

### Baseline hierarchy approximation

- operator action wording first
- chart and structural evidence later

### M4 challenger hierarchy

- chart first
- macro strip second
- next-regime card third
- tactical execution map fourth
- operator action detail last

The baseline pane may be a compact structural wireframe using the same event-time facts. It must not claim to reproduce production HTML exactly.

The JSON manifest must record both ordered section lists and confirm that the challenger chart appears before action wording.

## 12. Output contract

Publish exactly three files atomically and deterministically:

- `macro_operator_hierarchy_shadow.html`
- `macro_operator_hierarchy_shadow.json`
- `macro_operator_hierarchy_shadow.md`

The JSON is the canonical render manifest.

The Markdown is a compact review guide containing:

- selected event facts
- baseline/challenger section orders
- missing data
- source trace summary
- visual review checklist
- limitations
- safety boundary

Existing outputs require explicit replace behavior. A failed publication must preserve the complete previous three-file set.

## 13. CLI

Add one offline CLI route in `tools/log_feedback.py`:

```text
render-macro-operator-hierarchy-shadow
```

Required arguments:

- `--signal-context-csv`
- `--tactical-candidates-csv`
- `--macro-events-csv`
- `--macro-levels-csv`
- `--next-regime-events-csv`
- `--ohlcv-1h-csv`
- `--signal-id`
- `--output-html`
- `--output-json`
- `--output-md`
- explicit replace flag

Optional:

- `--ohlcv-4h-csv`

Stdout must be compact JSON only and contain output status, selected signal, section order, and missing-data status. Do not print HTML, raw rows, or private paths.

## 14. Required validation and fail-closed checks

Reject before publication when:

- selected signal is missing from signal context, macro events, or M3 events
- duplicate natural keys make the selected join ambiguous
- selected event timestamps materially disagree
- required schema/method versions are incompatible
- OHLCV interval is not 1h
- OHLCV timestamps are malformed, duplicated, or non-monotonic
- the chart has no candle closed at or before the selected event
- a referenced target or obstruction level is absent from the level file
- output HTML contains a forbidden future field name or serialized future value

Tactical candidates may be zero rows. In that case, render an explicit `no tactical candidate rows` state rather than fail.

## 15. Required focused tests

Add only focused M4 coverage for:

- deterministic join by explicit signal ID
- chart excludes candles after the event timestamp
- macro and tactical overlays are represented separately
- next-regime disagreement is explicit and does not imply execution permission
- `NONE` next-regime remains non-directional
- tactical outcomes and future fields do not enter the view model or HTML
- baseline and challenger section order is deterministic and challenger is chart-first
- operator action detail is after the primary hierarchy
- missing tactical candidates render explicitly
- missing target/obstruction reference fails closed
- incompatible versions and duplicate keys fail closed
- HTML escapes source text
- three outputs are byte-identical on repeat
- partial promotion failure restores the prior complete set
- actual CLI parser and dispatch

Do not add browser automation, screenshot comparison, external network calls, production notification tests, or runtime tests.

## 16. Allowed implementation files

- new `src/feedback/macro_operator_hierarchy_shadow.py`
- new `tests/test_macro_operator_hierarchy_shadow.py`
- `tools/log_feedback.py`
- `tests/test_log_feedback.py`
- this active spec only for short factual implementation notes

Do not edit:

- `src/notification/detail_page.py`
- production HTML, notification, mail, Big Chance, analysis, scoring, thresholds, gates, or classifiers
- daily P8 wrapper
- deploy, plist, launchd, or runtime files
- APIs, accounts, positions, or orders

## 17. Bounded artifact

Use explicit accepted local inputs and signal `20260719_130500` for the first bounded render.

This event is intentionally informative because tactical/structural context and the M3 next-regime candidate are not identical. It is an example for hierarchy verification only and must not become a pinned product rule.

The bounded artifact must remain under `local/` and uncommitted.

## 18. Completion and next phase

M4 source completion requires:

- focused tests pass
- one bounded local render succeeds
- exactly three outputs are complete and deterministic
- HTML is self-contained and future-outcome free
- chart-first order and source trace are recorded
- no production or runtime behavior changes

After ChatGPT acceptance, archive this spec and create a separate M5 active specification for the deterministic bounded champion/challenger proposal engine.

M4 acceptance does not authorize live UI deployment.

---

## 19. Reactivation after final M3 acceptance — controlling status

This section supersedes the preserved-draft status and reactivation warning in the title and Metadata above.

- current status: approved for bounded M4 source implementation
- accepted M3 head: `3ae30f4`
- accepted M3 spec: `chatgpt/specs/archive/20260721_macro_next_regime_offline_shadow.md`
- accepted M3 recommendation: `continue_shadow_collection`
- authorization: local deterministic render-only hierarchy shadow
- production UI deployment: not authorized
- notification, mail, scoring, thresholds, gates, classifiers, runtime, APIs, accounts, positions, and orders: unchanged and out of scope

The remaining sections are the active implementation contract. The first bounded render remains a hierarchy/usability artifact only and must not be treated as evidence that the M3 policy is production-ready.

---

## 20. Pre-implementation event-time level correction — controlling requirement

The accepted level-reliability CSV is a cumulative bounded replay output and may contain confirmations later than the selected M4 event. M4 must not display future-updated level geometry or reliability as if it were event-time evidence.

Required handling:

- A 1-hour candle is eligible only when `timestamp_utc + 1 hour <= selected_event_timestamp_utc`.
- A level row is event-time safe only when its confirmation metadata contains no confirmation timestamp after the selected event.
- If `last_confirmed_at` or any parsed `member_confirmation_timestamps` value is later than the event, do not use that row's low/high/center/reliability/lifecycle fields.
- A target or explicit obstruction required by the selected M3 contract must exist and be event-time safe; otherwise reject before publication.
- A nearest support/resistance reference that exists but is not event-time safe may be rendered only as `referenced ID / event-time geometry unavailable`; it must not produce a chart band or reliability claim.
- Record all excluded future-confirmed references in `missing_data_flags` and the trace map.
- Do not reconstruct unavailable event-time geometry from later cumulative values.

For the bounded signal `20260719_130500`, the tactical candidate rows are intentionally multi-row and must be joined by `source_signal_id`; this is not a duplicate-key error. Candidate identity remains `candidate_id`.

This section supersedes any broader reading that permits final cumulative level rows to be used without an event-time check.

---

## 21. Acceptance hold after M3 FIX-05 review — controlling status

This section supersedes Section 19's active authorization.

- implementation base preserved: `5574a2e`
- current status: implementation present, acceptance withheld, inactive draft
- M3 prerequisite: `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW-FIX-05` and ChatGPT acceptance
- M4 follow-up after M3 acceptance: `BTCFX-20260721-MACRO-OPERATOR-HIERARCHY-RENDER-SHADOW-FIX-01`
- M5: blocked
- live UI deployment: prohibited

The current renderer remains useful local work, but it is not accepted because unique level geometry, reference/role consistency, complete macro-strip content, full displayed-fact traceability, tactical entry-zone bands, required focused regressions, actual CLI proof, and multi-parent atomic publication still require review and correction.

Do not delete or reset commit `5574a2e`. Reactivate this specification only after M3 FIX-05 acceptance.
