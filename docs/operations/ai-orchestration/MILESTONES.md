# MILESTONES

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

## Current safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- human decides manually
