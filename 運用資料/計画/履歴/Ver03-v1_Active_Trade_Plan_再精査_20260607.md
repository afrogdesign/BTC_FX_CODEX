# Ver03-v1 Active Trade Plan 再精査メモ

更新日: 2026-06-07 JST  
対象ブランチ: `Ver03-v1`  
位置づけ: ChatGPT による設計判断メモ。Codex はこの内容を実装判断せず、後続作業で指定された範囲のみ実装する。

---

## 1. 結論

`運用資料/計画/20260607_active_trade_plan_実用化計画.md` の方向性は妥当である。

特に、既存の `trade_execution_gate` を雑に緩めず、高信頼 gate として残したうえで、別レイヤーとして `Active Trade Plan` を追加する方針は正しい。

現行システムの問題は、`trade_execution_gate` が厳しいこと自体ではない。

問題は、正式 GO 以外の局面で、人間が実務で使える行動計画が十分に提示されていないことである。

したがって Ver03-v1 では、以下を中心方針にする。

- `trade_execution_gate` は高信頼レーンとして維持する。
- `FORMAL_GO` と `ACTIVE_*` を混同しない。
- 通知は方向より先に「取れる行動」を出す。
- 成行よりも、指値・戻り待ち・サポレジ反応・保有ポジション処理を重視する。
- `NO_ACTION` も期待値がない局面を除外する重要分類として扱う。
- 実弾発注 API、秘密鍵、取引所注文送信はまだ禁止する。

---

## 2. repo 確認から見た妥当性

Ver03-v1 の repo には、Active Trade Plan を作る材料がすでにかなり揃っている。

`main.py` の `core_result` には、以下が入っている。

- `current_price`
- `bias`
- `market_regime`
- `market_map`
- `market_map_flags`
- `long_setup`
- `short_setup`
- `primary_setup_side`
- `primary_setup_status`
- `primary_setup_reason`
- `execution_precision_action`
- `breakout_up`
- `breakout_down`
- `volume_ratio`
- `confidence_direction_shadow`
- `confidence_execution_shadow`
- `confidence_wait_shadow`
- `warning_flags`
- `no_trade_flags`
- `risk_flags`
- `data_quality_flag`

つまり、Active Trade Plan は大規模なデータ取得追加なしに実装できる。

一方で、現行の `trade_execution_gate` は以下のように厳格である。

- `phase1_active == false` で blocked
- `primary_setup_status != ready` で blocked
- `confidence_execution_shadow <= 20` で blocked
- `confidence_wait_shadow >= 60` で blocked
- `no_trade_flags` があると blocked
- `data_quality_flag != ok` で blocked

また、`phase1_active` は `primary_setup_status == ready` のときだけ true になり、`watch` は `watch_reference_only` として false になる。

このため、BTC で頻出する以下の局面は、正式 GO になりにくい。

- 戻り売り待ち
- 押し目待ち
- サポート反発
- レジスタンス反落
- ブレイク後の再テスト
- sweep 後の反転
- 走りすぎ後の短期逆行

これはユーザーの運用ミスではなく、設計上自然に起きる。

---

## 3. 既存計画の良い点

既存の `20260607_active_trade_plan_実用化計画.md` は、以下の点で妥当である。

### 3.1 gate を緩めない方針

正式な `trade_execution_gate` を緩めず、高信頼 gate として残す方針は正しい。

正式 gate を安易に緩めると、将来の自動化候補と、実務上の構えが混ざってしまう。

Ver03-v1 では、以下を明確に分離する。

- `FORMAL_GO`: 既存 gate 通過。将来自動化候補。
- `ACTIVE_*`: 人間が使う行動計画。まだ自動発注対象ではない。

### 3.2 成行を厳しくする方針

既存計画は、成行エントリーを厳しく扱っている。

これは妥当である。

BTC は一方向に強く見える局面ほど、現在値で入ると遅いことが多い。

特に、サポート直近のショート、レジスタンス直近のロング、急落直後の追随は損切りになりやすい。

したがって `ACTIVE_MARKET_SMALL` は最も慎重に扱うべき分類である。

### 3.3 `ACTIVE_LIMIT_RETEST` を主戦場にする方針

BTC 実務では、現在値で追うよりも、戻り・押し目・再テストを待つ方が現実的である。

そのため、`ACTIVE_LIMIT_RETEST` を Ver03-v1 の主戦場にする方針は妥当である。

特に、以下のような通知は実務上有用である。

