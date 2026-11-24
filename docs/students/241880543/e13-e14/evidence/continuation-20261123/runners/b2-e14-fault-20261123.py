"""Launch four isolated E14 processes and retain health, runtime and E2E evidence."""
import os,sys,json,subprocess,time,urllib.request
from pathlib import Path
root=Path.cwd();out=root/'work/b2-e14-fault-20261123-01';out.mkdir(exist_ok=False)
os.environ.update(GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0='*',GIT_CONFIG_KEY_1='core.filemode',GIT_CONFIG_VALUE_1='false')
roles={'buildchecker':18081,'echecker':18082,'draft':18083,'mdfixer':18084};names=[]
def save(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def call(cmd,label,check=True):
 with (out/(label+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=900)
 (out/(label+'.exit')).write_text(str(r.returncode)+'\n')
 if check and r.returncode:raise RuntimeError(label+' failed')
 return r.returncode
try:
 image=subprocess.check_output(['docker','image','inspect','course-e11e12:241880543','--format','{{.Id}}'],text=True).strip()
 save(out/'runtime.json',{'image_id':image,'source':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'deployment':'four docker run processes using the course Compose settings; no group acceptance claimed'})
 for role,port in roles.items():
  name='b2-e14-20261123-'+role
  cmd=['docker','run','-d','--name',name,'--user','0:0','--cpus','1','--memory','768m','--pids-limit','128','--security-opt','no-new-privileges:true','-e','E14_ROLE='+role,'-e','PYTHONDONTWRITEBYTECODE=1','-v',str(root)+':/course','-w','/course','-p',f'127.0.0.1:{port}:8080']
  if role=='buildchecker':cmd+=['--cap-add','SYS_PTRACE']
  if role=='draft':cmd+=['-v','/var/run/docker.sock:/var/run/docker.sock']
  cmd += [image,'python3','labs/e13e14/service.py'];save(out/(role+'-command.json'),cmd);call(cmd,role+'-start');names.append(name)
 for role,port in roles.items():
  for attempt in range(30):
   try:
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=2) as r:health=json.load(r)
    save(out/(role+'-health.json'),health);break
   except OSError:
    time.sleep(1)
  else:raise RuntimeError(role+' unhealthy')
 (out/'containers.json').write_text(subprocess.check_output(['docker','inspect',*names],text=True))
 import urllib.error,uuid,hashlib
 source=root/'work/b2-teacher-20261123-02/H1-jsmn/e12/base-project'
 def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()}
 before=hashes();container_ids=subprocess.check_output(['docker','ps','-aq'],text=True).splitlines()
 failed_job='job-'+uuid.uuid4().hex;failed_trace='trace-'+uuid.uuid4().hex
 request={'project':'/course/'+source.relative_to(root).as_posix(),'out':'/course/'+(out/'timeout').relative_to(root).as_posix(),'candidate':'/course/data/b2-teacher-20261123-02/e13-upstream-student/H1-jsmn/candidate-b2-strace.Dockerfile','job_id':failed_job,'trace_id':failed_trace,'build_timeout':0.001,'expected_output':'1'}
 save(out/'timeout-request.json',request)
 message=urllib.request.Request('http://127.0.0.1:18083/v1/run',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'})
 try:
  response=urllib.request.urlopen(message,timeout=30)
 except urllib.error.HTTPError as exc:response=exc
 with response:reply={'http':response.status,'body':json.load(response)}
 save(out/'timeout-response.json',reply)
 assert reply['http']==422 and reply['body']['error_code']=='TIMEOUT',reply
 timed=json.loads((out/'timeout/result.json').read_text());assert timed['status']=='TIMED_OUT'
 remaining=subprocess.check_output(['docker','ps','-aq'],text=True).splitlines()
 assert set(remaining)==set(container_ids),'Timeout left a container'
 assert before==hashes(),'Timeout changed source'
 save(out/'timeout-verification.json',{'passed':True,'job_id':failed_job,'trace_id':failed_trace,'source_hashes_before':before,'source_hashes_after':hashes(),'containers_before':container_ids,'containers_after':remaining})
 for case in ('fixed',):
  if case=='transfer-eta':
   request=json.loads((root/'work/b2-c1-20261123-03/request.json').read_text());request['repo']='/course/data/b2-e14-real-20261123/repo';request['candidate']='/course/data/b2-e14-real-20261123/candidate-https.Dockerfile'
  elif case=='fixed':
   request=json.loads((root/'data/integration-sample/e12.json').read_text());request['repo']='/course/data/integration-sample/repo';request['candidate']='/course/data/integration-sample/candidate.Dockerfile'
  else:request=json.loads((root/'work/b2-teacher-20261123-02'/case/'request-e12.json').read_text())
  request['build_timeout']=300
  save(out/(case+'-request.json'),request)
  call(['docker','run','--rm','--network','host','--user','0:0','-v',str(root)+':/course','-w','/course',image,'python3','labs/e13e14/orchestrate.py','--request','/course/'+(out/(case+'-request.json')).relative_to(root).as_posix(),'--out','/course/'+(out/case).relative_to(root).as_posix()],case+'-console',check=False)
finally:
 for name in names:
  call(['docker','logs',name],name+'-logs',check=False)
  call(['docker','rm','-f',name],name+'-cleanup',check=False)
print('E14 evidence',out)
