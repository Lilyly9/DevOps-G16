"""B3 (241880597) E13 independent review: C8 idempotency conflict.

Covers the same-key/same-request reuse and the same-key/different-request
conflict at both the Store layer and the HTTP boundary, independently of A2.
"""

import copy
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

import pipeline
import server


def _request(repo=None):
    return {
        "mode": "e11-a",
        "repo": repo or str(pipeline.ROOT / "data/p"),
        "base": "a",
        "target": "b",
    }


class B3E13Tests(unittest.TestCase):
    def test_c8_same_key_same_request_returns_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            store = server.Store(Path(d) / "jobs")
            request = _request()
            with patch.object(store.pool, "submit"):
                first = store.submit(request, "b3-e13-c8-key")
                second = store.submit(copy.deepcopy(request), "b3-e13-c8-key")
            self.assertEqual(first["job_id"], second["job_id"])
            self.assertEqual(len(store.jobs), 1)
            store.pool.shutdown()

    def test_c8_same_key_different_target_is_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            store = server.Store(Path(d) / "jobs")
            request = _request()
            with patch.object(store.pool, "submit"):
                store.submit(request, "b3-e13-c8-key-2")
                changed = copy.deepcopy(request)
                changed["target"] = "c"
                with self.assertRaisesRegex(ValueError, "IDEMPOTENCY_CONFLICT"):
                    store.submit(changed, "b3-e13-c8-key-2")
            store.pool.shutdown()

    def test_c8_http_conflict_maps_to_409(self):
        with tempfile.TemporaryDirectory() as d:
            store = server.Store(Path(d) / "jobs")
            httpd = server.create_server(store, "127.0.0.1", 0)
            port = httpd.server_address[1]
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                with patch.object(store.pool, "submit"):
                    base = json.dumps(
                        {"input": _request(), "idempotency_key": "b3-http-key"}
                    ).encode()
                    hdrs = {"Content-Type": "application/json"}

                    def post(body):
                        req = urllib.request.Request(
                            f"http://127.0.0.1:{port}/v1/jobs",
                            data=body, headers=hdrs, method="POST",
                        )
                        try:
                            with urllib.request.urlopen(req, timeout=5) as resp:
                                return resp.status, json.load(resp)
                        except urllib.error.HTTPError as exc:
                            return exc.code, json.loads(exc.read())

                    status1, first = post(base)
                    self.assertEqual(status1, 202)
                    status2, second = post(base)
                    self.assertEqual(status2, 202)
                    self.assertEqual(first["job_id"], second["job_id"])

                    changed = _request()
                    changed["target"] = "c"
                    body = json.dumps(
                        {"input": changed, "idempotency_key": "b3-http-key"}
                    ).encode()
                    status3, third = post(body)
                    self.assertEqual(status3, 409)
                    self.assertEqual(third["error"], "IDEMPOTENCY_CONFLICT")
            finally:
                httpd.shutdown()
                httpd.server_close()
                store.pool.shutdown()


if __name__ == "__main__":
    unittest.main()
