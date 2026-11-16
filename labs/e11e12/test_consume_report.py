import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from consume_report import consume, read_transfer
from pipeline import Failure, save


SOURCE_JOB = 'job-' + '1' * 32
SOURCE_TRACE = 'trace-' + '2' * 32
TARGET = 'a' * 40


class OfflineConsumptionTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.transfer = self.root / 'download'
        self.transfer.mkdir()
        self.report = {
            'schema_version': 'e11e12-1', 'kind': 'incremental-check', 'status': 'SUCCEEDED',
            'job_id': SOURCE_JOB, 'trace_id': SOURCE_TRACE, 'commit': TARGET,
            'data': {'commit': TARGET, 'findings': []},
        }

    def stage_inputs(self):
        raw = json.dumps(self.report).encode('utf-8')
        digest = hashlib.sha256(raw).hexdigest()
        manifest = {
            'schema_version': 'e11e12-transfer-1', 'kind': 'incremental-check',
            'job_id': SOURCE_JOB, 'trace_id': SOURCE_TRACE, 'commit': TARGET,
            'download_path': f'/v1/jobs/{SOURCE_JOB}/files/incremental-check.json',
            'report': {'uri': f'artifact://{SOURCE_JOB}/incremental-check.json',
                       'sha256': digest, 'bytes': len(raw)},
        }
        (self.transfer / 'incremental-check.json').write_bytes(raw)
        save(self.transfer / 'transfer-manifest.json', manifest)
        save(self.transfer / 'response-headers.json', {'x-content-sha256': digest})
        return manifest

    def test_preserves_exact_http_bytes(self):
        original = self.stage_inputs()
        copy = self.root / 'transfer-copy'
        manifest, report = read_transfer(self.transfer, copy, TARGET)
        self.assertEqual(manifest, original)
        self.assertEqual(report, self.report)
        for source in self.transfer.iterdir():
            self.assertEqual((copy / source.name).read_bytes(), source.read_bytes())

    def test_local_report_hash_mismatch_fails_before_checkout_or_draft(self):
        self.stage_inputs()
        raw = self.transfer / 'incremental-check.json'
        raw.write_bytes(raw.read_bytes() + b'\n')
        out = self.root / 'out'
        with patch('consume_report.snapshot') as snapshot, patch('consume_report.auto_build') as draft:
            result = consume({'target': TARGET}, self.transfer, out)
        snapshot.assert_not_called()
        draft.assert_not_called()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['error']['code'], 'ARTIFACT_HASH_MISMATCH')
        self.assertTrue((out / 'result.json').exists())
        self.assertFalse((out / 'candidate.patch').exists())

    def test_consumer_rejects_inner_stale_commit_with_valid_hashes(self):
        self.report['data']['commit'] = 'b' * 40
        self.stage_inputs()
        with self.assertRaises(Failure) as failed:
            read_transfer(self.transfer, self.root / 'transfer-copy', TARGET)
        self.assertEqual(failed.exception.code, 'STALE_REPORT')

    def test_other_project_cannot_reuse_report_with_same_git_commit(self):
        self.report['project_path'] = 'projects/one'
        self.stage_inputs()
        request = {'target': TARGET, 'project_path': 'projects/two'}
        with patch('consume_report.snapshot') as snapshot:
            result = consume(request, self.transfer, self.root / 'out')
        snapshot.assert_not_called()
        self.assertEqual(result['error']['code'], 'REPORT_IDENTITY_MISMATCH')
