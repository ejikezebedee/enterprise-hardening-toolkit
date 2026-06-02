# Architecture

## Model

MVP-1 uses a local collector model.

- Endpoint collectors run locally and produce JSON.
- The backend imports JSON, stores audits in SQLite, scores findings, and generates reports.
- The dashboard/API does not remotely execute commands on endpoints.

## Data Model

Organization flow:

Client -> Device -> Audit -> Findings -> Report

SQLite tables:

- clients
- devices
- profiles
- audits
- findings
- reports

## Security Boundary

The product is defensive-only. It has no exploit code, no credential collection, no remote scanning, no auto-hardening, and no destructive cleanup feature.

