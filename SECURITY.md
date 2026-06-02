# Security Policy

## Product Boundary

This toolkit is defensive-only and intended for authorized hardening review, internal audit, learning, and compliance support.

It must not:

- exploit vulnerabilities
- bypass authentication
- collect passwords, tokens, SSH keys, or private certificates
- exfiltrate files
- disable security controls silently
- run destructive commands
- perform unauthorized network scanning
- modify systems without explicit administrator approval

## Data Handling

The MVP stores audit data locally in SQLite. Cloud export is not implemented.

## Reporting Sensitive Data

Collectors should record configuration evidence, not secrets. If a sensitive value is discovered, the collector should report that the value exists without storing the value.

## Deployment

The MVP is intended for localhost or internal use. Public deployment requires authentication, TLS, logging, access control, and hardening work outside this MVP scope.

## Reporting Vulnerabilities

Please report security issues privately before public disclosure.

When reporting, include:

- affected version or commit
- steps to reproduce
- expected and actual behavior
- security impact
- suggested fix, if known

Do not include secrets, private customer data, or unauthorized system data in reports.

## Responsible Use

Contributors must keep this project defensive. Pull requests that add exploitation, stealth, persistence, credential harvesting, unauthorized scanning, or destructive behavior will not be accepted.
