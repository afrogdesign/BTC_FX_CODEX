# BTC FX CODEX

BTC FX CODEX is an AI-assisted BTC market monitoring project.

BTC/FX の相場データを定期的に取得し、テクニカル指標・市場構造・流動性・Funding Rate・建玉/出来高系の情報を整理して、判断材料として読みやすく通知するための監視システムです。

> [!WARNING]
> このプロジェクトは投資助言、売買指示、自動売買の推奨を目的としたものではありません。出力される分析や通知は、学習・検証・個人の判断補助のための情報です。実際の取引判断は利用者自身の責任で行ってください。

---

## Overview

このリポジトリは、BTC/FX 取引における「見るべき情報が多すぎる」「判断材料が散らばる」「ログが残らない」という問題を減らすために作られています。

主な目的は次のとおりです。

- BTC/USDT 周辺の市場データを定期取得する
- 複数時間足の構造、指標、流動性、Funding Rate を整理する
- AI による要約・補助コメントを生成する
- メール通知やログ保存によって、あとから検証できる形にする
- Codex / OpenAI API / CLI を使ったメンテナンス・検証ワークフローを育てる

このプロジェクトはまだ成長段階ですが、金融系ツールとして扱うため、テスト、レビュー、依存関係管理、ログ管理、認証情報の扱いを重視して継続的に整備しています。

---

## Features

- **Market data monitoring**
  - MEXC の BTC/USDT データ取得
  - Binance Futures の市場構造補助データ取得

- **Technical analysis**
  - EMA / RSI / ATR / Volume
  - 複数時間足の構造判定
  - Support / Resistance
  - Liquidity / Liquidation cluster
  - Funding Rate
  - OI / CVD 系の補助分析

- **Risk and setup support**
  - Long / Short の方向性スコア
  - Confidence score
  - Signal tier
  - Position risk
  - RR / exit plan / position sizing の補助情報

- **AI-assisted workflow**
  - OpenAI API による要約・助言文生成
  - CLI 経由の AI 実行に切り替え可能
  - JSON 入出力を前提にした拡張可能な設計

- **Operations**
  - メール通知
  - heartbeat 出力
  - last result 保存
  - signal snapshot 保存
  - logs / tmp / status の運用整理

---

## Repository structure

```text
.
├── main.py                 # 監視システムのエントリーポイント
├── config.py               # 設定読み込み
├── requirements.txt        # Python dependencies
├── .env.example            # 環境変数テンプレート
├── src/
│   ├── ai/                 # AI要約・助言
│   ├── analysis/           # 市場構造・流動性・スコアリング分析
│   ├── data/               # 取引所データ取得・検証
│   ├── indicators/         # テクニカル指標
│   ├── notification/       # メール通知
│   ├── storage/            # JSON / CSV / snapshot 保存
│   └── trade/              # リスク・ポジション補助
└── 運用資料/                # 運用メモ・進捗記録
```

---

## Requirements

- Python 3.12 recommended
- OpenAI API key, if AI summary/advice is enabled
- SMTP account, if email notification is enabled
- Internet access to the configured exchange public APIs

Dependencies are listed in `requirements.txt`.

```text
numpy
pandas
requests
schedule
openai
websocket-client
```

---

## Setup

```bash
git clone https://github.com/afrogdesign/BTC_FX_CODEX.git
cd BTC_FX_CODEX

python3.12 -m venv .venv312
.venv312/bin/python -m pip install --upgrade pip
.venv312/bin/python -m pip install -r requirements.txt

cp .env.example .env
```

Then edit `.env`.

```bash
OPENAI_API_KEY=
SMTP_USER=
SMTP_PASSWORD=
MAIL_FROM=
MAIL_TO=
```

> [!CAUTION]
> `.env` には API key や SMTP password などの機密情報を入れます。絶対に Git にコミットしないでください。

---

## Basic usage

```bash
.venv312/bin/python main.py
```

`REPORT_TIMES` に指定された時刻に、相場データを取得し、分析・要約・通知を実行します。

例:

```env
REPORT_TIMES=00:05,01:05,02:05,03:05,04:05,05:05,06:05,07:05,08:05,09:05,10:05,11:05,12:05,13:05,14:05,15:05,16:05,17:05,18:05,19:05,20:05,21:05,22:05,23:05
```

