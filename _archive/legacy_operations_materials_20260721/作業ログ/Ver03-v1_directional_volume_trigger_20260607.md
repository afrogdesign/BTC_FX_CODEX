# Ver03-v1 directional volume trigger 修正ログ

作業番号: BTCFX-20260607-060  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `main.py` の `trigger_up` / `trigger_down` を方向付き出来高 trigger に変更した。
- 出来高急増だけでは long / short 両方向 trigger が立たないようにした。
- bullish high volume は `trigger_up` のみを立てるようにした。
- bearish high volume は `trigger_down` のみを立てるようにした。
- doji に近い candle は、出来高だけでは trigger にしないようにした。
- breakout_up / breakout_down は従来どおり方向付き trigger として維持した。
- market_map flags の `resistance_to_support_flip` / `failed_breakout_up_reversal` は long trigger として扱うようにした。
- market_map flags の `support_to_resistance_flip` / `failed_breakout_down_reversal` は short trigger として扱うようにした。
- 方向付き出来高 trigger の回帰テストを追加した。
- 進捗ボード HTML を更新した。

## 変更しなかったもの

- `tools/log_feedback.py`
- `src/storage/csv_logger.py`
- `src/trade/paper_position.py`
- `src/trade/opportunity_gate.py`
- `src/trade/active_plan.py`
- `src/analysis/result_flags.py`
- `src/analysis/confidence.py`
- `CSV_HEADER`
- `SHADOW_HEADER`
- `PAPER_POSITION_HEADER`
- filled-only 集計
- formal candidate hard blocker
- `short_reversal_risk`
- Active Plan intraperiod report
- daily-sync
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の修正は P1-2 である。

目的は、出来高急増だけで `trigger_up` と `trigger_down` が同時に true になり、方向認識が曖昧なまま confidence / setup へ進むことを防ぐことである。

次の作業では、P1-3 として `short_reversal_risk` を追加する。

## 検証

- `python -m unittest tests.test_directional_volume_trigger`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
