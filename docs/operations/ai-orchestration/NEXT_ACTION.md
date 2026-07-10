# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-REVIEW-CHECKPOINT`
- mode: `REVIEW_ONLY`
- task_type: `CHATGPT SOURCE / TEST / CONTRACT REVIEW`
- previous_work_id: `BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-FIX-1`
- previous_status: `P5 FIX-1 COMMITTED / PUSH NONE`

## Current goal

P5 classifierの修正済みsourceとtestsをChatGPTがreviewする。

P5 remains active. P5 is not yet archived. P6 has not started.

次 actionはChatGPT review of the corrected source and tests。Codex review-only execution is not required unless ChatGPT creates a new bounded task.

P6へ進まない。P5 active specはarchiveしない。

Reported implementation commit:

```text
2c5be02f1095331ef9f2cae0cda13079ed2a0201
```

Active spec:

```text
chatgpt/specs/active/20260710_manual_operator_classifier_offline.md
```

## Required fixes

### 1. Decimal and RR correctness

- Decimal parserはfinite valueだけを有効とし、NaN / Infinity / -Infinityをinvalid inputまたはinvalid threshold、exit 2にする。
- RR priorityでDecimal zeroを欠落扱いしない。
- `rr_zone_mid_tp1=0`は`rr_current_tp1`やsignal RRへfallbackせず0を保持する。
- TP2も同様にzeroを保持する。

### 2. Event-time join integrity

- matched candidateの`source_signal_id`がeventの`source_signal_id`と一致しない場合はinput error、exit 2。
- invalid event sideはinternal errorへ落とさずinput error、exit 2。
- ambiguous groupingはcandidate/signal join欠落より先に`ambiguous_grouping`として可視化する。

### 3. B classification contract

- Bは`data_quality_flag == ok`を必須にする。
- Bはshort/longとも`primary_setup_status in ready, watch`を必須にする。
- long Bは従来どおり`primary_setup_status == ready`を追加必須にする。
- blankまたはunknown execution gateはBにしない。
- pass-gate exceptionはA不成立かつgate以外のB条件がすべて成立した場合だけとし、`formal_evidence_incomplete`を付ける。

### 4. Canonical fingerprint normalization

Required-column fingerprintで次をcanonical Decimalとして扱う。

```text
candidate:
entry_price
entry_zone_low
entry_zone_high
stop_loss
tp1
tp2
rr_current_tp1
rr_current_tp2
rr_zone_mid_tp1
rr_zone_mid_tp2

signal:
current_price
confidence_direction_shadow
confidence_execution_shadow
confidence_wait_shadow
long_rr
short_rr
nearest_major_support
nearest_major_resistance
```

List-like fieldsはsupported representationをcanonical token列へ正規化する。

```text
trade_execution_blockers
phase1b_lite_reasons
opportunity_reasons
no_trade_flags
warning_flags
risk_flags
```

最低限、semicolon、comma、pipe、JSON list representationを同じsorted unique semicolon formへ正規化する。

追加列はfingerprintへ含めない。

### 5. Output row contract

Classification CSV各行へ、実際に使用した10個のthreshold値を全て記録する。

```text
short_direction_min
short_execution_min
short_wait_max
short_tp1_rr_min
short_tp2_rr_min
long_direction_min
long_execution_min
long_wait_max
long_tp1_rr_min
long_tp2_rr_min
```

次をnormalized semicolon tokenとして出力する。

```text
warning_codes <- warning_flags
risk_flags
no_trade_flags
trade_execution_blockers
```

STOP条件が複数同時成立する場合、該当するreason codeを全てdeterministic orderで保持する。

### 6. Summary and Markdown contract

JSON summaryへ次を追加する。

```text
warning_token_counts
risk_token_counts
no_trade_token_counts
```

Markdownにactive specで必須の全sectionを含める。

```text
Purpose
Input Status
Method and No-Leakage Boundary
Threshold Snapshot
Classification Coverage
Class Distribution
Side Breakdown
Regime Breakdown
Setup-Family Breakdown
Existing Gate Comparison
Warnings and Risks
Limitations
Safety Boundary
```

Markdownへ明示する。

- offline hypothesis only
- not FORMAL_GO
- no automatic order
- human decides manually
- A/B/C/STOP does not replace existing gates
- thresholds are comparison values, not production settings
- no profitability evaluation

### 7. Tests

既存testを維持し、少なくとも次を追加する。

- zero `rr_zone_mid_tp1` is retained and does not fallback
- zero `rr_zone_mid_tp2` is retained and does not fallback
- NaN and Infinity numeric input exit 2
- NaN and Infinity threshold exit 2
- candidate source signal mismatch exits 2
- invalid side exits 2 without traceback
- ambiguous event remains ambiguous when candidate/signal context is missing
- blank data quality does not produce B
- short setup status outside ready/watch does not produce B
- numeric-equivalent required fields such as `1` and `1.0` are exact duplicates, not conflicts
- comma/pipe/semicolon/JSON-list token forms normalize consistently
- CSV rows contain all threshold snapshot fields
- warning/risk/no-trade token counts are correct
- Markdown contains every required section and safety statement
- multiple simultaneous STOP reasons are retained

## Allowed edit

```text
src/feedback/manual_operator_classifier.py
tests/test_manual_operator_classifier.py
docs/operations/ai-orchestration/NEXT_ACTION.md
```

`tools/log_feedback.py`はCLI配線に修正が必要な場合だけ編集可。既存command wiringのrefactorは禁止。

Active specは原則編集しない。実装との不整合ではなくspec自体の明白な誤記が見つかった場合だけ停止して報告する。

## Validation

```bash
./.venv312/bin/python -m unittest \
  tests.test_manual_operator_classifier \
  tests.test_manual_scenario_normalizer \
  tests.test_manual_decision_events \
  tests.test_manual_scenario_coverage \
  tests.test_manual_trade_episode_builder \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report \
  tests.test_mexc_actual_trade_importer
```

```bash
git diff --check -- \
  src/feedback/manual_operator_classifier.py \
  tests/test_manual_operator_classifier.py \
  tools/log_feedback.py \
  docs/operations/ai-orchestration/NEXT_ACTION.md
```

## Completion transition

修正とvalidationが通った場合、同じcommit内で`NEXT_ACTION.md`をP5 review checkpointへ遷移させる。

```text
current_work_id: BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-REVIEW-CHECKPOINT
mode: REVIEW_ONLY
previous_status: P5 FIX-1 COMMITTED / PUSH NONE
```

次taskはChatGPTによるsource/test実体レビューであり、P6 implementationではない。

## Prohibited

- class、priority、default threshold値の変更
- production gate再計算
- production source edit
- notification / runtime / launchd edit
- API / account / order / secret access
- generated output commit
- raw exchange export commit
- `paper_positions.csv` integration
- frozen runtime repo access
- P6 implementationまたはspec作成

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
