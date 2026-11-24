"""C6 exit codes and redaction at the scanner CLI boundary."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RuntimeScanTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def scan(self, *paths):
        script = Path(__file__).with_name("scan_runtime_logs.py")
        return subprocess.run([sys.executable, script, *paths], capture_output=True, text=True)

    def test_hit_redaction_and_rescan(self):
        log = self.root / "draft.log"
        fake = "sk-" + "C6fixture" * 4
        log.write_text(fake + "\n")
        hit = self.scan(log)
        self.assertEqual(hit.returncode, 1)
        self.assertIn("hits=1", hit.stdout)
        self.assertNotIn(fake, hit.stdout + hit.stderr)
        log.write_text("credential removed\n")
        self.assertEqual(self.scan(log).returncode, 0)

    def test_one_valid_log_cannot_cover_an_unscanned_service(self):
        valid = self.root / "draft.log"
        valid.write_text("healthy\n")
        other = self.root / "mdfixer"
        other.mkdir()
        for content in (b"", b"\x00binary"):
            (other / "role.log").write_bytes(content)
            self.assertEqual(self.scan(valid, other).returncode, 2)
        self.assertEqual(self.scan(valid, self.root / "missing.log").returncode, 2)
