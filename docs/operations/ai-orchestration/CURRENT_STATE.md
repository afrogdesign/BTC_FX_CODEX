# CURRENT_STATE

last_updated: 2026-07-07

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- no runtime restart during normal product work
- no raw exchange export commit
- no `paper_positions.csv` integration unless explicitly approved
- human decides manually

## Current product focus

Current focus has moved from generic evidence / intraperiod / win-rate diagnostics to the Ver04-v2 manual-trading observation loop.
Ver04-v1 self-review / run-fingerprint checkpoint is complete, and Ver04-v2 is the active source working branch.

Primary objective:

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading remains out of scope and later-stage only.

Ver03-v4 is prior baseline/history; Ver04-v1 is the prior active product branch.
Ver04-v2 is the current active source working branch for follow-on observation/review work.

## Current Phase4 self-improvement route

- source-of-truth route now includes `docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md`
- recent Phase4 analysis / cue design / display planning is complete
- display/report-label-only implementation is complete
- commit `d2beafe` is pushed and runtime-applied
- active process path is `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/main.py`
- no-send/render-only smoke passed
- no scoring / gate / threshold / trading logic / notification trigger changes were made
- human approval is required before any future implementation beyond display labels
- Phase4 tuning remains blocked

## Current operational posture

- Ver04-v2 runtime deployment is complete and reflected active.
- display/report-label-only implementation `d2beafe` is runtime-applied.
- First post-deploy normal notification observation passed for signal `20260705_050500`.
- Value Defense observation snapshot source now includes `attack_review_flags`.
- Existing snapshot backfill / upgrade path exists for previously published observations.
- latest local observation `20260706_030500` has been backfilled with `self_review_readiness` and `attack_review_flags`.
- Immediate posture is post-deployment observation / review only.
- Notification sending behavior remains unchanged.
- No immediate implementation is required unless observation finds an issue.
- Next strategic design focus is Big Chance / Failed Thesis Layer.
- guiding principle: failed thesis is opportunity.
- Next major design target is VALUE-DEFENSE-ENTRY-LAYER.
- Ver04-v2 VALUE-DEFENSE-ENTRY-LAYER Phase1-3 are complete and production-applied:
  - Phase1: report-only payload attached to `build_setup`
  - Phase2: detail HTML surface added
  - Phase3: judgment self-review dimensions added

## Current source-of-truth route

- `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`

## Current design status

- Ver04-v1 integrated product plan is the active high-level plan.
- Self-improvement loop final design is now the active product route.
- Manual 15m win definition is the companion definition for evaluation semantics.
- Ver03-v4 remains the prior baseline/history.
- Product docs now define daily proxy / weekly review / biweekly ground truth loops.

## Current known status

- public HTML / notification mail / local dashboard は同じ判断ソースを維持する方針。
- notification mail is triage / entry point, not an order instruction.
- public HTML report is the current main manual-trading UI.
- local dashboard / app surface is confirmation and future automation foundation.
- diagnostic and post-evaluation remain report-only support.
- major turn / turning point diagnostics do not authorize manual or automatic entry.
- No restart / launchd action is required for the completed deployment.
- operator-facing version/mode labels are retired.
- public label is `BTCFX Manual Trading Report`.
- path slug is `manual-trading`.
- first observed notification/detail HTML used `logs/notifications_html/manual-trading/attention/20260705_050500.html` and `/manual-trading/attention/20260705_050500.html`.
- public/operator label check passed with no visible VerXX / `[CLI]` / `[API]` leakage in the subject/path surface.
- future verification should use commit hash, process path, generated_at, and report_fingerprint, not VerXX labels or SYSTEM_LABEL.
- breakout / inversion zones now have a report-only momentum confirmation layer for continuation / counter-bias risk visibility.
- report-only MACD indicator/scoring support is implemented, and report-only intraperiod breakout/breakdown alert candidate generation is implemented.
- live extra intraperiod mail sending is not enabled.
- notification sending behavior remains unchanged.
- executable Codex prompts emitted by ChatGPT should start with `AUTO_SEND`; `HUMAN_CHECK` means stop before emitting an executable prompt and consult the human.
- the project is now in a required post-deployment observation gate for the intraperiod / MACD buildout.
- this gate is mandatory before any live extra 15-minute sending decision.
- observation checklist: HTML/page usability, `15分足 早期注意` timing, MACD wording usefulness, actual chart movement match, counter-bias loss reduction, safety boundary visibility.
- actual judgment time and post-judgment self-review must be connected in the next design step.
- deterministic report-only judgment self-review link is now completed.
- normal notifications / generated HTML can be reviewed against self-review evidence when generated intraperiod inputs are available.
- judgment self-review now also carries deterministic review bucket / severity / human-review-required / improvement-focus fields for later human review.
- judgment self-review now also exposes a deterministic sanitized human review queue for quick row-level follow-up.
- judgment self-review now also exposes a deterministic rollup digest for operator next-action review.
- judgment self-review now also exposes a deterministic change-readiness gate to avoid premature tuning.
- judgment self-review now supports explicit `late` classification when late evidence is present.
- judgment self-review now includes deterministic run metadata and fingerprints for later report comparison.
- controlled runtime restart completed for the current Ver04-v2 production apply.
- active process path is `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/main.py`.
- deployed process after restart was pid `46203` started `2026-07-06 15:47:09 JST`.
- Ver04-v2 VALUE-DEFENSE-ENTRY-LAYER is runtime-applied and running on runtime_head `1099a1ae8169f9b1d39d501e46597349a7c13475`.
- Value Defense UI rendered with real data and the reusable local observation snapshot tool was added as a report-only helper.
- `tools/build_value_defense_observation_snapshot.py` was added in commit `fb7a32f12deb94e699a9f57636c7c8ebc7137faa`.
- GitHub DNS / SSH reachability issue was operationally mitigated by local MCP source fallback; OS/network config was not changed.
- Phase4 scoring / gate tuning is blocked until future notified observation evidence exists and the human explicitly approves.
- display/report-label-only work is complete; tuning remains blocked.
- operator-facing version/mode labels are retired; public subject/title/path no longer needs VerXX or API/CLI updates and runtime verification should rely on commit hash, process path, generated_at, and report_fingerprint.
- safety boundary remains report-only / not FORMAL_GO / no automatic order / human decides manually.

