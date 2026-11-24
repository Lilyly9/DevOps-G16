import json,hashlib,os,zipfile,shutil
from pathlib import Path
root=Path.cwd();e=root/'docs/students/241880543/e13-e14/evidence/continuation-20261123'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(path,e14=False):
 r=json.loads((path/'result.json').read_text(encoding='utf-8'));assert r['status']=='SUCCEEDED',path
 expected=['draft','full-check','incremental-check','repair','recheck'];assert [x['name'] for x in r['stages']]==expected
 count=0
 for item in r['artifacts']:
  rel=item['uri'].split('/',3)[3] if item['uri'].startswith('artifact://') else item['uri']
  p=path/rel; assert sha(p)==item['sha256'],p
  if 'bytes' in item:assert p.stat().st_size==item['bytes']
  count+=1
 for item in r['stages']:
  rel=item['artifact']['uri'].split('/',3)[3] if item['artifact']['uri'].startswith('artifact://') else item['artifact']['uri']
  p=path/rel;assert sha(p)==item['artifact']['sha256'];stage=json.loads(p.read_text())
  assert stage['job_id']==r['job_id'] and stage['trace_id']==r['trace_id']
 final=json.loads((path/'final-full/findings.json').read_text());assert final['status']=='SUCCEEDED' and not any(x['type']=='MISSING' for x in final['findings'])
 records=0;image=None
 if not e14:
  draft=json.loads((path/'draft-build/result.json').read_text());image=draft['attempts'][-1]['image_id']
  for p in path.rglob('*.json'):
   if '.git' in p.parts:continue
   obj=json.loads(p.read_text())
   if isinstance(obj,dict) and 'requested_image_id' in obj:
    assert obj['requested_image_id']==obj['actual_image_id']==image
    assert obj['container_exit_code']==0 and obj['cleanup_exit_code']==0;records+=1
 else:
  reply=json.loads((path/'repair-response.json').read_text());assert reply['validation']['accepted']
 return {'status':'SUCCEEDED','job_id':r['job_id'],'trace_id':r['trace_id'],'base':r['base_commit'],'target':r['target_commit'],'verified_artifacts':count,'stage_count':5,'remaining_missing':0,'draft_image_id':image,'same_image_command_records':records}
def archive(src,name):
 with zipfile.ZipFile(e/name,'w',zipfile.ZIP_DEFLATED) as z:
  for dp,dirs,fs in os.walk(src):
   dirs[:]=[d for d in dirs if d not in ('.git','__pycache__')]
   for f in fs:
    p=Path(dp)/f
    if p.suffix=='.pyc':continue
    z.write(p,p.relative_to(src).as_posix())
 return {'path':name,'sha256':sha(e/name),'bytes':(e/name).stat().st_size}
def deployment(folder,cases):
 containers=json.loads((folder/'containers.json').read_text());assert len(containers)==4
 assert len({c['Id'] for c in containers})==4
 images={c['Image'] for c in containers};assert len(images)==1
 requested=json.loads((folder/'runtime.json').read_text())['image_id']
 for c in containers:assert c['Config']['Image']==requested
 for role in ('buildchecker','echecker','draft','mdfixer'):
  h=json.loads((folder/(role+'-health.json')).read_text());assert h=={'status':'ok','role':role}
  assert (folder/('b2-e14-20261123-'+role+'-cleanup.exit')).read_text().strip()=='0'
  records=[]
  for line in (folder/('b2-e14-20261123-'+role+'-logs.log')).read_text().splitlines():
   try:entry=json.loads(line)
   except ValueError:continue
   if isinstance(entry,dict):records.append(entry)
  for case in cases:
   result=json.loads((folder/case/'result.json').read_text())
   found=[x for x in records if x.get('job_id')==result['job_id'] and x.get('trace_id')==result['trace_id'] and x.get('status')=='SUCCEEDED' and x.get('role')==role]
   assert len(found)==(3 if role=='buildchecker' else 1),(folder,case,role)
 return {'four_distinct_containers':True,'all_health_ok':True,'same_runtime_image':images.pop(),'job_trace_logs_verified':True,'cleanup_exit_codes':[0,0,0,0]}

r={'source_commit':'b376720', 'working_tree_sha256':{str(p):sha(p) for p in (Path('labs/e13e14/orchestrate.py'),Path('labs/e13e14/service.py'),Path('labs/e13e14/test_profile_241880543.py'))},'date':'2026-11-23','cases':{},'archives':{}}
for case in ('H1-jsmn','H3-tiny-aes'):
 r['cases'][case]=audit(root/'work/b2-teacher-20261123-02'/case/'e12')
