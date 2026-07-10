# Manual Trade Linkage and Ground-Truth Pipeline Active Spec

## Metadata

- work_id: `BTCFX-20260710-MTP-LINKAGE-PIPELINE-SPEC`
- created_at: `2026-07-10`
- status: active / design baseline
- phase: `P3`
- previous_phase: `P2 manual actual trade importer hardening complete`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

---

## 1. Objective

既存のmanual trade signal linkerとground-truth reportを、hardened importerのschemaとmanual trading practicality objectiveに適合させる。

P3はgreenfield implementationではない。

Existing implementation:

```text
tools/log_feedback.py
  score_manual_trade_signal_link()
  build_manual_trade_signal_link_rows()
  link_manual_trades_to_signals()
  summarize_manual_actual_trade_performance()
  calibrate_manual_trade_proxy_vs_actual()
  build_manual_trade_ground_truth_report()
```

Existing tests:

```text
tests/test_manual_trade_signal_linker.py
tests/test_manual_trade_ground_truth_report.py
```

P3の目的は、既存sourceが存在することを完成とみなさず、評価単位、link target、confidence、metric、migrationを明確にしてhardeningすることである。

---

## 2. Core correction

`manual_actual_trades.csv`はfill-level evidenceである。

したがって、次を同一視してはならない。

```text
fill row
order
position lifecycle
human trade episode
```

現行reportの`total_actual_trades`がfill row数を数えている場合、それを人間のtrade回数として解釈してはならない。

P3では次を分離する。

```text
fill-level monetary evidence
order-level execution evidence
position-lifecycle evidence
signal linkage evidence
human decision evidence
```

human decision evidenceはP4で扱う。

---

## 3. Canonical evaluation units

### 3.1 Fill

Source:

```text
logs/csv/manual_actual_trades.csv
```

Responsibility:

- fill price
- fill quantity
- fee
- realized PnL when present
- transaction side
- position action when present

A fill is not a human trade episode.

### 3.2 Order

Source:

```text
logs/csv/manual_actual_orders.csv
```

Responsibility:

- order timestamp
- order type
- filled quantity
- average fill price
- order status

An order may contain multiple fills and may not equal a complete position lifecycle.

### 3.3 Position lifecycle

Source:

```text
logs/csv/manual_actual_positions.csv
```

Responsibility:

- opened time
- closed time
- position side
- realized PnL
- open/closed status

Position lifecycle is the preferred exchange-ground-truth evaluation unit when a valid position row exists.

### 3.4 Manual trade episode

A manual trade episode is a normalized analytical entity built from one position lifecycle plus associated orders/fills.

It is not created by P3 unless deterministic association is possible.

P3 may create an episode only when:

- exactly one compatible position lifecycle is identified
- associated fills/orders fall within the episode time bounds
- symbol is compatible
- side/action evidence does not conflict
- no competing position candidate has equal evidence

Otherwise, evidence remains separate and status is `ambiguous`.

---

## 4. Canonical link target

Primary link target:

```text
position lifecycle
```

Fallback link target:

```text
manual trade episode
```

Fill rows are supporting evidence and are not the default signal-link target.

If no valid position lifecycle exists, P3 may generate a provisional episode from fills/orders only when deterministic episode boundaries are available.

Provisional episodes must be marked:

```text
episode_source=derived_without_position
```

They must not be treated as equal-quality evidence to position-backed episodes.

---

## 5. Side resolution

Hardened importer fields:

```text
side
transaction_side
position_action
```

Canonical position side resolution priority:

1. position row `side`
2. explicit fill/order `side` when it is `long` or `short`
3. explicit position action pair:
   - open long / close long -> long
   - open short / close short -> short
4. unresolved -> `unknown`

Do not infer:

```text
buy -> long
sell -> short
```

when `position_action` is unknown.

Buy/sell describes transaction direction, not necessarily position orientation.

Side conflict examples:

- position says long, associated fill says explicit short
- open action and close action imply incompatible position sides

Conflict result:

```text
side_compatibility=conflict
link_status=ambiguous
```

---

## 6. Cross-category association

Do not assume `source_uid_hash` is shared across fills, orders, and positions.

Association evidence may include:

- canonical symbol
- position side
- transaction side
- position action
- opened/closed timestamps
- fill/order timestamp within lifecycle window
- order/fill status
- price proximity when available

