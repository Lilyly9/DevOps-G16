import json,subprocess,os
from pathlib import Path
root=Path.cwd();e=root/'docs/students/241880543/e13-e14/evidence/continuation-20261123'
os.environ.update(GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0='*',GIT_CONFIG_KEY_1='core.filemode',GIT_CONFIG_VALUE_1='false',PYTHONPATH='labs/e11e12:labs/e8e10:labs/e11e12/vendor')
cmds=[('linux-e11e12',['python3','-m','unittest','discover','-s','labs/e11e12','-p','test_*.py','-v']),('linux-e14',['python3','-m','unittest','discover','-s','labs/e13e14','-p','test_*.py','-v']),('scanner-tests-linux',['python3','-m','unittest','discover','-s','e5/A-buildchecker/tests/tooling','-v'])]
for name,cmd in cmds:
 with (e/(name+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 (e/(name+'.exit')).write_text(str(r.returncode)+'\n');print(name,r.returncode)
