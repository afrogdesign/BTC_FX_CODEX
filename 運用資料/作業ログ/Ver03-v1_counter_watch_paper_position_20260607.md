# Ver03-v1 counter_long_short_watch paper position 修正ログ

作業番号: BTCFX-20260607-055  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `append_paper_position()` で `counter_long_short_watch` の保存対象 setup を反対側 setup に切り替えた。
- `bias=long` かつ `opportunity_type=counter_long_short_watch` の場合、`short_setup` の side / entry / SL / TP / RR を保存するようにした。
- `bias=short` かつ `opportunity_type=counter_long_short_watch` の場合、`long_setup` の side / entry / SL / TP / RR を保存するようにした。
- 通常 opportunity は従来どおり primary setup を保存するようにした。
- 反対側 setup が存在しない場合は primary setup に fallback するようにした。
- `PAPER_POSITION_HEADER` は変更していない。
- 回帰テストを追加した。

## 変更しなかったもの

- `main.py`
- `tools/log_feedback.py`
- `src/trade/paper_position.py`
- `src/trade/opportunity_gate.py`
- `src/trade/active_plan.py`
- `PAPER_POSITION_HEADER`
- `CSV_HEADER`
- `SHADOW_HEADER`
- `append_observation_paper_order()`
- `append_paper_order()`
- `append_phase1b_lite_paper_order()`
- filled-only 集計
- `missed_opportunity` / `entry_not_reached`
- formal candidate hard blocker
- volume trigger
- `short_reversal_risk`
- Active Plan intraperiod report
- daily-sync
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の修正は P0-1 である。

目的は、反転観察候補である `counter_long_short_watch` が、paper position 上で primary setup として誤保存される可能性をなくすこと。

これにより、P0-2 の filled-only 集計分離へ進む前に、paper position の side / entry / SL / TP の土台を修正した。

## 検証

- `python -m unittest tests.test_phase1_trade_plans`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
