set -Eeuo pipefail
umask 077

if [[ $# -ne 1 || ! -f "$1" ]]; then
    echo "Usage: bash run-sample.sh /absolute/path/Microservice_Lab.zip" >&2
    exit 2
fi
archive=$(realpath -- "$1")
work_parent=$(realpath -- "${FINAL_WORK_ROOT:-${TMPDIR:-/tmp}}")
run_root=$(mktemp -d "$work_parent/g16-final-sample.XXXXXX")
project="a16-final-sample-${run_root##*.}"
project=${project,,}
echo "RUN_ROOT=$run_root"
echo "COMPOSE_PROJECT=$project"
cd "$run_root"
sha256sum "$archive" > source.sha256
python3 - "$archive" <<'PY'
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import sys

prefix = 'Microservice_Lab/'
with ZipFile(sys.argv[1]) as archive:
    for entry in archive.infolist():
        if entry.is_dir() or not entry.filename.startswith(prefix):
            continue
        name = entry.filename.removeprefix(prefix)
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('Unsafe member name')
        if name not in ('compose.yaml', 'README.md') and path.parts[0] not in ('app', 'monitoring', 'scripts'):
            continue
        if any(part.startswith('.') or part == '__pycache__' for part in path.parts):
            continue
        target = Path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(entry))
PY
mkdir work
chmod -R a+rX monitoring
python3 scripts/lab.py init
export PYTHON_IMAGE=${PYTHON_IMAGE:-python:3.13-slim}
export PROMETHEUS_IMAGE=${PROMETHEUS_IMAGE:-prom/prometheus:v3.5.1}
export GRAFANA_IMAGE=${GRAFANA_IMAGE:-grafana/grafana:13.3.0}
printf '%s\n' "PYTHON_IMAGE=$PYTHON_IMAGE" "PROMETHEUS_IMAGE=$PROMETHEUS_IMAGE" "GRAFANA_IMAGE=$GRAFANA_IMAGE" > work/image-references.txt
read -r LAB_API_PORT LAB_PROM_PORT LAB_GRAFANA_PORT < <(python3 - <<'PY'
from socket import socket

sockets = [socket() for _ in range(3)]
for listener in sockets:
    listener.bind(('127.0.0.1', 0))
print(*(listener.getsockname()[1] for listener in sockets))
PY
)
export LAB_API_PORT LAB_PROM_PORT LAB_GRAFANA_PORT
python3 - <<'PY'
import os
from pathlib import Path

path = Path('.env')
lines = path.read_text().splitlines()
path.write_text(''.join(f'{name}={os.environ.get(name, value)}\n' for name, value in (line.split('=', 1) for line in lines)))
PY
printf '%s\n' "api=$LAB_API_PORT" "prometheus=$LAB_PROM_PORT" "grafana=$LAB_GRAFANA_PORT" > work/ports.txt
compose() { docker compose -p "$project" "$@"; }
collect() {
    code=$?
    trap - EXIT
    set +e
    compose logs --no-color --timestamps api worker > work/services.log 2>&1
    compose ps --all > work/compose-at-exit.txt 2>&1
    compose down > work/cleanup.log 2>&1
    echo "$code" > work/scenario.exit
    tar -czf "$run_root-evidence.tar.gz" compose.yaml monitoring work source.sha256
    sha256sum "$run_root-evidence.tar.gz"
    echo "EVIDENCE=$run_root-evidence.tar.gz"
    exit "$code"
}
trap collect EXIT
{
    date -Is
    docker --version
    docker compose version
    python3 --version
} > work/environment.txt
compose config --quiet
date +%s > work/sample-start.epoch
compose --progress plain up -d --wait --wait-timeout 100 > work/start.log 2>&1 || { tail -n 50 work/start.log; exit 1; }
compose ps > work/compose-before.txt
compose images > work/images.txt
for role in api worker prometheus grafana; do
    id=$(compose ps -q "$role")
    docker inspect --format '{{.Image}}' "$id" > "work/$role.image-id.txt"
done
compose exec -T worker python -c "from urllib.request import urlopen; print(urlopen('http://127.0.0.1:8080/health').read().decode())" > work/worker-health.json
curl -fsS "http://127.0.0.1:$LAB_API_PORT/health" > work/api-health.json
for ((attempt=0; attempt<30; attempt++)); do
    if curl -fsS "http://127.0.0.1:$LAB_GRAFANA_PORT/api/health" > work/grafana-health.json 2>/dev/null; then break; fi
    sleep 1
done
test -s work/grafana-health.json
python3 scripts/lab.py target 1
python3 scripts/lab.py run normal | tee work/normal-console.log
sleep 5
date -Is | tee work/worker-stopped-at.txt
compose stop worker
python3 scripts/lab.py target 0
python3 scripts/lab.py run down | tee work/down-console.log
sleep 5
compose start worker
python3 scripts/lab.py target 1
date -Is | tee work/worker-recovered-at.txt
python3 scripts/lab.py run recovered | tee work/recovered-console.log
compose ps > work/compose-after.txt
python3 scripts/lab.py run timeout | tee work/timeout-console.log
sleep 5
python3 - <<'PY'
import base64
import json
import os
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

root = Path('work')
prom = f"http://127.0.0.1:{os.environ['LAB_PROM_PORT']}"
grafana = f"http://127.0.0.1:{os.environ['LAB_GRAFANA_PORT']}"


def save(url, path, headers=None):
    with urlopen(Request(url, headers=headers or {}), timeout=10) as result:
        raw = result.read()
    path.write_bytes(raw)
    return json.loads(raw)


targets = save(f'{prom}/api/v1/targets', root / 'prometheus-targets.json')['data']['activeTargets']
observed = {target['labels']['job']: target['health'] for target in targets}
assert observed.get('lab-api') == observed.get('lab-worker') == 'up', observed
for label, query in {'worker-up': 'up{job="lab-worker"}', 'jobs-total': 'lab_jobs_total',
                     'duration': 'lab_job_duration_seconds_sum / lab_job_duration_seconds_count'}.items():
    params = urlencode({'query': query, 'start': root.joinpath('sample-start.epoch').read_text().strip(),
                        'end': int(time.time()), 'step': 2})
    data = save(f'{prom}/api/v1/query_range?{params}', root / f'prometheus-{label}.json')
    if label == 'worker-up':
        values = [value for _, value in data['data']['result'][0]['values']]
        first_down = values.index('0')
        assert '1' in values[:first_down] and '1' in values[first_down + 1:], values

settings = dict(line.split('=', 1) for line in Path('.env').read_text().splitlines())
credential = base64.b64encode(f"admin:{settings['GRAFANA_ADMIN_PASSWORD']}".encode()).decode()
headers = {'Authorization': f'Basic {credential}'}
panels = save(f'{grafana}/api/search?type=dash-db', root / 'grafana-dashboard-search.json', headers)
for panel in panels:
    uid = panel['uid']
    save(f'{grafana}/api/dashboards/uid/{uid}', root / f'grafana-dashboard-{uid}.json', headers)
assert panels, 'Grafana dashboard was not provisioned'
PY
