# Resume Protocol

Use only when a ChatGPT or Codex context was lost.

## Fresh resume

1. `AGENTS.md`
2. `START_HERE.md`
3. `CURRENT_STATE.md`
4. `NEXT_ACTION.md`
5. the one active spec
6. `AI_WORKFLOW.md`

Then inspect only files required by the current task.

## Same-thread continuation

Do not run the resume sequence. Use the new message as a delta and inspect only changed/named files.

## Block when

- branch, active spec, Work ID, or scope conflict
- primary and frozen repo are confused
- material product/trading/safety judgment remains unresolved

Historical files, `TASK_LEDGER.md`, handoffs, logs, and generated directories are not default resume reads.
