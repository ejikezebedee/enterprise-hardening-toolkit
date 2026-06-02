# Collector Guide

## Purpose

Collectors gather endpoint hardening evidence and save it as standardized JSON. The backend imports that JSON, scores findings, and generates reports.

## Standard Workflow

1. Run the collector on the endpoint.
2. Save the JSON output.
3. Import the JSON into the toolkit API.
4. Generate the Markdown report.

## Linux Collector

Run from the product root:

```bash
python3 audits/linux/collector.py --output linux_audit.json
```

The Linux collector checks:

- firewall status
- update status
- disk encryption indicators
- SSH exposure
- privileged local users
- logging status
- open listening services

The collector is read-only. Some checks may return more complete evidence when run with administrator privileges.

## Windows Collector

Open PowerShell as Administrator and run:

```powershell
.\audits\windows\Collect-HardeningAudit.ps1 -OutputPath .\windows_audit.json
```

The MVP uses PowerShell for Windows so Python does not need to be installed on Windows endpoints.

## Import Collector Output

Start the API, then use:

```text
POST /audits/import
```

Example body:

```json
{"path":"samples/windows_audit_sample.json"}
```

For your own collector output, replace the path with the generated JSON file path.

## Required JSON Fields

Each audit JSON must include:

- `scan_id`
- `hostname`
- `os_family`
- `os_version`
- `timestamp`
- `checks`

Each check must include:

- `check_id`
- `category`
- `name`
- `status`
- `current_value`
- `recommended_value`
- `severity`
- `evidence`
- `remediation`
- `compliance_mappings`

## MVP Limits

The MVP does not include:

- remote endpoint execution
- WinRM automation
- SSH orchestration
- automatic hardening
- background agents
- centralized fleet deployment
