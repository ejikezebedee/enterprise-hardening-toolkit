#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import DEFAULT_DB_PATH, REPORTS_DIR
from app.db.database import init_db
from app.services.audit_importer import import_audit_file
from app.services.reports import generate_markdown_report


def main() -> None:
    init_db(DEFAULT_DB_PATH)
    result = import_audit_file(Path("samples/windows_audit_sample.json"))
    report_path = generate_markdown_report(result["audit_id"], REPORTS_DIR)
    print(report_path)


if __name__ == "__main__":
    main()