### 6.1 Position-to-fill association

Eligible fill:

- same symbol
- timestamp within:

```text
opened_at - 15 minutes
through
closed_at + 15 minutes
```

For open positions, upper bound is absent.

Preferred evidence:

- explicit matching side
- explicit open/close action
- no conflicting position candidate

### 6.2 Position-to-order association

Eligible order:

- same symbol
- timestamp within the lifecycle window
- no explicit side conflict

### 6.3 Ambiguity

If one fill/order is equally compatible with multiple positions:

```text
association_status=ambiguous
```

Do not attach it automatically.

### 6.4 Association method version

Every association row includes:

```text
association_method_version=manual_trade_association.v1
```

---

## 7. Signal eligibility window

Only signals at or before position/episode entry are primary entry-link candidates.

Default eligibility:

```text
0 <= entry_timestamp - signal_timestamp <= 240 minutes
```

Rules:

- same timestamp is eligible
- future notification after entry is not an entry-link candidate
- post-entry notification may be separately classified as `management_candidate`
- followup notifications are not automatically equivalent to initial notifications
- multiple notifications may be candidates for one position
- one signal may be linked to multiple positions only when each link independently satisfies the contract

The 240-minute value remains an initial analysis parameter, not a production trading threshold.

CLI must expose it as:

```text
--max-lookback-minutes
```

Default:

```text
240
```

Changing the default requires a later evidence-backed review.

---

## 8. Link evidence and scoring

P3 link score is versioned:

```text
link_method_version=manual_trade_signal_link.v2
```

### 8.1 Disqualifying conditions

Candidate is ineligible when:

- signal timestamp is after entry for entry-link mode
- timestamp cannot be parsed
- symbol explicitly conflicts
- position side explicitly conflicts
- source entity ID is missing
- signal ID is missing

### 8.2 Evidence components

Initial deterministic score:

| evidence | points |
|---|---:|
| signal within 30 minutes before entry | +4 |
| signal within 31-90 minutes | +3 |
| signal within 91-240 minutes | +1 |
| position side exact match | +4 |
| side unknown on one side, no conflict | +1 |
| BTC symbol exact match | +2 |
| entry-like notification class | +2 |
| followup/management class in entry-link mode | excluded from entry-link candidates |
| position/action conflict | disqualify |
| symbol conflict | disqualify |

### 8.3 Confidence bands

```text
high: score >= 10 and unique top candidate
medium: score 7-9 and unique top candidate
low: score 4-6 and unique top candidate
ambiguous: tie, conflict, insufficient identity, or score < 4
```

Only `high` and `medium` links may contribute to actual-backed aggregate comparison.

`low` is review evidence only.

`ambiguous` contributes only to coverage diagnostics.

### 8.4 Tie behavior

If multiple candidates share the same top score:

```text
link_status=ambiguous
link_reason=competing_candidate_tie
signal_id blank
```

Do not use timestamp ordering as a hidden tie-breaker.

---

## 9. Canonical outputs

### 9.1 Position/episode evidence

New canonical output:

```text
logs/csv/manual_trade_episodes.csv
```

Schema:

```text
schema_version
episode_id
episode_source
position_id
symbol
side
opened_at_utc
opened_at_jst
closed_at_utc
closed_at_jst
status
realized_pnl
fee_total
fill_count
order_count
association_method_version
association_status
association_reason_codes
created_at_utc
```

Schema version:

```text
manual_trade_episode.v1
```

### 9.2 Signal links

Canonical output:

```text
logs/csv/manual_trade_signal_links.csv
```

Schema:

```text
schema_version
link_id
episode_id
position_id
signal_id
entry_timestamp_jst
mail_timestamp_jst
time_delta_minutes
position_side
priority_direction
side_compatibility
symbol_compatibility
notification_class
link_score
link_confidence
link_status
link_reason
link_method_version
created_at_utc
```

Schema version:

```text
manual_trade_signal_link.v2
```

### 9.3 Legacy output handling

Existing unversioned/legacy link CSV is not merged into v2.

Policy:

- detect legacy header
- default exit `4` with `existing_output_schema_mismatch`
- allow explicit rebuild with `--replace-output`
- rebuild uses current source inputs and overwrites only generated local output
- no automatic migration of old row semantics

---

## 10. Episode identity and idempotency

Position-backed episode ID:

