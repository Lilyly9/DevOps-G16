#!/usr/bin/env bash
set -euo pipefail
cd /root/241880485/DevOps-G16-e8-A1-20261103
source /root/241880485/e8-classroom_helpers-20261103.sh
lab_ready
lab_new_run e8 A
BASE_OUT="$OUT"
printf '%s\n' "$OUT" > work/A1-E8-baseline.path
cp "$0" "$OUT/executed-route.sh"
docker image inspect "$LAB_IMAGE" > "$OUT/image-inspect.json"
git status --porcelain > "$OUT/student-source-status.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/started-utc.txt"

# Official E8-A manual code block 1
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from lab import fixture
out=Path(sys.argv[1]); fixture(out/'project')
print('CREATED',out/'project')
PY

# Official E8-A manual code block 2
pwd
cat "$OUT/student-source-commit.txt"
cat "$OUT/project/Makefile"
cat "$OUT/project/main.c"
cat "$OUT/project/config.h"
cat "$OUT/project/helper.c"
git -C "$OUT/project" log -1 --oneline

# Official E8-A manual code block 3
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from lab import scan,save
out=Path(sys.argv[1]); report=scan(out/'project')
save(out/'baseline.json',report)
print('actual =',report['actual'])
print('declared =',report['declared'])
print('findings =',report['findings'])
assert report['actual']['main.o']==['config.h','main.c']
assert {(f['type'],f['target'],f['dependency']) for f in report['findings']}=={
 ('MISSING','main.o','config.h'),('REDUNDANT','main.o','unused.h')}
print('BASELINE_PASS')
PY
cp "$OUT/baseline.json" "$OUT/baseline-gcc-projection.json"

# Official E8-A manual code block 4
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import buildchecker,save
out=Path(sys.argv[1]); buildchecker(out/'project',out/'buildchecker')
r=json.loads((out/'baseline.json').read_text())
edges=json.loads((out/'buildchecker/actual-graph.json').read_text())
r['actual']={t:sorted({e['dependency'] for e in edges if e['target']==t}) for t in ['main.o','helper.o']}
r['baseline_source']='BuildChecker actual-graph.json projected to object targets'
save(out/'baseline.json',r)
print('BUILDCHECKER_BASELINE_PASS',r['actual'])
PY

# Official E8-A manual code block 5
cat "$OUT/buildchecker/findings.json"
grep -n 'main.o:' "$OUT/buildchecker/make-db.txt" | head -n 8
grep -n 'config.h' "$OUT/buildchecker/trace/"* | head -n 12
python3 -m json.tool "$OUT/baseline.json"

# Official E8-A manual code block 6
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import scan,save
out=Path(sys.argv[1]); old=json.loads((out/'baseline.json').read_text())
r=scan(out/'project',old);save(out/'incremental.json',r)
assert r['actual']==old['actual']
assert r['findings']==old['findings']
assert r['reused']==['main.o','helper.o'] and r['refreshed']==[]
print('REUSE_PASS',r['reused'],r['refreshed'])
PY

# Official E8-A manual code block 7
git -C "$OUT/project" status --short
printf 'A E8：main.o缺config.h，冗余unused.h；历史图来源为本次BuildChecker；未变化时两个目标复用。
' > "$OUT/结论.txt"
cat "$OUT/结论.txt"
ls "$OUT"

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/finished-utc.txt"
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp   -v "$PWD:/course" -w "/course/$OUT/buildchecker/project" "$LAB_IMAGE" ./app   > "$OUT/program-output.txt"
test "$(cat "$OUT/program-output.txt")" = 1
git -C "$OUT/project" bundle create "$PWD/$OUT/project-history.bundle" HEAD
git -C "$OUT/project" log --format='%H %s' > "$OUT/project-history.txt"

