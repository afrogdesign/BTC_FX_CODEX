# Phase 1 条件の見方

更新日: 2026-04-10 JST

## まず結論

- `primary_setup_status=ready` は「方向だけでなく、入る価格帯と引き金までそろって、やっと検討可能になった状態」です。
- `phase1_active=true` は、その `ready` がさらに Phase 1 の観測対象として有効だと確定した状態です。
- 今の実データでは、`ready` も `phase1_active=true` もかなり珍しく、しばらく普通に回して観測を待つのは妥当です。

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

つまり今の相場では、まだ `Phase 1` の本番観測が立っていない状態です。

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
なので `Phase 1` に進めない主因は、レビュー不足ではなく「相場と位置判定がまだ ready 水準まで来ていないこと」です。

## 6. 今どう読めばよいか

- `🟠 高め本通知` が来ても、すぐ `Phase 1` ではない
- 本当に見るべきなのは `primary_setup_status`
- それが `watch` なら「監視継続」
- それが `ready` なら、やっと「条件付きで検討」
- そのうえで `phase1_active=true` が立ったら、Phase 1 の本番観測として扱う

今の運用では、

- 通知は出る
- AI事後評価は溜まる
- 改善資料も溜まる
- ただし `Phase 1` への扉が開くのは `ready` と `phase1_active=true` が実ログに出たとき

という理解でよいです。

## 参照コード

- `src/analysis/rr.py`
- `src/analysis/position_risk.py`
- `src/trade/activation.py`
- `main.py`
