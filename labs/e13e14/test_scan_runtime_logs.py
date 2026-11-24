"""A1 (241880485) E13-C6 regression: the runtime log scanner must stay usable.

Pins the exit codes the E13 gate relies on (0 clean, 1 hit, 2 incomplete),
that a hit never prints the full secret, and that A2's pointer-assignment
exception keeps ordinary parser code from being reported as a credential.
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_runtime_logs

# Built at runtime on purpose: a literal key-shaped string in a tracked file
# would be reported by labs/e11e12/environment/scripts/secret_scan.py, which
# scans tracked sources and the full history in the E7/E13 gates.
FAKE_KEY = "sk-" + "demo" + "1234567890abcdefghijk"


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_scan(self, *paths):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = scan_runtime_logs.main([str(path) for path in paths])
        return code, out.getvalue(), err.getvalue()

    def test_clean_log_passes(self):
        log = self.root / "clean.log"
        log.write_text("stage=recheck status=SUCCEEDED missing=0\n", encoding="utf-8")
        code, out, _ = self.run_scan(log)
        self.assertEqual(code, 0)
        self.assertIn("hits=0", out)

    def test_fake_key_is_a_hit_and_is_masked(self):
        log = self.root / "probe.log"
        log.write_text(f'api_key = "{FAKE_KEY}"\n', encoding="utf-8")
        code, out, _ = self.run_scan(log)
        self.assertEqual(code, 1)
        self.assertIn("FOUND", out)
        self.assertNotIn(FAKE_KEY, out)

    def test_pointer_assignment_is_not_a_credential(self):
        source = self.root / "parser.c"
        source.write_text('char *token = &buffer[0];\n', encoding="utf-8")
        code, _, _ = self.run_scan(source)
        self.assertEqual(code, 0)

    def test_placeholder_assignment_is_ignored(self):
        source = self.root / "example.env"
        source.write_text('API_KEY=replace-with-your-own-key\n', encoding="utf-8")
        code, _, _ = self.run_scan(source)
        self.assertEqual(code, 0)

    def test_missing_path_is_incomplete(self):
        code, _, err = self.run_scan(self.root / "absent")
        self.assertEqual(code, 2)
        self.assertIn("missing path", err)

    def test_directory_without_text_is_incomplete(self):
        binary = self.root / "blob.bin"
        binary.write_bytes(b"\x00\x01\x02binary")
        code, _, _ = self.run_scan(binary)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
