"""Private offline audit. Reads originals; writes only this audit and recovered bare Git stores."""
from pathlib import Path, PurePosixPath
from collections import Counter
from statistics import median
import csv, hashlib, json, re, subprocess, sys, tempfile, types

base=Path(__file__).resolve().parent
originals=base/'remaining-originals'
repo=base.parents[1]/'第2次上机实验/Project/DevOps-G16'
report={'passed':False,'scope':'Offline independent audit of actual A1 E9-A, E10-A matrix and deletion extension; no experiment or network rerun','checks':[],'errors':[],'limitations':[]}

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,condition,details=None):
 row={'name':name,'passed':bool(condition)}
 if details is not None:row['details']=details
 report['checks'].append(row)
 if not condition:report['errors'].append(name)
 return bool(condition)
def cmd(argv,cwd=repo):
 p=subprocess.run(argv,cwd=cwd,capture_output=True)
 if p.returncode:raise ValueError('Command failed: '+repr(argv)+'; '+p.stderr.decode('utf-8','replace'))
 return p.stdout
def git_blob(commit,path,cwd=repo):return cmd(['git','show',commit+':'+path],cwd)
def norm_findings(rows):return sorted((f['type'],f['target'],f['dependency']) for f in rows)
def projection(rows):return {t:sorted({e['dependency'] for e in rows if e['target']==t}) for t in ['main.o','helper.o']}
def capture_originals():return {p.relative_to(originals).as_posix():sha(p) for p in originals.rglob('*') if p.is_file()}
initial_manifest=capture_originals()

def recover(folder,name,count,subjects):
 bundle=folder/'project-history.bundle'
 verify=cmd(['git','bundle','verify',str(bundle)]).decode('utf-8','replace')
 dest=recovery/name
 cmd(['git','clone','--bare',str(bundle),str(dest)],base)
 fsck=cmd(['git','fsck','--full','--strict','--no-reflogs'],dest).decode('utf-8','replace')
 commits=cmd(['git','rev-list','--reverse','HEAD'],dest).decode().splitlines()
 real_history=cmd(['git','log','--reverse','--format=%H %s'],dest).decode('utf-8')
 recorded=(folder/'project-history.txt').read_text(encoding='utf-8')
 actual_subjects=[cmd(['git','show','-s','--format=%s',c],dest).decode().strip() for c in commits]
 check(name+':bundle_full_history_recovers_and_fsck_passes',len(commits)==count and real_history==recorded and actual_subjects==subjects,{'commits':commits,'subjects':actual_subjects,'bundle_sha256':sha(bundle),'fsck_stdout':fsck})
 versions={}
 for commit in commits:
  names=cmd(['git','ls-tree','-r','--name-only',commit],dest).decode().splitlines()
  versions[commit]={n:git_blob(commit,n,dest).decode('utf-8') for n in names}
 final=versions[commits[-1]]
 check(name+':final_project_input_equals_recovered_HEAD',all((folder/'project'/n).read_bytes()==text.encode() for n,text in final.items()))
 return commits,versions

def derived_input(files):
 # Independent simple traversal of literal local include directives in these exact fixtures.
 actual={}
 for target,source in [('main.o','main.c'),('helper.o','helper.c')]:
  seen=set()
  def visit(name):
   if name in seen:return
   if name not in files:raise ValueError('Referenced deleted/missing input '+name)
   seen.add(name)
   for child in re.findall(r'^\s*#\s*include\s+"([^"]+)"',files[name],re.M):visit(child)
  visit(source);actual[target]=sorted(seen)
 make=files['Makefile']
 declared={t:sorted(set(re.search(r'^'+re.escape(t)+r': (.+)$',make,re.M)[1].split())) for t in ['main.o','helper.o']}
 flags=re.search(r'^CFLAGS = (.*)$',make,re.M)[1]
 findings=sorted((kind,t,d) for t in actual for kind,edges in [('MISSING',set(actual[t])-set(declared[t])),('REDUNDANT',set(declared[t])-set(actual[t]))] for d in edges)
 key={'directives':{n:[line for line in files[n].splitlines() if line.lstrip().startswith('#')] for n in sorted(files) if Path(n).suffix in ['.c','.h']},'recipes':[line for line in make.splitlines() if line.startswith('\t')],'flags':flags}
 return actual,declared,findings,key

