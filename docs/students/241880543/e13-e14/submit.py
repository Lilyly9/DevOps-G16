"""Check B2 evidence; --publish syncs, commits, pushes and opens its draft PR.

Run --publish in a normal terminal with repository write access and GitHub access.
It retains synchronization stashes and never force-pushes or merges the PR.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[4]
DOC = Path(__file__).resolve().parent
BRANCH = 'student/241880543/e13-e14'
REPOSITORY = 'Lilyly9/DevOps-G16'
PR_TITLE = 'fix(B2): roll back failed MDFixer rechecks and record C5 evidence'
ISSUE_TITLE = 'B2 C5: failed final recheck leaves candidate Makefile in target'
ALLOWED = ('AI_USAGE.md', 'CONTRIBUTIONS.md', 'E13-14_TASKS.md',
           'labs/e11e12/pipeline.py', 'labs/e8e10/lab.py',
           'labs/e11e12/test_student_241880543_e13e14.py')
DOC_PREFIX = 'docs/students/241880543/e13-e14/'


def run(argv, *, input=None):
    p = subprocess.run(argv, cwd=ROOT, input=input, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=120)
    if p.returncode:
        raise RuntimeError(f'{argv[0]} failed ({p.returncode}): {p.stderr.strip()}')
    return p.stdout.strip()


def git(*args):
    return run(['git', '-c', 'core.quotepath=false', *args])


def allowed(path):
    return path in ALLOWED or path.startswith(DOC_PREFIX)


def audit(out):
    manifest = json.loads((DOC / 'evidence/verification-current.json').read_text(encoding='utf-8'))
    for name, expected in manifest['implementation_git_blob_sha256'].items():
        # These Python sources use UTF-8 and Git's normal LF representation.
        actual = hashlib.sha256((ROOT / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        if actual != expected:
            raise ValueError(f'Implementation changed since the Linux evidence: {name}; rerun it first')
    for name, expected in manifest['evidence_sha256'].items():
        if hashlib.sha256((DOC / 'evidence' / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Evidence hash mismatch: {name}')
    for name in ('draft-build.zip', 'docker-c5.zip',
                 'teacher/e13-upstream-student.zip', 'teacher/teacher-runs.zip'):
        with zipfile.ZipFile(DOC / 'evidence' / name) as archive:
            if archive.testzip() is not None:
                raise ValueError(f'Archive CRC failed: {name}')
    teacher = json.loads((DOC / 'evidence/teacher/teacher-summary.json').read_text(encoding='utf-8'))
    for name, key in (('teacher/e13-upstream-student.zip', 'archive_sha256'),
                      ('teacher/teacher-runs.zip', 'run_archive_sha256')):
        expected = teacher[key]
        if hashlib.sha256((DOC / 'evidence' / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Teacher archive hash mismatch: {name}')
    environment = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1',
                       PYTHONPATH=os.pathsep.join(str(ROOT / p) for p in
                                                ('labs/e11e12', 'labs/e8e10', 'labs/e11e12/vendor')))
    for folder, pattern, label in (
        ('labs/e11e12', 'test_student_241880543_e13e14.py', 'b2'),
        ('labs/e13e14', 'test_handoff.py', 'handoff'),
    ):
        with (out / f'{label}.log').open('wb') as log:
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                     '-s', folder, '-p', pattern, '-v'], cwd=ROOT,
                                    env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        (out / f'{label}.exit').write_text(str(result.returncode) + '\n', encoding='utf-8')
        if result.returncode:
            raise ValueError(f'{label} tests failed: {out / (label + ".log")}')
    print('PASS: source hashes, evidence hashes, ZIP CRC, 10 B2 tests, 3 handoff tests')


def synchronize():
    if git('branch', '--show-current') != BRANCH:
        raise ValueError(f'Run from {BRANCH}')
    changed = set(git('diff', '--name-only', 'HEAD').splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').splitlines())
    unexpected = sorted(p for p in changed if not allowed(p))
    if unexpected:
        raise ValueError('Keep unrelated work separate before publishing: ' + ', '.join(unexpected))
    git('fetch', 'origin')
    if git('rev-list', '--count', 'HEAD..origin/main') != '0':
        stash = None
        if changed:
            git('stash', 'push', '--include-untracked', '-m', 'B2 before E13-E14 submission sync')
            stash = git('rev-parse', 'refs/stash')
            print('Retained synchronization stash:', stash)
        git('merge', '--no-edit', 'origin/main')
        if stash:
            git('stash', 'apply', '--index', stash)
    if git('diff', '--name-only', '--diff-filter=U'):
        raise ValueError('Resolve synchronization conflicts before publishing')


def client():
    # Never print or save the credential response.
    response = run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n')
    credential = dict(line.split('=', 1) for line in response.splitlines() if '=' in line)
    token = credential.get('password')
    if not token:
        raise ValueError('GitHub HTTPS credential is not configured')

    def api(path, body=None):
        request = urllib.request.Request(
            'https://api.github.com/' + path,
            data=None if body is None else json.dumps(body).encode('utf-8'),
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                     'Content-Type': 'application/json', 'User-Agent': 'DevOps-G16-B2'})
        with urllib.request.urlopen(request, timeout=45) as result:
            return json.load(result)
    return api


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    out = ROOT / 'work' / ('e13-241880543-submit-' + time.strftime('%Y%m%d-%H%M%S') + '-' + str(os.getpid()))
    out.mkdir(parents=True, exist_ok=False)
    audit(out)
    if not args.publish:
        print('Read-only Git check complete. Publication was not requested.')
        return 0
    # Resolve authentication before any local publication commit.
    api = client()
    synchronize()
    post_sync = out / 'after-sync'
    post_sync.mkdir()
    audit(post_sync)
    git('add', '--', *ALLOWED, DOC_PREFIX)
    staged = git('diff', '--cached', '--name-only').splitlines()
    if any(not allowed(p) for p in staged):
        raise ValueError('Unexpected staged files; refusing to commit unrelated work')
    if staged:
        git('commit', '-m', 'fix(B2): restore Makefile after failed final recheck and retain C5 evidence')
    sha = git('rev-parse', 'HEAD')
    git('push', '--set-upstream', 'origin', BRANCH)
    base = 'repos/' + REPOSITORY + '/'
    existing = api(base + 'pulls?state=open&head=' + urllib.parse.quote('Lilyly9:' + BRANCH, safe=''))
    issues = api('search/issues?q=' + urllib.parse.quote('repo:' + REPOSITORY + ' is:issue in:title "' + ISSUE_TITLE + '"'))
    matching = [item for item in issues['items'] if item['title'] == ISSUE_TITLE]
    issue = matching[0] if matching else api(base + 'issues', {
        'title': ISSUE_TITLE, 'body': (DOC / 'ISSUE_BODY.md').read_text(encoding='utf-8')})
    body = (DOC / 'PR_BODY.md').read_text(encoding='utf-8') + f'\n\nCloses #{issue["number"]}\n'
    pr = existing[0] if existing else api(base + 'pulls', {
        'title': PR_TITLE, 'head': BRANCH, 'base': 'main', 'body': body, 'draft': True})
    result = {'commit': sha, 'branch': BRANCH, 'issue': issue['html_url'],
              'pull_request': pr['html_url'], 'CI': 'PENDING_ACTUAL_RESULT',
              'gate': 'H1/H3/C1 and four-container E14 remain incomplete; no RC release'}
    (out / 'delivery.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('Check the PR checks before declaring CI passed. Delivery record:', out / 'delivery.json')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