```text
episode_id = "ep_" + sha256(
  position_id + association_method_version
)[:24]
```

Derived episode ID:

```text
episode_id = "ep_" + sha256(
  symbol + side + opened_at_utc + closed_at_utc + sorted(fill_ids) + sorted(order_ids)
)[:24]
```

Link ID:

```text
link_id = "lnk_" + sha256(
  episode_id + signal_id + link_method_version
)[:24]
```

Repeated build with unchanged inputs must produce identical IDs and rows.

Default output behavior:

```text
rebuild deterministic generated CSV
```

P3 linker output is derived evidence, not append-only source truth.

---

## 11. Ground-truth report contract

The report must separate the following sections.

### 11.1 Input coverage

- fills
- orders
- positions
- episodes
- links
- signals

### 11.2 Fill-level monetary evidence

Allowed metrics:

- fill row count
- fee total
- realized PnL sum when source provides it
- missing fee/PnL coverage

Do not label fill row count as trade count.

### 11.3 Position/episode-level performance

Allowed metrics:

- closed episode count
- open episode count
- wins/losses/breakeven by episode realized PnL
- long/short episode counts
- episode-level gross/net PnL

### 11.4 Link coverage

- total episodes
- linked high
- linked medium
- linked low
- ambiguous
- no candidate
- competing tie
- side conflict
- symbol conflict

### 11.5 Actual-backed comparison

Only high/medium links contribute.

Allowed categories:

```text
actual_positive_with_entry_like_signal
actual_negative_with_entry_like_signal
actual_positive_with_defensive_signal
actual_negative_with_defensive_signal
ambiguous_needs_review
ambiguous_needs_review
```

These are descriptive calibration categories only.

Do not call them causal proof.

### 11.6 Prohibited claims

The report must not claim:

- notification caused the trade
- skip avoided a loss
- watch was correct
- missed opportunity occurred
- user followed or ignored the mail
- strategy is profitable
- thresholds should be relaxed

---

## 12. CLI contract

Episode build:

```bash
./.venv312/bin/python tools/log_feedback.py build-manual-trade-episodes \
  --trades logs/csv/manual_actual_trades.csv \
  --orders logs/csv/manual_actual_orders.csv \
  --positions logs/csv/manual_actual_positions.csv \
  --output-csv logs/csv/manual_trade_episodes.csv \
  --stdout-json
```

Link build:

```bash
./.venv312/bin/python tools/log_feedback.py link-manual-trades-to-signals \
  --episodes logs/csv/manual_trade_episodes.csv \
  --signals logs/csv/user_reviews.csv \
  --signal-outcomes logs/csv/signal_outcomes.csv \
  --output-csv logs/csv/manual_trade_signal_links.csv \
  --max-lookback-minutes 240 \
  --stdout-json
```

Ground-truth report:

```bash
./.venv312/bin/python tools/log_feedback.py build-manual-trade-ground-truth-report \
  --trades logs/csv/manual_actual_trades.csv \
  --orders logs/csv/manual_actual_orders.csv \
  --positions logs/csv/manual_actual_positions.csv \
  --episodes logs/csv/manual_trade_episodes.csv \
  --links logs/csv/manual_trade_signal_links.csv \
  --signal-outcomes logs/csv/signal_outcomes.csv \
  --stdout-json
```

### 12.1 Common behavior

- `--dry-run` writes nothing
- `--stdout-json` emits one compact JSON object plus newline
- generated files remain local
- full private paths are not printed
- no raw UID is printed

### 12.2 Exit codes

| code | meaning |
|---:|---|
| 0 | success, including deterministic no-op/rebuild |
| 1 | unexpected internal error |
| 2 | missing/invalid input |
| 3 | ambiguous association above allowed policy when strict mode is enabled |
| 4 | existing generated output schema mismatch or I/O failure |

---

## 13. Validation and test matrix

Required tests:

