# Ver03-v1 filled-only paper diagnostics 分離ログ

作業番号: BTCFX-20260607-056  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- paper diagnostics の主指標を filled-only に分離した。
- `sl_hit`、`tp2_hit`、`timeout` を filled-only として扱う helper を追加した。
- `missed_opportunity` と `entry_not_reached` を non-entered として分離する helper を追加した。
- `_paper_position_group_lines()` の表示を filled-only 勝率、filled平均R、filled簡易PF中心に変更した。
- `missed_opportunity` と `entry_not_reached` は別件数として表示するようにした。
- `_paper_position_sl_group_lines()` の成績表示を filled-only 基準にした。
- `_paper_position_proposals()` の成績表示を filled-only 基準にした。
- 既存 `realized_r` と `_paper_position_realized_stats()` は互換性のため残した。
- filled-only / non-entered 分離を unittest で固定した。

## 変更しなかったもの

- `main.py`
- `src/storage/csv_logger.py`
- `src/trade/paper_position.py`
- `src/trade/opportunity_gate.py`
- `src/trade/active_plan.py`
- `PAPER_POSITION_HEADER`
- `CSV_HEADER`
- `SHADOW_HEADER`
- `paper_positions.csv` の列
- `_close_position()`
- `missed_opportunity` / `entry_not_reached` の生成挙動
- formal candidate hard blocker
- volume trigger
- `short_reversal_risk`
- Active Plan intraperiod report
- daily-sync
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の修正は P0-2 である。

目的は、約定していない `missed_opportunity` と `entry_not_reached` が、paper diagnostics の主指標である勝率、平均R、PFに混ざることを避けること。

これにより、次の実データ確認 report で、filled-only 成績と未約定系を分けて確認できる。

## 検証

- `python -m unittest tests.test_paper_position_filled_only_diagnostics`
- `python -m unittest tests.test_phase1_trade_plans`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
