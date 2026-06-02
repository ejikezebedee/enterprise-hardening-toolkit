from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.audit_schema import validate_audit_payload
from app.db.database import get_audit_by_scan_id, get_or_create_device, insert_audit, init_db
from app.services.scoring import enrich_findings, overall_score


def load_audit_json(path: Path | str) -> dict[str, Any]:
    audit_path = Path(path)
    with audit_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_audit_payload(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def import_audit_payload(payload: dict[str, Any], db_path: Path | str | None = None) -> dict[str, Any]:
    errors = validate_audit_payload(payload)
    if errors:
        raise ValueError("; ".join(errors))
    if db_path is None:
        init_db()
        existing = get_audit_by_scan_id(payload["scan_id"])
        if existing:
            return existing
        device_id = get_or_create_device(payload)
        findings = enrich_findings(payload["checks"])
        audit_id = insert_audit(device_id, payload, overall_score(findings), findings)
    else:
        init_db(db_path)
        existing = get_audit_by_scan_id(payload["scan_id"], db_path)
        if existing:
            return existing
        device_id = get_or_create_device(payload, db_path)
        findings = enrich_findings(payload["checks"])
        audit_id = insert_audit(device_id, payload, overall_score(findings), findings, db_path)
    return {"audit_id": audit_id, "device_id": device_id, "score": overall_score(findings), "findings": len(findings)}


def import_audit_file(path: Path | str, db_path: Path | str | None = None) -> dict[str, Any]:
    return import_audit_payload(load_audit_json(path), db_path)
