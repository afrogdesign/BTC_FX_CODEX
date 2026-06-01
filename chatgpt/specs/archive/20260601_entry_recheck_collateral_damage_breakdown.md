# entry recheck collateral damage breakdown 仕様

## 作業番号

BTCFX-20260601-14

## 目的

`entry_recheck_none` の collateral_damage_risk を追加分解し、high_wait / low_execution を今後 hard blocker 化してよいか判断できる材料を作る。

## 対象ブランチ

`ver02.6-v2`

## 今回の扱い

- 今回は仕様作成のみ。
- 実装は次回。
- `gate / score / opportunity_gate` は変更しない。
- Phase 1B 昇格判断には使わない。
- `price_distance_missing` は blocking reason にしない。
- `trend_flip_confirmed_up` は強評価へ戻さない。

## 次回実装対象

- `tools/log_feedback.py`
- `tests/test_log_feedback.py`
- `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260601.md`
- `運用資料/reports/report_hub_latest.md`
- `運用資料/NEXT_TASK.md`

## 実装内容

`paper_entry_sl_wait_redesign` report に次の新セクションを追加する。

```md
## entry recheck collateral damage breakdown
```

対象は `market_map_opportunity` のうち、counterfactual 上の `entry_recheck_none` group。

目的は、`entry_recheck_none` に残っている `missed_opportunity` / `tp2_hit` / `sl_hit` の内訳を分解し、抑制強化で巻き込むべきでない group を見つけること。

## 集計軸

以下の単位で group table を出す。

- side
- wait band
- execution band
- primary_setup_reason
- market_map_flags
- side + wait band
- side + execution band
- setup reason + execution band

## band 定義

wait:

- `wait<40`
- `40<=wait<60`
- `60<=wait<80`
- `wait>=80`

execution:

- `execution<20`
- `20<=execution<35`
- `35<=execution<50`
- `execution>=50`

## 指標

各 group に以下を出す。

- `group`
- `count`
- `entered_count`
- `sl_hit`
- `sl_hit_rate`
- `tp2_hit`
- `tp2_hit_rate`
- `missed_opportunity`
- `missed_rate`
- `timeout`
- `avg_R`
- `judgement`

## judgement

- `insufficient_n`
- `collateral_damage_risk`
- `suppress_candidate`
- `monitor_only`

## judgement 目安

- `count < 5` は `insufficient_n`
- `tp2_hit_rate >= 15%` または `missed_rate >= 30%` は `collateral_damage_risk`
- `sl_hit_rate >= 70%` かつ `tp2_hit_rate < 10%` かつ `missed_rate < 20%` は `suppress_candidate`
- その他は `monitor_only`

## 検証

次回実装時は最低限これを実行する。

```bash
./.venv312/bin/python -m unittest tests.test_log_feedback
./.venv312/bin/python tools/log_feedback.py --paper-entry-sl-wait-redesign
./.venv312/bin/python tools/log_feedback.py --report-hub
git diff --check
```

## 禁止

- `trade_execution_gate` を緩和しない。
- `phase1b_lite_gate` を変更しない。
- `opportunity_gate` を変更しない。
- `trend_flip_confirmed_up` を強評価へ戻さない。
- Phase 1B 正式昇格をしない。
- 実弾発注をしない。
- 取引所 API 送信をしない。
- 秘密情報を変更しない。

## 完了条件

- 次回 Codex が迷わず report builder 実装に入れる。
- 変更対象、集計軸、指標、judgement、検証方法が明確。
