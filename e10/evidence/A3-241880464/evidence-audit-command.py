from pathlib import Path
import csv,json,hashlib,statistics
r=Path('/home/perilla/Documents/DevOps/Practices/E8/DevOps-G16-A3')
w=r/'work/cloud-20261103/work'
standard=next(p for p in w.glob('e10-A-manual.*') if (p/'matrix').is_dir())
extension=next(p for p in w.glob('e10-A-manual.*') if (p/'extension').is_dir())
cases=['unchanged','body','include','declaration','flags','header']
result={}
for name,root in [('cloud',w),('local',r/'work')]:
    m=next(p/'matrix' for p in root.glob('e10-A-manual.*') if (p/'matrix/results.csv').is_file())
    rows=list(csv.DictReader((m/'results.csv').open()))
    assert len(rows)==30
    for case in cases:
        group=[x for x in rows if x['case']==case];assert len(group)==5
        actual={'main.o':['config.h','main.c'],'helper.o':['helper.c']}
        declared={'main.o':['main.c','unused.h'],'helper.o':['helper.c']}
        findings=[{'type':'MISSING','target':'main.o','dependency':'config.h'},{'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}]
        if case in cases[2:]:
            actual['main.o']=['config.h','extra.h','main.c']
            findings.insert(1,{'type':'MISSING','target':'main.o','dependency':'extra.h'})
        if case in cases[3:]:
            declared['main.o']=['config.h','extra.h','main.c','unused.h']
            findings=[{'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}]
        for row in group:
            repeat=int(row['repeat'])
            inc=json.loads((m/f'{case}-r{repeat}-incremental.json').read_text())
            full=json.loads((m/f'{case}-r{repeat}-full.json').read_text())
            for k,e in [('actual',actual),('declared',declared),('findings',findings)]:assert inc[k]==full[k]==e,(case,k)
            assert float(row['incremental_s'])==inc['elapsed_s']
            assert float(row['full_s'])==full['elapsed_s']
            reuse=case in ['unchanged','body','declaration']
            assert inc['reused']==(['main.o','helper.o'] if reuse else [])
            assert inc['refreshed']==([] if reuse else ['main.o','helper.o'])
        summary=next(x for x in csv.DictReader((m/'performance-summary.csv').open()) if x['case']==case)
        assert float(summary['inc_median_s'])==statistics.median(float(x['incremental_s']) for x in group)
        assert float(summary['full_median_s'])==statistics.median(float(x['full_s']) for x in group)
    bc=json.loads((m/'final-buildchecker/findings.json').read_text())
    assert bc['status']=='SUCCEEDED' and bc['build_exit_code']==bc['clean_exit_code']==0
    assert [(x['type'],x['target'],x['dependency']) for x in bc['findings']]==[('REDUNDANT','main.o','unused.h')]
    result[name]={'standard_rows':30,'independent_graph_assertions':True,'raw_timings_match_csv':True,'medians_verified':True,'dynamic_status':bc['status'],'trace_id':bc['trace_id'],'out':str(m.relative_to(root))}
x=extension/'extension';rows=list(csv.DictReader((x/'results.csv').open()));assert len(rows)==5
expected=json.loads((x/'expected.json').read_text())
for row in rows:
    for mode in ['incremental','full']:
        report=json.loads((x/f'macro-enabled-r{row["repeat"]}-{mode}.json').read_text())
        for k in ['actual','declared','findings']:assert report[k]==expected[k]
        assert report['elapsed_s']==float(row['incremental_s' if mode=='incremental' else 'full_s'])
result['extension']={'rows':5,'independent_expected':True,'raw_timings_match_csv':True}
result['cloud_source_sha']=(standard/'student-source-commit.txt').read_text().strip()
result['cloud_image_id']=(standard/'environment-image-id.txt').read_text().strip()
(r/'work/evidence-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
