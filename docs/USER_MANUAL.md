# Enterprise Hardening Toolkit User Manual

## 1. Product Purpose

Enterprise Hardening Toolkit is a defensive, local-first audit and reporting project for IT teams, MSPs, consultants, students, and compliance support teams.

It helps users:

- collect local endpoint hardening evidence
- import standardized audit JSON
- score findings by severity
- map findings to security controls
- generate practical remediation guidance
- produce Markdown reports for clients, managers, or audit preparation

The toolkit is audit-only by default. It does not exploit systems, collect credentials, bypass authentication, modify systems automatically, run remote scans, delete local files, or export data to cloud services.

## 2. What Is Included

- FastAPI backend
- SQLite database
- YAML baseline profiles
- Linux read-only collector
- Windows PowerShell collector template
- Windows sample audit JSON
- Standard audit JSON schema
- Severity scoring
- Remediation guide generation
- Markdown report export
- Sample report
- Tests and release verification script

## 3. Operating Model

The MVP uses a simple local collector workflow:

1. Run the collector on the endpoint being reviewed.
2. Save the collector output as JSON.
3. Import that JSON into the local toolkit API.
4. Store the audit result in SQLite.
5. Review the score, findings, and remediation guidance.
6. Generate a Markdown report.

This model avoids remote execution risk and keeps audit data local.

## 4. Safety Rules

Only use this toolkit on systems you own or are explicitly authorized to assess.

The toolkit must not be used to:

- exploit vulnerabilities
- bypass authentication
- collect passwords, tokens, SSH keys, or private certificates
- exfiltrate files
- disable security controls silently
- run destructive commands
- modify systems without explicit administrator approval
- scan external systems outside authorized scope

## 5. Folder Overview

```text
enterprise-hardening-toolkit/
  app/                  FastAPI backend, database, import, scoring, reports
  audits/linux/         Linux read-only audit collector
  audits/windows/       Windows PowerShell collector template
  baselines/            YAML hardening profiles
  docs/                 Architecture, usage, and this manual
  samples/              Example Linux and Windows audit JSON
  reports/              Generated Markdown reports
  scripts/              Sample report and release verification scripts
  tests/                Unit tests
  assets/               Optional public project images
```

## 6. Install The Toolkit

From the product folder, create and activate a Python virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The project requires:

- Python 3.10 or newer
- FastAPI
- Uvicorn
- Pydantic
- PyYAML

## 7. Start The Local API

Run:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open API documentation in a browser:

```text
http://127.0.0.1:8000/docs
```

Check system health:

```text
GET http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","mode":"audit-only"}
```

## 8. Create A Client

Use:

```text
POST /clients
```

Example body:

```json
{"name":"Sample Client"}
```

Expected result:

```json
{"client_id":1}
```

## 9. Register A Device

Use:

```text
POST /devices
```

Example body:

```json
{
  "client_id": 1,
  "hostname": "ubuntu-laptop-01",
  "os_family": "linux",
  "os_version": "Ubuntu 24.04",
  "role": "workstation"
}
```

Audit imports can also create the client and device automatically when the audit JSON includes client and device details.

## 10. Run A Linux Audit

On the Linux endpoint, run:

```bash
python3 audits/linux/collector.py --output linux_audit.json
```

The collector checks:

- firewall status
- package update status
- disk encryption indicators
- SSH exposure
- privileged local users
- logging status
- open listening services

The collector is read-only. Some checks may produce more useful evidence when run with administrator privileges, but the collector should not modify the endpoint.

## 11. Run A Windows Audit

On the Windows endpoint, open PowerShell as Administrator and run:

```powershell
.\audits\windows\Collect-HardeningAudit.ps1 -OutputPath .\windows_audit.json
```

The MVP uses PowerShell for Windows collection so Python does not need to be installed on Windows endpoints.

The MVP does not include:

- WinRM execution
- remote Windows execution
- auto-hardening
- Windows Python agent packaging

## 12. Import Audit JSON

Use:

```text
POST /audits/import
```

Example body:

```json
{"path":"samples/windows_audit_sample.json"}
```

Expected result:

```json
{
  "audit_id": 1,
  "device_id": 1,
  "score": 77,
  "findings": 3
}
```

## 13. Generate A Report

Use:

```text
POST /reports/{audit_id}
```

Example:

```text
POST /reports/1
```

The generated Markdown report is saved in:

```text
reports/
```

## 14. Generate The Included Sample Report

Run:

```bash
python3 scripts/generate_sample_report.py
```

This imports:

```text
samples/windows_audit_sample.json
```

and creates a Markdown report in:

```text
reports/
```

## 15. Read Finding Status

- `PASS`: the control appears satisfied
- `FAIL`: the control is not satisfied
- `WARN`: review is required or evidence is incomplete
- `INFO`: informational evidence only

## 16. Read Severity

- `critical`: urgent business/security risk
- `high`: important control failure
- `medium`: meaningful hardening gap
- `low`: minor improvement
- `informational`: context only

## 17. Use Baseline Profiles

Baseline files are stored in:

```text
baselines/
```

Included profiles:

- `ubuntu_debian.yaml`
- `windows_workstation.yaml`
- `windows_server.yaml`
- `small_business.yaml`

Use `GET /baselines` to view loaded profiles.

## 18. Run Tests

Run:

```bash
python3 -m unittest discover -s tests -v
```

Run release verification:

```bash
python3 scripts/verify_release.py
```

The verification script checks for expected files, secret-like patterns, and destructive command patterns.

## 19. Troubleshooting

If the API does not start:

- confirm the virtual environment is active
- confirm dependencies are installed
- confirm port `8000` is free
- run from the product root folder

If import fails:

- confirm the JSON path exists
- confirm the JSON uses the required audit schema
- confirm each check includes `check_id`, `name`, `category`, `status`, `current_value`, `recommended_value`, `severity`, `evidence`, `remediation`, and `compliance_mappings`

If the report does not generate:

- confirm the audit was imported successfully
- use `GET /audits` to confirm the audit ID exists
- run the sample report script to compare expected behavior

## 20. Workflow Example

1. Install the toolkit on a local workstation.
2. Start the FastAPI server.
3. Create a client record.
4. Register the target device.
5. Run the Linux or Windows collector on the endpoint.
6. Import the generated JSON file.
7. Review the audit score and findings.
8. Generate a Markdown report.
9. Share the report with the client or internal manager.
10. Use the remediation guidance to plan approved hardening work.
11. Re-run the collector after remediation.
12. Compare the new results with the previous report.

## 21. MVP Limitations

MVP-1 is intentionally scoped. It does not include:

- public deployment security
- RBAC
- hosted dashboard
- cloud export
- automatic hardening
- destructive cleanup
- live remote endpoint execution
- PDF export

These can be added in later versions after the local audit and reporting workflow is stable.
