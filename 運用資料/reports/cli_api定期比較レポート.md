# CLI と API の定期比較レポート

更新日: 2026-03-13 15:16 JST

このファイルは、`Ver02.1 API` と `Ver02.1 CLI` の安定性を見比べるための正本レポートです。
単発の異常メモではなく、比較材料がまとまって増えたときだけ更新して「CLI に切り替えてよいか」を判断する材料にします。

## このレポートの使い方

- 1 回の印象ではなく、数サイクル単位の傾向を見る
- 通知発生時、比較母数が増えた時、判断が変わる材料が出た時だけ更新する
- 例外や気になる1回分の深掘りは、別の単発メモへ逃がしてよい

## 比較対象

- API 側: `Ver02.1 API` 本番スナップショット
- CLI 側: `Ver02.1 CLI` 開発環境
- 目的: 将来的に CLI へ寄せられるかを、安定性中心で判断する

補足:

- 2026-03-13 10:30 JST 以降、このレポートの成功率集計は `Ver02.1` 以降だけを対象にする
- 古い `Ver02` ログは削除せず残すが、この定期比較の母集団には入れない
- 2026-03-13 10:50 JST 時点で、本番 `Ver02.1 API` の最新 pull を取得し、`20260312_220500` から `20260313_010500` の 4 サイクルを比較対象に追加した

## 重要な見る項目

- `ai_decision` が埋まった率
- `summary_body` が埋まった率
- `logs/errors/` の発生回数
- タイムアウト発生回数
- `decision` の一致率
- `quality` の一致率
- `warnings` / `primary_reason` の差
- 件名の読みやすさとフォールバック頻度
- 通知発生時の `notify_reason_codes` と本文差

## モデルと実行系の前提

### API 側

- 助言モデル: `gpt-4o`
- 要約モデル: `gpt-4o-mini`
- 実行系: OpenAI API

### CLI 側

- 入力上の指定モデル:
  - 助言 `gpt-4o`
  - 要約 `gpt-4o-mini`
- ただし実際の CLI 実行では、`codex_cli_wrapper.py` が「Codex 系モデル名でなければ `CODEX_CLI_DEFAULT_MODEL` へ寄せる」実装
- `CODEX_CLI_DEFAULT_MODEL` 未設定時の既定値は `gpt-5.3-codex`

補足:

- つまり今の API / CLI 比較は、「実行方式の差」だけでなく「モデル差」も混ざっている可能性が高い
- CLI 側は定額運用の範囲で上位モデルを使える可能性はあるが、実際にどのモデルが使えるかは Codex 側の利用条件に依存する
- 少なくともローカル実装上は、`CODEX_CLI_DEFAULT_MODEL` を設定すれば CLI 側のモデル比較は可能

## 比較サマリー

| 区分 | 母数 | `ai_decision` 成功率 | `summary_body` 成功率 | 両方成功かつ `data_quality_flag=ok` | 今の見え方 |
| --- | ---: | ---: | ---: | ---: | --- |
| `Ver02.1 API` 本番スナップショット | 8 | 8 / 8 = 100% | 8 / 8 = 100% | 8 / 8 = 100% | 14:05 JST まで取得し安定継続 |
| `Ver02.1 CLI` ローカル全体 | 8 | 8 / 8 = 100% | 8 / 8 = 100% | 8 / 8 = 100% | 14:05 JST まで安定継続 |
| `Ver02.1 CLI` 明示ラベル後 | 8 | 8 / 8 = 100% | 8 / 8 = 100% | 8 / 8 = 100% | `[CLI]` 表示区間で継続安定 |
| `Ver02.1-sandbox CLI` | 6 | 6 / 6 = 100% | 6 / 6 = 100% | 6 / 6 = 100% | 隔離確認では安定。比較環境を汚さず検証できた |

## 今回の集計条件

- `Ver02.1 API` 本番スナップショット:
  - `tmp/prod_ver021_snapshot_live/logs/signals/*.json` のうち `system_label=Ver02.1` かつ `system_mode_label=API`
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

### 2026-03-13 15:16 JST 時点

- `mbp2020-btc` alias と専用鍵 `~/.ssh/mbp2020_btc_monitor` で API 側 snapshot を取得できることを確認した
- API 側 snapshot は `20260313_060501`（15:05 JST）まで更新でき、取得経路は鍵認証が標準になった
- 今回の取得で `tools/pull_ver021_prod_logs_auto.sh` はパスワード入力なしで完走し、Automation 停止要因だった SSH 入力待ちを解消できた

### 2026-03-13 14:57 JST 時点

- API 側 snapshot を追加 pull し、`20260313_050500`（14:05 JST）まで取得を更新した
- `tmp/prod_ver021_snapshot_live/logs/last_result.json` は `system_mode_label=API`、`ai_decision=WAIT_FOR_SWEEP`、`data_quality_flag=ok` を確認した
- CLI 側も `20260313_050500`（14:05 JST）まで更新済みで、`system_mode_label=CLI`、`ai_decision=WAIT_FOR_SWEEP`、`data_quality_flag=ok` を確認した
- `Ver02.1 API` と `Ver02.1 CLI` は、現時点の母数 `8` で `ai_decision` / `summary_body` / 両方成功（`data_quality_flag=ok`）がともに `8 / 8`
- `tools/pull_ver021_prod_logs.sh` は `BTC_MONITOR_PROD_SSH_PASSWORD` を使った非対話実行へ対応し、`Too many authentication failures` ブロッカーを回避できることを確認した

### 2026-03-13 14:43 JST 時点

