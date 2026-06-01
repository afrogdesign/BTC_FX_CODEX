# counterfactual_quality_guard builder 正式化仕様

## 目的

quality guard hard / soft 分離後の評価を、単発レポートではなく再生成可能な report builder として正式化する。

この builder は、guard 条件を変更するためのものではなく、`require_execution_for_high_wait`、`suppress_long_high_wait`、`suppress_trend_flip_up_strong` が、sl_hit 抑制と tp2_hit / missed_opportunity 巻き込みにどう効いているかを継続評価するための診断である。

## 対象ブランチ

`ver02.6-v2`

## 変更範囲

将来の実装対象候補:

- `tools/log_feedback.py`
- 必要なら report builder 周辺の既存テスト
- `運用資料/reports/report_hub_latest.md`
- `運用資料/reports/analysis/quality_guard_effectiveness_YYYYMMDD.md`

今回の仕様では、以下は対象外:

- `trade_execution_gate` の緩和
- `phase1b_lite_gate` の変更
- `opportunity_gate` の緩和
- paper_orders planned を増やす目的の変更
- 実弾発注、取引所API送信、秘密鍵連携

## 実装内容

### 1. builder の役割

`paper_positions.csv` と `shadow_log.csv` を `signal_id` で突き合わせ、closed 済み paper position に対して quality guard 条件を後付け再計算する。

### 2. 入力

- `logs/csv/paper_positions.csv`
- `logs/csv/shadow_log.csv`
- 既存 daily-sync / diagnostics と同じ date cutoff の扱いがある場合は、それに揃える。

### 3. 対象行

- `paper_positions.csv` の `closed` 行を対象にする。
- `signal_id` で `shadow_log.csv` と突き合わせる。
- join できない行は件数を別途 `missing_shadow_join` として数える。

### 4. 再計算する guard leaf

以下を A/B/C として扱う。

- `A=require_execution_for_high_wait`
- `B=suppress_long_high_wait`
- `C=suppress_trend_flip_up_strong`

現行の hard / soft 区分は変更しない。

### 5. 出力する group

最低限、以下を出力する。

- `A only`
- `B only`
- `C only`
- `A+B`
- `A+C`
- `B+C`
- `A+B+C`
- `guard該当全体`
- `guard非該当全体`
- `closed全体`

### 6. group ごとの出力列

最低限、以下を Markdown table で出す。

- `count`
- `sl_hit`
- `sl_hit_rate`
- `tp2_hit`
- `tp2_hit_rate`
- `missed_opportunity`
- `missed_rate`
- `timeout`
- `entry_not_reached`
- `avg_R`
- `memo`

### 7. interpretation section

レポート末尾に、次の解釈を固定して出す。

- `A only` は失敗率が高く、hard blocker 維持を検討する材料。
- `B only` / `C only` は missed / 未到達の巻き込みを必ず見る。
- `B+C` や `A+B+C` は件数が少ない場合、断定しない。
- counterfactual は後付け再計算であり、実運用結果ではない。
- この report は guard 条件を即時変更するためのものではない。

## 検証方法

将来の実装時は最低限以下を確認する。

```bash
./.venv312/bin/python tools/log_feedback.py --report-hub
./.venv312/bin/python tools/log_feedback.py --quality-guard-effectiveness
```

実際のコマンド名は既存 CLI 構造に合わせる。ただし、仕様実装時に Codex が勝手に report 名や保存先を変えないこと。

## 完了条件

- `quality_guard_effectiveness_YYYYMMDD.md` が再生成できる。
- `report_hub_latest.md` の `quality_guard_effectiveness` latest が更新される。
- reason 組み合わせ別 table が出る。
- `trade_execution_gate`、`phase1b_lite_gate`、`opportunity_gate` は変わっていない。
- 実弾発注、取引所API送信、秘密鍵連携に触れていない。

## 注意事項

- `trade_execution_gate=pass=0件`、`paper_orders planned=0件` の間は実弾方向へ進めない。
- `A only` の成績が強く見えても、即 gate 緩和や hard 条件追加をしない。
- `B/C` 単独は missed / entry_not_reached 巻き込みがあるため、慎重に扱う。
- この仕様は builder 正式化であり、売買ロジック変更ではない。
