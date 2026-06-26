# Ver03-v1 Active Trade Plan notification context 接続ログ

作業番号: BTCFX-20260607-036  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `src/presentation/sanitize.py` の `build_notification_context()` に Active Plan 用フィールドを追加した。
- `active_primary_action` を notification context に追加した。
- `active_headline` を notification context に追加した。
- `active_market_entry_now` を notification context に追加した。
- `active_limit_retest_entry` を notification context に追加した。
- `active_breakout_follow_entry` を notification context に追加した。
- `active_countertrend_scalp_entry` を notification context に追加した。
- `active_position_management` を notification context に追加した。
- Active Plan が存在しない場合や壊れた値の場合でも safe default を返すテストを追加した。

## 変更しなかったもの

- `main.py`
- `src/trade/active_plan.py`
- `trade_execution_gate`
- `opportunity_gate`
- `paper_order_status`
- 通知件名
- HTML hero
- CSV schema
- paper order 生成条件
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業は、Active Trade Plan を通知表示へ使う前に、notification context へ通すための準備である。

通知件名や HTML hero を Active Plan 優先にする作業は、後続作業で行う。

## 検証

- `python -m unittest tests.test_notification_context_active_plan`
- `python -m unittest tests.test_active_trade_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
