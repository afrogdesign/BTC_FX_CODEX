# Ver03-v1 Active Plan intraperiod 実装前 repo 調査

作業番号: BTCFX-20260607-052  
作成日: 2026-06-07 JST  
対象ブランチ: Ver03-v1  
対象repo: afrogdesign/BTC_FX_CODEX

## 1. 結論

この調査は、Active Plan candidate intraperiod 検証実装前の repo 事実確認である。

本ファイルでは、以下を記録する。

- `update_outcomes()` 周辺の実装場所
- forward price / MFE / MAE / outcome 生成に関係する既存処理
- OHLCV / candle / kline / price history の既存有無
- logs/csv に存在する関連CSV
- intraperiod 関連実装の既存有無

Codex は採用方針を判断しない。  
最終判断は ChatGPT が行う。

## 2. 実行したコマンド

- `git status --short --branch`
- `git rev-parse HEAD`
- `grep -R "def update_outcomes" -n tools src tests || true`
- `grep -R "forward_price_24h\|signal_based_MFE_24h\|signal_based_MAE_24h\|OUTCOME_HEADER" -n tools src tests || true`
- `grep -R "direction_outcome\|tp1_hit_first\|evaluation_status" -n tools src tests || true`
- `grep -R "ohlcv\|OHLCV\|candle\|candles\|kline\|klines" -n . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=.venv312 --exclude-dir=__pycache__ --exclude-dir=.pytest_cache || true`
- `grep -R "price_history\|historical\|history\|forward_price\|base_price" -n tools src tests || true`
- `grep -R "high\|low\|close" -n tools src tests | head -n 200 || true`
- `find . \( -iname "*ohlcv*" -o -iname "*candle*" -o -iname "*kline*" -o -iname "*price*history*" -o -iname "*history*" -o -iname "*market*" \) -not -path "./.git/*" -not -path "./.venv/*" -not -path "./.venv312/*" -not -path "*/__pycache__/*" | sort | head -n 200`
- `find logs -maxdepth 3 -type f 2>/dev/null | sort | head -n 200 || true`
- `find . -path "*/logs/csv/*" -type f 2>/dev/null | sort | head -n 200 || true`
- `grep -R "active_plan_candidate_intraperiod\|intraperiod\|candidate_intraperiod" -n tools src tests "運用資料" || true`
- `sed -n '3160,3298p' tools/log_feedback.py`
- `sed -n '2980,3055p' tools/log_feedback.py`
- `sed -n '348,410p' tools/log_feedback.py`
- `sed -n '470,540p' tools/log_feedback.py`
- `sed -n '1,220p' src/data/fetcher.py`
- `sed -n '1,120p' src/data/validator.py`
- `sed -n '130,330p' main.py`
- `sed -n '1,260p' src/trade/paper_position.py`
- `sed -n '260,420p' src/trade/paper_position.py`
- `sed -n '1,180p' src/data/provider_client/binance_market.py`
- `sed -n '1,180p' tests/test_phase1_trade_plans.py`
- `sed -n '2380,2475p' tests/test_log_feedback.py`
- `find . -type f \( -iname "*ohlcv*" -o -iname "*candle*" -o -iname "*kline*" -o -iname "*price*history*" -o -iname "*history*" \) -not -path "./.git/*" -not -path "./.venv/*" -not -path "./.venv312/*" -not -path "*/__pycache__/*" | sort | head -n 200`

## 3. update_outcomes 周辺の確認結果

### 3.1 見つかったファイル・関数

- `tools/log_feedback.py:3173-3272` に `evaluate_trade_row()` がある。
- `tools/log_feedback.py:3275-3289` に `update_outcomes()` がある。
- `tools/log_feedback.py:357-394` に `OUTCOME_HEADER` がある。
- `tools/log_feedback.py:3002-3012` に `_fetch_future_15m_df()` がある。
- `tools/log_feedback.py:3015-3028` に `_window_df()` と `_close_at_or_after()` がある。
- `tools/log_feedback.py:3031-3042` に `_mfe_mae_atr()` がある。
- `tools/log_feedback.py:3045-3055` に `_evaluate_direction()` がある。
- `tools/log_feedback.py:3161-3170` に `_derive_trade_outcome()` がある。

### 3.2 forward price / MFE / MAE 関連

- `evaluate_trade_row()` は `forward_price_1h`、`forward_price_4h`、`forward_price_12h`、`forward_price_24h` を返している。
- 同関数は `signal_based_MFE_4h`、`signal_based_MAE_4h`、`signal_based_MFE_12h`、`signal_based_MAE_12h`、`signal_based_MFE_24h`、`signal_based_MAE_24h` を返している。
- `update_outcomes()` は `_load_trade_rows()` の結果を `_fetch_future_15m_df()` へ渡し、`evaluate_trade_row()` の戻り値を `_upsert_csv_rows()` で `signal_outcomes.csv` に書き込んでいる。
- `OUTCOME_HEADER` には `forward_price_24h`、`signal_based_MFE_24h`、`signal_based_MAE_24h` が含まれている。

### 3.3 direction_outcome / tp1_hit_first / evaluation_status 関連

