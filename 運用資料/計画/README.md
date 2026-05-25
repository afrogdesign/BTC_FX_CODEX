# 計画フォルダ

更新日: 2026-05-26 JST

このフォルダは、自動取引直前まで最短で進めるための計画正本を置く場所です。
旧マイルストーンと旧フェーズ計画は `archive/superseded/2026-05-18_pre_auto_redesign/` へ退避済みです。

## 現在の正本

- 現在の作業ブランチ: `ver02.6-v2`
- 運用本体の参照ブランチ: `ver02.5-v8`
- 現在版: `Ver02.5-v8` 稼働中 / `ver02.6-v2` で設計・仕様化中
- 現在フェーズ: `Phase C` 実装済み・観測中、`Phase D` 初期段階
- 実務正本: `運用資料/NEXT_TASK.md`
- レポート導線: `運用資料/reports/report_hub_latest.md`
- Codex 実装正本: `chatgpt/specs/active/`

## Ver02.6-v2 以降の設計運用

- 診断、設計、再考、フェーズ判断、改善案比較は ChatGPT プロジェクトで行う。
- Codex は、`chatgpt/specs/active/` に置かれた確定仕様の実装、検証、レポート生成、Git 操作を担当する。
- この `運用資料/計画/` には、長期方針・フェーズ定義・現在地の整理だけを置く。
- 日々の最新状態と次タスクは `運用資料/NEXT_TASK.md` を正本にする。
- branch 名は `NEXT_TASK.md` の `現在の作業ブランチ` を最優先する。
- Codex は未確定の設計案をこのフォルダで膨らませない。必要な材料整理は行ってよいが、最終判断は ChatGPT 側へ戻す。

## まず見るもの

1. [../NEXT_TASK.md](../NEXT_TASK.md)
   - 最新の作業ブランチ、現在状態、次タスクの正本。
2. [../reports/report_hub_latest.md](../reports/report_hub_latest.md)
   - 最新レポートへの案内板。
3. [自動取引直前_高速到達計画_20260518.md](自動取引直前_高速到達計画_20260518.md)
   - 自動取引直前まで進めるための基本計画。現在は Phase C 実装済み、Phase D 初期として読む。
4. [マイルストーン定義.md](マイルストーン定義.md)
   - Phase A-E と Ver 昇格条件の定義。
5. [../開発ロードマップ.md](../開発ロードマップ.md)
   - 現在地と次に見る数値の整理。

## 現行方針

- 正式 `trade_execution_gate` は安全基準として残す。
- `trade_execution_gate=pass` と `paper_orders planned` が自然発生するまでは、実弾 gate を緩和しない。
- フェーズ前進は、厳格 gate 待ちだけではなく `opportunity_gate` と `paper_positions.csv` の型別成績で進める。
- `opportunity_gate=pass` は `紙実行候補・実弾不可` であり、実弾候補ではない。
- `Phase 1B-lite` は正式 `Phase 1B` ではなく、専用紙トレード観測レーンとして扱う。
- 実弾発注、取引所API送信、秘密鍵連携はまだ行わない。
- 勝てる型の判断は、紙実行ログと quality blocker 後の型別成績を見てから行う。
- 型別の再調整案は ChatGPT 側で決め、Codex は確定後に実装と検証を担当する。

## 現在の重点

- `entry / wait / trend_flip` 品質ガードの実装。
- `wait>=80`、`execution<20`、`long + wait>=60 + execution<25`、`long + trend_flip_confirmed_up` の弱い紙候補を分離する。
- `support_to_resistance_flip` など有効な market_map 型は維持し、候補化条件だけを整える。
- SL/TP 倍率や RR 計算はまだ変更しない。

## archive の扱い

- `archive/implemented/`: 実装済み計画。履歴参照用。
- `archive/superseded/`: 現行計画に置き換えた古い計画。現行判断の正本にはしない。
- `履歴/`: 経緯確認用。現行判断の正本にはしない。
