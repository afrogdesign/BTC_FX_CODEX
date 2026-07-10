# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-LINKAGE-PIPELINE-SPEC`
- mode: `CHATGPT-DESIGN / DOCS-ONLY`
- task_type: `ACTIVE-SPEC-CREATION`
- previous_work_id: `BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-HARDENING`
- previous_status: `P2 COMPLETE / REVIEWED / LOCAL COMMITS REPORTED / NOT PUSHED`

## Current goal

既存のmanual trade linkerとground-truth reportを、hardened importerのschemaとmanual trading practicality objectiveに照らして再設計するactive specを作る。

P3はgreenfield implementationではない。

Existing source:

```text
tools/log_feedback.py
  link_manual_trades_to_signals()
  build_manual_trade_signal_link_rows()
  score_manual_trade_signal_link()
  build_manual_trade_ground_truth_report()
  summarize_manual_actual_trade_performance()
  calibrate_manual_trade_proxy_vs_actual()
```

Existing tests:

```text
tests/test_manual_trade_signal_linker.py
tests/test_manual_trade_ground_truth_report.py
```

## Completed P2

Importer hardening is complete and reviewed.

Archived spec:

```text
chatgpt/specs/archive/20260710_manual_actual_trade_importer.md
```

Reviewed implementation:

```text
src/feedback/manual_actual_trade_importer.py
tools/log_feedback.py
tests/test_mexc_actual_trade_importer.py
```

Reported local commits:

```text
d8ce83b  Harden manual actual trade importer
01746c1  Finalize manual trade importer safety
c9b7715  Close manual importer summary contract
```

Reported validation:

```text
./.venv312/bin/python -m unittest \
  tests.test_mexc_actual_trade_importer \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report

pass: 35 tests

targeted git diff --check: pass
```

Push remains `none`.

## P3 design questions that must be resolved

The current linker/report predates the hardened importer and must not be assumed semantically correct merely because compatibility tests pass.

The active spec must resolve at least the following.

### 1. Evaluation unit

Current code treats each row of `manual_actual_trades.csv` as an actual trade.

The importer defines this file as fill-level evidence. Therefore the P3 spec must decide the canonical evaluation unit among:

```text
fill
order
position lifecycle
manual trade episode
```

Do not report fill count as human trade count without an explicit aggregation contract.

### 2. Side compatibility

The hardened importer separates:

```text
side
transaction_side
position_action
```

A source direction such as `BUY` may normalize to:

```text
side=unknown
transaction_side=buy
position_action=unknown
```

The existing linker mainly reads `side`. The P3 spec must define deterministic side resolution and must not infer long/short from buy/sell when the position action is unknown.

### 3. Link target

The spec must decide whether signals link to:

```text
fills
orders
positions
manual trade episodes
```

Position lifecycle or an explicitly defined episode is preferred for human-trade evaluation. Fill-level rows may remain supporting evidence.

### 4. Cross-category association

Do not assume MEXC `UID` is an order ID, position ID, or cross-category event ID.

The spec must define association using only justified evidence such as:

```text
symbol
time window
position side
transaction side
position action
open/close timestamps
order/fill status
```

Ambiguous association must remain ambiguous and require review.

### 5. Signal candidate window

The current default is a prior-signal window of 240 minutes.

The spec must define:

- whether only signals before the trade/position open are eligible
- maximum lookback
- same-timestamp handling
- multiple notifications for one position
- notification after entry
- followup notification handling
- tie and ambiguity rules

No threshold change is approved merely because the current value is 240 minutes.

### 6. Link confidence

The existing score uses time, side, and BTC context.

The spec must define:

- evidence components
- disqualifying conflicts
- confidence bands
- deterministic tie behavior
- manual-review state
- versioned link method

A low-confidence or ambiguous link must not be promoted to actual-backed strategy evidence.

### 7. Ground-truth metrics

The current report calculates trade count, win rate, realized PnL, and fee totals from fill-level rows.

The spec must separate:

```text
fill-level monetary totals
position/episode-level win-loss metrics
link coverage
actual-backed evidence
proxy-only evidence
human-decision evidence
```

Avoided loss, missed opportunity, watch, and skip cannot be inferred from exchange export alone.

### 8. Human decision boundary

P3 may use exchange actuals and notification evidence only.

P3 must not claim to know:

- why the human entered
- whether a notification caused the entry
- whether the human intentionally skipped
- whether a loss was consciously avoided
- whether an opportunity was consciously missed

Those require the P4 human decision-event schema.

### 9. Canonical outputs

The spec must decide whether to retain, migrate, or deprecate:

```text
logs/csv/manual_trade_signal_links.csv
```

Any new output must have:

- schema version
- deterministic ID
- source entity ID
- signal ID
- link method version
- confidence
- reason codes
- ambiguity status
- timestamp delta
- side compatibility result
- privacy-safe reporting

### 10. Migration and compatibility

Existing reports and tests must not silently reinterpret old link rows as the new contract.

The spec must define:

- legacy schema detection
- migration or rebuild policy
- output overwrite/merge behavior
- dry-run behavior
- CLI contract
- exit codes
- targeted tests

## Required read

Read only as needed:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `docs/operations/ai-orchestration/CURRENT_STATE.md`
4. `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
5. `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
6. `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
7. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
8. `chatgpt/specs/archive/20260710_manual_actual_trade_importer.md`
9. linker/report source functions only
10. matching linker/report tests only

Do not perform broad repo exploration.

## Expected output

```text
chatgpt/specs/active/20260710_manual_trade_linkage_ground_truth_pipeline.md
```

P3 source implementation must not begin until this active spec is created and reviewed.

## Hard boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no API / secret / private / account / order endpoint
- no runtime restart
- no launchd modification
- no notification behavior change
- no gate / threshold / scoring change
- no production tuning
- no raw exchange export read or commit
- no `paper_positions.csv` integration

## Validation

P3 spec task is docs-only:

```text
active spec path exists
required design questions are resolved
git diff --check on task docs only
no source/test/generated file changed
```

## Later route

```text
P3 linker / ground-truth pipeline spec and hardening
→ P4 scenario identity, coverage, and human decision-event schema
→ P5 offline A/B/C/STOP classifier
→ P6 historical replay
→ P7 shadow surface
→ P8 human manual trial
→ P9 evidence-backed tuning review
```
