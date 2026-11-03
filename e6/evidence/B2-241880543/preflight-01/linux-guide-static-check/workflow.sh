(
set -euo pipefail
cd e5/B-draft

fresh_dir() {
    local base="$1" candidate="$1" n=1
    while [[ -e "$candidate" ]]; do
        printf -v candidate '%s-%02d' "$base" "$n"
        n=$((n + 1))
    done
    printf '%s\n' "$candidate"
}

capture() {
    local label="$1" code
    shift
    local folder="$log_dir/$label"
    mkdir "$folder"
    printf '%q ' "$@" > "$folder/command.sh"
    printf '\n' >> "$folder/command.sh"
    if "$@" > "$folder/stdout.log" 2> "$folder/stderr.log"; then
        code=0
    else
        code=$?
    fi
    printf '%s\n' "$code" > "$folder/exit-code.txt"
    cat "$folder/stdout.log"
    cat "$folder/stderr.log" >&2
    printf '%s EXIT_CODE=%s\n' "$label" "$code"
    return "$code"
}

mkdir -p work
log_dir=$(fresh_dir work/B2-241880543-linux)
mkdir "$log_dir"
build_dir=$(fresh_dir work/build-B2-01)
e6_dir=$(fresh_dir work/e6-B2-replay)
printf 'logs=%s\nbuild=%s\ne6=%s\n' "$log_dir" "$build_dir" "$e6_dir" \
    | tee "$log_dir/paths.txt"

capture doctor python3 scripts/lab_cloud.py doctor
capture build python3 scripts/lab_cloud.py build \
    --out "$build_dir" --image course1020-draft:241880543 --build-timeout 1200
capture e6 python3 scripts/lab_cloud.py e6 --replay \
    --out "$e6_dir" --image course1020-draft:241880543 --build-timeout 600
capture verify python3 scripts/verify_e6_b_evidence.py \
    --run-dir "$e6_dir/evidence"

# 只读独立复核：不调用课程验证函数，不改写实验 JSON。
cat > "$log_dir/independent_check.py" <<'PY'
import hashlib
import json
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
try:
    report = json.loads((root / "result.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as exc:
    print(f"FAIL: cannot read experiment result: {exc}")
    raise SystemExit(1)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def baseline():
    attempts = report["attempts"]
    require(len(attempts) == 2 and [a["iteration"] for a in attempts] == [1, 2],
            "expected exactly two ordered attempts")
    first = attempts[0]
    logs = "\n".join((root / "iter-01" / name).read_text(encoding="utf-8")
                     for name in ("build-stdout.log", "build-stderr.log"))
    require(first["build_exit_code"] != 0 and first["failure_class"] == "MISSING_MAKE",
            "baseline exit/classification mismatch")
    require(re.search(r"/bin/sh:.*\bmake: (?:not found|command not found)", logs),
            "missing-make message absent from raw logs")
    return f'MISSING_MAKE; build_exit_code={first["build_exit_code"]}'

def fixed():
    second = report["attempts"][1]
    require(second["iteration"] == 2 and second["build_exit_code"] == 0,
            "second build did not exit 0")
    logs = [(root / "iter-02" / name).read_bytes()
            for name in ("build-stdout.log", "build-stderr.log")]
    require(any(logs), "second build logs empty")
    return "build_exit_code=0; saved logs present"

def image():
    built = json.loads((root / "iter-02/image-inspect.json").read_text(encoding="utf-8"))[0]["Id"]
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", built), "invalid image ID")
    require(built == report["attempts"][1]["image_id"] == report["verification"]["command"][-1],
            "inspect, built and run image IDs differ")
    return built

def output():
    verification = report["verification"]
    actual = (root / "verify.log").read_text(encoding="utf-8")
    require(verification["exit_code"] == 0 and verification["output_matches"] is True,
            "runtime exit/output flag mismatch")
    require(actual == verification["actual_output"] and actual.rstrip("\r\n") == "hello E3"
            and verification["expected_output"] == "hello E3", "raw output mismatch")
    return "exit_code=0; hello E3; output_matches=true"

def inputs():
    project = root / "project"
    require(project.is_dir(), "project snapshot absent")
    require(not (project / "Dockerfile.reference").exists(), "reference answer in project")
    expected = report["input_sha256"]
    for name in expected:
        require((project / name).resolve().is_relative_to(project.resolve()), "input path outside project")
    # 与 autobuild.py 相同：有序递归、POSIX 相对路径、文件原始字节 SHA-256。
    actual = {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(project.rglob("*")) if p.is_file()}
    require(actual and actual == expected, "input file set or raw-byte hashes differ")
    return f"{len(actual)} input files; all hashes match"

checks = [
    ("第一轮缺少 make", "非零退出；MISSING_MAKE；原始日志吻合", "result.json; iter-01/build-*.log", baseline),
    ("第二轮构建成功", "build_exit_code=0；构建日志存在", "result.json; iter-02/build-*.log", fixed),
    ("同镜像运行", "inspect ID = 第二轮 ID = run 命令 ID", "iter-02/image-inspect.json; result.json", image),
    ("运行输出与退出码", "hello E3；exit=0；output_matches=true", "verify.log; result.json", output),
    ("输入副本哈希", "project 全部文件原始字节哈希及键集合一致", "project/; result.json input_sha256", inputs),
]
print("| 检查项目 | 预期结果 | 实际结果 | 证据文件路径 | PASS / FAIL |")
print("| --- | --- | --- | --- | --- |")
passed = report.get("status") == "SUCCEEDED"
for name, expected, paths, check in checks:
    try:
        actual, verdict = check(), "PASS"
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        actual, verdict, passed = str(exc), "FAIL", False
    actual = actual.replace("|", "\\|").replace("\n", " ")
    print(f"| {name} | {expected} | {actual} | {paths} | {verdict} |")
print(f'\nWorkflow status: {report.get("status")}; independent audit passed: {passed}')
raise SystemExit(0 if passed else 1)
PY

capture independent python3 "$log_dir/independent_check.py" "$e6_dir/evidence"
cp -- "$log_dir/independent/stdout.log" "$log_dir/five-checks.md"
printf 'Review actual logs and archive selected evidence from %s and %s\n' "$log_dir" "$e6_dir"
)
