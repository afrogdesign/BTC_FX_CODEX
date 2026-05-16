# フェーズ加速計画 Phase1B-lite

更新日: 2026-05-17 JST

## まず結論

この計画の目的は、正式な安全条件を壊さずに、プロジェクトを前へ進めることです。

2.5か月以上開発を続けており、疲れや熱意の低下が出ている。
一方で、最終目標は「勝てる自動トレード」であり、焦って実弾自動売買へ進むと、これまで積み上げた安全設計を壊す。

したがって、次の段階として `Phase 1B-lite` を追加します。

- `Phase 1A`: 観測紙トレード
- `Phase 1B-lite`: 限定条件付きの厳格紙トレード候補
- `Phase 1B`: 従来どおり `phase1_active=true` かつ `trade_execution_gate=pass`

`Phase 1B-lite` は、実弾ではありません。
正式 `Phase 1B` でもありません。
ただし、単なる観測より一段上の「本 Phase 1B へ進めるかを検証する専用レーン」として扱います。

## 外部リスク前提

BTC と crypto asset は、一般的な金融商品よりも価格変動、取引所リスク、ハッキング、流動性、操作的な値動きのリスクが大きい。

参照:

- CFTC: Customer Advisory: Understand the Risks of Virtual Currency Trading
  - https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/understand_risks_of_virtual_currency.html
- Investor.gov / SEC: Exercise Caution with Crypto Asset Securities
  - https://www.investor.gov/index.php/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-alerts/crypto-asset-securities

この計画では、「早く進めたい」という感情は尊重する。
ただし、実弾リスクを増やす判断は、紙トレードで最低限の再現性が出てからにする。

## 現状

2026-05-16 時点の判断材料は次の通りです。

- `trade_execution_gate=pass`: 0 件
- `paper_orders planned`: 0 件
- `phase1b_promotion_candidates`: 6 件
- `Phase 1B` 昇格候補の勝率: 50.0%
- `Phase 1B` 昇格候補の TP1先行率: 100.0%
- `Phase 1B` 昇格候補の近似PF: 1.26
- `market_map` 記録: 68 件
- `trend_flip_confirmed_up`: 11 件
- `trend_flip_confirmed_up` 勝率: 33.3%
- `trend_flip_confirmed_up` 平均MAE24h: 14.51
- AI事後評価 backlog: 69 件
- `request_failed`: 0 件

重要なのは、`phase1b_promotion_candidates` は少し良くなっているが、正式な `trade_execution_gate=pass` はまだ 0 件という点です。

つまり、正式 `Phase 1B` へ進む材料はまだ足りない。
しかし、限定候補だけを別枠で観測する価値は出ている。

## なぜ正式 Phase 1B を今すぐ上げないか

正式 `Phase 1B` は、従来どおり次を満たす段階です。

- `phase1_active=true`
- `trade_execution_gate=pass`
- `paper_order_status=planned`

これを今すぐ緩めると、次の問題が起きます。

- `confidence_below_min` を事実上無視することになる
- `SWEEP_WAIT` を実行候補と誤読しやすくなる
- `trend_flip_confirmed_up` の弱さを見落とす
- 「勝てる自動トレード」ではなく「候補を増やすだけ」になる

したがって、正式 `Phase 1B` はまだ上げない。
代わりに `Phase 1B-lite` を新設して、候補の再現性だけを早く検証します。

## Phase 1B-lite の定義

`Phase 1B-lite` は、次の条件をすべて満たす行だけを対象にします。

- `phase1_observation_type=confidence_watch_learning`
- `prelabel=SWEEP_WAIT`
- `risk_flags` に `sweep_incomplete` がある
- `risk_flags` に `lower_liquidity_close` がある
- 補助 hard flag がない
- `confidence_direction_shadow >= 55`
- `confidence_execution_shadow >= 18`
- `confidence_wait_shadow <= 85`
- `data_quality_flag=ok`

この条件は、現行の `phase1b_promotion_candidates` と同じ母集団を起点にします。

## 除外条件

次のいずれかがある場合は、`Phase 1B-lite` へ上げません。

- `NO_TRADE_CANDIDATE`
- `data_quality_flag != ok`
- `trade_execution_blockers` にデータ品質系の理由がある
- Funding 禁止域
- ATR 極端値
- hard flag 付きの `confidence_below_min`
- `trend_flip_confirmed_up` だけが主根拠
- `wait > 85`
- `execution < 18`

特に `trend_flip_confirmed_up` は、2026-05-16 時点では弱い。
上方向転換の根拠としては、まだ gate を緩める材料にしません。

## 記録ルール

将来実装する場合、正式 `paper_orders.csv` とは混ぜません。

新しく次を追加します。

- `phase1b_lite_gate`
- `phase1b_lite_type`
- `phase1b_lite_reasons`
- `phase1b_lite_paper_orders.csv`

`phase1b_lite_gate=pass` になっても、`trade_execution_gate=blocked` のままでよい。
これは矛盾ではなく、「正式実行 gate は blocked だが、限定検証レーンには入れる」という意味です。

## メール表示ルール

初期実装では、メール件名の最上位ランクには `Phase 1B-lite` を出しません。
まずは `daily-sync` と専用レポートで確認します。

メール本文や詳細ページへ補助表示する段階へ進む場合は、誤読防止のため次の表現を使います。

- 表示名: `厳格紙トレード候補`
- 本文冒頭: `これは実弾ではありません。正式 Phase 1B でもありません。`
- 補足: `Phase 1B-lite の限定検証対象です。`

使わない表現:

- `自動売買候補`
- `実行候補`
- `強い買い`
- `強い売り`
- `今すぐ入る`

