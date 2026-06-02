from __future__ import annotations

from typing import Any


VALID_STATUSES = {"PASS", "FAIL", "WARN", "INFO"}
VALID_SEVERITIES = {"critical", "high", "medium", "low", "informational"}
REQUIRED_SCAN_FIELDS = {"scan_id", "hostname", "os_family", "os_version", "timestamp", "checks"}
REQUIRED_CHECK_FIELDS = {
    "check_id",
    "category",
    "name",
    "status",
    "current_value",
    "recommended_value",
    "severity",
    "evidence",
    "remediation",
    "compliance_mappings",
}


def validate_audit_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing_scan_fields = sorted(REQUIRED_SCAN_FIELDS - set(payload))
    if missing_scan_fields:
        errors.append(f"Missing scan fields: {', '.join(missing_scan_fields)}")

    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("checks must be a non-empty list")
        return errors

    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"checks[{index}] must be an object")
            continue
        missing_check_fields = sorted(REQUIRED_CHECK_FIELDS - set(check))
        if missing_check_fields:
            errors.append(f"checks[{index}] missing fields: {', '.join(missing_check_fields)}")
        status = str(check.get("status", "")).upper()
        severity = str(check.get("severity", "")).lower()
        if status not in VALID_STATUSES:
            errors.append(f"checks[{index}] has invalid status: {status}")
        if severity not in VALID_SEVERITIES:
            errors.append(f"checks[{index}] has invalid severity: {severity}")
    return errors

