"""Compose the existing E5-E10 teaching components using versioned artifacts."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'labs/e8e10'), str(ROOT / 'labs/e11e12/vendor'),
                str(ROOT / 'labs/e11e12/environment/services/buildchecker')]
from lab import scan, patch, validate

class Failure(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def artifact(path, out, job_id):
    return {'uri': f'artifact://{job_id}/{path.relative_to(out).as_posix()}',
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes':path.stat().st_size}

def check_envelope(report, commit, kind=None):
    if report.get('schema_version') != 'e11e12-1':
        raise Failure('SCHEMA_MISMATCH', 'Expected e11e12-1')
    if report.get('commit') != commit:
        raise Failure('STALE_REPORT', 'Report belongs to another commit')
    if report.get('status') != 'SUCCEEDED':
        raise Failure('UPSTREAM_FAILED', 'Upstream stage did not succeed')
    if kind and report.get('kind') != kind:
        raise Failure('ARTIFACT_TYPE_MISMATCH', kind)

def load_artifact(path, expected_sha256):
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=expected_sha256:
        raise Failure('ARTIFACT_HASH_MISMATCH','Artifact content changed during transfer')
    return json.loads(data)

def command(argv, cwd, log):
    log.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=120)
    log.write_text(p.stdout+p.stderr, encoding='utf-8')
    if p.returncode:
        raise Failure('COMMAND_FAILED', f'{argv[0]} failed; see {log.name}')
    return p.stdout.strip()

def project_subdir(value):
    if not isinstance(value, str) or not value or any(
        not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', part)
        for part in value.split('/')
    ):
        raise Failure('INVALID_PROJECT_PATH', 'project_path must be a relative directory within the selected Git commit')
    return value


def snapshot(repo, revision, dest, logs, subdir=None):
    sha = command(['git','rev-parse','--verify','--end-of-options',revision+'^{commit}'], repo, logs/(dest.name+'-resolve.log'))
    command(['git','clone','--no-hardlinks','--no-checkout',repo.as_posix(),dest.as_posix()], repo, logs/(dest.name+'-clone.log'))
    if subdir:
        command(['git','sparse-checkout','set','--no-cone','--',f'/{subdir}/'],
                dest, logs/(dest.name+'-scope.log'))
    command(['git','checkout','--detach',sha], dest, logs/(dest.name+'-checkout.log'))
    project = dest if subdir is None else dest/subdir
    if not project.is_dir() or project.resolve() != project:
        raise Failure('UNSUPPORTED_PROJECT', 'Selected project directory must exist in both Git commits')
    return sha, project


def check_default_profile(project):
    # E8-E10 profile; fail early instead of silently ignoring other targets.
    names = {p.name for p in project.glob('*.c')}
    if names != {'main.c','helper.c'} or not (project/'config.h').is_file():
        raise Failure('UNSUPPORTED_PROJECT', 'Expected main.c/helper.c/config.h and explicit Make rules')

def full(project, folder, executor=None, profile=None):
    from buildchecker.fullcheck import full_check
    options = {'executor':executor} if executor is not None else {}
    if profile is not None:
        options.update(clean_command=f'make {profile.clean_target}', build_command=f'make {profile.build_target}')
    report = full_check(project, folder, **options)
    if report.get('status') != 'SUCCEEDED':
        raise Failure('FULL_CHECK_FAILED', str(report.get('error', report.get('error_code'))))
    return report

def normalized(findings, targets):
    return sorted((f['type'],f['target'],f['dependency']) for f in findings if f['target'] in targets)

def execute(request, out, job_id=None):
    job_id = job_id or 'job-'+uuid.uuid4().hex
    trace_id = 'trace-'+uuid.uuid4().hex
    if out.exists() and any(out.iterdir()):
        raise Failure('OUTPUT_EXISTS', 'Use a fresh output directory')
    out.mkdir(parents=True, exist_ok=True)
    result = {'schema_version':'e11e12-1','job_id':job_id,'trace_id':trace_id,'status':'RUNNING','stages':[]}
    save(out/'request.json',request)
    project_context = {}
    def stage(name, commit, payload, files=()):
        envelope = {'schema_version':'e11e12-1','job_id':job_id,'trace_id':trace_id,'kind':name,
                    'commit':commit,'status':'SUCCEEDED','data':payload,
                    'artifacts':[artifact(p,out,job_id) for p in files], **project_context}
        save(out/(name+'.json'),envelope)
        result['stages'].append({'name':name,'artifact':artifact(out/(name+'.json'),out,job_id)})
        return envelope
    try:
        mode=request['mode']
        if mode not in ('e11-a','e11-b','e12'):
            raise Failure('INVALID_REQUEST','Unknown mode')
        repo=Path(request['repo']).resolve()
        if not repo.is_dir():
            raise Failure('INVALID_REQUEST','Repository missing')
        subdir = project_subdir(request['project_path']) if 'project_path' in request else None
        if 'profile' in request and not isinstance(request['profile'], bool):
            raise Failure('INVALID_PROFILE', 'profile must be a boolean')
        if subdir:
            project_context['project_path'] = subdir
        base_sha,base=snapshot(repo,request['base'],out/'base-project',out/'logs',subdir)
        target_sha,target=snapshot(repo,request['target'],out/'target-project',out/'logs',subdir)
        result.update(base_commit=base_sha,target_commit=target_sha)
        profile = None
        if request.get('profile'):
            from project_profile import PROFILE_FILENAME, load_profile
            try:
                profile = load_profile(target)
                profile.validate_sources(base)
                profile.validate_sources(target)
            except (OSError, ValueError) as exc:
                raise Failure('INVALID_PROFILE', str(exc)) from exc
            shutil.copyfile(target/PROFILE_FILENAME,out/'project-profile.json')
            project_context['profile_sha256'] = profile.sha256
        else:
            check_default_profile(base)
            check_default_profile(target)
        result.update(project_context)
        targets = ('main.o','helper.o') if profile is None else profile.targets
        scan_options = {} if profile is None else {'targets':targets}
        draft_executor=None
        if mode in ('e11-b','e12'):
            from draft.autobuild import auto_build
            candidate=Path(request['candidate']).resolve()
            expected = request.get('expected_output','1') if profile is None else profile.expected_output
            draft_options = {}
            if profile is not None:
                draft_options['candidate_source'] = 'Repository project candidate replay; no model/API call during DRAFT'
            draft=auto_build(target,candidate,out/'draft-build',expected,timeout=request.get('build_timeout',600),**draft_options)
            if draft['status']!='SUCCEEDED':
                raise Failure('DRAFT_FAILED',draft.get('error','Inspect draft-build logs'))
            stage('draft',target_sha,draft,[out/'draft-build/result.json'])
            if mode=='e12':
                from draft_fullcheck import DraftExecutor
                try:
                    draft_executor=DraftExecutor(draft['attempts'][-1]['image_id'],
                                                 os.environ.get('E11E12_DOCKER_HOST_ROOT'), ROOT)
                except (ValueError, KeyError, IndexError) as exc:
                    raise Failure('DRAFT_EXECUTION_UNAVAILABLE', str(exc)) from exc
        if mode in ('e11-a','e12'):
            base_full=full(base,out/'baseline-full',draft_executor,profile)
            run_scans_in_draft = draft_executor is not None and profile is not None
            base_scan_options = dict(scan_options)
            target_scan_options = dict(scan_options)
            if run_scans_in_draft:
                base_scan_options['execute'] = draft_executor.capture(out/'baseline-scan')
                target_scan_options['execute'] = draft_executor.capture(out/'target-scan')
            old=scan(base,**base_scan_options)
            edges=json.loads((out/'baseline-full/actual-graph.json').read_text())
            projected={t:sorted({e['dependency'] for e in edges if e['target']==t}) for t in targets}
            if projected != old['actual']:
                raise Failure('GRAPH_MISMATCH','BuildChecker baseline differs from GCC observations')
            old['actual']=projected
            save(out/'baseline-cache.json',old)
            baseline_files=[out/'baseline-full/actual-graph.json',out/'baseline-full/findings.json',out/'baseline-cache.json']
            if draft_executor:
                baseline_files += [out/'baseline-full'/f for f in ('clean-execution.json','build-execution.json')]
            if profile is not None:
                baseline_files.append(out/'project-profile.json')
            if run_scans_in_draft:
                baseline_files.extend(sorted((out/'baseline-scan').glob('*.json')))
            baseline=stage('full-check',base_sha,base_full,baseline_files)
            check_envelope(baseline,base_sha,'full-check')
            current=scan(target,old,**target_scan_options)
            save(out/'incremental-report.json',current)
            reference=full(target,out/'target-full',draft_executor,profile)
            if normalized(reference['findings'],targets) != normalized(current['findings'],targets):
                raise Failure('FINDINGS_MISMATCH','Incremental/full object-target findings differ')
            increment_files=[out/'incremental-report.json',out/'target-full/findings.json']
            if draft_executor:
                increment_files += [out/'target-full'/f for f in ('clean-execution.json','build-execution.json')]
            if run_scans_in_draft:
                increment_files.extend(sorted((out/'target-scan').glob('*.json')))
            md_envelope=stage('incremental-check',target_sha,current,increment_files)
        else:
            # E11-B still consumes a fixed MD input, separately from A's live output.
            fixed=Path(request['fixed_report'])
            envelope=json.loads(fixed.read_text(encoding='utf-8'))
            check_envelope(envelope,target_sha,'fixed-md')
            current=envelope['data']
            if current.get('commit') != target_sha:
                raise Failure('STALE_REPORT','Fixed report data commit mismatch')
            save(out/'fixed-md-input.json',envelope)
            md_envelope=stage('fixed-md',target_sha,current,[out/'fixed-md-input.json'])
        if mode in ('e11-b','e12'):
            reference=result['stages'][-1]['artifact']
            md_envelope=load_artifact(out/(md_envelope['kind']+'.json'),reference['sha256'])
            check_envelope(md_envelope,target_sha)
            current=md_envelope['data']
            before=(target/'Makefile').read_bytes()
            diff,edits=patch(target,current)
            if not diff:
                raise Failure('NO_MISSING_DEPENDENCY','No MD to repair')
            patchfile=out/'candidate.patch';patchfile.write_text(diff,encoding='utf-8')
            save(out/'repair-plan.json',edits)
            stage('repair',target_sha,{'edits':edits,'input_report':artifact(out/(md_envelope['kind']+'.json'),out,job_id)},[patchfile,out/'repair-plan.json'])
            validation_runner = draft_executor.capture if draft_executor is not None and profile is not None else None
            verdict=validate(target,patchfile,out/'validation',profile=profile,runner=validation_runner)
            if not verdict['accepted']:
                raise Failure('REPAIR_REJECTED',str(verdict))
            final=full(target,out/'final-full',draft_executor,profile)
            if any(f['type']=='MISSING' for f in final['findings']):
                (target/'Makefile').write_bytes(before)
                raise Failure('RECHECK_FAILED','MD remains; working-copy declaration restored')
            recheck_files=[out/'validation/validation.json',out/'final-full/findings.json']
            if draft_executor:
                recheck_files += [out/'final-full'/f for f in ('clean-execution.json','build-execution.json')]
            if validation_runner:
                recheck_files.extend(sorted((out/'validation/execution').glob('*.json')))
            stage('recheck',target_sha,{'validation':verdict,'findings':final['findings'],'patched_makefile_sha256':hashlib.sha256((target/'Makefile').read_bytes()).hexdigest()},recheck_files)
        result['status']='SUCCEEDED'
    except (Failure,ValueError,OSError,KeyError,subprocess.TimeoutExpired) as exc:
        result.update(status='TIMED_OUT' if isinstance(exc,subprocess.TimeoutExpired) else 'FAILED',error={'code':getattr(exc,'code','EXECUTION_FAILED'),'message':str(exc)})
    result['artifacts']=[artifact(p,out,job_id) for p in sorted(out.rglob('*')) if p.is_file() and '.git' not in p.parts and not p.is_symlink()]
    save(out/'result.json',result)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--request',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=execute(json.loads(a.request.read_text(encoding='utf-8')),a.out.resolve());print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['status']=='SUCCEEDED' else 1

if __name__=='__main__':raise SystemExit(main())
