# Ver03-v1 Active Trade Plan HTML hero 優先化ログ

作業番号: BTCFX-20260607-039  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `src/notification/detail_page.py` の hero を Active Plan 優先表示にした。
- hero summary に `active_subject_label` と `active_headline` を反映した。
- hero の「最初に読む結論」で、成行・指値/戻り待ち・ブレイク追随・逆方向短期・保有中処理を表示するようにした。
- `ACTIVE_*` は `実弾不可・行動計画` と表示し、正式GOと混同しないようにした。
- `trade_execution_gate=pass` かつ `paper_order_status=planned` の場合は正式候補表示を優先した。
- `notification_kind=attention` の場合は注意報表示を維持した。
- Active Plan が未設定でも HTML が落ちないテストを追加した。

## 変更しなかったもの

- `main.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- 通知件名
- CSV schema
- `trade_execution_gate`
- `opportunity_gate`
- `paper_order_status`
- paper order 生成条件
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、通知件名に続き、HTML detail page の最初の表示も「方向」より「取れる行動」を優先する構造になった。

ただし、これは実弾発注ではない。  
`ACTIVE_*` は人間が確認する行動計画であり、正式 GO ではない。

CSV logging と diagnostics への接続は後続作業で行う。

## 検証

- `python -m unittest tests.test_detail_page_active_plan_hero`
- `python -m unittest tests.test_summary_active_plan_subject`
- `python -m unittest tests.test_summary_format`
- `python -m unittest tests.test_active_plan_subject_label`
- `python -m unittest tests.test_notification_context_active_plan`
- `python -m unittest tests.test_active_trade_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
