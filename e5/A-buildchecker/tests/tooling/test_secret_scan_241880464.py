"""A3 black-box regression checks: legacy bytes must not disable secret detection."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCANNER = Path(__file__).resolve().parents[2] / "scripts/secret_scan.py"


class LegacyHistoryTests(unittest.TestCase):
    def scan_commit(self, content):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args):
                subprocess.run(["git", "-C", folder, *args], check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            git("init", "-q")
            (root / "legacy.log").write_bytes(content)
            git("add", "legacy.log")
            git("-c", "user.name=A3-test", "-c", "user.email=a3@example.invalid",
                "commit", "-qm", "legacy encoding regression fixture")
            return subprocess.run([sys.executable, str(SCANNER), folder, "--history"],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_legacy_history_without_secret_finishes(self):
        result = self.scan_commit(b"legacy header: \xb4\xfa\xc2\xeb\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("UnicodeDecodeError", result.stderr)

    def test_secret_after_legacy_bytes_is_still_rejected_and_masked(self):
        token = "gh" + "p_" + "A" * 36
        result = self.scan_commit(b"legacy: \xb4\xfa\n" + token.encode() + b"\n")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("git-history:", result.stdout)
        self.assertIn("GitHub Token", result.stdout)
        self.assertNotIn(token, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
