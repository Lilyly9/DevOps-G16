"""B2 contracts for MDFixer's patch scope and report admission."""

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch as mock_patch

import pipeline
from lab import commit, declarations, fixture, patch, run


class MDFixerB2Tests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.project = self.root / 'project'

    def test_macro_shared_with_helper_is_repaired_only_on_main_rule(self):
        fixture(self.project, 'macro')
        makefile = self.project / 'Makefile'
        original = makefile.read_text().replace('helper.o: helper.c\n', 'helper.o: helper.c $(DEPS)\n')
        makefile.write_text(original)
        target = commit(self.project, 'Share the macro with helper.o')
        before = declarations(self.project)[0]

        report = {'commit': target, 'findings': [
            {'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'},
            {'type': 'MISSING', 'target': 'main.o', 'dependency': 'extra.h'},
        ]}
        diff, plan = patch(self.project, report, isolate_shared_macros=True)
        self.assertEqual(makefile.read_text(), original)
        self.assertEqual(plan, [
            {'target': 'main.o', 'dependency': 'config.h', 'style': 'mixed'},
            {'target': 'main.o', 'dependency': 'extra.h', 'style': 'mixed'},
        ])

        candidate = self.root / 'candidate.patch'
        candidate.write_bytes(diff.encode('utf-8'))
        run(['git', 'apply', str(candidate)], self.project)
        self.assertEqual(makefile.read_text(), original.replace(
            'main.o: $(DEPS)\n', 'main.o: $(DEPS) config.h extra.h\n',
        ))
        after = declarations(self.project)[0]
        self.assertEqual(after['helper.o'], before['helper.o'])
        self.assertEqual(set(after['main.o']) - set(before['main.o']), {'config.h', 'extra.h'})

    def test_fixed_report_with_stale_data_stops_before_repair(self):
        fixture(self.project)
        base = run(['git', 'rev-parse', 'HEAD'], self.project).strip()
        source = self.project / 'main.c'
        source.write_text('#include "extra.h"\n' + source.read_text())
        target = commit(self.project, 'Add the missing header dependency')
        report_path = self.root / 'fixed-md.json'
        pipeline.save(report_path, {
            'schema_version': 'e11e12-1', 'kind': 'fixed-md', 'status': 'SUCCEEDED',
            'commit': target, 'data': {'commit': base, 'findings': [
                {'type': 'MISSING', 'target': 'main.o', 'dependency': 'extra.h'},
            ]},
        })
        original_report = report_path.read_bytes()
        request = {
            'mode': 'e11-b', 'repo': str(self.project), 'base': base, 'target': target,
            'candidate': str(self.root / 'candidate.Dockerfile'), 'fixed_report': str(report_path),
        }

        def completed_draft(_target, _candidate, evidence, _expected, **_options):
            result = {'status': 'SUCCEEDED'}
            pipeline.save(evidence / 'result.json', result)
            return result

        out = self.root / 'result'
        with mock_patch('draft.autobuild.auto_build', side_effect=completed_draft), \
             mock_patch.object(pipeline, 'patch') as plan_patch, \
             mock_patch.object(pipeline, 'validate') as validate:
            result = pipeline.execute(request, out)
        self.assertEqual(result['status'], 'FAILED')
        diagnostics = [log.read_text(encoding='utf-8') for log in sorted((out / 'logs').glob('*.log'))]
        self.assertEqual(result['error']['code'], 'STALE_REPORT', (result['error'], diagnostics))
        self.assertEqual([stage['name'] for stage in result['stages']], ['draft'])
        plan_patch.assert_not_called()
        validate.assert_not_called()
        for filename in ('fixed-md.json', 'candidate.patch', 'repair-plan.json', 'validation'):
            self.assertFalse((out / filename).exists(), filename)
        self.assertEqual(report_path.read_bytes(), original_report)
        self.assertEqual((out / 'target-project/Makefile').read_bytes(),
                         (self.project / 'Makefile').read_bytes())

    def test_dynamic_report_with_verified_hash_still_requires_current_data_commit(self):
        target, old = 'a' * 40, 'b' * 40
        report = self.root / 'incremental-check.json'
        envelope = {
            'schema_version': 'e11e12-1', 'kind': 'incremental-check', 'status': 'SUCCEEDED',
            'commit': target, 'data': {'commit': old, 'findings': []},
        }
        pipeline.save(report, envelope)
        digest = hashlib.sha256(report.read_bytes()).hexdigest()
        verified = pipeline.load_artifact(report, digest)
        with self.assertRaises(pipeline.Failure) as error:
            pipeline.repair_input(verified, target, 'incremental-check')
        self.assertEqual(error.exception.code, 'STALE_REPORT')


if __name__ == '__main__':
    unittest.main()
