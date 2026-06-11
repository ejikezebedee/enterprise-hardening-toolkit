import unittest

from app.core.audit_schema import validate_audit_payload
from app.services.audit_importer import load_audit_json


class SchemaTests(unittest.TestCase):
    def test_windows_sample_schema_valid(self):
        payload = load_audit_json("samples/windows_audit_sample.json")
        self.assertEqual(validate_audit_payload(payload), [])

    def test_invalid_status_rejected(self):
        payload = load_audit_json("samples/windows_audit_sample.json")
        payload["checks"][0]["status"] = "BROKEN"
        errors = validate_audit_payload(payload)
        self.assertTrue(errors)

    def test_invalid_severity_rejected(self):
        payload = load_audit_json("samples/windows_audit_sample.json")
        payload["checks"][0]["severity"] = "catastrophic"
        errors = validate_audit_payload(payload)
        self.assertTrue(errors)
        self.assertTrue(any("invalid severity" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
