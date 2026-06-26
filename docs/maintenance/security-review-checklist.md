# Security review checklist

This checklist is for changes that touch credentials, logs, notifications, external APIs, generated analysis, or release preparation.

## Secret and credential checks

- [ ] `.env` is not committed
- [ ] real OpenAI API keys are not committed
- [ ] SMTP passwords are not committed
- [ ] private account identifiers are not committed
- [ ] SSH keys, token files, and credential dumps are not committed
- [ ] examples use placeholders only

Useful commands:

```bash
git status --short
git ls-files | grep -E '(^|/)(\.env|.*\.pem|id_rsa|id_ed25519|private|secret|token|credential)$' || true
git grep -n -I -E '(sk-[A-Za-z0-9_-]{20,}|OPENAI_API_KEY=.+|SMTP_PASSWORD=.+)' -- ':!*.md' ':!.env.example' ':!SECURITY.md' ':!CONTRIBUTING.md' ':!.github/workflows/ci.yml' || true
```

## Runtime-data checks

- [ ] `logs/` is not committed
- [ ] `tmp/` is not committed
- [ ] `last_result.json` is not committed
- [ ] `heartbeat.txt` is not committed
- [ ] `monitor.pid` is not committed
- [ ] generated reports are either intentionally documented or ignored
- [ ] operational samples are redacted or synthetic

## External API checks

- [ ] exchange API calls are read-only unless explicitly documented otherwise
- [ ] API failures do not produce unsafe default signals
- [ ] timeout and retry behavior are bounded
- [ ] data-fetching code is separated from scoring / notification logic where practical
- [ ] errors are safe to log without exposing secrets

## Financial-safety checks

- [ ] generated output is not described as financial advice
- [ ] notifications are framed as analysis / reference information
- [ ] no wording implies guaranteed profit or guaranteed entry quality
- [ ] any execution-related terminology is clearly labeled as paper / simulated unless real execution is explicitly and safely implemented
- [ ] real order execution is not enabled by default

## AI-output checks

- [ ] AI summaries are clearly auxiliary
- [ ] prompts do not require secrets to be sent to an AI provider
- [ ] model output is not directly trusted as an execution instruction
- [ ] output formatting changes are tested with representative payloads

## Release checks

Before release or public-review state:

- [ ] README warning is present
- [ ] `SECURITY.md` is current
- [ ] `CONTRIBUTING.md` is current
- [ ] `VERSION` matches README
- [ ] `.env.example` matches README
- [ ] CI includes at least compile and unit-test checks