def audit_report(label,r,files,previous=None):
 actual,declared,findings,key=derived_input(files)
 fields={k:r[k]==v for k,v in [('actual',actual),('declared',declared)]}
 fields['findings']=norm_findings(r['findings'])==findings
 fields['key']=all(r['key'][k]==v for k,v in key.items()) and r['key']['compiler']=='gcc (Debian 14.2.0-19) 14.2.0'
 fields['elapsed_positive']=r['elapsed_s']>0
 now=set(findings);old=set(norm_findings(previous['findings'])) if previous else set()
 fields['added']=r['added']==[list(x) for x in sorted(now-old)]
 fields['resolved']=r['resolved']==[list(x) for x in sorted(old-now)]
 reuse=bool(previous and previous['key']==r['key'])
 fields['reused']=r['reused']==(['main.o','helper.o'] if reuse else [])
 fields['refreshed']=r['refreshed']==([] if reuse else ['main.o','helper.o'])
 check(label+':input_independent_graph_findings_key_delta_and_reuse',all(fields.values()),fields)


def audit_measurements(folder,case,previous,versions,expected_commit,rows):
 check(case+':exactly_five_rows_and_repeat_numbers',len(rows)==5 and [int(x['repeat']) for x in rows]==list(range(1,6)))
 all_fields=[]
 for repeat,row in enumerate(rows,1):
  inc=load(folder/f'{case}-r{repeat}-incremental.json')
  full=load(folder/f'{case}-r{repeat}-full.json')
  # The deletion file prefix differs from the human-facing CSV case name.
  all_fields.append((inc,full))
  check(case+f'-r{repeat}:commit_complete_collection_equality_and_CSV_exact_values',inc['commit']==full['commit']==expected_commit and all(inc[k]==full[k] for k in ['actual','declared','findings']) and row['equal']=='True' and float(row['incremental_s'])==inc['elapsed_s'] and float(row['full_s'])==full['elapsed_s'] and int(row['reused'])==len(inc['reused']) and int(row['refreshed'])==len(inc['refreshed']))
  audit_report(case+f'-r{repeat}-incremental',inc,versions[expected_commit],previous)
  audit_report(case+f'-r{repeat}-full',full,versions[expected_commit])
 return all_fields

def audit_performance(folder,rows):
 stored=list(csv.DictReader((folder/'performance-summary.csv').open(newline='',encoding='utf-8')))
 summaries=[]
 for summary in stored:
  case=summary['case'];group=[r for r in rows if r['case']==case]
  inc=[float(r['incremental_s']) for r in group];full=[float(r['full_s']) for r in group]
  mi,mf=median(inc),median(full)
  expected={'n':len(group),'inc_median_s':mi,'full_median_s':mf,'inc_min_s':min(inc),'inc_max_s':max(inc),'full_min_s':min(full),'full_max_s':max(full),'full_over_inc':mf/mi}
  checks={k:float(summary[k])==v for k,v in expected.items() if k in summary}
  check(folder.name+':performance_summary_recomputed_'+case,all(checks.values()) and len(group)==5,{'recomputed':expected,'fields_equal':checks})
  summaries.append({'case':case,**expected})
 check(folder.name+':performance_cases_cover_all_raw_rows',Counter(x['case'] for x in stored)==Counter({x['case']:1 for x in rows}))
 return summaries

