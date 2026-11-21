from pathlib import Path
import json,shutil,sys,hashlib
sys.path.insert(0,'labs/e11e12')
from pipeline import ROOT,save
from lab import commit,run
base=ROOT/'data/integration-sample';root=ROOT/'data/a3-fixed';root.mkdir()
project=root/'repo';shutil.copytree(base/'repo',project)
f=project/'Dockerfile.broken';f.write_text(f.read_text().replace('FROM python:3.13-slim','FROM m.daocloud.io/docker.io/library/python:3.13-slim'))
target=commit(project,'A3 fixed fixture: same digest mirror for cloud Docker transport')
candidate=(base/'candidate.Dockerfile').read_text().replace('FROM python:3.13-slim','FROM m.daocloud.io/docker.io/library/python:3.13-slim')
candidate=candidate.replace('RUN apt-get update', "RUN sed -i -e 's|deb.debian.org/debian-security|mirrors.tuna.tsinghua.edu.cn/debian-security|g' -e 's|deb.debian.org/debian|mirrors.tuna.tsinghua.edu.cn/debian|g' /etc/apt/sources.list.d/debian.sources\nRUN apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=3 update")
(root/'candidate.Dockerfile').write_text(candidate)
request=json.loads((base/'e12.json').read_text());request.update(repo=str(project),target=target,candidate=str(root/'candidate.Dockerfile'));request.pop('fixed_report',None)
save(root/'request.json',request)
save(ROOT/'work/a3-20261115/inputs/fixed-network-adaptation.json',{'source':'course-generated fixed input, explicit network-only Dockerfile commit','original_request':json.loads((base/'e12.json').read_text()),'request':request,'digest_preserved':'70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f','candidate_sha256':hashlib.sha256(candidate.encode()).hexdigest(),'reason':'Original Docker Hub registry timed out before reproducing MISSING_MAKE; failure preserved at e12-cli-fixed'})
run(['git','bundle','create',str(ROOT/'work/a3-20261115/inputs/fixed-network-history.bundle'),'HEAD'],project)
print('FIXED_NETWORK_ADAPTATION_READY',target)
