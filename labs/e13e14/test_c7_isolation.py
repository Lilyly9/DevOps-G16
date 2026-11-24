"""A1 (241880485) C7 regression: the verifier must reject a contaminated pair.

These cases pin the C7 contract that ``verify_c7_isolation.py`` enforces, so a
future edit cannot loosen the isolation check without failing CI.
"""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_c7_isolation import main, verify


def artifact(path, root, job_id):
    data = path.read_bytes()
    return {
        "uri": f"artifact://{job_id}/{path.relative_to(root).as_posix()}",
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.failed = self.root / "failed"
        self.succeeded = self.root / "succeeded"
        for run in (self.failed, self.succeeded):
            run.mkdir()
        self.failed_job, self.failed_trace = "job-failed-01", "trace-failed-01"
        self.job, self.trace = "job-success-01", "trace-success-01"
        (self.failed / "final-full.json").write_text('{"ok": false}\n', encoding="utf-8")
        (self.succeeded / "incremental-check.json").write_text(
            '{"ok": true}\n', encoding="utf-8")
        self.write_failed()
        self.write_succeeded()

    def write_failed(self):
        result = {
            "schema_version": "e11e12-1",
            "job_id": self.failed_job,
            "trace_id": self.failed_trace,
            "status": "FAILED",
            "stages": [],
            "artifacts": [artifact(self.failed / "final-full.json", self.failed,
                                   self.failed_job)],
        }
        (self.failed / "result.json").write_text(json.dumps(result) + "\n", encoding="utf-8")

    def write_succeeded(self):
        result = {
            "schema_version": "e11e12-1",
            "job_id": self.job,
            "trace_id": self.trace,
            "status": "SUCCEEDED",
            "stages": [{"name": "incremental-check", "job_id": self.job,
                        "trace_id": self.trace}],
            "artifacts": [artifact(self.succeeded / "incremental-check.json",
                                   self.succeeded, self.job)],
        }
        (self.succeeded / "result.json").write_text(json.dumps(result) + "\n", encoding="utf-8")

    def reload_succeeded(self):
        path = self.succeeded / "result.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def store(self, data):
        (self.succeeded / "result.json").write_text(json.dumps(data) + "\n", encoding="utf-8")

    def test_clean_pair_passes(self):
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["succeeded"]["artifacts"], 1)
        self.assertTrue(all(item["passed"] for item in report["checks"]))
        self.assertEqual(main([str(self.failed), str(self.succeeded)]), 0)

    def test_shared_job_id_is_rejected(self):
        data = self.reload_succeeded()
        data["job_id"] = self.failed_job
        data["artifacts"] = [
            {"uri": f"artifact://{self.failed_job}/incremental-check.json",
             "sha256": hashlib.sha256(
                 (self.succeeded / "incremental-check.json").read_bytes()).hexdigest()}
        ]
        self.store(data)
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "FAIL")
        failed = {item["name"] for item in report["checks"] if not item["passed"]}
        self.assertIn("distinct_job_id", failed)

    def test_shared_trace_id_is_rejected(self):
        data = self.reload_succeeded()
        data["trace_id"] = self.failed_trace
        data["stages"][0]["trace_id"] = self.failed_trace
        self.store(data)
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "FAIL")
        failed = {item["name"] for item in report["checks"] if not item["passed"]}
        self.assertIn("distinct_trace_id", failed)

    def test_foreign_artifact_namespace_is_rejected(self):
        data = self.reload_succeeded()
        data["artifacts"][0]["uri"] = (
            f"artifact://{self.failed_job}/incremental-check.json")
        self.store(data)
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "FAIL")
        failed = {item["name"] for item in report["checks"] if not item["passed"]}
        self.assertIn("artifact_namespace", failed)

    def test_changed_bytes_are_rejected(self):
        (self.succeeded / "incremental-check.json").write_text(
            '{"ok": "tampered"}\n', encoding="utf-8")
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "FAIL")
        failed = {item["name"] for item in report["checks"] if not item["passed"]}
        self.assertIn("artifact_sha256", failed)

    def test_success_status_is_required(self):
        data = self.reload_succeeded()
        data["status"] = "FAILED"
        self.store(data)
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "FAIL")
        failed = {item["name"] for item in report["checks"] if not item["passed"]}
        self.assertIn("success_status", failed)

    def test_missing_evidence_is_unusable(self):
        (self.succeeded / "result.json").unlink()
        self.assertEqual(main([str(self.failed), str(self.succeeded)]), 2)

    def test_e11e12_stage_shape_without_identity_passes(self):
        # run_e11e12.py writes stages as {name, artifact} only; that shape must
        # not be reported as a foreign job.
        data = self.reload_succeeded()
        data["stages"] = [{"name": "incremental-check",
                           "artifact": data["artifacts"][0]}]
        self.store(data)
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(item["passed"] for item in report["checks"]))

    def test_stage_artifact_from_failed_job_is_rejected(self):
        data = self.reload_succeeded()
        data["stages"] = [{"name": "incremental-check", "artifact": {
            "uri": f"artifact://{self.failed_job}/incremental-check.json",
            "sha256": data["artifacts"][0]["sha256"]}}]
        self.store(data)
        report = verify(self.failed, self.succeeded)
        self.assertEqual(report["status"], "FAIL")
        failed = {item["name"] for item in report["checks"] if not item["passed"]}
        self.assertIn("stage_namespace", failed)


if __name__ == "__main__":
    unittest.main()
