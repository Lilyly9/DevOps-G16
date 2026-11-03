#!/usr/bin/env bash
set -euo pipefail
cd /root/241880485/DevOps-G16-e8-A1-20261103
source /root/241880485/e8-classroom_helpers-20261103.sh
lab_ready
test -z "$(git status --porcelain)"
test "$(git rev-parse HEAD)" = 18a79582672a71d486abc656bc9007d4aebdceab
lab_new_run e9 A
printf '%s\n' "$OUT" > work/A1-E9-manual.path
cp "$0" "$OUT/executed-route.sh"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/started-utc.txt"
git status --porcelain > "$OUT/student-source-status.txt"
docker image inspect "$LAB_IMAGE" > "$OUT/image-inspect.json"
printf '122604049bfc828119c525bf960585ab86f054eeda4060bfd6a3fc6a722c8019  9_E9_A组.md\n' > "$OUT/manual-sha256.txt"

# Unmodified official E9-A manual code block 1
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from lab import fixture
out=Path(sys.argv[1]); fixture(out/'project')
print('CREATED',out/'project')
PY

# Unmodified official E9-A manual code block 2
pwd
cat "$OUT/student-source-commit.txt"
cat "$OUT/project/Makefile"
cat "$OUT/project/main.c"
cat "$OUT/project/config.h"
cat "$OUT/project/helper.c"
git -C "$OUT/project" log -1 --oneline

# Unmodified official E9-A manual code block 3
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from lab import scan,save,run
out=Path(sys.argv[1]);p=out/'project'
(out/'C0-build.log').write_text(run(['make','app'],p))
save(out/'baseline.json',scan(p))
assert run(['./app'],p).strip()=='1'
print('C0_BUILD_AND_BASELINE_PASS')
PY

# Unmodified official E9-A manual code block 4
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys,time
from lab import commit,run
out=Path(sys.argv[1]);p=out/'project';time.sleep(1.05)
f=p/'main.c';f.write_text(f.read_text().replace('VALUE+helper()','VALUE+helper()+0'))
print('C1',commit(p,'C1 body change'))
(out/'C1-build.log').write_text(run(['make','app'],p))
print((out/'C1-build.log').read_text())
PY

# Unmodified official E9-A manual code block 5
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import scan,save
out=Path(sys.argv[1]);old=json.loads((out/'baseline.json').read_text())
r=scan(out/'project',old);save(out/'C1.json',r)
assert r['reused']==['main.o','helper.o'] and r['refreshed']==[]
assert r['findings']==old['findings'] and r['added']==[] and r['resolved']==[]
print('C1_REUSE_PASS',r['reused'])
PY

# Unmodified official E9-A manual code block 6
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys,time
from lab import commit,run
out=Path(sys.argv[1]);p=out/'project';time.sleep(1.05)
f=p/'main.c';f.write_text('#include "extra.h"\n'+f.read_text())
print('C2',commit(p,'C2 include change'))
(out/'C2-build.log').write_text(run(['make','app'],p))
print((out/'C2-build.log').read_text())
PY

# Unmodified official E9-A manual code block 7
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import scan,save
out=Path(sys.argv[1]);old=json.loads((out/'C1.json').read_text())
r=scan(out/'project',old);save(out/'C2.json',r)
assert set(r['refreshed'])=={'main.o','helper.o'}
assert ['MISSING','main.o','extra.h'] in r['added']
assert 'extra.h' in r['actual']['main.o']
print('C2_REFRESH_PASS',r['added'])
PY

# Unmodified official E9-A manual code block 8
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from lab import commit
out=Path(sys.argv[1]);p=out/'project';f=p/'Makefile'
f.write_text(f.read_text().replace('main.c unused.h','main.c unused.h config.h extra.h'))
print('C3',commit(p,'C3 repair declarations'))
print(f.read_text())
PY

# Unmodified official E9-A manual code block 9
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import scan,save
out=Path(sys.argv[1]);old=json.loads((out/'C2.json').read_text())
r=scan(out/'project',old);save(out/'C3.json',r)
assert r['reused']==['main.o','helper.o']
assert sorted(r['resolved'])==[['MISSING','main.o','config.h'],['MISSING','main.o','extra.h']]
assert r['findings']==[{'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}]
print('C3_RESOLVED_PASS',r['resolved'])
PY

# Unmodified official E9-A manual code block 10
git -C "$OUT/project" log --oneline --reverse
python3 - "$OUT" <<'PY'
from pathlib import Path
import sys,json
out=Path(sys.argv[1])
for name in ['baseline','C1','C2','C3']:
 r=json.loads((out/(name+'.json')).read_text())
 print(name,r['commit'],r['reused'],r['refreshed'],r['added'],r['resolved'])
PY

# Additional A1 checks do not replace any official step.
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import run,save
out=Path(sys.argv[1]);p=out/'project'
reports={n:json.loads((out/(n+'.json')).read_text()) for n in ['baseline','C1','C2','C3']}
expected0={'main.o':['config.h','main.c'],'helper.o':['helper.c']}
expected2={'main.o':['config.h','extra.h','main.c'],'helper.o':['helper.c']}
expected_findings={('MISSING','main.o','config.h'),('REDUNDANT','main.o','unused.h')}
norm=lambda r:{(f['type'],f['target'],f['dependency']) for f in r['findings']}
assert reports['baseline']['actual']==expected0 and norm(reports['baseline'])==expected_findings
assert reports['C1']['actual']==expected0 and norm(reports['C1'])==expected_findings
assert reports['C2']['actual']==expected2 and norm(reports['C2'])==expected_findings|{('MISSING','main.o','extra.h')}
assert reports['C3']['actual']==expected2 and norm(reports['C3'])=={('REDUNDANT','main.o','unused.h')}
assert len({r['commit'] for r in reports.values()})==4
for name,report in reports.items():
    (out/(name+'-commit-input.txt')).write_text(run(['git','show',report['commit']+':Makefile'],p)+'\n'+run(['git','show',report['commit']+':main.c'],p))
(out/'C3-build.log').write_text(run(['make','app'],p))
assert run(['./app'],p).strip()=='1'
(out/'program-output.txt').write_text(run(['./app'],p))
save(out/'a1-complete-check.json',{'passed':True,'commits':{n:r['commit'] for n,r in reports.items()},'expected_from_input':True})
print('A1_E9_COMPLETE_INPUT_AND_HISTORY_CHECK_PASS')
PY
git -C "$OUT/project" bundle create "$PWD/$OUT/project-history.bundle" HEAD
git -C "$OUT/project" log --reverse --format='%H %s' > "$OUT/project-history.txt"
git -C "$OUT/project" log --reverse --format=fuller --stat --patch > "$OUT/project-history.patch.log"
printf 'A1 E9：C1构建重编main.o但依赖图复用；C2刷新并新增extra.h MD；C3补声明消除两项MD、RD保留。\n' > "$OUT/结论.txt"

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/finished-utc.txt"
printf 'FINISHED_OUT=%s\n' "$OUT"
