# 目的

`ver02.6-v1` 上で、紙ポジション候補の quality guard を最小実装する。
対象は `sl_hit` 偏重、高 wait、低 execution、long 側の弱さの抑制であり、実行 gate 緩和や実弾化は行わない。

# 対象ブランチ

`ver02.6-v1`

# 変更範囲

- `src/trade/opportunity_gate.py`
- `tests/test_phase1_trade_plans.py`
- `tests/test_log_feedback.py`
- `tools/log_feedback.py`
- `運用資料/NEXT_TASK.md`

# 実装内容

1. `src/trade/opportunity_gate.py` に以下の quality guard を追加する
   - `require_execution_for_high_wait`
   - `suppress_long_high_wait`
   - `suppress_trend_flip_up_strong`
2. quality guard は以下の紙候補化だけを抑制する
   - `phase1_observation_gate` 由来の observation paper opportunity
   - `market_map_opportunity`
3. 以下は変更しない
   - `trade_execution_gate` の判定
   - `phase1b_lite_gate` の判定
   - `support_to_resistance_flip` 自体の有効性
4. `tools/log_feedback.py` の既存 CLI 出力に quality guard 集計を追加する
   - `build-paper-opportunity-diagnostics-report`
   - `daily-sync` が生成する `feedback_daily_sync_YYYYMMDD.md`
5. `paper_entry_sl_wait_redesign` については専用 CLI が見当たらないため、新規 CLI は増やさず、既存 builder 構造のまま対応可否を報告する

# 検証方法

1. 単体テスト追加
   - high wait + low execution の block
   - long + high wait の block
   - long + `trend_flip_confirmed_up` の block
   - `support_to_resistance_flip` 単体は維持
   - `trade_execution_gate=pass` と `phase1b_lite_gate=pass` の既存判定は維持
2. 既存テスト実行
   - `./.venv312/bin/python -m unittest discover -s tests -p "test*.py"`
3. レポート再生成
   - `tools/log_feedback.py` の既存 subcommand のみを使う
4. 差分確認
   - `git diff --check`
   - `git status --short`
   - `git diff --stat`

# 完了条件

- `require_execution_for_high_wait` が `opportunity_reasons` に出る
- `suppress_long_high_wait` が `opportunity_reasons` に出る
- `suppress_trend_flip_up_strong` が `opportunity_reasons` に出る
- `support_to_resistance_flip` 自体は維持される
- `trade_execution_gate` を変更していない
- `phase1b_lite_gate` を変更していない
- 単体テストが追加され、既存テストが通る
- 可能な範囲で関連レポートが再生成される
- `運用資料/NEXT_TASK.md` に実施結果と次論点が反映される

# 注意事項

- trade_execution_gate は緩和しない
- Phase 1B 正式昇格は行わない
- paper_orders planned を増やすこと自体を目的にしない
- 実弾発注、取引所API送信、秘密鍵連携は対象外
- analysis 文書は参考であり、実装正本は active spec とする
