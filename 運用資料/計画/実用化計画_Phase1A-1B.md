# 実用化計画 Phase1A-1B

更新日: 2026-04-22 02:40 JST

## 目的

BTC Monitor を「待つだけの監視」から、実用的な判断改善ツールへ進めるための計画です。

1.5か月以上 `trade_execution_gate=pass` が出ていないため、従来の Phase 1 を「本当に実行できる候補」だけに限定し続けると検証が進みません。
一方で、`phase1_observation_gate=pass` は 16 件出ており、特に `direction_rr_learning` は学習価値があります。

そのため Phase 1 を次の 2 段階に分けます。

- `Phase 1A`: 観測紙トレード。実行候補ではなく、方向・待機条件・仮想SL/TPを検証する段階。
- `Phase 1B`: 厳格紙トレード。従来どおり `phase1_active=true` かつ `trade_execution_gate=pass` を必要とする段階。

## 現状判断

- `phase1_observation_gate=pass`: 16 件
- `direction_rr_learning`: 10 件、近似PF 2.29、TP1先行 90.0%
- `setup_watch_learning`: 6 件、近似PF 0.54、TP1先行 66.7%
- `trade_execution_gate=pass`: 0 件
- `paper_orders planned`: 0 件

この状態は「相場が悪いから何もできない」ではなく、「実行候補はまだないが、観測候補は十分にある」と扱います。

## 運用ルール

### Phase 1A

Phase 1A は即日開始します。

対象は `phase1_observation_gate=pass` の行です。
`observation_paper_orders.csv` に保存し、実注文や実行候補とは明確に分けます。

主な用途:

- 方向判断が実際に伸びたか
- entry zone に到達したか
- 到達前に伸びたか
- 仮想 TP1 / TP2 / SL が妥当か
- `sweep_incomplete` 中の再発火条件が妥当か

除外対象:

- `confidence_below_min`
- `NO_TRADE_CANDIDATE`
- Funding 禁止
- ATR 極端値
- データ品質不良

### Phase 1B

Phase 1B は従来どおり厳格に維持します。

対象は `phase1_active=true` かつ `trade_execution_gate=pass` の行です。
保存先は `paper_orders.csv` です。

Phase 1A の成績が良くても、自動的に Phase 1B 条件を緩めません。
条件緩和は、観測タイプ別に最低 30 件を見てから判断します。

## 昇格判断

Phase 1A から Phase 1B の条件見直しへ進む目安:

- 観測タイプ別に 30 件以上
- 近似PF 1.2 以上
- TP1先行率 60% 以上
- 平均MFE が平均MAEを上回る

現時点では `direction_rr_learning` を優先分析対象にします。
`setup_watch_learning` は成績が弱いため、まず entry zone 未到達率と待機条件の改善対象として扱います。

## 実装方針

- `observation_paper_orders.csv` を Phase 1A 専用ログとして追加する。
- `main.py` は `phase1_observation_gate=pass` のときだけ Phase 1A ログへ保存する。
- `tools/log_feedback.py` は既存 `shadow_log.csv` から Phase 1A ログを backfill できるようにする。旧 `trades.csv` に観測 gate 列がない場合でも、shadow 側の補完済み判定を使う。
- `daily-sync` は `Phase 1A 観測紙トレード` と `紙トレード準備` を別セクションで表示する。
- `paper_orders.csv` は Phase 1B 専用のまま維持する。

## 次に見る数字

- `observation_paper_orders observing`
- `direction_rr_learning` の近似PF、TP1先行率、平均MFE / MAE
- `setup_watch_learning` の entry zone 未到達率
- `gate pass だが観測紙トレード未記録`
- `trade_execution_gate=pass`
- `paper_orders planned`

## 完了条件

- `observation_paper_orders.csv` が生成される
- daily-sync に Phase 1A セクションが出る
- 既存ログが Phase 1A として backfill される
- 次回以降の常駐サイクルで Phase 1A ログが自然に増える
- Phase 1B 用の `paper_orders.csv` とは混ざらない
