# Report Hub

- generated_at: 2026-06-01 23:03 JST
- purpose: ChatGPT が最初にここを開き、必要な raw report へ進むための案内板。

## ChatGPT が最初に開く順
1. `運用資料/NEXT_TASK.md`
2. [運用資料/reports/report_hub_latest.md](運用資料/reports/report_hub_latest.md)
3. 最新 `feedback_daily_sync`
4. 最新 `market_map_effectiveness`
5. 最新 `operational_focus`
6. 最新 `paper_opportunity_diagnostics`
7. テーマがあるときだけ追加の design report

## 現役レポート

### daily-sync 日次
- latest: [運用資料/reports/feedback_daily_sync_20260601.md](運用資料/reports/feedback_daily_sync_20260601.md)
- previous: [運用資料/reports/feedback_daily_sync_20260531.md](運用資料/reports/feedback_daily_sync_20260531.md)
- storage: `active`
- purpose: 日次の全体成績、AI事後評価、Phase1 状況の入口。
- last_date: `2026-06-01` / freshness: `fresh(0d)`

### market_map 有効性
- latest: [運用資料/reports/analysis/market_map_effectiveness_20260526.md](運用資料/reports/analysis/market_map_effectiveness_20260526.md)
- previous: [運用資料/reports/archive/analysis/market_map_effectiveness_20260525.md](運用資料/reports/archive/analysis/market_map_effectiveness_20260525.md)
- storage: `active`
- purpose: market_map flag 別の有効性確認。
- last_date: `2026-05-26` / freshness: `fresh(6d)`

### 運用フォーカス
- latest: [運用資料/reports/analysis/operational_focus_20260526.md](運用資料/reports/analysis/operational_focus_20260526.md)
- previous: [運用資料/reports/archive/analysis/operational_focus_20260525.md](運用資料/reports/archive/analysis/operational_focus_20260525.md)
- storage: `active`
- purpose: blocked 理由、AI backlog、Phase1 観測の詰まりどころを見る。
- last_date: `2026-05-26` / freshness: `fresh(6d)`

### 紙候補診断
- latest: [運用資料/reports/analysis/paper_opportunity_diagnostics_20260601.md](運用資料/reports/analysis/paper_opportunity_diagnostics_20260601.md)
- previous: [運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md](運用資料/reports/analysis/paper_opportunity_diagnostics_20260526.md)
- storage: `active`
- purpose: 紙候補の entry / wait / flag 別診断。
- last_date: `2026-06-01` / freshness: `fresh(0d)`

## 設計テーマ用 / on-demand

### 緩和候補
- latest: [運用資料/reports/analysis/relaxation_candidates_20260526.md](運用資料/reports/analysis/relaxation_candidates_20260526.md)
- previous: [運用資料/reports/archive/analysis/relaxation_candidates_20260525.md](運用資料/reports/archive/analysis/relaxation_candidates_20260525.md)
- storage: `active`
- purpose: gate 緩和候補の抽出。設計判断用。
- last_date: `2026-05-26` / freshness: `fresh(6d)`

### Phase 1B 昇格候補
- latest: [運用資料/reports/analysis/phase1b_promotion_candidates_20260526.md](運用資料/reports/analysis/phase1b_promotion_candidates_20260526.md)
- previous: [運用資料/reports/archive/analysis/phase1b_promotion_candidates_20260525.md](運用資料/reports/archive/analysis/phase1b_promotion_candidates_20260525.md)
- storage: `active`
- purpose: Phase 1B-lite からの昇格候補確認。
- last_date: `2026-05-26` / freshness: `fresh(6d)`

### SL/entry 再設計診断
- latest: [運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260601.md](運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260601.md)
- previous: [運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md](運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md)
- storage: `active`
- purpose: sl_hit 偏重、高 wait、低 execution の切り分け。
- last_date: `2026-06-01` / freshness: `fresh(0d)`

### quality guard 有効性
- latest: [運用資料/reports/analysis/quality_guard_effectiveness_20260601.md](運用資料/reports/analysis/quality_guard_effectiveness_20260601.md)
- previous: `missing`
- storage: `active`
- purpose: paper opportunity quality guard の初回反映評価と counterfactual 論点整理。
- last_date: `2026-06-01` / freshness: `fresh(0d)`

### soft risk collateral damage
- latest: [運用資料/reports/analysis/soft_risk_collateral_damage_20260601.md](運用資料/reports/analysis/soft_risk_collateral_damage_20260601.md)
- previous: `missing`
- storage: `active`
- purpose: B/C 単独 soft risk の hard blocker 化による巻き込み被害を評価する。
- last_date: `2026-06-01` / freshness: `fresh(0d)`

## Dormant / 補助診断

### market_map readiness
- latest: [運用資料/reports/analysis/market_map_readiness_20260514.md](運用資料/reports/analysis/market_map_readiness_20260514.md)
- previous: [運用資料/reports/archive/analysis/market_map_readiness_20260513.md](運用資料/reports/archive/analysis/market_map_readiness_20260513.md)
- storage: `active`
- purpose: market_map 記録の値入り確認。market_map ロジック刷新時だけ再生成する補助診断。
- last_date: `2026-05-14` / freshness: `stale(18d)`

## Archived / 現行運用外

### weekly 集計
- latest: [運用資料/reports/archive/weekly/feedback_weekly_20260330.md](運用資料/reports/archive/weekly/feedback_weekly_20260330.md)
- previous: `missing`
- storage: `archive`
- purpose: 週次の長め集計。現行運用では常用せず、必要時だけ履歴参照する。
- last_date: `2026-03-30` / freshness: `stale(63d)`

## Evergreen 比較

### 標準比較 notified_rr_to_entry
- latest: [運用資料/reports/analysis/notified_rr_to_entry.md](運用資料/reports/analysis/notified_rr_to_entry.md)
- previous: `missing`
- storage: `active`
- purpose: 標準比較の evergreen レポート。
- last_date: `n/a` / freshness: `evergreen`

### 標準比較 ask-heavy
- latest: [運用資料/reports/analysis/notified_rr_to_entry_orderbook_ask_heavy.md](運用資料/reports/analysis/notified_rr_to_entry_orderbook_ask_heavy.md)
- previous: `missing`
- storage: `active`
- purpose: 標準比較の evergreen レポート。
- last_date: `n/a` / freshness: `evergreen`

### 標準比較 rr_to_confidence
- latest: [運用資料/reports/analysis/rr_to_confidence.md](運用資料/reports/analysis/rr_to_confidence.md)
- previous: `missing`
- storage: `active`
- purpose: 標準比較の evergreen レポート。
- last_date: `n/a` / freshness: `evergreen`

## Legacy / 旧版説明

- legacy: [運用資料/reports/Ver02.3のレポート/README.md](運用資料/reports/Ver02.3のレポート/README.md)
- legacy: [運用資料/reports/Ver02までのレポート/README.md](運用資料/reports/Ver02までのレポート/README.md)
- purpose: 現行判断の正本ではなく、旧版の背景説明用。

## missing / stale 警告

- なし
