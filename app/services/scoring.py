from __future__ import annotations

from typing import Any


SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 3,
    "informational": 0,
}


def score_check(check: dict[str, Any]) -> int:
    status = str(check.get("status", "")).upper()
    severity = str(check.get("severity", "informational")).lower()
    if status == "PASS" or status == "INFO":
        return 0
    if status == "WARN":
        return max(1, SEVERITY_WEIGHTS.get(severity, 3) // 2)
    return SEVERITY_WEIGHTS.get(severity, 3)


def enrich_findings(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings = []
    for check in checks:
        enriched = dict(check)
        enriched["status"] = str(enriched["status"]).upper()
        enriched["severity"] = str(enriched["severity"]).lower()
        enriched["score"] = score_check(enriched)
        findings.append(enriched)
    return findings


def overall_score(findings: list[dict[str, Any]]) -> int:
    penalty = sum(int(finding["score"]) for finding in findings)
    return max(0, 100 - penalty)


def severity_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {name: 0 for name in SEVERITY_WEIGHTS}
    for finding in findings:
        if finding["status"] in {"FAIL", "WARN"}:
            counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
    return counts

