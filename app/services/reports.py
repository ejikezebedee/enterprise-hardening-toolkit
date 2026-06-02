from __future__ import annotations

from pathlib import Path

from app.core.config import REPORTS_DIR
from app.db.database import get_audit_bundle, record_report
from app.services.remediation import quick_wins, remediation_plan
from app.services.scoring import severity_counts


def _finding_line(finding: dict) -> str:
    mappings = finding.get("compliance_mappings", "")
    return (
        f"- **{finding['status']} / {finding['severity'].upper()}** `{finding['check_id']}` "
        f"{finding['name']}\\n"
        f"  - Current: {finding['current_value']}\\n"
        f"  - Recommended: {finding['recommended_value']}\\n"
        f"  - Evidence: {finding['evidence']}\\n"
        f"  - Remediation: {finding['remediation']}\\n"
        f"  - Compliance: {mappings}"
    )


def generate_markdown_report(audit_id: int, output_dir: Path = REPORTS_DIR, db_path: Path | str | None = None) -> Path:
    bundle = get_audit_bundle(audit_id) if db_path is None else get_audit_bundle(audit_id, db_path)
    audit = bundle["audit"]
    findings = bundle["findings"]
    counts = severity_counts(findings)
    wins = quick_wins(findings)
    plan = remediation_plan(findings)

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"audit-{audit['scan_id']}.md"
    sections = [
        f"# Enterprise Computer Hardening Report",
        "",
        "## Executive Summary",
        f"- Client: {audit['client_name']}",
        f"- Hostname: {audit['hostname']}",
        f"- Operating system: {audit['os_family']} {audit['os_version']}",
        f"- Audit timestamp: {audit['timestamp']}",
        f"- Overall hardening score: {audit['score']}/100",
        "",
        "## Severity Summary",
        f"- Critical: {counts.get('critical', 0)}",
        f"- High: {counts.get('high', 0)}",
        f"- Medium: {counts.get('medium', 0)}",
        f"- Low: {counts.get('low', 0)}",
        "",
        "## Quick Wins",
    ]
    sections.extend(_finding_line(finding) for finding in wins)
    sections.append("")
    sections.append("## Full Findings")
    sections.extend(_finding_line(finding) for finding in findings)
    sections.append("")
    sections.append("## Remediation Plan")
    for severity in ["critical", "high", "medium", "low", "informational"]:
        sections.append(f"### {severity.title()}")
        entries = plan.get(severity, [])
        if not entries:
            sections.append("- No open findings in this group.")
        else:
            sections.extend(f"- `{entry['check_id']}` {entry['remediation']}" for entry in entries)
    sections.append("")
    sections.append("## Safety Boundary")
    sections.append(
        "This report is defensive and audit-only. It does not authorize exploitation, credential collection, "
        "silent security-control changes, destructive commands, or activity on systems outside approved scope."
    )
    report_path.write_text("\\n".join(sections) + "\\n", encoding="utf-8")
    if db_path is None:
        record_report(audit_id, str(report_path))
    else:
        record_report(audit_id, str(report_path), db_path)
    return report_path

