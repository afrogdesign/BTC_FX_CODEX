# CURRENT_STATE

last_updated: 2026-07-02

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

Current focus has moved from generic evidence / intraperiod / win-rate diagnostics to the Ver04-v1 manual-trading self-improvement loop.

Primary objective:

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading remains out of scope and later-stage only.

Ver03-v4 is prior baseline/history; Ver04-v1 is the active branch for the major product-direction shift.

## Current operational posture

- Ver04-v1 runtime deployment is complete and reflected active.
- Immediate posture is post-deployment observation.
- Notification sending behavior remains unchanged.
- No immediate implementation is required unless observation finds an issue.

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
- notification version labels are expected to display Ver04-v1 after the display-label follow-up fix.
- post-deployment observation surfaced a readability issue in the public detail page, and a bounded UI readability pass was applied to human-facing labels and chart marker spacing.
- current human-facing cleanup simplifies the mail subject, current-price label, and internal support block; the live launchd process still needs a controlled restart before it can render those current-code changes.
- controlled runtime restart after the human UI / subject / chart cleanup is complete, and the live launchd process now loads the current Ver04-v1 code path.
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
- controlled runtime restart was performed to clear a stale running process so the active launchd job can load current Ver04-v1 code.

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
- Ver04-v1 runtime deployment complete

## Default avoid list

- `.venv312/`
- `logs/` unless explicitly scoped for audit
- generated CSV / report / HTML
- raw exchange exports under `local/manual_trade_imports/`
- full `TASK_LEDGER.md`
