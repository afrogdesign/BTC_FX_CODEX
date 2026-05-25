# 運用資料 入口

更新日: 2026-05-25 JST

## 概要

- 現行の主対象は `Ver02.6-v1`
- `Ver02.5-v8` の 2026-05-25 診断・レポート更新は `origin/ver02.5-v8` へ push 済み
- 日常の判断は入口文書だけで始められるようにする
- 履歴や旧版資料は残すが、入口からは一段下げる
- 診断、設計、再考、フェーズ管理は ChatGPT プロジェクト側で行い、Codex は確定済み実務の実行に徹する

## ChatGPT / Codex の読む順

1. ChatGPT: `ChatGPTプロジェクト設定.md`
2. ChatGPT: `NEXT_TASK.md`
3. ChatGPT: `開発ロードマップ.md`
4. ChatGPT: 必要なレポート、診断資料、計画資料
5. Codex: ChatGPT またはユーザーが確定した実装指示
6. Codex: 実施履歴が必要なときだけ `履歴/progress.md`

## 人が見る入口

- `運用/README.md`
- `計画/Phase1条件の見方.md`
- `計画/AI事後評価運用_Ver02.4-v1.md`
- Obsidian 側 `👩‍⚖️秘書.md`
  - `$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/👩‍⚖️秘書.md`
- Obsidian 側 `📒打ち合わせノート.md`
  - `$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/📒打ち合わせノート.md`

## 主役ファイル

- `ChatGPTプロジェクト設定.md`
  - ChatGPT プロジェクトに読み込ませる役割・参照順・出力ルール
- `NEXT_TASK.md`
  - ChatGPT へ渡す直近の状態と次判断
- `開発ロードマップ.md`
  - ChatGPT が扱うフェーズと大型節目
- `計画/Phase1条件の見方.md`
  - `ready` と `phase1_active=true` の意味
- `計画/AI事後評価運用_Ver02.4-v1.md`
  - `daily-sync` と `sync-ai-post-reviews` の運用
- `運用/実務/運用コマンドメモ.md`
  - 日常の確認コマンド

## フォルダ

- `計画/`
  - 現行の中期判断
- `運用/`
  - 日常の実務メモ
- `履歴/`
  - 進行ログと例外メモ
- `reports/`
  - 日次・週次の出力
- `参考資料/`
  - 旧版メモと補助資料
