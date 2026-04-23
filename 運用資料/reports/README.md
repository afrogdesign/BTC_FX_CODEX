更新日: 2026-04-24 04:40 JST

# reports 入口

このフォルダは、自動生成レポートと旧版説明レポートをまとめて置く場所です。

## まず見るもの

- [feedback_daily_sync_20260424.md](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/運用資料/reports/feedback_daily_sync_20260424.md)
  - 現行 `ver02.5-v4` の最新日次レポート
- [feedback_daily_sync_20260423.md](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/運用資料/reports/feedback_daily_sync_20260423.md)
  - 直近比較用の日次レポート

## 最新レポート要点

- 2026-04-24 レポート: 完了データ 31 件、近似PF 0.87、全体勝率 71.0%。
- Phase 1 は `ready=0`、`phase1_active=true=0` で本有効待ち。
- 改善候補の最上位は `NO_TRADE_CANDIDATE が強すぎる`。
- `phase1_observation_gate=pass:13件` で、`direction_rr_learning` は 2 件、`setup_watch_learning` は 11 件。
- `sweep_incomplete` を含む `watch 系通知済み履歴` は 10 件で、現行watch再計算もレポートから直接確認できる。
- `paper_orders planned=0件` のため、紙トレード候補はまだ発生待ち。

## フォルダ構成

- 直下の `feedback_*`
  - 現行運用で見る自動生成レポート
- `analysis/`
  - `compare-current-setup` の標準比較レポート置き場
  - `notified_rr_to_entry.md`
  - `notified_rr_to_entry_orderbook_ask_heavy.md`
  - `rr_to_confidence.md`
- `Ver02.3のレポート/`
  - 旧版 `Ver02.3` の解説レポート
- `Ver02までのレポート/`
  - さらに古い比較レポートやログレビュー

## 注意

- `daily-sync` は直下に新しい `feedback_daily_sync_YYYYMMDD.md` を出力する
- 旧版フォルダは履歴・比較用であり、現行判断の正本にはしない
