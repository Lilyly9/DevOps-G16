"""A2 contribution: execute EChecker/full-check commands inside the DRAFT image.

Passing an image id through JSON does not prove the execution environment was
handed over.  This executor launches a fresh container from the image DRAFT
built, mounts the same repository checkout, and runs gcc/strace there.  Every
invocation is recorded so the stage can cite the image id and exit code.
"""
import json
import os
from pathlib import Path
import re
import subprocess

IMAGE = re.compile(r'sha256:[0-9a-f]{64}\Z')


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class ImageExecutor:
    def __init__(self, image_id, host_root, root, docker='docker', timeout=240):
        if not isinstance(image_id, str) or not IMAGE.fullmatch(image_id):
            raise ValueError('DRAFT image id must be sha256:<64 hex>')
        self.image_id = image_id
        self.host_root = Path(host_root).resolve()
        self.root = Path(root).resolve()
        self.docker = docker
        self.timeout = timeout
        if not self.host_root.is_dir():
            raise ValueError('host root for the DRAFT image mount does not exist')

    def mapped(self, path):
        relative = Path(path).resolve().relative_to(self.root)
        return str(self.host_root / relative)

    def command(self, argv, cwd):
        user = f'{os.getuid()}:{os.getgid()}' if hasattr(os, 'getuid') else '1000:1000'
        return [self.docker, 'run', '--rm', '--network', 'none', '--cap-add', 'SYS_PTRACE',
                '--user', user, '-e', 'HOME=/tmp', '-e', 'PYTHONDONTWRITEBYTECODE=1',
                '-e', 'GIT_CONFIG_COUNT=1', '-e', 'GIT_CONFIG_KEY_0=safe.directory',
                '-e', 'GIT_CONFIG_VALUE_0=*',
                '-v', f'{self.host_root}:{self.host_root}', '-w', self.mapped(cwd),
                self.image_id, *argv]

    def __call__(self, argv, cwd):
        command = self.command(argv, cwd)
        result = subprocess.run(command, text=True, capture_output=True, timeout=self.timeout)
        if result.returncode:
            raise ValueError('IMAGE_COMMAND_FAILED ' + repr(argv) + '\n' + result.stdout + result.stderr)
        return result.stdout

    def capture(self, folder):
        folder = Path(folder)
        counter = {'value': 0}

        def execute(argv, cwd):
            counter['value'] += 1
            record = {'image_id': self.image_id, 'command': self.command(argv, cwd),
                      'argv': list(argv), 'cwd': str(cwd)}
            try:
                output = self(argv, cwd)
            except Exception as exc:
                record.update(exit_code=1, error=str(exc))
                save(folder / f'{counter["value"]:02d}.json', record)
                raise
            record.update(exit_code=0, stdout=output[-4000:])
            save(folder / f'{counter["value"]:02d}.json', record)
            return output
        return execute


FULL_CHECK = '''
import json, sys
sys.path.insert(0, "/app")
from buildchecker.fullcheck import full_check
report = full_check(sys.argv[1], sys.argv[2],
                    clean_command=sys.argv[3], build_command=sys.argv[4])
print(json.dumps(report, ensure_ascii=False))
'''


def full_check_in_image(executor, project, output, clean_target, build_target, evidence):
    """Run buildchecker's traced full check through a container from the DRAFT image."""
    execute = executor.capture(evidence)
    payload = execute(['python3', '-c', FULL_CHECK, executor.mapped(project), executor.mapped(output),
                       f'make {clean_target}', f'make {build_target}'], project)
    report = json.loads(payload)
    if report.get('status') != 'SUCCEEDED':
        raise ValueError('FULL_CHECK_IN_IMAGE_FAILED ' + str(report.get('error', report.get('error_code'))))
    return report


def image_toolchain(executor, project, evidence):
    execute = executor.capture(evidence)
    lock = execute(['cat', '/opt/toolchain.lock'], project)
    return lock.splitlines()
