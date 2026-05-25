# 20260526 自動トレード高速到達のための設計整理

## 目的

自動トレードへ早く到達するために、現時点で何を急ぐべきか、何を急いではいけないかを分離する。

結論として、いま急ぐべきなのは `trade_execution_gate` の緩和ではなく、紙候補の品質ガードである。

## 読んだ正本・レポート

- `運用資料/ChatGPTプロジェクト設定.md`
- `運用資料/NEXT_TASK.md`
- `運用資料/reports/report_hub_latest.md`
- `運用資料/reports/feedback_daily_sync_20260526.md`
- `運用資料/reports/analysis/market_map_effectiveness_20260526.md`
- `運用資料/reports/analysis/operational_focus_20260526.md`
- `運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md`
- `chatgpt/README.md`
- `chatgpt/analysis/20260526_entry_sl_tp_wait_redesign.md`
- `chatgpt/analysis/20260526_trend_flip_confirmed_up_reassessment.md`

## 確認した現在ブランチ

`運用資料/NEXT_TASK.md` の記載に従い、現在の作業ブランチは `ver02.6-v2` とする。

remote の最新 branch 一覧や `main` からは判断しない。

## 現在の詰まり

### 1. 実弾直前の gate はまだ pass していない

- `trade_execution_gate=pass` は 0 件
- `paper_orders planned` も 0 件
- `phase1_active=true` は出始めたが、正式な実行候補としてはまだ不足

したがって、実弾発注・取引所API送信・秘密鍵連携はまだ対象外にする。

### 2. 紙候補の失敗が SL 側に偏っている

`paper_positions` では、主な失敗が `missed_opportunity` より `sl_hit` に寄っている。

これは「もっと早く入る」よりも、次の切り分けを優先すべき状態を示す。

- entry が早すぎる
- wait が高すぎる
- execution が足りない
- long / trend_flip_confirmed_up 側が弱い
- SL がノイズに対して狭い可能性がある

### 3. long と上方向転換系がまだ弱い

`trend_flip_confirmed_up` は件数が増えたが、強評価へ戻す材料にはならない。

特に紙候補側では `trend_flip_confirmed_up` を含む候補が `sl_hit` に偏っており、long 方向の自動化を急ぐと損失型を増やす可能性が高い。

## 自動トレードへ早く近づくための方針

## 方針 A: 実弾 gate はまだ緩めない

現時点では `trade_execution_gate` を直接緩めない。

理由:

- `paper_orders planned=0` のまま実弾 gate を緩めると、検証済みの候補ではなく、未精査の watch / opportunity を実弾側へ近づけてしまう。
- `sl_hit` 偏重が残っており、品質改善前に候補を増やすと負け型が増える。
- `Phase 1B-lite` は観測レーンであり、正式 `Phase 1B` ではない。

## 方針 B: まず paper opportunity の品質ガードを入れる

Codex に渡す第一仕様は、紙候補の品質ガードにする。

対象は `src/trade/opportunity_gate.py` を中心に、候補化理由と block reason を明示する設計とする。

### 追加する品質ガード候補

1. `paper_quality_high_wait_block`
   - 条件: `wait >= 80`
   - 理由: `wait>=80` は `sl_hit` 偏重が強く、平均Rも弱い

2. `paper_quality_low_execution_block`
   - 条件: `execution < 20`
   - 理由: 低 execution 群は `sl_hit` が多い

3. `paper_quality_long_wait_block`
   - 条件: `bias/side が long` かつ `wait >= 60` かつ `execution < 25`
   - 理由: long と高 wait の組み合わせが弱い

4. `paper_quality_trend_flip_up_block`
   - 条件: long 候補かつ `trend_flip_confirmed_up` を含む
   - 理由: 上方向転換系は強評価へ戻さない

## 方針 C: SL/TP 数値はいったん触らない

SL が狭すぎる可能性はあるが、第一弾では SL/TP 倍率を変更しない。

理由:

- `sl_eval=too_tight` はあるが、entry が早い失敗と wait 劣化の失敗が混ざっている。
- 先に SL を広げると、損失幅だけが増えるリスクがある。
- 品質ガード後に残る `sl_hit` だけを見た方が、SL 再設計の精度が上がる。

## 方針 D: market_map の下方向優位を壊さない

`support_to_resistance_flip` と `trend_flip_confirmed_down` は相対的に有効である。

ただし、紙候補化の entry/wait 条件が粗いため、market_map flag 自体を弱めるのではなく、候補化する段階で quality guard を入れる。

## Codex へ渡す確定仕様

次の仕様書を作成する。

`chatgpt/specs/active/20260526_entry_wait_trend_flip_quality_guard.md`

この仕様は「自動トレード実装」ではなく「自動トレードに進むための紙候補品質改善」である。

## 成功条件

第一弾の成功条件は、候補数を増やすことではない。

成功条件は以下。

1. 弱い候補が `paper_orders planned` や `formal_execution_candidate` に近づかない
2. quality block reason が CSV / report で追跡できる
3. 次回 daily-sync / paper diagnostics で block 件数を確認できる
4. `sl_hit` 比率が下がるか、少なくとも弱い long / high wait / low execution が分離できる
5. `missed_opportunity` が過剰に増えていないか確認できる

## 次フェーズ判断

この品質ガードを入れた後、次の条件を見て Phase 1B / 自動トレード直前へ進めるか判断する。

- `trade_execution_gate=pass` が自然に出るか
- `paper_orders planned` が少数でも出るか
- planned 候補の `sl_hit` 偏重が改善しているか
- `support_to_resistance_flip` など有効 flag が残っているか
- long / trend_flip_confirmed_up が引き続き弱いなら long 側の gate を別扱いにするか

## 結論

自動トレードを早める最短ルートは、実弾 gate をいきなり緩めることではない。

いまは紙候補の品質ガードを入れて、失敗型を候補化前に分離する。これにより、次の daily-sync で「実弾化してよい候補」と「通知・観測に留める候補」を分けられるようにする。