```text
下方向優勢。
ただし成行ショート不可。
60,681-60,883 まで戻れば、戻り売り候補。
現値は短期反発帯。
````

この表現なら、ユーザーは「下方向だから今ショート」ではなく、「下方向だが今は追わず、戻りを待つ」と理解できる。

### 3.4 `POSITION_MANAGEMENT` を入れる方針

実務では、新規エントリーよりも、保有中ポジションの処理の方が重要な場面が多い。

Ver03-v1 では、実ポジションをまだ自動把握しなくても、まずは以下のような「もし保有中なら」を出す価値がある。

* short 保有中なら、サポート反発帯で利確または建値撤退を検討
* long 保有中なら、レジスタンス拒否帯で利確または建値撤退を検討
* 直近高値/安値の突破で撤退条件を提示
* TP1 到達時の部分利確目安を提示

---

## 4. 既存計画の修正点

既存計画は方向性として妥当だが、そのまま実装へ進めるには修正が必要である。

### 4.1 対象ブランチが古い

既存計画の対象ブランチは `ver02.6-v2` のままになっている。

現在の大改修ブランチは `Ver03-v1` である。

したがって、既存計画はそのまま正本として扱わず、Ver03-v1 用の改訂計画として再定義する必要がある。

### 4.2 `NO_ACTION` を弱く扱いすぎている

既存計画では、`NO_ACTION` を最後の手段にし、多くの通知で何らかの構えを出す方針になっている。

これは通知体験としては良い。

しかし、勝てるシステムとしては危険である。

期待値がない局面では、明確に `NO_ACTION` を出すべきである。

`NO_ACTION` は敗北ではない。

以下のような場面を除外する、重要な期待値フィルターである。

* データ不良
* RR 不成立
* サポートとレジスタンスの中間で優位性がない
* 急落直後で反発も戻り売りも条件未確定
* 価格が走りすぎている
* support / resistance 直撃で追随リスクが高い
* 出来高・確定足・再テストが未確認
* macro / ETF flow / risk off の影響が大きく、短期足が不安定

Ver03-v1 では、`NO_ACTION` を「何も出せない状態」ではなく、「期待値がないため何もしない状態」として扱う。

### 4.3 `ACTIVE_MARKET_SMALL` を出しすぎる危険

現行計画では、成行小ロットを分類として用意している。

分類自体は必要である。

ただし、これは最も危険な分類として扱うべきである。

特に、BTC が急落している局面では、`ACTIVE_MARKET_SMALL` が「落ちるナイフを小さく拾う」設計になりやすい。

Ver03-v1 では、成行小ロットは以下の条件を満たす場合だけに絞る。

* 現在値が entry zone 内
* RR current TP1 >= 0.8
* RR current TP2 >= 1.5
* `confidence_execution_shadow >= 24`
* `confidence_wait_shadow < 55`
* fatal no trade flag なし
* data quality が ok
* 主要サポート/レジスタンス直撃ではない
* 15分足で方向確認がある
* SL が明確
* サイズは通常の 1/4 から 1/2

### 4.4 `ACTIVE_COUNTER_SCALP` は新規売買より警告用途を優先する

逆方向短期スキャルは、正式なトレンド転換ではない。

これを新規売買の主戦略にすると危険である。

Ver03-v1 では、まず以下の扱いにする。

* 主用途は、主方向ポジションの利確・建値撤退警告
* 新規エントリーとしては `conditional` を基本にする
* `allowed` は診断で成績確認後に検討する
* サイズは通常の 1/4 程度
* TP は近め
* 長く持たない
* 主要サポート/レジスタンス反応が必須

---

## 5. 最新BTC市場に合わせた設計判断

2026年6月初旬のBTC市場は、強い上昇トレンドを機械的に順張りするより、急落後の戻り・反発・再失速を慎重に扱う環境である。

直近では、BTC は 73,000 ドル台から大きく下落し、60,000 ドル近辺が重要水準として意識されている。

また、Bitcoin ETF からの資金流出、リスク資産からの資金退避、Strategy による一部BTC売却報道、地政学リスク、株式市場への資金シフトなどが重なり、短期的には不安定な環境である。

この環境では、Ver03-v1 の勝ち筋は以下である。

```text
方向を当てるシステム
ではなく、
価格帯・RR・反応確認・保有処理を分けるシステム
```

つまり、通知は以下を明確に分ける必要がある。

* 大局方向はどちらか
* 今すぐ入れるのか
* 入れないなら、どの価格帯まで待つのか
* ブレイクなら何を確認するのか
* 逆方向短期はあるのか
* すでに保有中なら、利確・撤退・保持のどれか
* 正式 GO か、単なる実務 plan か

---

## 6. Ver03-v1 の分類再定義

Ver03-v1 では、分類の優先度を以下にする。

| 分類                       | 役割         | 実務扱い           | 自動化優先度 |
| ------------------------ | ---------- | -------------- | ------ |
| `FORMAL_GO`              | 既存 gate 通過 | 最上位。将来自動化候補    | 高      |
| `ACTIVE_LIMIT_RETEST`    | 戻り売り・押し目待ち | 主戦場            | 高      |
| `POSITION_MANAGEMENT`    | 保有中ポジション処理 | 実務価値が最も高い      | 高      |
| `ACTIVE_BREAKOUT_FOLLOW` | ブレイク追随     | 確定足・出来高・再テスト必須 | 中      |
| `ACTIVE_COUNTER_SCALP`   | 逆方向短期      | 警告用途優先。小サイズ限定  | 低〜中    |
| `ACTIVE_MARKET_SMALL`    | 現在値で小さく入る  | 最も危険。条件を絞る     | 低      |
| `NO_ACTION`              | 期待値なし      | 正常分類。無理に入らない   | 必須     |

重要なのは、`NO_ACTION` を最後に追いやりすぎないことである。

期待値がないなら、`NO_ACTION` は正しい出力である。

---

## 7. Active Trade Plan v1 の判定方針

### 7.1 FORMAL_GO

条件:

* `trade_execution_gate == pass`
* `paper_order_status == planned`
* data quality が ok
* fatal no trade flag なし

扱い:

* 最上位
* 将来自動化候補
* ただし Ver03-v1 ではまだ実弾発注しない

### 7.2 ACTIVE_LIMIT_RETEST

主戦場。

条件案:

* 対象 side の entry zone が存在
* SL / TP が存在
* zone mid 基準で RR が成立
* fatal no trade flag なし
* 現在値が zone 外でもよい
* ただし zone までの距離が遠すぎる場合は `watch` または `conditional`
* 15分足または1時間足で再失速・再反発を条件にする

最低 RR 案:

* `rr_zone_mid_tp1 >= 1.0`
* `rr_zone_mid_tp2 >= 1.8`

通知例:

```text
成行ショート不可。
60,681-60,883 まで戻り、15分足で再失速するなら戻り売り候補。
```

### 7.3 ACTIVE_MARKET_SMALL

最も絞る。

条件案:

* 現在値が entry zone 内
* `rr_current_tp1 >= 0.8`
* `rr_current_tp2 >= 1.5`
* `confidence_execution_shadow >= 24`
* `confidence_wait_shadow < 55`
* data quality が ok
* fatal no trade flag なし
* 主要 support / resistance 直撃ではない
* SL が明確
* 追いかけ禁止に該当しない

扱い:

* サイズ小さめ
* SL 同時設定必須
* paper 検証で成績が悪ければさらに降格

### 7.4 ACTIVE_BREAKOUT_FOLLOW

条件案:

* `breakout_up` または `breakout_down`
* `volume_ratio >= trigger_volume_ratio_threshold`
* 確定足後
* 役割転換または再テストを確認
* 追随成行ではなく、再評価を原則にする

扱い:

* breakout 直後の飛び乗りは避ける
* false breakout を重点的に検出する
* 15分足単独より、1時間足の文脈を優先する

### 7.5 ACTIVE_COUNTER_SCALP

条件案:

long counter scalp:

* 大局 bias が short または downtrend
* 現在値が long entry zone 内、または主要サポート直近
* `major_support_rejection` または `short_into_major_support`
* short の成行が blocked
* TP1 が近く SL が明確

short counter scalp:

* 大局 bias が long または uptrend
* 現在値が short entry zone 内、または主要レジスタンス直近
* `major_resistance_rejection` または `long_into_major_resistance`
* long の成行が blocked
* TP1 が近く SL が明確

扱い:

* まずは `conditional`
* 通常サイズの 1/4
* TP 近め
* 保有中ポジションへの警告として優先表示

### 7.6 POSITION_MANAGEMENT

v1 では実ポジションをまだ知らない前提で、「もし保有中なら」を出す。

例:

```text
short 保有中:
現値は主要サポート反発帯。
利確または建値撤退を優先。
60,883 上抜けで下落継続シナリオを弱める。

