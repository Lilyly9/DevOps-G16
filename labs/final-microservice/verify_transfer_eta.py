"""Verify the E12 artifact hashes, image handoff, and an independent rejected patch."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from draft_fullcheck import DraftExecutor
import lab
from project_profile import load_profile


def read(path):
    return json.loads(path.read_bytes())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def status(project):
    return {
        'head': git(project, 'rev-parse', 'HEAD'),
        'worktree': git(project, 'status', '--porcelain=v1', '--untracked-files=all'),
        'makefile_sha256': sha256((project / 'Makefile').read_bytes()).hexdigest(),
    }


def verify(evidence):
    result = read(evidence / 'result.json')
    draft = read(evidence / 'draft-build' / 'result.json')
    image = draft['attempts'][-1]['image_id']
    prefix = f"artifact://{result['job_id']}/"
    assert result['status'] == 'SUCCEEDED'
    runs = []
    for artifact in result['artifacts']:
        assert artifact['uri'].startswith(prefix)
        path = (evidence / artifact['uri'].removeprefix(prefix)).resolve()
        assert path.is_relative_to(evidence.resolve())
        raw = path.read_bytes()
        assert len(raw) == artifact['bytes'] and sha256(raw).hexdigest() == artifact['sha256'], path
        if path.suffix != '.json':
            continue
        value = json.loads(raw)
        if not isinstance(value, dict) or 'requested_image_id' not in value:
            continue
        assert value['requested_image_id'] == value['actual_image_id'] == image, path
        assert value['container_exit_code'] == value['cleanup_exit_code'] == 0, path
        runs.append(path.relative_to(evidence).as_posix())
    for part in ('baseline-full/', 'target-full/', 'final-full/', 'validation/'):
        assert any(run.startswith(part) for run in runs), part
    summary = {'job_id': result['job_id'], 'trace_id': result['trace_id'], 'base': result['base_commit'],
               'target': result['target_commit'], 'digest_count': len(result['artifacts']),
               'draft_image_id': image, 'draft_execution_records': runs}
    return summary


def rejected_patch(out, project, candidate_image, host_root):
    makefile = project / 'Makefile'
    before = status(project)
    assert not before['worktree']
    current = makefile.read_text(encoding='utf-8')
    rule = next(line for line in current.splitlines() if line.startswith('estimate.o:'))
    assert 'defaults.h' not in rule
    from difflib import unified_diff

    broken = current.replace(rule, rule + ' defaults.h', 1)
    patch = out / 'incomplete-dependency.patch'
    patch.write_text(''.join(unified_diff(current.splitlines(keepends=True), broken.splitlines(keepends=True),
                                        fromfile='a/Makefile', tofile='b/Makefile')), encoding='utf-8')
    save(out / 'before.json', before)
    runner = DraftExecutor(candidate_image, host_root).capture
    result = lab.validate(project, patch, out / 'validation', runner=runner, profile=load_profile(project))
    after = status(project)
    save(out / 'after.json', after)
    save(out / 'rejection.json', result)
    assert result['checks']['patch_applies'] and result['checks']['build'] and result['checks']['test'], result
    assert result['checks']['header_change'] is False and result['accepted'] is False, result
    assert before == after and result['source_unchanged'] and result['rollback'], result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('project', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('host_root')
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    summary = verify(args.evidence)
    save(args.output / 'e12-image-and-artifacts.json', summary)
    rejected_patch(args.output, args.project, summary['draft_image_id'], args.host_root)
    print(json.dumps({'job_id': summary['job_id'], 'artifact_count': summary['digest_count'],
                      'same_image_commands': len(summary['draft_execution_records']), 'patch_rejected': True}))


if __name__ == '__main__':
    main()
