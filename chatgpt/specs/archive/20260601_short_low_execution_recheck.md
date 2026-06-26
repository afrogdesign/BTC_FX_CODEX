# short low execution recheck 仕様

## 作業番号

BTCFX-20260601-16

## 目的

`entry_recheck_none` の collateral damage breakdown で `short | execution<20` が `suppress_candidate` になったため、この条件だけを局所的に entry recheck 対象へ追加する。

## 対象ブランチ

`ver02.6-v2`

## 根拠

`paper_entry_sl_wait_redesign_20260601.md` の `entry recheck collateral damage breakdown` で、以下が確認された。

- `short | execution<20`: count=9 / entered_count=8 / sl_hit=7 / sl_hit_rate=87.5% / tp2_hit_rate=0.0% / missed_rate=11.1% / avg_R=-0.25 / judgement=suppress_candidate
- `short | 20<=execution<35`: collateral_damage_risk のため、execution<35 などへ広げてはいけない
- `40<=wait<60` や `short` 全体も collateral_damage_risk のため、広く hard blocker 化しない

## 実装方針

`src/trade/opportunity_gate.py` の entry recheck reason 判定に、以下の blocking reason を追加する。

```txt
entry_recheck_required_short_low_execution
```

発火条件:

```txt
opportunity_type が market_map_opportunity 相当
side == short
confidence_execution_shadow < 20
```

ただし、既存実装で opportunity_type を直接受け取っていない場合は、既存の `market_map_opportunity` 判定フロー内だけに限定して実装する。
無理に関数引数を大きく増やさない。

## 変更対象

次回実装で触ってよいファイル:

* `src/trade/opportunity_gate.py`
* `tests/test_phase1_trade_plans.py`
* `tools/log_feedback.py`
* `tests/test_log_feedback.py`
* `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260601.md`
* `運用資料/reports/report_hub_latest.md`
* `運用資料/NEXT_TASK.md`

## report 反映

`paper_entry_sl_wait_redesign` report の counterfactual impact に、新 reason を追加する。

追加 group:

```txt
entry_recheck_required_short_low_execution
```

既存 group は維持する。

## 禁止

* `trade_execution_gate` は変更しない。
* `phase1b_lite_gate` は変更しない。
* `paper_orders planned` を増やす目的の変更をしない。
* `trend_flip_confirmed_up` を強評価へ戻さない。
* `short | 20<=execution<35` は抑制しない。
* `short` 全体を抑制しない。
* `40<=wait<60` 全体を抑制しない。
* `price_distance_missing` を blocking reason にしない。
* Phase 1B 正式昇格をしない。
* 実弾発注をしない。
* 取引所 API 送信をしない。
* 秘密情報を変更しない。

## 検証

次回実装時は最低限これを実行する。

```bash
./.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback
./.venv312/bin/python tools/log_feedback.py --paper-entry-sl-wait-redesign
./.venv312/bin/python tools/log_feedback.py --report-hub
git diff --check
```

## 完了条件

* `entry_recheck_required_short_low_execution` の仕様が明確。
* 抑制対象が `short + execution<20` に限定されている。
* collateral damage risk が出た group を巻き込まない注意が明記されている。
* 次回 Codex が実装に入れる。
