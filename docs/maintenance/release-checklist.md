# Release checklist

Use this checklist before making `main` represent a public release or externally reviewed state.

## Release identity

- [ ] README `Current version` is correct
- [ ] `VERSION` is correct
- [ ] `.env.example` `SYSTEM_LABEL` matches the release version
- [ ] Release notes or PR summary explain what changed
- [ ] Older branches / PRs are not being merged accidentally

## Source and runtime boundary

- [ ] `.env` is not tracked
- [ ] `logs/` is not tracked
- [ ] `tmp/` is not tracked
- [ ] generated runtime files are ignored or intentionally excluded
- [ ] private deployment paths and hostnames are not required for normal setup
- [ ] sample outputs are anonymized or synthetic

## Security

- [ ] no real API keys
- [ ] no SMTP passwords
- [ ] no private account identifiers
- [ ] no unredacted operational logs
- [ ] no exchange-side order execution is enabled by default
- [ ] external API errors are handled safely
- [ ] financial-safety warnings are present where needed

## Tests and checks

Recommended commands:

```bash
git diff --check
python3 -m compileall main.py config.py src
if [ -d tools ]; then python3 -m compileall tools; fi
if [ -d tests ]; then python3 -m unittest discover -s tests -p "test*.py"; fi
```

If using the project virtual environment:

```bash
.venv312/bin/python -m compileall main.py config.py src
if [ -d tools ]; then .venv312/bin/python -m compileall tools; fi
if [ -d tests ]; then .venv312/bin/python -m unittest discover -s tests -p "test*.py"; fi
```

## Documentation

- [ ] README setup still works for a new reader
- [ ] Security policy is still accurate
- [ ] Contributing guide is still accurate
- [ ] CI description matches the actual workflow
- [ ] Known limitations are not hidden

## Merge decision

A release-oriented PR should not be merged until:

1. The intended version is clear.
2. The diff has been reviewed at the file-category level.
3. CI or local checks have been run.
4. Any security-sensitive change has been explicitly reviewed.
5. The maintainer approves the public state of `main`.
