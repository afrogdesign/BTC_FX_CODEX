# reports 入口

更新日: 2026-05-30 JST

このフォルダは、自動生成レポートの保存場所です。
ChatGPT は生レポートを読むが、入口は常に `NEXT_TASK.md` と `report_hub_latest.md` から始める。

## 最初に開く順

1. [../NEXT_TASK.md](../NEXT_TASK.md)
2. [report_hub_latest.md](report_hub_latest.md)
3. Hub から最新の raw report

## フォルダ構成

- 直下
  - `README.md`
  - `report_hub_latest.md`
  - 最新と直前の `feedback_daily_sync_YYYYMMDD.md`
- `analysis/`
  - 各分析レポート族の最新 1 本だけを置く現役棚
- `archive/daily/YYYY-MM/`
  - 古い日次レポート
- `archive/weekly/`
  - 現行運用では常用しない週次レポート
- `archive/analysis/`
  - 古い分析レポート
- `Ver02.3のレポート/`、`Ver02までのレポート/`
  - 旧版の説明資料。現行判断の正本にはしない

## 運用ルール

- ChatGPT は Hub を案内板として使い、必要な raw report を直接読む。
- `analysis/` に dated report を増やし続けない。最新 1 本だけを残し、古いものは `archive/analysis/` へ移す。
- `daily-sync` の直下レポートも最新と直前だけを残し、それ以前は `archive/daily/YYYY-MM/` へ移す。
- `feedback_weekly` は現行運用の正本ではない。生成を再開するまでは `archive/weekly/` で履歴扱いにする。
- `market_map_readiness` は常用レポートではなく、market_map ロジック刷新時だけ再生成する dormant 診断として扱う。
- 現在の判断、最新レポート名、次指示の正本は `../NEXT_TASK.md`。
