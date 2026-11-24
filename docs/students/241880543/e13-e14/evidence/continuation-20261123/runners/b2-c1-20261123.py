import os,sys,json,hashlib,subprocess
from pathlib import Path
root=Path.cwd();out=root/'work/b2-c1-20261123-02';out.mkdir(exist_ok=False)
os.environ.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0='*')
def run(cmd,name):
 with (out/(name+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=900)
 (out/(name+'.exit')).write_text(str(r.returncode)+'\n')
 if r.returncode:raise RuntimeError(name+' failed')
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
a=json.loads((root/'docs/students/241880485/e11-e12/evidence/transfer-eta/request.json').read_text());a.update(mode='e11-a',repo='/course',candidate='/course/projects/transfer-eta/candidate.Dockerfile',build_timeout=240)
save(out/'a-request.json',a)
run(['python3','run_e11e12.py','run','--request',str((out/'a-request.json').relative_to(root)),'--out',str((out/'a').relative_to(root))],'a-console')
run(['python3','labs/e13e14/handoff_a_to_b.py','--a-result',str(out/'a/result.json'),'--target-sha',a['target'],'--out',str(out/'fixed-md.json')],'handoff')
b=dict(a,mode='e12',fixed_report='/course/'+(out/'fixed-md.json').relative_to(root).as_posix(),fixed_report_sha256=hashlib.sha256((out/'fixed-md.json').read_bytes()).hexdigest())
save(out/'b-request.json',b)
run(['python3','run_e11e12.py','run','--request',str((out/'b-request.json').relative_to(root)),'--out',str((out/'b').relative_to(root))],'b-console')
print('C1 success',out)