- 開発 `Ver02.1 CLI` 側は `20260313_050500.json`（14:05 JST）まで自然更新を確認した
- `heartbeat.txt` / `last_result.json` も 14:05 JST へ追随し、`ai_decision=WAIT_FOR_SWEEP`、`data_quality_flag=ok` を確認した
- `logs/errors/` の最新は引き続き `20260312_220848_ai_summary_error.log` で、07:08 JST 以降の新規エラーは確認されなかった
- API 側 snapshot 追加取得のため `zsh tools/pull_ver021_prod_logs.sh` を試行したが、実行環境制約で `ssh: connect to host 192.168.1.38 port 22: Operation not permitted` となり取得失敗
- そのため API 側の比較母数は 10:50 JST 取得分（`20260312_220500`〜`20260313_010500`）から増えていない

### 2026-03-13 11:16 JST 時点

- 開発 `Ver02.1 CLI` 側の自然更新は `20260313_020500.json`（11:05 JST 更新）まで進行した
- `20260312_230500` / `20260313_000500` / `20260313_010500` / `20260313_020500` の 4 サイクルは、`ai_decision`・`summary_body`・`data_quality_flag=ok` が継続し、通知は 0 件だった
- `logs/errors/` の最新は引き続き `20260312_220848_ai_summary_error.log` で、07:08 JST 以降の新規エラー追加は確認されなかった
- API 側は 10:50 JST 取得の snapshot（比較対象 4 サイクル）のままで、新しい pull はまだ取っていない

### 2026-03-13 10:50 JST 時点

- このレポートは `Ver02.1` 以降だけに集計を仕切り直した
- 本番 `Ver02.1 API` の最新 pull を取得し、`20260312_220500` から `20260313_010500` の 4 サイクルを確認できた
- `Ver02.1 API` は 4 / 4 成功で、`last_result.json` も `system_label=Ver02.1`、`system_mode_label=API`、`data_quality_flag=ok`、`ai_decision=WAIT_FOR_SWEEP` を確認した
- `Ver02.1 CLI` ローカル全体では 17 件中 6 件成功で、初期の不安定期間がまだ強く残っている
- ただし `[CLI]` ラベル導入後の明示区間では 4 / 4 成功、sandbox でも 6 / 6 成功で、直近の安定度は高い
- つまり、同じ 4 サイクル範囲では API も CLI も 4 / 4 成功で並んでおり、少なくとも現時点の直近比較では成功率差は見えていない

## AI 判断品質比較

### 2026-03-13 10:05 サイクル比較

同時刻の `20260313_010500.json` を比較すると、JSON の形はそろっているが中身は異なる。

| 項目 | API | CLI | 見え方 |
| --- | --- | --- | --- |
| `decision` | `WAIT_FOR_SWEEP` | `WAIT_FOR_SWEEP` | 一致 |
| `quality` | `C` | `B` | CLI の方が一段強気 |
| `confidence` | `0.78` | `0.78` | 一致 |
| `primary_reason` | 上側流動性回収待ちを強調 | 上側流動性 + sweep未完了を強調 | 近いが説明密度が違う |
| `warnings` | `上側流動性が近い`, `清算クラスターが近い` | `上側流動性が近い`, `sweep未完了`, `板バイアスと衝突` | 危険視する観点が違う |
| 件名 | `RISKY_ENTRY / short / Confidence 51` | `SWEEP_WAIT / short / Confidence 46` | かなり違う |
| 本文 | 文章は丁寧だが一般化されやすい | 具体要因が多く、実務メモ寄り | 読み味が違う |

### 現時点の読み方

- JSON のスキーマはそろっているので、壊れ方のリスクは低い
- ただし `quality`、`warnings`、`primary_reason` がズレるため、本文や件名の差は実際に出る
- したがって、「成功率が同じ」だけでは採用判断はできず、「判断内容がどちらの実務に合うか」も別軸で見る必要がある

## 今回の判断

- 古い `Ver02` 履歴を混ぜた比較はやめ、`Ver02.1` からの比較へ切り替えた
- 最新 pull により、同期間の `Ver02.1 API` 4 件と `Ver02.1 CLI` 4 件を並べて比較できるようになった
- その結果、直近 4 サイクルの成功率は API も CLI も 100% で並んでいる
- したがって、現時点の実務判断は「少なくとも直近比較では CLI は API と同等に安定している」としてよい
- 一方で AI 判断の中身は完全一致しておらず、特に `quality` と `warnings` の差が件名・本文差へつながっている
- そのため、今後の比較では「安定性」と「判断品質」を分けて見る
- ただし母数はまだ少ないため、本番通知発生時の本文品質差と、より長い期間での再発有無は引き続き観測する

## 次回更新で必ず見ること

- API 側の新しい本番スナップショットを定期的に pull し、`Ver02.1 API` の母数を増やせたか
- CLI 側で `ai_advice_error` / `ai_summary_error` が再発したか
- `[CLI]` 明示ラベル後のローカル母数が 10 サイクル以上まで増えたか
- 同時刻サイクルで `decision` / `quality` / `warnings` の一致率を比較できたか
- CLI 側のモデル設定を固定したうえで、モデル差と実行方式差を分けて見られるようにできたか
- 初回通知発生時に、件名・本文・`notify_reason_codes` を API / CLI で並べて比べられたか

## 更新ルール

- このファイルは上書き更新で使う
- 小さな読取確認のたびには更新しない
- 古い時点の細かい経緯は `progress.md` や打ち合わせノートへ逃がす
- 単発比較メモは履歴として残してよいが、定期判断の正本はこのファイルに寄せる

## 関連資料

- 履歴メモ: `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/reports/log_review_ver02_vs_ver021_20260312.md`
- 打ち合わせノート: `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️ デジタルスキル/00_🗃️ PROJECT/📁 FX/トレード支援システム/📒打ち合わせノート.md`
- 直近タスク: `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/運用資料/NEXT_TASK.md`
