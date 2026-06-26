# Codex-assisted maintenance workflow

BTC FX CODEX is maintained as an AI-assisted OSS experiment.

The project uses AI tools to reduce maintenance friction, but the repository is not treated as an autonomous trading system and AI output is not treated as final authority.

## Roles

| Role | Responsibility |
|---|---|
| Maintainer | Final approval, merge decisions, release decisions, public wording, safety boundaries |
| ChatGPT | Planning, review, design comparison, documentation drafting, risk framing, prompt preparation |
| Codex / code worker | Local implementation, tests, refactors, reports, branch preparation, PR preparation |
| CI | Basic repeatable checks for install, compile, tests, and committed-secret hygiene |

## Workflow

1. **Define the intent**
   - Clarify whether the change is documentation, analysis logic, notification behavior, runtime operation, or security maintenance.
   - For market-analysis changes, separate observation, scoring, notification, and execution-related concerns.

2. **Prepare a bounded task**
   - AI workers should receive a narrow task with allowed files, expected output, test commands, and explicit prohibitions.
   - The task should state whether it may create files, update docs, run tests, or open a PR.

3. **Implement locally first when needed**
   - Codex may edit code, docs, tests, and operational notes.
   - Secrets, `.env`, private logs, and runtime artifacts must never be committed.

4. **Run checks**
   - `git diff --check`
   - Python compile checks
   - unit tests when available
   - secret / runtime-file checks

5. **Open a PR or make a small direct docs update**
   - Large changes should use a PR.
   - Small documentation corrections may be committed directly by the maintainer or through a controlled tool.

6. **Human review**
   - Confirm the change matches the intended version.
   - Confirm safety boundaries are preserved.
   - Confirm generated text does not imply financial advice or guaranteed outcomes.

7. **Merge / release**
   - `main` is the public source of truth.
   - `VERSION`, README, `.env.example`, and release notes should agree before release-oriented changes are merged.

## Safety boundaries

AI-assisted work must not:

- add real API keys, SMTP passwords, private account identifiers, or unredacted logs
- enable real exchange-side order execution by default
- remove financial-safety warnings
- present model output as a guaranteed trading signal
- bypass tests or reviewer approval for large changes
- force-push or rewrite public history without explicit maintainer approval

## Good Codex tasks

Examples of useful AI-assisted maintenance tasks:

- Add tests for pure analysis functions
- Refactor scoring logic into smaller functions
- Improve error handling for exchange API failures
- Add redacted sample outputs
- Review notification wording for financial-safety risk
- Create release checklists
- Summarize large operational logs without committing private data
- Compare current output against previous documented versions

## Review checklist for AI-generated changes

Before accepting AI-generated code or documentation, check:

- Does the change preserve the stated project scope?
- Are credentials and private logs absent?
- Are tests or manual checks recorded?
- Did the change alter notification rank, scoring, or risk thresholds?
- Does the text avoid financial advice language?
- Are README, `VERSION`, and `.env.example` still aligned?

## Current public version

The current documented public operating version is `Ver03-v4`.

`main` should remain aligned with:

- `VERSION`
- README `Current version`
- `.env.example` `SYSTEM_LABEL`
