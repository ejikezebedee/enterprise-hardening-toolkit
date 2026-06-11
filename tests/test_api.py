import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import DEFAULT_DB_PATH, IMPORTS_DIR
from app.db.database import init_db
from app.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        if DEFAULT_DB_PATH.exists():
            DEFAULT_DB_PATH.unlink()
        init_db(DEFAULT_DB_PATH)
        IMPORTS_DIR.mkdir(exist_ok=True)

    def tearDown(self):
        for path in IMPORTS_DIR.glob("test_*.json"):
            path.unlink()

    def test_health_endpoint(self):
        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "audit-only")

    def test_baselines_endpoint(self):
        client = TestClient(app)
        response = client.get("/baselines")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json())

    def test_clients_endpoint(self):
        client = TestClient(app)
        response = client.post("/clients", json={"name": "API Test Client"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["client_id"], 0)

    def test_devices_endpoint(self):
        client = TestClient(app)
        client_id = client.post("/clients", json={"name": "Device Test Client"}).json()["client_id"]
        response = client.post(
            "/devices",
            json={
                "client_id": client_id,
                "hostname": "api-test-host",
                "os_family": "linux",
                "os_version": "22.04",
                "role": "workstation",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["device_id"], 0)

    def test_audits_import_endpoint_accepts_sample(self):
        client = TestClient(app)
        response = client.post("/audits/import", json={"path": "samples/windows_audit_sample.json"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["audit_id"], 0)

    def test_reports_endpoint_generates_report(self):
        client = TestClient(app)
        audit_id = client.post("/audits/import", json={"path": "samples/windows_audit_sample.json"}).json()["audit_id"]
        response = client.post(f"/reports/{audit_id}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Path(response.json()["report_path"]).exists())

    def test_invalid_audit_json_rejected(self):
        invalid_path = IMPORTS_DIR / "test_invalid_audit.json"
        invalid_path.write_text('{"scan_id": "bad", "checks": []}', encoding="utf-8")
        client = TestClient(app)
        response = client.post("/audits/import", json={"path": "imports/test_invalid_audit.json"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("checks must be a non-empty list", response.json()["detail"])

    def test_path_traversal_import_rejected(self):
        client = TestClient(app)
        response = client.post("/audits/import", json={"path": "../enterprise-hardening-toolkit/README.md"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("restricted to approved directories", response.json()["detail"])

    def test_missing_audit_report_returns_safe_error(self):
        client = TestClient(app)
        response = client.post("/reports/999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Audit not found: 999999")


if __name__ == "__main__":
    unittest.main()
