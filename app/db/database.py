from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.core.config import DEFAULT_DB_PATH, ensure_runtime_dirs


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    hostname TEXT NOT NULL,
    os_family TEXT NOT NULL,
    os_version TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'workstation',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    os_family TEXT NOT NULL,
    source_path TEXT NOT NULL,
    loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id TEXT NOT NULL UNIQUE,
    device_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    score INTEGER NOT NULL,
    raw_json TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id)
);

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    check_id TEXT NOT NULL,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    severity TEXT NOT NULL,
    score INTEGER NOT NULL,
    current_value TEXT NOT NULL,
    recommended_value TEXT NOT NULL,
    evidence TEXT NOT NULL,
    remediation TEXT NOT NULL,
    compliance_mappings TEXT NOT NULL,
    FOREIGN KEY (audit_id) REFERENCES audits(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id)
);
"""


def connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    ensure_runtime_dirs()
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA_SQL)


def create_client(name: str, db_path: Path | str = DEFAULT_DB_PATH) -> int:
    with connect(db_path) as connection:
        cursor = connection.execute("INSERT OR IGNORE INTO clients(name) VALUES (?)", (name,))
        if cursor.lastrowid:
            return int(cursor.lastrowid)
        row = connection.execute("SELECT id FROM clients WHERE name = ?", (name,)).fetchone()
        return int(row["id"])


def create_device(
    client_id: int,
    hostname: str,
    os_family: str,
    os_version: str,
    role: str = "workstation",
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO devices(client_id, hostname, os_family, os_version, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (client_id, hostname, os_family, os_version, role),
        )
        return int(cursor.lastrowid)


def get_or_create_device(payload: dict[str, Any], db_path: Path | str = DEFAULT_DB_PATH) -> int:
    client_id = create_client(payload.get("client_name", "Sample Client"), db_path)
    hostname = str(payload["hostname"])
    os_family = str(payload["os_family"])
    os_version = str(payload["os_version"])
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT id FROM devices
            WHERE client_id = ? AND hostname = ? AND os_family = ? AND os_version = ?
            ORDER BY id DESC LIMIT 1
            """,
            (client_id, hostname, os_family, os_version),
        ).fetchone()
        if row:
            return int(row["id"])
    return create_device(client_id, hostname, os_family, os_version, payload.get("role", "workstation"), db_path)


def list_rows(table: str, db_path: Path | str = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    allowed = {"clients", "devices", "profiles", "audits", "findings", "reports"}
    if table not in allowed:
        raise ValueError(f"Unsupported table: {table}")
    with connect(db_path) as connection:
        return [dict(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()]


def get_audit_by_scan_id(scan_id: str, db_path: Path | str = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        audit = connection.execute(
            "SELECT id, device_id, score FROM audits WHERE scan_id = ?",
            (scan_id,),
        ).fetchone()
        if not audit:
            return None
        findings_count = connection.execute(
            "SELECT COUNT(*) AS total FROM findings WHERE audit_id = ?",
            (audit["id"],),
        ).fetchone()
        return {
            "audit_id": int(audit["id"]),
            "device_id": int(audit["device_id"]),
            "score": int(audit["score"]),
            "findings": int(findings_count["total"]),
        }


def insert_audit(
    device_id: int,
    payload: dict[str, Any],
    score: int,
    findings: list[dict[str, Any]],
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO audits(scan_id, device_id, timestamp, score, raw_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload["scan_id"], device_id, payload["timestamp"], score, json.dumps(payload, indent=2)),
        )
        audit_id = int(cursor.lastrowid)
        for finding in findings:
            connection.execute(
                """
                INSERT INTO findings(
                    audit_id, check_id, category, name, status, severity, score,
                    current_value, recommended_value, evidence, remediation, compliance_mappings
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    finding["check_id"],
                    finding["category"],
                    finding["name"],
                    finding["status"],
                    finding["severity"],
                    finding["score"],
                    str(finding["current_value"]),
                    str(finding["recommended_value"]),
                    str(finding["evidence"]),
                    str(finding["remediation"]),
                    json.dumps(finding["compliance_mappings"], sort_keys=True),
                ),
            )
        return audit_id


def get_audit_bundle(audit_id: int, db_path: Path | str = DEFAULT_DB_PATH) -> dict[str, Any]:
    with connect(db_path) as connection:
        audit = connection.execute(
            """
            SELECT audits.*, devices.hostname, devices.os_family, devices.os_version, clients.name AS client_name
            FROM audits
            JOIN devices ON audits.device_id = devices.id
            JOIN clients ON devices.client_id = clients.id
            WHERE audits.id = ?
            """,
            (audit_id,),
        ).fetchone()
        if not audit:
            raise ValueError(f"Audit not found: {audit_id}")
        findings = connection.execute("SELECT * FROM findings WHERE audit_id = ? ORDER BY score DESC", (audit_id,)).fetchall()
        return {"audit": dict(audit), "findings": [dict(row) for row in findings]}


def record_report(audit_id: int, path: str, db_path: Path | str = DEFAULT_DB_PATH) -> None:
    with connect(db_path) as connection:
        connection.execute("INSERT INTO reports(audit_id, path) VALUES (?, ?)", (audit_id, path))
