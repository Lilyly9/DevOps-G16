"""A2 (241880496) E13 regressions: C2, C3 and C8."""

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pipeline
import server

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "labs/e13e14"))
from handoff_a_to_b import make_handoff


class A2E13Tests(unittest.TestCase):
    def test_c2_old_commit_is_rejected_before_repair(self):
        with tempfile.TemporaryDirectory() as d:
            fixed = Path(d) / "fixed-md.json"
            fixed.write_text(
                '{"schema_version":"e11e12-1","kind":"fixed-md","commit":"'
                + "a" * 40
                + '","status":"SUCCEEDED","data":{"commit":"'
                + "a" * 40
                + '","findings":[]}}',
                encoding="utf-8",
            )
            request = {
                "mode": "e11-b",
                "repo": str(Path(d) / "not-present"),
                "base": "a" * 40,
                "target": "b" * 40,
                "fixed_report": str(fixed),
            }
            result = pipeline.execute(request, Path(d) / "out")
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["error"]["code"], "STALE_REPORT")

    def test_c3_transferred_report_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fixed = Path(d) / "fixed-md.json"
            fixed.write_text('{"kind":"fixed-md"}\n', encoding="utf-8")
            request = {
                "mode": "e11-b",
                "repo": str(pipeline.ROOT / "data/p"),
                "base": "a" * 40,
                "target": "b" * 40,
                "fixed_report": str(fixed),
                "fixed_report_sha256": "0" * 64,
            }
            out = Path(d) / "out"
            result = pipeline.execute(request, out)
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["error"]["code"], "ARTIFACT_HASH_MISMATCH")

    def test_c8_same_key_same_request_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            store = server.Store(Path(d) / "jobs")
            request = {
                "mode": "e11-a",
                "repo": str(pipeline.ROOT / "data/p"),
                "base": "a",
                "target": "b",
            }
            with patch.object(store.pool, "submit"):
                first = store.submit(request, "a2-e13-key")
                second = store.submit(copy.deepcopy(request), "a2-e13-key")
                self.assertEqual(first["job_id"], second["job_id"])
                changed = copy.deepcopy(request)
                changed["target"] = "c"
                with self.assertRaisesRegex(ValueError, "IDEMPOTENCY_CONFLICT"):
                    store.submit(changed, "a2-e13-key")
            store.pool.shutdown()

    def test_handoff_module_is_available_for_a_report_export(self):
        self.assertTrue(callable(make_handoff))


if __name__ == "__main__":
    unittest.main()
