# Security Policy

BTC FX CODEX handles market-data APIs, AI API settings, SMTP configuration, and runtime logs. Even when the project is used only for monitoring and analysis, security review is important.

## Supported versions

This repository is currently in an early public-maintenance phase. Security fixes are applied to the `main` branch unless a release branch is explicitly created later.

| Version | Supported |
|---|---|
| `main` | Yes |
| older snapshots | No |

## What to report

Please report issues related to:

- API keys, SMTP passwords, or credentials being exposed
- Sensitive data being written to logs
- Unsafe handling of `.env` values
- External API request handling problems
- Dependency vulnerabilities
- Output that could be misread as automated trading execution
- Any code path that could accidentally trigger real exchange-side order execution

## What not to include publicly

Do not post the following in public issues or pull requests:

- API keys
- SMTP passwords
- Private account identifiers
- Full unredacted `.env` files
- Private operational logs
- Server hostnames, SSH paths, or private deployment details

Use redacted examples instead.

## Reporting process

If you find a vulnerability, please open a GitHub issue with a redacted description, or contact the maintainer privately if the details cannot be safely shared in public.

Please include:

1. A short summary of the issue
2. Affected file or feature
3. Steps to reproduce, if safe to share
4. Potential impact
5. Suggested mitigation, if known

## Maintainer response

The maintainer will triage reports with the following priority:

1. Secret exposure or credential leakage
2. Unintended order execution risk
3. Log privacy problems
4. Dependency vulnerabilities
5. Documentation or warning-label improvements

## Trading and financial safety

This project is not intended to provide financial advice or execute trades automatically. Security reports that reduce the chance of misunderstanding, unsafe automation, or over-trust in generated analysis are welcome.
