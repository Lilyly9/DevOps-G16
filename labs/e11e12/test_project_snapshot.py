import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline import Failure, project_subdir, snapshot


class ProjectSnapshotTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'posix', 'The pipeline runs on the Linux course host')
    def test_nested_checkout_keeps_commit_and_excludes_sibling_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            repo = root / 'source'
            repo.mkdir()

            def git(*args, cwd=repo):
                return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()

            git('init', '-q')
            git('config', 'user.name', 'E12 test')
            git('config', 'user.email', 'e12-test@example.invalid')
            subdir = repo / 'projects/tool'
            subdir.mkdir(parents=True)
            (subdir / 'source.c').write_text('base\n', encoding='utf-8')
            (repo / 'sibling.txt').write_text('not a build input\n', encoding='utf-8')
            git('add', '.')
            git('commit', '-qm', 'base')
            base = git('rev-parse', 'HEAD')
            (subdir / 'source.c').write_text('target\n', encoding='utf-8')
            git('commit', '-qam', 'target')
            checkout = root / 'base'
            sha, project = snapshot(repo, base, checkout, root / 'logs', 'projects/tool')
            self.assertEqual((sha, git('rev-parse', 'HEAD', cwd=project)), (base, base))
            self.assertEqual((project / 'source.c').read_text(encoding='utf-8'), 'base\n')
            self.assertFalse((checkout / 'sibling.txt').exists())

    def test_project_path_rejects_traversal_and_pattern_syntax(self):
        for value in ('../tool', 'projects/../tool', '/projects/tool', 'projects//tool',
                      'projects/[a]', 'projects/.git', 'projects\\tool'):
            with self.subTest(value=value), self.assertRaises(Failure) as exc:
                project_subdir(value)
            self.assertEqual(exc.exception.code, 'INVALID_PROJECT_PATH')


if __name__ == '__main__':
    unittest.main()
