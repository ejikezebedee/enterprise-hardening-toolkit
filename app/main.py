from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.config import BASELINES_DIR, DEFAULT_DB_PATH
from app.db.database import create_client, create_device, init_db, list_rows
from app.services.audit_importer import import_audit_file
from app.services.baselines import load_all_baselines
from app.services.reports import generate_markdown_report


class ClientCreate(BaseModel):
    name: str


class DeviceCreate(BaseModel):
    client_id: int
    hostname: str
    os_family: str
    os_version: str
    role: str = "workstation"


class AuditImportRequest(BaseModel):
    path: str


app = FastAPI(
    title="Enterprise Computer Hardening Toolkit",
    version="0.1.0",
    description="Defensive local-first endpoint hardening audit and reporting toolkit.",
)


@app.on_event("startup")
def startup() -> None:
    init_db(DEFAULT_DB_PATH)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "audit-only"}


@app.get("/baselines")
def baselines() -> list[dict]:
    return load_all_baselines(BASELINES_DIR)


@app.post("/clients")
def clients_create(payload: ClientCreate) -> dict[str, int]:
    return {"client_id": create_client(payload.name)}


@app.get("/clients")
def clients_list() -> list[dict]:
    return list_rows("clients")


@app.post("/devices")
def devices_create(payload: DeviceCreate) -> dict[str, int]:
    return {"device_id": create_device(payload.client_id, payload.hostname, payload.os_family, payload.os_version, payload.role)}


@app.get("/devices")
def devices_list() -> list[dict]:
    return list_rows("devices")


@app.post("/audits/import")
def audits_import(payload: AuditImportRequest) -> dict:
    path = Path(payload.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Audit JSON not found: {path}")
    try:
        return import_audit_file(path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/audits")
def audits_list() -> list[dict]:
    return list_rows("audits")


@app.post("/reports/{audit_id}")
def report_create(audit_id: int) -> dict[str, str]:
    try:
        path = generate_markdown_report(audit_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"report_path": str(path)}

