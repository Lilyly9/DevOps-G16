"""A3 自主配置场景：条件编译宏启用新的本地依赖。"""
import csv
import json
import sys
from pathlib import Path
from statistics import median
from lab import fixture, scan, save, commit

EXPECTED_ACTUAL = {'main.o': ['config.h', 'main.c', 'mode.h'], 'helper.o': ['helper.c']}
EXPECTED_DECLARED = {'main.o': ['main.c', 'unused.h'], 'helper.o': ['helper.c']}
EXPECTED_FINDINGS = [
    {'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'},
    {'type': 'MISSING', 'target': 'main.o', 'dependency': 'mode.h'},
    {'type': 'REDUNDANT', 'target': 'main.o', 'dependency': 'unused.h'},
]

def prepare(project):
    fixture(project)
    (project/'mode.h').write_text('#define MODE_EXTRA 0\n')
    source = project/'main.c'
    source.write_text('#ifdef MODE\n#include "mode.h"\n#endif\n' + source.read_text())
    commit(project, 'A3: conditional header disabled')
    return scan(project)

def enable(project):
    makefile = project/'Makefile'
    makefile.write_text(makefile.read_text().replace('-O0', '-O0 -DMODE=1'))
    return commit(project, 'A3: enable MODE dependency')

def check(incremental, full):
    for key, expected in [('actual', EXPECTED_ACTUAL), ('declared', EXPECTED_DECLARED), ('findings', EXPECTED_FINDINGS)]:
        assert incremental[key] == expected, (key, incremental[key], expected)
        assert full[key] == expected, (key, full[key], expected)
    assert incremental['reused'] == []
    assert incremental['refreshed'] == ['main.o', 'helper.o']
    assert incremental['added'] == [['MISSING', 'main.o', 'mode.h']]
    assert incremental['resolved'] == []

def measure(out):
    out.mkdir()
    # 独立预期先落盘，随后才创建输入、运行扫描。
    save(out/'expected.json', {'actual': EXPECTED_ACTUAL, 'declared': EXPECTED_DECLARED,
         'findings': EXPECTED_FINDINGS, 'reused': [], 'refreshed': ['main.o', 'helper.o'],
         'added': [['MISSING', 'main.o', 'mode.h']], 'resolved': []})
    project = out/'project'
    previous = prepare(project)
    assert previous['actual'] == {'main.o': ['config.h', 'main.c'], 'helper.o': ['helper.c']}
    save(out/'baseline.json', previous)
    enable(project)
    rows = []
    for repeat in range(1, 6):
        incremental, full = scan(project, previous), scan(project)
        save(out/f'macro-enabled-r{repeat}-incremental.json', incremental)
        save(out/f'macro-enabled-r{repeat}-full.json', full)
        check(incremental, full)
        rows.append({'case': 'macro-enabled', 'repeat': repeat, 'equal': True,
                     'incremental_s': incremental['elapsed_s'], 'full_s': full['elapsed_s'],
                     'reused': len(incremental['reused']), 'refreshed': len(incremental['refreshed'])})
        print(rows[-1])
    with (out/'results.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    inc = [row['incremental_s'] for row in rows]; full = [row['full_s'] for row in rows]
    with (out/'performance-summary.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['case','n','inc_median_s','full_median_s','inc_min_s','inc_max_s','full_over_inc'])
        writer.writerow(['macro-enabled',5,median(inc),median(full),min(inc),max(inc),median(full)/median(inc)])
    save(out/'gate.json', {'track':'A','passed':True,'rows':5,'independent_expected':True})
    print('A3_MACRO_FIVE_REPEATS_PASS')

if __name__ == '__main__':
    measure(Path(sys.argv[1])/'extension')
