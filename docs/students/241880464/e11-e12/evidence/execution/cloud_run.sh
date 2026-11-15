set -eu
cd /root/241880464/DevOps-G16-e11-e12-A3-20261115
ROOT_RUN=work/a3-20261115
mkdir -p "$ROOT_RUN/logs"
git rev-parse HEAD > "$ROOT_RUN/source-sha.txt"
docker image inspect course-e11e12:241880464 --format '{{.Id}}' > "$ROOT_RUN/environment-image-id.txt"
docker run --rm --network none course-e11e12:241880464 cat /opt/toolchain.lock > "$ROOT_RUN/toolchain.lock"
python3 run_e11e12.py test > "$ROOT_RUN/logs/contracts.log" 2>&1
printf '0\n' > "$ROOT_RUN/logs/contracts.exit"
python3 run_e11e12.py prepare > "$ROOT_RUN/logs/prepare.log" 2>&1
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/course" -w /course -e PYTHONPATH=/course/labs/e11e12:/course/labs/e8e10:/course/labs/e11e12/vendor:/app course-e11e12:241880464 python3 work/a3-20261115/setup_inputs.py > "$ROOT_RUN/logs/inputs.log" 2>&1
run_case() {
    case_name=$1
    input=$2
    printf 'python3 run_e11e12.py run --request %s --out %s/%s\n' "$input" "$ROOT_RUN" "$case_name" > "$ROOT_RUN/logs/$case_name.command"
    set +e
    python3 run_e11e12.py run --request "$input" --out "$ROOT_RUN/$case_name" > "$ROOT_RUN/logs/$case_name.log" 2>&1
    code=$?
    set -e
    printf '%s\n' "$code" > "$ROOT_RUN/logs/$case_name.exit"
    test "$code" = 0
}
run_case e11-a-standard data/integration-sample/e11-a.json
run_case e11-a-autonomous data/a3-autonomous/request.json
run_case e12-cli-fixed data/integration-sample/e12.json
run_case e12-cli-real data/a3-real-request.json
