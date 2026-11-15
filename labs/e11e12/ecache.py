"""A2 contribution: configurable EChecker with incremental cache refresh/reuse.

Unlike ``labs/e8e10/lab.py`` (course fixture targets main.o/helper.o), this
module maps whatever object targets a subject project declares in
``e11e12-project.json`` to their sources and rules.  It also exposes a
profile-aware patch/validate path and accepts an execution hook so the same
commands can be replayed inside the DRAFT-built image.
"""
import difflib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

SKIP_DIRS = {'.git', 'work', '__pycache__', 'node_modules', 'build', 'out', 'dist'}
SAFE_FLAG = re.compile(r'(?:-I[^\s]+|-D[^\s]*|-U[^\s]*|-O[^\s]*|-g[^\s]*|-std=[^\s]+|-m[^\s]+|-f[^\s]+|-W[^\s]*|-w|-pthread|-pipe|-ansi|-pedantic(?:-errors)?)\Z')


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=120)
    if result.returncode:
        raise ValueError('COMMAND_FAILED ' + repr(argv) + '\n' + result.stdout + result.stderr)
    return result.stdout


def git_commit(project, execute=run):
    return execute(['git', 'rev-parse', 'HEAD'], project).strip()


def _expand(text, variables, depth=0):
    if depth > 8:
        raise ValueError('UNSUPPORTED_DECLARATION recursive variable expansion')
    def replace(match):
        name = match.group(1)
        if name not in variables:
            raise ValueError(f'UNSUPPORTED_DECLARATION unknown variable {name}')
        return _expand(variables[name], variables, depth + 1)
    return re.sub(r'\$\((\w+)\)', replace, text)


def _variables(text):
    return {name: value for name, value in re.findall(r'^([A-Za-z_]\w*)\s*=\s*(.*)$', text, re.M)}


def declarations(project, config, execute=run):
    text = (project / 'Makefile').read_text(encoding='utf-8')
    variables = _variables(text)
    graph = {}
    for target, _source in config.targets:
        match = re.search(r'^' + re.escape(target) + r': ([^\n]*)$', text, re.M)
        if not match:
            raise ValueError(f'UNSUPPORTED_RULE missing rule for {target}')
        raw = match.group(1)
        if '|' in raw or '%' in raw:
            raise ValueError(f'UNSUPPORTED_DECLARATION order-only or pattern dependency on {target}')
        expanded = _expand(raw, variables)
        if '$' in expanded:
            raise ValueError(f'UNSUPPORTED_DECLARATION unresolved variable on {target}')
        graph[target] = sorted(set(expanded.split()))
    flags = []
    for name in ('CPPFLAGS', 'CFLAGS'):
        value = variables.get(name, '')
        expanded = _expand(value, variables)
        for token in expanded.split():
            if not SAFE_FLAG.fullmatch(token):
                raise ValueError(f'UNSUPPORTED_FLAGS {name} token {token!r}')
            if token not in flags:
                flags.append(token)
    for directory in config.include_dirs:
        token = '-I' + directory
        if token not in flags:
            flags.append(token)
    return graph, flags


def _directive_files(project):
    files = {}
    for path in sorted(project.rglob('*')):
        if not path.is_file() or path.suffix not in ('.c', '.h'):
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(project).parts[:-1]):
            continue
        files[path.relative_to(project).as_posix()] = [
            line for line in path.read_text(encoding='utf-8', errors='replace').splitlines()
            if line.lstrip().startswith('#')
        ]
    return files


def invalidation(key, old):
    if not old:
        return ['NO_HISTORY']
    previous = old.get('key', {})
    reasons = [name for name in sorted(set(previous.get('directives', {})) | set(key['directives']))
               if previous.get('directives', {}).get(name) != key['directives'].get(name)]
    reasons += [field for field in ('recipes', 'flags', 'compiler', 'targets', 'config')
                if previous.get(field) != key.get(field)]
    return reasons


def scan(project, config, old=None, execute=run, commit=None):
    project = Path(project)
    start = time.perf_counter()
    declared, flags = declarations(project, config, execute)
    directives = _directive_files(project)
    key = {'directives': directives,
           'recipes': [line for line in (project / 'Makefile').read_text(encoding='utf-8').splitlines()
                       if line.startswith('\t')],
           'flags': flags,
           'compiler': execute(['gcc', '--version'], project).splitlines()[0],
           'targets': dict(config.targets),
           'config': config.sha256}
    global_equal = bool(old) and all(old.get('key', {}).get(field) == key[field]
                                     for field in ('recipes', 'flags', 'compiler', 'targets', 'config'))
    previous_directives = old.get('key', {}).get('directives', {}) if old else {}
    changed = {name for name in set(previous_directives) | set(directives)
               if previous_directives.get(name) != directives.get(name)}
    actual, refreshed, reused = {}, [], []
    for target, source in config.targets:
        dependencies = set(old.get('actual', {}).get(target, [])) if old else set()
        affected = source in changed or bool(dependencies & changed)
        if global_equal and target in old.get('actual', {}) and not affected:
            actual[target] = old['actual'][target]
            reused.append(target)
        else:
            output = execute(['gcc', *flags, '-MM', '-MT', target, source], project)
            actual[target] = sorted(set(output.replace('\\\n', ' ').split(':', 1)[1].split()))
            refreshed.append(target)
    findings = []
    for target in actual:
        for kind, edges in (('MISSING', set(actual[target]) - set(declared[target])),
                            ('REDUNDANT', set(declared[target]) - set(actual[target]))):
            findings.extend({'type': kind, 'target': target, 'dependency': dep}
                            for dep in sorted(edges))
    current = {(item['type'], item['target'], item['dependency']) for item in findings}
    previous = {(item['type'], item['target'], item['dependency'])
                for item in old.get('findings', [])} if old else set()
    return {'schema_version': 'e11e12-ecache-1',
            'profile_sha256': config.sha256,
            'commit': commit or git_commit(project, execute),
            'key': key, 'actual': actual, 'declared': declared,
            'findings': findings,
            'added': [list(item) for item in sorted(current - previous)],
            'resolved': [list(item) for item in sorted(previous - current)],
            'refreshed': refreshed, 'reused': reused,
            'invalidation': invalidation(key, old),
            'elapsed_s': time.perf_counter() - start}


