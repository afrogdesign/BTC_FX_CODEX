# BTC Monitor

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

### コードを本番 Ver02.1 へ反映する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/deploy_ver021_prod.sh
```

### 本番 Ver02.1 ログをローカルへ取得する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/pull_ver021_prod_logs.sh
```

補足:

- これで「コード反映」と「実データ確認」を分けて扱えます。
- `.env`、仮想環境、`logs/` は本番側のまま残るため、実運用データを消しにくい構成です。
- 件名は `SYSTEM_LABEL` に加えて実行モードも自動で付きます。
  - 例: `[Ver02.1] [API] [BTC監視] ...`
  - 例: `[Ver02.1] [CLI] [BTC監視] ...`
