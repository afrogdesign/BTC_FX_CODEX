# 20260526 entry / wait / trend_flip quality guard

## Codex 実行依頼

### 目的

自動トレードへ進む前段として、紙候補の品質ガードを追加する。

現時点では `trade_execution_gate` を直接緩めない。
`sl_hit` に偏っている候補を分離し、次回 daily-sync / paper diagnostics で実弾化できる候補だけを評価できる状態にする。

今回の目的は「自動トレード実装」ではなく、「自動トレード直前へ進むための候補品質改善」である。

### 対象ブランチ

`ver02.6-v2`

このブランチ名は `運用資料/NEXT_TASK.md` の `現在の作業ブランチ` を正本として採用する。
`main` や remote branch 一覧から推測しない。

### 参照した根拠

- `AGENTS.md`
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
- `chatgpt/analysis/20260526_auto_trade_fast_path_design.md`
- `src/trade/opportunity_gate.py`
- `src/trade/paper_position.py`
- `tools/log_feedback.py`

### 現状判断

- `trade_execution_gate=pass` は 0 件。
- `paper_orders planned` は 0 件。
- `paper_positions` は `sl_hit` 偏重が残っている。
- `long`、高 wait、低 execution、`trend_flip_confirmed_up` が弱い。
- `support_to_resistance_flip` は相対的に有効だが、候補化時の entry / wait 条件が粗い。
- したがって、今回の目的は gate 緩和ではなく、紙候補の品質ガードである。

### 変更範囲

主対象:

- `src/trade/opportunity_gate.py`

必要に応じて触ってよい:

- `tests/` 配下の関連テスト
- `tools/log_feedback.py` の report / diagnostics 出力
- `運用資料/NEXT_TASK.md` の作業記録
- `運用資料/履歴/progress.md` の履歴記録
- `運用資料/reports/report_hub_latest.md` の導線更新

触らない:

- 実弾発注処理
- 取引所API送信処理
- 秘密鍵・認証情報
- 本番発注を有効化する設定
- SL/TP 倍率そのもの
- `trade_execution_gate` の pass 条件緩和
- `Phase 1B-lite` の正式 `Phase 1B` 昇格
- 通知ランクを `執行候補` へ上げる変更

### 実装内容

#### 1. paper quality blocker を追加する

`src/trade/opportunity_gate.py` の `determine_opportunity_gate()` に、紙候補品質用の blocker を追加する。

既存の fatal blocker と混ぜすぎず、理由名で区別できるようにする。

追加する blocker 名:

```txt
paper_quality_high_wait_block
paper_quality_low_execution_block
paper_quality_long_wait_block
paper_quality_trend_flip_up_block
```

#### 2. blocker の適用範囲

quality blocker は、主に以下の候補化を止めるために使う。

```txt
phase1_observation_gate pass 由来の opportunity
phase1b_lite_gate pass 由来の opportunity
market_map_opportunity
```

重要:

- `trade_execution_gate` 自体の判定条件は変更しない。
- 今回の仕様で `trade_execution_gate` を緩めない。
- 将来 `trade_execution_gate=pass` が出た場合に、quality blocker が formal candidate を無条件に握り潰す設計にはしない。
- ただし、`trade_execution_gate=pass` かつ quality blocker 該当が発生した場合は、Codex は勝手に formal candidate の扱いを決めず、`formal_candidate_quality_conflict` としてログ・レポート上で分かるようにするか、実装前に確認事項として返す。

この仕様の主眼は「弱い紙候補を観測候補・market_map候補から paper position 化しないこと」であり、formal execution gate の新設計ではない。

#### 3. `paper_quality_high_wait_block`

条件:

```txt
confidence_wait_shadow >= 80
```

扱い:

- 非 formal candidate では `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_high_wait_block` を出す

理由:

- `wait>=80` は `sl_hit` 偏重が強く、平均Rが弱い。
- 自動トレード前に候補化から外すべき。

#### 4. `paper_quality_low_execution_block`

条件:

```txt
confidence_execution_shadow < 20
```

扱い:

- 非 formal candidate では `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_low_execution_block` を出す

理由:

- `execution<20` は低品質 entry になりやすく、`sl_hit` が多い。

#### 5. `paper_quality_long_wait_block`

条件:

```txt
long_side == true
AND confidence_wait_shadow >= 60
AND confidence_execution_shadow < 25
```

`long_side` は以下で判定する。

```txt
bias == "long" OR primary_setup_side == "long"
```

扱い:

- 非 formal candidate では `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_long_wait_block` を出す

理由:

- long と高 wait の組み合わせは現状弱い。
- long 側を自動トレードに近づけるのは時期尚早。

#### 6. `paper_quality_trend_flip_up_block`

条件:

```txt
long_side == true
AND (
  "trend_flip_confirmed_up" in risk_flags
  OR "trend_flip_confirmed_up" in market_map_flags
)
```

扱い:

- 非 formal candidate では `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_trend_flip_up_block` を出す

理由:

- `trend_flip_confirmed_up` は件数こそ増えたが、強評価へ戻す根拠がない。
- 紙ポジション側でも `sl_hit` 偏重が確認されている。

