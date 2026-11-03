"""本人 E8/E9 自主贡献：共享间接依赖与间接依赖移除。"""
import sys
from pathlib import Path
from lab import fixture, scan, commit, save, buildchecker


def finding(kind, dependency, target='main.o'):
    return {'type': kind, 'target': target, 'dependency': dependency}


def add_shared_header(project):
    (project/'shared.h').write_text('#define SHARED_ZERO 0\n')
    (project/'config.h').write_text('#include "shared.h"\n#define VALUE 1\n')
    (project/'helper.c').write_text('#include "shared.h"\nint helper(void){return SHARED_ZERO;}\n')
    return commit(project, 'A3 E8: shared header via two object jobs')


def check_shared(report, full):
    expected = {
        'actual': {'main.o': ['config.h','main.c','shared.h'], 'helper.o': ['helper.c','shared.h']},
        'declared': {'main.o': ['main.c','unused.h'], 'helper.o': ['helper.c']},
        'findings': [finding('MISSING','config.h'), finding('MISSING','shared.h'),
                     finding('REDUNDANT','unused.h'), finding('MISSING','shared.h','helper.o')],
    }
    for key, value in expected.items():
        assert report[key] == full[key] == value, (key, report[key], value)
    assert report['reused'] == [] and report['refreshed'] == ['main.o','helper.o']
    assert report['added'] == [['MISSING','helper.o','shared.h'], ['MISSING','main.o','shared.h']]
    assert report['resolved'] == []


def prepare_chain(project):
    fixture(project)
    (project/'config.h').write_text('#include "branch.h"\n#define VALUE 1\n')
    (project/'branch.h').write_text('#include "leaf.h"\n')
    (project/'leaf.h').write_text('#define LEAF_ZERO 0\n')
    commit(project, 'A3 E9: nested header baseline')
    return scan(project)


def remove_indirect_include(project):
    (project/'branch.h').write_text('/* leaf no longer included; file retained */\n')
    return commit(project, 'A3 E9: remove nested include')


def check_removed(report, full):
    expected = {
        'actual': {'main.o': ['branch.h','config.h','main.c'], 'helper.o': ['helper.c']},
        'declared': {'main.o': ['main.c','unused.h'], 'helper.o': ['helper.c']},
        'findings': [finding('MISSING','branch.h'), finding('MISSING','config.h'), finding('REDUNDANT','unused.h')],
    }
    for key, value in expected.items():
        assert report[key] == full[key] == value, (key, report[key], value)
    assert report['reused'] == [] and report['refreshed'] == ['main.o','helper.o']
    assert report['added'] == []
    assert report['resolved'] == [['MISSING','main.o','leaf.h']]


def run_extension(stage, out):
    project = out/'project'
    if stage == 'e8':
        save(out/'expected.json', {'description':'共享头通过config.h间接被main.o读取，同时被helper.o直接读取；新增两条shared.h MD，保留config.h MD与unused.h RD。',
             'actual':{'main.o':['config.h','main.c','shared.h'],'helper.o':['helper.c','shared.h']},
             'added':[['MISSING','helper.o','shared.h'],['MISSING','main.o','shared.h']]})
        fixture(project)
        baseline = scan(project)
        save(out/'baseline-gcc-projection.json', baseline)
        buildchecker(project, out/'baseline-buildchecker')
        import json
        edges = json.loads((out/'baseline-buildchecker/actual-graph.json').read_text())
        baseline['actual'] = {t:sorted({e['dependency'] for e in edges if e['target']==t}) for t in ['main.o','helper.o']}
        baseline['baseline_source'] = 'BuildChecker actual-graph.json projected to object targets'
        save(out/'baseline.json', baseline)
        add_shared_header(project)
        report, full = scan(project, baseline), scan(project)
        save(out/'incremental.json', report); save(out/'full.json', full)
        check_shared(report, full)
        buildchecker(project, out/'after-buildchecker')
    elif stage == 'e9':
        save(out/'expected.json', {'description':'仅移除branch.h中的间接include，保留leaf.h文件；两个对象刷新，仅消除MD leaf.h，再只补声明复用两对象并保留RD unused.h。',
             'actual':{'main.o':['branch.h','config.h','main.c'],'helper.o':['helper.c']},
             'resolved':[['MISSING','main.o','leaf.h']]})
        baseline = prepare_chain(project)
        assert baseline['actual'] == {'main.o':['branch.h','config.h','leaf.h','main.c'],'helper.o':['helper.c']}
        save(out/'baseline.json', baseline)
        remove_indirect_include(project)
        report, full = scan(project, baseline), scan(project)
        save(out/'removed-incremental.json',report); save(out/'removed-full.json',full)
        check_removed(report, full)
        makefile=project/'Makefile'
        makefile.write_text(makefile.read_text().replace('main.c unused.h','main.c unused.h config.h branch.h'))
        commit(project,'A3 E9: declare remaining actual headers')
        repaired=scan(project,report)
        save(out/'declared.json',repaired)
        assert repaired['actual'] == report['actual']
        assert repaired['reused'] == ['main.o','helper.o'] and repaired['refreshed'] == []
        assert repaired['findings'] == [finding('REDUNDANT','unused.h')]
        assert repaired['resolved'] == [['MISSING','main.o','branch.h'],['MISSING','main.o','config.h']]
        buildchecker(project,out/'final-buildchecker')
    else:
        raise ValueError(stage)
    save(out/'gate.json',{'stage':stage,'track':'A','passed':True,'independent_expected':True})
    print(stage.upper()+'_PERSONAL_EXTENSION_PASS')


if __name__ == '__main__':
    run_extension(sys.argv[1], Path(sys.argv[2]))
