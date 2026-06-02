# Troubleshooting

## API Does Not Start

Check that dependencies are installed:

```bash
pip install -r requirements.txt
```

Start the API from the product root:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If port `8000` is busy, use another port:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

## Import Fails

Confirm the JSON file exists and the path is correct:

```json
{"path":"samples/windows_audit_sample.json"}
```

Confirm the JSON contains the required audit fields listed in `docs/COLLECTOR_GUIDE.md`.

## Sample Demo Fails

Run from the product root:

```bash
python3 scripts/run_demo.py
```

If it fails, run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_release.py
```

## Windows PowerShell Script Will Not Run

Open PowerShell as Administrator.

If PowerShell blocks the script, review your execution policy. A common one-time local command is:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run:

```powershell
.\audits\windows\Collect-HardeningAudit.ps1 -OutputPath .\windows_audit.json
```

## Linux Collector Returns Limited Evidence

Some checks may return limited information without administrator privileges. Re-run with appropriate local authorization if more complete evidence is required.

## Report Does Not Generate

Confirm the audit exists:

```text
GET /audits
```

Then generate the report:

```text
POST /reports/{audit_id}
```

## Release Verification Fails

Run:

```bash
python3 scripts/verify_release.py
```

Review the JSON output. The release scan checks for expected files, secret-like patterns, and destructive command patterns.

