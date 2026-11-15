"""Execute project commands in the exact DRAFT image."""
import json
import os
import re
import subprocess
import uuid
from pathlib import Path, PurePosixPath


class DraftExecutor:
    def __init__(self, image_id, host_root, course_root=Path('/course')):
        if not isinstance(image_id, str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', image_id):
            raise ValueError("DRAFT must return an immutable image ID")
        if not host_root or not PurePosixPath(host_root).is_absolute() or '..' in PurePosixPath(host_root).parts:
            raise ValueError("DRAFT execution requires the Docker host's absolute checkout path")
        self.image_id = image_id
        self.host_root = PurePosixPath(host_root)
        self.work = Path(course_root).resolve() / 'work'

    def _bind(self, path):
        path = Path(path)
        if not path.is_dir() or not path.resolve().is_relative_to(self.work) or path.resolve() != path:
            raise ValueError("DRAFT execution may only bind created directories under work/")
        host = self.host_root / path.relative_to(self.work.parent).as_posix()
        if any(c in str(host) + str(path) for c in (',', '\r', '\n')):
            raise ValueError("Docker bind path cannot contain commas or newlines")
        return ['--mount', f'type=bind,source={host},target={path.as_posix()}']

    def capture(self, evidence):
        """Return a lab runner with a separate record for every command."""
        evidence.mkdir(parents=True, exist_ok=True)
        count = 0

        def run(argv, cwd):
            nonlocal count
            count += 1
            base = evidence / f'{count:02d}-{Path(argv[0]).name}'
            stdout = base.with_suffix('.stdout.log')
            stderr = base.with_suffix('.stderr.log')
            code = self(argv, cwd, stdout, stderr, 120, record_path=base.with_suffix('.json'))
            if code:
                raise ValueError(f'DRAFT command exited {code}; see {stderr.name}: {stderr.read_text(encoding="utf-8", errors="replace")}')
            return stdout.read_text(encoding='utf-8')

        return run

    def __call__(self, argv, cwd, stdout_path, stderr_path, timeout, *, record_path=None):
        cwd, stdout_path, stderr_path = map(Path, (cwd, stdout_path, stderr_path))
        mounts = self._bind(cwd)
        tracing = argv[0] == 'strace'
        caps = []
        if tracing:
            trace_dir = Path(argv[argv.index('-o') + 1]).parent
            if trace_dir != cwd.parent / 'trace':
                raise ValueError("Trace output must be beside the BuildChecker project copy")
            mounts += self._bind(trace_dir)
            caps = ['--cap-add', 'SYS_PTRACE']
        name = 'e11-full-' + uuid.uuid4().hex
        create = [
            'docker', 'create', '--name', name, '--pull=never', '--network', 'none',
            '--cpus', '1', '--memory', '512m', '--pids-limit', '128',
            '--cap-drop', 'ALL', *caps, '--security-opt', 'no-new-privileges',
            '--user', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp',
            '-e', 'LC_ALL=C.UTF-8', *mounts, '--workdir', cwd.as_posix(),
            '--entrypoint', argv[0], self.image_id, *argv[1:],
        ]
        if record_path is None:
            record_path = cwd.parent / ('build-execution.json' if tracing else 'clean-execution.json')
        record = {'requested_image_id': self.image_id, 'create_argv': create,
                  'stdout': stdout_path.name, 'stderr': stderr_path.name}
        cid = None
        try:
            created = subprocess.run(create, capture_output=True, text=True, timeout=20)
            if created.returncode != 0:
                raise ValueError(f"Docker could not create DRAFT container: {created.stderr.strip()}")
            cid = created.stdout.strip()
            if not re.fullmatch(r'[0-9a-f]{64}', cid):
                raise ValueError("Docker did not return the container ID")
            record['container_id'] = cid
            actual = self._inspect(cid, '{{.Image}}')
            record['actual_image_id'] = actual
            if actual != self.image_id:
                raise ValueError("Created container image differs from DRAFT image")
            start = ['docker', 'start', '--attach', cid]
            record['start_argv'] = start
            with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
                started = subprocess.run(start, stdout=stdout, stderr=stderr, timeout=timeout)
            record['attach_exit_code'] = started.returncode
            status = self._inspect(cid, '{{.State.Status}} {{.State.ExitCode}}').split()
            if len(status) != 2 or status[0] != 'exited' or not status[1].isdigit():
                raise ValueError("DRAFT container did not exit; collection is incomplete")
            record['container_exit_code'] = int(status[1])
            return started.returncode or int(status[1])
        except subprocess.TimeoutExpired as exc:
            record['error'] = 'DRAFT Docker command timed out'
            raise TimeoutError(record['error']) from exc
        except (OSError, ValueError) as exc:
            record['error'] = str(exc)
            raise
        finally:
            # The randomly named container is ours, even if create timed out before returning its ID.
            try:
                removed = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, text=True, timeout=15)
                record['cleanup_exit_code'] = removed.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                record['cleanup_error'] = str(exc)
            record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')

    @staticmethod
    def _inspect(cid, template):
        proc = subprocess.run(['docker', 'container', 'inspect', '--format', template, cid],
                              capture_output=True, text=True, timeout=15)
        if proc.returncode:
            raise ValueError(f"Docker could not inspect DRAFT container: {proc.stderr.strip()}")
        return proc.stdout.strip()
