# Usage Guide

This MVP is local-first and audit-only by default.

## Workflow

1. Start the FastAPI application on localhost.
2. Create a client.
3. Register a device or import an audit JSON that creates the device automatically.
4. Import Linux or Windows collector JSON.
5. Generate a Markdown report.
6. Review findings and remediation guidance.

## Linux Collection

Run the collector locally on the Linux endpoint:

```bash
python3 audits/linux/collector.py --output linux_audit.json
```

The collector is read-only. It checks firewall status, updates, encryption indicators, SSH configuration, privileged users, logging, and listening services.

## Windows Collection

Run the PowerShell collector locally on the Windows endpoint as Administrator:

```powershell
.\audits\windows\Collect-HardeningAudit.ps1 -OutputPath .\windows_audit.json
```

The PowerShell collector outputs JSON for import. MVP-1 does not include remote WinRM execution.

## Import Sample Data

```bash
python3 scripts/generate_sample_report.py
```

## Run Verification Tests

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_release.py
```

## Safety

This product does not exploit, bypass authentication, collect credentials, exfiltrate files, disable security controls silently, or perform destructive actions.
