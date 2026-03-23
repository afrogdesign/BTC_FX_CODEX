# BTC Monitor

更新日: 2026-03-23 18:35 JST

BTC監視システムの実行プロジェクトです。

## セットアップ
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
python3.12 -m venv .venv312
.venv312/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

## 実行
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
.venv312/bin/python main.py
```

## 補足
- 運用メモ・手順書は `運用資料/` にあります。
- 市場構造の補助データとして Binance の公開APIも使います。
- Funding 閾値（`FUNDING_*`）は `%` 単位で設定します（例: `0.05` は `0.05%`）。

## AI の切り替え

- 助言と要約は、それぞれ `API / CLI` を別々に切り替えられます。
- `.env` の設定例:

```bash
AI_ADVICE_PROVIDER=api
AI_SUMMARY_PROVIDER=cli
AI_ADVICE_CLI_COMMAND=
AI_SUMMARY_CLI_COMMAND=/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/tools/codex_cli_wrapper.py
```

- `AI_ADVICE_PROVIDER`
  - `api` なら OpenAI API を使います
  - `cli` なら `AI_ADVICE_CLI_COMMAND` を実行します
- `AI_SUMMARY_PROVIDER`
  - `api` なら OpenAI API を使います
  - `cli` なら `AI_SUMMARY_CLI_COMMAND` を実行します
- CLI モードでは、監視システムは JSON を標準入力へ渡し、標準出力を受け取ります。
  - 助言CLIは JSON オブジェクトを返す必要があります
  - 要約CLIは本文テキストを返す想定です
- 同じラッパーを両方に使えます。
  - `AI_ADVICE_CLI_COMMAND=/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/tools/codex_cli_wrapper.py`
  - `AI_SUMMARY_CLI_COMMAND=/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/tools/codex_cli_wrapper.py`
  - ラッパー側は、入力 JSON の `task` を見て `summary` と `ai_advice` を自動で切り替えます

## 本番運用の考え方

- Git は「コードの正本」に使います。
  - 正本: いちばん信頼して管理する元データ
- `logs/` や実行中に増える CSV / JSON は Git へ入れません。
- 本番 MBP2020 への反映は、`git ls-files` を元にした `rsync` 配備へ寄せます。
- 本番ログの確認は、必要なものだけを別同期します。
- 実行履歴は `運用資料/progress.md` を軽く保ち、重い履歴は `運用資料/progress_weekly/` へ週ごとに退避します。
- `tmp/` は `status/`、`snapshots/`、`errors/` に分け、日常確認では `status/` だけを見ます。

### コードを本番 Ver02.1 へ反映する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/deploy_ver021_prod.sh
```

### 本番 Ver02.1 状態を軽く同期する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/sync_ver021_prod_status.sh
```

補足:

- まずはこちらを普段使いの入口にします。
- 本番からは `heartbeat.txt`、`last_result.json`、`monitor.pid` だけを軽量取得します。
- そのあと `tmp/status/prod_status_summary.json` と `tmp/status/prod_status_summary.md` を作り、重いログを毎回読み直さなくてよい形にします。

### 2時間ごとの軽量同期を登録する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/start_prod_status_sync.sh
```

補足:

- 基本は `iMac 2019` 側 `launchd` で `tools/sync_ver021_prod_status.sh` を 2 時間ごとに実行します。
- `MBA M4` は持ち運び前提なので、常設先にはしません。
- 停止するときは `zsh tools/stop_prod_status_sync.sh` を使います。
- 定期処理は `launchd` に固定し、AI の自動巡回は使いません。
- 日常確認は、まず `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt` だけを見ます。

### 本番 Ver02.1 ログをフル取得する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/pull_ver021_prod_logs_auto.sh
```

補足:

- これで「コード反映」と「実データ確認」を分けて扱えます。
- 普段は使わず、通知発生後や詳細調査のときだけ使います。
- `tmp/status/prod_status_summary.md` で足りるあいだは呼びません。
- `tools/pull_ver021_prod_logs.sh` は下位入口で、個別オプションを直接使いたいときだけ呼びます。
- 標準は鍵認証です。パスワード fallback が本当に必要なときだけ `zsh tools/pull_ver021_prod_logs_with_password.sh` を明示的に使います。

### `tmp/` を整理する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/cleanup_tmp_status.sh
```

補足:

- 日常確認用を `tmp/status/`、詳細 snapshot を `tmp/snapshots/`、失敗記録を `tmp/errors/` へ寄せます。
- 古い `.tgz` や不要な `.DS_Store`、比較母集団外の古い snapshot を掃除します。
- `--light` を付けると、`heartbeat.txt`、`last_result.json`、`monitor.pid` だけを取得します。
- `.env`、仮想環境、`logs/` は本番側のまま残るため、実運用データを消しにくい構成です。
- 件名は `SYSTEM_LABEL` に加えて実行モードも自動で付きます。
  - 例: `[Ver02.1] [API] [BTC監視] ...`
  - 例: `[Ver02.1] [CLI] [BTC監視] ...`

### 週次 progress を圧縮する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/archive_progress_week.sh
```

補足:

- `運用資料/progress.md` は入口だけを軽く保ちます。
- 週次アーカイブは「システム本体の変化 / 検証結果 / 未解決」だけを残す方向で圧縮します。
