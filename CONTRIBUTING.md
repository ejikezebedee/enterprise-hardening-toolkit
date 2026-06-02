# Contributing

Thank you for helping improve Enterprise Hardening Toolkit.

## Scope

This project accepts defensive improvements only:

- audit checks
- baseline profiles
- reporting improvements
- documentation
- tests
- bug fixes
- safe local workflow improvements

Do not submit exploitation, credential collection, stealth, persistence, evasion, unauthorized scanning, destructive commands, or offensive automation.

## Development Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Run release verification:

```bash
python3 scripts/verify_release.py
```

## Pull Request Checklist

- Keep changes defensive and local-first.
- Add or update tests for behavior changes.
- Update documentation when workflows change.
- Avoid storing secrets, local paths, or customer data.
- Keep generated runtime files out of commits.

## Reporting Issues

When opening an issue, include:

- what you tried
- expected behavior
- actual behavior
- operating system
- Python version
- relevant logs or traceback without secrets