r['cases']['C1-B']=audit(root/'work/b2-c1-20261123-03/b')
a=json.loads((root/'work/b2-c1-20261123-02/a/result.json').read_text());assert a['status']=='SUCCEEDED'
fixed=root/'work/b2-c1-20261123-02/fixed-md.json';handoff=json.loads(fixed.read_text());br=json.loads((root/'work/b2-c1-20261123-03/request.json').read_text());assert br['fixed_report_sha256']==sha(fixed);assert handoff['source_report']['job_id']==a['job_id'];assert handoff['source_report']['trace_id']==a['trace_id'];assert handoff['source_report']['sha256']==sha(root/'work/b2-c1-20261123-02/a/incremental-check.json')
r['cases']['C1-A-handoff']={'job_id':a['job_id'],'trace_id':a['trace_id'],'report_sha256':handoff['source_report']['sha256'],'fixed_report_sha256':sha(fixed),'status':'SUCCEEDED'}
r['cases']['E14-H1']=audit(root/'work/b2-e14-20261123-02/H1-jsmn',True)
for folder,name in [('b2-teacher-20261123-02','teacher-linux.zip'),('b2-e14-20261123-02','e14-four-services.zip'),('b2-runtime-20261123-04','runtime-overlay.zip'),('b2-c1-20261123-02','c1-a-and-first-b.zip'),('b2-c1-20261123-03','c1-b-recovery.zip')]:r['archives'][folder]=archive(root/'work'/folder,name)

for case in ('fixed','H3-tiny-aes'):
 r['cases']['E14-'+case]=audit(root/'work/b2-e14-20261123-03'/case,True)
r['archives']['e14-fixed-h3']=archive(root/'work/b2-e14-20261123-03','e14-fixed-h3.zip')

r['cases']['E14-transfer-eta']=audit(root/'work/b2-e14-20261123-04/transfer-eta',True)
r['archives']['e14-real-project']=archive(root/'work/b2-e14-20261123-04','e14-real-project.zip')
shutil.copyfile(root/'work/e13-241880543-remote-checks.json',e/'ci-scanner-fix.json')

fault=root/'work/b2-e14-fault-20261123-01';v=json.loads((fault/'timeout-verification.json').read_text());assert v['passed'];assert v['source_hashes_before']==v['source_hashes_after'];assert set(v['containers_before'])==set(v['containers_after']);r['cases']['E14-timeout-recovery']=audit(fault/'fixed',True);assert r['cases']['E14-timeout-recovery']['job_id']!=v['job_id'];assert r['cases']['E14-timeout-recovery']['trace_id']!=v['trace_id'];r['timeout']={'status':'TIMED_OUT','failed_job':v['job_id'],'failed_trace':v['trace_id'],'source_unchanged':True,'no_new_containers':True}
r['archives']['e14-fault-recovery']=archive(fault,'e14-fault-recovery.zip')
r['deployments']={n:deployment(root/'work'/n,c) for n,c in [('b2-e14-20261123-02',['H1-jsmn']),('b2-e14-20261123-03',['fixed','H3-tiny-aes']),('b2-e14-20261123-04',['transfer-eta']),('b2-e14-fault-20261123-01',['fixed'])]}
r['archives']['failure-attempts']={'path':'failure-attempts.zip'}
with zipfile.ZipFile(e/'failure-attempts.zip','w',zipfile.ZIP_DEFLATED) as z:
 for folder in ('b2-teacher-20261123-01','b2-c1-20261123-01','b2-e14-20261123-01','b2-runtime-20261123','b2-runtime-20261123-02','b2-runtime-20261123-03'):
  for dp,dirs,fs in os.walk(root/'work'/folder):
   dirs[:]=[d for d in dirs if d not in ('.git','__pycache__')]
   for f in fs:
    p=Path(dp)/f
    z.write(p,p.relative_to(root/'work').as_posix())
r['archives']['failure-attempts'].update(sha256=sha(e/'failure-attempts.zip'),bytes=(e/'failure-attempts.zip').stat().st_size)
for item in r['archives'].values():
 with zipfile.ZipFile(e/item['path']) as z:
  assert z.testzip() is None
  for name in z.namelist():
   if name.endswith('/result.json') or name=='result.json':
    report=json.loads(z.read(name));parent=name.rsplit('/',1)[0]+'/' if '/' in name else ''
    for ref in report.get('artifacts',[]):
     uri=ref['uri'];rel=uri.split('/',3)[3] if uri.startswith('artifact://') else uri
     assert hashlib.sha256(z.read(parent+rel)).hexdigest()==ref['sha256'],(item['path'],rel)
r['archive_crc_and_artifact_hashes_verified']=True
(e/'verified-runs.json').write_text(json.dumps(r,indent=2)+'\n')
print('Audited cases:', ', '.join(r['cases']))
