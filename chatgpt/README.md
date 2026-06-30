# ChatGPT 作業ディレクトリ

現在の AI orchestration entrypoint は `docs/operations/ai-orchestration/START_HERE.md` です。
この `chatgpt/` 配下は reference material であり、active orchestration entrypoint ではありません。

このフォルダーは、BTC Monitor プロジェクトにおける ChatGPT 専用の作業領域です。

ChatGPT は診断、考察、設計、仕様化を担当し、Codex は確定済み仕様に基づいて実装、テスト、Git 操作を担当します。
設定の正本は `運用資料/ChatGPTプロジェクト設定.md` に置き、最新の状態と次指示の正本は `運用資料/NEXT_TASK.md` に置きます。
レポート導線の案内板は `運用資料/reports/report_hub_latest.md` に置きます。
このディレクトリは入口と受け渡しに絞って使います。
古い ChatGPT analysis/spec folders は reference として保持し、現在の repo-local orchestration 正本とは分けて扱います。

## ChatGPT が最初に読む順

1. `運用資料/ChatGPTプロジェクト設定.md`
2. `運用資料/NEXT_TASK.md`
3. `運用資料/reports/report_hub_latest.md`
4. Hub から必要な raw report
5. `chatgpt/README.md`
6. 関連する `chatgpt/analysis/*.md`
7. 必要時だけ `運用資料/開発ロードマップ.md` と `運用資料/履歴/progress.md`

## ディレクトリ構造

```txt
chatgpt/
├── analysis/
├── specs/
│   ├── active/
│   └── archive/
├── templates/
├── README.md
└── initial_settings.md
```

## 各フォルダーの役割

### `analysis/`

ChatGPT が行う診断、考察、改善案比較のレポートを保存します。
旧 analysis は reference material であり、active orchestration entrypoint ではありません。

例:

```txt
chatgpt/analysis/20260526_entry_sl_tp_wait_redesign.md
chatgpt/analysis/20260526_trend_flip_confirmed_up_reassessment.md
```

### `specs/active/`

Codex に渡す、現役の確定済み仕様書を保存します。

ここに置かれたファイルは、Codex が実装判断ではなく実務実行に使うための文書です。

例:

```txt
chatgpt/specs/active/20260526_entry_gate_update.md
```

### `specs/archive/`

実施済み、または履歴参照用の仕様書を保存します。
Codex は通常ここを起点に実装しません。
archive は削除対象ではなく、reference として残します。

### `templates/`

分析レポートや仕様書のテンプレートを保存します。

### `initial_settings.md`

ChatGPT プロジェクトの「情報源」に登録する要約版です。
詳細の正本は `運用資料/ChatGPTプロジェクト設定.md` を参照します。

## 運用原則

- ChatGPT は先に設計する。
- Codex は確定仕様だけを実装する。
- 仕様が曖昧な状態で Codex に実装させない。
- 実弾発注、取引所API送信、秘密鍵連携は明示許可があるまで対象外にする。
- ChatGPT 設定の正本は `運用資料/ChatGPTプロジェクト設定.md` に置く。
- 最新状態と次指示の正本は `運用資料/NEXT_TASK.md` に置く。
- ChatGPT は `NEXT_TASK.md` の次に `運用資料/reports/report_hub_latest.md` を開き、必要な raw report を選ぶ。
- 未確定の継続設計は `chatgpt/analysis/` に残し、次回の ChatGPT がそこから再開できるようにする。
- 実装仕様の正本は `chatgpt/specs/active/` に置く。
- 実施済み仕様は `chatgpt/specs/archive/` に移す。
