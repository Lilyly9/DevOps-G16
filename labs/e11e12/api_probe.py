"""A3 API 入口预跑，保存请求、轮询、阶段标识与下载核验原件。"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pipeline import Failure, save
from report_exchange import download_report


def probe(base_url, request, key, out, timeout=900):
    out.mkdir(parents=True, exist_ok=False)
    def http(path, body=None):
        headers={'Content-Type':'application/json'} if body is not None else {}
        data=None if body is None else json.dumps(body).encode()
        message=Request(base_url.rstrip('/')+path,data=data,headers=headers)
        try:
            response=urlopen(message,timeout=30)
        except HTTPError as error:
            response=error
        with response:
            raw=response.read()
            return response.status, json.loads(raw)
    body={'idempotency_key':key,'input':request}
    save(out/'submit-request.json',body)
    code,first=http('/v1/jobs',body)
    save(out/'submit-response.json',{'http_status':code,'body':first})
    if code!=202:
        raise Failure('SUBMIT_FAILED',str(first))
    job=first['job_id']
    states=[];deadline=time.monotonic()+timeout
    while True:
        code,state=http('/v1/jobs/'+job)
        states.append(state);save(out/'polls.json',states)
        if code!=200:
            raise Failure('POLL_FAILED',str(state))
        if state['status'] in ['SUCCEEDED','FAILED','TIMED_OUT']:
            break
        if time.monotonic()>deadline:
            raise Failure('POLL_TIMEOUT',job)
        time.sleep(2)
    code,result=http('/v1/jobs/'+job+'/artifacts')
    save(out/'result.json',result)
    if state['status']!='SUCCEEDED' or code!=200:
        raise Failure('TASK_FAILED',str(state))
    if [x['name'] for x in result['stages']]!=['draft','full-check','incremental-check','repair','recheck']:
        raise Failure('STAGE_ORDER_MISMATCH','Expected all five E12 stages')
    downloads=out/'downloads';downloads.mkdir()
    files=['draft.json','full-check.json','incremental-check.json','repair.json','recheck.json','candidate.patch']
    for name in files:
        ref=next(x for x in result['artifacts'] if x['uri']==f'artifact://{job}/{name}')
        with urlopen(f'{base_url.rstrip("/")}/v1/jobs/{job}/files/{name}',timeout=30) as response:
            data=response.read();headers=dict(response.headers)
            digest=hashlib.sha256(data).hexdigest()
            if digest!=ref['sha256'] or digest!=response.headers.get('X-Content-SHA256'):
                raise Failure('ARTIFACT_HASH_MISMATCH',name)
        (downloads/name).write_bytes(data);save(downloads/(name+'.headers.json'),headers)
        if name.endswith('.json'):
            report=json.loads(data)
            expected=request['base'] if name=='full-check.json' else request['target']
            if report['job_id']!=job or report['trace_id']!=result['trace_id'] or report['commit']!=expected:
                raise Failure('REPORT_IDENTITY_MISMATCH',name)
    download_report(base_url,job,request['target'],out/'report-transfer')
    code,replayed=http('/v1/jobs',body)
    save(out/'same-key-response.json',{'http_status':code,'body':replayed})
    if code!=202 or replayed['job_id']!=job:
        raise Failure('IDEMPOTENCY_FAILED','Same input must keep the job')
    conflict={'idempotency_key':key,'input':dict(request,target=request['base'])}
    save(out/'conflict-request.json',conflict)
    code,rejected=http('/v1/jobs',conflict)
    save(out/'conflict-response.json',{'http_status':code,'body':rejected})
    if code!=409 or rejected.get('error')!='IDEMPOTENCY_CONFLICT':
        raise Failure('IDEMPOTENCY_FAILED','Changed target must return 409')
    code,unchanged=http('/v1/jobs/'+job)
    if code!=200 or unchanged!=state:
        raise Failure('IDEMPOTENCY_FAILED','Conflict changed the original task state')
    save(out/'verification.json',{'passed':True,'job_id':job,'trace_id':result['trace_id'],
         'target':request['target'],'download_count':len(files),'replay_same_job':True,
         'changed_target_http_status':409,'original_state_unchanged':True})
    print('API_E12_VERIFIED',job,result['trace_id'])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--base-url',required=True)
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--key',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    probe(args.base_url,json.loads(args.request.read_text()),args.key,args.out)
