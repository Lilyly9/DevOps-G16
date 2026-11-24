import os,subprocess
from pathlib import Path
os.environ.update(GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_1='core.filemode',GIT_CONFIG_VALUE_1='false',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0='*')
out=Path('work/b2-teacher-20261123-02-console.log')
with out.open('w') as f:r=subprocess.run(['python3','docs/students/241880543/e13-e14/run_teacher.py','--execute','--with-strace','--out','work/b2-teacher-20261123-02'],stdout=f,stderr=subprocess.STDOUT)
out.with_suffix('.exit').write_text(str(r.returncode)+'\n')
print(out.read_text()[-2500:])