#### 7. market_map の有効 flag は潰さない

以下の既存 market_map opportunity flags は維持する。

```txt
support_to_resistance_flip
failed_breakout_down_reversal
resistance_to_support_flip
```

ただし、上記 quality blocker に該当する場合は候補化しない。

特に `support_to_resistance_flip` / `trend_flip_confirmed_down` の下方向優位を壊さないこと。

#### 8. `Phase 1B-lite` は正式昇格させない

今回の変更で `Phase 1B-lite` を正式 `Phase 1B` に上げない。

専用CSVの観測レーンは維持する。
`Phase 1B-lite` の gate 条件そのものを変更する場合は、この仕様の範囲外とする。

#### 9. SL/TP 数値は変更しない

今回、以下は変更しない。

- SL 幅
- TP 距離
- RR 計算式
- breakeven 条件
- timeout 時間

理由:

`sl_eval=too_tight` の裏付けはあるが、entry 早すぎ / wait 劣化 / long 弱さが混ざっているため、第一弾では品質ガードを先に入れる。

### 検証

Codex は次を実行する。

#### 1. 現在ブランチ確認

```bash
git branch --show-current
```

期待値:

```txt
ver02.6-v2
```

#### 2. 既存テスト

AGENTS.md のルールに合わせ、原則として `.venv312` を使う。

```bash
.venv312/bin/python -m pytest
```

もし repo の現行テストコマンドが別に定義されている場合は、それを優先し、実行したコマンドを記録する。

#### 3. opportunity_gate 単体テスト

既存テストがある場合は追加・更新する。
ない場合は `tests/` 配下に `determine_opportunity_gate()` のテストを追加する。

最低限確認するケース:

1. `wait=80` 以上で `paper_quality_high_wait_block`
2. `execution=19.9` 以下で `paper_quality_low_execution_block`
3. `long_side=true / wait>=60 / execution<25` で `paper_quality_long_wait_block`
4. `long_side=true / trend_flip_confirmed_up` で `paper_quality_trend_flip_up_block`
5. `support_to_resistance_flip` かつ quality blocker なしなら `market_map_opportunity` を維持
6. `phase1b_lite_gate=pass` でも quality blocker 該当なら、formal ではない opportunity としては blocked になる
7. `trade_execution_gate=pass` かつ quality blocker 該当時は、Codex が仕様外判断をせず、少なくとも conflict として把握できる

#### 4. レポート生成確認

この repo の実際の CLI は `tools/log_feedback.py` 配下にある。
`python -m tools.feedback_daily_sync` は使わない。

可能なら以下を実行する。

```bash
.venv312/bin/python tools/log_feedback.py daily-sync --max-new-ai-reviews 0
.venv312/bin/python tools/log_feedback.py build-paper-opportunity-diagnostics-report --date-from 2026-04-18 --date-to 2026-05-26 --output-md 運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md
.venv312/bin/python tools/log_feedback.py build-report-hub
```

確認項目:

- `paper_quality_high_wait_block` 件数が追跡できる
- `paper_quality_low_execution_block` 件数が追跡できる
- `paper_quality_long_wait_block` 件数が追跡できる
- `paper_quality_trend_flip_up_block` 件数が追跡できる
- `opportunity_gate=pass` が不自然に増えていない
- `paper_orders planned` を勝手に増やしていない
- `report_hub_latest.md` から最新レポートを辿れる

### 完了条件

- `.venv312/bin/python -m pytest` または repo 既定の主要テストが通る
- `determine_opportunity_gate()` の quality blocker がテストで確認できる
- quality blocker が `opportunity_reasons` に残る
- market_map の既存 opportunity flag が blocker なしでは維持される
- `trade_execution_gate` の pass 条件を緩めていない
- SL/TP 倍率や実弾発注関連には触っていない
- `Phase 1B-lite` を正式 `Phase 1B` に昇格していない
- 変更内容を `運用資料/NEXT_TASK.md` または `運用資料/履歴/progress.md` に短く記録する
- 実施後、この仕様書を `chatgpt/specs/archive/` へ移し、`active/` には未着手仕様だけを残す

### 注意

- 実弾発注はしない。
- 取引所API送信はしない。
- 秘密鍵連携はしない。
- `trade_execution_gate` の緩和はしない。
- `Phase 1B-lite` を正式 `Phase 1B` に昇格しない。
- 件名ランクを `執行候補` に上げない。
- 今回は自動トレード実装ではなく、自動トレード直前へ進むための品質ガード実装である。

### 実装後に ChatGPT が見るべき数値

次回 ChatGPT は以下を見る。

- quality blocker 別件数
- blocker 後の `opportunity_gate=pass` 件数
- blocker 後の `paper_positions` の `sl_hit` 比率
- `missed_opportunity` が増えすぎていないか
- `support_to_resistance_flip` の有効性が維持されているか
- `long` / `trend_flip_confirmed_up` がまだ弱いか
- `trade_execution_gate=pass` と `paper_orders planned` が自然発生するか
