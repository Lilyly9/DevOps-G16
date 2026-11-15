"""A2 contribution: declarative target/rule mapping for an E11-E12 subject project.

The course fixture hardcodes main.o/helper.o, ./app, output 1 -> 2 and config.h.
A real project supplies those settings in ``e11e12-project.json`` at its root so
the same EChecker can map object targets, rules, build/test commands and the
header-change verification without editing shared code.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

FILENAME = 'e11e12-project.json'
SCHEMA_VERSION = 'e11e12-project-1'
_NAME = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.-]*\Z')
_SOURCE = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.-]*\.c\Z')
_HEADER = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.-]*\.h\Z')
_OUTPUT = re.compile(r'[^\s\0]{1,200}\Z')


def _flat_name(value, field, pattern=_NAME):
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f'{field} must be a flat file/target name')
    return value


def _line(value, field):
    if not isinstance(value, str) or not value or any(ch in value for ch in '\r\n\0'):
        raise ValueError(f'{field} must be one nonempty line')
    return value


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate field: {key}')
        result[key] = value
    return result


def _regular(project, name):
    path = project / name
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'{name} must be a regular file in the selected commit')
    return path


@dataclass(frozen=True)
class HeaderChange:
    file: str
    before: str
    after: str
    expected_output: str

    def apply(self, project):
        header = _regular(project, self.file)
        lines = header.read_bytes().splitlines(keepends=True)
        before = self.before.encode('utf-8')
        matches = [i for i, line in enumerate(lines) if line.rstrip(b'\r\n') == before]
        if len(matches) != 1:
            raise ValueError(f'{self.file} must contain exactly one copy of the configured line')
        index = matches[0]
        lines[index] = self.after.encode('utf-8') + lines[index][len(before):]
        header.write_bytes(b''.join(lines))


@dataclass(frozen=True)
class ProjectConfig:
    targets: tuple
    clean_target: str
    build_target: str
    test_target: str
    program: tuple
    expected_output: str
    header_change: HeaderChange
    include_dirs: tuple
    sha256: str

    @property
    def target_map(self):
        return dict(self.targets)

    def validate_sources(self, project):
        _regular(project, 'Makefile')
        for _, source in self.targets:
            _regular(project, source)
        _regular(project, self.header_change.file)


def load_config(project):
    project = Path(project)
    raw = _regular(project, FILENAME).read_bytes()
    try:
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=_object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'{FILENAME} must be a UTF-8 JSON object') from exc
    required = {'targets', 'clean_target', 'build_target', 'test_target', 'program',
                'expected_output', 'header_change'}
    allowed = required | {'schema_version', 'include_dirs'}
    if not isinstance(data, dict) or set(data) - allowed or required - set(data):
        raise ValueError('profile must contain exactly: ' + ', '.join(sorted(required)))
    if data.get('schema_version', SCHEMA_VERSION) != SCHEMA_VERSION:
        raise ValueError(f'schema_version must be {SCHEMA_VERSION}')

    targets = data['targets']
    if not isinstance(targets, dict) or not targets:
        raise ValueError('targets must map one or more object names to source names')
    normalized = []
    for target, source in targets.items():
        normalized.append((_flat_name(target, 'object target'),
                           _flat_name(source, 'source', _SOURCE)))
    if len({target for target, _ in normalized}) != len(normalized):
        raise ValueError('object targets must be unique')

    clean = _flat_name(data['clean_target'], 'clean_target')
    build = _flat_name(data['build_target'], 'build_target')
    test = data['test_target']
    if test is not None:
        _flat_name(test, 'test_target')
        if len({clean, build, test}) != 3:
            raise ValueError('clean_target, build_target and test_target must differ')
    elif clean == build:
        raise ValueError('clean_target and build_target must differ')

    program = data['program']
    if not isinstance(program, list) or not program or program[0] != f'./{build}':
        raise ValueError('program must start with the built executable ./BUILD_TARGET')
    if any(not isinstance(arg, str) or not _OUTPUT.fullmatch(arg) for arg in program[1:]):
        raise ValueError('program arguments must be single non-whitespace tokens')
    expected = _line(data['expected_output'], 'expected_output')

    change = data['header_change']
    fields = {'file', 'before', 'after', 'expected_output'}
    if not isinstance(change, dict) or set(change) != fields:
        raise ValueError('header_change must contain file, before, after and expected_output')
    header = HeaderChange(_flat_name(change['file'], 'header_change.file', _HEADER),
                          _line(change['before'], 'header_change.before'),
                          _line(change['after'], 'header_change.after'),
                          _line(change['expected_output'], 'header_change.expected_output'))
    if header.before == header.after or header.expected_output == expected:
        raise ValueError('header_change must change the line and the expected output')

    include_dirs = data.get('include_dirs', [])
    if not isinstance(include_dirs, list):
        raise ValueError('include_dirs must be a list')
    for item in include_dirs:
        if not isinstance(item, str) or not item or any(part in ('', '.', '..') for part in item.split('/')):
            raise ValueError('include_dirs entries must be relative directory paths without . or ..')
        if not (project / item).is_dir():
            raise ValueError(f'include_dirs entry does not exist: {item}')

    config = ProjectConfig(tuple(normalized), clean, build, test, tuple(program), expected,
                           header, tuple(include_dirs), hashlib.sha256(raw).hexdigest())
    config.validate_sources(project)
    return config
