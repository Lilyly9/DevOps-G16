#!/usr/bin/env bash
# Run from a Linux checkout with Docker Compose v2 and the three local images:
# COURSE_E12_IMAGE=course-e11e12:final PROMETHEUS_IMAGE=prom/prometheus:v3.5.1 \
#   GRAFANA_IMAGE=grafana/grafana:13.3.0 bash labs/final-microservice/run-real.sh
# Set FINAL_DEMO=1 to pause with the Grafana dashboard available between stages.
set -Eeuo pipefail
umask 077
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
checkout=$(cd -- "$script_dir/../.." && pwd -P)
cd "$checkout"
export E14_ROOT="$checkout"
export E14_IMAGE=${E14_IMAGE:-${COURSE_E12_IMAGE:-course-e11e12:final}}
export PROMETHEUS_IMAGE=${PROMETHEUS_IMAGE:-prom/prometheus:v3.5.1}
export GRAFANA_IMAGE=${GRAFANA_IMAGE:-grafana/grafana:13.3.0}

for image in "$E14_IMAGE" "$PROMETHEUS_IMAGE" "$GRAFANA_IMAGE"; do
    if ! docker image inspect "$image" >/dev/null 2>&1; then
        printf '找不到本地镜像 %s，请先构建课程镜像或拉取对应监控镜像。\n' "$image" >&2
        exit 1
    fi
done

