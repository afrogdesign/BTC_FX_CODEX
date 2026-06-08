# Ver03-v1 Active Plan runtime確認手順

## 1. 目的

Ver03-v1 で追加した `active_trade_plan`、`active_plan_candidates.csv`、`active_trade_plan_diagnostics_YYYYMMDD.md` が、実際の監視サイクル後に期待どおり動いているかを確認する。

この手順書は確認用であり、実弾発注や取引所API送信を行うものではない。

## 2. 現在地

- `BTCFX-20260608-032` で `active_trade_plan` 候補CSV `logs/csv/active_plan_candidates.csv` の記録レーンを追加済み。
- `BTCFX-20260608-033` で `active_trade_plan_diagnostics_YYYYMMDD.md` builder / CLI を追加済み。
- `BTCFX-20260608-034` で `NEXT_TASK.md` を Ver03-v1 現在地に同期済み。
- `BTCFX-20260608-036` で既知の未追跡ファイル 3 件の扱いを決定済み。
- 2026-06-08 時点の `active_trade_plan_diagnostics_20260608.md` では `active_plan_candidates.csv: missing`。
- これは、032以降の新しい監視サイクルがまだ候補CSVを生成していない状態を意味する。

## 3. 確認タイミング

以下のいずれかの後に確認する。

1. Ver03-v1 の監視サイクルが1回以上実行された後。
2. `logs/csv/trades.csv` に 032 以降の新しい行が追記された後。
3. `logs/last_result.json` が 032 以降のコードで更新された後。

## 4. 確認コマンド

repo root で実行する。

```bash
git status --short --branch
git rev-parse --short HEAD
ls -l logs/csv/active_plan_candidates.csv || true
tail -n 5 logs/csv/trades.csv || true
tail -n 5 logs/csv/active_plan_candidates.csv || true
```

## 5. 期待する状態

### 5.1 `active_plan_candidates.csv` が生成されている場合

期待:

* `logs/csv/active_plan_candidates.csv` が存在する。
* header に以下が含まれる。
  * `candidate_id`
  * `source_signal_id`
  * `active_primary_action`
  * `candidate_type`
  * `candidate_status`
  * `side`
  * `entry_mode`
* 候補がある場合、`candidate_id` は以下形式になる。
  * `<source_signal_id>:<side>:<candidate_type>`

次に実行する。

```bash
python tools/log_feedback.py --build-active-trade-plan-diagnostics --active-plan-report-date 20260608
```

その後、以下を確認する。

```bash
sed -n '1,120p' "運用資料/reports/analysis/active_trade_plan_diagnostics_20260608.md"
```

期待:

* `active_plan_candidates.csv: missing` が消えている。
* 候補タイプ別件数、side別件数、candidate_status別件数、entry_mode別件数が表示される。
* 代表候補に `candidate_id` が出る。

### 5.2 `active_plan_candidates.csv` がまだ生成されていない場合

想定される理由:

* 032以降の監視サイクルがまだ走っていない。
* 監視サイクルは走ったが、payload に `active_trade_plan` が入る前の古いコードだった。
* 監視サイクルは走ったが、候補条件に該当する side plan がなかった。
* `run_cycle` が途中で失敗し、CSV追記まで到達していない。

確認するファイル:

```bash
ls -l logs/last_result.json || true
tail -n 50 logs/runtime/monitor.err || true
tail -n 50 logs/runtime/feedback_daily_sync.err || true
```

確認観点:

* `logs/last_result.json` の更新時刻。
* `logs/runtime/monitor.err` に例外がないか。
* `trades.csv` の最新行に `active_primary_action` が入っているか。
* `trades.csv` の最新行に `active_trade_plan_json` が入っているか。

## 6. 判断基準

| 状態 | 判断 |
| --- | --- |
| `active_plan_candidates.csv` があり、候補行もある | Active Plan 候補CSVレーンは稼働確認済み |
| `active_plan_candidates.csv` はあるが header のみ | レーンは作成されたが候補条件は未発生 |
| `active_plan_candidates.csv` がなく、trades 最新行に `active_primary_action` がある | append_active_plan_candidates の接続確認が必要 |
| `active_plan_candidates.csv` がなく、trades 最新行も blank | 032以降のコードで監視サイクルが走っていない可能性 |
| runtime error がある | 先に runtime error を修正する |

## 7. 次に進む条件

次の実装へ進む条件:

* `active_plan_candidates.csv` が生成されている。
* 少なくとも1件以上の候補行がある。
* `active_trade_plan_diagnostics_YYYYMMDD.md` に候補集計が出ている。

条件を満たしたら、次は以下に進む。

1. `active_plan_candidate_outcomes` の builder / CLI 正本化。
2. daily-sync への Active Plan 診断接続。
3. `report_hub_latest.md` の Active Plan レポート参照確認。

## 8. 今回やらないこと

* 監視プロセスの起動・停止・再起動。
* 実弾発注APIの追加。
* 取引所APIキーや秘密鍵の確認。
* Active Plan 判定ロジックの変更。
* `trade_execution_gate` の変更。
* `paper_positions.csv` の仕様変更。
