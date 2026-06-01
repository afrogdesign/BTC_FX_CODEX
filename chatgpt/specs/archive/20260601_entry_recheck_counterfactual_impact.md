# entry recheck counterfactual impact 仕様

## 作業番号

`BTCFX-20260601-11`

## 目的

`paper_entry_sl_wait_redesign` report の `entry recheck reason impact` を、保存済み `opportunity_reasons` だけでなく、BTCFX-08 の recheck 条件を過去データへ後付け再計算した counterfactual として評価できるようにする。  
新しい standalone report は増やさず、既存 `paper_entry_sl_wait_redesign` builder を拡張する。

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

必要なら読むだけ:

- `src/trade/opportunity_gate.py`
- `tests/test_phase1_trade_plans.py`

## 実装方針

`build_paper_entry_sl_wait_redesign_report(...)` 内で、`market_map_opportunity` rows に対して BTCFX-08 の recheck 条件を後付け再計算する。

保存済み `opportunity_reasons` は logged impact として残してよい。  
追加で以下の counterfactual セクションを出す。

```md
## entry recheck counterfactual impact
```

## 集計 group

- `entry_recheck_required_high_wait`
- `entry_recheck_required_low_execution`
- `entry_recheck_required_long_weakness`
- `entry_recheck_required_trend_flip_up`
- `price_distance_missing`
- `entry_recheck_any`
- `entry_recheck_none`
- `market_map_opportunity 全体`

## 指標

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

- `insufficient_n`
- `risk_confirmed`
- `collateral_damage_risk`
- `monitor_only`

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

## 再計算ルール

BTCFX-08 と同じ意味にする。

- `entry_recheck_required_high_wait`
  - `wait>=60`
  - かつ high wait keep 条件を満たさない
- `entry_recheck_required_low_execution`
  - `execution<24`
  - かつ low execution keep 条件を満たさない
- `entry_recheck_required_long_weakness`
  - `side=long`
  - かつ long keep 条件を満たさない
- `entry_recheck_required_trend_flip_up`
  - `side=long`
  - `trend_flip_confirmed_up` を含む
  - かつ trend_flip_up keep 条件を満たさない
- `price_distance_missing`
  - setup reason が `entry_zone_not_reached` または `near_entry_zone_waiting_trigger`
  - かつ既存 distance 値が空

`src/trade/opportunity_gate.py` の helper を直接 import できるなら使う。  
難しければ `tools/log_feedback.py` 側に同等の private helper を置く。  
ただし意味がズレないよう、テストで確認する。

## interpretation への必須記載

- このセクションは counterfactual であり、過去実行時に実際に出た reason ではない。
- logged impact が 0件でも、counterfactual impact で過去候補への影響を評価する。
- entry recheck reason は paper candidate 品質改善のための抑制理由であり、実弾 gate ではない。
- `trade_execution_gate` / `phase1b_lite_gate` は変更しない。
- `price_distance_missing` は非blocking reason として扱う。
- B/C 単独 soft risk は hard blocker 化しない。
- `trend_flip_confirmed_up` は強評価へ戻さない。
- この集計は Phase 1B 昇格材料ではなく、次の再設計判断材料。

## テスト要件（次回）

`tests/test_log_feedback.py` に以下を追加する。

- `## entry recheck counterfactual impact` が出る
- counterfactual で `entry_recheck_required_high_wait` が集計される
- counterfactual で `entry_recheck_required_low_execution` が集計される
- counterfactual で `entry_recheck_required_long_weakness` が集計される
- counterfactual で `entry_recheck_required_trend_flip_up` が集計される
- counterfactual で `price_distance_missing` が集計される
- `entry_recheck_any` / `entry_recheck_none` が出る
- logged reason が空でも counterfactual 側は 0件にならないケースを確認
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

- `paper_entry_sl_wait_redesign` に `entry recheck counterfactual impact` が追加される
- logged impact と counterfactual impact の違いが明記される
- 新しい standalone report は増やさない
- `trade_execution_gate` / `phase1b_lite_gate` は変更しない
- B/C 単独 soft risk は hard blocker 化しない
- active spec は実装後に `archive` へ移動する
