set -eu
cd /root/241880464/DevOps-G16-e11-e12-A3-20261115
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/course" -w /course -e PYTHONPATH=/course/labs/e11e12:/course/labs/e8e10:/course/labs/e11e12/vendor:/app course-e11e12:241880464 python3 work/a3-20261115/network_inputs.py > work/a3-20261115/logs/network-inputs.log 2>&1
for case_name in e12-cli-fixed-retry e12-cli-real; do
    if [ "$case_name" = e12-cli-fixed-retry ]; then input=data/a3-fixed/request.json; else input=data/a3-real-request.json; fi
    printf 'python3 run_e11e12.py run --request %s --out work/a3-20261115/%s\n' "$input" "$case_name" > "work/a3-20261115/logs/$case_name.command"
    set +e
    python3 run_e11e12.py run --request "$input" --out "work/a3-20261115/$case_name" > "work/a3-20261115/logs/$case_name.log" 2>&1
    code=$?
    set -e
    printf '%s\n' "$code" > "work/a3-20261115/logs/$case_name.exit"
    test "$code" = 0
 done
