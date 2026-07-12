# PRODUCT_IMPLEMENTATION_ROUTE

last_updated: 2026-07-10
repo: `afrogdesign/BTC_FX_CODEX`
primary_mcp_working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
status: active product route for future AI / ChatGPT / Codex work

## Purpose

このファイルは、今後のAIがbtc_monitorのproduct作業を迷わず進めるための上位導線である。

現時点の最優先目的は自動売買ではない。

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

## Product source of truth

product / evaluation / practicality / implementation判断は次の順で読む。

1. `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
   - future AIがphaseを飛ばさず実行するための制御文書。

2. `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
   - 本採用候補の少なさ、operator action、scenario lifecycle、ground truthを統合した詳細改善計画。

3. `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
   - daily proxy / weekly review / biweekly actual trade importの自己改善設計。

4. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
   - entryだけでなくwatch / skip / exit / take-profitを含む評価定義。

5. `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
   - 高位product direction。

6. `docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md`
   - Phase4 observation / cue / approval gate。

7. `docs/operations/ai-orchestration/MILESTONES.md`
   - accepted history。

8. `docs/operations/ai-orchestration/NEXT_ACTION.md`
   - immediate next task。

## Current product doctrine

### What the system is

- 人間のmanual trading support system。
- notification mailはtriage / chart-check trigger。
- public HTML reportはmain operator UI。
- local dashboardはconfirmation / future automation foundation。
- mail / HTML / dashboardはsingle-source doctrineを守る。
- human decides manually。

### What the system is not yet

- automatic trading systemではない。
- `FORMAL_GO`ではない。
- `ACTIVE_*`は注文許可ではない。
- private/account/order endpointを使わない。
- API key / secretを扱わない。

## Current practicality decision

現在の問題は、候補生成能力そのものより、候補からoperator actionへ変換する層にある。

既存の厳格判定は残す。

```text
A_FORMAL
  現行の厳格な最高品質候補。

B_CHECK_15M
  人間が15分足でtriggerを確認する条件付き候補。

C_WATCH_ZONE
  価格帯・scenarioを監視する候補。

STOP_OR_EXIT
  新規停止・利確・撤退を優先する局面。
```

重要:

- A/B/C/STOPは既存gateの置換ではない。
- `trade_execution_gate`は緩和しない。
- `phase1b_lite_gate`を勝手に変更しない。
- `opportunity_gate`を勝手に緩和しない。
- `trend_flip_confirmed_up`単独を強評価へ戻さない。
- planning routeの追加はproduction tuning承認ではない。

## Scenario doctrine

candidate row数と独立した機会数を混同しない。

将来は次のlifecycleへ統合する。

```text
detected
→ approaching_zone
→ zone_touched
→ trigger_wait
→ confirmed
→ entered / skipped / watched
→ tp1 / tp2 / manual_exit / invalidated / expired
```

`signal_id`と`scenario_id`を分ける。

同一scenarioの小幅更新は新しい機会として数えず、重要なstate transitionだけを通知候補にする。

## Self-improvement layers

```text
Layer 1: Daily Proxy Loop
  actual tradeなしでも方向、候補、over-suppression、turning riskを評価する。

Layer 2: Weekly Review Loop
  long/short、regime、通知過多、守りすぎの傾向を見る。

Layer 3: Biweekly Ground Truth Loop
  actual trade exportを取り込み、proxyを実損益で補正する。
```

actual trade ground truthが入るまで、proxyを実績として断定しない。

## Active implementation route

### P0: Plan and AI routing

Status: planning route created.

Outputs:

- `MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
- `MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
- startup / control / next-action routing

### P1: Manual actual trade import active spec

Current next task:

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC
```

Goal:

- 既存の `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER` を新しいpracticality routeへ接続するactive specを作る。
- source実装前にschema、安全境界、test、idempotency、privacyを確定する。

P1では実装しない。

### P2: Actual trade importer implementation

Implementation candidate:

```text
BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER
```

Rules:

- local xlsx only
- raw exports remain local
- no API
- normalized generated CSV
- no `paper_positions.csv` mixing

### P3: Actual trade to signal/scenario linking

- timestamp
- side
- price context
- competing signals
- manual confirmation
- confidence

### P4: Coverage and scenario normalization

- no_ohlcv root cause
- resolved coverage
- scenario identity
- duplicate compression
- lifecycle outcome

### P5: Offline A/B/C/STOP classifier

- report-only
- existing gates unchanged
- side-aware
- regime-aware
- thresholds are comparison parameters only

### P6: Historical replay

Compare:

- current strict baseline
- A only
- A+B
- A+B+C observation
- long/short
- regime
- notification frequency
- TP1-first / SL-first
- MFE / MAE
- over-suppression / missed opportunity

### P7: Shadow surface

- local report or render-only HTML
- no live sending change
- no runtime change without explicit task

### P8: Human manual trial

- A: high-quality candidate
- B: enter only after human 15m confirmation
- C: watch only
- STOP: no new entry / take-profit / exit

### P9: Evidence-backed tuning review

Requires:

- actual ground truth
- stable linking
- scenario normalization
- adequate sample
- explicit human approval

P9 first produces a proposal. It does not automatically change production behavior.

## Active spec rule

- `chatgpt/specs/active/`が空ならsource実装へ進まない。
- next phaseのactive specを1本だけ作る。
- active specがある場合は、それを実装正本とする。
- plan / current stateとの矛盾時はspec修正taskにする。
- completed specはarchiveへ移す。

## Success model

The product is successful when:

1. strict A candidate quality is retained.
2. B candidates add useful human-review opportunities.
3. C candidates preserve early opportunities without notification noise.
4. STOP improves exits and loss avoidance.
5. candidate rows are compressed into independent scenarios.
6. actual trades calibrate proxy evaluation.
7. A/B, long/short, and regime performance are measured separately.
8. over-suppression and turning misses are visible.
9. production tuning is evidence-backed, human-approved, and reversible.

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no API keys or secrets
- no raw exchange export commit
- no runtime restart during normal product work
- no notification behavior change without explicit approval
- no threshold auto-mutation
- human decides manually
