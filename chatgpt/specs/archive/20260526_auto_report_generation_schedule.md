# 20260526 auto report generation schedule

## Codex 実行依頼

### 目的

BTC Monitor のレポート生成を、毎回 ChatGPT / Codex へ手動依頼しなくても回せるようにする。

ただし、今回の対象は **レポート生成の自動化・半自動化** であり、実弾発注・取引所API送信・秘密鍵連携・trade gate 緩和には一切触れない。

現時点では、監視本体は `launchd` 常駐で自動実行されている。一方、Markdown レポート群は `tools/log_feedback.py` の CLI で生成できるが、毎日どの順番で生成するか、どこにログを残すか、失敗時にどう止めるかがまだ整理されていない。

この仕様では、既存 CLI を壊さず、定期実行しやすい薄いラッパーを追加する。

---

## 対象ブランチ

`ver02.6-v2`

このブランチ名は `運用資料/NEXT_TASK.md` の `現在の作業ブランチ` を正本として採用する。
`main` や remote branch 一覧から推測しない。

---

## 参照する正本

Codex は最初に以下を読む。

1. `運用資料/ChatGPTプロジェクト設定.md`
2. `運用資料/NEXT_TASK.md`
3. `運用資料/計画/latest_integrated_plan_20260526.md`
4. `運用資料/reports/report_hub_latest.md`
5. `tools/log_feedback.py`
6. `運用資料/運用/実務/ログ検証と改善運用ガイド.md` が存在する場合は参照する
7. `chatgpt/specs/active/20260526_entry_wait_trend_flip_quality_guard.md`

---

## 現状認識

### 自動で回っているもの

- BTC 監視本体
- `logs/heartbeat.txt`
- `logs/last_result.json`
- `logs/csv/trades.csv` などの通常ログ

### 半自動・手動寄りのもの

- `feedback_daily_sync_YYYYMMDD.md`
- `market_map_effectiveness_YYYYMMDD.md`
- `operational_focus_YYYYMMDD.md`
- `paper_opportunity_diagnostics_YYYYMMDD.md`
- `paper_entry_sl_wait_redesign_YYYYMMDD.md`
- `report_hub_latest.md`

これらは `tools/log_feedback.py` の既存 CLI で生成できるが、現時点では「いつ・どの順序で・どのログを残して・失敗時にどう扱うか」が定期実行用に明確化されていない。

---

## 重要方針

### 1. 既存 CLI を主系にする

新しい集計ロジックを大量に作らない。

主系はあくまで以下。

```bash
.venv312/bin/python tools/log_feedback.py daily-sync
.venv312/bin/python tools/log_feedback.py build-paper-opportunity-diagnostics-report
.venv312/bin/python tools/log_feedback.py build-market-map-effectiveness-report
.venv312/bin/python tools/log_feedback.py build-operational-focus-report
.venv312/bin/python tools/log_feedback.py build-report-hub
```

Codex はこの既存 CLI を安全に呼ぶ wrapper を作る。

### 2. GitHub への自動 push は実装しない

今回、自動 commit / push は実装しない。

理由:

- レポート自動生成の失敗・日付ズレ・重複生成が起きた場合、不要な commit が積まれる。
- まずはローカルで daily report set を安定生成できることを優先する。
- GitHub 反映は Codex 指示または人間判断で行う。

### 3. 実弾関連には触らない

以下は禁止。

- 実弾発注
- 取引所API送信
- 秘密鍵・APIキー連携
- `trade_execution_gate` の pass 条件変更
- `paper_orders planned` を増やすための gate 緩和
- `Phase 1B-lite` の正式昇格

### 4. 失敗しても監視本体を止めない

レポート生成に失敗しても、BTC 監視本体は止めない。

ただし、エラーは明確に保存する。

---

## 追加するファイル

### 1. `tools/run_daily_reports.py`

新規追加。

役割:

- 既存の `tools/log_feedback.py` CLI を順番に呼び出す。
- 日付を JST 基準で決める。
- 出力先を統一する。
- 実行ログ・エラーログを `logs/runtime/` に残す。
- 失敗したコマンドがあっても、どこで失敗したか分かるようにする。

