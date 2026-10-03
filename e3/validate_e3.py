#!/usr/bin/env python3
"""Validate saved A-group E3 evidence; needs only Python and local Git objects."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    e3 = root / 'e3'
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)
        return bool(condition)

    def read(path, kind=dict):
        try:
            value = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
            return None
        if not require(isinstance(value, kind), f'{path.relative_to(root)}: expected {kind.__name__}'):
            return None
        return value

    def git(*args):
        return subprocess.run(['git', '-C', str(root), *args], capture_output=True)

    def commit(sha, label):
        return require(isinstance(sha, str) and re.fullmatch(r'[0-9a-f]{40}', sha)
                       and git('cat-file', '-e', f'{sha}^{{commit}}').returncode == 0,
                       f'{label}: missing/invalid commit {sha}')

    def local_file(folder, value, label):
        if not require(isinstance(value, str) and bool(value), f'{label}: missing file reference'):
            return None
        path = (folder / value).resolve()
        if not require(path.is_relative_to(folder.resolve()) and path.is_file(), f'{label}: missing/unsafe file {value}'):
            return None
        return path

    for name in ('README.md', 'env/README.md', 'docs/A3_REPORT.md', 'docs/A3_AI_USAGE.md', 'docs/A3_CONTRIBUTIONS.md'):
        require((e3 / name).is_file(), f'missing documentation: e3/{name}')
    for member in ('A1', 'A2', 'A3'):
        env = read(e3 / 'env' / f'toolchain-{member}.txt')
        if env is not None:
            for key in ('member', 'os', 'architecture', 'versions'):
                require(bool(env.get(key)), f'{member}: missing environment {key}')
            require(env.get('member') == member, f'{member}: environment member mismatch')

    expected = {}
    for name in ('buildchecker-md-rd.json', 'echecker-c0-c1-c2.json'):
        item = read(e3 / 'expected' / name)
        if item is None:
            continue
        expected[name] = item
        require(item.get('provenance') in ('INSTRUCTOR_ORACLE', 'MANUAL_EXPECTED'), f'{name}: invalid provenance')
        require(bool(item.get('source')), f'{name}: missing expected-answer source')
        require(isinstance(item.get('configuration'), dict) and bool(item['configuration'].get('id')), f'{name}: missing configuration id')

    a1 = expected.get('buildchecker-md-rd.json', {})
    findings = a1.get('findings', [])
    require(isinstance(findings, list) and {(f.get('type'), f.get('dependency')) for f in findings if isinstance(f, dict)}
            == {('MISSING', 'config.h'), ('REDUNDANT', 'unused.h')}, 'A1: MD/RD expected answers missing')
    if a1:
        repo = a1.get('repository', {})
        sha = repo.get('commit')
        if commit(sha, 'A1 expected source'):
            for name in ('main.c', 'config.h', 'unused.h', 'Makefile', 'Makefile.before'):
                path = e3 / 'fixtures/md-rd' / name
                blob = git('show', f'{sha}:e3/fixtures/md-rd/{name}')
                require(path.is_file() and blob.returncode == 0 and path.read_bytes() == blob.stdout, f'A1 fixture differs: {name}')

    a2 = expected.get('echecker-c0-c1-c2.json', {})
    refs = a2.get('repository', {}).get('refs', {})
    require(isinstance(refs, dict) and set(refs) == {'C0', 'C1', 'C2'}, 'A2: missing C0/C1/C2 refs')
    for tag in ('C0', 'C1', 'C2'):
        sha = refs.get(tag) if isinstance(refs, dict) else None
        if not commit(sha, tag):
            continue
        snapshot = e3 / 'fixtures/commits' / tag
        manifest = read(snapshot / 'commit.json')
        if manifest is None:
            continue
        require(manifest.get('commit') == sha, f'{tag}: manifest commit mismatch')
        files = manifest.get('files')
        if not require(isinstance(files, dict) and bool(files), f'{tag}: missing manifest files'):
            continue
        tree = git('ls-tree', '--name-only', f'{sha}:e3/fixtures/commits/lab')
        require(tree.returncode == 0 and set(tree.stdout.decode().splitlines()) == set(files), f'{tag}: incomplete manifest')
        for name, info in files.items():
            path = local_file(snapshot, name, f'{tag}/{name}')
            if path is None or not require(isinstance(info, dict), f'{tag}/{name}: invalid manifest entry'):
                continue
            data = path.read_bytes()
            blob = git('show', f'{sha}:e3/fixtures/commits/lab/{name}')
            require(blob.returncode == 0 and blob.stdout == data, f'{tag}/{name}: bytes differ from commit')
            require(info.get('sha256') == hashlib.sha256(data).hexdigest() and info.get('bytes') == len(data), f'{tag}/{name}: manifest hash/size mismatch')

    runs = sorted(p for p in (e3 / 'work').glob('*') if p.is_dir())
    members = set()
    for run in runs:
        commands = read(run / 'commands.json', list)
        obs = read(run / 'observations.json')
        env = read(run / 'environment.json')
        ids = {}
        if commands is not None:
            require(bool(commands), f'{run.name}: empty commands')
            for command in commands:
                if not require(isinstance(command, dict), f'{run.name}: command must be object'):
                    continue
                label = f'{run.name}/{command.get("id")}'
                require(isinstance(command.get('argv'), list) and bool(command['argv']), f'{label}: missing argv')
                require(bool(command.get('cwd')), f'{label}: missing cwd')
                require(type(command.get('exit_code')) is int, f'{label}: missing exit code')
                require(command.get('id') not in ids, f'{label}: duplicate command id')
                ids[command.get('id')] = command
                for stream in ('stdout', 'stderr'):
                    local_file(run, command.get(stream), f'{label}/{stream}')
        if obs is None:
            continue
        members.add(obs.get('member'))
        require(obs.get('observation_type') == 'ACTUAL_RUN' and obs.get('run_id') == run.name, f'{run.name}: invalid actual-run identity')
        if env is not None:
            require(env.get('member') == obs.get('member') and env.get('run_id') == run.name, f'{run.name}: environment/run mismatch')
        if obs.get('member') == 'A1':
            commit(obs.get('source_commit'), run.name)
        if obs.get('member') == 'A2':
            require(obs.get('commits') == refs, f'{run.name}: observation commits differ from expected')
            if env is not None and a2:
                require(env.get('configuration_id') == a2['configuration']['id'], f'{run.name}: configuration mismatch')
            outputs = {'c0-run': ('c0_clean_output', '10'), 'c1-incremental-run': ('c1_incremental_output', '12'),
                       'c1-touch-feature-run': ('c1_stale_output_after_feature_edit', '12'),
                       'c1-clean-rebuild-run': ('c1_clean_rebuild_output', '13'),
                       'c2-incremental-run': ('c2_incremental_output', '12'), 'c2-clean-rebuild-run': ('c2_clean_output', '19')}
            for label, (field, value) in outputs.items():
                command = ids.get(label, {})
                path = local_file(run, command.get('stdout'), f'{run.name}/{label}')
                require(obs.get(field) == value and path is not None and path.read_text().strip() == value, f'{run.name}/{label}: output inconsistent')
            require(obs.get('status') == 'PASSED' and obs.get('failures') == [], f'{run.name}: A2 baseline did not pass')
    require({'A1', 'A2'}.issubset(members), 'missing A1/A2 actual runs')

    schema = read(root / 'contracts/task.schema.json')
    if schema is not None:
        artifact = schema.get('$defs', {}).get('artifact', {})
        require(set(('artifact_id', 'type', 'uri', 'media_type', 'producer_job_id')).issubset(artifact.get('required', [])), 'E2 artifact fields changed')
    result = subprocess.run([__import__('sys').executable, str(e3 / 'scripts/a1_verify_evidence.py')], capture_output=True, text=True)
    require(result.returncode == 0, 'A1 deep evidence check failed: ' + result.stdout + result.stderr)
    if errors:
        for error in errors:
            print('FAIL:', error)
        return 1
    print(f'PASS: A-group E3 documentation, environment, expected answers, {len(runs)} runs, source commits and snapshot hashes; A1 deep check passed')
    print('Scope: saved A-group evidence only; B-group evidence and whole-team confirmation are not checked.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
