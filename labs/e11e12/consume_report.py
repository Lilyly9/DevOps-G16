"""Verify A's downloaded report and independently repair B's checkout."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

from pipeline import (
    ROOT, Failure, artifact, check_default_profile, full, patch, project_subdir,
    repair_input, save, snapshot, validate,
)
from draft.autobuild import auto_build
from draft_fullcheck import DraftExecutor
from project_profile import PROFILE_FILENAME, load_profile
from report_exchange import COMMIT, TRANSFER_SCHEMA, verify_report


def read_transfer(source, dest, target):
    """Preserve input bytes and confirm manifest, HTTP header and report agree."""
    dest.mkdir()
    data = {}
    for name in ('transfer-manifest.json', 'response-headers.json', 'incremental-check.json'):
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise Failure('INVALID_TRANSFER', f'Missing regular transfer file {name}')
        raw = path.read_bytes()
        (dest / name).write_bytes(raw)
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise Failure('INVALID_TRANSFER', f'{name} must be a JSON object')
        data[name] = (raw, value)

    manifest = data['transfer-manifest.json'][1]
    headers = data['response-headers.json'][1]
    raw_report, report = data['incremental-check.json']
    if manifest.get('schema_version') != TRANSFER_SCHEMA:
        raise Failure('SCHEMA_MISMATCH', f'Expected {TRANSFER_SCHEMA}')
    if manifest.get('kind') != 'incremental-check':
        raise Failure('ARTIFACT_TYPE_MISMATCH', 'Expected incremental-check transfer')
    if manifest.get('commit') != target:
        raise Failure('STALE_REPORT', 'Transferred commit differs from the requested B target')
    job = manifest.get('job_id')
    trace = manifest.get('trace_id')
    if not isinstance(job, str) or not re.fullmatch(r'job-[0-9a-f]{32}', job):
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Expected the original A job ID')
    if not isinstance(trace, str) or not re.fullmatch(r'trace-[0-9a-f]{32}', trace):
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Expected the original A trace ID')
    ref = manifest.get('report')
    if (not isinstance(ref, dict) or ref.get('uri') != f'artifact://{job}/incremental-check.json'
            or manifest.get('download_path') != f'/v1/jobs/{job}/files/incremental-check.json'):
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Transfer reference does not identify the A report')
    digest = hashlib.sha256(raw_report).hexdigest()
    header_hashes = [value for name, value in headers.items() if name.lower() == 'x-content-sha256']
    if ref.get('sha256') != digest or header_hashes != [digest] or ref.get('bytes') != len(raw_report):
        raise Failure('ARTIFACT_HASH_MISMATCH', 'Manifest, HTTP header and report bytes must agree')
    verify_report(report, job, trace, target)
    return manifest, report


def consume(request, transfer, out):
    out.mkdir(parents=True, exist_ok=False)
    job = 'job-' + uuid.uuid4().hex
    trace = 'trace-' + uuid.uuid4().hex
    result = {'schema_version': 'e11e12-consumption-1', 'job_id': job, 'trace_id': trace,
              'consumer_job_id': job, 'consumer_trace_id': trace, 'status': 'RUNNING', 'stages': []}
    save(out / 'request.json', request)

    def stage(kind, payload, files):
        envelope = {'schema_version': 'e11e12-1', 'kind': kind, 'status': 'SUCCEEDED',
                    'job_id': job, 'trace_id': trace, 'commit': result['target_commit'],
                    'data': payload, 'artifacts': [artifact(p, out, job) for p in files]}
        save(out / (kind + '.json'), envelope)
        result['stages'].append({'name': kind, 'artifact': artifact(out / (kind + '.json'), out, job)})

    try:
        target = request['target']
        if not isinstance(target, str) or not COMMIT.fullmatch(target):
            raise Failure('INVALID_TARGET', 'B requires a complete lowercase Git target SHA')
        result['target_commit'] = target
        manifest, report = read_transfer(transfer, out / 'transfer', target)
        payload = repair_input(report, target, 'incremental-check')
        result.update(source_job_id=manifest['job_id'], source_trace_id=manifest['trace_id'],
                      report_sha256=manifest['report']['sha256'], source_report=manifest['report'])
        subdir = project_subdir(request['project_path']) if 'project_path' in request else None
        if subdir != report.get('project_path'):
            raise Failure('REPORT_IDENTITY_MISMATCH', 'A report and B request select different project paths')
        profile_flag = request.get('profile', False)
        if not isinstance(profile_flag, bool):
            raise Failure('INVALID_PROFILE', 'profile must be a boolean')
        repo = Path(request['repo']).resolve()
        if not repo.is_dir() or out.resolve().is_relative_to(repo):
            raise Failure('INVALID_REQUEST', 'Local source repository and independent output are required')
        actual_target, project = snapshot(repo, target, out / 'target-project', out / 'logs', subdir)
        if actual_target != target:
            raise Failure('STALE_REPORT', 'B checkout resolved to a different commit')
        profile = None
        if profile_flag:
            profile = load_profile(project)
            profile.validate_sources(project)
        else:
            check_default_profile(project)
        profile_sha = profile.sha256 if profile else None
        if profile_sha != report.get('profile_sha256'):
            raise Failure('REPORT_IDENTITY_MISMATCH', 'A report and B checkout use different project profiles')
        if profile:
            (out / 'project-profile.json').write_bytes((project / PROFILE_FILENAME).read_bytes())
        result.update(project_path=subdir, profile_sha256=profile_sha)
        transfer_files = sorted((out / 'transfer').iterdir())
        stage('transfer-check', {key: result[key] for key in
              ('source_job_id', 'source_trace_id', 'report_sha256', 'source_report')}, transfer_files)

        before = (project / 'Makefile').read_bytes()
        diff, edits = patch(project, payload, isolate_shared_macros=True)
        if not diff:
            raise Failure('NO_MISSING_DEPENDENCY', 'Transferred report has no MD to repair')
        image = request.get('image_id')
        draft_files = []
        if 'image_id' in request:
            image_source = 'A_DRAFT_IMAGE_ID'
            draft = {'image_id': image, 'source_job_id': manifest['job_id']}
        else:
            image_source = 'B_DRAFT_CANDIDATE_REPLAY'
            candidate = Path(request['candidate']).resolve()
            expected = profile.expected_output if profile else request.get('expected_output', '1')
            draft = auto_build(project, candidate, out / 'draft-build', expected,
                               timeout=request.get('build_timeout', 600),
                               candidate_source='B local candidate replay from independent checkout')
            if draft['status'] != 'SUCCEEDED':
                raise Failure('DRAFT_FAILED', draft.get('error', 'Inspect independent B DRAFT logs'))
            image = draft['attempts'][-1]['image_id']
            draft_files.append(out / 'draft-build/result.json')
        executor = DraftExecutor(image, os.environ.get('E11E12_DOCKER_HOST_ROOT'), ROOT)
        result.update(image_id=image, image_source=image_source)
        stage('draft', dict(draft, image_id=image, image_source=image_source), draft_files)

        patchfile = out / 'candidate.patch'
        patchfile.write_text(diff, encoding='utf-8')
        save(out / 'repair-plan.json', edits)
        stage('repair', {'input_report': manifest['report'], 'edits': edits},
              [patchfile, out / 'repair-plan.json', out / 'transfer/incremental-check.json'])
        try:
            verdict = validate(project, patchfile, out / 'validation', profile=profile, runner=executor.capture)
            if not verdict['accepted']:
                raise Failure('REPAIR_REJECTED', str(verdict))
            final = full(project, out / 'final-full', executor, profile)
            if any(f['type'] == 'MISSING' for f in final['findings']):
                raise Failure('RECHECK_FAILED', 'Independent B dynamic recheck still reports MD')
        except (ValueError, OSError, subprocess.TimeoutExpired, TimeoutError):
            (project / 'Makefile').write_bytes(before)
            raise
        validation_files = sorted((out / 'validation/execution').glob('*.json'))
        stage('recheck', {'validation': verdict, 'findings': final['findings'], 'image_id': image},
              [out / 'validation/validation.json', out / 'final-full/findings.json',
               out / 'final-full/clean-execution.json', out / 'final-full/build-execution.json', *validation_files])
        save(out / 'verification.json', {
            'passed': True, 'consumer_job_id': job, 'consumer_trace_id': trace,
            'source_job_id': result['source_job_id'], 'source_trace_id': result['source_trace_id'],
            'target_commit': target, 'report_sha256': result['report_sha256'],
            'project_path': subdir, 'profile_sha256': profile_sha, 'image_id': image,
            'image_source': image_source,
            'accepted': True, 'findings': final['findings'],
        })
        result['status'] = 'SUCCEEDED'
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired, TimeoutError) as exc:
        timed_out = isinstance(exc, (subprocess.TimeoutExpired, TimeoutError))
        result.update(status='TIMED_OUT' if timed_out else 'FAILED',
                      error={'code': getattr(exc, 'code', 'TIMEOUT' if timed_out else 'CONSUMPTION_FAILED'),
                             'message': str(exc)})
    result['artifacts'] = [artifact(p, out, job) for p in sorted(out.rglob('*'))
                           if p.is_file() and '.git' not in p.parts and not p.is_symlink()]
    save(out / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--transfer', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_bytes())
    result = consume(request, args.transfer.resolve(), args.out.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'SUCCEEDED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