### 2. `運用資料/運用/実務/定期レポート生成ガイド.md`

新規追加。

役割:

- 何が自動で作られ、何が手動かを説明する。
- 手動実行コマンドを書く。
- launchd / cron に載せる場合の注意を書く。
- GitHub 自動 push はまだしないことを明記する。

### 3. 任意: `運用資料/運用/環境/launchd_定期レポート設定例.plist.txt`

任意追加。

役割:

- 実際に自動化する場合の launchd 設定例。
- ただし plist を本番 `~/Library/LaunchAgents/` に配置する作業はしない。
- repo 内に「例」として置くだけ。

---

## `tools/run_daily_reports.py` の仕様

### CLI 仕様

```bash
.venv312/bin/python tools/run_daily_reports.py
```

オプション:

```bash
--date YYYYMMDD
--date-from YYYY-MM-DD
--date-to YYYY-MM-DD
--max-new-ai-reviews 8
--skip-ai
--skip-heavy
--dry-run
--python-bin .venv312/bin/python
```

### デフォルト挙動

- JST の今日を `YYYYMMDD` として使う。
- `date-to` は JST 今日。
- `date-from` は未指定なら `2026-04-18` を使う。
  - 理由: 現在の紙ポジション診断の基準期間と合わせるため。
- `max-new-ai-reviews` は 8。
  - 理由: `NEXT_TASK.md` で daily cap 8 が安定とされているため。

### 実行するコマンド

デフォルトでは以下を順に実行する。

```bash
.venv312/bin/python tools/log_feedback.py daily-sync \
  --max-new-ai-reviews 8 \
  --output-md 運用資料/reports/feedback_daily_sync_YYYYMMDD.md

.venv312/bin/python tools/log_feedback.py build-paper-opportunity-diagnostics-report \
  --date-from 2026-04-18 \
  --date-to YYYY-MM-DD \
  --output-md 運用資料/reports/analysis/paper_opportunity_diagnostics_YYYYMMDD.md

.venv312/bin/python tools/log_feedback.py build-market-map-effectiveness-report \
  --date-from 2026-05-13 \
  --date-to YYYY-MM-DD \
  --output-md 運用資料/reports/analysis/market_map_effectiveness_YYYYMMDD.md

.venv312/bin/python tools/log_feedback.py build-operational-focus-report \
  --date-from 2026-04-18 \
  --date-to YYYY-MM-DD \
  --output-md 運用資料/reports/analysis/operational_focus_YYYYMMDD.md

.venv312/bin/python tools/log_feedback.py build-paper-entry-sl-wait-redesign-report \
  --date-from 2026-04-18 \
  --date-to YYYY-MM-DD \
  --output-md 運用資料/reports/analysis/paper_entry_sl_wait_redesign_YYYYMMDD.md

.venv312/bin/python tools/log_feedback.py build-report-hub
```

重要:

- `build-paper-entry-sl-wait-redesign-report` がまだ存在しない場合は、Codex は勝手に実装しない。
- 既存 CLI 名を確認し、存在しなければそのステップを `skipped_missing_command` としてログに残す。
- ただし、`paper_entry_sl_wait_redesign_YYYYMMDD.md` を生成する既存関数・既存コマンドがあるなら、それを使う。

### `--skip-heavy`

`--skip-heavy` 指定時は、重めの分析を省略する。

実行するもの:

- `daily-sync`
- `build-operational-focus-report`
- `build-report-hub`

省略するもの:

- `build-paper-opportunity-diagnostics-report`
- `build-market-map-effectiveness-report`
- `paper_entry_sl_wait_redesign` 系

### `--skip-ai`

`--skip-ai` 指定時は、`daily-sync` の `--max-new-ai-reviews` を 0 にする。

### `--dry-run`

`--dry-run` 指定時は、実行予定コマンドを表示するだけで、ファイル生成はしない。

---

## ログ仕様

### 出力するログ

```text
logs/runtime/daily_reports.out
logs/runtime/daily_reports.err
logs/runtime/daily_reports_last_result.json
```

### `daily_reports_last_result.json` の例

