# MILESTONES

## Ver04-v1 branch opened for major product direction shift

- branch `Ver04-v1` is the active product branch
- `Ver03-v4` remains prior baseline / history
- objective is unchanged in essence: notification mail -> 15m check -> aggressive-but-controlled manual trading support
- self-improvement loop is daily proxy / weekly review / biweekly actual trade ground truth
- automatic trading remains later-stage only
- post-eval asset health audit is completed history
- daily proxy evaluator is implemented and tested
- default next implementation task is `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`

## Daily Proxy Evaluator implemented

- deterministic report-only Daily Proxy Evaluator was implemented in this thread
- CLI entry is `build-daily-proxy-evaluator-report`
- output path is `運用資料/reports/post_eval/daily_proxy_evaluator_YYYYMMDD.md`
- safety boundary stays proxy-only / not `FORMAL_GO` / no automatic order / no private/account/order endpoints / human decides manually

## Ver04-v1 implementation readiness package

- implementation readiness package was created to hand off cleanly to the next implementation thread
- it records the current source of truth, the MEXC export path, and the normalized output design
- next implementation task pointer is `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`

## Dashboard parity and checkpoint push

- dashboard parity smoke test result is `dashboard_parity_complete`
- issues found are `none`
- local dashboard parity now includes `Safety Flags`, `Surface Roles`, and `Ready Gate Copy`
- single-source boundary is confirmed for public HTML / notification mail / local dashboard
- checkpoint push was reported successful on branch `Ver03-v4`
- upstream was reported as `origin/Ver03-v4`
- runtime pull handoff remains separate and not executed

## Ver03-v4 surface alignment

- public HTML / notification mail / local dashboard の manual action surface が Ver03-v4 で aligned
- accepted sequence includes `BTCFX-20260623-181-V4-PUBLIC-HTML-MANUAL-ACTION-CHECKLIST`, `183`, `184`, `186`
- current doctrine は 3 surface を single source の別表示として扱う

## Intraperiod review workflow

- accepted intraperiod workflow includes `BTCFX-20260623-188`, `189`, `191`, `192`, `195`, `197`, `199`, `201`, `202`
- local/report-only path includes `build-active-plan-intraperiod-outcomes`
- one-shot review CLI `build-active-plan-intraperiod-review --stdout-json` と app contract exposure が accepted
- same-bar TP1+TP2 without SL classified as `tp2_first` in accepted local/report-only tooling

## Operator status diagnostics

- runtime/operator status milestone includes `BTCFX-20260623-216`, `218`, `221`, `223`
- accepted scope includes runtime startup observability, app contract exposure, dashboard display, and stdout JSON evidence
- diagnostic remains local/report-only support

## Safe config schema audit

- safe config schema audit CLI and app surface integration are accepted
- accepted scope includes app contract exposure, ready gate validation, dashboard display, and stdout JSON evidence
- accepted safety rule: no `.env` value read, no secret exposure, no private endpoint use

## Operator triage summary

- operator triage summary is aligned across current manual-delivery app surface validation stdout JSON, public HTML, and notification mail
- alias lookup includes `app_surface_validation`, `app_surface_validation_data`, `manual_delivery_app_surface_validation`, and `current_manual_delivery_app_surface_validation`

## Integrated evidence overview

- integrated evidence overview is aligned across dashboard, app surface validation stdout JSON, public HTML report, and notification mail
- accepted evidence set includes `intraperiod_review_stdout_json`, `operator_status_diagnostic`, `safe_config_schema_audit`, `operator_triage_summary`, and `manual_action_checklist_surface`
- accepted dashboard rendering shows evidence lists and renders empty missing/not-ready/execution-required lists as `none`
- integrated_evidence_overview operator hints milestone is accepted using existing safe fields only

## Major turning point diagnostic

- major turning point opportunity milestone is accepted across public HTML, notification mail, and dashboard
- major turning point diagnostic is accepted across intraperiod outcomes markdown, app surface validation stdout JSON, dashboard, public HTML, and notification mail
- accepted classification uses `potential_missed_turn`, `potential_fakeout`, `bad_entry_timing`, and `inconclusive`
- diagnostic remains post-hoc support only and does not authorize manual or automatic entry

## Manual 15m self-improvement direction

- final product objective is now explicit: notification mail を受け取った人間が15分足を確認し、攻めの姿勢で勝てる manual trading support system を作る
- active route is `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- Ver04-v1 integrated product plan is the active high-level plan
- final self-improvement design is `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- companion definition is `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- Ver03-v4 is prior baseline / history
- accepted self-improvement structure:
  - Daily Proxy Loop: runs without actual exchange export
  - Weekly Review Loop: summarizes attack/defense/regime trends
  - Biweekly Ground Truth Loop: imports actual futures Excel exports and calibrates proxy vs actual human trade results
- actual human trade exports are local/generated inputs and must not be committed by default
- actual human trades must not be mixed into `paper_positions.csv` unless explicitly approved
- AI post review is optional qualitative enrichment, not the main evaluation layer

## Current implementation route

- post-eval asset health audit is completed history
- daily proxy evaluator is implemented and tested
- implementation readiness package is created
- next default implementation task is `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`
- next task is local MEXC xlsx importer / normalized CSV output
- no API integration
- no raw MEXC export commit
- no order execution
- no trading logic change

## Current safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- no runtime restart during normal product work
- no notification send behavior change without explicit approval
- no raw exchange export commit
- no `paper_positions.csv` integration unless explicitly approved
- human decides manually
