# Ver03-v1 Active Trade Plan 実装棚卸し

作成日: 2026-06-07 JST  
対象ブランチ: Ver03-v1  
対象repo: afrogdesign/BTC_FX_CODEX

## 1. 結論

Ver03-v1 の Active Trade Plan は、第一段階として実用通知・記録・診断・日次確認まで接続済みになった。

現時点でできることは以下。

- 毎回の通知で、正式GOとは別に Active Plan を生成する。
- 通知件名で、方向より先に「取れる行動」を表示する。
- HTML hero で、方向より先に Active Plan を表示する。
- `trades.csv` に Active Plan の主要列を保存する。
- Active Plan の出方を diagnostics で確認する。
- Active Plan と `signal_outcomes.csv` を join して effectiveness を確認する。
- Active Plan 候補を `active_plan_paper_candidates.csv` に分離保存する。
- Active Plan 候補と outcome を join して `active_plan_candidate_outcomes.csv` を生成する。
- daily-sync で candidate CSV、candidate outcome CSV、candidate outcome report を標準成果物として生成する。
- Active Plan 系 report family が registry から落ちないようにテスト固定する。

ただし、現時点ではまだ本格的な紙検証ではない。

現在の candidate outcomes は forward close ベースの暫定評価であり、intraperiod の高値・安値による TP / SL 到達、entry zone 到達、候補 entry price 基準の MFE / MAE 再計算、timeout 判定は未実装である。

したがって、次の大きな作業は `active_plan_candidate_outcomes` を本格検証へ拡張する前の設計固定である。

## 2. 完了済みの実装範囲

### 2.1 Active Plan core

`src/trade/active_plan.py` を追加し、Active Trade Plan の最小コア判定を実装した。

主な分類:

- `FORMAL_GO`
- `ACTIVE_MARKET_SMALL`
- `ACTIVE_LIMIT_RETEST`
- `ACTIVE_BREAKOUT_FOLLOW`
- `ACTIVE_COUNTER_SCALP`
- `POSITION_MANAGEMENT`
- `NO_ACTION`

現時点では、`ACTIVE_*` は実弾発注ではなく、人間が確認する行動計画である。

### 2.2 main payload 接続

`main.py` に Active Plan payload を接続した。

追加された top-level payload:

- `active_trade_plan`
- `active_primary_action`
- `active_headline`

ただし、既存の `trade_execution_gate`、`opportunity_gate`、`paper_order_status` の挙動は変更していない。

### 2.3 notification context 接続

`src/presentation/sanitize.py` に Active Plan 用 context を追加した。

追加された主な context:

- `active_primary_action`
- `active_headline`
- `active_subject_label`
- `active_market_entry_now`
- `active_limit_retest_entry`
- `active_breakout_follow_entry`
- `active_countertrend_scalp_entry`
- `active_position_management`

Active Plan が未設定または壊れた値でも safe default を返す。

### 2.4 通知件名

`src/ai/summary.py` の件名生成を Active Plan 優先にした。

main 通知では、方向ラベルより前に `active_subject_label` を出す。  
`ACTIVE_*` は `実弾不可・行動計画` と明記する。

ただし、以下は legacy 件名を維持する。

- `notification_kind == "attention"`
- `trade_execution_gate == "pass" and paper_order_status == "planned"`

### 2.5 HTML hero

`src/notification/detail_page.py` の hero を Active Plan 優先にした。

HTML detail page の最初に以下を表示する。

- Active Plan
- 成行
- 指値・戻り待ち
- ブレイク追随
- 逆方向短期
- 保有中処理

ただし、attention 通知と正式 gate 通過時は既存の意味を壊さない表示を維持している。

### 2.6 trades.csv logging

`src/storage/csv_logger.py` に Active Plan 列を追加した。

追加された主な列:

- `active_plan_version`
- `active_primary_action`
- `active_subject_label`
- `active_headline`
- `active_market_entry_long`
- `active_market_entry_short`
- `active_limit_retest_long`
- `active_limit_retest_short`
- `active_breakout_follow_long`
- `active_breakout_follow_short`
- `active_countertrend_scalp_long`
- `active_countertrend_scalp_short`
- `active_position_management_long`
- `active_position_management_short`
- `active_trade_plan_json`

これにより、各通知サイクルの Active Plan 判定が `trades.csv` に残る。

### 2.7 Active Plan diagnostics

`tools/log_feedback.py` に `build_active_trade_plan_diagnostics_report()` を追加した。