base=5ef9d829e2f893af23f60399dcb67095800d121e
target=e7414083c4f1760cb234f96a9d75f2d0255e3f57
project_path=projects/transfer-eta
mkdir -p work data
run_path=$(mktemp -d "$checkout/work/final-real.XXXXXX")
run_id=${run_path##*/}
input="$checkout/data/$run_id"
project="a16-final-real-${run_id##*.}"
project=${project,,}
export FINAL_CONFIG="$run_path/config"
logs="$run_path/evidence"
echo "RUN_ROOT=$run_path"
echo "INPUT_ROOT=$input"
echo "COMPOSE_PROJECT=$project"
mkdir "$input"
mkdir -p "$FINAL_CONFIG/observations" "$logs"
cp -- "$script_dir/observe.py" "$script_dir/monitoring.yaml" "$script_dir/prometheus.yml" "$FINAL_CONFIG/"
cp -R -- "$script_dir/grafana" "$FINAL_CONFIG/"
chmod -R a+rX "$FINAL_CONFIG/grafana"
chmod a+r "$FINAL_CONFIG/prometheus.yml"
read -r draft_port build_port echeck_port fix_port FINAL_PROM_PORT FINAL_GRAFANA_PORT < <(python3 - <<'PY'
from socket import socket

sockets = [socket() for _ in range(6)]
for listener in sockets:
    listener.bind(('127.0.0.1', 0))
print(*(listener.getsockname()[1] for listener in sockets))
PY
)
export FINAL_PROM_PORT FINAL_GRAFANA_PORT
GRAFANA_ADMIN_PASSWORD=$(python3 -c 'from secrets import token_urlsafe; print(token_urlsafe(24))')
printf 'GRAFANA_ADMIN_PASSWORD=%s\n' "$GRAFANA_ADMIN_PASSWORD" > "$run_path/.env"
compose() { docker compose -p "$project" --env-file "$run_path/.env" -f "$FINAL_CONFIG/e14-base.yaml" -f "$FINAL_CONFIG/monitoring.yaml" "$@"; }
sed -e "s/127\.0\.0\.1:18081:/127.0.0.1:$build_port:/g" \
    -e "s/127\.0\.0\.1:18082:/127.0.0.1:$echeck_port:/g" \
    -e "s/127\.0\.0\.1:18083:/127.0.0.1:$draft_port:/g" \
    -e "s/127\.0\.0\.1:18084:/127.0.0.1:$fix_port:/g" \
    labs/e13e14/compose.yaml > "$FINAL_CONFIG/e14-base.yaml"
collect() {
    local code=$? archive="$run_path-evidence.tar.gz"
    trap - EXIT
    set +e
    if [[ ${compose_started:-0} == 1 ]]; then
        compose logs --no-color --timestamps draft buildchecker echecker mdfixer > "$logs/role-services.log" 2>&1
        compose logs --no-color --timestamps telemetry prometheus > "$logs/monitoring-services.log" 2>&1
        compose ps --all > "$logs/compose-at-exit.txt" 2>&1
        if ! compose down > "$logs/cleanup.log" 2>&1 && [[ $code == 0 ]]; then
            code=1
        fi
    fi
    printf '%s\n' "$code" > "$logs/scenario.exit"
    if tar --exclude=.git --exclude=.env --exclude=__pycache__ -czf "$archive" -C "$run_path" . &&
       (cd -- "$(dirname -- "$archive")" && sha256sum "$(basename -- "$archive")") > "$archive.sha256"; then
        cat "$archive.sha256"
        echo "EVIDENCE=$archive"
    else
        echo '生成证据包或 SHA256 失败。' >&2
        code=1
        printf '%s\n' "$code" > "$logs/scenario.exit"
    fi
    exit "$code"
}
trap collect EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

git init --bare --quiet "$input/repo"
git -C "$input/repo" fetch --no-tags "$checkout" \
    "$base:refs/heads/base" "$target:refs/heads/target" > "$logs/input-fetch.log" 2>&1
git -C "$input/repo" symbolic-ref HEAD refs/heads/target
git show "$target:$project_path/candidate.Dockerfile" > "$input/candidate.Dockerfile"
cp -- "$input/candidate.Dockerfile" "$logs/candidate.Dockerfile"
(cd -- "$logs" && sha256sum candidate.Dockerfile > candidate.sha256)
python3 - "$run_id" "$project_path" "$base" "$target" > "$logs/request.json" <<'PY'
import json
import sys

run_id, project_path, base, target = sys.argv[1:]
data = f'/course/data/{run_id}'
print(json.dumps({
    'mode': 'e12', 'repo': f'{data}/repo', 'project_path': project_path,
    'profile': True, 'base': base, 'target': target,
    'candidate': f'{data}/candidate.Dockerfile', 'expected_output': 'eta_seconds=13',
    'build_timeout': 600,
}, indent=2))
PY
{
    git rev-parse HEAD
    git status --short -- labs/e11e12 labs/e13e14 labs/e8e10 labs/final-microservice
    date -Is
    docker compose version
    python3 --version
    grep MemTotal /proc/meminfo
} > "$logs/environment.txt"
printf 'draft=%s\nbuildchecker=%s\nechecker=%s\nmdfixer=%s\nprometheus=%s\ngrafana=%s\n' \
    "$draft_port" "$build_port" "$echeck_port" "$fix_port" "$FINAL_PROM_PORT" "$FINAL_GRAFANA_PORT" > "$logs/ports.txt"
compose config --quiet
date +%s > "$logs/start.epoch"
compose_started=1
compose up -d --wait --wait-timeout 100 2>&1 | tee "$logs/start.log"
compose ps > "$logs/compose-before.txt"
compose images > "$logs/images.txt"
for role in draft buildchecker echecker mdfixer telemetry prometheus grafana; do
    id=$(compose ps -q "$role")
    docker inspect --format '{{.Config.Image}} {{.Image}}' "$id" > "$logs/$role.image.txt"
done
health() {
    curl -fsS "http://127.0.0.1:$draft_port/health" > "$logs/draft-$1.json"
    curl -fsS "http://127.0.0.1:$build_port/health" > "$logs/buildchecker-$1.json"
    curl -fsS "http://127.0.0.1:$echeck_port/health" > "$logs/echecker-$1.json"
    curl -fsS "http://127.0.0.1:$fix_port/health" > "$logs/mdfixer-$1.json"
}
wait_probe() {
    local url="http://127.0.0.1:$FINAL_PROM_PORT/api/v1/query"
    local query='a16_role_ready{role="echecker"}'
    local attempt
    for ((attempt=0; attempt<40; attempt++)); do
        if curl --max-time 5 -fsS -G --data-urlencode "query=$query" "$url" > "$logs/echecker-probe-$2.json" 2>/dev/null && \
            python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["data"]["result"]; sys.exit(not (r and r[0]["value"][1]==sys.argv[2]))' "$logs/echecker-probe-$2.json" "$1"; then
            return
        fi
        sleep 1
    done
    return 1
}
task() {
    python3 "$FINAL_CONFIG/observe.py" run "$checkout" "$logs/request.json" "$run_path/$1" \
        "$FINAL_CONFIG/observations" "$draft_port" "$build_port" "$echeck_port" "$fix_port" | tee "$logs/$1.log"
}
demo_pause() {
    if [[ ${FINAL_DEMO:-0} == 1 ]]; then
        printf '\n%s\n' "$1"
        read -r -p '确认后按 Enter 继续：' _
    fi
}
health before
wait_probe 1 before
demo_pause "服务已就绪。Grafana 端口是 $FINAL_GRAFANA_PORT，登录密码在 RUN_ROOT 下的 .env。"
task normal
python3 labs/e13e14/verify_e14.py "$run_path/normal" > "$logs/normal-verification.json"
sleep 5
demo_pause '正常任务已通过。先看任务计数和日志，再进入停机。'
date -Is > "$logs/echecker-stop.txt"
compose stop echecker
wait_probe 0 down
failed_exit=0
task down || failed_exit=$?
test "$failed_exit" -eq 1
python3 - "$run_path/down" <<'PY'
import json
from pathlib import Path
import sys

out = Path(sys.argv[1])
result = json.loads((out / 'result.json').read_bytes())
failure = json.loads((out / 'incremental-response-transport-error.json').read_bytes())
assert result['status'] == 'FAILED' and 'echecker: DOWNSTREAM_UNAVAILABLE' == result['error']
assert [value['name'] for value in result['stages']] == ['draft', 'full-check']
assert all(result[key] == failure[key] for key in ('job_id', 'trace_id'))
assert failure['role'] == 'echecker' and failure['error_code'] == 'DOWNSTREAM_UNAVAILABLE'
PY
sleep 5
demo_pause '故障任务已经结束。先找 EChecker 角色和失败阶段，再恢复服务。'
compose start echecker
wait_probe 1 recovered
health after
date -Is > "$logs/echecker-recovered.txt"
task recovered
python3 labs/e13e14/verify_e14.py "$run_path/recovered" > "$logs/recovered-verification.json"
sleep 6
python3 - "$run_path" <<'PY'
import base64
import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

root = Path(sys.argv[1])
logs = root / 'evidence'
prom = f"http://127.0.0.1:{os.environ['FINAL_PROM_PORT']}"
grafana = f"http://127.0.0.1:{os.environ['FINAL_GRAFANA_PORT']}"


def get(url, filename, headers=None):
    with urlopen(Request(url, headers=headers or {}), timeout=10) as response:
        raw = response.read()
    (logs / filename).write_bytes(raw)
    return json.loads(raw)


targets = get(f'{prom}/api/v1/targets', 'prometheus-targets.json')['data']['activeTargets']
assert any(item['health'] == 'up' and item['labels']['job'] == 'a16-task-telemetry' for item in targets)
window = {'start': int((logs / 'start.epoch').read_text()), 'end': int(time.time()), 'step': 2}
(logs / 'metrics-window.json').write_text(json.dumps(window, indent=2) + '\n')
queries = {'role-ready': 'a16_role_ready', 'jobs-total': 'a16_jobs_total',
           'duration': 'a16_job_duration_seconds_sum / a16_job_duration_seconds_count'}
curves = {}
for name, query in queries.items():
    result = get(f'{prom}/api/v1/query_range?{urlencode(dict(window, query=query))}', f'prometheus-{name}.json')
    curves[name] = result['data']['result']
echecker = next(series for series in curves['role-ready'] if series['metric']['role'] == 'echecker')
values = [value for _, value in echecker['values']]
down = values.index('0')
assert '1' in values[:down] and '1' in values[down + 1:]
counts = {series['metric']['status']: series['values'][-1][1] for series in curves['jobs-total']}
assert counts == {'SUCCEEDED': '2', 'FAILED': '1'}, counts
credential = (root / '.env').read_text().strip().split('=', 1)[1]
auth = base64.b64encode(f'admin:{credential}'.encode()).decode()
dashboard = get(f'{grafana}/api/dashboards/uid/a16-microservice-real', 'grafana-dashboard.json',
                {'Authorization': f'Basic {auth}'})
assert len(dashboard['dashboard']['panels']) == 3
print('PASS Prometheus observed EChecker 1 -> 0 -> 1 and terminal count 2 SUCCEEDED / 1 FAILED')
PY
demo_pause '恢复任务和图表已核验。保存截图后退出本次 Compose。'
