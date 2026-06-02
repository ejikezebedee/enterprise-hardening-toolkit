#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path


def run(command: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(command, check=False, text=True, capture_output=True, timeout=10)
        return completed.returncode, (completed.stdout or completed.stderr).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)


def check_firewall() -> dict:
    ufw_code, ufw_output = run(["ufw", "status"])
    firewall_cmd_code, firewall_cmd_output = run(["firewall-cmd", "--state"])
    active = ("Status: active" in ufw_output) or (firewall_cmd_code == 0 and "running" in firewall_cmd_output)
    return make_check(
        "LINUX-FIREWALL-001",
        "network",
        "Host firewall is enabled",
        "PASS" if active else "FAIL",
        ufw_output or firewall_cmd_output or "No firewall status command available",
        "Host firewall enabled and active",
        "high",
        "Enable and configure ufw or firewalld according to business policy.",
        {"cis": "CIS Linux Firewall Configuration", "nist_800_53": "SC-7", "iso_27001": "A.8.20", "soc2": "CC6"},
    )


def check_updates() -> dict:
    apt_code, apt_output = run(["apt-get", "-s", "upgrade"])
    if apt_code == 0:
        pending = "Inst " in apt_output
        current = "Pending package updates found" if pending else "No pending package updates detected"
    else:
        current = "Package update status unavailable"
        pending = True
    return make_check(
        "LINUX-UPDATES-001",
        "patching",
        "Operating system packages are current",
        "WARN" if pending else "PASS",
        current,
        "No pending security or package updates",
        "medium",
        "Review and apply vendor security updates through standard change control.",
        {"cis": "CIS Linux Updates", "nist_800_53": "SI-2", "iso_27001": "A.8.8", "soc2": "CC7"},
    )


def check_disk_encryption() -> dict:
    code, output = run(["lsblk", "-o", "NAME,TYPE,FSTYPE,MOUNTPOINT"])
    encrypted = "crypt" in output.lower()
    return make_check(
        "LINUX-DISK-001",
        "storage",
        "Disk encryption indicator detected",
        "PASS" if encrypted else "WARN",
        output if output else "Unable to inspect block devices",
        "Encrypted root or data volume where required by policy",
        "medium",
        "Confirm encryption requirements and enable LUKS or approved disk encryption for sensitive devices.",
        {"cis": "CIS Storage Encryption", "nist_800_53": "SC-28", "iso_27001": "A.8.24", "gdpr": "Article 32"},
    )


def check_ssh_exposure() -> dict:
    sshd_config = Path("/etc/ssh/sshd_config")
    if not sshd_config.exists():
        current = "OpenSSH server config not found"
        status = "PASS"
    else:
        text = sshd_config.read_text(encoding="utf-8", errors="ignore")
        risky = "PermitRootLogin yes" in text or "PasswordAuthentication yes" in text
        status = "FAIL" if risky else "PASS"
        current = "Risky SSH settings detected" if risky else "No risky SSH settings detected in sshd_config"
    return make_check(
        "LINUX-SSH-001",
        "remote_access",
        "SSH configuration avoids high-risk defaults",
        status,
        current,
        "Root login disabled and password authentication restricted where possible",
        "high",
        "Set PermitRootLogin no and prefer key-based access with approved MFA or access controls.",
        {"cis": "CIS SSH Server Configuration", "nist_800_53": "AC-17", "iso_27001": "A.8.5", "soc2": "CC6"},
    )


def check_local_admins() -> dict:
    code, output = run(["getent", "group", "sudo"])
    members = output.split(":", 3)[-1] if ":" in output else ""
    status = "WARN" if members.strip() else "PASS"
    return make_check(
        "LINUX-USERS-001",
        "identity",
        "Privileged local users are reviewed",
        status,
        members or "No sudo group members detected through getent",
        "Only approved administrators have sudo membership",
        "medium",
        "Review sudo group membership and remove stale or unauthorized administrator accounts.",
        {"cis": "CIS User Accounts and Environment", "nist_800_53": "AC-2", "iso_27001": "A.5.18", "soc2": "CC6"},
    )


def check_logging() -> dict:
    code, output = run(["systemctl", "is-active", "rsyslog"])
    journald_code, journald_output = run(["systemctl", "is-active", "systemd-journald"])
    active = output == "active" or journald_output == "active"
    return make_check(
        "LINUX-LOGGING-001",
        "logging",
        "System logging service is active",
        "PASS" if active else "FAIL",
        f"rsyslog={output}; systemd-journald={journald_output}",
        "At least one approved system logging service active",
        "high",
        "Enable rsyslog or systemd-journald persistence according to organizational logging policy.",
        {"cis": "CIS Logging and Auditing", "nist_800_53": "AU-2", "iso_27001": "A.8.15", "soc2": "CC7"},
    )


def check_open_services() -> dict:
    code, output = run(["ss", "-tulpen"])
    if code != 0:
        code, output = run(["netstat", "-tulpen"])
    risky_terms = [":23 ", ":21 ", ":5900 "]
    risky = any(term in output for term in risky_terms)
    return make_check(
        "LINUX-SERVICES-001",
        "services",
        "Open listening services are reviewed",
        "FAIL" if risky else "WARN",
        output[:2000] if output else "Unable to list listening services",
        "Only approved business services are listening",
        "medium",
        "Review listening services and disable unneeded network daemons through change control.",
        {"cis": "CIS Services", "nist_800_53": "CM-7", "iso_27001": "A.8.9", "soc2": "CC6"},
    )


def make_check(
    check_id: str,
    category: str,
    name: str,
    status: str,
    current_value: str,
    recommended_value: str,
    severity: str,
    remediation: str,
    compliance_mappings: dict,
) -> dict:
    return {
        "check_id": check_id,
        "category": category,
        "name": name,
        "status": status,
        "current_value": current_value,
        "recommended_value": recommended_value,
        "severity": severity,
        "evidence": current_value,
        "remediation": remediation,
        "compliance_mappings": compliance_mappings,
    }


def collect() -> dict:
    return {
        "scan_id": f"linux-{uuid.uuid4().hex[:12]}",
        "client_name": "Local Assessment",
        "hostname": socket.gethostname(),
        "os_family": "linux",
        "os_version": platform.platform(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "collector": {
            "name": "linux-local-readonly",
            "requires_root": False,
            "is_root": os.geteuid() == 0 if hasattr(os, "geteuid") else False,
            "mode": "audit-only",
        },
        "checks": [
            check_firewall(),
            check_updates(),
            check_disk_encryption(),
            check_ssh_exposure(),
            check_local_admins(),
            check_logging(),
            check_open_services(),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Linux hardening collector")
    parser.add_argument("--output", default="linux_audit.json", help="Output JSON path")
    args = parser.parse_args()
    Path(args.output).write_text(json.dumps(collect(), indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

