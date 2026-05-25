# ChatGPT 作業ディレクトリ

このフォルダーは、BTC Monitor プロジェクトにおける ChatGPT 専用の作業領域です。

ChatGPT は診断、考察、設計、仕様化を担当し、Codex は確定済み仕様に基づいて実装、テスト、Git 操作を担当します。
設定の正本は `運用資料/ChatGPTプロジェクト設定.md` に置き、最新の状態と次指示の正本は `運用資料/NEXT_TASK.md` に置きます。
レポート導線の案内板は `運用資料/reports/report_hub_latest.md` に置きます。
このディレクトリは入口と受け渡しに絞って使います。

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

例:

```txt
chatgpt/analysis/20260526_sl_hit_redesign.md
chatgpt/analysis/20260526_trend_flip_review.md
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
- 実装仕様の正本は `chatgpt/specs/active/` に置く。
- 実施済み仕様は `chatgpt/specs/archive/` に移す。
