# Maintenance documentation

This directory collects the public maintenance rules for BTC FX CODEX.

The goal is to make the project easier to review, safer to operate, and easier to improve with AI assistance while keeping human approval as the final decision point.

## Documents

| Document | Purpose |
|---|---|
| [`codex-workflow.md`](codex-workflow.md) | How ChatGPT / Codex-assisted maintenance is used in this repository |
| [`release-checklist.md`](release-checklist.md) | Checklist before making `main` represent a public release state |
| [`security-review-checklist.md`](security-review-checklist.md) | Practical checks for secrets, logs, API behavior, and financial-safety wording |

## Operating principle

AI tools may help with analysis, implementation, documentation, testing, and review. They do not replace maintainer approval.

Every meaningful change should answer:

1. What changed?
2. Why was it changed?
3. How was it tested?
4. Does it affect output, notification behavior, runtime safety, or credentials?
