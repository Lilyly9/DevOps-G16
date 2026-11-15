"""A 侧增量报告出口与下载核验，供独立消费者按契约接入。"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen

from pipeline import Failure, check_envelope, load_artifact, save

TRANSFER_SCHEMA = 'e11e12-transfer-1'
COMMIT = re.compile(r'[0-9a-f]{40}\Z')


def export_report(out, job_id, target):
    """只导出已完成任务中、与清单和目标一致的实际增量封装。"""
    if not isinstance(target, str) or not COMMIT.fullmatch(target):
        raise Failure('INVALID_TARGET', 'target must be a complete lowercase Git SHA')
    result_path = out/'result.json'
    if not result_path.is_file():
        raise Failure('RESULT_NOT_READY', 'Wait until the task finishes')
    result = json.loads(result_path.read_text())
    if result.get('status') != 'SUCCEEDED':
        raise Failure('UPSTREAM_FAILED', 'The source task must succeed before handoff')
    if result.get('job_id') != job_id:
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Source result belongs to another job')
    if result.get('target_commit') != target:
        raise Failure('STALE_REPORT', 'Requested target differs from the completed task')
    stages = [s for s in result['stages'] if s['name'] == 'incremental-check']
    if len(stages) != 1:
        raise Failure('ARTIFACT_TYPE_MISMATCH', 'Exactly one incremental-check stage is required')
    ref = stages[0]['artifact']
    expected_uri = f'artifact://{job_id}/incremental-check.json'
    if ref.get('uri') != expected_uri:
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Stage artifact URI does not identify this job')
    path = out/'incremental-check.json'
    if path.is_symlink():
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Report must be a regular task artifact')
    report = load_artifact(path, ref['sha256'])
    if path.stat().st_size != ref.get('bytes'):
        raise Failure('ARTIFACT_HASH_MISMATCH', 'Artifact size differs from the task manifest')
    verify_report(report, job_id, result['trace_id'], target)
    return {'schema_version': TRANSFER_SCHEMA, 'kind': 'incremental-check',
            'job_id': job_id, 'trace_id': result['trace_id'], 'commit': target,
            'report': ref, 'download_path': f'/v1/jobs/{job_id}/files/incremental-check.json'}


def verify_report(report, job_id, trace_id, target):
    if not isinstance(report, dict) or not isinstance(report.get('data'), dict):
        raise Failure('SCHEMA_MISMATCH', 'Report and data must be JSON objects')
    check_envelope(report, target, 'incremental-check')
    if report.get('job_id') != job_id or report.get('trace_id') != trace_id:
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Report job/trace differs from its source manifest')
    if report.get('data', {}).get('commit') != target:
        raise Failure('STALE_REPORT', 'Inner EChecker data belongs to another commit')


def download_report(base_url, job_id, target, out):
    """从 HTTP 文件接口下载原始字节，核对清单、响应头和实际内容。"""
    if out.exists():
        raise Failure('OUTPUT_EXISTS', 'Use a fresh transfer directory')
    out.mkdir(parents=True)
    manifest_url = f'{base_url.rstrip("/")}/v1/jobs/{job_id}/reports/incremental-check?target={target}'
    with urlopen(manifest_url, timeout=30) as response:
        raw_manifest = response.read()
    (out/'transfer-manifest.json').write_bytes(raw_manifest)
    manifest = json.loads(raw_manifest)
    if manifest.get('schema_version') != TRANSFER_SCHEMA:
        raise Failure('SCHEMA_MISMATCH', 'Expected e11e12-transfer-1')
    if manifest.get('job_id') != job_id or manifest.get('commit') != target:
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Transfer manifest differs from the request')
    expected_path = f'/v1/jobs/{job_id}/files/incremental-check.json'
    if manifest.get('download_path') != expected_path or manifest.get('kind') != 'incremental-check':
        raise Failure('ARTIFACT_TYPE_MISMATCH', 'Expected this job incremental report download')
    if manifest.get('report', {}).get('uri') != f'artifact://{job_id}/incremental-check.json':
        raise Failure('REPORT_IDENTITY_MISMATCH', 'Transfer artifact URI differs from the request')
    with urlopen(base_url.rstrip('/')+expected_path, timeout=30) as response:
        data = response.read()
        headers = dict(response.headers)
        response_hash = response.headers.get('X-Content-SHA256')
    (out/'incremental-check.json').write_bytes(data)
    save(out/'response-headers.json', headers)
    digest = hashlib.sha256(data).hexdigest()
    if digest != manifest['report']['sha256'] or digest != response_hash or len(data) != manifest['report']['bytes']:
        raise Failure('ARTIFACT_HASH_MISMATCH', 'Manifest, HTTP header and actual bytes must agree')
    report = json.loads(data)
    verify_report(report, job_id, manifest['trace_id'], target)
    save(out/'verification.json', {'passed': True, 'job_id': job_id,
         'trace_id': manifest['trace_id'], 'target': target, 'sha256': digest,
         'uri': manifest['report']['uri'], 'source_url': manifest_url})
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--job', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    download_report(args.base_url, args.job, args.target, args.out)
    print('REPORT_TRANSFER_VERIFIED', args.out)
