# Start Here

Welcome to Enterprise Hardening Toolkit.

This open-source project is a defensive, local-first audit and reporting toolkit for IT teams, MSPs, consultants, students, and compliance support teams.

## What To Do First

1. Read `README.md` for the short product overview.
2. Read `docs/USER_MANUAL.md` for the complete step-by-step manual.
3. Run the sample demo:

```bash
python3 scripts/run_demo.py
```

4. Review the generated report in:

```text
reports/audit-windows-sample-001.md
```

5. Start the API locally:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

6. Open:

```text
http://127.0.0.1:8000/docs
```

## Important Safety Boundary

Use this product only on systems you own or are authorized to assess.

This MVP does not include offensive tooling, exploit code, credential collection, remote execution, auto-hardening, public deployment, cloud export, or file deletion.

## Included Documents

- `README.md` - product overview and quick start
- `docs/USER_MANUAL.md` - full step-by-step usage manual
- `docs/COLLECTOR_GUIDE.md` - Linux and Windows collector instructions
- `docs/TROUBLESHOOTING.md` - common setup and usage issues
- `SECURITY.md` - defensive boundaries and safe usage
- `CONTRIBUTING.md` - contribution workflow
- `CODE_OF_CONDUCT.md` - community standards
- `RELEASE_CHECKLIST.md` - final release verification checklist

## Fastest Demo Path

Run:

```bash
python3 scripts/run_demo.py
```

Expected result:

```text
DEMO_STATUS=PASS
REPORT_GENERATED=true
```
