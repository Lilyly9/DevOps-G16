"""Launch four isolated E14 processes and retain health, runtime and E2E evidence."""
import os,sys,json,subprocess,time,urllib.request
from pathlib import Path
root=Path.cwd();out=root/'work/b2-e14-20261123-04';out.mkdir(exist_ok=False)
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
 data=root/'data/b2-e14-real-20261123-02';data.mkdir(exist_ok=False)
 call(['docker','run','--rm','--network','none','-v',str(root)+':/course','-w','/course',image,'git','clone','--no-hardlinks','--no-checkout','/course','/course/data/b2-e14-real-20261123-02/repo'],'real-input-clone')
 candidate=data/'candidate-https.Dockerfile';candidate.write_bytes((root/'work/b2-c1-20261123-03/candidate-https.Dockerfile').read_bytes())
 for case in ('transfer-eta',):
  if case=='transfer-eta':
   request=json.loads((root/'work/b2-c1-20261123-03/request.json').read_text());request['repo']='/course/data/b2-e14-real-20261123-02/repo';request['candidate']='/course/data/b2-e14-real-20261123-02/candidate-https.Dockerfile'
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
