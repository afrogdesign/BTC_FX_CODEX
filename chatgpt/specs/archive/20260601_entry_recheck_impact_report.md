# entry recheck reason impact report 仕様

## 作業番号

`BTCFX-20260601-09`

## 目的

既存 `paper_entry_sl_wait_redesign` report に、BTCFX-20260601-08 で追加した entry recheck reason の影響確認セクションを追加する。  
新しい standalone report は増やさず、既存 builder を拡張する。

## 対象ブランチ

`ver02.6-v2`

## 今回の扱い

- 今回は仕様作成のみ。実装は次回。
- `trade_execution_gate` / `phase1b_lite_gate` は変更しない。
- B/C 単独 soft risk は hard blocker 化しない。
- `trend_flip_confirmed_up` は強評価へ戻さない。

## 次回実装対象

- `tools/log_feedback.py`
- `tests/test_log_feedback.py`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260601.md`
- `運用資料/reports/report_hub_latest.md`
- `運用資料/NEXT_TASK.md`

## 追加する report セクション

`paper_entry_sl_wait_redesign_20260601.md` に次のセクションを追加する。

```md
## entry recheck reason impact
```

### 集計グループ

- `entry_recheck_required_high_wait`
- `entry_recheck_required_low_execution`
- `entry_recheck_required_long_weakness`
- `entry_recheck_required_trend_flip_up`
- `price_distance_missing`
- `entry_recheck_any`
- `entry_recheck_none`
- `market_map_opportunity 全体`

### 指標

- `group`
- `count`
- `entered_count`
- `sl_hit`
- `sl_hit_rate`
- `tp2_hit`
- `tp2_hit_rate`
- `timeout`
- `missed_opportunity`
- `entry_not_reached`
- `avg_R`
- `judgement`

## judgement 仕様

### 判定値

- `risk_confirmed`
- `collateral_damage_risk`
- `monitor_only`
- `insufficient_n`

### 条件

- `insufficient_n`
  - `count < 10`
  - または `entered_count < 10`
- `risk_confirmed`
  - `entered_count >= 10`
  - `sl_hit_rate >= 70%`
  - `tp2_hit_rate < 20%`
- `collateral_damage_risk`
  - `tp2_hit_rate >= 20%`
  - または `missed_opportunity / count >= 40%`
- `monitor_only`
  - 上記以外

### 優先順位

`insufficient_n > collateral_damage_risk > risk_confirmed > monitor_only`

## interpretation への必須記載

- entry recheck reason は paper candidate 品質改善のための抑制理由であり、実弾 gate ではない。
- `trade_execution_gate` / `phase1b_lite_gate` は変更しない。
- `price_distance_missing` は非blocking reason として扱う。
- B/C 単独 soft risk は hard blocker 化しない。
- `trend_flip_confirmed_up` は強評価へ戻さない。
- この集計は次の再設計判断材料であり、即 Phase 1B 昇格材料ではない。

## 実装方針（次回）

- `build_paper_entry_sl_wait_redesign_report(...)` を拡張し、既存 report 本文に `entry recheck reason impact` を挿入する。
- `opportunity_reasons` 由来で reason 別グルーピングし、`entry_recheck_any` / `entry_recheck_none` / `market_map_opportunity 全体` も同時に出力する。
- `price_distance_missing` は非blocking reason のため、`opportunity_gate=pass` ケースを含んだ集計になる前提で扱う。
- 既存 CLI `build-paper-entry-sl-wait-redesign-report` と alias `--paper-entry-sl-wait-redesign` の導線は維持する。
- standalone report は追加しない。

## テスト要件（次回）

`tests/test_log_feedback.py` に次を追加する。

- `paper_entry_sl_wait_redesign` report に `## entry recheck reason impact` が出る
- `entry_recheck_required_high_wait` が集計される
- `entry_recheck_required_low_execution` が集計される
- `entry_recheck_required_long_weakness` が集計される
- `entry_recheck_required_trend_flip_up` が集計される
- `price_distance_missing` が集計される
- `entry_recheck_any` / `entry_recheck_none` が出る
- `judgement` が出る
- 既存 `--paper-entry-sl-wait-redesign` alias は壊さない

## 検証コマンド（次回）

```bash
./.venv312/bin/python -m unittest tests.test_log_feedback
./.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback
./.venv312/bin/python tools/log_feedback.py --paper-entry-sl-wait-redesign
./.venv312/bin/python tools/log_feedback.py --report-hub
git diff --check
```

## 完了条件（次回）

- `paper_entry_sl_wait_redesign` に `entry recheck reason impact` が追加される
- 新しい standalone report は増やさない
- `trade_execution_gate` / `phase1b_lite_gate` は変更しない
- B/C 単独 soft risk は hard blocker 化しない
- active spec は実装後に `archive` へ移動する