def project_edge(actual_graph, target, dependency):
    """Return the baseline evidence for one object edge, or raise if absent."""
    for edge in actual_graph:
        if edge.get('target') == target and edge.get('dependency') == dependency:
            return {'target': target, 'dependency': dependency, 'kind': edge.get('kind'),
                    'evidence': edge.get('evidence')}
    raise ValueError(f'edge {target} -> {dependency} is absent from the baseline graph')


def patch(project, report, execute=run):
    project = Path(project)
    if report['commit'] != git_commit(project, execute):
        raise ValueError('STALE_REPORT')
    original = (project / 'Makefile').read_text(encoding='utf-8')
    changed = original
    edits = []
    for finding in report['findings']:
        if finding['type'] != 'MISSING':
            continue
        target, dependency = finding['target'], finding['dependency']
        if '..' in Path(dependency).parts or Path(dependency).is_absolute():
            raise ValueError('UNSAFE_PATH')
        if not (project / dependency).is_file():
            raise ValueError('MISSING_INPUT')
        match = re.search(r'^' + re.escape(target) + r': (.*)$', changed, re.M)
        if not match:
            raise ValueError('UNSUPPORTED_TARGET')
        raw = match.group(1)
        macros = re.findall(r'\$\((\w+)\)', raw)
        if raw.strip() == ('$(%s)' % macros[0] if macros else ''):
            name = macros[0]
            variable = re.search(r'^' + name + r' = (.*)$', changed, re.M)
            if not variable:
                raise ValueError('UNSUPPORTED_MACRO')
            changed = changed[:variable.end()] + ' ' + dependency + changed[variable.end():]
            style = 'macro'
        else:
            changed = changed[:match.end()] + ' ' + dependency + changed[match.end():]
            style = 'mixed' if macros else 'direct'
        edits.append({'target': target, 'dependency': dependency, 'style': style})
    diff = ''.join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
                                        fromfile='a/Makefile', tofile='b/Makefile'))
    return diff, edits


def validate(project, patchfile, evidence, config, fail_test=False, execute=run):
    project, evidence = Path(project), Path(evidence)
    evidence.mkdir(parents=True)
    before = (project / 'Makefile').read_bytes()
    sandbox = evidence / 'sandbox'
    shutil.copytree(project, sandbox, ignore=shutil.ignore_patterns(
        '.git', '*.o', '*.a', Path(config.program[0]).name))
    run(['git', 'init', '-b', 'main'], sandbox)
    run(['git', 'config', 'user.name', 'ValidationSandbox'], sandbox)
    run(['git', 'config', 'user.email', 'fixture@localhost'], sandbox)
    run(['git', 'add', '.'], sandbox)
    run(['git', 'commit', '-m', 'sandbox input'], sandbox)
    checks, error = {}, None
    output = changed_output = None
    try:
        run(['git', 'apply', '--check', str(Path(patchfile).resolve())], sandbox)
        checks['patch_applies'] = True
        run(['git', 'apply', str(Path(patchfile).resolve())], sandbox)
        log = execute(['make', config.clean_target], sandbox) + execute(['make', config.build_target], sandbox)
        (evidence / 'build.log').write_text(log, encoding='utf-8')
        checks['build'] = True
        if config.test_target is not None:
            (evidence / 'project-test.log').write_text(
                execute(['make', config.test_target], sandbox), encoding='utf-8')
            checks['project_make_test'] = True
        output = execute(list(config.program), sandbox).strip()
        checks['test'] = output == ('99' if fail_test else config.expected_output)
        time.sleep(1.05)
        config.header_change.apply(sandbox)
        (evidence / 'incremental.log').write_text(
            execute(['make', config.build_target], sandbox), encoding='utf-8')
        changed_output = execute(list(config.program), sandbox).strip()
        checks['header_change'] = changed_output == config.header_change.expected_output
        recheck = scan(sandbox, config, execute=execute,
                       commit=run(['git', 'rev-parse', 'HEAD'], sandbox).strip())
        save(evidence / 'recheck.json', recheck)
        checks['no_missing'] = not any(item['type'] == 'MISSING' for item in recheck['findings'])
    except (ValueError, subprocess.TimeoutExpired) as exc:
        error = str(exc)
    accepted = bool(checks) and all(checks.values()) and error is None
    if accepted:
        (project / 'Makefile').write_bytes((sandbox / 'Makefile').read_bytes())
    unchanged = (project / 'Makefile').read_bytes() == before
    result = {'accepted': accepted, 'checks': checks, 'error': error,
              'source_unchanged': unchanged, 'rollback': not accepted and unchanged,
              'outputs': {'expected': config.expected_output, 'actual': output,
                          'expected_after_header_change': config.header_change.expected_output,
                          'actual_after_header_change': changed_output}}
    save(evidence / 'validation.json', result)
    return result
