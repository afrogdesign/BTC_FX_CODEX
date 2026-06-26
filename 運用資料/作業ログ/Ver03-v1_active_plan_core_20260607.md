# Ver03-v1 Active Trade Plan コア実装ログ

作業番号: BTCFX-20260607-033  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `src/trade/active_plan.py` を追加した。
- `tests/test_active_trade_plan.py` を追加した。
- Active Trade Plan の最小コア判定をテストで固定した。
- `main.py`、通知、HTML、CSV、既存 gate には接続していない。

## 実装した分類

- `ACTIVE_MARKET_SMALL`
- `ACTIVE_LIMIT_RETEST`
- `ACTIVE_BREAKOUT_FOLLOW`
- `ACTIVE_COUNTER_SCALP`
- `NO_ACTION`

`FORMAL_GO` は今回未実装。  
理由は、今回の `build_active_trade_plan()` には `trade_execution_gate` と `paper_order_status` を渡していないため。

## 重要な安全条件

- 既存 `trade_execution_gate` は変更していない。
- `paper_order_status` は変更していない。
- 実弾発注 API は追加していない。
- 取引所 API キーや秘密鍵は扱っていない。
- 自動注文送信は実装していない。

## 検証

- `python -m unittest tests.test_active_trade_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
