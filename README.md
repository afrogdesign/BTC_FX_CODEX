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

## 本番運用の考え方

- Git は「コードの正本」に使います。
  - 正本: いちばん信頼して管理する元データ
- `logs/` や実行中に増える CSV / JSON は Git へ入れません。
- 本番 MBP2020 への反映は、`git ls-files` を元にした `rsync` 配備へ寄せます。
- 本番ログの確認は、必要なものだけを別同期します。

### コードを本番へ反映する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/deploy_ver02_prod.sh
```

### 本番ログをローカルへ取得する

```bash
cd /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor
zsh tools/pull_ver02_prod_logs.sh
```

補足:

- これで「コード反映」と「実データ確認」を分けて扱えます。
- `.env`、仮想環境、`logs/` は本番側のまま残るため、実運用データを消しにくい構成です。
