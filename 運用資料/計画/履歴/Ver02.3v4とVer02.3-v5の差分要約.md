# Ver02.3v4 と Ver02.3-v5 の差分要約

更新日: 2026-04-02 15:08 JST

## 結論

- `Ver02.3v4` は、`7b8c02b` の安定点に固定した。
- `Ver02.3-v5` は、その先に AI 役割再設計を積んだ継続開発版とした。
- この 2 本の差分は「AI を全サイクル補足から通知時監査へ切り替えたこと」が中心である。

## ブランチ位置

- `Ver02.3v4`
  - 安定点
  - コミット: `7b8c02b`
  - 意味: v5 着手直前の完成基準
- `Ver02.3-v5`
  - 継続開発版
  - コミット: `e96917b`
  - 意味: AI役割再設計を含む次フェーズの作業線

## コミット差分

- `e7bae27` `AI役割再設計の設計書を保存`
- `61f64ef` `AIを通知時監査へ切り替え`
- `e96917b` `v4とv5のブランチ整理を入口資料へ反映`

## 変更規模

- 17ファイル変更
- 361行追加
- 124行削除

## 何が変わったか

### 1. AI の役割

- `Ver02.3v4`
  - AI は全サイクルで補足的に走る構成だった。
  - ただし通知可否の主判断ではなく、補足説明寄りの役割に留まっていた。
- `Ver02.3-v5`
  - AI は通知が出る回だけ走る `通知時監査` に変更した。
  - 役割は「方向を言い換えること」ではなく、「その通知が妥当かを監査すること」に寄せた。

### 2. 通知判定の責任分担

- `Ver02.3v4`
  - 実質的に通知可否は機械判定のみで決まっていたが、AI が全サイクルで走っていたため役割が見えにくかった。
- `Ver02.3-v5`
  - 通知可否は機械判定のみと明示的に整理した。
  - `signal_tier` も機械判定ベースへ戻し、`strong_ai_confirmed` を廃止した。

### 3. 表示と保存

- `Ver02.3v4`
  - AI の補足は、待機理由や補足文の一部に混ざる形だった。
- `Ver02.3-v5`
  - AI の文言が主理由や次条件を上書きしないように整理した。
  - 必要時だけ `AI監査メモ` を出す形へ変更した。
  - `ai_audit_*` の保存列を追加し、後からレビューと照合しやすくした。

### 4. 設計資料

- `Ver02.3v4`
  - AI役割再整理の設計書はまだ持っていない。
- `Ver02.3-v5`
  - [AI役割再設計_通知監査移行設計.md](AI役割再設計_通知監査移行設計.md) を追加済み。

## 主な変更ファイル

- 実行フロー: [main.py](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/main.py)
- AI監査ロジック: [advice.py](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/src/ai/advice.py)
- AIプロンプト: [advice_prompt.md](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/prompts/advice_prompt.md)
- 通知本文: [summary.py](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/src/ai/summary.py)
- 詳細HTML: [detail_page.py](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/src/notification/detail_page.py)
- シグナル階層: [signal_tier.py](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/src/analysis/signal_tier.py)
- CSV保存: [csv_logger.py](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/src/storage/csv_logger.py)
- 集計: [log_feedback.py](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/tools/log_feedback.py)
- 入口資料: [NEXT_TASK.md](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/NEXT_TASK.md), [開発ロードマップ.md](/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/開発ロードマップ.md)

## 一言まとめ

- `Ver02.3v4` は AI 再設計前の安定版。
- `Ver02.3-v5` は AI を通知監査役へ切り替えた次フェーズ版。
