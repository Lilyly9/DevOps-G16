"""Declarative C/Make settings for an E12 subject project."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


PROFILE_FILENAME = 'e12-profile.json'
SCHEMA_VERSION = 'e12-project-1'
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]*\Z')
ARGUMENT = re.compile(r'[0-9]{1,18}\Z')


def _name(value, field, suffix=''):
    if not isinstance(value, str) or not NAME.fullmatch(value) or not value.endswith(suffix):
        raise ValueError(f'{field} must be a flat name{f" ending in {suffix}" if suffix else ""}')
    return value


def _line(value, field):
    if not isinstance(value, str) or not value or any(c in value for c in '\r\n\0'):
        raise ValueError(f'{field} must be one nonempty line')
    return value


def _read_regular(project, filename):
    path = project / filename
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'{filename} must be a regular file in {project}')
    return path


def _object_pairs(pairs):
    values = {}
    for key, value in pairs:
        if key in values:
            raise ValueError(f'duplicate profile field: {key}')
        values[key] = value
    return values


@dataclass(frozen=True)
class HeaderChange:
    file: str
    before: str
    after: str
    expected_output: str

    def apply(self, project):
        header = _read_regular(project, self.file)
        lines = header.read_bytes().splitlines(keepends=True)
        before = self.before.encode('utf-8')
        matches = [index for index, line in enumerate(lines) if line.rstrip(b'\r\n') == before]
        if len(matches) != 1:
            raise ValueError(f'{self.file} must contain exactly one copy of the original header line')
        index = matches[0]
        lines[index] = self.after.encode('utf-8') + lines[index][len(before):]
        header.write_bytes(b''.join(lines))


@dataclass(frozen=True)
class ProjectProfile:
    targets: dict[str, str]
    clean_target: str
    build_target: str
    test_target: str
    program: tuple[str, ...]
    expected_output: str
    header_change: HeaderChange
    sha256: str

    def validate_sources(self, project):
        _read_regular(project, 'Makefile')
        for source in self.targets.values():
            _read_regular(project, source)


def load_profile(project: Path) -> ProjectProfile:
    """Read the selected checkout's fixed profile file and validate its fields."""
    project = Path(project)
    data = _read_regular(project, PROFILE_FILENAME).read_bytes()
    try:
        settings = json.loads(data.decode('utf-8'), object_pairs_hook=_object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'{PROFILE_FILENAME} must be a UTF-8 JSON object') from exc
    required = {'targets', 'clean_target', 'build_target', 'test_target', 'program',
                'expected_output', 'header_change'}
    if not isinstance(settings, dict) or set(settings) - {'schema_version'} != required:
        raise ValueError(f'{PROFILE_FILENAME} must contain: {", ".join(sorted(required))}')
    if settings.get('schema_version', SCHEMA_VERSION) != SCHEMA_VERSION:
        raise ValueError(f'schema_version must be {SCHEMA_VERSION}')

    targets = settings['targets']
    if not isinstance(targets, dict) or len(targets) < 2:
        raise ValueError('targets must map two or more object names to source names')
    targets = {_name(k, 'object target', '.o'): _name(v, 'source', '.c') for k, v in targets.items()}

    clean_target = _name(settings['clean_target'], 'clean_target')
    build_target = _name(settings['build_target'], 'build_target')
    test_target = _name(settings['test_target'], 'test_target')
    if len({clean_target, build_target, test_target}) != 3:
        raise ValueError('clean_target, build_target, and test_target must differ')

    program = settings['program']
    if not isinstance(program, list) or not program or program[0] != f'./{build_target}':
        raise ValueError('program must start with the built executable ./BUILD_TARGET')
    if any(not isinstance(arg, str) or not ARGUMENT.fullmatch(arg) for arg in program[1:]):
        raise ValueError('program arguments must be quoted nonnegative integers')

    expected = _line(settings['expected_output'], 'expected_output')
    change = settings['header_change']
    fields = {'file', 'before', 'after', 'expected_output'}
    if not isinstance(change, dict) or set(change) != fields:
        raise ValueError('header_change must contain file, before, after, and expected_output')
    header = HeaderChange(
        _name(change['file'], 'header_change.file', '.h'),
        _line(change['before'], 'header_change.before'),
        _line(change['after'], 'header_change.after'),
        _line(change['expected_output'], 'header_change.expected_output'),
    )
    if header.before == header.after or header.expected_output == expected:
        raise ValueError('header_change must change the header line and expected output')
    return ProjectProfile(targets, clean_target, build_target, test_target, tuple(program), expected,
                          header, hashlib.sha256(data).hexdigest())
