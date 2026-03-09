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
python3 -m pip install -r requirements.txt
cp .env.example .env
```

`.env` に本番値を設定してください（APIキー・SMTP情報など）。

## 単発実行チェック
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
python3 -c "from pathlib import Path; from config import load_config; from main import run_cycle; cfg=load_config(Path('.')); r=run_cycle(cfg, Path('.')); print(r['bias'], r['confidence'])"
```

## 常駐実行
```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
python3 main.py
```

## 運用時の確認ポイント
- `logs/heartbeat.txt` が更新される
- `logs/last_result.json` が更新される
- `logs/errors/` に新しい例外が増えていない

## 注意
- `.env` は機密情報を含むため、絶対にコミットしないでください。
- 初回は `DRYRUN_MODE=true` で動作確認し、その後 `false` に切り替えるのがおすすめです。
