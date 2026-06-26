# Contributing to BTC FX CODEX

Thank you for considering a contribution.

BTC FX CODEX is an AI-assisted BTC market monitoring project. Contributions should improve safety, reproducibility, documentation, tests, or maintainability.

## Project scope

This project focuses on:

- BTC/USDT market-data monitoring
- Technical and market-structure analysis
- AI-assisted summaries and review workflows
- Notification and logging for later verification
- Safe OSS maintenance around credentials, logs, and external APIs

This project does **not** aim to provide financial advice or encourage automated trading.

## Good first contribution areas

- Documentation improvements
- Setup and environment clarification
- Test cases for pure analysis functions
- Safer error handling
- Dependency and security review
- Redacted sample outputs
- CI / lint / format improvements

## Before opening a pull request

Please check the following:

- Do not commit `.env`, API keys, SMTP passwords, logs, or private data
- Do not include unredacted operational logs
- Keep changes focused and easy to review
- Explain how the change was tested
- Avoid changing notification rank, trading assumptions, or risk thresholds without a clear reason

## Pull request checklist

Please include:

- Summary of the change
- Motivation / reason
- Files changed
- Test or verification result
- Security impact, if any
- Whether output format changes

## Maintenance references

For larger changes, review these documents first:

- [`docs/maintenance/codex-workflow.md`](docs/maintenance/codex-workflow.md)
- [`docs/maintenance/release-checklist.md`](docs/maintenance/release-checklist.md)
- [`docs/maintenance/security-review-checklist.md`](docs/maintenance/security-review-checklist.md)
- [`docs/samples/anonymized-output.md`](docs/samples/anonymized-output.md)

## Coding guidelines

- Prefer small, explicit functions
- Keep analysis logic testable without network access
- Separate data fetching from scoring / classification logic
- Avoid hidden side effects
- Use environment variables for secrets and runtime settings
- Keep runtime logs out of Git

## Security-related changes

If a change touches credentials, `.env`, logs, external APIs, SMTP, or notification behavior, describe the risk and mitigation in the pull request.

Security-related changes should also use the security review checklist in `docs/maintenance/security-review-checklist.md`.

## Financial-safety note

Do not present generated output as a guaranteed signal or trading instruction. Any wording that may be interpreted as financial advice should be softened and clearly labeled as analysis or reference information.