```json
{
  "started_at_jst": "2026-05-26T06:00:00+09:00",
  "finished_at_jst": "2026-05-26T06:03:12+09:00",
  "status": "success",
  "date": "20260526",
  "date_from": "2026-04-18",
  "date_to": "2026-05-26",
  "steps": [
    {
      "name": "daily-sync",
      "status": "success",
      "returncode": 0,
      "output_md": "運用資料/reports/feedback_daily_sync_20260526.md"
    }
  ]
}
```

### 失敗時

- どれか1つ失敗したら全体 `status` は `partial_failed` にする。
- 失敗コマンドの stderr を `daily_reports.err` に追記する。
- 後続の `build-report-hub` は可能なら最後に実行する。
  - ただし、主要レポートが生成できていない場合でも、hub 更新が危険なら skip してよい。
- 監視本体は止めない。

---

## launchd / cron の扱い

今回、Codex は本番環境へ plist をインストールしない。

repo 内に設定例を置くだけにする。

### 推奨時刻

JST 06:10 など、BTC監視サイクルが落ち着いた後に実行する想定。

理由:

- daily-sync は通知後24時間経過した対象を評価する性質がある。
- 深夜〜早朝に一度まとめて処理する方が、日次レポートとして読みやすい。

### 設定例に含めること

- `WorkingDirectory`
- `.venv312/bin/python`
- `tools/run_daily_reports.py`
- `--max-new-ai-reviews 8`
- 標準出力: `logs/runtime/daily_reports.launchd.out`
- 標準エラー: `logs/runtime/daily_reports.launchd.err`

---

## テスト / 検証

Codex は以下を実行する。

### 1. 構文チェック

```bash
.venv312/bin/python -m py_compile tools/run_daily_reports.py
```

### 2. dry-run

```bash
.venv312/bin/python tools/run_daily_reports.py --date 20260526 --dry-run
```

確認:

- 実行予定コマンドが表示される。
- ファイルを生成しない。
- exit code 0。

### 3. skip-heavy 実行

```bash
.venv312/bin/python tools/run_daily_reports.py --date 20260526 --skip-heavy --skip-ai
```

確認:

- `daily-sync` は `--max-new-ai-reviews 0` で動く。
- `operational_focus` と `report_hub` が実行される。
- `logs/runtime/daily_reports_last_result.json` が生成される。

### 4. 既存テスト

```bash
.venv312/bin/python -m pytest
```

repo で既定のテストコマンドが別にある場合は、それを優先し、実行したコマンドを記録する。

---

## 完了条件

- `tools/run_daily_reports.py` が追加されている。
- `--dry-run` が動く。
- `--skip-heavy --skip-ai` が動く。
- `logs/runtime/daily_reports_last_result.json` が生成される。
- 既存の `tools/log_feedback.py` の集計ロジックを壊していない。
- `build-report-hub` が最後に呼ばれる。
- GitHub 自動 push は実装していない。
- 実弾発注・取引所API送信・秘密鍵連携に触っていない。
- `運用資料/運用/実務/定期レポート生成ガイド.md` が追加されている。
- launchd 設定は「例」だけで、本番配置はしていない。
- 変更内容を `運用資料/NEXT_TASK.md` または `運用資料/履歴/progress.md` に短く記録する。

---

## 注意事項

- この仕様は自動レポート生成の設計であり、自動トレード化ではない。
- 自動 commit / push は今回対象外。
- `trade_execution_gate` には触らない。
- `paper_orders planned` を増やす変更はしない。
- `Phase 1B-lite` を正式昇格しない。
- レポート生成に失敗しても監視本体は止めない。
- 失敗内容は `logs/runtime/daily_reports.err` と `daily_reports_last_result.json` に残す。

---

## 実装後に ChatGPT が確認すること

- `daily_reports_last_result.json` の `status`
- 生成された `feedback_daily_sync_YYYYMMDD.md`
- 生成された `paper_opportunity_diagnostics_YYYYMMDD.md`
- 生成された `market_map_effectiveness_YYYYMMDD.md`
- 生成された `operational_focus_YYYYMMDD.md`
- `report_hub_latest.md` が最新レポートへ向いているか
- `daily_reports.err` が空、または許容できる warning だけか
- AI事後評価 `request_failed` が増えていないか
