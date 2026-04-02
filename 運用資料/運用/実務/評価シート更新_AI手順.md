# 評価シート更新 AI 手順

更新日: 2026-03-30 23:57 JST

この手順は、ユーザーから「評価シートを更新してください」と依頼されたときの最短実行用です。

## 目的

- 通知評価フォームと関連データを最新状態へ更新する。
- 更新対象:
  - iCloud 側 `評価シート入力フォーム.html`
  - iCloud 側 `通知評価シート.md`
  - repo 側 `logs/review/review_form_state.json`
  - repo 側 `logs/csv/user_reviews.csv`

## 実行前チェック

1. カレントディレクトリが `btc_monitor` であることを確認する。
2. 既存の未整理変更は巻き込まない（`git status` で確認する）。

## 実行コマンド

```bash
./.venv312/bin/python tools/log_feedback.py export-review-queue
```

## 失敗時の対応

- `PermissionError` で iCloud 側に書き込めない場合:
  - 同じコマンドを権限昇格で再実行する。
  - 目的は「iCloud 側フォームと通知評価シートの再生成」と明記する。

## 更新確認

次の 4 ファイルの更新時刻を確認する。

```bash
ls -l \
  '/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/評価シート入力フォーム.html' \
  '/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/通知評価シート.md' \
  logs/review/review_form_state.json \
  logs/csv/user_reviews.csv
```

## ユーザー報告テンプレ

- 実行コマンド
- 更新された 4 ファイル
- 実行時刻
- 補足（未追跡ファイルなど、今回作業外のものがあれば明記）
