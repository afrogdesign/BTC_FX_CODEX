# CLI と API の定期比較レポート

更新日: 2026-03-13 07:20 JST

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

## 重要な見る項目

- `ai_decision` が埋まった率
- `summary_body` が埋まった率
- `logs/errors/` の発生回数
- タイムアウト発生回数
- 件名の読みやすさとフォールバック頻度
- 通知発生時の `notify_reason_codes` と本文差

## 比較サマリー

| 項目 | API | CLI | 今の見え方 |
| --- | --- | --- | --- |
| `ai_decision` 安定性 | 観測継続中 | 欠落が目立つ | 現時点では API 優勢 |
| `summary_body` 安定性 | 観測継続中 | 概ね出るがタイムアウトあり | CLI は要約だけ遅延の懸念あり |
| `logs/errors/` | スナップショット追随待ち | `ai_summary_error` 1 件確認 | CLI 側で再発有無を監視中 |
| 実通知比較 | 未着手 | 未着手 | 通知発生待ち |
| 将来の採用判断 | 保留 | 保留 | まだ CLI 採用判断は早い |

## 直近観測メモ

### 2026-03-13 07:16 JST 時点

- CLI 側は `signal_id=20260312_220500` まで進み、`last_result.json` と `signals` は更新が進んだ
- CLI 側 `heartbeat.txt` は 07:05 JST のまま
- CLI 側 `logs/errors/20260312_220848_ai_summary_error.log` で、要約生成 60 秒タイムアウトを 1 件確認
- API 側スナップショットは `heartbeat` / `last_result` / `signals` が 06:05 JST のまま据え置き

## 今回の判断

- まだ「CLI に切り替えてよい」とは言えない
- 理由は、CLI 側で `ai_decision` 欠落と要約タイムアウトが残っており、API 側との同時刻比較もまだ十分にそろっていないため
- 当面は API を比較基準に据えたまま、CLI の安定度改善が進むかを定期観測で判断する

## 次回更新で必ず見ること

- API 側スナップショットが CLI 側と近い時刻まで追随したか
- CLI 側で `ai_summary_error` が再発したか
- `ai_decision` / `summary_body` の欠落率が改善したか
- 初回通知発生時に、件名・本文・`notify_reason_codes` を API / CLI で並べて比べられたか

## 更新ルール

- このファイルは上書き更新で使う
- 古い時点の細かい経緯は `progress.md` や打ち合わせノートへ逃がす
- 単発比較メモは履歴として残してよいが、定期判断の正本はこのファイルに寄せる

## 関連資料

- 履歴メモ: `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/reports/log_review_ver02_vs_ver021_20260312.md`
- 打ち合わせノート: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_デジタルスキル/00_PROJECT/FX/トレード支援システム/📒打ち合わせノート.md`
- 直近タスク: `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/NEXT_TASK.md`
