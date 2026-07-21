# Ver03-v1 Active Plan candidate intraperiod outcomes 追加ログ

作業番号: BTCFX-20260607-053  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `tools/log_feedback.py` に `ACTIVE_PLAN_CANDIDATE_INTRAPERIOD_HEADER` を追加した。
- `tools/log_feedback.py` に `build_active_plan_candidate_intraperiod_outcomes()` を追加した。
- `active_plan_paper_candidates.csv` と OHLCV CSV から、候補ごとの intraperiod outcome を生成できるようにした。
- entry 到達、TP1、TP2、SL、timeout、pending、not_entered、no_ohlcv を判定できるようにした。
- 同一足で TP1 と SL が両方見える場合は `ambiguous_sl_first` として保守的に扱うようにした。
- candidate entry price 基準の MFE / MAE を計算できるようにした。
- CLI subcommand `build-active-plan-candidate-intraperiod-outcomes` を追加した。
- long TP1 first、short SL first、limit not entered、same bar ambiguous、timeout、pending、no_ohlcv、output_csv 指定をテストで固定した。

## 変更しなかったもの

- `main.py`
- `src/storage/csv_logger.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `CSV_HEADER`
- `SHADOW_HEADER`
- `build_shadow_log()`
- `daily_sync()`
- `paper_positions.csv`
- 既存 `build_paper_positions()`
- 既存 paper order 生成条件
- `paper_order_status`
- `trade_execution_gate`
- `opportunity_gate`
- 通知件名
- HTML hero
- Active Plan core の判定ロジック
- report builder
- 外部API取得
- `fetch_klines()` 接続
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、Active Plan candidate の intraperiod outcome を独立CSVとして生成できるようになった。

ただし、まだ daily-sync には接続していない。  
また、report builder もまだ作っていない。  
OHLCV 入力は `--ohlcv-path` または builder 引数で明示的に渡す前提である。

次の作業では、この intraperiod outcome の Markdown report builder を追加する。

## 検証

- `python -m unittest tests.test_active_plan_candidate_intraperiod_outcomes`
- `python -m unittest tests.test_active_plan_candidate_outcomes`
- `python -m unittest tests.test_active_plan_paper_candidates`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