この report は `trades.csv` を直接読み、Active Plan の出方を確認する。

確認できるもの:

- action 別件数
- 成行 allowed 件数
- 指値・戻り待ち allowed 件数
- ブレイク armed 件数
- 逆方向短期 conditional 件数
- `NO_ACTION` 比率
- 代表例

### 2.8 Active Plan effectiveness

`tools/log_feedback.py` に `build_active_trade_plan_effectiveness_report()` を追加した。

この report は `trades.csv` と `signal_outcomes.csv` を `signal_id` で join し、Active Plan action 別の値動き結果を確認する。

確認できるもの:

- direction 正解率
- TP1先行率
- 平均MFE24h
- 平均MAE24h
- action 別 effectiveness
- 代表例

ただし、これは signal 単位の outcome であり、candidate entry price 基準ではない。

### 2.9 Active Plan paper candidates

`tools/log_feedback.py` に `build_active_plan_paper_candidates()` を追加した。

`trades.csv` の `active_trade_plan_json` を読み、以下の候補を `active_plan_paper_candidates.csv` に分離保存する。

- `active_market_small`
- `active_limit_retest`
- `active_counter_scalp`

`ACTIVE_COUNTER_SCALP` は `conditional` 候補として保存する。

まだ既存 `paper_positions.csv` には接続していない。

### 2.10 Active Plan candidate outcomes

`tools/log_feedback.py` に `build_active_plan_candidate_outcomes()` を追加した。

`active_plan_paper_candidates.csv` と `signal_outcomes.csv` を join し、候補ごとの暫定 outcome を `active_plan_candidate_outcomes.csv` に出す。

現時点の評価は forward close ベースである。

出力できるもの:

- `candidate_delta_12h`
- `candidate_delta_24h`
- `candidate_result_12h`
- `candidate_result_24h`
- `tp1_close_reached_24h`
- `tp2_close_reached_24h`
- `sl_close_reached_24h`

注意: これは 24h 終値が水準を超えたかを見るだけで、途中到達判定ではない。

### 2.11 Active Plan candidate outcomes report

`tools/log_feedback.py` に `build_active_plan_candidate_outcomes_report()` を追加した。

`active_plan_candidate_outcomes.csv` を読み、Markdown report を生成する。

確認できるもの:

- 候補タイプ別の 24h favorable
- TP1 close 到達率
- SL close 到達率
- 平均delta
- side 別集計
- status 集計
- 代表例

### 2.12 daily-sync 接続

`daily_sync()` に以下を接続した。

- `build_active_plan_paper_candidates()`
- `build_active_plan_candidate_outcomes()`
- `build_active_plan_candidate_outcomes_report()`

daily-sync 実行時に以下が標準成果物として生成される。

1. `logs/csv/active_plan_paper_candidates.csv`
2. `logs/csv/active_plan_candidate_outcomes.csv`
3. `運用資料/reports/analysis/active_plan_candidate_outcomes_YYYYMMDD.md`

### 2.13 report family registry

`REPORT_FAMILY_SPECS` に以下が登録済み。

- `active_trade_plan_diagnostics`
- `active_trade_plan_effectiveness`
- `active_plan_candidate_outcomes`

`tests/test_active_plan_report_family_registry.py` で、登録・pattern・date_pattern・search_roots・section・label・purpose を固定した。

## 3. まだ実装していない範囲

### 3.1 intraperiod TP / SL 到達判定

未実装。

現在の `active_plan_candidate_outcomes.csv` は forward close ベースであり、途中の高値・安値を見ていない。

未実装の判定:

- entry zone に到達したか
- entry 後に TP1 に到達したか
- entry 後に TP2 に到達したか
- entry 後に SL に到達したか
- TP と SL のどちらが先に到達したか
- timeout になったか

### 3.2 candidate entry price 基準の MFE / MAE 再計算

未実装。

現在の MFE / MAE は signal outcome 側の値を参照している。  
候補ごとに entry price が異なるため、本来は candidate entry price 基準で MFE / MAE を再計算する必要がある。

### 3.3 active_plan_paper_positions.csv

未実装。

既存 `paper_positions.csv` とは接続していない。  
Active Plan 候補は現時点では `active_plan_paper_candidates.csv` と `active_plan_candidate_outcomes.csv` に分離している。

### 3.4 既存 paper_positions.csv への接続

未実装。

現時点では、既存の `paper_positions.csv`、`paper_order_status`、`build_paper_positions()` の挙動は変更していない。

