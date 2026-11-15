#!/usr/bin/env bash
set -euo pipefail
cd /root/241880485/DevOps-G16-e8-A1-20261103
source /root/241880485/e8-classroom_helpers-20261103.sh
lab_ready
test -z "$(git status --porcelain)"
test "$(git rev-parse HEAD)" = 18a79582672a71d486abc656bc9007d4aebdceab
lab_new_run e10 A
printf '%s\n' "$OUT" > work/A1-E10-manual.path
cp "$0" "$OUT/executed-route.sh"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/started-utc.txt"
git status --porcelain > "$OUT/student-source-status.txt"
docker image inspect "$LAB_IMAGE" > "$OUT/image-inspect.json"
printf '6c44c9ce91472081f5b221060d5b12ce8290149af2c3f7a3b1d6818f2fa8d329  10_E10_A组.md\n' > "$OUT/manual-sha256.txt"

# Unmodified official E10-A manual code block 1
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from lab import fixture,scan,save
out=Path(sys.argv[1])/'matrix';out.mkdir()
fixture(out/'project');save(out/'baseline.json',scan(out/'project'))
print('MATRIX_BASELINE_READY',out)
print((out/'project/Makefile').read_text())
PY

# Unmodified official E10-A manual code block 2
lab_python "$OUT" <<'PY'
from pathlib import Path
import csv,json,sys
from lab import scan,save,commit
out=Path(sys.argv[1])/'matrix';p=out/'project'
previous=json.loads((out/'baseline.json').read_text())
print('NO_SOURCE_CHANGE')
rows=[]
for repeat in range(1,6):
 inc=scan(p,previous);full=scan(p)
 equal=all(inc[k]==full[k] for k in ['actual','declared','findings'])
 save(out/f'unchanged-r{repeat}-incremental.json',inc)
 save(out/f'unchanged-r{repeat}-full.json',full)
 assert equal,'unchanged: dependency graph or findings differ'
 row={'case':'unchanged','repeat':repeat,'equal':equal,'incremental_s':inc['elapsed_s'],'full_s':full['elapsed_s'],'reused':len(inc['reused']),'refreshed':len(inc['refreshed'])}
 rows.append(row);print(row)
with (out/'results.csv').open('a',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]))
 if f.tell()==0:writer.writeheader()
 writer.writerows(rows)
save(out/'unchanged.json',inc)
print('UNCHANGED_FIVE_REPEATS_PASS')
PY

# Unmodified official E10-A manual code block 3
lab_python "$OUT" <<'PY'
from pathlib import Path
import csv,json,sys
from lab import scan,save,commit
out=Path(sys.argv[1])/'matrix';p=out/'project'
previous=json.loads((out/'unchanged.json').read_text())
(p/'helper.c').write_text('int helper(void){return 0+0;}\n')
print('COMMIT',commit(p,'body'))
rows=[]
for repeat in range(1,6):
 inc=scan(p,previous);full=scan(p)
 equal=all(inc[k]==full[k] for k in ['actual','declared','findings'])
 save(out/f'body-r{repeat}-incremental.json',inc)
 save(out/f'body-r{repeat}-full.json',full)
 assert equal,'body: dependency graph or findings differ'
 row={'case':'body','repeat':repeat,'equal':equal,'incremental_s':inc['elapsed_s'],'full_s':full['elapsed_s'],'reused':len(inc['reused']),'refreshed':len(inc['refreshed'])}
 rows.append(row);print(row)
with (out/'results.csv').open('a',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]))
 if f.tell()==0:writer.writeheader()
 writer.writerows(rows)
save(out/'body.json',inc)
print('BODY_FIVE_REPEATS_PASS')
PY

# Unmodified official E10-A manual code block 4
lab_python "$OUT" <<'PY'
from pathlib import Path
import csv,json,sys
from lab import scan,save,commit
out=Path(sys.argv[1])/'matrix';p=out/'project'
previous=json.loads((out/'body.json').read_text())
(p/'main.c').write_text('#include "extra.h"\n'+(p/'main.c').read_text())
print('COMMIT',commit(p,'include'))
rows=[]
for repeat in range(1,6):
 inc=scan(p,previous);full=scan(p)
 equal=all(inc[k]==full[k] for k in ['actual','declared','findings'])
 save(out/f'include-r{repeat}-incremental.json',inc)
 save(out/f'include-r{repeat}-full.json',full)
 assert equal,'include: dependency graph or findings differ'
 row={'case':'include','repeat':repeat,'equal':equal,'incremental_s':inc['elapsed_s'],'full_s':full['elapsed_s'],'reused':len(inc['reused']),'refreshed':len(inc['refreshed'])}
 rows.append(row);print(row)
with (out/'results.csv').open('a',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]))
 if f.tell()==0:writer.writeheader()
 writer.writerows(rows)
