# Repository Map for AI

## Repository

- repo: `afrogdesign/BTC_FX_CODEX`
- current branch: read from `git status --short --branch` and `CONTROL.md`
- historical branch labels such as `Ver03-v2` are historical only and must not be treated as the current default

## Repo paths

| Label | Path | Rule |
|---|---|---|
| MCP primary repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | default read / edit / test / git |
| Old runtime execution repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | do not edit or run by default; update later by GitHub pull after checkpoint push |

## AI operation anchors

| Path | Purpose |
|---|---|
| `AGENTS.md` | Fixed Codex / agent rules |
| `docs/operations/ai-orchestration/START_HERE.md` | First read entrypoint |
| `docs/operations/ai-orchestration/CURRENT_STATE.md` | Short current operating state |
| `docs/operations/ai-orchestration/NEXT_ACTION.md` | Current work frame |
| `docs/operations/ai-orchestration/CONTROL.md` | Current AI operating state |
| `docs/operations/ai-orchestration/TASK_LEDGER.md` | Work ledger, read only as needed |
| `docs/operations/ai-orchestration/DECISIONS.md` | Durable decisions |
| `docs/operations/ai-orchestration/PROMPTS.md` | Prompt templates |
| `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | Thread handoff |

## Directories to avoid by default

- `.venv312/`
- `logs/`
- generated CSV / report / HTML outputs
- large generated files under `local/`
- full `TASK_LEDGER.md`

## Project source directories

| Path | Purpose |
|---|---|
| `src/` | application and trading/report logic |
| `tools/` | CLI and support tooling |
| `tests/` | automated tests |
| `scripts/` | operator entry scripts |

## Operational docs directories

| Path | Purpose |
|---|---|
| `docs/operations/ai-orchestration/` | AI operation anchors and prompts |
| `docs/operations/strategy/` | reviewed roadmap and product direction |
| `運用資料/` | human-facing operational notes and reports |
| `chatgpt/` | ChatGPT-side supporting material |

## Rule

- AI should start with `AGENTS.md` and `docs/operations/ai-orchestration/START_HERE.md`
- do not full-scan the repo unless explicitly asked
- read only the files named in the current task plus required nearby context
- normal MCP task should end with local commit or `PUSH: none`, not routine push
