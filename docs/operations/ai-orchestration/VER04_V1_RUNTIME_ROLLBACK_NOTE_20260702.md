# Ver04-v1 Runtime Rollback Note 2026-07-02

This note records the post-reflection runtime state and a future human-approved rollback procedure only. It does not execute rollback, restart, launchd changes, or mail sending.

## Runtime state

- runtime path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- runtime branch: `Ver04-v1`
- runtime HEAD: `9c07c0fe75f69c5c849426a9bf64518eba2f54df`
- reflected source commit: `9c07c0fe75f69c5c849426a9bf64518eba2f54df`
- previous runtime branch before reflection: `Ver03-v4`
- previous runtime head before reflection: `7a5ccee01bce36cdd2a7be2d16520296e090ba62`
- no-send smoke command: `./.venv312/bin/python tools/render_notification_no_send_smoke.py --stdout-json`

## Rollback posture

- rollback executed: no
- restart_required: no
- launchd_action_required: no
- real_mail_sent: no
- notification sending behavior changed: no
- report-only / not FORMAL_GO / no automatic order / human decides manually: yes

## Future procedure

If a rollback is ever approved by a human, it should be planned as a separate runtime operation with explicit approval and a clean target state. This note does not provide executable rollback steps.

## Completion reference

- completion note path: `docs/operations/ai-orchestration/VER04_V1_RUNTIME_DEPLOYMENT_COMPLETE_20260702.md`
- current runtime state is reflected_active and does not require rollback
