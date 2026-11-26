#!/usr/bin/env bash
# Submit the maintained transfer-eta revisions through the teacher E12 client.
# Usage: bash run-e12.sh /absolute/Microservice_Lab.zip [G16_REPO_ROOT]
# E12_IMAGE selects an existing course image. Otherwise the local numeric Git
# user.name selects course-e11e12:<student-id>. Run on the Linux Docker host.
# The source is its committed HEAD. The temporary checkout and archive are kept.
set -Eeuo pipefail
umask 077

usage() {
    cat <<'TEXT'
Usage: bash run-e12.sh /absolute/Microservice_Lab.zip [G16_REPO_ROOT]

Run from a Linux host with Docker, Git, Python 3, curl and an existing E12 image.
Keep verify_transfer_eta.py beside this script. The optional repository argument
defaults to the repository containing labs/final-microservice/run-e12.sh.

E12_IMAGE can select the teaching image explicitly. TMPDIR controls where the
isolated checkout is created. Evidence and the checkout remain there after exit.
TEXT
}

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    usage
    exit 0
fi
if [[ $# -lt 1 || $# -gt 2 ]]; then
    usage >&2
    exit 2
fi
if [[ $(uname -s) != Linux ]]; then
    printf 'Run this script on the Linux Docker host.\n' >&2
    exit 2
fi
for command in docker git python3 curl sha256sum tar mktemp stat realpath; do
    command -v "$command" >/dev/null || { printf 'Required command missing: %s\n' "$command" >&2; exit 2; }
done

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
script_file="$script_dir/$(basename -- "${BASH_SOURCE[0]}")"
teacher_zip=$(realpath -e -- "$1")
repo=$(realpath -e -- "${2:-$script_dir/../..}")
helper="$script_dir/verify_transfer_eta.py"
test -f "$teacher_zip"
test -f "$helper"
repo=$(git -C "$repo" rev-parse --show-toplevel)
pinned=$(git -C "$repo" rev-parse HEAD)
base=5ef9d829e2f893af23f60399dcb67095800d121e
target=e7414083c4f1760cb234f96a9d75f2d0255e3f57
for revision in "$base" "$target"; do
    git -C "$repo" cat-file -e "$revision:projects/transfer-eta/Makefile"
done

image=${E12_IMAGE:-}
if [[ -z "$image" ]]; then
    sid=$(git -C "$repo" config --local user.name || true)
    if [[ ! "$sid" =~ ^[0-9]{6,16}$ ]]; then
        printf 'Set E12_IMAGE to an existing course E11-E12 image.\n' >&2
        exit 2
    fi
    image="course-e11e12:$sid"
fi
docker info >/dev/null
docker image inspect "$image" >/dev/null
test -S /var/run/docker.sock

run_root=$(mktemp -d "${TMPDIR:-/tmp}/g16-final-e12.XXXXXX")
checkout="$run_root/DevOps-G16"
container_name="g16-final-e12-${run_root##*.}"
container_name=${container_name,,}
archive="$run_root-evidence.tar.gz"
printf 'RUN_ROOT=%s\nSOURCE_SHA=%s\n' "$run_root" "$pinned"
git clone --quiet --no-hardlinks --no-checkout "$repo" "$checkout"
git -C "$checkout" checkout --quiet --detach "$pinned"
cd "$checkout"
mkdir -p data/final-eta work/client/scripts work/experiment
printf '%s\n' "$pinned" > work/experiment/source.sha
printf '%s\n' "$base" "$target" > work/experiment/project-commits.txt
cp -- "$helper" work/experiment/verify_transfer_eta.py
cp -- "$script_file" work/experiment/run-e12.sh
sha256sum "$teacher_zip" > work/experiment/teacher-archive.sha256
docker image inspect --format '{{.Id}}' "$image" > work/experiment/teaching-image.txt

api_started=0
collect() {
    code=$?
    trap - EXIT
    set +e
    if [[ "$api_started" == 1 ]]; then
        docker logs --timestamps "$container_name" > work/experiment/e12-service.log 2>&1
        docker stop --time 10 "$container_name" >/dev/null 2>&1
    fi
    printf '%s\n' "$code" > work/experiment/scenario.exit
    if tar --exclude=.git --exclude=__pycache__ -czf "$archive" work; then
        sha256sum "$archive" | tee "$archive.sha256"
        printf 'EVIDENCE=%s\nCHECKOUT=%s\n' "$archive" "$checkout"
    else
        printf 'Archive creation failed. Evidence remains in %s/work\n' "$checkout" >&2
        if [[ "$code" == 0 ]]; then code=1; fi
    fi
    exit "$code"
}
trap collect EXIT

git clone --quiet --mirror --no-hardlinks "$checkout" data/final-eta/repo
git show "$target:projects/transfer-eta/candidate.Dockerfile" > data/final-eta/candidate.Dockerfile
sha256sum data/final-eta/candidate.Dockerfile > work/experiment/candidate.sha256
cp data/final-eta/candidate.Dockerfile work/experiment/
python3 - "$teacher_zip" "$base" "$target" <<'PY'
import json
from pathlib import Path
import sys
from zipfile import ZipFile

with ZipFile(sys.argv[1]) as archive:
    for name in ('project.py', 'lab.py'):
        Path('work/client/scripts', name).write_bytes(archive.read('Microservice_Lab/scripts/' + name))
request = {
    'mode': 'e12',
    'repo': '/course/data/final-eta/repo',
    'project_path': 'projects/transfer-eta',
    'profile': True,
    'base': sys.argv[2],
    'target': sys.argv[3],
    'candidate': '/course/data/final-eta/candidate.Dockerfile',
    'expected_output': 'eta_seconds=13',
    'build_timeout': 600,
}
Path('work/experiment/real-request.json').write_text(json.dumps(request, indent=2) + '\n', encoding='utf-8')
PY
sha256sum work/client/scripts/project.py work/client/scripts/lab.py > work/experiment/teacher-client.sha256

docker run --rm -d --name "$container_name" --publish 127.0.0.1::8080 \
    --user "$(id -u):$(id -g)" --group-add "$(stat -c %g /var/run/docker.sock)" \
    --cap-add SYS_PTRACE --network bridge \
    -v "$checkout:/course" -v /var/run/docker.sock:/var/run/docker.sock -w /course \
    -e HOME=/tmp -e "E11E12_DOCKER_HOST_ROOT=$checkout" \
    -e PYTHONPATH=/course/labs/e11e12:/course/labs/e8e10:/course/labs/e11e12/vendor:/app \
    "$image" python3 labs/e11e12/server.py --host 0.0.0.0 > work/experiment/api-container-id.txt
api_started=1
endpoint=$(docker port "$container_name" 8080/tcp)
port=${endpoint##*:}
printf '%s\n' "$endpoint" > work/experiment/api-endpoint.txt
for ((attempt=0; attempt<20; attempt++)); do
    if curl --max-time 2 -fsS "http://$endpoint/health" > work/experiment/e12-health.json 2>/dev/null; then
        break
    fi
    sleep 1
done
test -s work/experiment/e12-health.json
python3 work/client/scripts/project.py work/experiment/real-request.json --port "$port" --wait 900 \
    | tee work/experiment/course-project-console.log
job=$(python3 - <<'PY'
import json
from pathlib import Path

check, = Path('work/client/work').glob('project-*/check.json')
print(json.loads(check.read_bytes())['job_id'])
PY
)
git clone --quiet --no-hardlinks --no-checkout data/final-eta/repo work/reject-source
git -C work/reject-source sparse-checkout set --no-cone -- '/projects/transfer-eta/'
git -C work/reject-source checkout --quiet --detach "$target"
docker exec "$container_name" python3 work/experiment/verify_transfer_eta.py \
    "/course/work/api-jobs/$job/evidence" /course/work/reject-source/projects/transfer-eta \
    /course/work/reject-run "$checkout" | tee work/experiment/independent-check.log