save(out/'include.json',inc)
print('INCLUDE_FIVE_REPEATS_PASS')
PY

# Unmodified official E10-A manual code block 5
lab_python "$OUT" <<'PY'
from pathlib import Path
import csv,json,sys
from lab import scan,save,commit
out=Path(sys.argv[1])/'matrix';p=out/'project'
previous=json.loads((out/'include.json').read_text())
f=p/'Makefile';f.write_text(f.read_text().replace('main.c unused.h','main.c unused.h config.h extra.h'))
print('COMMIT',commit(p,'declaration'))
rows=[]
for repeat in range(1,6):
 inc=scan(p,previous);full=scan(p)
 equal=all(inc[k]==full[k] for k in ['actual','declared','findings'])
 save(out/f'declaration-r{repeat}-incremental.json',inc)
 save(out/f'declaration-r{repeat}-full.json',full)
 assert equal,'declaration: dependency graph or findings differ'
 row={'case':'declaration','repeat':repeat,'equal':equal,'incremental_s':inc['elapsed_s'],'full_s':full['elapsed_s'],'reused':len(inc['reused']),'refreshed':len(inc['refreshed'])}
 rows.append(row);print(row)
with (out/'results.csv').open('a',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]))
 if f.tell()==0:writer.writeheader()
 writer.writerows(rows)
save(out/'declaration.json',inc)
print('DECLARATION_FIVE_REPEATS_PASS')
PY

# Unmodified official E10-A manual code block 6
lab_python "$OUT" <<'PY'
from pathlib import Path
import csv,json,sys
from lab import scan,save,commit
out=Path(sys.argv[1])/'matrix';p=out/'project'
previous=json.loads((out/'declaration.json').read_text())
f=p/'Makefile';f.write_text(f.read_text().replace('-O0','-O1'))
print('COMMIT',commit(p,'flags'))
rows=[]
for repeat in range(1,6):
 inc=scan(p,previous);full=scan(p)
 equal=all(inc[k]==full[k] for k in ['actual','declared','findings'])
 save(out/f'flags-r{repeat}-incremental.json',inc)
 save(out/f'flags-r{repeat}-full.json',full)
 assert equal,'flags: dependency graph or findings differ'
 row={'case':'flags','repeat':repeat,'equal':equal,'incremental_s':inc['elapsed_s'],'full_s':full['elapsed_s'],'reused':len(inc['reused']),'refreshed':len(inc['refreshed'])}
 rows.append(row);print(row)
with (out/'results.csv').open('a',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]))
 if f.tell()==0:writer.writeheader()
 writer.writerows(rows)
save(out/'flags.json',inc)
print('FLAGS_FIVE_REPEATS_PASS')
PY

# Unmodified official E10-A manual code block 7
lab_python "$OUT" <<'PY'
from pathlib import Path
import csv,json,sys
from lab import scan,save,commit
out=Path(sys.argv[1])/'matrix';p=out/'project'
previous=json.loads((out/'flags.json').read_text())
(p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
print('COMMIT',commit(p,'header'))
rows=[]
for repeat in range(1,6):
 inc=scan(p,previous);full=scan(p)
 equal=all(inc[k]==full[k] for k in ['actual','declared','findings'])
 save(out/f'header-r{repeat}-incremental.json',inc)
 save(out/f'header-r{repeat}-full.json',full)
 assert equal,'header: dependency graph or findings differ'
 row={'case':'header','repeat':repeat,'equal':equal,'incremental_s':inc['elapsed_s'],'full_s':full['elapsed_s'],'reused':len(inc['reused']),'refreshed':len(inc['refreshed'])}
 rows.append(row);print(row)
with (out/'results.csv').open('a',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]))
 if f.tell()==0:writer.writeheader()
 writer.writerows(rows)
save(out/'header.json',inc)
print('HEADER_FIVE_REPEATS_PASS')
PY

# Unmodified official E10-A manual code block 8
lab_python "$OUT" <<'PY'
from pathlib import Path
import csv,sys
from lab import buildchecker,save
out=Path(sys.argv[1])/'matrix';rows=list(csv.DictReader((out/'results.csv').open()))
assert len(rows)==30 and all(r['equal']=='True' for r in rows)
buildchecker(out/'project',out/'final-buildchecker')
save(out/'gate.json',{'track':'A','passed':True,'rows':len(rows)})
print('DYNAMIC_CROSSCHECK_AND_MATRIX_PASS')
PY

