#!/usr/bin/env bash
set -euo pipefail
cd /root/241880485/DevOps-G16-e8-A1-20261103
source /root/241880485/e8-classroom_helpers-20261103.sh
lab_ready
test -z "$(git status --porcelain)"
lab_new_run e10 A
printf '%s\n' "$OUT" > work/A1-E10-deletion.path
cp "$0" "$OUT/executed-route.sh"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/started-utc.txt"
git status --porcelain > "$OUT/student-source-status.txt"
docker image inspect "$LAB_IMAGE" > "$OUT/image-inspect.json"
lab_python "$OUT" <<'PY'
from pathlib import Path
from statistics import median
import csv,json,sys
from lab import fixture,scan,save,commit,buildchecker,run
out=Path(sys.argv[1]);p=out/'project';fixture(p)
# Define the outcome from the planned input before scanning the changed state.
expected={'provenance':'A1_EXPECTED_FROM_PLANNED_HEADER_REMOVAL',
 'scenario':'remove config.h include of extra.h and delete extra.h',
 'actual':{'main.o':['config.h','main.c'],'helper.o':['helper.c']},
 'declared':{'main.o':['main.c','unused.h'],'helper.o':['helper.c']},
 'findings':[['MISSING','main.o','config.h'],['REDUNDANT','main.o','unused.h']],
 'added':[],'resolved':[['MISSING','main.o','extra.h']],
 'refreshed':['main.o','helper.o'],'reused':[]}
save(out/'independent-expected.json',expected)
(p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
commit(p,'A1 setup indirect header before deletion')
before=scan(p);save(out/'baseline.json',before)
assert before['actual']=={'main.o':['config.h','extra.h','main.c'],'helper.o':['helper.c']}
buildchecker(p,out/'buildchecker-before')
(p/'config.h').write_text('#define VALUE 1\n');(p/'extra.h').unlink()
changed=commit(p,'A1 remove indirect include and delete extra.h')
rows=[]
for repeat in range(1,6):
    inc=scan(p,before);full=scan(p)
    save(out/f'deletion-r{repeat}-incremental.json',inc);save(out/f'deletion-r{repeat}-full.json',full)
    for report in [inc,full]:
        assert report['commit']==changed
        assert report['actual']==expected['actual'] and report['declared']==expected['declared']
        assert sorted([f['type'],f['target'],f['dependency']] for f in report['findings'])==expected['findings']
    assert all(inc[k]==full[k] for k in ['actual','declared','findings'])
    for field in ['added','resolved','refreshed','reused']:assert inc[field]==expected[field],field
    row={'case':'remove-indirect-header','repeat':repeat,'equal':True,'incremental_s':inc['elapsed_s'],'full_s':full['elapsed_s'],'reused':len(inc['reused']),'refreshed':len(inc['refreshed'])}
    rows.append(row);print(row)
with (out/'results.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
inc_times=[r['incremental_s'] for r in rows];full_times=[r['full_s'] for r in rows]
mi,mf=median(inc_times),median(full_times)
with (out/'performance-summary.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['case','n','inc_median_s','full_median_s','inc_min_s','inc_max_s','full_min_s','full_max_s','full_over_inc'])
    w.writerow(['remove-indirect-header',5,mi,mf,min(inc_times),max(inc_times),min(full_times),max(full_times),mf/mi])
buildchecker(p,out/'buildchecker-after')
edges=json.loads((out/'buildchecker-after/actual-graph.json').read_text())
projected={t:sorted({e['dependency'] for e in edges if e['target']==t}) for t in ['main.o','helper.o']}
assert projected==expected['actual']
(out/'build.log').write_text(run(['make','app'],p));(out/'program-output.txt').write_text(run(['./app'],p))
assert (out/'program-output.txt').read_text().strip()=='1'
save(out/'gate.json',{'passed':True,'rows':5,'independent_expected':True,'dynamic_actual_equal':True,'baseline_commit':before['commit'],'changed_commit':changed})
print('A1_HEADER_DELETION_FIVE_REPEATS_AND_DYNAMIC_PASS')
PY
git -C "$OUT/project" bundle create "$PWD/$OUT/project-history.bundle" HEAD
git -C "$OUT/project" log --reverse --format='%H %s' > "$OUT/project-history.txt"
git -C "$OUT/project" log --reverse --format=fuller --stat --patch > "$OUT/project-history.patch.log"
printf '删除extra.h并移除间接include：完整图减一边、extra.h MD消除；五次从相同旧图扫描并保守刷新两个目标；独立预期、全量和动态投影一致。\n' > "$OUT/结论.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/finished-utc.txt"
printf 'FINISHED_OUT=%s\n' "$OUT"