これは安全のため正しい。

### 3.5 実弾発注 API

未実装。  
追加していない。  
追加してはいけない。

### 3.6 自動注文送信

未実装。  
追加していない。  
追加してはいけない。

## 4. 現時点の設計判断

### 4.1 trade_execution_gate は残す

`trade_execution_gate` は高信頼 gate として残す。

`FORMAL_GO` と `ACTIVE_*` は混同しない。  
正式 gate 通過時は既存の正式候補表示を維持する。

### 4.2 Active Plan は実務行動計画であり、実弾発注ではない

`ACTIVE_*` は、通知利用者が相場をどう構えるかを判断するための補助情報である。

自動発注、実弾発注、注文APIとは切り離す。

### 4.3 Active Plan candidate は既存 paper_positions と分離する

現時点では、Active Plan 候補を既存 paper_positions に混ぜない。

理由:

- 既存 paper_positions は `opportunity_gate=pass` と密接に関係している。
- Active Plan は `watch` や `conditional` を含む。
- 両者を混ぜると、正式 gate と実務 plan の評価が混ざる。
- まず独立CSVで挙動を見るのが安全。

### 4.4 forward close ベース評価は暫定

現在の `active_plan_candidate_outcomes.csv` と report は、あくまで 12h / 24h forward close ベースの暫定評価である。

これだけで TP/SL の実到達を判断してはいけない。

### 4.5 次にやるなら intraperiod 検証の設計を先に固定する

次の大きな実装は、候補ごとの intraperiod TP / SL / timeout 検証である。

ただし、これは影響範囲が大きいため、いきなり実装せず、先に Markdown 設計を作る。

## 5. 次の推奨作業

次は `BTCFX-20260607-051` として、以下の Markdown 設計を作る。

作業名:

`Active Plan candidate intraperiod 検証設計`

目的:

- どのCSVを入力にするか決める。
- どのOHLCVデータを使うか決める。
- entry 到達判定をどうするか決める。
- TP / SL の先行判定をどうするか決める。
- timeout 判定をどうするか決める。
- output CSV の列を決める。
- daily-sync へ接続するタイミングを決める。
- 既存 `paper_positions.csv` へ接続するかどうかを保留条件つきで整理する。

推奨 output:

`運用資料/計画/Ver03-v1_Active_Plan_candidate_intraperiod検証設計_20260607.md`

この次の作業でも、まず Markdown 設計のみとする。  
コード実装はその後にする。

## 6. 次の実装候補

設計後の実装候補は以下。

1. `ACTIVE_PLAN_CANDIDATE_INTRAPERIOD_HEADER` を追加する。
2. `build_active_plan_candidate_intraperiod_outcomes()` を追加する。
3. 15m OHLCV を使って candidate ごとに entry 到達を判定する。
4. entry 後の high / low で TP1 / TP2 / SL 先行を判定する。
5. timeout を判定する。
6. candidate entry price 基準の MFE / MAE を計算する。
7. `active_plan_candidate_intraperiod_outcomes.csv` を出力する。
8. report builder を追加する。
9. daily-sync に接続する。
10. 十分に安定したら、既存 paper_positions との関係を再検討する。

## 7. 安全条件

今後も以下は守る。

- 実弾発注 API は追加しない。
- 取引所 API キーは扱わない。
- 秘密鍵は扱わない。
- 自動注文送信はしない。
- `ACTIVE_*` を正式GOとして扱わない。
- `trade_execution_gate=pass` と `ACTIVE_*` を混同しない。
- `paper_positions.csv` への接続は、独立検証が十分進むまで行わない。
- Codex に設計判断をさせない。
- ChatGPT が設計し、Codex は指定内容をファイルへ反映するだけにする。

## 8. 現時点の到達点

Ver03-v1 は、「正式GOが少なすぎる」という問題に対して、正式 gate を壊さずに Active Plan レイヤーを追加する方向へ進んでいる。

現在の到達点は妥当。

ただし、勝てるシステムへ近づけるには、次に以下を必ず確認する必要がある。

- `ACTIVE_LIMIT_RETEST` が本当に主戦場として機能するか。
- `ACTIVE_MARKET_SMALL` が過剰売買になっていないか。
- `ACTIVE_COUNTER_SCALP` が allowed ではなく conditional として機能しているか。
- `NO_ACTION` が期待値のない局面を除外できているか。
- 候補ごとの entry 到達後に TP / SL / timeout がどう出るか。

そのため、次段階は intraperiod 検証設計である。
