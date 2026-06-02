import unittest

from app.services.baselines import build_control_index, load_all_baselines


class BaselineTests(unittest.TestCase):
    def test_baselines_load(self):
        baselines = load_all_baselines()
        self.assertTrue(baselines)
        self.assertTrue(any(item["os_family"] == "linux" for item in baselines))

    def test_control_index_contains_linux_firewall(self):
        index = build_control_index()
        self.assertIn("LINUX-FIREWALL-001", index)


if __name__ == "__main__":
    unittest.main()