---

## AI provider settings

AI の助言と要約は、それぞれ `api` または `cli` に切り替えられます。

```env
AI_ADVICE_PROVIDER=api
AI_SUMMARY_PROVIDER=api
AI_ADVICE_CLI_COMMAND=
AI_SUMMARY_CLI_COMMAND=
```

- `api`: OpenAI API を使います
- `cli`: 指定した CLI コマンドへ JSON を渡し、標準出力を受け取ります

CLI モードを使う場合の例:

```env
AI_ADVICE_PROVIDER=cli
AI_SUMMARY_PROVIDER=cli
AI_ADVICE_CLI_COMMAND=/path/to/codex_cli_wrapper.py
AI_SUMMARY_CLI_COMMAND=/path/to/codex_cli_wrapper.py
```

この設計により、OpenAI API、Codex CLI、ローカル検証用スクリプトなどを用途に応じて差し替えられます。

---

## Important environment variables

| Variable | Purpose |
|---|---|
| `MEXC_BASE_URL` | MEXC public API endpoint |
| `MEXC_SYMBOL` | MEXC symbol, for example `BTC_USDT` |
| `BINANCE_BASE_URL` | Binance Futures public API endpoint |
| `BINANCE_SYMBOL` | Binance symbol, for example `BTCUSDT` |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_SUMMARY_MODEL` | Model for summary generation |
| `OPENAI_ADVICE_MODEL` | Model for advice generation |
| `SMTP_HOST` / `SMTP_PORT` | SMTP server settings |
| `MAIL_FROM` / `MAIL_TO` | Notification mail settings |
| `REPORT_TIMES` | Scheduled execution times |
| `DRYRUN_MODE` | Dry-run mode flag |
| `HEARTBEAT_FILE` | Health check heartbeat path |

Funding Rate thresholds are expressed in percent.

```env
# 0.05 means 0.05%, not raw value 0.0005
FUNDING_LONG_WARNING=0.05
FUNDING_LONG_PROHIBITED=0.08
FUNDING_SHORT_WARNING=-0.03
FUNDING_SHORT_PROHIBITED=-0.05
```

---

## Security notes

This project may interact with API keys, SMTP credentials, logs, and external market-data APIs. Security review is important even though the project does not aim to execute trades automatically.

Recommended checks:

- Keep `.env` and runtime logs out of Git
- Review logs before sharing issue reports
- Avoid exposing API keys, mail credentials, account identifiers, or private URLs
- Keep dependencies updated
- Use least-privilege credentials where possible
- Run in dry-run or local verification mode before production operation

---

## Logs and runtime files

Runtime files should not be treated as source code.

Typical runtime outputs include:

- `logs/`
- `tmp/status/`
- `tmp/snapshots/`
- `tmp/errors/`
- `last_result.json`
- `heartbeat.txt`

The repository should remain the source of truth for code and documentation, while operational logs should be handled separately.

---

## Maintenance policy

This repository is maintained as a practical OSS experiment for AI-assisted financial-data monitoring.

Current maintenance priorities:

1. Improve README and operational documentation
2. Add safer test cases for data parsing and scoring logic
3. Improve error handling around external APIs
4. Review security risks around keys, logs, dependencies, and notifications
5. Make Codex-assisted maintenance reproducible

---

## Roadmap

- [ ] Add automated tests for core analysis modules
- [ ] Add sample anonymized output
- [ ] Add GitHub Actions for lint/test checks
- [ ] Add security checklist for releases
- [ ] Improve English documentation for international users
- [ ] Document Codex-based maintenance workflow

---

## Contributing

Issues and pull requests are welcome.

For changes related to market analysis logic, please include:

- What changed
- Why it changed
- How it was tested
- Whether it affects notifications, scoring, or output format

For security-related issues, avoid posting secrets or private operational logs in public issues.

---

## License

No license file is currently included.

If you intend to reuse this project, please check the repository owner’s latest license decision before redistribution or commercial use.

---

## Disclaimer

This software is provided for learning, research, and operational assistance only. It is not financial advice. The maintainer is not responsible for trading losses, operational errors, missed notifications, API outages, or decisions made based on the output of this system.
