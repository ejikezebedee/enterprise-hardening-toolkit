from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.config import IMPORTS_DIR, PROJECT_ROOT, SAMPLES_DIR
from app.core.audit_schema import validate_audit_payload
from app.db.database import get_audit_by_scan_id, get_or_create_device, insert_audit, init_db
from app.services.scoring import enrich_findings, overall_score


APPROVED_IMPORT_DIRS = (SAMPLES_DIR, IMPORTS_DIR)


def resolve_allowed_audit_path(path: Path | str) -> Path:
    requested = Path(path)
    candidate = requested if requested.is_absolute() else PROJECT_ROOT / requested
    resolved = candidate.resolve(strict=False)
    approved_roots = tuple(directory.resolve(strict=False) for directory in APPROVED_IMPORT_DIRS)
    if not any(resolved == root or root in resolved.parents for root in approved_roots):
        allowed = ", ".join(str(root.relative_to(PROJECT_ROOT)) for root in APPROVED_IMPORT_DIRS)
        raise ValueError(f"Audit imports are restricted to approved directories: {allowed}")
    if not resolved.exists():
        raise FileNotFoundError(f"Audit JSON not found: {requested}")
    if not resolved.is_file():
        raise ValueError(f"Audit import path must be a file: {requested}")
    return resolved


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
    return import_audit_payload(load_audit_json(resolve_allowed_audit_path(path)), db_path)
