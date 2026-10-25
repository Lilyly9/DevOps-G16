
import hashlib, json
from pathlib import Path
root = Path('work/e6-B2-replay/evidence')
paths = [root / 'result.json', root / 'iter-01/build-stdout.log', root / 'iter-01/build-stderr.log', root / 'iter-02/build-stdout.log', root / 'iter-02/build-stderr.log', root / 'iter-02/image-inspect.json', root / 'verify.log', root / 'verify-stderr.log', root / 'project']
report = json.loads((root / 'result.json').read_text(encoding='utf-8')) if (root / 'result.json').is_file() else None
project = root / 'project'
actual_hashes = {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(project.rglob('*')) if p.is_file()} if project.is_dir() else None
print(json.dumps({'scope': 'Read-only independent inventory; no Docker execution or generated experiment result', 'paths_exist': {str(p): p.exists() for p in paths}, 'report_available': report is not None, 'project_sha256': actual_hashes, 'comparison_possible': report is not None and actual_hashes is not None, 'verdict': 'FAIL: required experiment artifacts absent' if report is None else 'Inspect actual artifacts before acceptance'}, indent=2))
