#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATTERNS = [
    r"password\s*=",
    r"api[_-]?key\s*=",
    r"secret\s*=",
    r"BEGIN (RSA|OPENSSH|PRIVATE) KEY",
]
DESTRUCTIVE_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r"\bshutdown\b",
    r"\breboot\b",
    r"Remove-Item\s+-Recurse\s+-Force",
]
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "data",
    "htmlcov",
    "reports",
}


def scan(patterns: list[str]) -> list[str]:
    hits = []
    for path in ROOT.rglob("*"):
        if path.is_dir() or IGNORED_PARTS.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                hits.append(f"{path.relative_to(ROOT)}::{pattern}")
    return hits


def main() -> None:
    secrets = scan(FORBIDDEN_PATTERNS)
    destructive = scan(DESTRUCTIVE_PATTERNS)
    expected = [
        "app/main.py",
        "audits/linux/collector.py",
        "audits/windows/Collect-HardeningAudit.ps1",
        "samples/windows_audit_sample.json",
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "SUPPORT.md",
        "RELEASE_CHECKLIST.md",
    ]
    missing = [item for item in expected if not (ROOT / item).exists()]
    result = {
        "secrets_found": bool(secrets),
        "secrets_hits": secrets,
        "destructive_commands_found": bool(destructive),
        "destructive_hits": destructive,
        "expected_files_missing": missing,
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if secrets or destructive or missing else 0)


if __name__ == "__main__":
    main()
