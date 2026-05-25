# 20260526 entry / SLTP / wait-execution redesign

## 目的

`sl_hit` 偏重の主因を、`entry 発火条件`、`SL/TP 条件`、`wait / execution 抑制条件` に分けて再設計するための分析メモ。

## この文書が扱う範囲

- `market_map_opportunity` の紙ポジション診断
- `long` / `wait>=60` / `wait>=80` / `execution<20` の弱点整理
- AI事後評価の `too_tight` / `too_early` / `tf_15m_eval=poor` の扱い

この文書では仕様確定までは行わない。Codex に渡す前に、設計論点と比較案を整理する。

## 現在の根拠

### 主要レポート

- `運用資料/reports/feedback_daily_sync_20260526.md`
- `運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md`
- `運用資料/reports/analysis/operational_focus_20260526.md`

### 主要数値

- `paper_positions closed=19 / sl_hit=12 / missed_opportunity=5`
- `market_map_opportunity=97件 / 平均R 0.36 / 簡易PF 1.97`
- `long=18件 / 平均R -0.51 / 簡易PF 0.29 / sl_hit=15`
- `wait>=60=39件 / 平均R -0.16 / 簡易PF 0.74`
- `wait>=80=7件 / 平均R -0.84 / sl_hit=6`
- `execution<20=44件 / 平均R -0.02 / sl_hit=29`
- `late_wait_sl=20 / trend_flip_long_sl=10 / other_sl=18`

### AI事後評価の補助根拠

- `sl_eval=too_tight` が SL 再設計候補を押し上げている
- `user_verdict=too_early` と `tf_15m_eval=poor` が entry 遅延候補を押し上げている
- `misleading_entry_like_wording=yes` は通知文面の中立化候補

## いま分かっていること

1. `long`、高 wait、低 execution が混ざって悪化しているため、1 つの gate 緩和/抑制でまとめて触るべきではない。
2. `sl_hit` は「SL が狭い」のか「entry が早い」のか「待ちすぎ後の劣化 entry」なのかを分けて設計する必要がある。
3. AI事後評価は日常判断の主系になったので、設計案にも `too_tight` / `too_early` を直接使ってよい。

## ChatGPT が次に詰めること

1. `entry 発火条件` の再設計案
   - `execution<20` と `tf_15m_eval=poor` をどう抑制条件へ入れるか
   - `too_early` を引きやすい signal 群を個別に抑えるか
2. `SL/TP 条件` の再設計案
   - `too_tight` 優勢群だけ SL を広げるのか
   - TP を変えるべき群を分離するのか
3. `wait / execution` の扱い
   - `wait>=80` を hard に落とすか
   - `wait>=60` は signal 別に扱うか
   - `execution<20` を direction / signal / market_map flag と組み合わせるか

## Codex に渡す前に固める条件

- `entry`、`SL/TP`、`wait/execution` の3軸を分けた仕様になっていること
- どのレポートのどの数値を根拠にしたか書かれていること
- `trade_execution_gate` 緩和ではなく、紙候補品質の改善であることを明記すること
- 変更対象ファイルと検証レポート名が指定されていること
