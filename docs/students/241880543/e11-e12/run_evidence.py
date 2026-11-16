"""Run B2's E11 and E12 evidence cases in a personal Linux checkout."""

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNNER = [sys.executable, 'run_e11e12.py']
MODULES = ('labs/e11e12', 'labs/e8e10', 'labs/e11e12/vendor')
CASES = ('fixed', 'macro', 'stale', 'e12', 'transfer-eta')
BASE = '5ef9d829e2f893af23f60399dcb67095800d121e'
TARGET = 'e7414083c4f1760cb234f96a9d75f2d0255e3f57'
PROJECT = 'projects/transfer-eta'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def prepare_inputs(folder, cases):
    """Resolve paths in the same filesystem view as the actual pipeline."""
    sys.path[:0] = [str(ROOT / path) for path in MODULES]
    from lab import commit, fixture, scan

    folder.mkdir(parents=True)
    standard = ROOT / 'data/integration-sample'
    standard_paths = {'repo': str(standard / 'repo'),
                      'candidate': str(standard / 'candidate.Dockerfile'),
                      'fixed_report': str(standard / 'fixed-md.json')}
    for case, mode in (('fixed', 'e11-b'), ('e12', 'e12')):
        if case in cases:
            request = read(standard / (mode + '.json'))
            request.update(standard_paths)
            write(folder / (case + '.json'), request)

    if set(cases) & {'macro', 'stale'}:
        project = folder / 'macro-project'
        fixture(project, style='macro')
        makefile = project / 'Makefile'
        makefile.write_text(makefile.read_text().replace(
            'helper.o: helper.c\n', 'helper.o: helper.c $(DEPS)\n'), encoding='utf-8')
        shutil.copyfile(standard / 'repo/Dockerfile.broken', project / 'Dockerfile.broken')
        base = commit(project, 'B2 baseline with a shared prerequisite variable')
        source = project / 'main.c'
        source.write_text('#include "extra.h"\n' + source.read_text(), encoding='utf-8')
        target = commit(project, 'B2 target with an undeclared extra.h dependency')
        envelope = {'schema_version': 'e11e12-1', 'kind': 'fixed-md', 'status': 'SUCCEEDED',
                    'commit': target, 'data': scan(project)}
        stale = copy.deepcopy(envelope)
        stale['data']['commit'] = base
        template = dict(read(standard / 'e11-b.json'), **standard_paths)
        for case, report in (('macro', envelope), ('stale', stale)):
            if case in cases:
                report_path = folder / (case + '-report.json')
                write(report_path, report)
                write(folder / (case + '.json'), dict(template, repo=str(project), base=base,
                                                    target=target, fixed_report=str(report_path)))

    if 'transfer-eta' in cases:
        git('cat-file', '-e', BASE + '^{commit}')
        candidate = git('show', f'{TARGET}:{PROJECT}/candidate.Dockerfile')
        candidate_path = folder / 'transfer-eta.Dockerfile'
        candidate_path.write_bytes(candidate)
        project = folder / 'transfer-eta-repo'
        subprocess.run(['git', 'clone', '--no-hardlinks', '--no-checkout', str(ROOT), str(project)],
                       check=True)
        write(folder / 'transfer-eta.json', {'mode': 'e12', 'repo': str(project),
              'project_path': PROJECT, 'profile': True, 'base': BASE, 'target': TARGET,
              'candidate': str(candidate_path), 'build_timeout': 600})


def record_command(command, logs, name, env=None):
    write(logs / (name + '.command.json'), command)
    with (logs / (name + '.log')).open('wb') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    (logs / (name + '.exit')).write_text(f'{result.returncode}\n', encoding='utf-8')
    return result.returncode


