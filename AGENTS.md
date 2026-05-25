## BTC Monitor 共通参照

更新日: 2026-05-26 JST

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

## ChatGPT / Codex 役割分担

- 今後の診断、設計、再考、フェーズ判断、改善案比較、実装前の仕様決定は ChatGPT プロジェクト側で行う。
- Codex は実務実行に徹する。主な担当は、確定済み仕様の実装、テスト、レポート生成、Git 操作、常駐確認、運用資料への実施結果反映。
- Codex は、明示された仕様なしに大きな設計変更、フェーズ昇格判断、gate 緩和判断、売買ロジックの方向性決定を行わない。
- ユーザーから設計判断を求められた場合、Codex は必要な現状確認や材料整理まで行い、最終判断は ChatGPT プロジェクトへ渡す前提で扱う。
- ChatGPT 側で決まった設計を repo に反映するときだけ、Codex が実装計画、コード変更、検証、commit / push を担当する。

## GitHub 上の ChatGPT 作業動線

この repo では、ChatGPT と Codex の受け渡しを GitHub 上の `chatgpt/` ディレクトリで行う。

- `chatgpt/README.md`: ChatGPT 作業ディレクトリ全体の入口。
- `chatgpt/initial_settings.md`: ChatGPT プロジェクトの「情報源」に入れる要約版。正本は `運用資料/ChatGPTプロジェクト設定.md`。
- `chatgpt/analysis/`: ChatGPT が作る診断、考察、比較検討の正本。
- `chatgpt/specs/active/`: Codex が次に実行する現役の確定仕様書。
- `chatgpt/specs/archive/`: 実施済み、または履歴参照用の仕様書。
- `chatgpt/templates/`: ChatGPT と Codex が使う文書テンプレート。

Codex は、ユーザーから「ChatGPT から引き継いで」「仕様書を読んで」「続きの作業」と言われた場合、まず `chatgpt/specs/active/` の最新仕様書だけを確認する。
設計が未確定な話は `chatgpt/analysis/` を確認し、勝手に実装へ進めない。ChatGPT の次判断や最新指示は常に `運用資料/NEXT_TASK.md` を正本とし、レポート導線は `運用資料/reports/report_hub_latest.md` を案内板として使う。

### Codex 作業開始時の固定順

1. `AGENTS.md` を読む。
2. `chatgpt/README.md` を読む。
3. `chatgpt/initial_settings.md` を読む。
4. `chatgpt/specs/active/` の最新仕様書 1 件を確認する。
5. その仕様書の `目的`、`変更範囲`、`実装内容`、`検証方法`、`完了条件`、`注意事項` を確認する。
6. 実装完了後は、検証、必要な raw report 生成、`運用資料/reports/report_hub_latest.md` 更新、archive 整理、`commit / push`、実施済み仕様書の `chatgpt/specs/archive/` への移動までを一連の作業として行う。
7. `active/` が空なら `運用資料/ChatGPTプロジェクト設定.md` → `運用資料/NEXT_TASK.md` を読む。
8. それでも判断が必要なら、実装せず確認事項として返す。

確認コマンド例:

```bash
git checkout ver02.6-v1
git pull origin ver02.6-v1
find chatgpt -maxdepth 3 -type f | sort
ls -lt chatgpt/specs/active/*.md 2>/dev/null | head
```

### ChatGPT から Codex への受け渡しルール

ChatGPT が Codex に実装を渡す場合は、必ず `chatgpt/specs/active/YYYYMMDD_topic.md` に仕様書を置く。

仕様書には最低限、次を含める。

- 目的
- 対象ブランチ
- 変更範囲
- 実装内容
- 検証方法
- 完了条件
- 注意事項

Codex は、`chatgpt/specs/active/` に置かれた最新仕様書を実務実行の正本として扱う。
チャット本文だけを正本にしない。
チャットで追加指示があった場合も、必要なら `chatgpt/specs/active/` の仕様書へ反映してから作業する。
実装が完了した仕様は、検証と `commit / push` の後に `chatgpt/specs/archive/` へ移し、`active/` には未着手の現役仕様だけを残す。

### ChatGPT 分析文書の置き場所

ChatGPT 側の未確定な考察、原因仮説、改善案比較、追加診断依頼は `chatgpt/analysis/` に置く。

`analysis/` の文書は、そのまま実装してよい仕様ではない。
Codex は `analysis/` だけを根拠に gate 緩和、score 変更、trade ロジック変更を行わない。分析が固まったものだけを `chatgpt/specs/active/` へ移す。

### 今回の直近仕様書

- `chatgpt/specs/active/` が現役の実行対象
- `chatgpt/specs/archive/20260526_codex_handoff_chatgpt_scaffold_normalization.md` は実施済みの履歴参照用

## 作業開始

- まず `Global_BOX` の `マシン構成.md` を確認する
- ネットワーク判断が必要なら `ネットワーク全体図.md` を確認する
- デプロイ先や常駐構成を扱うなら `Global_BOX` の `デプロイ先/一覧.md` を確認する
- この案件では `AGENTS.md` → `chatgpt/README.md` → `chatgpt/initial_settings.md` → `chatgpt/specs/active/` → `運用資料/ChatGPTプロジェクト設定.md` → `運用資料/NEXT_TASK.md` → `運用資料/開発ロードマップ.md` の順で読む

## 案件の前提

- 現行主流は `iMac 2019` 上の `ver02.6-v1`
- `Phase 1B-lite` 実装 commit は `1401a69` で、常駐 `com.afrog.btc-monitor` へ反映済み。
- `MBP2020` の `Ver02.1` は停止・凍結済みで、archive 参照用として扱う
- 現行の事後評価運用は `daily-sync` と `sync-ai-post-reviews`
- 案件固有の運用コマンドは `運用資料/運用/実務/運用コマンドメモ.md` を見る

## 記録

- AI の入口は `AGENTS.md` → `chatgpt/README.md` → `chatgpt/specs/active/` → `運用資料/ChatGPTプロジェクト設定.md` → `運用資料/NEXT_TASK.md` → `運用資料/reports/report_hub_latest.md` → `運用資料/開発ロードマップ.md`
- ChatGPT の最新判断、直近レポート名、次に扱う論点は `運用資料/NEXT_TASK.md` に一元管理する
- AI事後評価は日常判断の主系として扱う。`human_override` は必要時だけの例外で、人向け評価導線は進捗メモと上書きUIとして最小限に保つ
- 実施履歴は `運用資料/履歴/progress.md`
- 例外時だけ `運用資料/履歴/スレッド引き継ぎファイル.md`
- 人向け入口は Obsidian 側 `👩‍⚖️秘書.md`
  - `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/👩‍⚖️秘書.md`
- 人向け履歴は Obsidian 側 `📒打ち合わせノート.md`
  - `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/📒打ち合わせノート.md`
- ユーザーが `報告して` と書いたときは、人向けと AI 向けの報告先を一式更新する
  - AI 向け: `運用資料/NEXT_TASK.md` と `運用資料/履歴/progress.md`
  - ChatGPT / Codex 受け渡しに関わる場合: `chatgpt/analysis/` または `chatgpt/specs/active/`
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
- ChatGPT / Codex の作業動線、仕様、申し送りが変わったら `chatgpt/` 配下の該当ファイルも更新する
- デプロイ先の実態が変わったら `Global_BOX` 側の該当ページも更新する
