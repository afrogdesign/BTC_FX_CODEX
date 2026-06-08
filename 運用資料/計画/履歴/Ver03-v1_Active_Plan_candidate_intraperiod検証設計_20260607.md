# Ver03-v1 Active Plan candidate intraperiod 検証設計

作成日: 2026-06-07 JST  
対象ブランチ: Ver03-v1  
対象repo: afrogdesign/BTC_FX_CODEX

## 1. 結論

Active Plan candidate の次段階は、forward close ベースの暫定評価から、intraperiod の高値・安値を使った候補別検証へ進むことである。

ただし、この作業は既存の `paper_positions.csv` や `paper_order_status` と混ぜない。

まずは独立した検証レーンとして、以下を新設する。

- `active_plan_candidate_intraperiod_outcomes.csv`
- `build_active_plan_candidate_intraperiod_outcomes()`
- `ACTIVE_PLAN_CANDIDATE_INTRAPERIOD_HEADER`
- 後続で `active_plan_candidate_intraperiod_outcomes_report()`

このレーンでは、`active_plan_paper_candidates.csv` の各候補について、15m OHLCV などの intraperiod 足を使い、entry 到達、TP1 / TP2 / SL 先行、timeout、candidate entry price 基準の MFE / MAE を評価する。

重要:

- 実弾発注ではない。
- 自動注文送信ではない。
- 既存 `paper_positions.csv` にはまだ接続しない。
- `ACTIVE_*` を正式GOとして扱わない。
- `trade_execution_gate=pass` と `ACTIVE_*` を混同しない。
- まず独立CSVで挙動を観察する。

## 2. 背景

現時点では、Active Plan candidate の評価は forward close ベースである。

現在できているもの:

- `active_plan_paper_candidates.csv`
- `active_plan_candidate_outcomes.csv`
- `active_plan_candidate_outcomes_YYYYMMDD.md`

ただし、現在の candidate outcomes は以下の限界を持つ。

- 12h / 24h の forward close しか見ていない。
- entry zone に到達したかを見ていない。
- TP1 / TP2 / SL に途中到達したかを見ていない。
- TP と SL のどちらが先に到達したかを見ていない。
- candidate entry price 基準の MFE / MAE を再計算していない。
- timeout を判定していない。

そのため、実務的な紙検証としてはまだ弱い。

BTC の実務では、以下が重要である。

- 指値候補が実際に entry zone に届いたか。
- 届いた後、TP と SL のどちらに先に触れたか。
- entry 後にどれくらい順行したか。
- entry 後にどれくらい逆行したか。
- timeout まで何も起きなかったか。
- `ACTIVE_MARKET_SMALL` が過剰売買になっていないか。
- `ACTIVE_LIMIT_RETEST` が主戦場として機能しているか。
- `ACTIVE_COUNTER_SCALP` が conditional として妥当か。

## 3. 入力CSV

### 3.1 Active Plan candidate 入力

主入力は以下。