def check_case(case, out, code, mounted_root):
    result = read(out / 'result.json')
    target = result['target_commit']
    request = read(out / 'request.json')
    draft = read(out / 'draft-build/result.json')
    expected_output = 'eta_seconds=13' if case == 'transfer-eta' else '1'
    require(draft['status'] == 'SUCCEEDED', draft.get('error', 'DRAFT did not succeed'))
    initial, repaired = draft['attempts']
    verification = draft['verification']
    image = repaired['image_id']
    require(initial['build_exit_code'] != 0 and initial['failure_class'] == 'MISSING_MAKE',
            'Initial DRAFT build must fail on missing Make')
    require(repaired['build_exit_code'] == 0 and verification['command'][-1] == image
            and verification['exit_code'] == 0 and verification['output_matches']
            and verification['actual_output'].strip() == expected_output,
            'DRAFT candidate must run in its built image and produce the expected output')
    summary = {key: result[key] for key in ('job_id', 'trace_id', 'base_commit', 'target_commit', 'status')}
    summary.update(exit_code=code, image_id=image, initial_failure=initial['failure_class'],
                   draft_output=verification['actual_output'].strip(),
                   candidate_sha256=sha256(ROOT / Path(request['candidate']).relative_to(mounted_root)))

    if 'fixed_report' in request and request['mode'] == 'e11-b':
        fixed = ROOT / Path(request['fixed_report']).relative_to(mounted_root)
        envelope = read(fixed)
        inner_commit = envelope['data']['commit']
        require(envelope['schema_version'] == 'e11e12-1' and envelope['kind'] == 'fixed-md'
                and envelope['status'] == 'SUCCEEDED' and envelope['commit'] == target,
                'Fixed envelope header must match the target commit and declared schema')
        summary['fixed_report'] = {'path': str(fixed.relative_to(ROOT)), 'sha256': sha256(fixed),
                                   'outer_commit': target, 'data_commit': inner_commit}
        expected_commit = result['base_commit'] if case == 'stale' else target
        require(inner_commit == expected_commit, 'Unexpected fixed report data.commit')

    if case == 'stale':
        require(code == 1 and result['status'] == 'FAILED' and result['error']['code'] == 'STALE_REPORT',
                'Old data.commit must stop with STALE_REPORT')
        require([stage['name'] for stage in result['stages']] == ['draft']
                and all(not (out / name).exists() for name in
                        ('candidate.patch', 'repair-plan.json', 'repair.json', 'validation')),
                'Stale input must leave no repair or validation artifact')
        summary['error'] = result['error']
        return summary

    require(code == 0 and result['status'] == 'SUCCEEDED', 'Pipeline did not succeed')
    recheck = read(out / 'recheck.json')['data']
    findings = recheck['findings']
    require(recheck['validation']['accepted'] and all(f['type'] != 'MISSING' for f in findings),
            'Repair must be accepted with no remaining MD')
    plan = read(out / 'repair-plan.json')
    expected_edits = ({('eta_cli.o', 'defaults.h')} if case == 'transfer-eta'
                      else {('main.o', 'config.h'), ('main.o', 'extra.h')})
    require(len(plan) == len(expected_edits)
            and {(p['target'], p['dependency']) for p in plan} == expected_edits,
            'Unexpected repair targets or dependencies')
    summary.update(edits=plan, findings=findings, accepted=True)
    input_kind = 'fixed-md' if request['mode'] == 'e11-b' else 'incremental-check'
    source = read(out / 'repair.json')['data']['input_report']
    require(source['uri'] == f"artifact://{result['job_id']}/{input_kind}.json"
            and source['sha256'] == sha256(out / (input_kind + '.json')),
            'Repair must cite the actual input report')
    summary['input_report'] = source

    if case == 'macro':
        diff = (out / 'candidate.patch').read_text(encoding='utf-8').splitlines()
        changed = [line for line in diff if line.startswith(('+', '-'))
                   and not line.startswith(('+++', '---'))]
        require(len(changed) == 2 and changed[0] == '-main.o: $(DEPS)'
                and changed[1].split()[:2] == ['+main.o:', '$(DEPS)']
                and set(changed[1].split()[2:]) == {'config.h', 'extra.h'}
                and all(edit['style'] == 'mixed' for edit in plan),
                'Shared macro repair must modify only the intended target rule')

    if request['mode'] == 'e12':
        stages = [stage['name'] for stage in result['stages']]
        require(stages == ['draft', 'full-check', 'incremental-check', 'repair', 'recheck'],
                'E12 stage order changed')
        for name in stages:
            report = read(out / (name + '.json'))
            require(report['job_id'] == result['job_id'] and report['trace_id'] == result['trace_id']
                    and report['commit'] == (result['base_commit'] if name == 'full-check' else target),
                    f'{name} stage identity mismatch')
        validation_records = list((out / 'validation/execution').glob('*.json'))
        require(bool(validation_records), 'Same-image validation records are missing')
        for record_path in validation_records + [out / 'final-full/build-execution.json']:
            record = read(record_path)
            require(record['actual_image_id'] == image and record['container_exit_code'] == 0,
                    f'{record_path.name} must succeed in the original DRAFT image')
        summary['same_image_validation_commands'] = len(validation_records)
        if case == 'transfer-eta':
            outputs = recheck['validation']['outputs']
            require(outputs['actual'] == 'eta_seconds=13'
                    and outputs['actual_after_header_change'] == 'eta_seconds=20'
                    and not findings, 'transfer-eta profile output or final findings changed')
            summary['outputs'] = outputs
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Fresh directory directly under work/')
    parser.add_argument('--backend', choices=('course', 'native'), default='course')
    parser.add_argument('--cases', choices=CASES, nargs='+', default=CASES)
    parser.add_argument('--make-inputs', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.make_inputs:
        prepare_inputs(args.out, args.cases)
        return 0
    if os.name != 'posix':
        parser.error('Run from Linux with a working local Docker daemon')
    out = (ROOT / args.out).resolve()
    if out.parent != ROOT / 'work' or not re.fullmatch(r'[A-Za-z0-9_-]+', out.name):
        parser.error('--out must name a fresh work/<run-id> directory')
    data = ROOT / 'data' / out.name
    if out.exists() or data.exists() or len(set(args.cases)) != len(args.cases):
        parser.error('Output and input directories must be fresh, and cases must be unique')
    logs = out / 'logs'
    logs.mkdir(parents=True)
    mounted_root = Path('/course') if args.backend == 'course' else ROOT
    summary = {'runner_sha': git('rev-parse', 'HEAD').decode().strip(), 'backend': args.backend,
               'out': str(out), 'inputs': str(data), 'cases': {}}
    write(out / 'summary.json', summary)
    require(record_command(['docker', 'version'], logs, 'docker') == 0, 'Docker is unavailable')

    env = dict(os.environ, E11E12_DOCKER_HOST_ROOT=str(ROOT),
               PYTHONPATH=os.pathsep.join(str(ROOT / path) for path in MODULES))
    python = [sys.executable]
    if args.backend == 'course':
        sid = git('config', '--local', 'user.name').decode().strip()
        require(re.fullmatch(r'[0-9]{6,16}', sid), 'Set local Git user.name to your numeric student ID')
        image = 'course-e11e12:' + sid
        require(record_command(['docker', 'image', 'inspect', '--format', '{{.Id}}', image],
                               logs, 'course-image') == 0, f'Build {image} with run_e11e12.py build first')
        python = ['docker', 'run', '--rm', '--network', 'none', '--user', f'{os.getuid()}:{os.getgid()}',
                  '-e', 'HOME=/tmp', '-v', f'{ROOT}:/course', '-w', '/course', image, 'python3']

    standard = ROOT / 'data/integration-sample'
    if set(args.cases) - {'transfer-eta'} and not standard.exists():
        command = RUNNER + ['prepare'] if args.backend == 'course' else python + ['labs/e11e12/prepare.py']
        require(record_command(command, logs, 'prepare', env) == 0, 'Course sample preparation failed')
    inputs = mounted_root / data.relative_to(ROOT)
    script = Path(__file__).resolve().relative_to(ROOT)
    command = python + [str(script), '--make-inputs', '--out', str(inputs), '--cases', *args.cases]
    require(record_command(command, logs, 'prepare-b2-inputs', env) == 0, 'B2 input preparation failed')

    failed = False
    for case in args.cases:
        print(f'Running {case} in {out / case}', flush=True)
        request = (data / (case + '.json')).relative_to(ROOT)
        case_out = (out / case).relative_to(ROOT)
        entry = RUNNER + ['run'] if args.backend == 'course' else python + ['labs/e11e12/pipeline.py']
        command = entry + ['--request', str(request), '--out', str(case_out)]
        code = record_command(command, logs, case, env)
        try:
            summary['cases'][case] = check_case(case, ROOT / case_out, code, mounted_root)
        except (KeyError, OSError, ValueError) as error:
            summary['cases'][case] = {'exit_code': code, 'evidence_error': str(error)}
            failed = True
        write(out / 'summary.json', summary)
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
