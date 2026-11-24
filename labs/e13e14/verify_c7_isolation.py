"""Verify C7: one failed task must not contaminate the next normal task.

Usage: python3 labs/e13e14/verify_c7_isolation.py work/e13-c7-failed work/e13-c7-success

Both arguments are E11-E12 run directories written by
``python3 run_e11e12.py run --request <request> --out <dir>``.  The first run
must be a failure, the second a success.  The check covers the C7 minimum
evidence from the E13 manual: a distinct job_id and trace_id, a status that
matches the observed exit code, every success artifact inside the success
job's own ``artifact://<job_id>/`` namespace with a matching SHA-256 and byte
count, and no artifact carried over from the failed task.

Exit: 0 = isolation holds, 1 = isolation violated, 2 = the evidence itself is
unusable (missing or unparsable ``result.json``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def load(run_dir: Path) -> dict:
    path = run_dir / "result.json"
    if not path.is_file():
        raise ValueError(f"missing result.json: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"result.json is not an object: {path}")
    return data


def verify(failed_dir: Path, succeeded_dir: Path) -> dict:
    """Return a structured report; ``ok`` is True only when every check passes."""
    failed = load(failed_dir)
    succeeded = load(succeeded_dir)
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    failed_job = failed.get("job_id")
    failed_trace = failed.get("trace_id")
    job = succeeded.get("job_id")
    trace = succeeded.get("trace_id")

    check("failed_status", failed.get("status") == "FAILED",
          f"failed run status={failed.get('status')!r}")
    check("success_status", succeeded.get("status") == "SUCCEEDED",
          f"second run status={succeeded.get('status')!r}")
    check("failed_job_id", isinstance(failed_job, str) and failed_job.startswith("job-"),
          f"failed job_id={failed_job!r}")
    check("success_job_id", isinstance(job, str) and job.startswith("job-"),
          f"success job_id={job!r}")
    check("distinct_job_id", failed_job != job,
          f"failed={failed_job!r} success={job!r}")
    check("distinct_trace_id", failed_trace != trace,
          f"failed={failed_trace!r} success={trace!r}")

    prefix = f"artifact://{job}/"
    failed_prefix = f"artifact://{failed_job}/"
    failed_uris = {item.get("uri") for item in failed.get("artifacts") or []
                   if isinstance(item, dict)}
    success_uris: list[str] = []
    for item in succeeded.get("artifacts") or []:
        if not isinstance(item, dict):
            check("artifact_entry", False, f"artifact entry is not an object: {item!r}")
            continue
        uri = item.get("uri")
        if not isinstance(uri, str) or not uri.startswith(prefix):
            check("artifact_namespace", False, f"artifact outside the success job: {uri!r}")
            continue
        relative = uri[len(prefix):]
        path = (succeeded_dir / relative).resolve()
        if not path.is_relative_to(succeeded_dir.resolve()) or not path.is_file():
            check("artifact_present", False, f"missing or escaping artifact: {uri!r}")
            continue
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        check("artifact_sha256", digest == item.get("sha256"),
              f"{uri!r} expected={item.get('sha256')!r} actual={digest}")
        if "bytes" in item:
            check("artifact_bytes", len(data) == item["bytes"],
                  f"{uri!r} expected={item['bytes']} actual={len(data)}")
        success_uris.append(uri)

    for uri in failed_uris:
        if not isinstance(uri, str) or not uri.startswith(failed_prefix):
            check("failed_artifact_namespace", False,
                  f"failed artifact outside the failed job: {uri!r}")
    overlap = sorted(set(success_uris) & {u for u in failed_uris if isinstance(u, str)})
    check("no_shared_artifact", not overlap, f"shared artifacts: {overlap}")

    for stage in succeeded.get("stages") or []:
        if not isinstance(stage, dict):
            check("stage_entry", False, f"stage entry is not an object: {stage!r}")
            continue
        name = stage.get("name")
        artifact = stage.get("artifact")
        if isinstance(artifact, dict) and isinstance(artifact.get("uri"), str):
            check("stage_namespace", artifact["uri"].startswith(prefix),
                  f"stage {name!r} artifact outside the success job: {artifact['uri']!r}")
        # E14 responses carry the identity directly; E11-E12 result.json does not.
        if "job_id" in stage or "trace_id" in stage:
            check("stage_identity",
                  (stage.get("job_id"), stage.get("trace_id")) == (job, trace),
                  f"stage {name!r} carries another job/trace")

    ok = all(item["passed"] for item in checks)
    return {
        "schema_version": "e13e14-c7-1",
        "status": "PASS" if ok else "FAIL",
        "failed": {"dir": str(failed_dir), "job_id": failed_job,
                   "trace_id": failed_trace, "status": failed.get("status")},
        "succeeded": {"dir": str(succeeded_dir), "job_id": job,
                      "trace_id": trace, "status": succeeded.get("status"),
                      "artifacts": len(success_uris)},
        "checks": checks,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify C7 failure isolation between two runs")
    parser.add_argument("failed", type=Path)
    parser.add_argument("succeeded", type=Path)
    parser.add_argument("--out", type=Path, help="optional path for the JSON report")
    args = parser.parse_args(argv)
    try:
        report = verify(args.failed, args.succeeded)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"C7_ISOLATION=UNUSABLE {exc}")
        return 2
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    for item in report["checks"]:
        if not item["passed"]:
            print(f"C7_CHECK_FAILED {item['name']}: {item['detail']}")
    print(f"C7_ISOLATION={report['status']} artifacts={report['succeeded']['artifacts']} "
          f"checks={len(report['checks'])}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
