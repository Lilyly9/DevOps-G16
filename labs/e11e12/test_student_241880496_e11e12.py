"""A2 (241880496) tests: configurable EChecker mapping, cache reuse and provenance."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import ecache
import project_config
from draft_exec import ImageExecutor


def write(root, name, text):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def make_project(root, targets=None, flags='-O0'):
    targets = targets or {'core.o': 'core.c', 'util.o': 'util.c'}
    write(root, 'core.c', '#include "common.h"\nint core(void){return COMMON;}\n')
    write(root, 'util.c', '#include <stdio.h>\n#include "config.h"\nint util(void){return VALUE;}\n')
    write(root, 'common.h', '#define COMMON 1\n')
    write(root, 'config.h', '#define VALUE 1\n')
    write(root, 'extra.h', '#define EXTRA 0\n')
    rules = ''.join(f'{target}: {source}\n\tgcc $(CFLAGS) -c {source} -o {target}\n'
                    for target, source in targets.items())
    write(root, 'Makefile',
          f'CFLAGS = {flags}\napp: {" ".join(targets)}\n\tgcc {" ".join(targets)} -o app\n'
          f'{rules}clean:\n\trm -f *.o app\n')
    write(root, 'e11e12-project.json', json.dumps({
        'schema_version': 'e11e12-project-1', 'targets': targets,
        'clean_target': 'clean', 'build_target': 'app', 'test_target': None,
        'program': ['./app'], 'expected_output': '1',
        'header_change': {'file': 'config.h', 'before': '#define VALUE 1',
                          'after': '#define VALUE 2', 'expected_output': '2'},
        'include_dirs': []}))
    git(root, 'init', '-b', 'main')
    git(root, 'config', 'user.name', 'A2ProfileTest')
    git(root, 'config', 'user.email', 'a2@example.invalid')
    write(root, '.gitignore', '*.o\napp\n')
    git(root, 'add', '.')
    git(root, 'commit', '-m', 'C0 profile baseline')
    return project_config.load_config(Path(root))


class ProfileMapping(unittest.TestCase):
    def test_declared_targets_replace_fixture_names(self):
        with tempfile.TemporaryDirectory() as root:
            config = make_project(root)
            report = ecache.scan(Path(root), config)
            self.assertEqual(set(report['actual']), {'core.o', 'util.o'})
            self.assertIn(('MISSING', 'util.o', 'config.h'),
                          {(f['type'], f['target'], f['dependency']) for f in report['findings']})
            self.assertNotIn('main.o', report['actual'])

    def test_change_refreshes_only_affected_target(self):
        with tempfile.TemporaryDirectory() as root:
            config = make_project(root)
            baseline = ecache.scan(Path(root), config)
            write(root, 'core.c', '#include "extra.h"\n' + (Path(root) / 'core.c').read_text())
            git(root, 'add', '.'); git(root, 'commit', '-m', 'C1 add extra include')
            report = ecache.scan(Path(root), config, baseline)
            self.assertEqual(report['refreshed'], ['core.o'])
            self.assertEqual(report['reused'], ['util.o'])
            self.assertIn(['MISSING', 'core.o', 'extra.h'], report['added'])
            self.assertIn('core.c', ' '.join(report['invalidation']))

    def test_incremental_findings_equal_full_set(self):
        with tempfile.TemporaryDirectory() as root:
            config = make_project(root)
            baseline = ecache.scan(Path(root), config)
            write(root, 'core.c', '#include "extra.h"\n' + (Path(root) / 'core.c').read_text())
            git(root, 'add', '.'); git(root, 'commit', '-m', 'C1 add extra include')
            incremental = ecache.scan(Path(root), config, baseline)
            complete = ecache.scan(Path(root), config)
            self.assertEqual(sorted(map(tuple, incremental['findings'])),
                             sorted(map(tuple, complete['findings'])))
            self.assertNotEqual(incremental['reused'], [])

    def test_baseline_edge_can_be_traced_to_graph(self):
        graph = [{'target': 'core.o', 'dependency': 'common.h', 'kind': 'ACTUAL_READ_OPEN',
                  'evidence': {'trace_file': 't.11', 'line': 7}}]
        edge = ecache.project_edge(graph, 'core.o', 'common.h')
        self.assertEqual(edge['evidence']['line'], 7)
        with self.assertRaisesRegex(ValueError, 'absent'):
            ecache.project_edge(graph, 'core.o', 'missing.h')

    def test_stale_commit_is_rejected_before_repair(self):
        with tempfile.TemporaryDirectory() as root:
            config = make_project(root)
            report = ecache.scan(Path(root), config)
            report['commit'] = '0' * 40
            with self.assertRaisesRegex(ValueError, 'STALE_REPORT'):
                ecache.patch(Path(root), report)

    def test_unsupported_flag_is_rejected_explicitly(self):
        with tempfile.TemporaryDirectory() as root:
            config = make_project(root, flags='-O0 -include /etc/passwd')
            with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_FLAGS'):
                ecache.scan(Path(root), config)

    def test_profile_rejects_duplicate_fields_and_unknown_targets(self):
        with tempfile.TemporaryDirectory() as root:
            make_project(root)
            path = Path(root) / 'e11e12-project.json'
            data = json.loads(path.read_text())
            data['targets'] = {'core.o': 'missing.c'}
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'missing.c'):
                project_config.load_config(Path(root))

    def test_executor_requires_digest_image(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, 'sha256'):
                ImageExecutor('course-e11e12:latest', root, root)


if __name__ == '__main__':
    unittest.main()
