# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-HARDENING`
- mode: `BOUNDED_CODEX`
- task_type: `PYTHON SOURCE / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC`
- previous_status: `P1 SPEC CREATED; GIT VALIDATION PENDING`

## Current goal

既存MEXC actual trade importerを、active specに従ってhardeningする。

これはgreenfield実装ではない。

Existing baseline:

```text
tools/log_feedback.py
  import_mexc_actual_trades()
  normalize_mexc_trade_history()
  normalize_mexc_order_history()
  normalize_mexc_position_history()

tests/test_mexc_actual_trade_importer.py
```

Existing downstream:

```text
tests/test_manual_trade_signal_linker.py
tests/test_manual_trade_ground_truth_report.py
```

Active spec:

```text
chatgpt/specs/active/20260710_manual_actual_trade_importer.md
```

## Completed preparation

ChatGPT has already:

- inspected the current importer, linker, report, and matching tests
- corrected the plan from “new importer implementation” to “existing importer hardening”
- selected `local/manual_trade_imports/YYYYMMDD/` as the canonical private input path
- added `local/manual_trade_imports/` to `.gitignore`
- created the active spec
- separated exchange ground truth from human decision ground truth
- fixed input, schema, privacy, idempotency, merge, conflict, CLI, exit-code, and test contracts

No real exchange export was read.

## Required read

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `chatgpt/specs/active/20260710_manual_actual_trade_importer.md`
4. `tools/log_feedback.py` only around the existing importer and CLI registration
5. `tests/test_mexc_actual_trade_importer.py`
6. downstream tests only as required for compatibility

Do not perform broad repo exploration.

## Exact next task

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-HARDENING
```

## Required implementation outcome

- add canonical CLI `import-manual-actual-trades`
- preserve `import-mexc-actual-trades` as an alias
- validate all three required workbook categories
- select sheets according to the active spec
- validate required columns before normalization
- normalize timezone, Decimal values, BTC symbol aliases, side/action/status, fee, and realized PnL
- add deterministic file, batch, source-row, logical-key, and row fingerprints
- merge with existing canonical CSVs
- skip exact duplicates
- reject corrected-export conflicts by default
- support explicit `--conflict-policy replace`
- perform atomic multi-output updates
- produce privacy-safe compact stdout JSON
- produce sanitized issues CSV when applicable
- preserve linker/report compatibility or update matching tests in the same bounded task

## Preferred structure

`tools/log_feedback.py` is already very large. Prefer extracting importer logic to:

```text
src/feedback/__init__.py
src/feedback/manual_actual_trade_importer.py
```

Keep CLI wiring in `tools/log_feedback.py`.

Do not extract unrelated code.

## Allowed edit

```text
.gitignore
tools/log_feedback.py
src/feedback/__init__.py
src/feedback/manual_actual_trade_importer.py
tests/test_mexc_actual_trade_importer.py
tests/test_manual_trade_signal_linker.py
tests/test_manual_trade_ground_truth_report.py
chatgpt/specs/active/20260710_manual_actual_trade_importer.md
```

The active spec may be corrected only when implementation proves a narrow technical impossibility or an internal contradiction. Report any such correction explicitly.

## Prohibited

- frozen old runtime repo
- real exchange export
- API key / secret / `.env`
- account/private/order endpoint
- runtime restart
- launchd modification
- mail sending or notification behavior change
- gate / threshold / score / trading logic change
- `paper_positions.csv` integration
- raw/export/generated CSV commit
- silent conflict overwrite

## Validation

Run once after implementation:

```bash
./.venv312/bin/python -m unittest \
  tests.test_mexc_actual_trade_importer \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report
git diff --check
```

Do not add `py_compile` when the targeted tests already import the changed modules.

Do not run the full suite unless shared-helper impact makes it necessary.

## Git and dirty tree

Start once with:

```bash
git status --short --branch
```

- integrate only safe overlapping changes
- leave unrelated dirty files untouched
- never reset, checkout, delete, or stash existing work
- stage only this task’s files
- stop if the branch is unclear, changes conflict, or private data appears

## Commit / push

Commit meaningful completed work in the same task.

Suggested commit:

```text
Harden manual actual trade importer
```

Do not push unless a checkpoint push is explicitly requested in the current user instruction.

## Compact report

Report:

```text
WORK_ID
STATUS
BRANCH
CHANGED
TESTS
COMMIT
PUSH
NOTES
```

Also write the same compact report exactly once to:

```text
/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt
```

Do not read, check, retry, watch, or recreate that file after writing.

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```

## Later corrected route

```text
P2 importer hardening
→ P3 existing linker / ground-truth pipeline audit and hardening
→ P4 scenario identity, coverage, and human decision-event schema
→ P5 offline A/B/C/STOP classifier
→ P6 historical replay
→ P7 shadow surface
→ P8 human manual trial
→ P9 evidence-backed tuning review
```

The exchange export alone cannot measure watch, skip, avoided loss, missed opportunity, or the reason for a human decision. Those require the P4 human decision-event layer.
