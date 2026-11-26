"""Collect real E14 task results and probe Compose service health for Prometheus."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


ROLES = ('draft', 'buildchecker', 'echecker', 'mdfixer')
STATUSES = ('SUCCEEDED', 'FAILED')


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def ready(role):
    try:
        with urlopen(f'http://{role}:8080/health', timeout=1) as response:
            return int(json.load(response)['role'] == role)
    except (OSError, ValueError, KeyError):
        return 0


def metrics(evidence):
    counts = Counter({state: 0 for state in STATUSES})
    elapsed = Counter({state: 0 for state in STATUSES})
    for path in evidence.glob('*.json'):
        result = read(path)
        counts[result['status']] += 1
        elapsed[result['status']] += result['duration_seconds']
    with ThreadPoolExecutor(max_workers=len(ROLES)) as pool:
        probes = list(pool.map(ready, ROLES))
    rows = ['# TYPE a16_role_ready gauge']
    rows.extend(f'a16_role_ready{{role="{role}"}} {up}' for role, up in zip(ROLES, probes, strict=True))
    rows.append('# TYPE a16_jobs_total counter')
    rows.extend(f'a16_jobs_total{{status="{state}"}} {counts[state]}' for state in STATUSES)
    rows.append('# TYPE a16_job_duration_seconds summary')
    for state in STATUSES:
        rows.append(f'a16_job_duration_seconds_sum{{status="{state}"}} {elapsed[state]:.6f}')
        rows.append(f'a16_job_duration_seconds_count{{status="{state}"}} {counts[state]}')
    return ('\n'.join(rows) + '\n').encode()


def serve(folder):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/metrics':
                self.send_error(404)
                return
            body = metrics(folder)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with ThreadingHTTPServer(('0.0.0.0', 8080), Handler) as server:
        server.serve_forever()


def run(checkout, request, output, observations, ports):
    sys.path.insert(0, str(checkout / 'labs/e13e14'))
    import orchestrate

    orchestrate.PORTS.update(zip(ROLES, ports, strict=True))
    original_call = orchestrate.call

    def observed_call(role, payload, evidence):
        start = time.monotonic()
        fields = {'timestamp': datetime.now(timezone.utc).isoformat(), 'role': role,
                  'job_id': payload['job_id'], 'trace_id': payload['trace_id'],
                  'stage_response': evidence.name}
        try:
            value = original_call(role, payload, evidence)
        except HTTPError:
            raise
        except (URLError, TimeoutError) as exc:
            fields.update(event='call_failed', error_code='DOWNSTREAM_UNAVAILABLE',
                          reason=str(exc), duration_ms=round((time.monotonic() - start) * 1000))
            write(evidence.with_name(evidence.stem + '-transport-error.json'), fields)
            print(json.dumps(fields), flush=True)
            raise ValueError(f'{role}: {fields["error_code"]}') from exc
        fields.update(event='call_succeeded', duration_ms=round((time.monotonic() - start) * 1000))
        print(json.dumps(fields), flush=True)
        return value

    orchestrate.call = observed_call
    start = time.monotonic()
    try:
        result = orchestrate.execute(read(request), output)
    finally:
        orchestrate.call = original_call
    observation = {name: result[name] for name in ('job_id', 'trace_id', 'status')}
    observation.update(duration_seconds=round(time.monotonic() - start, 6),
                       timestamp=datetime.now(timezone.utc).isoformat())
    if 'error' in result:
        observation['error'] = result['error']
    path = observations / f'{result["job_id"]}.json'
    temporary = path.with_suffix('.tmp')
    write(temporary, observation)
    temporary.replace(path)
    print(json.dumps(observation), flush=True)
    return int(result['status'] != 'SUCCEEDED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    server = commands.add_parser('serve')
    server.add_argument('observations', type=Path)
    runner = commands.add_parser('run')
    for name in ('checkout', 'request', 'output', 'observations'):
        runner.add_argument(name, type=Path)
    runner.add_argument('ports', nargs=len(ROLES), type=int)
    args = parser.parse_args()
    if args.command == 'serve':
        serve(args.observations)
        return 0
    return run(args.checkout.resolve(), args.request, args.output.resolve(), args.observations, args.ports)


if __name__ == '__main__':
    raise SystemExit(main())