try:
 metadata=load(originals/'A1-E9E10-provenance.8s_ev_pt/metadata.json')
 source=metadata['source_commit']
 report.update(student_id=metadata['student_id'],source_commit=source,image_id=metadata['image_id'])
 source_hashes={n:hashlib.sha256(git_blob(source,n)).hexdigest()==h for n,h in metadata['source_sha256'].items()}
 check('recorded_source_hashes_match_exact_source_commit',all(source_hashes.values()),source_hashes)
 check('source_student_identity_and_clean_status',metadata['student_id']=='241880485' and metadata['name']=='焦龙' and metadata['group']=='A16' and metadata['paired_group']=='B16' and metadata['source_branch']=='student/241880485/e8-e10' and metadata['source_status']=='')
 check('image_reused_with_unchanged_environment',not metadata['environment_rebuilt'] and metadata['image_id']=='sha256:7461c2bbd458c9a1955c9cfd502d435f8213a8e15b59f952eca833edcfe4e691' and not cmd(['git','diff','9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a',source,'--','labs/e8e10/environment']))
 prov=originals/'A1-E9E10-provenance.8s_ev_pt'
 check('runtime_dependency_lock_matches_Git',(prov/'image-lock.stdout.log').read_bytes()==git_blob(source,'labs/e8e10/environment/requirements-dev.lock'))
 check('provenance_commands_exited_zero',all(x['exit_code']==0 for x in metadata['commands']))
 e9=originals/'e9-A-manual.eqLOHp';e10=originals/'e10-A-manual.eVOOik';extra=originals/'e10-A-manual.n9BhPY';matrix=e10/'matrix'
 for folder,expected_steps in [(e9,9),(e10,9),(extra,1)]:
  image=load(folder/'image-inspect.json')[0]
  check(folder.name+':identity_and_image',image['Id']==metadata['image_id'] and image['Architecture']=='amd64' and (folder/'environment-image-id.txt').read_text().strip()==metadata['image_id'] and (folder/'student-source-commit.txt').read_text().strip()==source and (folder/'student-source-status.txt').read_text()=='')
  logs=list((folder/'steps').glob('*.log'))
  values=[{'file':p.name,'codes':re.findall(r'^STEP_EXIT_CODE=(\d+)$',p.read_text(encoding='utf-8'),re.M),'traceback':'Traceback (most recent call last)' in p.read_text(encoding='utf-8')} for p in logs]
  check(folder.name+':all_steps_zero',len(logs)==expected_steps and all(x['codes']==['0'] and not x['traceback'] for x in values),values)
  check(folder.name+':executed_route_and_UTC_bounds_exist',(folder/'executed-route.sh').is_file() and (folder/'started-utc.txt').read_text().strip()<=(folder/'finished-utc.txt').read_text().strip())
  input_hashes=load(folder/'input-sha256.json')
  project=folder/'project' if folder!=e10 else matrix/'project'
  check(folder.name+':final_input_hashes_match',all((project/n).is_file() and sha(project/n)==h for n,h in input_hashes.items()),input_hashes)
 recovery=Path(tempfile.mkdtemp(prefix='remaining-audit-recovery-',dir=base))
 assert recovery.resolve().is_relative_to(base.resolve())
 report['private_recovered_bundles']=str(recovery)
 c9,v9=recover(e9,'e9',4,['C0 baseline','C1 body change','C2 include change','C3 repair declarations'])
 r9={n:load(e9/(n+'.json')) for n in ['baseline','C1','C2','C3']}
 previous=None
 for label,commit in zip(['baseline','C1','C2','C3'],c9):
  r=r9[label]
  check('E9-'+label+':report_commit_and_saved_input_correspond',r['commit']==commit and (e9/(label+'-commit-input.txt')).read_text(encoding='utf-8')==v9[commit]['Makefile']+'\n'+v9[commit]['main.c'])
  audit_report('E9-'+label,r,v9[commit],previous)
  previous=r
 changes9=[[n for n in sorted(set(v9[a])|set(v9[b])) if v9[a].get(n)!=v9[b].get(n)] for a,b in zip(c9,c9[1:])]
 check('E9-exact_C1_C2_C3_edits',changes9==[['main.c'],['main.c'],['Makefile']] and v9[c9[1]]['main.c']==v9[c9[0]]['main.c'].replace('VALUE+helper()','VALUE+helper()+0') and v9[c9[2]]['main.c']=='#include "extra.h"\n'+v9[c9[1]]['main.c'] and v9[c9[3]]['Makefile']==v9[c9[2]]['Makefile'].replace('main.c unused.h','main.c unused.h config.h extra.h'),changes9)
 expected_builds={'C0':['gcc -O0 -c main.c -o main.o','gcc -O0 -c helper.c -o helper.o','gcc main.o helper.o -o app'],'C1':['gcc -O0 -c main.c -o main.o','gcc main.o helper.o -o app'],'C2':['gcc -O0 -c main.c -o main.o','gcc main.o helper.o -o app'],'C3':["make: 'app' is up to date."]}
 for label,lines in expected_builds.items():check('E9-'+label+':actual_make_log_matches_expected_recipes',(e9/(label+'-build.log')).read_text(encoding='utf-8').splitlines()==lines)
 check('E9-program_output_one',(e9/'program-output.txt').read_bytes()==b'1\n')
 report['e9_commits']=dict(zip(['C0','C1','C2','C3'],c9))

 cm,vm=recover(matrix,'e10-matrix',6,['C0 baseline','body','include','declaration','flags','header'])
 cases=['unchanged','body','include','declaration','flags','header']
 rows=list(csv.DictReader((matrix/'results.csv').open(newline='',encoding='utf-8')))
 check('E10-matrix_exact_30_rows_six_cases_each_five',len(rows)==30 and Counter(r['case'] for r in rows)==Counter({x:5 for x in cases}) and all(r['equal']=='True' for r in rows))
 check('E10-60_distinct_original_repeat_reports',len(list(matrix.glob('*-r*-incremental.json')))==30 and len(list(matrix.glob('*-r*-full.json')))==30)
 previous=load(matrix/'baseline.json');audit_report('E10-baseline',previous,vm[cm[0]])
 check('E10-baseline_commit_matches_C0',previous['commit']==cm[0])
 for case,commit in zip(cases,cm):
  pairs=audit_measurements(matrix,case,previous,vm,commit,[r for r in rows if r['case']==case])
  last=load(matrix/(case+'.json'))
  check(case+':terminal_report_is_fifth_incremental',last==pairs[-1][0])
  previous=last
 expected_deltas=[['helper.c'],['main.c'],['Makefile'],['Makefile'],['config.h']]
 deltas=[[n for n in sorted(set(vm[a])|set(vm[b])) if vm[a].get(n)!=vm[b].get(n)] for a,b in zip(cm,cm[1:])]
 check('E10-matrix_exact_cumulative_source_changes',deltas==expected_deltas and vm[cm[1]]['helper.c']=='int helper(void){return 0+0;}\n' and vm[cm[2]]['main.c']=='#include "extra.h"\n'+vm[cm[1]]['main.c'] and vm[cm[3]]['Makefile']==vm[cm[2]]['Makefile'].replace('main.c unused.h','main.c unused.h config.h extra.h') and vm[cm[4]]['Makefile']==vm[cm[3]]['Makefile'].replace('-O0','-O1') and vm[cm[5]]['config.h']=='#include "extra.h"\n#define VALUE 1\n',deltas)
 check('E10-matrix_gate_passed_with_30_rows',load(matrix/'gate.json')=={'track':'A','passed':True,'rows':30})
 report['e10_performance']=audit_performance(matrix,rows)
 report['e10_commits']=dict(zip(cases,cm))

 ce,ve=recover(extra,'e10-deletion',3,['C0 baseline','A1 setup indirect header before deletion','A1 remove indirect include and delete extra.h'])
 expected={'provenance':'A1_EXPECTED_FROM_PLANNED_HEADER_REMOVAL','scenario':'remove config.h include of extra.h and delete extra.h','actual':{'main.o':['config.h','main.c'],'helper.o':['helper.c']},'declared':{'main.o':['main.c','unused.h'],'helper.o':['helper.c']},'findings':[['MISSING','main.o','config.h'],['REDUNDANT','main.o','unused.h']],'added':[],'resolved':[['MISSING','main.o','extra.h']],'refreshed':['main.o','helper.o'],'reused':[]}
 check('deletion-full_independent_expectation_is_explicit',load(extra/'independent-expected.json')==expected)
 base_extra=load(extra/'baseline.json');audit_report('deletion-baseline',base_extra,ve[ce[1]])
 check('deletion-baseline_is_second_internal_commit',base_extra['commit']==ce[1])
 check('deletion-exact_three_version_input_changes',ve[ce[1]]==dict(ve[ce[0]],**{'config.h':'#include "extra.h"\n#define VALUE 1\n'}) and ve[ce[2]]=={k:('#define VALUE 1\n' if k=='config.h' else v) for k,v in ve[ce[1]].items() if k!='extra.h'})
 extension_rows=list(csv.DictReader((extra/'results.csv').open(newline='',encoding='utf-8')))
 check('deletion-five_rows_and_ten_raw_reports',len(extension_rows)==5 and [int(r['repeat']) for r in extension_rows]==list(range(1,6)) and {r['case'] for r in extension_rows}=={'remove-indirect-header'} and len(list(extra.glob('deletion-r*-*.json')))==10)
 pairs=audit_measurements(extra,'deletion',base_extra,ve,ce[2],extension_rows)
 for i,(inc,full) in enumerate(pairs,1):
  comparisons={field:inc[field]==value for field,value in expected.items() if field in inc and field!='findings'}
  comparisons['findings']=norm_findings(inc['findings'])==[tuple(x) for x in expected['findings']]
  check(f'deletion-r{i}:matches_all_independent_expected_fields',all(comparisons.values()),comparisons)
 report['deletion_performance']=audit_performance(extra,extension_rows)
 gate=load(extra/'gate.json')
 check('deletion-gate_matches_real_versions_and_rows',gate=={'passed':True,'rows':5,'independent_expected':True,'dynamic_actual_equal':True,'baseline_commit':ce[1],'changed_commit':ce[2]})
 check('deletion-program_output_one',(extra/'program-output.txt').read_bytes()==b'1\n')
 report['deletion_commits']=dict(zip(['C0','indirect_before','deleted_after'],ce))

 parser_source=git_blob(source,'labs/e8e10/environment/services/buildchecker/buildchecker/fullcheck.py')
 module=types.ModuleType('_remaining_original_fullcheck_parser');module.__file__='<Git:'+source+':fullcheck.py>';sys.modules[module.__name__]=module
 exec(compile(parser_source,module.__file__,'exec'),module.__dict__)
 dynamic=[]
 for folder,known_report in [(matrix/'final-buildchecker',load(matrix/'header.json')),(extra/'buildchecker-before',base_extra),(extra/'buildchecker-after',pairs[-1][0])]:
  name=folder.relative_to(originals).as_posix();stored=load(folder/'findings.json');trace_files=sorted((folder/'trace').glob('t.*'));processes=load(folder/'processes.json')
  check(name+':successful_clean_and_build',stored['status']=='SUCCEEDED' and stored['clean_exit_code']==stored['build_exit_code']==0)
  hashes=stored['input_sha256'];check(name+':dynamic_input_snapshot_matches_hashes',all((folder/'project'/n).is_file() and sha(folder/'project'/n)==h for n,h in hashes.items()))
  pids={int(p.name.rsplit('.',1)[1]) for p in trace_files};stored_pids={x['pid'] for x in processes}
  trace_ok=len(trace_files)==10 and pids==stored_pids and all(x['parent'] is None or x['parent'] in stored_pids for x in processes) and all(p.read_text(encoding='utf-8').splitlines()[-1]=='+++ exited with 0 +++' for p in trace_files)
  check(name+':complete_process_tree_and_zero_exits',trace_ok,{'trace_files':len(trace_files),'pids':sorted(pids)})
  prefix=stored['trace_command'][stored['trace_command'].index('-o')+1];linux_root=str(PurePosixPath(prefix).parent.parent/'project')
  parsed=module.analyze(folder/'trace',folder/'make-db.txt',linux_root)
  fields={'actual_graph':parsed['actual_graph']==load(folder/'actual-graph.json'),'declared_graph':parsed['declared_graph']==load(folder/'declared-graph.json'),'processes':parsed['processes']==processes,'findings':parsed['findings']==stored['findings']}
  check(name+':raw_trace_and_make_database_reparse_exactly_matches_all_reports',all(fields.values()),fields)
  projected_findings=[f for f in stored['findings'] if f['target'] in ['main.o','helper.o']]
  check(name+':dynamic_object_projection_matches_scan_and_independent_input',projection(parsed['actual_graph'])==known_report['actual'] and norm_findings(projected_findings)==norm_findings(known_report['findings']))
  dynamic.append({'path':name,'linux_project_root':linux_root,'trace_count':len(trace_files),'actual':projection(parsed['actual_graph']),'findings':norm_findings(projected_findings),'trace_manifest':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in trace_files}})
 report['dynamic_offline_reparse']=dynamic
 unit=originals/'A1-E9E10-tests.7gI6Xf';test_text=(unit/'stdout.log').read_text(encoding='utf-8')+(unit/'stderr.log').read_text(encoding='utf-8')
 test_names=re.findall(r'^(test_[^\n]+?) \.\.\. ok$',test_text,re.M)
 check('new_cloud_unit_test_log_has_original_seven_and_own_one',len(test_names)==8 and 'Ran 8 tests' in test_text and '\nOK\n' in test_text and (unit/'exit-code.txt').read_text().strip()=='0' and 'test_header_include_invalidates_previous_dependency_graph' in test_text and (unit/'student-source-commit.txt').read_text().strip()==source,test_names)
 report['limitations']=['Offline audit verifies preserved inputs, Git object histories, syscall/make evidence and arithmetic; it does not rerun Linux GCC, Make or strace on Windows.','Stored measurement intervals cannot be independently timed again without a new experiment; all 35 CSV values are checked exactly against the 70 original report timers and summaries are recomputed.','3.5 GiB visible memory is below the 4 GiB material recommendation.','Raw trace reparse uses the exact recorded source version of the course parser; independent literal-include/source traversal and expected sets provide a separate object-graph check.']
except Exception as ex:
 report['errors'].append(type(ex).__name__+': '+str(ex))
finally:
 final_manifest=capture_originals()
 check('audit_did_not_change_any_downloaded_original',initial_manifest==final_manifest,{'file_count':len(initial_manifest),'manifest_sha256':hashlib.sha256(json.dumps(initial_manifest,sort_keys=True).encode()).hexdigest()})
 report['passed']=not report['errors'] and all(x['passed'] for x in report['checks'])
 report['check_count']=len(report['checks'])
 (base/'remaining-independent-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'errors':report['errors'],'limitations':report['limitations']},ensure_ascii=False,indent=2))
