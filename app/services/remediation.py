from __future__ import annotations

from typing import Any


def quick_wins(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for finding in findings:
        if finding["status"] in {"FAIL", "WARN"} and finding["severity"] in {"high", "medium", "low"}:
            selected.append(finding)
    return sorted(selected, key=lambda item: item["score"], reverse=True)[:5]


def remediation_plan(findings: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    plan = {"critical": [], "high": [], "medium": [], "low": [], "informational": []}
    for finding in findings:
        if finding["status"] in {"FAIL", "WARN"}:
            plan.setdefault(finding["severity"], []).append(finding)
    return plan

