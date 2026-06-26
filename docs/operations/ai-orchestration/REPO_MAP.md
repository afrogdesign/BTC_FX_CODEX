# Repository Map for AI

## Repository

- repo: `afrogdesign/BTC_FX_CODEX`
- active branch: `Ver03-v2`

## AI operation anchors

| Path | Purpose |
|---|---|
| `AGENTS.md` | Fixed Codex / agent rules |
| `docs/operations/ai-orchestration/CONTROL.md` | Current AI operating state |
| `docs/operations/ai-orchestration/TASK_LEDGER.md` | Work ledger |
| `docs/operations/ai-orchestration/DECISIONS.md` | Durable decisions |
| `docs/operations/ai-orchestration/PROMPTS.md` | Prompt templates |
| `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | Thread handoff |

## Product planning

| Path | Purpose |
|---|---|
| `運用資料/計画/README.md` | Planning folder entry |
| `運用資料/計画/00_Ver03-v1_統合再計画_20260608.md` | Integrated product plan |
| `運用資料/計画/01_計画フォルダ再構成案_20260608.md` | Planning folder structure |
| `運用資料/計画/02_Ver03-v1_実装ロードマップ_20260608.md` | Roadmap |
| `運用資料/計画/03_AI参照ファイル設計_20260608.md` | AI file design |
| `運用資料/計画/04_次にCodexへ渡す作業方針_20260608.md` | Next Codex policy |

## Runtime and trading code

| Path | Purpose |
|---|---|
| `main.py` | Monitor entrypoint |
| `src/trade/active_plan.py` | Active Plan logic |
| `src/storage/csv_logger.py` | CSV logging |
| `tools/log_feedback.py` | Report builders / CLI |
| `tests/` | Tests |

## Operational reports

| Path | Purpose |
|---|---|
| `運用資料/reports/` | Human-readable reports |
| `運用資料/reports/analysis/` | Analysis reports |
| `logs/csv/` | Runtime CSV logs |
| `logs/runtime/` | Runtime stdout / stderr |

## Rule

AI should start with:

1. `docs/operations/ai-orchestration/CONTROL.md`
2. `docs/operations/ai-orchestration/REPO_MAP.md`
3. the files named in the current task