```text
logs/csv/active_plan_paper_candidates.csv
````

このCSVは `build_active_plan_paper_candidates()` により生成済み。

主要列:

* `candidate_id`
* `source_signal_id`
* `timestamp_jst`
* `active_primary_action`
* `candidate_type`
* `candidate_status`
* `side`
* `entry_mode`
* `entry_price`
* `entry_zone_low`
* `entry_zone_high`
* `stop_loss`
* `tp1`
* `tp2`
* `rr_current_tp1`
* `rr_current_tp2`
* `rr_zone_mid_tp1`
* `rr_zone_mid_tp2`
* `market_entry_status`
* `limit_entry_status`
* `counter_scalp_status`
* `breakout_status`
* `active_subject_label`
* `active_headline`
* `next_condition`

### 3.2 OHLCV 入力

intraperiod 検証には、candidate timestamp 以降の OHLCV が必要である。

推奨足:

```text
15m OHLCV
```

理由:

* Active Plan は短期の実務行動計画である。
* 1h 足では entry / TP / SL の先行順序が粗くなる。
* 1m 足は理想だが、データ量と既存システム負荷が大きい。
* まず 15m 足で設計し、必要なら後続で 5m / 1m に拡張する。

想定入力形式:

```text
timestamp_jst, open, high, low, close
```

または以下も許容する設計にする。

```text
timestamp_utc, open, high, low, close
```

実装時の方針:

* repo 内に既存 OHLCV CSV / cache がある場合は、それを優先して使う。
* 既存の OHLCV 保存場所が確認できない場合は、builder の引数 `--ohlcv-path` で明示指定する。
* デフォルト推定パスは実装前レビューで決める。
* OHLCV が存在しない場合、実装は落とさず、`evaluation_status=no_ohlcv` として空結果を出せるようにする。

## 4. 出力CSV

新設するCSV:

```text
logs/csv/active_plan_candidate_intraperiod_outcomes.csv
```

新設する header 名:

```python
ACTIVE_PLAN_CANDIDATE_INTRAPERIOD_HEADER
```

推奨列:

```text
candidate_id
source_signal_id
timestamp_jst
active_primary_action
candidate_type
candidate_status
side
entry_mode
entry_price
entry_zone_low
entry_zone_high
stop_loss
tp1
tp2
active_subject_label
active_headline
next_condition
evaluation_status
entry_reached
entry_reached_at_jst
entry_reached_price
first_exit
first_exit_at_jst
first_exit_price
tp1_reached
tp1_reached_at_jst
tp2_reached
tp2_reached_at_jst
sl_reached
sl_reached_at_jst
timeout_reached
timeout_at_jst
mfe
mae
mfe_price
mae_price
max_favorable_at_jst
max_adverse_at_jst
bars_evaluated
evaluation_window_hours
notes
```

## 5. evaluation_status

`evaluation_status` は以下を使う。

```text
complete
not_entered
timeout
no_ohlcv
invalid_candidate
pending
```

意味:

* `complete`: entry 後に TP / SL / timeout のいずれかで評価完了。
* `not_entered`: 評価期間内に entry 条件へ到達しなかった。
* `timeout`: entry 後、TP / SL に到達せず timeout。
* `no_ohlcv`: 必要な OHLCV がない。
* `invalid_candidate`: candidate に必要な価格情報が不足。
* `pending`: 評価期間がまだ十分に経過していない。

## 6. entry 到達判定

### 6.1 market entry

`entry_mode == "market"` の場合:

* candidate timestamp 以降の最初の足を entry 足とする。
* `entry_price` は candidate の `entry_price` を使う。
* `entry_reached=true`
* `entry_reached_at_jst` は candidate timestamp 以降の最初の OHLCV timestamp。
* ただし、OHLCV がない場合は `evaluation_status=no_ohlcv`。

対象:

* `active_market_small`

### 6.2 limit zone mid

`entry_mode == "limit_zone_mid"` の場合:

候補の `side` に応じて、entry zone に価格が触れたかを判定する。

long:

* `low <= entry_price <= high` なら entry 到達。
* より保守的には `low <= entry_zone_high and high >= entry_zone_low` でも zone touch とみなせる。
* Ver03-v1 初期実装では `entry_price` 到達を採用する。

short:

* `low <= entry_price <= high` なら entry 到達。
* Ver03-v1 初期実装では `entry_price` 到達を採用する。

対象:

* `active_limit_retest`

補足:

* zone touch 判定と mid touch 判定は結果が異なる可能性がある。
* 初期実装では mid touch を採用し、後続で zone touch 版と比較できるようにする。

### 6.3 market conditional

`entry_mode == "market_conditional"` の場合:

現時点では条件成立を自動判定しない。

初期実装では以下の扱いにする。

* candidate timestamp 以降の最初の足を仮 entry 足とする。
* `candidate_status=conditional` を維持する。
* `notes` に `conditional_candidate_assumed_market_entry` を入れる。
* 後続で条件成立判定を追加する。

対象:

* `active_counter_scalp`

理由:

* counter scalp は、本来 15m 足の反発/反落確認が必要。
* ただし初期の検証では、仮に入った場合のリスクを把握するため、market conditional として暫定評価する。

## 7. TP / SL 到達判定

entry 到達後の足から、high / low を使って TP1 / TP2 / SL 到達を判定する。

### 7.1 long

long の場合:

* TP1 到達: `high >= tp1`
* TP2 到達: `high >= tp2`
* SL 到達: `low <= stop_loss`

### 7.2 short

short の場合:

* TP1 到達: `low <= tp1`
* TP2 到達: `low <= tp2`
* SL 到達: `high >= stop_loss`

## 8. 同一足で TP と SL が同時に見える場合

15m 足では、同一足の中で TP と SL のどちらが先に到達したか分からないことがある。

この場合の初期方針は保守的にする。

### 8.1 long

同一足で以下が両方成立した場合:

* `high >= tp1`
* `low <= stop_loss`

結果:

* `first_exit=ambiguous_sl_first`
* 実務上は loss 寄りに扱う。
* `notes` に `same_bar_tp_sl_ambiguous_conservative_sl` を入れる。

### 8.2 short

同一足で以下が両方成立した場合:

* `low <= tp1`
* `high >= stop_loss`

結果:

* `first_exit=ambiguous_sl_first`
* 実務上は loss 寄りに扱う。
* `notes` に `same_bar_tp_sl_ambiguous_conservative_sl` を入れる。

理由:

* 同一足の順序が不明な場合、勝ち寄りに評価すると過大評価になる。
* 初期検証は保守的にする。

## 9. first_exit

`first_exit` は以下を使う。

```text
tp1
tp2
sl
timeout
not_entered
ambiguous_sl_first
pending
no_ohlcv
invalid_candidate
```

初期実装では、TP2 より先に TP1 を評価する。

原則:

* TP1 に先に到達したら `first_exit=tp1`
* SL に先に到達したら `first_exit=sl`
* 同一足で TP1 と SL が同時に見える場合は `ambiguous_sl_first`
* entry しなければ `not_entered`
* 評価期間不足なら `pending`
* OHLCV がなければ `no_ohlcv`

## 10. timeout 判定

初期の timeout は以下にする。

```text
evaluation_window_hours = 24
```

entry 到達後、24h 以内に TP1 / TP2 / SL へ到達しない場合:

* `timeout_reached=true`
* `first_exit=timeout`
* `evaluation_status=timeout`

ただし、candidate timestamp から 24h 分の OHLCV が揃っていない場合:

* `evaluation_status=pending`
* `first_exit=pending`

## 11. MFE / MAE

candidate entry price 基準で MFE / MAE を計算する。

### 11.1 long

long:

* MFE = `max(high_after_entry) - entry_price`
* MAE = `entry_price - min(low_after_entry)`

### 11.2 short

short:

* MFE = `entry_price - min(low_after_entry)`
* MAE = `max(high_after_entry) - entry_price`

計算対象期間:

* entry 到達後から first_exit まで。
* first_exit が timeout の場合は timeout まで。
* first_exit が pending の場合は取得済み OHLCV の範囲まで。
* not_entered の場合は MFE / MAE は空または 0 とする。初期実装では空文字を推奨する。

## 12. 日付・時刻

timestamp は JST を基準にする。

入力 OHLCV が UTC の場合:

* 実装で JST に変換する。
* 出力列は `_jst` suffix を使う。

初期実装の出力:

* `entry_reached_at_jst`
* `first_exit_at_jst`
* `tp1_reached_at_jst`
* `tp2_reached_at_jst`
* `sl_reached_at_jst`
* `timeout_at_jst`
* `max_favorable_at_jst`
* `max_adverse_at_jst`

## 13. CLI 設計

新設する CLI:

```bash
python tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes
```

引数:

```text
--candidates-path
--ohlcv-path
--output-csv
--date-from
--date-to
--evaluation-window-hours
```

デフォルト:

```text
candidates_path = logs/csv/active_plan_paper_candidates.csv
output_csv = logs/csv/active_plan_candidate_intraperiod_outcomes.csv
evaluation_window_hours = 24
```

`ohlcv_path` は初期実装では必須にしてもよい。
ただし、既存repoに標準OHLCVファイルが確認できた場合は、それをデフォルトにしてよい。

## 14. daily-sync 接続方針

初期実装では、intraperiod outcomes builder を作ってテスト固定するまで daily-sync へ接続しない。

推奨順序:

1. Markdown 設計を作る。
2. `build_active_plan_candidate_intraperiod_outcomes()` を単体実装する。
3. fixture CSV で long / short / not_entered / timeout / ambiguous をテストする。
4. report builder を作る。
5. daily-sync に接続する。
6. report family registry に登録する。

理由:

* OHLCV 入力が不安定な状態で daily-sync に入れると、標準運用に壊れた成果物が混ざる。
* まず単体 builder とテストを固定する。

## 15. 既存 paper_positions.csv との関係

現時点では接続しない。

理由:

* 既存 `paper_positions.csv` は正式 gate / opportunity gate 系の paper management と結びついている。
* Active Plan は watch / conditional / limit retest を含む。
* 両者を混ぜると正式GOと実務行動計画の成績が混ざる。
* Active Plan intraperiod 検証が安定するまで、独立CSVで評価する。

将来的に接続する場合も、以下の条件を満たしてからにする。

* `active_limit_retest` の entry 到達後 TP1 / SL 比率が十分に見えている。
* `active_market_small` が過剰売買になっていない。
* `active_counter_scalp` が conditional として機能している。
* `NO_ACTION` が期待値フィルターとして機能している。
* 既存 paper_positions と分けて表示できる。

## 16. report 設計

intraperiod outcomes 実装後に、以下の report を追加する。

```text
active_plan_candidate_intraperiod_outcomes_YYYYMMDD.md
```

集計項目:

* candidate_type 別 count
* entry_reached rate
* TP1 first rate
* SL first rate
* timeout rate
* ambiguous rate
* average MFE
* average MAE
* side 別成績
* entry_mode 別成績
* 代表例
* `ACTIVE_LIMIT_RETEST` と `ACTIVE_MARKET_SMALL` の比較
* `ACTIVE_COUNTER_SCALP` の conditional 妥当性

## 17. 最初の実装テスト候補

最初の実装では、以下の fixture を使う。

### 17.1 long TP1 first

* side: long
* entry_price: 100
* tp1: 110
* tp2: 120
* stop_loss: 95
* OHLCV:

  * high が 110 以上になる
  * low は 95 を割らない
* expected:

  * entry_reached=true
  * first_exit=tp1

### 17.2 short SL first

* side: short
* entry_price: 100
* tp1: 90
* tp2: 80
* stop_loss: 105
* OHLCV:

  * high が 105 以上になる
  * low が 90 に届かない
* expected:

  * entry_reached=true
  * first_exit=sl

### 17.3 limit not entered

* entry_mode: limit_zone_mid
* entry_price: 100
* OHLCV:

  * high / low が entry_price に触れない
* expected:

  * entry_reached=false
  * first_exit=not_entered
  * evaluation_status=not_entered

### 17.4 same bar ambiguous

* side: long
* entry_price: 100
* tp1: 110
* stop_loss: 95
* same bar:

  * high >= 110
  * low <= 95
* expected:

  * first_exit=ambiguous_sl_first
  * notes includes `same_bar_tp_sl_ambiguous_conservative_sl`

### 17.5 timeout

* entry reached
* TP / SL unreached
* evaluation window complete
* expected:

  * first_exit=timeout
  * evaluation_status=timeout

### 17.6 pending

* entry reached
* TP / SL unreached
* evaluation window not complete
* expected:

  * first_exit=pending
  * evaluation_status=pending

## 18. 実装前の確認事項

実装に進む前に、ChatGPT が以下を repo 上で確認する。

* 既存の OHLCV 保存ファイルがあるか。
* 既存の価格履歴 cache があるか。
* `update_outcomes()` がどのデータソースから forward price / MFE / MAE を作っているか。
* 15m OHLCV を再利用できるか。
* CSV の timestamp が JST か UTC か。
* テスト fixture に合わせて helper をどこへ置くか。
* `tools/log_feedback.py` にさらに関数を追加してよいか、分割ファイル化するか。

## 19. 安全条件

以下は守る。

* 実弾発注 API は追加しない。
* 取引所 API キーは扱わない。
* 秘密鍵は扱わない。
* 自動注文送信はしない。
* `ACTIVE_*` を正式GOとして扱わない。
* `trade_execution_gate=pass` と `ACTIVE_*` を混同しない。
* `paper_positions.csv` への接続は、独立検証が十分進むまで行わない。
* OHLCV がない場合に無理に外部取得しない。
* Codex に設計判断をさせない。
* ChatGPT が設計し、Codex は指定内容をファイルへ反映するだけにする。

## 20. 次の作業

この設計ファイル作成後、次の作業は `BTCFX-20260607-052` とする。

候補:

`Active Plan candidate intraperiod 検証実装前 repo 調査`

目的:

* repo 内の OHLCV / price history / update_outcomes 周辺を確認する。
* どのファイル・関数を使って intraperiod 判定を実装するか確定する。
* その結果を Markdown に残す。

その後、`BTCFX-20260607-053` で最小実装に進む。
