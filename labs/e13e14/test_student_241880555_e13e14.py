"""B1 241880555 E13-E14 extension tests: A-to-B handoff and fixed-report SHA gate.

The CI runner has no Docker socket, so draft.autobuild.auto_build is patched to
raise at the DRAFT boundary. What is verified without Docker:

1. A legal A report converted by handoff_a_to_b.make_handoff, wrapped in a B
   request with the matching fixed_report_sha256, passes the transfer-SHA gate,
   the envelope identity checks, snapshot and the default-profile check, and
   stops exactly at the patched DRAFT boundary (EXECUTION_FAILED/CI_NO_DOCKER).
2. If the report bytes change during transfer but the old SHA is kept, the
   pipeline must reject with ARTIFACT_HASH_MISMATCH before any snapshot runs.
3. A malformed fixed_report_sha256 value must be rejected as ARTIFACT_HASH_MISMATCH.
4. A missing report file must be rejected as ARTIFACT_HASH_MISMATCH.

The server-side C4 timeout run (work/e13-c4-241880555-01: outer FAILED/DRAFT_FAILED,
inner draft-build TIMED_OUT, no leftover docker build client or verify container)
is the real-evidence counterpart of the timeout path; it cannot run in CI.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO_ROOT / 'labs/e11e12'), str(Path(__file__).resolve().parent)]

import pipeline
from handoff_a_to_b import make_handoff


def artifact(path, root, job_id):
    data = path.read_bytes()
    return {
        "uri": f"artifact://{job_id}/{path.relative_to(root).as_posix()}",
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def make_git_repo(root):
    repo = root / 'repo'
    repo.mkdir()
    (repo / 'main.c').write_text(
        '#include <stdio.h>\n#include "config.h"\nint helper(void);\n'
        'int main(void){printf("%d\\n", VALUE);return 0;}\n', encoding='utf-8')
    (repo / 'helper.c').write_text('int helper(void){return 0;}\n', encoding='utf-8')
    (repo / 'config.h').write_text('#define VALUE 1\n', encoding='utf-8')
    (repo / 'Makefile').write_text(
        'app: main.o helper.o\n\tgcc main.o helper.o -o app\n'
        'main.o: main.c config.h\n\tgcc -O0 -c main.c -o main.o\n'
        'helper.o: helper.c\n\tgcc -O0 -c helper.c -o helper.o\n'
        '.PHONY: clean\nclean:\n\trm -f main.o helper.o app\n', encoding='utf-8')
    (repo / 'Dockerfile.broken').write_text(
        'FROM python:3.13-slim\nWORKDIR /work\nCOPY Makefile config.h helper.c main.c ./\n'
        'RUN make app\nCMD ["./app"]\n', encoding='utf-8')

    def git(*argv):
        subprocess.run(['git', '-C', str(repo), *argv], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    git('init', '-q', '-b', 'main')
    git('config', 'user.name', 'handoff-tests')
    git('config', 'user.email', 'handoff-tests@localhost')
    git('add', '-A')
    git('commit', '-q', '-m', 'C0 handoff test fixture')
    head = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                          check=True, capture_output=True, text=True).stdout.strip()
    return repo, head


def make_a_report(root, target_sha):
    """Build a minimal successful E11-A result tree, then run make_handoff on it."""
    job = 'job-handoff-fixture'
    trace = 'trace-handoff-fixture'
    inner = root / 'incremental-report.json'
    inner.write_text('{"findings": []}\n', encoding='utf-8')
    stage = {
        'schema_version': 'e11e12-1', 'kind': 'incremental-check', 'status': 'SUCCEEDED',
        'commit': target_sha, 'job_id': job, 'trace_id': trace,
        'data': {'commit': target_sha, 'findings': []},
        'artifacts': [artifact(inner, root, job)],
    }
    stage_path = root / 'incremental-check.json'
    stage_path.write_text(json.dumps(stage) + '\n', encoding='utf-8')
    result = {
        'schema_version': 'e11e12-1', 'status': 'SUCCEEDED', 'target_commit': target_sha,
        'job_id': job, 'trace_id': trace,
        'stages': [{'name': 'incremental-check',
                    'artifact': artifact(stage_path, root, job)}],
    }
    result_path = root / 'result.json'
    result_path.write_text(json.dumps(result) + '\n', encoding='utf-8')
    return make_handoff(result_path, target_sha)


class B1HandoffShaGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.head = make_git_repo(self.root)
        self.envelope = make_a_report(self.root, self.head)
        self.envelope_path = self.root / 'fixed-md-envelope.json'
        self.envelope_path.write_text(json.dumps(self.envelope) + '\n', encoding='utf-8')

    def request(self, sha256=None):
        r = {'mode': 'e11-b', 'repo': str(self.repo), 'base': self.head,
             'target': self.head, 'candidate': str(self.repo / 'Dockerfile.broken'),
             'fixed_report': str(self.envelope_path),
             'fixed_report_sha256': sha256,
             'expected_output': '1', 'build_timeout': 600}
        if sha256 is None:
            del r['fixed_report_sha256']
        return r

    def run_pipeline(self, request, out_name):
        with patch('draft.autobuild.auto_build',
                   side_effect=ValueError('CI_NO_DOCKER')):
            return pipeline.execute(request, self.root / out_name)

    def test_handoff_envelope_with_matching_sha_reaches_draft_boundary(self):
        sha = hashlib.sha256(self.envelope_path.read_bytes()).hexdigest()
        result = self.run_pipeline(self.request(sha), 'out-ok')
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['error']['code'], 'EXECUTION_FAILED')
        self.assertIn('CI_NO_DOCKER', result['error']['message'])
        self.assertTrue((self.root / 'out-ok' / 'request.json').is_file())

    def test_tampered_report_with_old_sha_is_rejected(self):
        self.envelope_path.write_text(
            json.dumps(self.envelope) + '\n', encoding='utf-8')
        with self.envelope_path.open('a', encoding='utf-8') as f:
            f.write(' ')
        sha = hashlib.sha256(json.dumps(self.envelope).encode('utf-8')).hexdigest()
        result = self.run_pipeline(self.request(sha), 'out-tamper')
        self.assertEqual(result['error']['code'], 'ARTIFACT_HASH_MISMATCH')
        self.assertIn('changed during transfer', result['error']['message'])
        self.assertFalse((self.root / 'out-tamper' / 'base-project').exists())

    def test_malformed_sha_is_rejected(self):
        result = self.run_pipeline(self.request('not-a-sha'), 'out-badsha')
        self.assertEqual(result['error']['code'], 'ARTIFACT_HASH_MISMATCH')
        self.assertIn('lowercase SHA-256', result['error']['message'])

    def test_missing_report_file_is_rejected(self):
        r = self.request(hashlib.sha256(b'x').hexdigest())
        r['fixed_report'] = str(self.root / 'no-such-report.json')
        with patch('draft.autobuild.auto_build', side_effect=ValueError('CI_NO_DOCKER')):
            result = pipeline.execute(r, self.root / 'out-missing')
        self.assertEqual(result['error']['code'], 'ARTIFACT_HASH_MISMATCH')
        self.assertIn('missing', result['error']['message'])


if __name__ == '__main__':
    unittest.main()
