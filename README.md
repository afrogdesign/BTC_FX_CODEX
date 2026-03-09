# BTC Monitor

BTC監視システムです。MEXCの価格データを取得し、機械判定（bias/confidence）を行い、必要に応じてメール通知します。

## 主な機能
- MEXC API から `4h / 1h / 15m` データ取得
- テクニカル判定（トレンド・構造・RR・confidence）
- OpenAI を使った要約文生成（失敗時は機械判定のみで継続）
- 通知（SMTPメール）
- ログ保存（`logs/last_result.json`, `logs/signals/`, `logs/csv/trades.csv` など）

## ディレクトリ構成（主要）
- `main.py`: 実行エントリポイント
- `config.py`: `.env` 読み込みと設定
- `src/`: 判定ロジック・通知・保存
- `prompts/`: AIプロンプト
- `backtest/`: バックテスト関連
- `logs/`: 実行ログ（git管理外）

## 前提
- Python 3.9 以上（3.11 以上推奨）

## セットアップ
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
python3.12 -m venv .venv312
.venv312/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` に本番値を設定してください（APIキー・SMTP情報など）。

## 単発実行チェック
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
.venv312/bin/python -c "from pathlib import Path; from config import load_config; from main import run_cycle; cfg=load_config(Path('.')); r=run_cycle(cfg, Path('.')); print(r['bias'], r['confidence'])"
```

## 常駐実行
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
.venv312/bin/python main.py
```

## 本番常駐登録（macOS）
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/start_monitor.sh
```

- `launchd` に `com.afrog.btc-monitor` として登録します。
- 実行系は `.venv312/bin/python`（Python 3.12）を使います。
- 標準出力は `logs/runtime/monitor.out`、エラー出力は `logs/runtime/monitor.err` に出ます。
- 初回の定時実行は `REPORT_TIMES` の次回時刻です。

## 運用時の確認ポイント
- `logs/heartbeat.txt` が更新される
- `logs/last_result.json` が更新される
- `logs/errors/` に新しい例外が増えていない

## ログ検証・年次集計
- 運用ガイド: `ログ検証と改善運用ガイド.md`
- 全期間レポート作成:
```bash
python3 tools/log_analytics.py --output-md reports/log_review_all.md
```
- 年次レポート作成（例: 2026年）:
```bash
python3 tools/log_analytics.py --year 2026 --output-md reports/log_review_2026.md
```

## 注意
- `.env` は機密情報を含むため、絶対にコミットしないでください。
- 初回は `DRYRUN_MODE=true` で動作確認し、その後 `false` に切り替えるのがおすすめです。