1. one closed position + matching fills/orders -> one episode
2. one position with multiple fills -> one episode, fill_count > 1
3. two positions with overlapping times -> ambiguous fill association
4. buy transaction without position side does not become long
5. sell transaction without position side does not become short
6. explicit open/close long association
7. explicit open/close short association
8. side conflict remains ambiguous
9. signal before entry within 30 minutes
10. signal before entry 31-90 minutes
11. signal before entry 91-240 minutes
12. signal outside lookback rejected
13. signal after entry rejected from entry-link mode
14. same timestamp eligible
15. competing equal-score candidates remain ambiguous
16. followup/management notification does not silently become entry signal
17. unique high-confidence link
18. unique medium-confidence link
19. low-confidence link excluded from actual-backed comparison
20. legacy link header rejected by default
21. explicit replace-output rebuild
22. deterministic episode/link IDs
23. dry-run no write
24. missing input compact failure
25. malformed timestamp compact failure
26. raw UID/full path non-leak
27. fill count not labeled trade count
28. episode-level win rate uses episodes, not fills
29. high/medium links only in actual-backed aggregates
30. avoided-loss/missed-opportunity claims absent
31. downstream report safety boundary remains visible

Targeted validation:

```bash
./.venv312/bin/python -m unittest \
  tests.test_manual_trade_episode_builder \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report

git diff --check
```

---

## 14. Preferred implementation structure

`tools/log_feedback.py` is already large.

Preferred modules:

```text
src/feedback/manual_trade_episode_builder.py
src/feedback/manual_trade_signal_linker.py
src/feedback/manual_trade_ground_truth.py
```

CLI wiring remains in:

```text
tools/log_feedback.py
```

Do not refactor unrelated report or trading code.

---

## 15. Allowed implementation files for P3

```text
tools/log_feedback.py
src/feedback/__init__.py
src/feedback/manual_trade_episode_builder.py
src/feedback/manual_trade_signal_linker.py
src/feedback/manual_trade_ground_truth.py
tests/test_manual_trade_episode_builder.py
tests/test_manual_trade_signal_linker.py
tests/test_manual_trade_ground_truth_report.py
chatgpt/specs/active/20260710_manual_trade_linkage_ground_truth_pipeline.md
```

P3 must not modify:

```text
src/trade/execution_gate.py
src/trade/phase1b_lite.py
src/trade/opportunity_gate.py
notification sending/trigger code
runtime/launchd files
paper_positions.csv integration
```

---

## 16. Completion criteria

P3 spec is complete when:

- fill/order/position/episode units are separated
- primary link target is explicit
- side resolution avoids buy=long / sell=short inference
- association ambiguity is explicit
- signal eligibility and scoring are versioned
- confidence bands and tie handling are deterministic
- canonical output schemas are fixed
- legacy migration policy is fixed
- report metrics separate fill and episode evidence
- causal/human-decision claims are prohibited
- CLI, exit codes, dry-run, privacy, and tests are fixed
- no implementation decision is left to Codex

P3 implementation is complete only after targeted tests pass and ChatGPT reviews the resulting source and report contract.

---

## 17. Archive condition

Archive this spec only after:

1. episode builder is implemented
2. linker v2 is implemented
3. ground-truth report uses episode-level performance
4. targeted tests pass
5. no raw/private data is in diff
6. ChatGPT reviews the compact report and source
7. P4 active spec is selected explicitly

Archive destination:

```text
chatgpt/specs/archive/20260710_manual_trade_linkage_ground_truth_pipeline.md
```


---

## 18. Post-implementation review corrections — 2026-07-10

This section overrides any conflicting earlier wording in this active spec.

### 18.1 Position-backed episodes only in P3 v1

The first implementation grouped positionless fills by calendar date and side. That does not prove one lifecycle and can merge unrelated manual trades.

P3 v1 therefore uses only:

```text
episode_source=position_backed
```

Rules:

- no position lifecycle -> no canonical episode
- do not group fills by date, side, or proximity alone
- do not emit `derived_without_position` episodes in P3 v1
- unmatched fills/orders remain unresolved supporting evidence and are counted in the compact summary
- a later explicit phase may add derived lifecycle reconstruction only after a separate deterministic contract is approved

### 18.2 Canonical input validation

Episode builder inputs must be hardened importer v2 outputs.

Required schema value for trades, orders, and positions:

```text
manual_actual_trade.v2
```

Required identity/time fields must be present and non-empty for every source row:

- trade: `actual_trade_id`, `symbol`, and a parseable canonical timestamp
- order: `actual_order_id`, `symbol`, and a parseable canonical timestamp
- position: `actual_position_id`, `symbol`, parseable open timestamp, and status-consistent close timestamp

Do not silently drop rows missing identity or required time fields.

Episode and link readers must validate both required headers and exact schema-version values.

