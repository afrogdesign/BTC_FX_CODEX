# Phase 1 条件の見方

更新日: 2026-04-22 02:40 JST

## まず結論

- `primary_setup_status=ready` は「方向だけでなく、入る価格帯と引き金までそろって、やっと検討可能になった状態」です。
- `phase1_active=true` は、その `ready` がさらに Phase 1 の観測対象として有効だと確定した状態です。
- 今後は実用化のため、`Phase 1A` と `Phase 1B` を分けます。`Phase 1A` は `phase1_observation_gate=pass` を使う観測紙トレード、`Phase 1B` は従来の `phase1_active=true` と `trade_execution_gate=pass` を使う厳格紙トレードです。
- 直近データでは `Phase 1B` はまだ未達ですが、`Phase 1A` は開始可能です。

## 0. Phase 1A / 1B の分け方

`Phase 1A` は「実行する候補」ではありません。悪い相場でも、方向判断や待機条件がどれくらい使えるかを検証する観測紙トレードです。

- 対象: `phase1_observation_gate=pass`
- 保存先: `logs/csv/observation_paper_orders.csv`
- 見る数字: 観測タイプ別の近似PF、TP1先行率、平均MFE / MAE、entry zone 未到達率

`Phase 1B` は従来どおり厳格な紙トレードです。

- 対象: `phase1_active=true` かつ `trade_execution_gate=pass`
- 保存先: `logs/csv/paper_orders.csv`
- 見る数字: planned 件数、サイズ計画、出口計画、実行 gate のブロック理由

## 1. 何が起きたら `ready` なのか

`ready` は「通知が出た」ではありません。次の条件を全部通ったときだけ立ちます。

1. まず禁止条件に引っかかっていない
- `RR不足` ではない
- `ATR極端値` ではない
- `Funding禁止域` ではない
- `confidence不足` ではない
- `warning多発` ではない

2. 価格がエントリー帯まで来ている
- 現在値がエントリー帯の中にいる
- または、エントリー帯までの距離が `ATRの0.08倍以内`

3. 引き金が出ている
- `breakout_up / breakout_down` のどちらかが出ている
- または `15分足の volume_ratio >= TRIGGER_VOLUME_RATIO`

4. 位置リスクの補正で落とされていない
- `prelabel=RISKY_ENTRY` なら `ready` でも `watch` に落ちる
- `prelabel=SWEEP_WAIT` なら `watch`
- `prelabel=NO_TRADE_CANDIDATE` なら `invalid`

要するに、`ready` は「方向が合っていそう」ではなく、

- 価格が来た
- 引き金が出た
- RRやFundingも通った
- 位置リスクでも止められていない

この全部を通った状態です。

## 2. 何が起きたら `phase1_active=true` なのか

`phase1_active=true` は、`ready` よりさらに一段上の確認です。次を全部満たしたときだけ立ちます。

- `primary_setup_side` が `long` か `short`
- `bias` が `wait` ではない
- `entry_price > 0`
- `stop_loss_price > 0`
- `entry_price` と `stop_loss_price` が同じではない
- `data_quality_flag != partial_missing`
- `primary_setup_status == ready`

つまり、かなり単純に言うと、

- `ready` が立っている
- 入る価格と損切り価格がちゃんと計算できている
- データ欠損がない

この状態になったときだけ `phase1_active=true` です。

## 3. 実データではどれくらい起きているか

対象: `logs/csv/trades.csv` の有効 669 件  
補足: 古い壊れた 11 行は除外

全体の実績

- `invalid`: 300 件
- `watch`: 259 件
- `none`: 107 件
- `ready`: 3 件
- `phase1_active=true`: 1 件

発生率

- `ready` 発生率: `3 / 669 = 0.45%`
- `phase1_active=true` 発生率: `1 / 669 = 0.15%`

`bias=long/short` が出ている行だけで見た場合

- 対象: 558 件
- `ready` 発生率: `3 / 558 = 0.54%`
- `phase1_active=true` 発生率: `1 / 558 = 0.18%`

