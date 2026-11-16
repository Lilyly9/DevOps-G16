"""B3 241880597 extension tests: consumer-side rejection of the A-report handoff.

A3's test_student_241880464.py covers the producer side (export_report) and the
happy-path download against a real loopback server. B3 owns the *consumer* side:
a consumer on the far end must not trust the producer's bytes, so these tests
replay the two HTTP responses (transfer manifest + incremental-check bytes) with
scriptable corruption and assert that download_report rejects each mismatch.

Covered consumer-side rejections of report_exchange.download_report:
  - OUTPUT_EXISTS            (target transfer directory already used)
  - SCHEMA_MISMATCH          (manifest schema_version is not e11e12-transfer-1)
  - REPORT_IDENTITY_MISMATCH (manifest job_id / commit / report.uri mismatch)
  - ARTIFACT_TYPE_MISMATCH   (wrong kind or download_path)
  - ARTIFACT_HASH_MISMATCH   (manifest sha256 vs header vs actual bytes/size)
  - STALE_REPORT             (inner data.commit expired while outer commit matches)
  - REPORT_IDENTITY_MISMATCH (report trace_id differs from manifest)
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline import Failure
import report_exchange

JOB = 'job-b3-consumer'
TRACE = 'trace-b3-consumer'
TARGET = 'a' * 40


def build_report(job=JOB, trace=TRACE, target=TARGET):
    return {
        'schema_version': 'e11e12-1',
        'kind': 'incremental-check',
        'status': 'SUCCEEDED',
        'commit': target,
        'job_id': job,
        'trace_id': trace,
        'data': {'commit': target, 'findings': [
            {'type': 'MISSING', 'target': 'main.o', 'dependency': 'extra.h'}]},
        'artifacts': [],
    }


def build_manifest(job=JOB, trace=TRACE, target=TARGET, report_bytes=b''):
    return {
        'schema_version': 'e11e12-transfer-1',
        'kind': 'incremental-check',
        'job_id': job,
        'trace_id': trace,
        'commit': target,
        'report': {
            'uri': f'artifact://{job}/incremental-check.json',
            'sha256': hashlib.sha256(report_bytes).hexdigest(),
            'bytes': len(report_bytes),
        },
        'download_path': f'/v1/jobs/{job}/files/incremental-check.json',
    }


class FakeResponse:
    def __init__(self, data, headers=None):
        self._data = data
        self.headers = headers if headers is not None else {}

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeHTTP:
    """Replay the two urlopen calls download_report makes, with scriptable inputs."""

    def __init__(self, manifest, report_bytes, report_headers=None):
        self.manifest_bytes = json.dumps(manifest).encode()
        self.report_bytes = report_bytes
        self.report_headers = report_headers if report_headers is not None else {}

    def __call__(self, url, timeout=None):
        if 'reports/incremental-check' in url:
            return FakeResponse(self.manifest_bytes)
        headers = dict(self.report_headers)
        headers.setdefault('X-Content-SHA256',
                           hashlib.sha256(self.report_bytes).hexdigest())
        return FakeResponse(self.report_bytes, headers)


class B3ConsumerRejection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.report = build_report()
        self.report_bytes = json.dumps(self.report).encode()
        self.manifest = build_manifest(report_bytes=self.report_bytes)
        self.report_headers = {}

    def download(self, out_name='received'):
        with patch.object(report_exchange, 'urlopen',
                          FakeHTTP(self.manifest, self.report_bytes, self.report_headers)):
            return report_exchange.download_report(
                'http://127.0.0.1:18086', JOB, TARGET, self.root / out_name)

    def expect_code(self, code, out_name='received'):
        with self.assertRaises(Failure) as caught:
            self.download(out_name)
        self.assertEqual(caught.exception.code, code)

    def test_accept_current_report_and_three_hashes(self):
        report = self.download()
        self.assertEqual(report, self.report)
        self.assertEqual((self.root / 'received/incremental-check.json').read_bytes(),
                         self.report_bytes)
        verification = json.loads((self.root / 'received/verification.json').read_text())
        self.assertTrue(verification['passed'])
        self.assertEqual(verification['sha256'],
                         hashlib.sha256(self.report_bytes).hexdigest())
        self.assertEqual(verification['uri'], f'artifact://{JOB}/incremental-check.json')

    def test_reject_output_exists(self):
        (self.root / 'received').mkdir()
        self.expect_code('OUTPUT_EXISTS')

    def test_reject_manifest_schema(self):
        self.manifest['schema_version'] = 'e11e12-transfer-old'
        self.expect_code('SCHEMA_MISMATCH')

    def test_reject_manifest_job_mismatch(self):
        self.manifest['job_id'] = 'job-other-task'
        self.expect_code('REPORT_IDENTITY_MISMATCH')

    def test_reject_manifest_commit_mismatch(self):
        self.manifest['commit'] = 'b' * 40
        self.expect_code('REPORT_IDENTITY_MISMATCH')

    def test_reject_wrong_kind(self):
        self.manifest['kind'] = 'full-check'
        self.expect_code('ARTIFACT_TYPE_MISMATCH')

    def test_reject_wrong_download_path(self):
        self.manifest['download_path'] = '/v1/jobs/other/files/incremental-check.json'
        self.expect_code('ARTIFACT_TYPE_MISMATCH')

    def test_reject_wrong_report_uri(self):
        self.manifest['report']['uri'] = 'artifact://job-other/incremental-check.json'
        self.expect_code('REPORT_IDENTITY_MISMATCH')

    def test_reject_manifest_sha_mismatch(self):
        self.manifest['report']['sha256'] = '0' * 64
        self.expect_code('ARTIFACT_HASH_MISMATCH')

    def test_reject_header_sha_mismatch(self):
        self.report_headers = {'X-Content-SHA256': '1' * 64}
        self.expect_code('ARTIFACT_HASH_MISMATCH')

    def test_reject_byte_size_mismatch(self):
        self.manifest['report']['bytes'] = len(self.report_bytes) + 1
        self.expect_code('ARTIFACT_HASH_MISMATCH')

    def test_reject_inner_commit_expired(self):
        self.report['data']['commit'] = 'b' * 40
        self.report_bytes = json.dumps(self.report).encode()
        self.manifest = build_manifest(report_bytes=self.report_bytes)
        self.expect_code('STALE_REPORT')

    def test_reject_report_trace_mismatch(self):
        self.report['trace_id'] = 'trace-other-task'
        self.report_bytes = json.dumps(self.report).encode()
        self.manifest = build_manifest(report_bytes=self.report_bytes)
        self.expect_code('REPORT_IDENTITY_MISMATCH')


if __name__ == '__main__':
    unittest.main()
