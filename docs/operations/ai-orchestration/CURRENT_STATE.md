# CURRENT_STATE

last_updated: 2026-07-05

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

## Current operational posture

- Ver04-v2 runtime deployment is complete and reflected active.
- Immediate posture is post-deployment observation / review only.
- Notification sending behavior remains unchanged.
- No immediate implementation is required unless observation finds an issue.
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
- Ver04-v2 VALUE-DEFENSE-ENTRY-LAYER is runtime-applied and running on runtime_head `1099a1ae8169f9b1d39d501e46597349a7c13475`.
- active process path is `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/main.py` and the deployed process after restart was pid `73939` started `2026-07-05 11:40:20 JST`.
- GitHub DNS / SSH reachability issue was operationally mitigated by local MCP source fallback; OS/network config was not changed.
- Phase4 scoring / gate tuning is blocked until observation evidence exists and the human explicitly approves.
- operator-facing version/mode labels are retired; public subject/title/path no longer needs VerXX or API/CLI updates and runtime verification should rely on commit hash, process path, generated_at, and report_fingerprint.
- safety boundary remains report-only / not FORMAL_GO / no automatic order / human decides manually.

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
