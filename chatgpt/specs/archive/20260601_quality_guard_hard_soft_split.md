# 目的

`ver02.6-v1` の paper opportunity quality guard を、次回実装時に `hard blocker` と `soft risk` へ分離できるように仕様案を固定する。

今回は仕様書作成だけを行い、コード実装、テスト追加、レポート再生成は行わない。

# 根拠

根拠は `運用資料/reports/analysis/quality_guard_effectiveness_20260601.md` の counterfactual reason 組み合わせ別 outcome を正本とする。

主要数値は以下。

- `A=require_execution_for_high_wait`
- `B=suppress_long_high_wait`
- `C=suppress_trend_flip_up_strong`
- `A only: 89件 / sl_hit=81件 / sl_hit_rate=91.0%`
- `B only: 18件 / sl_hit=1件 / missed_opportunity=9件 / entry_not_reached=7件`
- `C only: 6件 / sl_hit=2件 / missed_opportunity=4件`
- `A+B: 106件 / sl_hit=8件 / entry_not_reached=89件`
- `A+C: 0件`
- `B+C: 1件 / sl_hit=1件`
- `A+B+C: 5件 / sl_hit=5件`

読み方は次の通り。

- `A only` は件数を伴って `sl_hit_rate` が高く、hard blocker 維持を支持する。
- `B only` は `missed` / `entry_not_reached` の巻き込みが大きく、単独 hard blocker としては弱い。
- `C only` は件数が少なく、`missed` 巻き込みも多いため、単独 hard blocker としては弱い。
- `A+B` は `A` を含むため block 自体は維持候補だが、性質は `sl_hit` 抑制より `entry_not_reached` 圧縮に近い。
- `B+C` / `A+B+C` は `sl_hit_rate` は高いが件数が少ないため、断定しない。

# 現行 guard の定義

現行 guard は以下の 3 つで構成される。

- `require_execution_for_high_wait`
- `suppress_long_high_wait`
- `suppress_trend_flip_up_strong`

現行では、これらを紙候補化の quality guard としてまとめて block している。

前提として、次の挙動は変えない。

- `trade_execution_gate` は緩和しない
- `phase1b_lite_gate` は変更しない
- `formal_execution_candidate` は現行どおり `trade_execution_gate=pass` を優先する
- 実弾発注、取引所API送信、秘密鍵連携は対象外

# hard blocker と soft risk の分離案

次回実装時の仕様案として、以下を固定する。

## hard blocker に残す候補

- `A only`
- `A+B`
- `A+C`
- `A+B+C`

理由:

- `A only` は `89件` 中 `81件` が `sl_hit` で、`sl_hit_rate=91.0%`。件数も十分ある。
- `A` を含む group は、少なくとも `high wait + low execution` という低品質条件を含む。
- `A+B` は `entry_not_reached` が多く、性質は `sl_hit` 抑制だけではないが、候補化遅延の抑制としては維持候補。

## soft risk に落とす候補

- `B only`
- `C only`
- `B+C`

理由:

- `B only` は `18件` 中 `sl_hit=1件` で、`missed_opportunity=9件`、`entry_not_reached=7件`。単独 hard block では機会損失寄り。
- `C only` は `6件` 中 `missed_opportunity=4件` で、件数も少ない。単独 hard block には弱い。
- `B+C` は `sl_hit_rate=100%` だが `1件` のみで断定できない。

## まだ判断しないもの

- `wait>=60 / execution<24` の閾値変更
- `trend_flip_confirmed_up` の完全復権
- long 側全体の gate 緩和
- Phase 1B 正式昇格

この分解は、guard 条件を即時変更するためのものではない。次回 ChatGPT が、`閾値維持 / 閾値調整 / guard分割` を判断するための材料である。

# opportunity_reasons の設計案

次回実装時の `opportunity_reasons` は、hard blocker と soft risk を分けて記録する。

## hard blocker の reason

- `require_execution_for_high_wait`
- `require_execution_for_high_wait+suppress_long_high_wait`
- `require_execution_for_high_wait+suppress_trend_flip_up_strong`
- `require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong`

## soft risk の reason

- `soft_risk:suppress_long_high_wait`
- `soft_risk:suppress_trend_flip_up_strong`
- `soft_risk:suppress_long_high_wait+suppress_trend_flip_up_strong`

## formal candidate の扱い

- `trade_execution_gate=pass` の場合、現行どおり `formal_execution_candidate` は block しない。
- ただし `quality conflict` は reason に残す。
- `soft risk` も同様に reason に残す。

# レポート集計の設計案

次回実装時に、`daily-sync` / `paper_opportunity_diagnostics` / `quality_guard_effectiveness` で次を見られるようにする。

- `hard_quality_blocked` 件数
- `soft_quality_risk` 件数
- hard blocker reason 別件数
- soft risk reason 別件数
- hard / soft 別の `market_map before/after` 件数
- hard / soft 別の counterfactual `sl_hit / tp2_hit / missed_opportunity`

今回は builder 実装は行わない。`tools/log_feedback.py` も触らない。

# 実装対象ファイル案

次回 Codex が実装する場合の対象案は以下。

- `src/trade/opportunity_gate.py`
- `tools/log_feedback.py`
- `tests/test_phase1_trade_plans.py`
- `tests/test_log_feedback.py`
- `運用資料/NEXT_TASK.md`
- `運用資料/reports/report_hub_latest.md`

今回はこれらを変更しない。

既存の `chatgpt/specs/active/20260526_paper_opportunity_quality_guard.md` は、quality guard の初回実装仕様として役割が異なる。次回実装に進める段階で、実施済み仕様として `archive` へ移すかを別途判断する。

# 検証方法案

次回実装時の検証案は以下。

1. `hard blocker` と `soft risk` の unit test を分けて追加する
2. `trade_execution_gate=pass` の formal candidate が block されないことを確認する
3. `soft risk` が `opportunity_reasons` に残ることを確認する
4. `daily-sync` / `paper_opportunity_diagnostics` / `quality_guard_effectiveness` に hard / soft 集計が出ることを確認する
5. `git diff --check` と既存 test suite を通す

# 完了条件案

- `A only / A+B / A+C / A+B+C` が hard blocker として扱われる
- `B only / C only / B+C` が soft risk として扱われる
- `opportunity_reasons` に hard / soft の区別が残る
- `formal_execution_candidate` は現行どおり block しない
- `trade_execution_gate` を変更しない
- `phase1b_lite_gate` を変更しない
- hard / soft 別の集計がレポートに出る

# 注意事項

- 今回はコード実装しない
- guard 条件は今回変更しない
- `src/trade/opportunity_gate.py` を触らない
- `tools/log_feedback.py` を触らない
- report builder を正式化しない
- `trade_execution_gate` を緩和しない
- Phase 1B 正式昇格をしない
- `paper_orders planned` を増やすことを目的にしない
- 実弾発注、取引所API送信、秘密鍵連携に触れない
- 件数が少ない `B+C` / `A+B+C` を過剰に断定しない
