# PRODUCT_IMPLEMENTATION_ROUTE

last_updated: 2026-07-02
repo: `afrogdesign/BTC_FX_CODEX`
primary_mcp_working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
status: active product route for future AI / ChatGPT / Codex work

## Purpose

このファイルは、今後 AI が迷わず btc_monitor の実装を進めるための導線です。

Ver04-v1 は major product-direction branch です。Ver03-v4 は prior baseline / history として扱います。

現時点の最優先目的は、自動売買ではありません。

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

## Source-of-truth documents

今後の product / evaluation / implementation 判断は、次の順で読む。

1. `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
   - Ver04-v1 の上位計画。
   - Ver03-v4 を prior baseline として引き継ぎつつ、Ver04-v1 の active direction を定義する。

2. `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
   - 今回の最終設計正本。
   - daily proxy / weekly review / biweekly actual trade import の自己改善ループを定義する。

3. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
   - 「15分足で人間が勝てる」の定義正本。
   - entry だけでなく watch / skip / exit / take-profit / avoided_loss / missed_opportunity / over_suppression / turning_point を評価対象にする。

4. `docs/operations/ai-orchestration/MILESTONES.md`
   - durable accepted history。
   - 今回の product direction milestone もここへ集約する。

5. `docs/operations/ai-orchestration/NEXT_ACTION.md`
   - 次に Codex / future AI が実行すべき narrow task。

## Current product doctrine

### What the system is

- 人間の manual trading support system。
- notification mail は triage / entry point。
- public HTML report は current main manual-trading UI。
- local dashboard / app surface は confirmation / future automation foundation。
- 3 surface は single-source doctrine を守る。

### What the system is not yet

- 自動売買システムではない。
- `FORMAL_GO` ではない。
- automatic order はしない。
- private/account/order endpoint は触らない。
- API key / secret は読まない、表示しない。

## Product direction

守りすぎる通知から、攻めるためのレーダーへ変更する。

ただし、long / short の両方を常に検出する。
現在の regime に合わせて優先方向だけ変える。

entry は人間が15分足で判断する。
turning point risk が高いときだけ強制ブレーキをかける。

## Self-improvement loop

今後の評価/改善は3層で進める。

```text
Layer 1: Daily Proxy Loop
  毎日自動で回る。
  実取引Excelなしで、通知・方向・攻め候補・守りすぎ・転換警戒を評価する。

Layer 2: Weekly Review Loop
  週次で傾向を見る。
  short / long の偏り、regime変化、守りすぎ、転換見落としを確認する。

Layer 3: Biweekly Ground Truth Loop
  2週間に1回の実取引Excelインポート。
  実際の人間の損益を ground truth として、daily proxy のズレを補正する。
```

## Implementation route

### Phase V1-1: Post-eval asset health audit

First Ver04-v1 implementation task.

Goal:

- 既存の事後評価資産を棚卸しする。
- deterministic daily proxy evaluator に使えるデータを確定する。
- AI post review / runtime logs / old path / stopped_after_failures の状態を安全に確認する。

Allowed:

- read-only repo/local audit
- docs-only report
- narrow CSV schema inspection
- runtime log summary if explicitly scoped

Not allowed:

- API call
- secret read/print
- runtime restart
- launchctl modification
- notification sending
- trading logic change
- exchange fetch
- private/account/order endpoint

### Phase V1-2: Daily proxy evaluator

Implemented.

- `tools/log_feedback.py` now provides `build-daily-proxy-evaluator-report`
- output path is `運用資料/reports/post_eval/daily_proxy_evaluator_YYYYMMDD.md`
- report-only safety boundary is preserved

### Phase V1-3: Manual actual trade import schema

Next active implementation phase.

- local MEXC xlsx import schema
- raw exports stay local only
- normalize into generated CSVs for later linking / ground truth

### Phase V1-4: Actual trade to signal linking

Goal:

- actual trade と notification/signal を heuristic で紐づける。
- confidence: high / medium / low / manual_confirmed / ambiguous。

### Phase V1-5: Biweekly ground truth report

Goal:

- 実取引ベースの損益、manual short/long 成績、proxy-vs-actual calibration を出す。

### Phase V1-6: Recommendation engine

Goal:

- evidence から改善候補を ranking する。
- subject / label / NO_TRADE split / turning brake / long-short regime weighting の改善候補を出す。

### Phase V1-7: Surface integration

Goal:

- post-eval status を public HTML / mail / dashboard に report-only で表示する。
- single-source doctrine を維持する。

## Default next task

Unless the user says otherwise, the next implementation task is:

```text
BTCFX-20260702-POST-EVAL-ASSET-HEALTH-AUDIT
```

This should be a read-only / docs-only audit before any evaluator implementation.

## Boundary reminders

- Do not use old runtime repo for normal work.
- Do not commit raw exchange exports.
- Do not mix actual manual trades into `paper_positions.csv`.
- Do not treat `ACTIVE_*` labels as `FORMAL_GO`.
- Do not let AI post review failure block deterministic evaluation.
- Keep product docs concise and route through this file, not scattered intermediate drafts.
