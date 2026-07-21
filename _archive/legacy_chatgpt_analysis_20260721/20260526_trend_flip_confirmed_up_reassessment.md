# 20260526 trend_flip_confirmed_up reassessment

## 目的

`trend_flip_confirmed_up` を上方向転換の強根拠へ戻さずに、今後どう扱うかを再判定するための分析メモ。

## この文書が扱う範囲

- score 加点
- gate 判定
- 紙候補化
- 通知文言

この4つを混ぜずに扱う。1 つの結論で一括変更しない。

## 現在の根拠

### 主要レポート

- `運用資料/reports/analysis/market_map_effectiveness_20260526.md`
- `運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md`
- `運用資料/NEXT_TASK.md`

### 主要数値

- `trend_flip_confirmed_up=32件`
- 勝率 `41.2%`
- `wrong_rate=28.1%`
- 平均 `MFE24h=2.50 / MAE24h=10.85`
- 紙ポジション診断では `trend_flip_confirmed_up=7件` がすべて `sl_hit`

## いま分かっていること

1. 件数は増えたが、強評価へ戻す根拠にはなっていない。
2. 紙候補でも `sl_hit` 偏重なので、少なくとも現状のまま long 側を押し上げる材料には使えない。
3. ただし完全無効化ではなく、文言上の参考 flag として残す余地はある。

## ChatGPT が次に詰めること

1. `score`
   - 加点を完全停止するか、弱い参考加点だけ残すか
2. `gate`
   - `trade_execution_gate` や紙候補昇格に使わないことを固定するか
3. `paper`
   - `trend_flip_confirmed_up` を含む long 候補を別抑制するか
4. `wording`
   - 通知文面では「上方向転換の可能性」程度に抑えるか

## Codex に渡す前に固める条件

- score / gate / paper / wording のどこを変えるかが分離されていること
- `trend_flip_confirmed_up` を強評価へ戻さない前提が明記されていること
- 関連する signal / flag / 表示文言の変更範囲が明記されていること
