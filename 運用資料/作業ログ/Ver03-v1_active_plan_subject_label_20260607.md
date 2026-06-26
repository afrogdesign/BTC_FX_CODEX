# Ver03-v1 Active Trade Plan 件名ラベル固定ログ

作業番号: BTCFX-20260607-037  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `src/presentation/sanitize.py` に Active Plan 件名用 helper を追加した。
- `build_notification_context()` に `active_subject_label` を追加した。
- `active_primary_action` から件名用の短い行動ラベルを生成できるようにした。
- short / long / neutral bias 別の件名ラベルをテストで固定した。
- `active_primary_action` が空の場合に `active_trade_plan["primary_action"]` へ fallback するテストを追加した。

## 固定した主なラベル

short bias:

- `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP`: 戻り売り待ち・短期反発注意
- `ACTIVE_MARKET_SMALL`: 小ロット成行ショート候補
- `ACTIVE_LIMIT_RETEST`: 戻り売り待ち

long bias:

- `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP`: 押し目買い待ち・短期反落注意
- `ACTIVE_MARKET_SMALL`: 小ロット成行ロング候補
- `ACTIVE_LIMIT_RETEST`: 押し目買い待ち

共通:

- `ACTIVE_BREAKOUT_FOLLOW`: ブレイク追随待ち
- `ACTIVE_COUNTER_SCALP`: 逆方向短期注意
- `NO_ACTION`: 見送り
- unknown action: 見送り

## 変更しなかったもの

- `main.py`
- `src/trade/active_plan.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `trade_execution_gate`
- `opportunity_gate`
- `paper_order_status`
- 実際の通知件名
- HTML hero
- CSV schema
- paper order 生成条件
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業は、通知件名を Active Plan 優先へ切り替える前の仕様固定である。

実際に通知件名へ `active_subject_label` を使う作業は、後続作業で行う。

## 検証

- `python -m unittest tests.test_active_plan_subject_label`
- `python -m unittest tests.test_notification_context_active_plan`
- `python -m unittest tests.test_active_trade_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
