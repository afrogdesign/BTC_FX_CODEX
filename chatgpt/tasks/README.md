# Optional Task Contract Tooling

This directory contains the A1 task-manifest and report-validation tooling artifacts.

## Status

- A1 tooling: accepted and available
- A2 pilot: completed
- A3 default routing: superseded
- A4 CWT integration: not planned

This is not the normal Codex route.

Normal work uses:

```text
compact prompt
→ one bounded implementation
→ matching validation
→ compact report
→ ChatGPT MCP review
```

Use these manifests and schemas only when exact machine alignment is acceptance-critical, such as a bounded heavy acceptance command, runtime task, checkpoint task, or multi-stage ownership contract.

## Commands

```text
./.venv312/bin/python tools/ai_task_contract.py validate-task --task <path>
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context fresh
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context delta
./.venv312/bin/python tools/ai_task_contract.py validate-report --task <path> --report <path>
```

## Contents

- `schemas/`: task and report JSON schemas
- `examples/`: non-authoritative examples
- `archive/`: completed pilot manifests
- `active/`: normally empty; populated only by an explicitly authorized strict task

The fixed response outbox remains `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`. A report is written exactly once with no read-back, retry, polling, or recreation.