直近 168 件では

- `ready`: 0 件
- `phase1_active=true`: 0 件

つまり今の相場では、まだ `Phase 1B` の本番観測が立っていない状態です。
ただし `Phase 1A` は `phase1_observation_gate=pass` を使って開始できます。

## 4. どこで止まりやすいのか

最も多い停止パターン

- `setup_not_ready`: 282 件
- `watch_reference_only`: 232 件
- `bias_wait`: 4 件
- `partial_missing_data`: 1 件

人が読むときの意味

- `setup_not_ready`
  価格がまだ帯に来ていない、または引き金が弱い
- `watch_reference_only`
  方向や価格帯は見えているが、まだ「入る」段階ではない
- `bias_wait`
  方向そのものをまだ決めないほうがよい
- `partial_missing_data`
  データ欠損で Phase 1 判定に使えない

## 5. `prelabel` ごとの現実

- `ENTRY_OK`: 30 件中 `ready` は 1 件 (`3.33%`)
- `RISKY_ENTRY`: 247 件中 `ready` は 0 件
- `SWEEP_WAIT`: 238 件中 `ready` は 0 件
- `NO_TRADE_CANDIDATE`: 138 件中 `ready` は 0 件

ここが重要です。

`SWEEP_WAIT` や `NO_TRADE_CANDIDATE` が多いあいだは、そもそも `ready` が立ちにくい設計です。  
なので `Phase 1B` に進めない主因は、レビュー不足ではなく「相場と位置判定がまだ ready 水準まで来ていないこと」です。
一方で `Phase 1A` は ready を待たず、観測価値のある候補を記録して改善材料にします。

## 6. 今どう読めばよいか

- `🟠 高優先監視・実行不可` が来ても、すぐ `Phase 1B` ではない
- 本当に見るべきなのは `primary_setup_status`
- それが `watch` なら「監視継続」
- それが `ready` なら、やっと「条件付きで検討」
- `phase1_observation_gate=pass` なら `Phase 1A` の観測紙トレード
- そのうえで `phase1_active=true` と `trade_execution_gate=pass` が立ったら、`Phase 1B` の厳格紙トレード

今の運用では、

- 通知は出る
- AI事後評価は溜まる
- 改善資料も溜まる
- `Phase 1A` は `phase1_observation_gate=pass` で始める
- `Phase 1B` への扉が開くのは `ready` と `phase1_active=true` と `trade_execution_gate=pass` が実ログに出たとき

という理解でよいです。

## 7. 通知ランクと実行可否の分離

`Ver02.5-v7` では、通知ランクを実行可否で分けます。

- `執行候補・強` / `執行候補`
  - `trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ出る
- `高優先監視・実行不可`
  - `trade_execution_gate=blocked` だが `phase1_observation_gate=pass` のときに出る
- `通常監視・実行不可`
  - 本通知だが、実行候補でも高優先観測候補でもない
- `注意報・売買非推奨`
  - 方向変化や初動の共有で、売買推奨ではない

これにより、方向や構造が強い通知でも、実行ゲートを通っていないものは `執行候補` と表示しません。

## 8. Phase 1B-lite の扱い

`Phase 1B-lite` は正式 `Phase 1B` ではありません。
`SWEEP_WAIT` 限定の専用紙トレード観測レーンで、正式 `paper_orders.csv` とは分けます。

- 対象: `phase1b_lite_gate=pass`
- 保存先: `logs/csv/phase1b_lite_paper_orders.csv`
- 件名ランク: `執行候補` へは上げない
- 昇格目安: まず 10〜15 件まで観測し、TP1先行率、近似PF、平均MFE/MAEを見る

## 参照コード

- `src/analysis/rr.py`
- `src/analysis/position_risk.py`
- `src/trade/activation.py`
- `src/trade/observation_gate.py`
- `src/trade/phase1b_lite.py`
- `main.py`
