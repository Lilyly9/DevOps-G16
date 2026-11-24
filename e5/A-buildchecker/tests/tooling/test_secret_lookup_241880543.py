"""B2 scanner regressions, exercised against both E7 implementations."""
import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[4]
class LookupTests(unittest.TestCase):
    def test_lookups_and_literal_secrets(self):
        for side in ('A-buildchecker', 'B-draft'):
            spec = importlib.util.spec_from_file_location('scanner', ROOT/'e5'/side/'scripts/secret_scan.py')
            scanner = importlib.util.module_from_spec(spec); spec.loader.exec_module(scanner)
            assignment = 'tok' + 'en = '
            for prefix in ('', '+', '-'):
                with self.subTest(side=side, prefix=prefix):
                    self.assertEqual(scanner.scan_text(prefix+assignment+"credential.get('password')", 'fixture'), [])
                    for rhs in (repr('Z'*24), "credential.get('password', '"+'Z'*24+"')", repr("credential.get('password')"), "credential.get('"+'Z'*24+"')"):
                        self.assertTrue(scanner.scan_text(prefix+assignment+rhs, 'fixture'), rhs)
                    # The strong token detector must still fire, even in a lookup.
                    strong = 'gh' + 'p_' + 'A'*36
                    self.assertTrue(scanner.scan_text(assignment+"credential.get('"+strong+"')", 'fixture'))
if __name__ == '__main__': unittest.main()
