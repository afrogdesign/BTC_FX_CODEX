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

- `運用資料/NEXT_TASK.md`
- `運用資料/reports/feedback_daily_sync_20260526.md`
- `運用資料/reports/analysis/market_map_effectiveness_20260526.md`
- `運用資料/reports/analysis/operational_focus_20260526.md`
- `運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md`
- `chatgpt/analysis/20260526_entry_sl_tp_wait_redesign.md`
- `chatgpt/analysis/20260526_trend_flip_confirmed_up_reassessment.md`
- `chatgpt/analysis/20260526_auto_trade_fast_path_design.md`

### 現状判断

- `trade_execution_gate=pass` は 0 件。
- `paper_orders planned` は 0 件。
- `paper_positions` は `sl_hit` 偏重が残っている。
- `long`、高 wait、低 execution、`trend_flip_confirmed_up` が弱い。
- したがって、今回の目的は gate 緩和ではなく、紙候補の品質ガードである。

### 変更範囲

主対象:

- `src/trade/opportunity_gate.py`

必要に応じて触ってよい:

- `tests/` 配下の関連テスト
- `tools/` 配下の report / diagnostics 生成ロジック
- `運用資料/NEXT_TASK.md` の作業記録
- `運用資料/履歴/progress.md` の履歴記録

触らない:

- 実弾発注処理
- 取引所API送信処理
- 秘密鍵・認証情報
- 本番発注を有効化する設定
- SL/TP 倍率そのもの
- `trade_execution_gate` の pass 条件緩和
- `Phase 1B-lite` の正式 `Phase 1B` 昇格

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

品質 blocker は、`opportunity_gate=pass` へ進む前に評価する。
該当する場合は、`opportunity_gate=blocked` / `opportunity_type=blocked` / `opportunity_reasons` に blocker 名を残す。

#### 2. `paper_quality_high_wait_block`

条件:

```txt
confidence_wait_shadow >= 80
```

扱い:

- `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_high_wait_block` を出す

理由:

- `wait>=80` は `sl_hit` 偏重が強く、平均Rが弱い。
- 自動トレード前に候補化から外すべき。

#### 3. `paper_quality_low_execution_block`

条件:

```txt
confidence_execution_shadow < 20
```

扱い:

- `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_low_execution_block` を出す

理由:

- `execution<20` は低品質 entry になりやすく、`sl_hit` が多い。

#### 4. `paper_quality_long_wait_block`

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

- `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_long_wait_block` を出す

理由:

- long と高 wait の組み合わせは現状弱い。
- long 側を自動トレードに近づけるのは時期尚早。

#### 5. `paper_quality_trend_flip_up_block`

条件:

```txt
long_side == true
AND (
  "trend_flip_confirmed_up" in risk_flags
  OR "trend_flip_confirmed_up" in market_map_flags
)
```

扱い:

- `opportunity_gate=blocked`
- `opportunity_type=blocked`
- `opportunity_reasons` に `paper_quality_trend_flip_up_block` を出す

理由:

- `trend_flip_confirmed_up` は件数こそ増えたが、強評価へ戻す根拠がない。
- 紙ポジション側でも `sl_hit` 偏重が確認されている。

#### 6. market_map の有効 flag は潰さない

以下の既存 market_map opportunity flags は維持する。

```txt
support_to_resistance_flip
failed_breakout_down_reversal
resistance_to_support_flip
```

ただし、上記 quality blocker に該当する場合は候補化しない。

特に `support_to_resistance_flip` / `trend_flip_confirmed_down` の下方向優位を壊さないこと。

#### 7. SL/TP 数値は変更しない

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

#### 1. 既存テスト

```bash
pytest
```

または repo の既存ルールに従い、現在使われている全体テストコマンドを実行する。

#### 2. opportunity_gate 単体テスト

既存テストがある場合は追加・更新する。
ない場合は `tests/` 配下に `determine_opportunity_gate()` のテストを追加する。

最低限確認するケース:

1. `wait=80` 以上で `paper_quality_high_wait_block`
2. `execution=19.9` 以下で `paper_quality_low_execution_block`
3. `long_side=true / wait>=60 / execution<25` で `paper_quality_long_wait_block`
4. `long_side=true / trend_flip_confirmed_up` で `paper_quality_trend_flip_up_block`
5. `support_to_resistance_flip` かつ quality blocker なしなら `market_map_opportunity` を維持
6. `trade_execution_gate=pass` でも quality blocker がある場合に blocked へ寄せる

#### 3. レポート生成確認

可能なら次を生成する。

```bash
python -m tools.feedback_daily_sync
```

または repo で使っている daily-sync / paper diagnostics の正式コマンドを実行する。

確認項目:

- `paper_quality_high_wait_block` 件数が追跡できる
- `paper_quality_low_execution_block` 件数が追跡できる
- `paper_quality_long_wait_block` 件数が追跡できる
- `paper_quality_trend_flip_up_block` 件数が追跡できる
- `opportunity_gate=pass` が不自然に増えていない
- `paper_orders planned` を勝手に増やしていない

### 完了条件

- `pytest` が通る
- `determine_opportunity_gate()` の quality blocker がテストで確認できる
- quality blocker が `opportunity_reasons` に残る
- market_map の既存 opportunity flag が blocker なしでは維持される
- SL/TP 倍率や実弾発注関連には触っていない
- 変更内容を `運用資料/NEXT_TASK.md` または `運用資料/履歴/progress.md` に短く記録する

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
