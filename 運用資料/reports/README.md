更新日: 2026-04-17 01:10 JST

# reports 入口

このフォルダは、自動生成レポートと旧版説明レポートをまとめて置く場所です。

## まず見るもの

- [feedback_daily_sync_20260417.md](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/運用資料/reports/feedback_daily_sync_20260417.md)
  - 現行 `ver02.5-v1` の最新日次レポート
- [feedback_daily_sync_20260416.md](/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/運用資料/reports/feedback_daily_sync_20260416.md)
  - 直近比較用の日次レポート

## 最新レポート要点

- 2026-04-17 レポート: 完了データ 37 件、近似PF 0.97、全体勝率 75.7%。
- Phase 1 は `ready=0`、`phase1_active=true=0` で本有効待ち。
- 改善候補の最上位は `TP が近すぎるケースが多い`。
- `paper_orders planned=0件` のため、紙トレード候補はまだ発生待ち。

## フォルダ構成

- 直下の `feedback_*`
  - 現行運用で見る自動生成レポート
- `Ver02.3のレポート/`
  - 旧版 `Ver02.3` の解説レポート
- `Ver02までのレポート/`
  - さらに古い比較レポートやログレビュー

## 注意

- `daily-sync` は直下に新しい `feedback_daily_sync_YYYYMMDD.md` を出力する
- 旧版フォルダは履歴・比較用であり、現行判断の正本にはしない
