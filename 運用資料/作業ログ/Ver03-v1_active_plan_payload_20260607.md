# Ver03-v1 Active Trade Plan payload 接続ログ

作業番号: BTCFX-20260607-035  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `main.py` に `build_active_trade_plan` を import した。
- `core_result["active_trade_plan"]` を追加した。
- `core_result["active_primary_action"]` を追加した。
- `core_result["active_headline"]` を追加した。
- `should_notify()` と `build_notification_context()` より前に Active Plan payload を生成するようにした。

## 変更しなかったもの

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

今回の作業は、Active Trade Plan を表示へ使う前の payload 接続である。

通知件名や HTML hero を Active Plan 優先にする作業は、後続作業で行う。

## 検証

- `python -m unittest tests.test_active_trade_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
