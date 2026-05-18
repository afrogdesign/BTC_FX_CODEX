# reports 入口

更新日: 2026-05-18 JST

このフォルダは、自動生成レポートと旧版説明レポートを置く場所です。
日常判断では最新だけを見て、古い日次レポートは `archive/` から必要時だけ探します。

## まず見るもの

- [feedback_daily_sync_20260518.md](feedback_daily_sync_20260518.md)
  - 最新の日次レポート。完了 47 件、近似PF 0.73、全体勝率 46.8%。
- [analysis/market_map_effectiveness_20260518.md](analysis/market_map_effectiveness_20260518.md)
  - `market_map` の直近有効性。上方向転換の弱さと下方向 flag の相対的な強さを見る。
- [analysis/operational_focus_20260518.md](analysis/operational_focus_20260518.md)
  - Phase 1 の pass / blocked と、次に詰める阻害要因を見る。

## フォルダ構成

- 直下の `feedback_daily_sync_YYYYMMDD.md`
  - 最新と直近比較用だけを残す。古い日次は `archive/daily/YYYY-MM/`。
- `analysis/`
  - 現行判断で見る最新分析と標準比較レポート。
- `archive/analysis/`
  - 過去日の分析レポート。
- `Ver02.3のレポート/`、`Ver02までのレポート/`
  - 旧版の説明・比較用。現行判断の正本にはしない。

## 整理ルール

- `daily-sync` は直下に新しい日次レポートを出す。
- 直下に残す日次は最新と直近比較用を基本にする。
- 古いレポートは削除せず `archive/` へ移す。
- 現在地の要約は `../NEXT_TASK.md` を正本にする。
