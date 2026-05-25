# Codex 実行依頼: entry / wait / trend_flip 品質ガード

作成日: 2026-05-26 JST
作成者: ChatGPT プロジェクト

## 目的

`paper_positions.csv` の `sl_hit` 偏重を減らすため、実弾 gate 緩和ではなく、紙候補の品質ガードを追加する。

今回の目的は次の 3 点に限定する。

1. `long` + 高 `wait` + 低 `execution` の弱い紙候補を抑制する。
2. `trend_flip_confirmed_up` を上方向の強評価・紙候補昇格根拠として使わない。
3. 変更後に、日次レポートと追加診断で抑制理由が追えるようにする。

## 対象ブランチ

- 作業ブランチ: `ver02.6-v2`
- 運用本体の参照ブランチ: `ver02.5-v8`

`運用資料/NEXT_TASK.md` の現在値を正本とし、作業開始時に必ず確認する。

## 根拠

### 参照レポート

- `運用資料/reports/feedback_daily_sync_20260526.md`
- `運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md`
- `運用資料/reports/analysis/market_map_effectiveness_20260526.md`
- `chatgpt/analysis/20260526_entry_sl_tp_wait_redesign.md`
- `chatgpt/analysis/20260526_trend_flip_confirmed_up_reassessment.md`

### 判断に使う主要数値

- `paper_positions closed=19 / sl_hit=12 / missed_opportunity=5`
- `market_map_opportunity=97件 / 平均R 0.36 / 簡易PF 1.97`
- `long=18件 / 平均R -0.51 / 簡易PF 0.29 / sl_hit=15`
- `wait>=60=39件 / 平均R -0.16 / 簡易PF 0.74`
- `wait>=80=7件 / 平均R -0.84 / sl_hit=6`
- `execution<20=44件 / 平均R -0.02 / sl_hit=29`
- `trend_flip_confirmed_up=32件 / 勝率41.2% / wrong_rate28.1% / MFE24h2.50 / MAE24h10.85`
- 紙ポジション診断では `trend_flip_confirmed_up=7件` がすべて `sl_hit`

## 変更範囲

Codex は実装前に関連ファイルを検索し、実際のファイル名に合わせて最小変更する。

触ってよい範囲:

- scoring / signal / opportunity gate / paper order 判定まわり
- `paper_positions.csv` や `paper_orders` 生成に関わる理由フラグ出力
- 日次・分析レポート生成 CLI
- 通知文言のうち `trend_flip_confirmed_up` を強く見せている表現
- `運用資料/NEXT_TASK.md`
- `運用資料/履歴/progress.md`
- `運用資料/reports/report_hub_latest.md`

触らない範囲:

- 実弾発注処理
- 取引所 API 送信
- 秘密鍵・認証情報
- launchd / 常駐設定そのもの
- `trade_execution_gate` を緩める変更
- SL / TP の倍率・距離・RR 計算

## 実装内容

### 1. 高 wait / 低 execution / long の紙候補ガード

以下の抑制理由を追加する。

#### `paper_quality_high_wait_block`

条件:

- `wait >= 80`

効果:

- `paper_order_status=planned` にしない。
- 既存の watch / 通知は残してよい。
- 理由フラグとして CSV / JSON / レポートに残す。

#### `paper_quality_low_execution_block`

条件:

- `execution < 20`

効果:

- 原則として `paper_order_status=planned` にしない。
- ただし既存コードに明確な例外条件がある場合は、Codex は勝手に拡張せず、その例外を保ったうえで理由ログだけ追加する。

#### `paper_quality_long_wait_block`

条件:

- `direction` が long 系である。
- かつ `wait >= 60`
- かつ `execution < 25`

効果:

- `paper_order_status=planned` にしない。
- long 側の高 wait / 低 execution を別理由で追えるようにする。

### 2. `trend_flip_confirmed_up` の扱い固定

`trend_flip_confirmed_up` は、現時点では強い上方向根拠として扱わない。

実装すること:

- `trend_flip_confirmed_up` 単独で score を大きく押し上げない。
- `trend_flip_confirmed_up` 単独で `trade_execution_gate=pass` に近づけない。
- `trend_flip_confirmed_up` 単独で `paper_order_status=planned` にしない。
- long 候補かつ `trend_flip_confirmed_up` を含む場合、追加理由 `paper_quality_trend_flip_up_block` を出せるようにする。

通知文言:

- 強い表現は禁止。
- 例: `上方向転換を確認`、`ロング優勢`、`買い候補` のような誤読しやすい表現は避ける。
- 許容例: `上方向転換の可能性はあるが、現行評価では紙候補昇格には使わない`。

### 3. SL / TP は今回変更しない

今回の第一弾では SL / TP の倍率・距離・RR 計算を触らない。

理由:

- `sl_eval=too_tight` は補助根拠として重要だが、現時点では「SL が狭い」のか「entry が早い」のか「待ちすぎ entry」なのかが混ざっている。
- SL を広げるだけだと、損失幅だけが増える可能性がある。
- まず弱い entry を抑制し、その後に `too_tight` 優勢群だけを別診断する方が安全。

### 4. レポート出力

日次または分析レポートに、最低限次の集計を追加する。

- `paper_quality_high_wait_block` 件数
- `paper_quality_low_execution_block` 件数
- `paper_quality_long_wait_block` 件数
- `paper_quality_trend_flip_up_block` 件数
- 抑制後の `paper_order_status=planned` 件数
- 抑制後の `sl_hit` / `tp2_hit` / `missed_opportunity` の変化が後日追える導線

既存レポートに自然に入るなら追加でよい。
独立レポートが必要なら、`運用資料/reports/analysis/paper_quality_guard_YYYYMMDD.md` を生成する CLI を追加する。

## 検証

Codex は最低限、以下を実行する。

```bash
git branch --show-current
git pull
find chatgpt -maxdepth 3 -type f | sort
```

その後、repo の既存ルールに従ってテストを実行する。

必須確認:

- 既存テストが通る。
- `trade_execution_gate` を緩めていない。
- 実弾発注、取引所API、秘密鍵連携に触れていない。
- SL / TP の倍率・距離・RR 計算に触れていない。
- `trend_flip_confirmed_up` が強評価へ戻っていない。
- 新しい抑制理由が CSV / JSON / レポートのいずれかで追える。
- 生成した raw report を `運用資料/reports/report_hub_latest.md` から辿れる。

## 完了条件

- `ver02.6-v2` に実装 commit が入っている。
- 全体テストまたは既存の主要テストが通っている。
- 必要な日次・分析レポートが生成されている。
- `運用資料/NEXT_TASK.md` に、今回追加した品質ガードと次に見る数値が反映されている。
- `運用資料/履歴/progress.md` に作業履歴が追記されている。
- この仕様書を `chatgpt/specs/archive/` へ移動し、`chatgpt/specs/active/` には未着手仕様だけを残す。
- commit / push 済み。

## 注意事項

- これは `Phase 1B` 昇格ではない。
- これは実弾 gate 緩和ではない。
- `paper_order_status=planned` を増やす作業ではなく、弱い紙候補を減らす作業である。
- 数値条件を追加で変えたくなった場合は、Codex 側で勝手に判断せず、確認事項として返す。
- `mfe_atr` / `mae_atr` / `rr_estimate` は欠損が残っているため、thin RR 系の判定は今回の主条件にしない。
