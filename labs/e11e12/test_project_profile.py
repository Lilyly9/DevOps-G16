import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from project_profile import PROFILE_FILENAME, load_profile


class ProjectProfileTests(unittest.TestCase):
    def setUp(self):
        workspace = TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.project = Path(workspace.name)
        self.file = self.project / PROFILE_FILENAME
        self.profile = {
            'schema_version': 'e12-project-1',
            'targets': {'eta_cli.o': 'eta_cli.c', 'estimate.o': 'estimate.c'},
            'clean_target': 'clean',
            'build_target': 'transfer-eta',
            'test_target': 'test',
            'program': ['./transfer-eta', '100'],
            'expected_output': 'eta_seconds=13',
            'header_change': {
                'file': 'defaults.h',
                'before': '#define DEFAULT_RATE_MIB_S 8',
                'after': '#define DEFAULT_RATE_MIB_S 5',
                'expected_output': 'eta_seconds=20',
            },
        }

    def write_profile(self, settings):
        data = json.dumps(settings).encode('utf-8')
        self.file.write_bytes(data)
        return data

    def test_profile_reads_configured_names_and_checks_both_git_snapshots(self):
        data = self.write_profile(self.profile)
        profile = load_profile(self.project)
        self.assertEqual(profile.sha256, hashlib.sha256(data).hexdigest())
        self.assertEqual(profile.program, ('./transfer-eta', '100'))
        base = self.project / 'base'
        base.mkdir()
        for snapshot in (base, self.project):
            for name in ('Makefile', 'eta_cli.c', 'estimate.c'):
                (snapshot / name).touch()
        profile.validate_sources(self.project)
        profile.validate_sources(base)
        (base / 'estimate.c').unlink()
        with self.assertRaisesRegex(ValueError, 'estimate.c must be a regular file'):
            profile.validate_sources(base)

    def test_rejects_paths_and_non_declarative_program_arguments(self):
        cases = (
            ('targets', {'eta_cli.o': '../eta_cli.c', 'estimate.o': 'estimate.c'}),
            ('targets', {'eta_cli.o': 'eta_cli.c', 'extra/estimate.o': 'estimate.c'}),
            ('build_target', '-C'),
            ('test_target', 'test && echo ok'),
            ('program', ['/bin/sh', '100']),
            ('program', ['./transfer-eta', '100 && echo ok']),
            ('header_change', dict(self.profile['header_change'], file='../defaults.h')),
        )
        for key, value in cases:
            with self.subTest(field=key, value=value):
                settings = copy.deepcopy(self.profile)
                settings[key] = value
                self.write_profile(settings)
                with self.assertRaises(ValueError):
                    load_profile(self.project)

    def test_header_edit_replaces_only_one_exact_line_preserving_other_bytes(self):
        self.write_profile(self.profile)
        edit = load_profile(self.project).header_change
        header = self.project / edit.file
        source = b'/* group defaults */\r\n#define DEFAULT_RATE_MIB_S 8\r\n/* end */'
        header.write_bytes(source)
        edit.apply(self.project)
        self.assertEqual(header.read_bytes(), source.replace(b'_S 8', b'_S 5'))

        ambiguous = b'#define DEFAULT_RATE_MIB_S 8\n#define DEFAULT_RATE_MIB_S 8\n'
        header.write_bytes(ambiguous)
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            edit.apply(self.project)
        self.assertEqual(header.read_bytes(), ambiguous)