long 保有中:
60,940 付近で部分利確。
60,322 割れで撤退検討。
```

v2 以降で `logs/manual_positions.csv` を追加し、手動ポジションを active plan に反映する。

---

## 8. 通知UIの方針

通知は、方向より先に行動を出す。

### 8.1 件名

悪い例:

```text
[通常監視・実行不可] 下方向バイアス | サポート割れ後の戻り売り確認
```

改善例:

```text
[戻り売り待ち・成行ショート不可] 下方向優勢 / 指値 60,681-60,883 / 現値は反発帯
```

または:

```text
[現値ショート不可・短期反発注意] 下目線 / short待ち 60,681-60,883 / long反発 60,322-60,524
```

### 8.2 HTML hero

hero の表示順は以下にする。

1. 今すぐ成行できるか
2. 指値・戻り待ちはどこか
3. ブレイク追随なら何を待つか
4. 逆方向短期はあるか
5. 保有中ならどう処理するか
6. 大局方向
7. 正式 GO の有無

方向スコアは最上段に出さない。

方向スコアは「大局判断」セクションへ下げる。

---

## 9. 実装順序

Ver03-v1 では、以下の順で進める。

### Step 1: 設計メモと正本整理

* 本メモを保存する。
* 既存計画との差分を明確にする。
* 対象ブランチを `Ver03-v1` に統一する。

### Step 2: `active_plan.py` 最小実装

追加:

* `src/trade/active_plan.py`
* `tests/test_active_trade_plan.py`

必須関数:

```python
def classify_zone_position(side: str, price: float, entry_low: float, entry_high: float) -> str:
    ...

