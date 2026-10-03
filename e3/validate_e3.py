#!/usr/bin/env python3
"""Offline completeness check for the A-group E3 baseline; no tool accuracy claims."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E3 = ROOT / 'e3'
errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

def load(path):
    check(path.is_file(), f'missing: {path.relative_to(ROOT)}')
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        errors.append(f'invalid JSON: {path.relative_to(ROOT)}: {exc}')
        return None

for member in ('A1', 'A2'):
    check((E3 / 'env' / f'toolchain-{member}.txt').is_file(), f'missing environment: {member}')
for name in ('buildchecker-md-rd.json', 'echecker-c0-c1-c2.json'):
    item = load(E3 / 'expected' / name)
    if item:
        check(item.get('provenance') in ('INSTRUCTOR_ORACLE', 'MANUAL_EXPECTED'), f'bad provenance: {name}')
        check(bool(item.get('findings') or item.get('versions')), f'empty expected findings/versions: {name}')

runs = sorted((E3 / 'work').iterdir())
for member in ('A1', 'A2'):
    check(any(run.is_dir() and f'-{member}-' in run.name for run in runs), f'no run for {member}')
for run in runs:
    if not run.is_dir():
        continue
    commands = load(run / 'commands.json')
    observations = load(run / 'observations.json')
    if isinstance(commands, list):
        check(bool(commands), f'no commands: {run.name}')
        for command in commands:
            check(isinstance(command.get('exit_code'), int), f'missing exit code: {run.name}/{command.get("id")}')
            for stream in ('stdout', 'stderr'):
                value = command.get(stream)
                check(isinstance(value, str) and (run / value).is_file(), f'missing {stream} log: {run.name}/{command.get("id")}')
    if isinstance(observations, dict):
        check(observations.get('observation_type') == 'ACTUAL_RUN', f'not actual run: {run.name}')

expected = load(E3 / 'expected' / 'echecker-c0-c1-c2.json')
if expected:
    refs = expected.get('repository', {}).get('refs', {})
    for tag in ('C0', 'C1', 'C2'):
        sha = refs.get(tag, '')
        check(len(sha) == 40, f'bad SHA: {tag}')
        result = subprocess.run(['git', 'cat-file', '-e', f'{sha}^{{commit}}'], cwd=ROOT, capture_output=True)
        check(result.returncode == 0, f'unavailable commit: {tag} {sha}')
        snapshot = E3 / 'fixtures' / 'commits' / tag
        manifest = load(snapshot / 'commit.json')
        if isinstance(manifest, dict):
            check(manifest.get('commit') == sha, f'snapshot SHA mismatch: {tag}')
        for source in snapshot.iterdir():
            if source.name == 'commit.json' or not source.is_file():
                continue
            blob = subprocess.run(['git', 'show', f'{sha}:e3/fixtures/commits/lab/{source.name}'], cwd=ROOT, capture_output=True)
            check(blob.returncode == 0 and blob.stdout == source.read_bytes(), f'snapshot bytes differ: {tag}/{source.name}')

schema = load(ROOT / 'contracts' / 'task.schema.json')
if schema:
    artifact = schema.get('$defs', {}).get('artifact', {})
    check(set(('artifact_id', 'type', 'uri', 'media_type', 'producer_job_id')).issubset(artifact.get('required', [])), 'E2 artifact required fields changed')
    check('configuration_id' not in artifact.get('required', []), 'configuration_id unexpectedly required on artifact')

if errors:
    print('\n'.join(f'FAIL {item}' for item in errors), file=sys.stderr)
    sys.exit(1)
print('PASS: A-group E3 expected answers, run logs, refs, environment and E2 artifact fields')
