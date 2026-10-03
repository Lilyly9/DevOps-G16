#!/usr/bin/env python3
"""Read E4 A-group evidence and compare runs; writes only the requested review output."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

REQUIRED = ('env.json', 'build.log', 'image.json', 'toolchain.lock', 'test.log', 'smoke.json', 'secret-scan.txt')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True, help='shared repository clone root')
    parser.add_argument('--run', type=Path, action='append', required=True, help='successful evidence directory; repeat for comparison')
    parser.add_argument('--scan', action='store_true', help='independently scan this repository/history and the image recorded by each run')
    parser.add_argument('--out', type=Path, required=True, help='new output JSON; existing files are not overwritten')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('output already exists; choose a new review path')
    repo = args.repo.resolve()
    errors, records = [], []

    def command(argv):
        return subprocess.run(argv, capture_output=True, text=True)

    def check(condition, message):
        if not condition:
            errors.append(message)
        return bool(condition)

    def read_json(path):
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            errors.append(f'{path}: invalid/missing JSON ({type(exc).__name__})')
            return None

    for run in args.run:
        run = run.resolve()
        prefix = str(run)
        record = {'directory':prefix, 'files':{}}
        records.append(record)
        missing = []
        for name in REQUIRED:
            path = run / name
            if not path.is_file():
                missing.append(name)
                continue
            data = path.read_bytes()
            record['files'][name] = {'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}
        if not check(not missing, f'{prefix}: missing evidence {missing}'):
            continue
        env, smoke, image = (read_json(run / name) for name in ('env.json','smoke.json','image.json'))
        if not check(isinstance(env,dict) and isinstance(smoke,dict), f'{prefix}: env/smoke must be objects'):
            continue
        sha = env.get('template_sha')
        record['template_sha'] = sha
        check(isinstance(sha,str) and re.fullmatch('[0-9a-f]{40}',sha)
              and command(['git','-C',str(repo),'cat-file','-e',f'{sha}^{{commit}}']).returncode == 0, f'{prefix}: template SHA unavailable')
        check(env.get('template_subdirectory') == 'e4/A-buildchecker', f'{prefix}: wrong template subdirectory')
        check(env.get('problems') == [], f'{prefix}: doctor problems not empty')
        identity = env.get('git',{}).get('user.name')
        record['student_id'] = identity
        check(isinstance(identity,str) and identity.isdigit(), f'{prefix}: Git identity not a student number')
        test = (run/'test.log').read_text(errors='replace')
        check(re.search(r'\b3 passed\b',test) is not None and not re.search(r'\b[1-9][0-9]* (failed|error|errors)\b',test), f'{prefix}: unit test gate not passed')
        record['test_passed'] = bool(re.search(r'\b3 passed\b',test))
        smoke_gate = {'make_exit_code':smoke.get('make_exit_code'), 'app_output':smoke.get('app_output'),
                      'config_h_opened':bool(smoke.get('config_h_opened')), 'passed':smoke.get('passed')}
        record['smoke'] = smoke_gate
        check(type(smoke.get('make_exit_code')) is int and smoke.get('passed') is True and smoke_gate == {'make_exit_code':0,'app_output':'1','config_h_opened':True,'passed':True}, f'{prefix}: smoke gate not passed')
        scan_log = (run/'secret-scan.txt').read_text(errors='replace')
        record['recorded_scan_passed'] = '未发现问题' in scan_log and 'FOUND ' not in scan_log
        check(record['recorded_scan_passed'], f'{prefix}: recorded scan not passed')
        check('含 Git 历史' in scan_log and '含镜像' in scan_log, f'{prefix}: scan did not cover history and image')
        images = image if isinstance(image,list) else [image]
        info = images[0] if images and isinstance(images[0],dict) else {}
        tags = info.get('RepoTags') or []
        record['image_id'] = info.get('id') or info.get('Id')
        record['image_architecture'] = info.get('arch') or info.get('Architecture')
        check(bool(record['image_id']) and record['image_architecture'] == 'amd64', f'{prefix}: missing image/amd64 record')
        record['toolchain_sha256'] = record['files']['toolchain.lock']['sha256']
        if args.scan:
            image_ref = info.get('image') or (tags[0] if tags else record['image_id'])
            if check(isinstance(image_ref,str) and bool(image_ref), f'{prefix}: cannot select image for independent scan'):
                scan = command(['python3',str(repo/'e4/A-buildchecker/scripts/secret_scan.py'),str(repo/'e4/A-buildchecker'),'--history','--image',image_ref])
                record['independent_scan'] = {'exit_code':scan.returncode, 'masked_output':scan.stdout, 'completed':scan.returncode == 0}
                check(scan.returncode == 0, f'{prefix}: independent history/image scan not passed; inspect masked output')
                live = command(['docker','image','inspect','--format','{{.Id}}',image_ref])
                check(live.returncode == 0 and live.stdout.strip() == record['image_id'], f'{prefix}: current image differs from recorded image')
    if len(records) >= 2:
        check(len({r.get('template_sha') for r in records}) == 1, 'comparison: template SHA differs')
        check(len({r.get('toolchain_sha256') for r in records}) == 1, 'comparison: toolchain.lock differs')
        check(len({r.get('student_id') for r in records}) == len(records), 'comparison: student identities must be independent')
    tracked = command(['git','-C',str(repo),'ls-files','-z'])
    check(tracked.returncode == 0, 'cannot enumerate tracked files')
    tracked_env = [p for p in tracked.stdout.split('\0') if p and Path(p).name == '.env']
    check(not tracked_env, '.env is tracked')
    result = {'scope':'E4 A-group run evidence; B-group README rerun is a separate required task',
              'records':records, 'tracked_env':tracked_env, 'independent_scan_requested':args.scan,
              'passed':not errors, 'errors':errors}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x') as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2)
        handle.write('\n')
    print('PASS' if not errors else 'FAIL', 'E4 A-group evidence:', args.out)
    for error in errors:
        print(error)
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