## Followup notification lifecycle

- followup notification lifecycle is implemented, tested, checkpoint-pushed, and runtime-applied
- implementation commit is `b4f0089`
- runtime path remained the primary repo path
- current posture remains observation / review only
- compact email triage body is now used on the actual CLI runtime path as well
- the earlier compact body change was preview/API-oriented only; runtime CLI now uses the same compact body
- compact CLI email wording has been polished; safety boundary is canonical and paper-candidate heading only appears for pass/planned
- HTML reflection fix applied for Big Chance anchor and human-facing safety boundary display
- Big Chance / Failed Thesis Layer runtime apply is complete.
- implementation commit is `76e8b302078ff1d7fae9ed1abc4b581e247540b6`.
- replay artifact for `20260706_100500` has been generated for the failure-case review.
- no live Big Chance notification trigger was added.
- no scoring / gate / threshold tuning was performed.
- `invalidated` Big Chance candidates must be shown as replayed / expired, not as active top-priority opportunities.
- Phase4 remains blocked until future observation evidence and explicit human approval.

## Current operational blocker

- MCP working repo と old runtime execution repo の 2 つが存在し、混同すると unsafe。
- actual exchange export contains private account/trade info and must remain local/generated, not source-controlled.

## Current repo-operation mode

- MCP repo is source of truth.
- ChatGPT verifies via AFROG_MCP_Business.
- GitHub is not routine review path.
- Codex prompts should be compact and diff-based inside same thread.
- commit only at meaningful boundaries.
- TASK_LEDGER / handoff docs are not updated every task.

## Product backlog next candidate

- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`
- Start this after observation or when the user explicitly requests implementation.
- `BTCFX-20260702-VER04-V1-INTRAPERIOD-LIVE-SEND-DECISION` only if the user explicitly approves live extra notification sending behavior.

## Completed history

- post-eval asset health audit completed
- daily proxy evaluator implemented
- implementation readiness package created
- Ver04-v2 runtime deployment complete

## Default avoid list

- `.venv312/`
- `logs/` unless explicitly scoped for audit
- generated CSV / report / HTML
- raw exchange exports under `local/manual_trade_imports/`
- full `TASK_LEDGER.md`


## Planning route update — 2026-07-10

The user approved direct documentation and AI routing for the manual trading practicality improvement plan.

New active planning sources:

- `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
- `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`

Current planning decision:

- retain the strict formal candidate path as `A_FORMAL`
- add future report-only/manual-review layers `B_CHECK_15M`, `C_WATCH_ZONE`, and `STOP_OR_EXIT`
- do not relax existing gates
- normalize candidate rows into scenario lifecycle before changing notification volume
- connect actual trade ground truth before evidence-backed production tuning

This planning update does not change runtime behavior, scoring, gates, thresholds, notification triggers, or live mail sending.

Current exact next task:

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC
```

The next task is active-spec creation only. Importer source implementation remains blocked until the spec is reviewed and approved.


---

## 2026-07-10 importer-plan correction

Repo inspection confirmed that the actual-trade importer, manual trade linker, and ground-truth report already exist as early implementations. The active route is corrected accordingly.

Completed preparation:

- created `chatgpt/specs/active/20260710_manual_actual_trade_importer.md`
- selected `local/manual_trade_imports/YYYYMMDD/` as the canonical private input path
- added `local/manual_trade_imports/` to `.gitignore`
- defined deterministic merge/idempotency/conflict behavior
- preserved report-only / not FORMAL_GO / human-decided boundaries
- separated exchange ground truth from later human decision-event ground truth

Current exact next task:

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-HARDENING
```

Git branch, dirty tree, validation result, commit, and push remain unverified because the public MCP file interface does not expose Git metadata or execute repo commands. Those checks belong at the beginning/end of the bounded Codex implementation task.
