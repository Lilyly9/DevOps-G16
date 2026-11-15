"""A3 的来源/哈希出口、HTTP 幂等与重启恢复独立预期。"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pipeline
import report_exchange
import server


class Student241880464(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.job = 'job-a3-independent'
        self.trace = 'trace-a3-independent'
        self.target = 'a'*40
        self.store = server.Store(self.root/'jobs')
        self.addCleanup(self.store.pool.shutdown)
        self.out = self.store.root/self.job/'evidence'
        self.report = {'schema_version':'e11e12-1','kind':'incremental-check',
                       'status':'SUCCEEDED','commit':self.target,'job_id':self.job,
                       'trace_id':self.trace,'data':{'commit':self.target,'findings':[
                           {'type':'MISSING','target':'main.o','dependency':'extra.h'}]},
                       'artifacts':[]}
        self.write_report()
        self.store.jobs[self.job] = {'job_id':self.job,'status':'SUCCEEDED','trace_id':self.trace}

    def write_report(self):
        pipeline.save(self.out/'incremental-check.json',self.report)
        ref=pipeline.artifact(self.out/'incremental-check.json',self.out,self.job)
        pipeline.save(self.out/'result.json',{'status':'SUCCEEDED','job_id':self.job,
                      'trace_id':self.trace,'target_commit':self.target,
                      'stages':[{'name':'incremental-check','artifact':ref}]})

    def export(self, target=None):
        return report_exchange.export_report(self.out,self.job,target or self.target)

    def expect_code(self, code, target=None):
        with self.assertRaises(pipeline.Failure) as caught:
            self.export(target)
        self.assertEqual(caught.exception.code,code)

    def start_server(self):
        httpd=server.create_server(self.store,port=0)
        thread=threading.Thread(target=httpd.serve_forever,daemon=True)
        thread.start()
        def close():
            httpd.shutdown();httpd.server_close();thread.join(timeout=5)
        self.addCleanup(close)
        return f'http://127.0.0.1:{httpd.server_port}'

    def test_report_export_has_current_identity_and_exact_hash(self):
        result=self.export()
        data=(self.out/'incremental-check.json').read_bytes()
        self.assertEqual(result['report']['sha256'],hashlib.sha256(data).hexdigest())
        self.assertEqual(result['report']['bytes'],len(data))
        self.assertEqual(result['download_path'],f'/v1/jobs/{self.job}/files/incremental-check.json')
        self.assertEqual((result['job_id'],result['trace_id'],result['commit']),
                         (self.job,self.trace,self.target))

    def test_export_rejects_requested_old_target(self):
        self.expect_code('STALE_REPORT','b'*40)

    def test_export_rejects_schema(self):
        self.report['schema_version']='e11e12-old';self.write_report()
        self.expect_code('SCHEMA_MISMATCH')

    def test_export_rejects_kind(self):
        self.report['kind']='fixed-md';self.write_report()
        self.expect_code('ARTIFACT_TYPE_MISMATCH')

    def test_export_rejects_inner_commit_even_when_outer_matches(self):
        self.report['data']['commit']='b'*40;self.write_report()
        self.expect_code('STALE_REPORT')

    def test_export_rejects_trace_from_another_job(self):
        self.report['trace_id']='trace-from-another-task';self.write_report()
        self.expect_code('REPORT_IDENTITY_MISMATCH')

    def test_export_rejects_tampered_bytes(self):
        with (self.out/'incremental-check.json').open('a') as stream:stream.write(' ')
        self.expect_code('ARTIFACT_HASH_MISMATCH')

    def test_export_rejects_incomplete_source(self):
        data=json.loads((self.out/'result.json').read_text());data['status']='FAILED'
        pipeline.save(self.out/'result.json',data)
        self.expect_code('UPSTREAM_FAILED')

    def test_http_export_downloads_original_bytes_and_three_hashes(self):
        base=self.start_server()
        report=report_exchange.download_report(base,self.job,self.target,self.root/'received')
        self.assertEqual(report,self.report)
        self.assertEqual((self.root/'received/incremental-check.json').read_bytes(),
                         (self.out/'incremental-check.json').read_bytes())
        self.assertTrue(json.loads((self.root/'received/verification.json').read_text())['passed'])

    def test_http_stale_target_returns_contract_code(self):
        base=self.start_server()
        with self.assertRaises(HTTPError) as caught:
            urlopen(f'{base}/v1/jobs/{self.job}/reports/incremental-check?target='+ 'b'*40)
        self.assertEqual(caught.exception.code,409)
        self.assertEqual(json.load(caught.exception)['error'],'STALE_REPORT')

    def test_http_conflict_preserves_original_task_and_queue_count(self):
        base=self.start_server()
        body={'idempotency_key':'a3-conflict','input':{'mode':'e11-a',
              'repo':str(pipeline.ROOT/'data/a3-case'),'base':'a'*40,'target':'b'*40}}
        def post(value):
            return urlopen(Request(base+'/v1/jobs',data=json.dumps(value).encode(),
                                   headers={'Content-Type':'application/json'}))
        with patch.object(self.store.pool,'submit') as submit:
            with post(body) as response:first=json.load(response)
            state_before=(self.store.root/first['job_id']/'state.json').read_bytes()
            with post(body) as response:self.assertEqual(json.load(response)['job_id'],first['job_id'])
            changed=copy.deepcopy(body);changed['input']['target']='c'*40
            with self.assertRaises(HTTPError) as caught:post(changed)
            self.assertEqual(caught.exception.code,409)
            self.assertEqual(json.load(caught.exception)['error'],'IDEMPOTENCY_CONFLICT')
            self.assertEqual((self.store.root/first['job_id']/'state.json').read_bytes(),state_before)
            self.assertEqual(submit.call_count,1)

    def test_stage_timeout_is_saved_as_timed_out_result(self):
        request={'mode':'e11-a','repo':str(self.root),'base':'a'*40,'target':'b'*40}
        with patch.object(pipeline,'snapshot',side_effect=TimeoutError('isolated stage deadline')):
            result=pipeline.execute(request,self.root/'timeout-evidence')
        self.assertEqual(result['status'],'TIMED_OUT')
        self.assertEqual(result['error']['code'],'TIMEOUT')
        self.assertEqual(json.loads((self.root/'timeout-evidence/result.json').read_text()),result)

    def test_restart_marks_unfinished_but_preserves_completed_result(self):
        for suffix,status in [('running','RUNNING'),('done','SUCCEEDED')]:
            pipeline.save(self.store.root/f'job-{suffix}'/'state.json',
                {'job_id':f'job-{suffix}','status':status,'idempotency_key':suffix,
                 'request_hash':suffix,'trace_id':self.trace})
        completed=(self.store.root/'job-done/state.json').read_bytes()
        restarted=server.Store(self.store.root)
        self.addCleanup(restarted.pool.shutdown)
        self.assertEqual(restarted.jobs['job-running']['status'],'FAILED')
        self.assertEqual(restarted.jobs['job-running']['error']['code'],'SERVER_RESTARTED')
        self.assertEqual(restarted.jobs['job-done']['status'],'SUCCEEDED')
        self.assertEqual((self.store.root/'job-done/state.json').read_bytes(),completed)


if __name__ == '__main__':
    unittest.main()
