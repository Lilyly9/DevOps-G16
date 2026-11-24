"""B2 C5 contracts; Docker/full-check failures are explicitly injected."""

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch as mock_patch

import lab
import pipeline


class MDFixerRollbackB2Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / 'project'
        lab.fixture(self.project)
        self.makefile = self.project / 'Makefile'
        self.before = self.makefile.read_bytes()
        self.commit = lab.run(['git', 'rev-parse', 'HEAD'], self.project).strip()
        self.before_files = self.source_files()
        self.candidate = self.root / 'candidate.patch'
        report = {'commit': self.commit, 'findings': [
            {'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'},
        ]}
        diff, _ = lab.patch(self.project, report, isolate_shared_macros=True)
        self.candidate.write_bytes(diff.encode('utf-8'))

    def source_files(self):
        return {p.name: p.read_bytes() for p in self.project.iterdir() if p.is_file()}

    def assert_source_unchanged(self):
        self.assertEqual(self.source_files(), self.before_files)
        self.assertEqual(lab.run(['git', 'rev-parse', 'HEAD'], self.project).strip(), self.commit)
        self.assertEqual(lab.run(['git', 'status', '--porcelain'], self.project), '')

    def test_malformed_patch_rejected_before_build_with_unchanged_source_hash(self):
        self.candidate.write_bytes(b'not a unified patch\n')
        calls = []

        def runner(_evidence):
            def execute(argv, cwd):
                calls.append(argv)
                self.fail('A rejected patch must not execute a build')
            return execute

        evidence = self.root / 'rejected'
        result = lab.validate(self.project, self.candidate, evidence, runner=runner)
        self.assertFalse(result['accepted'])
        self.assertTrue(result['rollback'])
        self.assertEqual(calls, [])
        self.assertEqual(result['source_sha256_before'], hashlib.sha256(self.before).hexdigest())
        self.assertEqual(result['source_sha256_after'], result['source_sha256_before'])
        self.assertEqual(result['patch_sha256'], hashlib.sha256(self.candidate.read_bytes()).hexdigest())
        self.assertEqual(json.loads((evidence / 'validation.json').read_text()), result)
        self.assert_source_unchanged()

    def test_runner_timeout_and_oserror_preserve_validation_and_source(self):
        failures = (TimeoutError('container timed out'),
                    subprocess.TimeoutExpired(['make', 'app'], 1),
                    OSError('container execution unavailable'))
        for index, failure in enumerate(failures):
            with self.subTest(failure=type(failure).__name__):
                def runner(_evidence):
                    def execute(argv, cwd):
                        raise failure
                    return execute

                evidence = self.root / f'runner-failure-{index}'
                result = lab.validate(self.project, self.candidate, evidence, runner=runner)
                self.assertFalse(result['accepted'])
                self.assertTrue(result['rollback'])
                self.assertIn(str(failure), result['error'])
                self.assertTrue((evidence / 'validation.json').is_file())
                self.assert_source_unchanged()

    def accepted_validation(self, target, _patchfile, evidence, **_options):
        """Isolate final recheck admission from the build toolchain."""
        target.joinpath('Makefile').write_bytes(self.before + b'# accepted candidate\n')
        result = {'accepted': True, 'checks': {'build': True}}
        pipeline.save(evidence / 'validation.json', result)
        return result

    def transaction(self, out):
        return pipeline.validate_repair(
            self.project, self.candidate, out, None, None,
            commit=self.commit, job_id='job-b2-c5', trace_id='trace-b2-c5',
        )

    def assert_rollback_record(self, out, phase):
        self.assert_source_unchanged()
        record = json.loads((out / 'rollback.json').read_text())
        self.assertEqual(record['phase'], phase)
        self.assertEqual(record['commit'], self.commit)
        self.assertEqual(record['job_id'], 'job-b2-c5')
        self.assertEqual(record['trace_id'], 'trace-b2-c5')
        self.assertTrue(record['rollback'])
        self.assertEqual(record['source_sha256_after'], hashlib.sha256(self.before).hexdigest())
        self.assertEqual(record['source_sha256_before'], record['source_sha256_after'])

    def test_recheck_that_removes_makefile_still_restores_original_bytes(self):
        out = self.root / 'missing-makefile'

        def failed_recheck(*_args):
            self.makefile.unlink()
            raise OSError('Recheck lost the Makefile')

        with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation), \
             mock_patch.object(pipeline, 'full', side_effect=failed_recheck):
            with self.assertRaisesRegex(OSError, 'Recheck lost'):
                self.transaction(out)
        self.assert_rollback_record(out, 'recheck')
        self.assertIsNone(json.loads((out / 'rollback.json').read_text())['candidate_makefile_sha256'])

    def test_recheck_command_error_restores_candidate_and_saves_rollback(self):
        out = self.root / 'recheck-error'
        with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation), \
             mock_patch.object(pipeline, 'full', side_effect=ValueError('strace failed')):
            with self.assertRaisesRegex(ValueError, 'strace failed'):
                self.transaction(out)
        self.assert_rollback_record(out, 'recheck')

    def test_recheck_timeout_and_oserror_also_restore_candidate(self):
        for index, error in enumerate((TimeoutError('recheck timed out'), OSError('trace missing'))):
            with self.subTest(error=type(error).__name__):
                out = self.root / f'recheck-error-{index}'
                with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation), \
                     mock_patch.object(pipeline, 'full', side_effect=error):
                    with self.assertRaises(type(error)):
                        self.transaction(out)
                self.assert_rollback_record(out, 'recheck')

    def test_remaining_missing_dependency_rejects_and_restores_candidate(self):
        final = {'findings': [{'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'}]}
        out = self.root / 'remaining-md'
        with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation), \
             mock_patch.object(pipeline, 'full', return_value=final):
            with self.assertRaises(pipeline.Failure) as rejected:
                self.transaction(out)
        self.assertEqual(rejected.exception.code, 'RECHECK_FAILED')
        self.assert_rollback_record(out, 'recheck')

    def test_validation_rejection_never_runs_final_recheck(self):
        out = self.root / 'invalid'
        with mock_patch.object(pipeline, 'validate', return_value={'accepted': False}), \
             mock_patch.object(pipeline, 'full') as full:
            with self.assertRaises(pipeline.Failure) as rejected:
                self.transaction(out)
        self.assertEqual(rejected.exception.code, 'REPAIR_REJECTED')
        full.assert_not_called()
        self.assert_rollback_record(out, 'validation')

    def test_success_commits_candidate_and_allows_redundant_dependency(self):
        final = {'findings': [{'type': 'REDUNDANT', 'target': 'main.o', 'dependency': 'unused.h'}]}
        out = self.root / 'accepted'
        with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation), \
             mock_patch.object(pipeline, 'full', return_value=final):
            verdict, actual = self.transaction(out)
        self.assertTrue(verdict['accepted'])
        self.assertEqual(actual, final)
        self.assertEqual(self.makefile.read_bytes(), self.before + b'# accepted candidate\n')
        self.assertFalse((out / 'rollback.json').exists())
        self.assertEqual(lab.run(['git', 'rev-parse', 'HEAD'], self.project).strip(), self.commit)

    def test_validation_and_recheck_receive_the_same_draft_executor(self):
        executor = Mock()
        out = self.root / 'same-image-contract'
        with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation) as validate, \
             mock_patch.object(pipeline, 'full', return_value={'findings': []}) as full:
            pipeline.validate_repair(self.project, self.candidate, out, executor, None,
                                     commit=self.commit, job_id='job-image', trace_id='trace-image')
        self.assertIs(validate.call_args.kwargs['runner'], executor.capture)
        full.assert_called_once_with(self.project, out / 'final-full', executor, None)

    def test_failed_recheck_then_fresh_attempt_succeeds_on_restored_source(self):
        failed, recovered = self.root / 'failed', self.root / 'recovered'
        with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation), \
             mock_patch.object(pipeline, 'full', side_effect=TimeoutError('injected timeout')):
            with self.assertRaises(TimeoutError):
                self.transaction(failed)
        self.assert_rollback_record(failed, 'recheck')
        saved_failure = (failed / 'rollback.json').read_bytes()
        with mock_patch.object(pipeline, 'validate', side_effect=self.accepted_validation), \
             mock_patch.object(pipeline, 'full', return_value={'findings': []}):
            verdict, _ = pipeline.validate_repair(
                self.project, self.candidate, recovered, None, None, commit=self.commit,
                job_id='job-recovered', trace_id='trace-recovered',
            )
        self.assertTrue(verdict['accepted'])
        self.assertEqual((failed / 'rollback.json').read_bytes(), saved_failure)
        self.assertFalse((recovered / 'rollback.json').exists())


if __name__ == '__main__':
    unittest.main()
