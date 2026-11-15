from pathlib import Path
import hashlib,json,shutil,sys
sys.path.insert(0,'labs/e11e12')
from pipeline import ROOT,save,command
from lab import commit
base=ROOT/'data/integration-sample';record=ROOT/'work/a3-20261115/inputs';record.mkdir(parents=True,exist_ok=True)
standard=json.loads((base/'e11-a.json').read_text());project=ROOT/'data/a3-autonomous/repo'
project.parent.mkdir();shutil.copytree(base/'repo',project)
previous=standard['target']
(project/'helper.c').write_text('int helper(void){return 0 + 0;}\n')
revision=commit(project,'A3 autonomous: equivalent helper body with unchanged dependency signature')
request={'mode':'e11-a','repo':str(project),'base':previous,'target':revision}
save(ROOT/'data/a3-autonomous/request.json',request)
save(record/'autonomous-expected.json',{'source':'A3 new real Git commit on course fixture','base':previous,'target':revision,'expected_reused':['main.o','helper.o'],'expected_refreshed':[],'expected_added':[],'expected_resolved':[],
    'findings':[{'type':'MISSING','target':'main.o','dependency':'config.h'},{'type':'MISSING','target':'main.o','dependency':'extra.h'},{'type':'REDUNDANT','target':'main.o','dependency':'unused.h'}]})
real=ROOT/'data/real-project'
command(['git','clone','--no-hardlinks',str(ROOT),str(real)],ROOT,record/'real-project-clone.log')
real_base='5ef9d829e2f893af23f60399dcb67095800d121e';real_target='e7414083c4f1760cb234f96a9d75f2d0255e3f57'
candidate=ROOT/'data/real-candidate.Dockerfile'
candidate.write_text(command(['git','show',real_target+':projects/transfer-eta/candidate.Dockerfile'],real,record/'real-candidate-read.log')+'\n')
request={'mode':'e12','repo':str(real),'base':real_base,'target':real_target,'candidate':str(candidate),'project_path':'projects/transfer-eta','profile':True,'build_timeout':600}
save(ROOT/'data/a3-real-request.json',request)
save(record/'real-dataset.json',{'source':'https://github.com/Lilyly9/DevOps-G16','project_path':'projects/transfer-eta','base':real_base,'target':real_target,'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'profile_at_target':real_target+':projects/transfer-eta/e12-profile.json','selection_owner':'A1 PR #21','course_acceptance':'A1 records that course acceptance of the newly created group project is pending','expected_missing':[['MISSING','eta_cli.o','defaults.h']],'expected_output':'eta_seconds=13','expected_after_header_change':'eta_seconds=20'})
for p in [base/'e11-a.json',base/'e12.json',ROOT/'data/a3-real-request.json',ROOT/'data/a3-autonomous/request.json',base/'dataset.json']:
    shutil.copyfile(p,record/(p.parent.name+'-'+p.name))
for name,repo in [('sample',base/'repo'),('autonomous',project),('real',real)]:
    command(['git','bundle','create',str(record/(name+'-history.bundle')),'HEAD'],repo,record/(name+'-bundle.log'))
print('A3_INPUTS_READY')
