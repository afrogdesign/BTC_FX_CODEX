---
name: Bug report
description: Report a reproducible problem with BTC FX CODEX
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting a problem. Use redacted or synthetic examples only.
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: What happened?
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
      description: What did you expect to happen?
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: Use redacted or synthetic examples only.
      placeholder: |
        1. Run ...
        2. Observe ...
        3. Expected ...
    validations:
      required: false
  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: OS, Python version, and relevant package versions.
    validations:
      required: false
  - type: checkboxes
    id: safety
    attributes:
      label: Safety confirmation
      options:
        - label: I removed private credentials, private logs, and account identifiers from this report.
          required: true
        - label: I understand that project output is analysis/reference information, not financial advice.
          required: true
