#!/usr/bin/env python3
"""B1 DRAFT baseline runner (Tiny Greeting double-layer check).

Stage build: copy fixtures/draft into the run runtime dir, run `make`,
verify the `hello` artifact, run `./hello`, and expect stdout `hello E3`
with exit code 0 (B1-2/B1-3).

Stage docker: build Dockerfile.broken (expect non-zero exit and a
`make: not found` line), build Dockerfile.reference, `docker run --rm`
it and expect `hello E3`; record the reference image ID (B1-4/B1-5).

Both stages append to the same work/<run-id>/ evidence set:
commands.json, observations.json, environment.json and logs/.

Usage (run inside Linux/WSL; the docker stage needs a working daemon):
  RUNID=20261004-HHMMSS-B1-<sha6> python3 e3/scripts/b1_run_draft_baseline.py --stage build --run-id $RUNID
  RUNID=... python3 e3/scripts/b1_run_draft_baseline.py --stage docker --run-id $RUNID
"""
import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CTX = REPO / 'e3' / 'fixtures' / 'draft'
WORK = REPO / 'e3' / 'work'
TAG = '20261004'
CONFIGURATION_ID = 'b1-wsl-gcc-default'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=('build', 'docker'), required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()

    run_dir = WORK / args.run_id
    logs = run_dir / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    runtime = run_dir / 'runtime'

    head = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()

    commands_path = run_dir / 'commands.json'
    commands = json.loads(commands_path.read_text()) if commands_path.exists() else []
    by_id = {c['id']: c for c in commands}
    obs_path = run_dir / 'observations.json'
    obs = json.loads(obs_path.read_text()) if obs_path.exists() else {}

    def run(cmd_id, argv, cwd):
        started = datetime.now(timezone.utc).isoformat()
        t0 = time.monotonic()
        proc = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)
        duration = round(time.monotonic() - t0, 4)
        (logs / f'{cmd_id}.stdout.log').write_text(proc.stdout)
        (logs / f'{cmd_id}.stderr.log').write_text(proc.stderr)
        by_id[cmd_id] = {
            'id': cmd_id,
            'argv': argv,
            'cwd': str(cwd),
            'source_commit': head,
            'started_at': started,
            'duration_seconds': duration,
            'exit_code': proc.returncode,
            'stdout': f'logs/{cmd_id}.stdout.log',
            'stderr': f'logs/{cmd_id}.stderr.log',
        }
        print(f'{cmd_id}: exit={proc.returncode}')
        return proc

    if args.stage == 'build':
        runtime.mkdir(exist_ok=True)
        for name in ('main.c', 'Makefile'):
            shutil.copy2(CTX / name, runtime / name)
        versions = {}
        for tool in ('git', 'make', 'cc', 'python3', 'docker'):
            proc = run(f'env-{tool}', [tool, '--version'], REPO)
            first = proc.stdout.strip().splitlines()
            versions[tool] = first[0] if proc.returncode == 0 and first else f'NOT_AVAILABLE (exit {proc.returncode})'
        build = run('draft-build', ['make'], runtime)
        check = run('draft-build-check', ['ls', '-l', 'hello'], runtime)
        hello = run('draft-run', ['./hello'], runtime)
        obs.update({
            'member': 'B1',
            'run_id': args.run_id,
            'source_commit': head,
            'observation_type': 'ACTUAL_RUN',
            'configuration_id': CONFIGURATION_ID,
            'draft_build_exit_code': build.returncode,
            'draft_build_artifact_listed': check.returncode == 0 and 'hello' in check.stdout,
            'draft_run_output': hello.stdout.strip(),
            'draft_run_exit_code': hello.returncode,
            'failures': [],
        })
        passed = (build.returncode == 0 and obs['draft_build_artifact_listed']
                  and obs['draft_run_output'] == 'hello E3' and hello.returncode == 0)
        obs['failures'] = [f for f in obs.get('failures', []) if 'local double-layer' not in f]
        obs['behavior_status'] = 'PASSED' if passed else 'FAILED'
        if not passed:
            obs['failures'].append('local double-layer check (make && ./hello) did not pass')
        env_doc = {
            'member': 'B1',
            'run_id': args.run_id,
            'source_commit': head,
            'system': 'Linux',
            'os': 'Ubuntu 26.04 LTS (WSL2)',
            'architecture': 'x86_64',
            'versions': versions,
            'configuration_id': CONFIGURATION_ID,
            'callsite': 'executed as root inside WSL2; invoked from the Windows host via wsl.exe',
        }
        (run_dir / 'environment.json').write_text(json.dumps(env_doc, indent=2) + '\n')
    else:
        broken = run('docker-broken-build',
                     ['docker', 'build', '-f', 'Dockerfile.broken', '-t', f'nju-e3-draft-broken:{TAG}', '.'], CTX)
        reference = run('docker-reference-build',
                        ['docker', 'build', '-f', 'Dockerfile.reference', '-t', f'nju-e3-draft-reference:{TAG}', '.'], CTX)
        container = run('docker-reference-run',
                        ['docker', 'run', '--rm', f'nju-e3-draft-reference:{TAG}'], REPO)
        image = run('docker-reference-image-id',
                    ['docker', 'image', 'inspect', '--format', '{{.Id}}  {{.RepoTags}}',
                     f'nju-e3-draft-reference:{TAG}'], REPO)
        broken_out = (logs / 'docker-broken-build.stdout.log').read_text()
        broken_err = (logs / 'docker-broken-build.stderr.log').read_text()
        obs['failures'] = [f for f in obs.get('failures', []) if 'docker' not in f]
        obs.update({
            'docker_broken_exit_code': broken.returncode,
            'docker_broken_make_not_found': 'make: not found' in broken_out + broken_err,
            'docker_reference_build_exit_code': reference.returncode,
            'docker_reference_run_output': container.stdout.strip(),
            'docker_reference_run_exit_code': container.returncode,
            'docker_reference_image_id': image.stdout.strip(),
        })
        passed = (broken.returncode != 0 and obs['docker_broken_make_not_found']
                  and reference.returncode == 0 and container.stdout.strip() == 'hello E3'
                  and container.returncode == 0)
        obs['docker_status'] = 'PASSED' if passed else 'FAILED'
        if not passed:
            obs.setdefault('failures', []).append('docker broken/reference pair did not match the expected judgments')

    merged = []
    seen = set()
    for cmd in commands:
        merged.append(by_id[cmd['id']])
        seen.add(cmd['id'])
    for cmd in by_id.values():
        if cmd['id'] not in seen:
            merged.append(cmd)
    commands_path.write_text(json.dumps(merged, indent=2) + '\n')
    obs_path.write_text(json.dumps(obs, indent=2) + '\n')
    print('STATUS', obs.get('docker_status') or obs.get('behavior_status'))
    print('RUN_DIR', run_dir)


if __name__ == '__main__':
    main()