# Unmodified official E10-A manual code block 9
cat "$OUT/matrix/gate.json"
python3 - "$OUT" <<'PY'
from pathlib import Path
from collections import Counter
import csv,json,sys
out=Path(sys.argv[1])/'matrix';rows=list(csv.DictReader((out/'results.csv').open()))
assert len(rows)==30 and all(r['equal']=='True' for r in rows)
counts=Counter(r['case'] for r in rows)
assert set(counts)=={'unchanged','body','include','declaration','flags','header'}
assert all(v==5 for v in counts.values())
assert json.loads((out/'gate.json').read_text())['passed'] is True
print('MATRIX_PASS',dict(counts))
PY

# Unmodified official E10-A manual code block 10
python3 - "$OUT" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1])/'matrix'
for name in ['unchanged','body','include','declaration','flags','header']:
 r=json.loads((p/(name+'.json')).read_text())
 print(name,'reuse=',r['reused'],'refresh=',r['refreshed'],'findings=',r['findings'])
PY

# Unmodified official E10-A manual code block 11
python3 - "$OUT" <<'PY'
from pathlib import Path
from statistics import median
import csv,sys
p=Path(sys.argv[1])/'matrix';rows=list(csv.DictReader((p/'results.csv').open()))
with (p/'performance-summary.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['case','n','inc_median_s','full_median_s','inc_min_s','inc_max_s','full_over_inc'])
 for case in ['unchanged','body','include','declaration','flags','header']:
  group=[r for r in rows if r['case']==case]
  inc=[float(r['incremental_s']) for r in group];full=[float(r['full_s']) for r in group]
  mi,mf=median(inc),median(full);ratio=mf/mi if mi>0 else None
  result=[case,len(group),mi,mf,min(inc),max(inc),ratio]
  w.writerow(result);print(result)
print('SAVED',p/'performance-summary.csv')
PY

# Unmodified official E10-A manual code block 12
cat "$OUT/matrix/final-buildchecker/findings.json"
grep -n 'main.o:' "$OUT/matrix/final-buildchecker/make-db.txt" | head -n 8
ls "$OUT/matrix/final-buildchecker/trace" | head -n 8

# Unmodified official E10-A manual code block 13
grep -nE 'for repeat|passed=all|assert passed' labs/e8e10/lab.py
cat "$OUT/matrix/performance-summary.csv"
printf 'A E10：六类各五次，完整actual/declared/findings对照；性能为本机扫描耗时，最终另做BuildChecker对象目标交叉核对。
' > "$OUT/结论.txt"

# Explicit A1 expectations and complete dynamic graph projection.
lab_python "$OUT" <<'PY'
from pathlib import Path
import json,sys
from lab import save
out=Path(sys.argv[1])/'matrix'
for case in ['unchanged','body','include','declaration','flags','header']:
    r=json.loads((out/(case+'.json')).read_text())
    expected_actual={'main.o':['config.h','main.c'] if case in ['unchanged','body'] else ['config.h','extra.h','main.c'],'helper.o':['helper.c']}
    expected_declared={'main.o':['main.c','unused.h'] if case in ['unchanged','body','include'] else ['config.h','extra.h','main.c','unused.h'],'helper.o':['helper.c']}
    expected_findings={('REDUNDANT','main.o','unused.h')}
    if case in ['unchanged','body','include']:expected_findings.add(('MISSING','main.o','config.h'))
    if case=='include':expected_findings.add(('MISSING','main.o','extra.h'))
    for repeat in range(1,6):
        for kind in ['incremental','full']:
            result=json.loads((out/f'{case}-r{repeat}-{kind}.json').read_text())
            assert result['actual']==expected_actual and result['declared']==expected_declared
            assert {(f['type'],f['target'],f['dependency']) for f in result['findings']}==expected_findings
        inc=json.loads((out/f'{case}-r{repeat}-incremental.json').read_text())
        assert inc['reused']==(['main.o','helper.o'] if case in ['unchanged','body','declaration'] else [])
        assert inc['refreshed']==([] if inc['reused'] else ['main.o','helper.o'])
    if case=='header':final=r
edges=json.loads((out/'final-buildchecker/actual-graph.json').read_text())
projected={t:sorted({e['dependency'] for e in edges if e['target']==t}) for t in ['main.o','helper.o']}
assert projected==final['actual']
save(out/'a1-complete-check.json',{'passed':True,'rows':30,'raw_pairs':30,'full_expected_collections_checked':True,'dynamic_actual_equal':True})
print('A1_E10_ALL_EXPECTED_COLLECTIONS_AND_DYNAMIC_GRAPH_PASS')
PY
git -C "$OUT/matrix/project" bundle create "$PWD/$OUT/matrix/project-history.bundle" HEAD
git -C "$OUT/matrix/project" log --reverse --format='%H %s' > "$OUT/matrix/project-history.txt"
git -C "$OUT/matrix/project" log --reverse --format=fuller --stat --patch > "$OUT/matrix/project-history.patch.log"

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/finished-utc.txt"
printf 'FINISHED_OUT=%s\n' "$OUT"
