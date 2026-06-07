# Ver03-v1 Active Trade Plan 件名優先化ログ

作業番号: BTCFX-20260607-038  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `src/ai/summary.py` の `build_summary_subject()` を Active Plan 優先にした。
- main 通知では `active_subject_label` を方向ラベルより前に出すようにした。
- `ACTIVE_*` 件名には `実弾不可・行動計画` を明記した。
- `active_headline` を件名 detail として使うようにした。
- Active Plan が未設定の場合は既存件名へ fallback するようにした。
- attention 通知は既存件名を維持した。
- `trade_execution_gate=pass` かつ `paper_order_status=planned` の正式 gate 通過時は既存件名を維持した。

## 変更しなかったもの

- `main.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/notification/detail_page.py`
- HTML hero
- CSV schema
- `trade_execution_gate`
- `opportunity_gate`
- `paper_order_status`
- paper order 生成条件
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、通知件名は「方向」より先に「取れる行動」を示す構造になった。

ただし、これは実弾発注ではない。  
`ACTIVE_*` は人間が確認する行動計画であり、正式 GO ではない。

HTML hero を Active Plan 優先へ切り替える作業は、後続作業で行う。

## 検証

- `python -m unittest tests.test_summary_active_plan_subject`
- `python -m unittest tests.test_summary_format`
- `python -m unittest tests.test_active_plan_subject_label`
- `python -m unittest tests.test_notification_context_active_plan`
- `python -m unittest tests.test_active_trade_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