### 18.3 Position-side resolution

Position row side remains first priority.

When position side is `unknown`:

- inspect only uniquely associated fill/order rows with explicit `side=long|short` and explicit `position_action=open|close|reduce`
- exactly one consistent explicit side -> use it
- mixed explicit sides -> episode side remains `unknown`, association becomes `ambiguous`, reason includes `side_conflict`
- buy/sell alone never resolves position side

### 18.4 Ambiguous evidence does not erase unique evidence

When an episode has both uniquely associated rows and other rows ambiguous between positions:

- keep counts, fees, and evidence from uniquely associated rows
- do not attach ambiguous rows
- set episode `association_status=ambiguous`
- include `competing_position_candidates`

Do not zero all counts merely because another row is ambiguous.

### 18.5 Zero-value preservation

Numeric zero is valid evidence.

- `0` realized PnL remains `0`
- `0` fee remains `0`
- do not use truthiness tests that convert `Decimal("0")` into blank

### 18.6 Deterministic provenance timestamp

`created_at_utc` must not use a fabricated epoch timestamp.

For episodes:

- use the maximum valid `imported_at_utc` among the position and uniquely associated rows
- blank when source provenance time is unavailable

For links:

- use the maximum valid source provenance timestamp among episode `created_at_utc` and signal review/evaluation provenance timestamps
- blank when unavailable

Repeated builds with unchanged inputs must remain byte-deterministic.

### 18.7 Entry notification classification

Entry-link classification is fail-closed.

- explicit followup/management -> excluded from entry-link candidates
- explicit defensive/watch/wait -> `defensive`
- explicit entry/attention/candidate class or recognized entry wording -> `entry_like`
- otherwise -> `unknown`

Missing classification must not default silently to `entry_like`.

Signal/outcome merging must not overwrite a non-empty value with an empty value.

Malformed non-empty signal timestamps are input errors, not silently skipped rows.

`--max-lookback-minutes` must be a positive integer.

### 18.8 Ground-truth monetary and win-rate semantics

Fill-level totals and episode-level totals remain separate.

Episode metrics:

```text
episode_gross_pnl = sum(numeric realized_pnl of closed episodes)
episode_fee_total = sum(numeric fee_total of those closed episodes)
episode_net_pnl   = episode_gross_pnl - episode_fee_total
```

Do not subtract global fill fees from episode PnL.

Episode win-rate denominator:

```text
wins + losses + breakeven
```

Closed episodes with missing/invalid realized PnL are reported as `episode_missing_pnl_count` and excluded from the denominator.

### 18.9 Actual-backed descriptive categories

Only high/medium linked rows are actual-backed aggregate inputs.

Canonical categories are:

```text
actual_positive_with_entry_like_signal
actual_negative_with_entry_like_signal
actual_positive_with_defensive_signal
actual_negative_with_defensive_signal
ambiguous_needs_review
```

Breakeven, missing PnL, unknown notification class, or any incompatible state goes to `ambiguous_needs_review`.

Side/symbol conflicts are disqualified from linked high/medium rows and belong to link-coverage diagnostics. They are not an actual-backed category.

### 18.10 Input failure and output safety

V2 report generation must fail closed when required inputs are missing, malformed, wrong-schema, or wrong-version:

- `ok=false`
- exit code `2`
- no report mutation

Episode CSV, link CSV, and report Markdown writes use same-filesystem temporary-file replacement. No direct partial write is allowed.

### 18.11 Required final regression coverage

Add explicit tests for:

1. no position rows produces zero episodes and unresolved fill/order counts
2. calendar-date grouping is not performed
3. position unknown side resolves only from explicit side plus position action
4. ambiguous competing evidence does not erase unique fill/order counts
5. zero fee and zero PnL remain zero
6. malformed or wrong-version importer input fails
7. missing IDs/timestamps fail instead of being dropped
8. malformed signal timestamp fails
9. non-positive lookback fails
10. unknown notification class does not default to entry-like
11. non-empty signal outcome values survive empty review fields
12. episode net PnL uses episode-associated fee only
13. missing episode PnL is excluded from win-rate denominator
14. negative defensive evidence uses the corrected category
15. missing/wrong-version report inputs fail without output mutation
16. new episode/link/report CLI routes are exercised through subprocess
17. atomic write failure leaves the prior generated output intact
