"""B2 C5 evidence: real Git rejection locally; optional same-image Linux checks."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / 'labs/e11e12'), str(ROOT / 'labs/e8e10')]
import pipeline
from lab import fixture, patch, run


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_hashes(project):
    return {p.name: digest(p) for p in project.iterdir() if p.is_file()}


def case(folder, kind, executor):
    project = folder / 'project'
    fixture(project)
    commit = run(['git', 'rev-parse', 'HEAD'], project).strip()
    before = source_hashes(project)
    report = {'commit': commit, 'findings': [
        {'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'},
    ]}
    diff, edits = patch(project, report, isolate_shared_macros=True)
    candidate = folder / 'candidate.patch'
    candidate.write_bytes((
        'not a unified patch\n' if kind == 'malformed'
        else diff.replace('+main.o: main.c unused.h config.h',
                          '+main.o: main.c unused.h extra.h') if kind == 'wrong-dependency'
        else diff
    ).encode('utf-8'))
    job, trace = 'job-' + uuid.uuid4().hex, 'trace-' + uuid.uuid4().hex
    pipeline.save(folder / 'request.json', {
        'case': kind, 'scope': 'isolated MDFixer C5; not the shared five-stage API',
        'commit': commit, 'job_id': job, 'trace_id': trace,
        'image_id': None if executor is None else executor.image_id,
        'patch_sha256': digest(candidate),
    })
    pipeline.save(folder / 'repair-plan.json', edits)
    rejected = None
    try:
        verdict, final = pipeline.validate_repair(
            project, candidate, folder, executor, None,
            commit=commit, job_id=job, trace_id=trace,
        )
    except pipeline.Failure as exc:
        rejected = {'code': exc.code, 'message': str(exc)}
    if kind in ('malformed', 'wrong-dependency'):
        require(rejected is not None and rejected['code'] == 'REPAIR_REJECTED',
                'The bad candidate must fail validation')
        require(source_hashes(project) == before, 'Rejected patch changed source files')
        require(run(['git', 'rev-parse', 'HEAD'], project).strip() == commit,
                'Rejected patch changed the target commit')
        rollback = json.loads((folder / 'rollback.json').read_text(encoding='utf-8'))
        validation = json.loads((folder / 'validation/validation.json').read_text(encoding='utf-8'))
        require(rollback['rollback'] and not validation['accepted'], 'Rollback evidence missing')
        require(not (folder / 'final-full').exists(), 'Rejected patch reached the final check')
        if kind == 'wrong-dependency':
            require(validation['checks']['patch_applies'] and validation['checks']['build']
                    and validation['checks']['test'], 'Wrong-dependency patch must apply and build')
            require(not validation['checks']['header_change']
                    and not validation['checks']['no_missing'],
                    'The semantic failure must be detected by incremental execution and GCC')
        result = {'expected_rejection': True, 'error': rejected, 'rollback': rollback}
    else:
        require(rejected is None, f'Recovery candidate was rejected: {rejected}')
        require(verdict['accepted'] and all(f['type'] != 'MISSING' for f in final['findings']),
                'Recovery must pass validation and the real strace recheck')
        require(digest(project / 'config.h') == before['config.h'],
                'Header-change validation escaped its sandbox')
        result = {'accepted': True, 'findings': final['findings']}
    result.update(job_id=job, trace_id=trace, commit_before=commit,
                  commit_after=run(['git', 'rev-parse', 'HEAD'], project).strip(),
                  source_hashes_before=before, source_hashes_after=source_hashes(project),
                  patch_sha256=digest(candidate))
    pipeline.save(folder / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--draft-result', type=Path,
                        help='Successful DRAFT result.json; enables same-image Linux + Docker checks')
    args = parser.parse_args()
    out = (ROOT / args.out).resolve()
    if out.parent != ROOT / 'work' or out.exists():
        parser.error('--out must be a fresh work/<run-id> directory')
    if args.draft_result and os.name != 'posix':
        parser.error('Same-image validation requires the Linux Docker environment')
    executor = None
    draft_reference = None
    image_id = None
    if args.draft_result:
        draft_path = (ROOT / args.draft_result).resolve()
        draft = json.loads(draft_path.read_text(encoding='utf-8'))
        require(draft['status'] == 'SUCCEEDED', 'DRAFT result must have succeeded')
        image_id = draft['attempts'][-1]['image_id']
        draft_reference = {'path': str(draft_path), 'sha256': digest(draft_path), 'image_id': image_id}
        from draft_fullcheck import DraftExecutor
        executor = DraftExecutor(image_id, os.environ.get('E11E12_DOCKER_HOST_ROOT', str(ROOT)), ROOT)
    out.mkdir(parents=True)
    summary = {
        'runner_sha': run(['git', 'rev-parse', 'HEAD'], ROOT).strip(),
        'platform': sys.platform, 'python': sys.version,
        'image_id': image_id, 'draft_result': draft_reference, 'cases': {},
        'implementation_sha256': {str(p.relative_to(ROOT)): digest(p) for p in (
            ROOT / 'labs/e8e10/lab.py', ROOT / 'labs/e11e12/pipeline.py', Path(__file__).resolve(),
        )},
        'scope': 'real Git malformed-patch rejection only' if executor is None
                 else 'isolated C5 with real same-image build, test and strace recheck',
    }
    pipeline.save(out / 'summary.json', summary)
    try:
        kinds = ('malformed',) if executor is None else ('malformed', 'wrong-dependency', 'recovery')
        for kind in kinds:
            summary['cases'][kind] = case(out / kind, kind, executor)
            pipeline.save(out / 'summary.json', summary)
    except (ValueError, OSError, TimeoutError, subprocess.TimeoutExpired) as exc:
        summary.update(status='FAILED', error=str(exc))
        pipeline.save(out / 'summary.json', summary)
        print(str(exc), file=sys.stderr)
        return 1
    summary['status'] = 'SUCCEEDED'
    if executor is None:
        summary['pending'] = ['semantic wrong-dependency rollback', 'same-image recovery and strace',
                              'H1 jsmn', 'E14 four-container E2E', 'push, PR and remote CI']
    pipeline.save(out / 'summary.json', summary)
    print(json.dumps({'status': summary['status'], 'scope': summary['scope'], 'out': str(out)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
