# ChatGPT 作業ディレクトリ

このフォルダーは、BTC Monitor プロジェクトにおける ChatGPT 専用の作業領域です。

ChatGPT は診断、考察、設計、仕様化を担当し、Codex は確定済み仕様に基づいて実装、テスト、Git 操作を担当します。

## ディレクトリ構造

```txt
chatgpt/
├── analysis/
├── specs/
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

### `specs/`

Codex に渡す確定済み仕様書の正本を保存します。

ここに置かれたファイルは、Codex が実装判断ではなく実務実行に使うための文書です。

例:

```txt
chatgpt/specs/20260526_entry_gate_update.md
```

### `templates/`

分析レポートや仕様書のテンプレートを保存します。

### `initial_settings.md`

ChatGPT プロジェクトの「情報源」に登録する初期設定ファイルです。

## 運用原則

- ChatGPT は先に設計する。
- Codex は確定仕様だけを実装する。
- 仕様が曖昧な状態で Codex に実装させない。
- 実弾発注、取引所API送信、秘密鍵連携は明示許可があるまで対象外にする。
- 正本となる文書は GitHub 上の `chatgpt/` に置く。