この表示を入れても、`final_rank_code` は `執行候補` 系へ上げません。
正式 `trade_execution_gate=pass` と `paper_order_status=planned` がない限り、件名上は監視系のままにします。

## 成功条件

まず 10〜15 件だけ観測します。

そのうえで、次を満たしたら正式 `Phase 1B` 条件の見直しへ進めます。

- TP1先行率 60% 以上
- 近似PF 1.2 以上
- 平均MFE > 平均MAE
- 誤読レビュー 0 件
- runtime error 0 件
- `request_failed=0` 継続

この条件を満たしても、すぐ実弾には進みません。
次に進めるのは、正式 `Phase 1B` の gate 条件見直しです。

## 自動トレードまでの現実的ロードマップ

### Step 1: Phase 1B-lite

目的は、候補を増やすことではなく、少数の型が再現するかを見ること。

見る数字:

- 件数
- TP1先行率
- 近似PF
- 平均MFE / MAE
- entry zone 到達率
- stop 相当の逆行幅
- 誤読レビュー

### Step 2: 正式 Phase 1B

`Phase 1B-lite` で条件を満たした型だけ、正式 gate へ反映する。

この段階でも実弾ではなく、厳格紙トレードのままです。

見る数字:

- `trade_execution_gate=pass`
- `paper_order_status=planned`
- `paper_orders.csv` の planned 件数
- planned 後の TP1 / SL / timeout
- 連敗時の risk reduction

### Step 3: 自動トレード前の Shadow Execution

実注文を出さず、実際に約定した前提で約定、手数料、滑り、最大逆行、timeout を記録する。

ここで初めて「実弾に近い検証」になります。

必要な数字:

- 30 件以上
- 近似PF 1.3 以上
- 最大ドローダウンが許容範囲
- SL 到達率が異常でない
- timeout が多すぎない
- 連敗後のサイズ縮小が効いている

### Step 4: 最小実弾

最小サイズでのみ開始します。

この段階の目的は利益ではなく、注文、約定、キャンセル、SL/TP、ログ保存が壊れないかの確認です。

## 採用しない案

今は次を採用しません。

- `confidence_below_min` の一律緩和
- `NO_TRADE_CANDIDATE` の解禁
- `trend_flip_confirmed_up` の強評価
- `trade_execution_gate=pass` 条件の直接緩和
- 実弾自動売買への移行
- 通知件数を増やすだけの調整

## 再考と精査

計画を一度書いたあと、改めて見直す。

### 再考 1: 早く進めたい気持ちへの答えになっているか

答えになっている。

理由は、従来の `Phase 1A` 観測だけだと「また観測か」という疲労感が強い。
`Phase 1B-lite` を切ることで、次の段階へ進んでいる実感を作れる。

ただし、実弾リスクは増やさない。
このバランスが今の最善です。

### 再考 2: 正式 Phase 1B を壊していないか

壊していない。

`trade_execution_gate=pass` はそのまま維持する。
`paper_orders.csv` にも混ぜない。
したがって、正式 Phase 1B の安全条件は守られる。

### 再考 3: 勝てる自動トレードに近づいているか

近づいている。

ただし、利益を急ぐ方向ではなく、勝てる可能性のある型を狭く固定する方向で近づく。
BTC はノイズと急変が大きいため、候補を広げるより、負けやすい型を削るほうが重要です。

### 再考 4: 危険な抜け道はないか

最大の危険は、`Phase 1B-lite` を実行候補と誤読すること。

対策として、メールとレポートでは必ず次を明記する。

- 実弾ではない
- 正式 Phase 1B ではない
- `trade_execution_gate=blocked` のままでよい
- `paper_orders.csv` とは混ぜない

### 再考 5: いま実装に進んでよいか

計画書としては実装に進んでよい。

ただし、最初の実装は「記録と集計」までに限定する。
通知の見せ方は入れてよいが、実注文や正式 `trade_execution_gate` の変更はしない。

## 次の実装単位

最初の実装単位は小さくする。

1. `phase1b_lite_gate` 判定を追加する
2. `phase1b_lite_paper_orders.csv` に保存する
3. `daily-sync` に `Phase 1B-lite` セクションを追加する
4. `build-phase1b-promotion-report` と同じ母集団で件数と成績を表示する
5. メール件名には出さず、まずレポートで確認する

この 5 つまでを最初の実装範囲にする。

## 完了条件

- `Phase 1B-lite` の定義がコードとレポートに入っている
- 正式 `Phase 1B` とログが混ざっていない
- `trade_execution_gate=pass` の条件を緩めていない
- 10〜15 件たまるまで gate 変更しない運用になっている
- `NEXT_TASK.md` に `Phase 1B-lite` の次判断が書かれている

## 実装結果

2026-05-17 JST に初期実装を行いました。

- `phase1b_lite_gate`、`phase1b_lite_type`、`phase1b_lite_reasons` を通常ログへ追加
- `logs/csv/phase1b_lite_paper_orders.csv` を追加
- live 判定と `tools/log_feedback.py` の再集計で同じ条件を使うように統一
- `daily-sync` に `Phase 1B-lite` セクションを追加
- `build-phase1b-promotion-report` に `Phase 1B-lite` セクションを追加

確認結果:

- `./.venv312/bin/python -m unittest discover -s tests`: 160 件 OK
- `git diff --check`: OK
- 実データの `daily-sync` 検証で `Phase 1B-lite` セクション表示を確認
- `build-phase1b-promotion-report --date-from 2026-04-18 --date-to 2026-05-17` で lite 候補 5 件を確認

未実施:

- メール件名ランクへの反映
- 正式 `paper_orders.csv` への混在
- `trade_execution_gate=pass` 条件の緩和
- 実弾自動売買への接続
