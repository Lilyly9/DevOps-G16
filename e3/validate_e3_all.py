#!/usr/bin/env python3
"""Check saved E3 evidence for all four services; does not run Docker or sign for members."""
import argparse
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    errors = []
    for script in ('e3/validate_e3.py', 'e3/scripts/b2_verify_evidence.py'):
        result = subprocess.run(['python3', str(root/script), '--root', str(root)], capture_output=True)
        print(result.stdout.decode(errors='replace').strip())
        if result.returncode:
            errors.append(script + ': failed')
    try:
        for member in ('A1','A2','A3','B1','B2'):
            env = json.loads((root/'e3/env'/f'toolchain-{member}.txt').read_text())
            assert env.get('member') == member and env.get('os') and env.get('architecture') and env.get('versions'), f'{member}: incomplete environment'
        expected = root/'e3/expected/draft-sample.md'
        assert 'MANUAL_EXPECTED' in expected.read_text(), 'B1: missing manual provenance'
        run = root/'e3/work/20261004-115744-B1-8f5ca8'
        obs = json.loads((run/'observations.json').read_text())
        assert obs['observation_type'] == 'ACTUAL_RUN' and not obs['failures'], 'B1: observation status'
        sha = obs['source_commit']
        assert re.fullmatch('[a-f0-9]{40}',sha), 'B1: source SHA'
        assert subprocess.run(['git','-C',str(root),'cat-file','-e',sha+'^{commit}'],capture_output=True).returncode == 0, 'B1: unavailable source context'
        commands = json.loads((run/'commands.json').read_text())
        by_id = {cmd['id']:cmd for cmd in commands}
        def text(cmd,channel):
            path = (run/cmd[channel]).resolve()
            assert path.is_relative_to(run.resolve()) and path.is_file(), 'B1: missing/unsafe log'
            return path.read_text(errors='replace')
        for cmd in commands:
            assert cmd['argv'] and cmd['cwd'] and type(cmd['exit_code']) is int and cmd['source_commit'] == sha, 'B1: incomplete command metadata'
            text(cmd,'stdout'); text(cmd,'stderr')
        for name in ('draft-build','draft-build-check','draft-run','docker-reference-build','docker-reference-run','docker-reference-image-id'):
            assert by_id[name]['exit_code'] == 0, f'B1: {name} failed'
        for name in ('draft-run','docker-reference-run'):
            assert text(by_id[name],'stdout').strip() == 'hello E3', f'B1: {name} output'
        broken=by_id['docker-broken-build']
        assert broken['exit_code'] != 0 and 'make: not found' in text(broken,'stdout')+text(broken,'stderr'), 'B1: expected failure absent'
        assert re.search(r'sha256:[a-f0-9]{64}',text(by_id['docker-reference-image-id'],'stdout')), 'B1: image ID missing'
        assert obs['draft_run_output'] == obs['docker_reference_run_output'] == 'hello E3', 'B1: observation/log mismatch'
        assert obs['docker_broken_exit_code'] == broken['exit_code'] and obs['docker_status'] == obs['behavior_status'] == 'PASSED', 'B1: observation/exit mismatch'
        for name in ('Dockerfile.broken','Dockerfile.reference','Makefile','main.c'):
            assert (root/'e3/fixtures/draft'/name).is_file(), f'B1: missing fixture {name}'
    except (OSError,ValueError,KeyError,AssertionError) as exc:
        errors.append(str(exc))
    if errors:
        print('FAIL: '+'; '.join(errors))
        return 1
    print('PASS: four-service saved E3 baseline evidence and five member environments')
    print('Scope: manual baselines and archived logs; not detector accuracy, live image identity, or personal signatures.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
