import subprocess
import sys
import unittest


class ReleaseVerificationTests(unittest.TestCase):
    def test_release_verification_script_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/verify_release.py"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
