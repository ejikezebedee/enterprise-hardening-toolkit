import tempfile
import unittest
from pathlib import Path

from app.db.database import init_db, list_rows
from app.services.audit_importer import import_audit_file
from app.services.reports import generate_markdown_report


class ImportReportTests(unittest.TestCase):
    def test_import_windows_sample_and_generate_report(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            db_path = tmp_path / "test.sqlite3"
            init_db(db_path)
            result = import_audit_file(Path("samples/windows_audit_sample.json"), db_path)
            self.assertGreater(result["audit_id"], 0)
            self.assertLess(result["score"], 100)
            self.assertTrue(list_rows("findings", db_path))
            report_path = generate_markdown_report(result["audit_id"], tmp_path, db_path)
            self.assertTrue(report_path.exists())
            self.assertIn("Enterprise Computer Hardening Report", report_path.read_text(encoding="utf-8"))

    def test_reimport_same_scan_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "test.sqlite3"
            init_db(db_path)
            first = import_audit_file(Path("samples/windows_audit_sample.json"), db_path)
            second = import_audit_file(Path("samples/windows_audit_sample.json"), db_path)
            self.assertEqual(first["audit_id"], second["audit_id"])
            self.assertEqual(len(list_rows("audits", db_path)), 1)


if __name__ == "__main__":
    unittest.main()
