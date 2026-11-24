"""Prepare the supplied teacher repositories and record B2's H1/H3 runs.

GCC smoke checks are separate from the Docker/strace E12 result. --execute also
invokes the official run_e11e12.py entry, retaining its real exit and output.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[4]
DOC = Path(__file__).resolve().parent
ARCHIVE_SHA = 'd9818c5f34d6ff5b6016222dabd7f56daca09ceaa5f525be214e146e3d485435'


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv, cwd, log):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=900,
                            env=dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONUTF8='1'))
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + result.stderr, encoding='utf-8')
    log.with_suffix('.exit').write_text(str(result.returncode) + '\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--gcc', default='gcc')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--with-strace', action='store_true',
                        help='Create a separate candidate with the runtime strace dependency')
    args = parser.parse_args()
    out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT / 'work') or out.exists():
        parser.error('--out must be a fresh directory below work/')
    archive_path = DOC / 'evidence/teacher/e13-upstream-student.zip'
    if digest(archive_path) != ARCHIVE_SHA:
        raise ValueError('Teacher archive hash does not match the supplied original')
    data = ROOT / 'data' / out.name
    if data.exists():
        raise ValueError('Use a fresh input directory as well as a fresh output directory')
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise ValueError('Teacher archive CRC failed')
        for item in archive.infolist():
            destination = (data / item.filename).resolve()
            if not destination.is_relative_to(data) or (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Unsafe teacher archive path')
        archive.extractall(data)
    out.mkdir(parents=True)
    summary = {'scope': 'B2 H1 execution / H3 review on supplied course-adapted repositories',
               'archive_sha256': ARCHIVE_SHA, 'platform': sys.platform, 'python': sys.version,
               'runner_commit': command(['git', 'rev-parse', 'HEAD'], ROOT, out / 'runner.log').stdout.strip(),
               'runner_sha256': digest(Path(__file__)), 'cases': {}}
    save(out / 'summary.json', summary)
    for name in ('H1-jsmn', 'H3-tiny-aes'):
        folder = data / 'e13-upstream-student' / name
        repo = folder / 'repo'
        case_out = out / name
        case_out.mkdir()
        history = command(['git', 'log', '-2', '--format=%H'], repo, case_out / 'commits.log')
        commits = history.stdout.splitlines()
        if history.returncode or len(commits) != 2 or any(not re.fullmatch('[0-9a-f]{40}', c) for c in commits):
            raise ValueError('Unable to resolve the supplied C0/C1 history: ' + name)
        target, base = commits
        status = command(['git', 'status', '--porcelain'], repo, case_out / 'status-before.log')
        fsck = command(['git', 'fsck', '--full'], repo, case_out / 'fsck.log')
        if status.returncode or status.stdout or fsck.returncode:
            raise ValueError('Teacher repository is not clean and intact: ' + name)
        before = {p.name: digest(p) for p in repo.iterdir() if p.is_file()}
        upstream = (repo / 'UPSTREAM.md').read_text(encoding='utf-8')
        (case_out / 'UPSTREAM.md').write_text(upstream, encoding='utf-8')
        candidate = folder / 'candidate.Dockerfile'
        if args.with_strace:
            original = candidate.read_bytes()
            if original.count(b'--no-install-recommends build-essential') != 1:
                raise ValueError('Unexpected teacher candidate; refusing automatic adaptation')
            candidate = folder / 'candidate-b2-strace.Dockerfile'
            candidate.write_bytes(original.replace(b'--no-install-recommends build-essential',
                                                   b'--no-install-recommends build-essential strace'))
        request = {'mode': 'e12', 'repo': '/course/' + repo.relative_to(ROOT).as_posix(),
                   'base': base, 'target': target,
                   'candidate': '/course/' + candidate.relative_to(ROOT).as_posix(),
                   'expected_output': '1', 'build_timeout': 600}
        save(case_out / 'request-e12.json', request)
        smoke = command([args.gcc, '-O0', 'main.c', 'helper.c', '-o', str(case_out / 'smoke.exe')],
                        repo, case_out / 'gcc-build.log')
        execution = None
        if smoke.returncode == 0:
            execution = command([str(case_out / 'smoke.exe')], repo, case_out / 'gcc-run.log')
        dependency_logs = {}
        for source in ('main.c', 'helper.c'):
            result = command([args.gcc, '-O0', '-MM', source], repo,
                             case_out / (source + '-dependencies.log'))
            dependency_logs[source] = {'exit_code': result.returncode, 'output': result.stdout.strip()}
        sys.path.insert(0, str(ROOT / 'labs/e8e10'))
        from lab import scan, patch
        scan_count = 0

        def gcc_observation(argv, cwd):
            nonlocal scan_count
            scan_count += 1
            observed = command([args.gcc, *argv[1:]], cwd,
                               case_out / f'gcc-scan-{scan_count}.log')
            if observed.returncode:
                raise ValueError('GCC observation failed: ' + name)
            return observed.stdout

        gcc_report = scan(repo, execute=gcc_observation)
        save(case_out / 'gcc-scan.json', gcc_report)
        diff, edits = patch(repo, gcc_report, isolate_shared_macros=True)
        (case_out / 'candidate.patch').write_bytes(diff.encode('utf-8'))
        save(case_out / 'repair-plan.json', edits)
        applies = command(['git', 'apply', '--check', str(case_out / 'candidate.patch')],
                          repo, case_out / 'patch-applies.log')
        entry = {'base': base, 'target': target, 'upstream': upstream,
                 'source_hashes_before': before, 'candidate_sha256': digest(folder / 'candidate.Dockerfile'),
                 'candidate_contains_strace': b'strace' in (folder / 'candidate.Dockerfile').read_bytes(),
                 'selected_candidate_sha256': digest(candidate),
                 'selected_candidate': candidate.name,
                 'gcc_findings': gcc_report['findings'], 'patch_check_exit': applies.returncode,
                 'patch_sha256': digest(case_out / 'candidate.patch'),
                 'gcc_smoke': {'build_exit': smoke.returncode,
                               'run_exit': None if execution is None else execution.returncode,
                               'stdout': None if execution is None else execution.stdout.strip(),
                               'expected_output': '1'},
                 'gcc_dependencies': dependency_logs,
                 'e12_status': 'NOT_EXECUTED', 'e12_exit': None}
        if args.execute:
            e12 = command([sys.executable, 'run_e11e12.py', 'run', '--request',
                           str((case_out / 'request-e12.json').relative_to(ROOT)),
                           '--out', str((case_out / 'e12').relative_to(ROOT))], ROOT, case_out / 'e12-console.log')
            result_path = case_out / 'e12/result.json'
            entry.update(e12_exit=e12.returncode,
                         e12_status='BLOCKED_BEFORE_PIPELINE' if not result_path.exists() else
                         json.loads(result_path.read_text(encoding='utf-8'))['status'])
        entry['source_hashes_after'] = {p.name: digest(p) for p in repo.iterdir() if p.is_file()}
        entry['source_unchanged'] = entry['source_hashes_after'] == before
        status_after = command(['git', 'status', '--porcelain'], repo, case_out / 'status-after.log')
        entry['git_clean_after'] = status_after.returncode == 0 and not status_after.stdout
        if not entry['source_unchanged'] or not entry['git_clean_after']:
            raise ValueError('Teacher input changed: ' + name)
        save(case_out / 'preflight.json', entry)
        summary['cases'][name] = entry
        save(out / 'summary.json', summary)
        print(name, base, target, 'GCC=', entry['gcc_smoke'], 'E12=', entry['e12_status'])
    print('Evidence:', out)
    # A GCC smoke result is never reported as a five-stage E12 success.
    return 0 if not args.execute or all(c['e12_status'] == 'SUCCEEDED' for c in summary['cases'].values()) else 2


if __name__ == '__main__':
    raise SystemExit(main())
