import os,json,subprocess,hashlib
from pathlib import Path
root=Path.cwd();out=root/'work/b2-c1-20261123-03';out.mkdir(exist_ok=False)
os.environ.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0='*')
original=root/'projects/transfer-eta/candidate.Dockerfile'
text=original.read_text();text=text.replace('RUN apt-get',"RUN sed -i 's|http:|https:|g' /etc/apt/sources.list.d/debian.sources\nRUN apt-get").replace('-o Acquire::ForceIPv4=true ','')
candidate=out/'candidate-https.Dockerfile';candidate.write_text(text)
request=json.loads((root/'work/b2-c1-20261123-02/b-request.json').read_text());request['candidate']='/course/'+candidate.relative_to(root).as_posix();request['build_timeout']=300
(out/'request.json').write_text(json.dumps(request,indent=2)+'\n');(out/'candidate-provenance.json').write_text(json.dumps({'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'selected_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'change':'HTTPS package source and default IP selection; original candidate and target source unchanged','source_a_result':'work/b2-c1-20261123-02/a/result.json'},indent=2)+'\n')
with (out/'console.log').open('w') as f:r=subprocess.run(['python3','run_e11e12.py','run','--request',str((out/'request.json').relative_to(root)),'--out',str((out/'b').relative_to(root))],stdout=f,stderr=subprocess.STDOUT,timeout=900)
(out/'console.exit').write_text(str(r.returncode)+'\n');print((out/'console.log').read_text()[-1500:])
