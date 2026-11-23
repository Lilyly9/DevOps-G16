import os,subprocess,json
from pathlib import Path
root=Path.cwd(); out=root/'work/b2-runtime-20261123-04';out.mkdir(exist_ok=False)
def run(cmd,name):
 with (out/(name+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 (out/(name+'.exit')).write_text(str(r.returncode)+'\n');return r.returncode
image=subprocess.check_output(['docker','image','inspect','course-e13e14:241880543','--format','{{.Id}}'],text=True).strip()
(out/'docker-wrapper').write_text('#!/bin/sh\nif [ "$1" = build ]; then\n shift\n exec /usr/local/bin/docker-real build --network host "$@"\nfi\nexec /usr/local/bin/docker-real "$@"\n')
(out/'Dockerfile').write_text(f'FROM course-e13e14:241880543\nUSER root\nRUN mv /usr/local/bin/docker /usr/local/bin/docker-real\nCOPY docker-wrapper /usr/local/bin/docker\nRUN chmod 755 /usr/local/bin/docker && git config --system safe.directory "*" && git config --system core.filemode false\nENV GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=*\n')
code=run(['docker','build','--network','host','-t','course-e11e12:241880543',str(out)],'build')
if code:raise SystemExit(code)
(out/'image.json').write_text(subprocess.check_output(['docker','image','inspect','course-e11e12:241880543'],text=True))
print('Runtime ready',out)
