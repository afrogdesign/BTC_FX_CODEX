# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-FIX-2`
- mode: `BOUNDED CODEX FIX`
- task_type: `PYTHON SOURCE / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-FIX-1`
- previous_status: `FIX-1 COMMITTED / CHATGPT REVIEW FOUND TWO REMAINING CONTRACT DEFECTS`

## Goal

P5 classifierの残存契約逸脱だけを修正する。P6へ進まない。active specはarchiveしない。

Active spec:

```text
chatgpt/specs/active/20260710_manual_operator_classifier_offline.md
```

Reported fix commit:

```text
5d505be
```

## Fix

### 1. Blank data qualityの誤STOP

Current wrong behavior:
- `data_quality_flag`がblankでも`STOP_OR_EXIT`になる。

Required behavior:
- STOPのdata-quality条件は、active specどおり「non-empty and not equal to ok」のときだけ。
- blank qualityはA/Bを満たさないが、join、side、entry、shadow、RR、candidate stateが完全なら`C_WATCH_ZONE`。
- blank qualityをSTOPまたはBにしない。

Required tests:
- blank quality => C
- blank quality => not STOP
- non-empty non-ok quality => STOP

### 2. Numeric canonicalization / validation漏れ

Current wrong behavior:
- `stop_loss`、`tp1`、`tp2`、`nearest_major_support`、`nearest_major_resistance`がfingerprint Decimal normalizationとinvalid-numeric validationの対象から漏れている。

Required behavior:
- active spec記載のcandidate/signal numeric required columnsを一つの明示的なfield setで管理し、fingerprint normalizationとvalidationで共用する。
- non-empty malformedまたはnon-finite valueはexit 2。
- numeric-equivalent textは同一fingerprintとする。

Required tests:
- `stop_loss` / `tp1` / `tp2`の`1`と`1.0`はexact duplicate
- nearest support/resistanceの`1`と`1.0`はexact duplicate
-各漏れfieldのmalformed valueはexit 2

### 3. Fix-1で要求済みだが不足しているregression tests

追加する:
- ambiguous event remains ambiguous with missing candidate context
- ambiguous event remains ambiguous with missing signal context
- semicolon/comma/pipe/JSON-list forms produce identical fingerprints
- simultaneous STOP conditions retain all applicable reason codes
- setup-side mismatch uses `side_mismatch` rather than `missing_entry_definition`

## Allowed read

```text
AGENTS.md
docs/operations/ai-orchestration/NEXT_ACTION.md
chatgpt/specs/active/20260710_manual_operator_classifier_offline.md
src/feedback/manual_operator_classifier.py
tests/test_manual_operator_classifier.py
```

## Allowed edit

```text
src/feedback/manual_operator_classifier.py
tests/test_manual_operator_classifier.py
docs/operations/ai-orchestration/NEXT_ACTION.md
```

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

git diff --check -- \
  src/feedback/manual_operator_classifier.py \
  tests/test_manual_operator_classifier.py \
  docs/operations/ai-orchestration/NEXT_ACTION.md
```

## Completion transition

validation通過後、同じcommit内で`NEXT_ACTION.md`を次へ遷移する。

```text
current_work_id: BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-REVIEW-CHECKPOINT-2
mode: REVIEW_ONLY
previous_status: P5 FIX-2 COMMITTED / PUSH NONE
```

## Stop / Safety / Git

- branch違い、spec判断が必要、許可外file編集が必要、task外test failure、secret/private/generated/raw data混入時は停止
- production gate、scoring、threshold、notification、runtime、launchd、API、account/order endpoint、FORMAL_GO、automatic orderは禁止
- frozen runtime repoへ触れない
- unrelated差分を触らず、reset / checkout / delete / stash apply/pop/dropをしない
- task fileだけstage、pushなし

## Commit

```text
fix: close remaining offline classifier gaps
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
