# 20260526 entry / SLTP / wait-execution redesign

## 目的

`sl_hit` 偏重の主因を、`entry 発火条件`、`SL/TP 条件`、`wait / execution 抑制条件` に分けて再設計するための分析メモ。

この更新では、実弾 gate 緩和ではなく、紙候補の品質ガードを優先する。

## この文書が扱う範囲

- `market_map_opportunity` の紙ポジション診断
- `long` / `wait>=60` / `wait>=80` / `execution<20` の弱点整理
- AI事後評価の `too_tight` / `too_early` / `tf_15m_eval=poor` の扱い
- `trend_flip_confirmed_up` を強評価へ戻さない前提での紙候補抑制

この文書は分析メモだが、今回の判断は Codex 用仕様書へ上げられる粒度まで固める。

## 現在の根拠

### 主要レポート

- `運用資料/reports/feedback_daily_sync_20260526.md`
- `運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md`
- `運用資料/reports/analysis/operational_focus_20260526.md`
- `運用資料/reports/analysis/market_map_effectiveness_20260526.md`

### 主要数値

- `paper_positions closed=19 / sl_hit=12 / missed_opportunity=5`
- `market_map_opportunity=97件 / 平均R 0.36 / 簡易PF 1.97`
- `long=18件 / 平均R -0.51 / 簡易PF 0.29 / sl_hit=15`
- `wait>=60=39件 / 平均R -0.16 / 簡易PF 0.74`
- `wait>=80=7件 / 平均R -0.84 / sl_hit=6`
- `execution<20=44件 / 平均R -0.02 / sl_hit=29`
- `late_wait_sl=20 / trend_flip_long_sl=10 / other_sl=18`
- `trend_flip_confirmed_up=32件 / 勝率41.2% / wrong_rate28.1% / MFE24h2.50 / MAE24h10.85`
- 紙ポジション診断では `trend_flip_confirmed_up=7件` がすべて `sl_hit`

### AI事後評価の補助根拠

- `sl_eval=too_tight` が SL 再設計候補を押し上げている
- `user_verdict=too_early` と `tf_15m_eval=poor` が entry 遅延候補を押し上げている
- `misleading_entry_like_wording=yes` は通知文面の中立化候補

## いま分かっていること

1. `long`、高 wait、低 execution が混ざって悪化しているため、1 つの gate 緩和/抑制でまとめて触るべきではない。
2. `sl_hit` は「SL が狭い」のか「entry が早い」のか「待ちすぎ後の劣化 entry」なのかを分けて設計する必要がある。
3. AI事後評価は日常判断の主系になったので、設計案にも `too_tight` / `too_early` を直接使ってよい。
4. `trend_flip_confirmed_up` は件数こそ増えたが、強評価へ戻す根拠にはならない。
5. 現時点で優先すべきは、`paper_order_status=planned` を増やすことではなく、弱い紙候補を予定化しないことである。

## 設計判断

### 1. entry 発火条件

`execution<20` は紙候補の予定化を抑制する。

理由:

- `execution<20=44件 / 平均R -0.02 / sl_hit=29` で、低 execution 群は `sl_hit` が多い。
- ここを gate 緩和すると、紙候補を増やしても失敗型を増幅する可能性が高い。

実装方針:

- `execution<20` は `paper_quality_low_execution_block` として記録する。
- 原則として `paper_order_status=planned` にしない。
- 既存コードに明確な例外がある場合、Codex は勝手に例外を広げず、既存挙動を保ちながら理由ログを追加する。

### 2. wait / execution 抑制条件

`wait>=80` は hard 寄りの抑制条件にする。

理由:

- `wait>=80=7件 / 平均R -0.84 / sl_hit=6` で明確に悪い。
- `late_wait_sl=20` が出ており、待ちすぎ後の劣化 entry が疑われる。

実装方針:

- `wait>=80` は `paper_quality_high_wait_block` として記録する。
- `paper_order_status=planned` にしない。
- watch / 観測通知は残してよい。

`wait>=60` は単独 hard block にしない。

理由:

- `wait>=60=39件 / 平均R -0.16 / 簡易PF 0.74` と弱いが、`wait>=80` ほど決定的ではない。
- ただし `long` と `低 execution` が重なる場合は明確に弱い。

実装方針:

- `long` 系かつ `wait>=60` かつ `execution<25` を `paper_quality_long_wait_block` として記録する。
- `paper_order_status=planned` にしない。

### 3. SL / TP 条件

今回の第一弾では SL / TP の数値変更は行わない。

理由:

- `sl_eval=too_tight` は補助根拠として重要だが、現時点では「SL が狭い」のか「entry が早い」のか「待ちすぎ entry」なのかが混ざっている。
- SL を広げるだけだと、損失幅だけが増える可能性がある。
- まず弱い entry を抑制し、その後に `too_tight` 優勢群だけを別診断する方が安全。

実装方針:

- SL / TP の倍率・距離・RR 計算は今回触らない。
- 次回診断で、抑制後にも残る `sl_eval=too_tight` 群だけを SL 再設計候補にする。

### 4. `trend_flip_confirmed_up` の扱い

`trend_flip_confirmed_up` は強評価へ戻さない。

理由:

- `trend_flip_confirmed_up=32件` まで増えたが、勝率 `41.2%`、wrong_rate `28.1%`、平均 `MFE24h=2.50 / MAE24h=10.85` で弱い。
- 紙ポジション診断では `trend_flip_confirmed_up=7件` がすべて `sl_hit`。

実装方針:

- `trend_flip_confirmed_up` 単独で score を大きく押し上げない。
- `trend_flip_confirmed_up` 単独で `trade_execution_gate=pass` に近づけない。
- `trend_flip_confirmed_up` 単独で `paper_order_status=planned` にしない。
- long 候補かつ `trend_flip_confirmed_up` を含む場合は `paper_quality_trend_flip_up_block` を出す。
- 通知文言は「上方向転換の可能性」程度に抑え、ロング推奨に見える表現を避ける。

## Codex に渡す仕様化方針

今回 Codex に渡す仕様は、次の名前で作成する。

- `chatgpt/specs/active/20260526_entry_wait_trend_flip_quality_guard.md`

仕様書には次を含める。

- 目的
- 対象ブランチ `ver02.6-v2`
- 変更範囲
- 実装内容
- 検証方法
- 完了条件
- 注意事項

## Codex に渡す前に固めた条件

- `entry`、`SL/TP`、`wait/execution` の3軸を分けた。
- 根拠数値を `20260526` の最新レポートに限定した。
- `trade_execution_gate` 緩和ではなく、紙候補品質の改善であることを明記した。
- SL / TP 数値変更は今回見送る。
- `trend_flip_confirmed_up` は強評価へ戻さない。

## 次回見る数値

実装後の次回 daily-sync / analysis では以下を確認する。

- `paper_quality_high_wait_block` 件数
- `paper_quality_low_execution_block` 件数
- `paper_quality_long_wait_block` 件数
- `paper_quality_trend_flip_up_block` 件数
- 抑制後の `paper_order_status=planned` 件数
- 抑制後の `sl_hit` 比率
- 抑制によって `missed_opportunity` が増えすぎていないか
- `long` と `trend_flip_confirmed_up` の改善/悪化
