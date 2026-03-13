# CLI と API の定期比較レポート

更新日: 2026-03-13 10:30 JST

このファイルは、`Ver02.1 API` と `Ver02.1 CLI` の安定性を定期的に見比べるための正本レポートです。
単発の異常メモではなく、同じ観点を毎回更新して「CLI に切り替えてよいか」を判断する材料にします。

## このレポートの使い方

- 1 回の印象ではなく、数サイクル単位の傾向を見る
- 毎回、下の `比較サマリー` と `今回の判断` を更新する
- 例外や気になる1回分の深掘りは、別の単発メモへ逃がしてよい

## 比較対象

- API 側: `Ver02.1 API` 本番スナップショット
- CLI 側: `Ver02.1 CLI` 開発環境
- 目的: 将来的に CLI へ寄せられるかを、安定性中心で判断する

補足:

- 2026-03-13 10:30 JST 以降、このレポートの成功率集計は `Ver02.1` 以降だけを対象にする
- 古い `Ver02` ログは削除せず残すが、この定期比較の母集団には入れない
- そのため、API 側は現時点では「まだ `Ver02.1 API` の新しい pull 前で母数 0 件」という扱いになる

## 重要な見る項目

- `ai_decision` が埋まった率
- `summary_body` が埋まった率
- `logs/errors/` の発生回数
- タイムアウト発生回数
- 件名の読みやすさとフォールバック頻度
- 通知発生時の `notify_reason_codes` と本文差

## 比較サマリー

| 区分 | 母数 | `ai_decision` 成功率 | `summary_body` 成功率 | 両方成功かつ `data_quality_flag=ok` | 今の見え方 |
| --- | ---: | ---: | ---: | ---: | --- |
| `Ver02.1 API` 本番スナップショット | 0 | 0 / 0 | 0 / 0 | 0 / 0 | まだ新しい本番 pull 前。現時点では比較用母数なし |
| `Ver02.1 CLI` ローカル全体 | 17 | 6 / 17 = 35.3% | 17 / 17 = 100% | 6 / 17 = 35.3% | `Ver02.1` 初期の不安定期間を含む全体像 |
| `Ver02.1 CLI` 明示ラベル後 | 4 | 4 / 4 = 100% | 4 / 4 = 100% | 4 / 4 = 100% | `[CLI]` 件名導入後は安定 |
| `Ver02.1-sandbox CLI` | 6 | 6 / 6 = 100% | 6 / 6 = 100% | 6 / 6 = 100% | 隔離確認では安定。比較環境を汚さず検証できた |

## 今回の集計条件

- `Ver02.1 API` 本番スナップショット:
  - `tmp/prod_ver02_snapshot/signals/*.json` のうち `system_label=Ver02.1` かつ `system_mode_label=API`
- `Ver02.1 CLI` ローカル全体:
  - `logs/signals/*.json` のうち `system_label=Ver02.1`
- `Ver02.1 CLI` 明示ラベル後:
  - `logs/signals/*.json` のうち `system_label=Ver02.1` かつ `system_mode_label=CLI`
- `Ver02.1-sandbox CLI`:
  - `/Users/marupro/CODEX/BTC_FX_CODEX_sandbox/btc_monitor/logs/signals/*.json` のうち `system_label=Ver02.1-sandbox`

成功判定の定義:

- `ai_decision` 成功:
  - `ai_decision` が空でなく、`ai_advice` が JSON で入っている
- `summary_body` 成功:
  - `summary_body` が空でない
- 両方成功:
  - 上の 2 条件を満たし、`data_quality_flag=ok` かつ `data_missing_fields` に `ai_response` がない

## 直近観測メモ

### 2026-03-13 10:30 JST 時点

- このレポートは `Ver02.1` 以降だけに集計を仕切り直した
- `Ver02.1 API` 側は、まだ新しい本番スナップショットを pull していないため、比較用母数は 0 件
- `Ver02.1 CLI` ローカル全体では 17 件中 6 件成功で、初期の不安定期間がまだ強く残っている
- ただし `[CLI]` ラベル導入後の明示区間では 4 / 4 成功、sandbox でも 6 / 6 成功で、直近の安定度は高い
- したがって、いま必要なのは CLI をさらに疑うことではなく、`Ver02.1 API` 側の新しい母数を取り直して、公正な比較を始めること

## 今回の判断

- 古い `Ver02` 履歴を混ぜた比較はやめ、`Ver02.1` からの比較へ切り替えた
- 現時点では `Ver02.1 API` 側の母数が 0 件なので、API と CLI の優劣はまだ判定しない
- 一方で `Ver02.1 CLI` の直近区間は安定しており、少なくとも「CLI は現時点でも不安定」という言い方はもう適切ではない
- 当面の判断は、「API 側の新しい本番 pull を取るまで採用判断は保留。ただし CLI 直近安定度は良好」とする

## 次回更新で必ず見ること

- API 側の新しい本番スナップショットを pull して、`Ver02.1 API` の母数を 0 件から更新できたか
- CLI 側で `ai_advice_error` / `ai_summary_error` が再発したか
- `[CLI]` 明示ラベル後のローカル母数が 10 サイクル以上まで増えたか
- 初回通知発生時に、件名・本文・`notify_reason_codes` を API / CLI で並べて比べられたか

## 更新ルール

- このファイルは上書き更新で使う
- 古い時点の細かい経緯は `progress.md` や打ち合わせノートへ逃がす
- 単発比較メモは履歴として残してよいが、定期判断の正本はこのファイルに寄せる

## 関連資料

- 履歴メモ: `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/reports/log_review_ver02_vs_ver021_20260312.md`
- 打ち合わせノート: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_デジタルスキル/00_PROJECT/FX/トレード支援システム/📒打ち合わせノート.md`
- 直近タスク: `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/NEXT_TASK.md`
