## BTC Monitor 共通参照

更新日: 2026-05-17 JST

- 共通ルール: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/00_Global_BOX/10_共通ルール/共通運用ルール.md`
- 記録ファイル構成: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/00_Global_BOX/10_共通ルール/記録ファイル構成.md`
- マシン構成: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/00_Global_BOX/20_環境情報/マシン構成.md`
- ネットワーク全体図: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/00_Global_BOX/20_環境情報/ネットワーク全体図.md`
- デプロイ先一覧: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/00_Global_BOX/20_環境情報/デプロイ先/一覧.md`
- 秘密情報: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/00_Global_BOX/20_環境情報/秘密情報管理.md`

## 基本

- 返答、説明、作業メモは日本語で行う
- まず対象ファイル、関連ファイル、実行フローを確認する
- 変更は必要最小限にとどめる
- Python 実行は原則 `.venv312/bin/python` を使い、システムの `python3` は直接使わない
- 本番影響、破壊的変更、追加料金リスクがあるときだけ事前共有する

## 作業開始

- まず `Global_BOX` の `マシン構成.md` を確認する
- ネットワーク判断が必要なら `ネットワーク全体図.md` を確認する
- デプロイ先や常駐構成を扱うなら `Global_BOX` の `デプロイ先/一覧.md` を確認する
- この案件では `運用資料/README.md` を入口にし、AI は `運用資料/NEXT_TASK.md` → `運用資料/開発ロードマップ.md` の順で読む

## 案件の前提

- 現行主流は `iMac 2019` 上の `ver02.5-v6`
- `Phase 1B-lite` 実装 commit は `1401a69` で、常駐 `com.afrog.btc-monitor` へ反映済み。
- `MBP2020` の `Ver02.1` は停止・凍結済みで、archive 参照用として扱う
- 現行の事後評価運用は `daily-sync` と `sync-ai-post-reviews`
- 案件固有の運用コマンドは `運用資料/運用/実務/運用コマンドメモ.md` を見る

## 記録

- AI の入口は `運用資料/NEXT_TASK.md` → `運用資料/開発ロードマップ.md`
- 実施履歴は `運用資料/履歴/progress.md`
- 例外時だけ `運用資料/履歴/スレッド引き継ぎファイル.md`
- 人向け入口は Obsidian 側 `👩‍⚖️秘書.md`
  - `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/👩‍⚖️秘書.md`
- 人向け履歴は Obsidian 側 `📒打ち合わせノート.md`
  - `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/📒打ち合わせノート.md`
- ユーザーが `報告して` と書いたときは、人向けと AI 向けの報告先を一式更新する
  - AI 向け: `運用資料/NEXT_TASK.md` と `運用資料/履歴/progress.md`
  - 人向け: `👩‍⚖️秘書.md` と `📒打ち合わせノート.md`
  - その時点までの最新の実施内容、判断、次に見る点を反映し、片方だけで終えない

## 👩‍⚖️秘書.md の固定ルール

- `👩‍⚖️秘書.md` は「最新状態だけの短い入口」。履歴、経緯、古い版の説明、詳細な実施内容は書かない。
- 更新時は必ず既存本文を整理し、古い行を残して追記し続けない。
- 見出しは必ず `## 最新状態`、`## 次に見る`、`## 入口` の 3 つだけにする。
- `最新状態` は最大 4 行、`次に見る` は最大 3 行、`入口` は最大 2 リンクにする。
- 書く内容は、主系統、最新コミットまたはデプロイ状態、最新レポートの主要数値、現在の判断だけに絞る。
- 詳細説明、作業履歴、決定の背景、長いリンク集は `📒打ち合わせノート.md`、`NEXT_TASK.md`、`progress.md` へ逃がす。

## 更新

- 次の判断が変わったら `運用資料/NEXT_TASK.md`
- フェーズや大型節目が変わったら `運用資料/開発ロードマップ.md`
- 新しい事実や実作業が出たら `運用資料/履歴/progress.md`
- デプロイ先の実態が変わったら `Global_BOX` 側の該当ページも更新する