# A1 own extension: a separate fresh fixture and output, not overwriting C0.
lab_new_run e8 A
EXT_OUT="$OUT"
printf '%s\n' "$OUT" > work/A1-E8-extension.path
cp "$0" "$OUT/executed-route.sh"
docker image inspect "$LAB_IMAGE" > "$OUT/image-inspect.json"
git status --porcelain > "$OUT/student-source-status.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/started-utc.txt"
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import fixture,scan,save,commit,buildchecker
out=Path(sys.argv[1]);p=out/'project';fixture(p)
before=scan(p)
buildchecker(p,out/'buildchecker-before')
edges=json.loads((out/'buildchecker-before/actual-graph.json').read_text())
before['actual']={t:sorted({e['dependency'] for e in edges if e['target']==t}) for t in ['main.o','helper.o']}
before['baseline_source']='BuildChecker actual-graph.json projected to object targets'
save(out/'baseline.json',before)
expected_actual={'main.o':['config.h','extra.h','main.c'],'helper.o':['helper.c']}
expected_findings={('MISSING','main.o','config.h'),('MISSING','main.o','extra.h'),('REDUNDANT','main.o','unused.h')}
save(out/'independent-expected.json',{'provenance':'MANUAL_EXPECTED_FROM_EDITED_INPUT','actual':expected_actual,
     'findings':[list(x) for x in sorted(expected_findings)],'refreshed':['main.o','helper.o'],'reused':[],
     'added':[['MISSING','main.o','extra.h']],'resolved':[]})
(p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
changed_commit=commit(p,'A1 E8 indirect include in config.h')
incremental=scan(p,before);full=scan(p)
save(out/'incremental.json',incremental);save(out/'full.json',full)
assert changed_commit!=before['commit'] and incremental['commit']==changed_commit
assert incremental['actual']==expected_actual
assert {(f['type'],f['target'],f['dependency']) for f in incremental['findings']}==expected_findings
assert incremental['refreshed']==['main.o','helper.o'] and incremental['reused']==[]
assert incremental['added']==[['MISSING','main.o','extra.h']] and incremental['resolved']==[]
assert all(incremental[k]==full[k] for k in ['actual','declared','findings'])
buildchecker(p,out/'buildchecker-after')
after=json.loads((out/'buildchecker-after/findings.json').read_text())
actual=json.loads((out/'buildchecker-after/actual-graph.json').read_text())
projected={t:sorted({e['dependency'] for e in actual if e['target']==t}) for t in ['main.o','helper.o']}
assert projected==expected_actual
assert {(f['type'],f['target'],f['dependency']) for f in after['findings'] if f['target'] in expected_actual}==expected_findings
save(out/'extension-check.json',{'passed':True,'source':'A1 independently stated expected edges/findings',
     'incremental_full_equal':True,'dynamic_buildchecker_equal':True,'before_commit':before['commit'],'after_commit':changed_commit})
print('A1_INDIRECT_INCLUDE_EXTENSION_PASS',incremental['added'],incremental['refreshed'])
PY
git -C "$OUT/project" bundle create "$PWD/$OUT/project-history.bundle" HEAD
git -C "$OUT/project" log --reverse --format='%H %s' > "$OUT/project-history.txt"
printf 'A1间接include：新增extra.h实际依赖和MD；两个对象保守刷新；增量/全量/动态BuildChecker投影一致。\n' > "$OUT/结论.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/finished-utc.txt"

TEST_OUT=work/A1-E8-unit-tests-20261103
test ! -e "$TEST_OUT"
mkdir -p "$TEST_OUT"
set +e
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp   -v "$PWD:/course" -w /course "$LAB_IMAGE"   python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v   > "$TEST_OUT/stdout.log" 2> "$TEST_OUT/stderr.log"
TEST_CODE=$?
set -e
printf '%s\n' "$TEST_CODE" > "$TEST_OUT/exit-code.txt"
cat "$TEST_OUT/stdout.log" "$TEST_OUT/stderr.log"
test "$TEST_CODE" = 0
docker run --rm --network none "$LAB_IMAGE" cat /opt/toolchain.lock > "$TEST_OUT/toolchain.lock"
docker image inspect "$LAB_IMAGE" > "$TEST_OUT/image-inspect-after.json"
printf 'BASE_OUT=%s\nEXT_OUT=%s\nUNIT_TEST_EXIT=%s\n' "$BASE_OUT" "$EXT_OUT" "$TEST_CODE"
