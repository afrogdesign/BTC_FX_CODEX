# P8 Issue Lifecycle Alignment

## Metadata

- work_id: `BTCFX-20260721-P8-ISSUE-LIFECYCLE-ALIGNMENT`
- mode: `BOUNDED_CODEX`
- status: approved for bounded implementation
- date: 2026-07-21
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## Goal

Align the deterministic P8 issue-summary output with already accepted operator-surface behavior so resolved UI issues are not emitted as permanently open observations.

## Confirmed mismatch

`src/feedback/manual_operator_trial_evidence.py` currently seeds these issue summaries as `confirmed usability issue` on every run:

- `P8-ISSUE-002_MAIN_VS_BIG_CHANCE_HIERARCHY`
- `P8-ISSUE-003_RAW_CLASSIFIER_PAYLOAD_EXPOSED`
- `P8-ISSUE-004_STOP_CARD_SIDE_IDENTITY`

Current source and regressions already establish:

- side-aware operator action is primary and Big Chance remains auxiliary/stale when conflicting
- raw execution flags are hidden from the primary operator workspace and internal values are collapsed
- Long/Short identity and side-specific STOP/action wording are explicit

These three entries are seeded known UI observations, not row-detected trading-performance findings. Their fixed open status therefore misstates the accepted implementation state.

## Required behavior

1. Preserve all existing issue keys and output compatibility.
2. Keep `P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY` unchanged as an evidence-driven `open hypothesis`.
3. Emit issues 002, 003, and 004 with status `resolved`.
4. Clearly distinguish their resolution from market-performance evidence:
   - no synthetic occurrence count
   - no synthetic resolved row count
   - no actual-backed count
   - no tuning eligibility
   - deterministic accepted-implementation confidence/basis metadata
5. Add stable, machine-readable resolution basis values for 002–004. The basis must describe the accepted observable contract, not commit hashes or local paths.
6. Do not inspect source files or tests dynamically at report runtime. The deterministic report must use explicit accepted lifecycle metadata.
7. Preserve report schema compatibility for existing consumers; additive fields are allowed.
8. Preserve deterministic rerun behavior and privacy-safe output.

## Acceptance invariants

- counts, class distribution, comparison metrics, review queue, actual evidence, global STOP opportunity, and P9 readiness are unchanged for the same fixtures
- issue 001 lifecycle and evidence semantics are unchanged
- issues 002–004 have zero row-derived counts and status `resolved`
- issues 002–004 include non-empty stable resolution basis metadata
- no classifier, gate, threshold, score, notification, mail, runtime, API, account, position, or order behavior changes

## Allowed files

- `src/feedback/manual_operator_trial_evidence.py`
- `tests/test_manual_operator_trial_evidence.py`
- `chatgpt/specs/active/20260721_p8_issue_lifecycle_alignment.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`

The issue register will be updated by ChatGPT after source/test review and acceptance. Do not edit it in this implementation task.

## Validation budget

Run only:

```text
./.venv312/bin/python -m unittest tests.test_manual_operator_trial_evidence
git diff --check -- src/feedback/manual_operator_trial_evidence.py tests/test_manual_operator_trial_evidence.py chatgpt/specs/active/20260721_p8_issue_lifecycle_alignment.md docs/operations/ai-orchestration/NEXT_ACTION.md
```

No full bundle, real-data replay, runtime operation, or second full run is authorized.

## Commit

Create one local commit containing only the allowed task files. Push is not authorized.

## Completion report

Return the compact report required by `AGENTS.md` and write the same report exactly once to:

`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`

Do not read, check, retry, recreate, monitor, or watch that file after writing.

## Acceptance — 2026-07-21

- status: accepted
- implementation commit: `0eeb26b`
- reported branch: `Ver04-v3`
- focused unittest: pass
- task-scoped `git diff --check`: pass
- direct MCP review confirmed:
  - issue 001 remains evidence-driven `open hypothesis`
  - issues 002–004 are emitted as `resolved`
  - stable accepted-implementation resolution metadata is present
  - row-derived and actual-backed counts remain zero for the seeded UI issues
  - evaluation, global STOP, actual evidence, and P9 readiness calculation paths are unchanged
- safety review: no classifier, gate, threshold, scoring, notification, mail, runtime, API, account, position, or order behavior change
- acceptance action: archive this spec and return P8 focus to actual-backed evidence readiness