- `evaluate_trade_row()` は `direction_outcome` を `_evaluate_direction()` で生成している。
- `evaluate_trade_row()` は `tp1_hit_first` を `_tp1_vs_stop()` で生成している。
- `evaluate_trade_row()` は `evaluation_status` を `forward_24h is not None` で `complete` / `pending` に分けている。
- `OUTCOME_HEADER` には `direction_outcome`、`tp1_hit_first`、`evaluation_status` が含まれている。

## 4. OHLCV / candle / kline 系の確認結果

### 4.1 grep 結果

- `src/data/fetcher.py` に `fetch_klines()`、`_parse_kline_payload()` が見つかった。
- `src/data/validator.py` に `validate_klines()` が見つかった。
- `main.py` に `fetch_klines(fetch_cfg, "4h" / "1h" / "15m", ...)` が見つかった。
- `src/trade/paper_position.py` に `evaluate_paper_position()` と 15m candles を扱う処理が見つかった。
- `tests/test_phase1_trade_plans.py` に candle fixture を使うテストが見つかった。
- `tests/test_notification_detail_page.py` と `tests/test_chart_pattern_shadow.py` に `candles_4h` / `candles_1h` / `candles_15m` を使う fixture が見つかった。

### 4.2 find 結果

- `ohlcv` / `candle` / `kline` / `price history` / `history` を含むファイル名の実ファイルは見つからなかった。
- `market` を含むファイルとしては `src/analysis/market_map.py`、`src/data/provider_client/binance_market.py`、複数の `market_map_*` report が見つかった。

## 5. price history / historical 系の確認結果

- `src/data/provider_client/binance_market.py` に `fetch_open_interest_stats()` があり、関数内コメントと例外メッセージに `open interest history` が見つかった。
- `tools/log_feedback.py` には `forward_price_1h`、`forward_price_4h`、`forward_price_12h`、`forward_price_24h` を扱う処理が見つかった。
- `tools/log_feedback.py:3002-3012` の `_fetch_future_15m_df()` は `fetch_klines()` を呼び、15m データを取得している。

## 6. high / low / close を扱う既存処理

- `src/data/fetcher.py:82-177` で kline payload から `timestamp`、`open`、`high`、`low`、`close`、`volume` を DataFrame 化している。
- `main.py:141-164` で chart 用 candles に `open`、`high`、`low`、`close`、`volume` を詰めている。
- `src/trade/paper_position.py:86-107` に `_touches_entry()`、`_touches_tp()`、`_touches_stop()` がある。
- `src/trade/paper_position.py:123-136` に `_mfe_mae()` がある。
- `src/trade/paper_position.py:163-313` に `evaluate_paper_position()` があり、15m candles を使って entry、TP1、TP2、SL、timeout を順に扱っている。
- `src/trade/paper_position.py:273-305` では、同一足で `tp1` と `sl` が両方見える場合に `sl_hit` を先に返している。
- `tests/test_phase1_trade_plans.py:95-101` に、同一 candle で TP と SL が両方成立した場合は SL を優先するテストがある。
- `src/analysis/market_map.py` と `src/analysis/support_resistance.py` に high / low を使う処理がある。

## 7. logs/csv の既存CSV

- `logs/csv/observation_paper_orders.csv`
- `logs/csv/paper_orders.csv`
- `logs/csv/paper_positions.csv`
- `logs/csv/phase1b_lite_paper_orders.csv`
- `logs/csv/shadow_log.csv`
- `logs/csv/signal_outcomes.csv`
- `logs/csv/trades.csv`
- `logs/csv/user_reviews.csv`
- `logs/csv/user_reviews_backfill_20260419_013047.csv`
- `logs/csv/user_reviews_human_archive.csv`
- `logs/cache/binance_liquidations_BTCUSDT.json`

`logs/csv` の一覧には OHLCV / candle / kline / history 名を含む CSV は見つからなかった。

## 8. Active Plan intraperiod 関連の既存有無

- `tools/log_feedback.py:7825` 付近に、intraperiod の高値 / 安値到達、entry zone 到達、timeout を後続で扱う旨の文言が見つかった。
- `運用資料/計画/Ver03-v1_Active_Plan_candidate_intraperiod検証設計_20260607.md` が存在する。
- `運用資料/計画/Ver03-v1_Active_Plan_実装棚卸し_20260607.md` に intraperiod TP / SL 到達判定の未実装説明がある。
- `運用資料/作業ログ/Ver03-v1_active_plan_candidate_outcomes_report_20260607.md`、`Ver03-v1_daily_sync_active_plan_candidate_outcomes_report_20260607.md`、`Ver03-v1_active_plan_report_family_registry_20260607.md` にも intraperiod の未実装注記がある。
- `grep` では `active_plan_candidate_intraperiod` / `candidate_intraperiod` のコード実装やテストは見つからなかった。

## 9. 調査上の注意

- このファイルでは設計判断をしない。
- OHLCV 入力をどれにするかは未決定。
- intraperiod 検証はまだ実装しない。
- `paper_positions.csv` とはまだ接続しない。
- 実弾発注 API、自動注文送信、取引所キーは扱わない。

## 10. ChatGPT が次に判断する事項

- 既存 OHLCV / price history を再利用できるか。
- `--ohlcv-path` 必須で初期実装するか。
- `tools/log_feedback.py` に実装を追加するか、別ファイルへ分割するか。
- 15m OHLCV を前提にするか。
- UTC / JST 変換をどこで吸収するか。
- `active_plan_candidate_intraperiod_outcomes.csv` の最小実装へ進めるか。