def rr_for_entry(side: str, entry_price: float, stop: float, target: float) -> float | None:
    ...

def build_active_trade_plan(...):
    ...
```

最初の fixture は `20260606_230500` 型を使う。

期待:

* short side の `market_entry_status` は `blocked`
* short side の `limit_entry_status` は `allowed`
* long side の `counter_scalp_status` は `conditional`
* headline は「成行ショート不可」「戻り売り待ち」「短期反発帯」の意味を含む

### Step 3: `main.py` へ payload 接続

* `core_result["active_trade_plan"]` を追加
* `core_result["active_primary_action"]` を追加
* `core_result["active_headline"]` を追加

ただし、以下は変更しない。

* `trade_execution_gate`
* `paper_order_status`
* `opportunity_gate`
* 通知件名
* HTML hero

### Step 4: 通知件名と HTML hero を Active Plan 優先へ変更

* `src/ai/summary.py`
* `src/presentation/sanitize.py`
* `src/notification/detail_page.py`

### Step 5: CSV と diagnostics

* `src/storage/csv_logger.py` に active plan 列を追加
* `tools/log_feedback.py` に `active_trade_plan_diagnostics` を追加

集計項目:

* primary_action 別件数
* market entry allowed / blocked 件数
* limit retest allowed 件数
* counter scalp conditional 件数
* MFE / MAE
* TP1 先行率
* sl_hit
* missed_opportunity
* `NO_ACTION` が妥当か
* `ACTIVE_MARKET_SMALL` が多すぎないか

### Step 6: active paper positions

`paper_positions.csv` または別ログで、active plan 別の紙検証を行う。

候補:

* `active_market_small`
* `active_limit_retest`
* `active_counter_scalp`
* `active_breakout_follow`

### Step 7: manual position tracking

v2 以降で検討。

候補:

* `logs/manual_positions.csv`
* 手動入力の side / entry / size / stop / tp
* 通知上の利確・撤退・保持判断へ反映

---

## 10. やってはいけないこと

Ver03-v1 では以下を禁止する。

* `trade_execution_gate` の pass 条件を雑に緩める
* `ACTIVE_*` を `FORMAL_GO` と表示する
* `ACTIVE_MARKET_SMALL` を乱発する
* `NO_ACTION` を失敗分類として扱う
* 方向スコアだけで売買判断させる
* `下方向バイアス` を `今ショートしてよい` と誤読させる
* `上方向バイアス` を `今ロングしてよい` と誤読させる
* `trend_flip_confirmed_up` 単独を強い long 根拠に戻す
* 実弾発注 API を追加する
* 取引所 API キーや秘密鍵を扱う
* 自動注文送信を実装する

---

## 11. 最終判断

既存の Active Trade Plan 計画は、Ver03-v1 の中核として採用してよい。

ただし、以下の修正を入れてから実装へ進む。

1. 対象ブランチを `Ver03-v1` に修正する。
2. `ACTIVE_LIMIT_RETEST` を主戦場にする。
3. `POSITION_MANAGEMENT` を高優先にする。
4. `ACTIVE_MARKET_SMALL` は最も厳しく制限する。
5. `ACTIVE_COUNTER_SCALP` は新規売買よりも、まず保有ポジション警告として使う。
6. `NO_ACTION` を正常な期待値フィルターとして扱う。
7. active plan 別の紙検証と diagnostics を必須にする。
8. 実弾発注はまだ禁止する。

Ver03-v1 が目指すべき状態は、以下である。

```text
大局方向: short
成行: 不可
指値: short 60,681-60,883
逆方向短期: long 60,322-60,524 条件付き
保有中: short は利確/建値撤退警戒
正式GO: なし
```

この形なら、ユーザーは「方向」ではなく「実際にどう構えるか」を読める。

Ver03-v1 の勝ち筋は、方向を当てることだけではない。

価格帯、RR、反応確認、ポジション処理、そして見送り判断を分離し、毎回の通知を実務行動計画へ変えることである。
