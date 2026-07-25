# BTC Monitor

`btc_monitor` は、notificationを受け取った人間が15分足を確認し、manual trading判断を行うための支援システムです。

現段階の安全境界:

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order

## Repository

Primary working repo:

`/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

Frozen old runtime repo:

`/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`

通常作業はprimary repoだけを対象にします。frozen repoは明示された`RUNTIME_TASK`以外で使用しません。

## Setup

```bash
python3.12 -m venv .venv312
.venv312/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
.venv312/bin/python main.py
```

## AI / project navigation

新しいAI contextは次から開始します。

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

全体計画:

- `docs/operations/ai-orchestration/MASTER_PLAN.md`

現在地と次作業:

- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`

実行ルール:

- `docs/operations/ai-orchestration/AI_WORKFLOW.md`
- `docs/operations/ai-orchestration/CONTROL.md`

## Main directories

| Path | Purpose |
|---|---|
| `src/` | application and evidence logic |
| `tools/` | CLI and support tools |
| `scripts/` | operator scripts |
| `tests/` | tests |
| `chatgpt/specs/active/` | one current implementation contract when needed |
| `chatgpt/specs/archive/` | accepted historical contracts |
| `docs/operations/ai-orchestration/` | current plan, state, workflow, and controls |
| `docs/operations/strategy/` | current product research and route references |
| `local/reports/` | generated report output path (local, uncommitted) |
| `_archive/` | historical material; never a default read |

Generated reports are written under `local/reports/` and are intentionally uncommitted. Historical operations material is preserved under `_archive/legacy_operations_materials_20260721/`.

## Safety

- no automatic order
- no secrets or private/account/order endpoints
- no raw exchange export commit
- no unapproved runtime, launchd, mail, or notification change
- no unapproved gate, threshold, scoring, or classifier change
- human approval is required for production adoption

## Development line

- current development line: `Ver04-v5`
- accepted base line: `Ver04-v4`
- accepted cleanup checkpoint locator: `bff7669`
- `Ver05` is reserved for an evidence-backed, explicitly approved, implemented, validated, and accepted M6 change
- M1–M5 acceptance alone does not promote the project to `Ver05`
