# フェーズ別計画 Phase2-3

更新日: 2026-03-12 11:10 JST

このファイルは、`Phase 2` と `Phase 3` の大きな流れを軽く見通すための計画書です。
直近の実務は `Phase0-1` 側で進め、こちらは将来の着手条件と未実装項目をまとめます。

## 現在の前提

- `Phase 2` と `Phase 3` は、`Phase 0` の実運用確認と `Phase 1` の中核導入が進んだあとに本格着手する
- すでにある基盤は流用し、未実装部分だけを段階的に足す

## Phase 2

### 目的

- 通知品質と危険回避を強化する

### 既にある土台

- 通知監査 A/B/C/D の集計基盤
- `shadow_log.csv`
- `notify_reason_codes`
- AI審査呼び出しと本文生成呼び出しの分離

### まだ未実装の主項目

- blackout
- 価格乖離監視
- `watch_prices`
- 構造化 AI審査出力
- `config_change_log`

### 実装候補

- `src/data/macro_filter.py`
- `src/data/exchange_check.py`
- `src/analysis/watch_prices.py`
- `logs/config_change_log.csv`

### 着手条件

- `Phase 0` の通知後フロー一周が終わっている
- `Phase 1` のサイズ計画と出口計画が live ログへ保存されている

### Ver04 との関係

- blackout、価格乖離、`watch_prices`、構造化 AI審査、`config_change_log` が live で動いたら `Ver04` 候補

## Phase 3

### 目的

- 蓄積ログを根拠にロジック自体を精密化する

### 主な項目

- 因子相関分析
- prelabel 内部スコア化
- A/B比較モード
- `build_setup()` 精密化
- シナリオ分岐出力

### 進め方

- 先に分析ツールを作る
- 次に比較ログを残せる状態を作る
- 最後にロジック変更を行う

### 現時点でやらないこと

- サンプル不足のまま閾値を動かす
- 一度に複数のロジック変更を入れる
- A/B 比較なしで build_setup をまとめて強化する

### 着手条件

- `Phase 2` の安全装置が運用に乗っている
- 比較判断に使えるログ量が確保できている
- `config_change_log` が使える

### Ver05 との関係

- 因子分析、内部スコア、A/B比較、build_setup 比較運用、シナリオ分岐がそろった段階を `Ver05` とする

## 補足

- paper execution はこのファイルの対象外
- paper execution は `Phase 4` の大型節目として別扱いにする
