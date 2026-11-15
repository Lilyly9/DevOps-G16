import tempfile, unittest
from pathlib import Path
from lab import fixture, scan, patch, validate

class StudentE10B(unittest.TestCase):
    def test_build_failure_keeps_original_makefile(self):
        # 候选可应用，但 main.c 故意写成非法 C -> 编译失败 -> 拒绝且源 Makefile 逐字节不变。
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'sample'
            fixture(p)
            diff, plan = patch(p, scan(p))
            candidate = root / 'candidate.patch'
            candidate.write_text(diff)
            before = (p / 'Makefile').read_bytes()
            (p / 'main.c').write_text('this is invalid C;\n')
            result = validate(p, candidate, root / 'validation')
            self.assertTrue(result['checks']['patch_applies'])
            self.assertFalse(result['checks'].get('build', False))
            self.assertIn('COMMAND_FAILED', result['error'])
            self.assertFalse(result['accepted'])
            self.assertTrue(result['rollback'])
            self.assertTrue(result['source_unchanged'])
            self.assertEqual((p / 'Makefile').read_bytes(), before)

if __name__ == '__main__':
    unittest.main()
