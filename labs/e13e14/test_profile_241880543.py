"""E14 must preserve real project Git snapshots and reject unsafe selection."""
import hashlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('e14_orchestrate', ROOT/'labs/e13e14/orchestrate.py')
e14 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e14)
class RealProjectSnapshots(unittest.TestCase):
    def test_real_profile_preserves_source_and_snapshot_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);repo=root/'repo'
            shutil.copytree(ROOT/'projects/transfer-eta',repo)
            settings=(repo/'e12-profile.json').read_bytes()
            (repo/'e12-profile.json').unlink()
            def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.STDOUT,text=True).strip()
            git('init','-q');git('add','.')
            git('-c','user.name=B2-test','-c','user.email=b2@example.invalid','commit','-qm','project')
            base=git('rev-parse','HEAD')
            (repo/'e12-profile.json').write_bytes(settings);git('add','.')
            git('-c','user.name=B2-test','-c','user.email=b2@example.invalid','commit','-qm','target profile')
            sha=git('rev-parse','HEAD')
            before=hashlib.sha256((repo/'Makefile').read_bytes()).hexdigest()
            actual,project=e14.snapshot(repo,sha,root/'selected',root/'logs',profile=True)
            self.assertEqual(actual,sha)
            self.assertTrue((project/'e12-profile.json').is_file())
            self.assertEqual(hashlib.sha256((project/'Makefile').read_bytes()).hexdigest(),before)
            self.assertEqual(git('status','--porcelain'),'')
            _,baseline=e14.snapshot(repo,base,root/'baseline',root/'logs',profile=True)
            self.assertFalse((baseline/'e12-profile.json').exists())
            e14.load_profile(project).validate_sources(baseline)
            with self.assertRaisesRegex(ValueError,'Unsupported'):
                e14.snapshot(repo,sha,root/'unsupported',root/'logs')
    def test_project_path_cannot_escape_snapshot(self):
        for value in ('../projects','/projects','projects/../x','projects//x'):
            with self.subTest(value=value),self.assertRaises(ValueError):e14.project_subdir(value)
if __name__=='__main__':unittest.main()
