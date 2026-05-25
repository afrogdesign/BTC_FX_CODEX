---
title: ChatGPT 作業ディレクトリ正規化 Codex 申し送り
date: 2026-05-26
tags:
  - btc-monitor
  - codex
  - handoff
  - chatgpt
---

> [!abstract]
> この文書は、`ver02.6-v1` ブランチに追加済みの `chatgpt/` ディレクトリを、repo運用ルールに沿って正規化するための Codex 実行依頼です。ChatGPT 側で途中まで作成したファイルを整理し、今後の正本ディレクトリとして使える状態に整えます。

## 📋 目次

- [[#🎯 目的]]
- [[#🌿 対象ブランチ]]
- [[#📌 現在の状態]]
- [[#🧩 変更範囲]]
- [[#🛠 実装内容]]
- [[#🧪 検証方法]]
- [[#✅ 完了条件]]
- [[#⚠️ 注意事項]]

---

## 🎯 目的

`chatgpt/` 配下を、ChatGPT と Codex の役割分離を前提とした正本ディレクトリとして整備する。

ChatGPT は診断、考察、設計、仕様化、フェーズ判断を担当する。
Codex は確定済み仕様に基づく実装、テスト、Git操作、ファイル生成を担当する。

今回の目的は、実装ロジックの変更ではなく、今後の運用の受け皿となる文書・ディレクトリ構造を正規化すること。

---

## 🌿 対象ブランチ

```txt
ver02.6-v1
```

---

## 📌 現在の状態

ChatGPT 側で、GitHub API 経由により以下を作成済み。

```txt
chatgpt/README.md
chatgpt/analysis/README.md
chatgpt/analysis/.gitkeep
chatgpt/specs/readme.txt
chatgpt/templates/spec_template.md
chatgpt/initial_settings.md
```

ただし、一部はAPI制約回避のため理想形ではない。
特に `chatgpt/specs/readme.txt` は `chatgpt/specs/README.md` に正規化する必要がある。

---

## 🧩 変更範囲

### 触ってよいファイル

```txt
chatgpt/README.md
chatgpt/analysis/README.md
chatgpt/analysis/.gitkeep
chatgpt/specs/readme.txt
chatgpt/specs/README.md
chatgpt/specs/.gitkeep
chatgpt/templates/spec_template.md
chatgpt/templates/.gitkeep
chatgpt/initial_settings.md
```

### 触らないファイル

```txt
.env
logs/
tmp/
src/
config.py
main.py
運用資料/
```

今回、BTC判定ロジック、通知ロジック、trade gate、score、phase判定には触らない。

---

## 🛠 実装内容

### 1. 最新状態を取得

```bash
git checkout ver02.6-v1
git pull origin ver02.6-v1
```

---

### 2. 現在の `chatgpt/` 構造を確認

```bash
find chatgpt -maxdepth 3 -type f | sort
```

---

### 3. `specs/readme.txt` を `specs/README.md` に正規化

```bash
mv chatgpt/specs/readme.txt chatgpt/specs/README.md
```

内容は以下にする。

```md
# specs

このディレクトリには、Codex に渡す確定済み仕様書の正本を保存します。

ここに置く文書は、ChatGPT 側で目的、変更範囲、成功条件、検証方法が固まった後の実装指示として扱います。

Codex はこのディレクトリ内の仕様書をもとに、実装、テスト、Git操作を行います。

## 運用ルール

- 未確定の考察は置かない。
- ChatGPT が設計を確定した仕様だけを置く。
- Codex はこのディレクトリの仕様書を実務実行の正本として扱う。
- 実装判断が必要になった場合は、実装せず確認事項として返す。
```

---

### 4. `.gitkeep` を追加

以下を追加する。

```bash
touch chatgpt/specs/.gitkeep
touch chatgpt/templates/.gitkeep
```

---

### 5. `analysis/README.md` を日本語運用文書へ整える

内容は以下にする。

```md
# analysis

このディレクトリには、ChatGPT が行う診断、考察、改善案比較のレポートを保存します。

ここに置く文書は、まだ実装仕様として確定していない分析・仮説・比較検討のための資料です。

## 保存するもの

- ログやレポートの読解結果
- 原因仮説
- 改善案の比較
- gate や score の再設計案
- Codex に追加調査を依頼するための整理

## 保存しないもの

- Codex にそのまま実装させる確定仕様
- 実装済みコードの説明だけの文書
- 秘密情報
- `.env` の内容
- APIキー、秘密鍵、個人情報

## 命名規則

```txt
YYYYMMDD_topic.md
```

例:

```txt
20260526_sl_hit_redesign.md
20260526_trend_flip_review.md
```

## specs との違い

`analysis/` は考察用です。
`specs/` は確定仕様用です。

分析が終わり、実装方針が固まったものだけを `specs/` に移してください。
```

---

### 6. `initial_settings.md` を確認

`chatgpt/initial_settings.md` は ChatGPT プロジェクトの「情報源」に登録するための初期設定ファイル。

最低限、以下が入っていることを確認する。

- ChatGPT は診断・設計・フェーズ判断担当。
- Codex は確定済み仕様の実務実行担当。
- 最初に読む順番。
- 現在の前提。
- 直近の設計テーマ。
- 診断で重視する点。
- Codexへ渡す実行指示の形。
- 実弾発注、秘密鍵、取引所APIは明示許可まで対象外。

不足があれば補完する。

---

## 🧪 検証方法

以下を実行する。

```bash
find chatgpt -maxdepth 3 -type f | sort
```

期待される出力に以下が含まれること。

```txt
chatgpt/README.md
chatgpt/analysis/.gitkeep
chatgpt/analysis/README.md
chatgpt/initial_settings.md
chatgpt/specs/.gitkeep
chatgpt/specs/README.md
chatgpt/specs/20260526_codex_handoff_chatgpt_scaffold_normalization.md
chatgpt/templates/.gitkeep
chatgpt/templates/spec_template.md
```

続けて差分を確認する。

```bash
git status
git diff
```

---

## ✅ 完了条件

以下が満たされれば完了。

| 項目 | 条件 |
|---|---|
| ディレクトリ | `chatgpt/` 配下が期待構造になっている |
| specs | `specs/readme.txt` が `specs/README.md` に正規化されている |
| gitkeep | `specs/.gitkeep` と `templates/.gitkeep` が存在する |
| analysis | `analysis/README.md` が日本語運用説明になっている |
| template | `templates/spec_template.md` が残っている |
| settings | `initial_settings.md` が情報源として使える内容になっている |
| commit | 変更が `ver02.6-v1` にコミットされている |

---

## ⚠️ 注意事項

- `.env` には触らない。
- `logs/` には触らない。
- `tmp/` には触らない。
- 実装ロジックには触らない。
- BTC判定ロジック、通知ロジック、trade gate、score、phase判定は今回の対象外。
- 今回は `chatgpt/` 配下の文書・ディレクトリ整備のみ。
- 判断が必要な箇所が出た場合は、勝手に実装せず確認事項として返す。

---

## Codex 推奨コミットメッセージ

```txt
20260526: normalize ChatGPT workflow scaffold
```
