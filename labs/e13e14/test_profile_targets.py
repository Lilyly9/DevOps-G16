"""E13-E14: orchestrate.snapshot/read_profile accept real projects via e12-profile.json."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orchestrate import read_profile, snapshot

GIT_ENV = {'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@example.invalid',
           'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@example.invalid'}


def git(cwd, *args):
    subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, **GIT_ENV})


PROFILE = {'schema_version': 'e12-project-1',
           'targets': {'eta_cli.o': 'eta_cli.c', 'estimate.o': 'estimate.c'}}


class SnapshotProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def make_repo(self, files):
        repo = self.tmp / 'repo'
        repo.mkdir()
        git(repo, 'init', '-q')
        for name, content in files.items():
            (repo / name).write_text(content, encoding='utf-8')
        git(repo, 'add', '.')
        git(repo, 'commit', '-qm', 'init')
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo,
                              capture_output=True, text=True).stdout.strip()
        return repo, head

    def test_profile_project_accepted(self):
        repo, head = self.make_repo({'eta_cli.c': 'int main(void){return 0;}\n',
                                     'estimate.c': '',
                                     'e12-profile.json': json.dumps(PROFILE)})
        target = self.tmp / 'target'
        self.assertEqual(snapshot(repo, head, target, self.tmp / 'logs'), head)
        self.assertEqual(sorted(read_profile(target)['targets']),
                         ['estimate.o', 'eta_cli.o'])

    def test_profile_missing_source_rejected(self):
        broken = dict(PROFILE, targets={'eta_cli.o': 'no_such.c'})
        repo, head = self.make_repo({'eta_cli.c': '', 'e12-profile.json': json.dumps(broken)})
        with self.assertRaises(ValueError) as ctx:
            snapshot(repo, head, self.tmp / 'target', self.tmp / 'logs')
        self.assertIn('Profile sources missing', str(ctx.exception))

    def test_invalid_profile_rejected(self):
        repo, head = self.make_repo({'eta_cli.c': '',
                                     'e12-profile.json': json.dumps({'schema_version': 'other'})})
        with self.assertRaises(ValueError) as ctx:
            snapshot(repo, head, self.tmp / 'target', self.tmp / 'logs')
        self.assertIn('Invalid e12-profile.json', str(ctx.exception))

    def test_teaching_project_accepted(self):
        repo, head = self.make_repo({'main.c': '', 'helper.c': '', 'config.h': ''})
        self.assertEqual(snapshot(repo, head, self.tmp / 'target', self.tmp / 'logs'), head)

    def test_teaching_project_without_config_rejected(self):
        repo, head = self.make_repo({'main.c': '', 'helper.c': ''})
        with self.assertRaises(ValueError) as ctx:
            snapshot(repo, head, self.tmp / 'target', self.tmp / 'logs')
        self.assertIn('Unsupported teaching project profile', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
