"""Validate B2's offline examples, including cross-file handoff consistency."""

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path):
    return path.read_text(encoding="utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def resolve_artifact(uri):
    require(uri.startswith("repo://"), "Expected a repo:// fixture URI")
    relative = uri[len("repo://"):]
    require(relative and not Path(relative).is_absolute(), "Expected a relative artifact path")
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), "Artifact escapes repository root")
    return path


def check_handoff(request, response):
    require(request["input"] == response["input"], "Request/response inputs differ")
    require(request["trace_id"] == response["trace_id"], "Trace IDs differ")
    require(request["schema_version"] == response["schema_version"], "Schema versions differ")
    report = read(resolve_artifact(request["input"]["error_report_uri"]))
    require(report["sample_origin"] == "MANUAL_FIXTURE", "Report must identify manual origin")
    require(report["repository"] == request["input"]["repository"], "Report repository mismatch")
    require(report["configuration_id"] == request["input"]["configuration_id"], "Report configuration mismatch")
    missing = [f for f in report["findings"] if f["type"] == "MISSING"]
    require(missing, "Report has no MISSING findings to repair")
    missing_ids = {f["finding_id"] for f in missing}
    output = response["output"]
    consumed = output["summary"]["consumed_finding_ids"]
    require(len(consumed) == len(set(consumed)), "Duplicate consumed finding ID")
    require(set(consumed) == missing_ids, "Consumed findings must equal report MISSING findings")
    require(output["summary"]["fixed_count"] + output["summary"]["rejected_count"] == len(consumed), "Fix/reject counts do not sum to consumed findings")
    rejected = output.get("rejected", [])
    rejected_ids = {r["finding_id"] for r in rejected}
    require(len(rejected_ids) == len(rejected), "Duplicate rejected finding ID")
    require(output["summary"]["rejected_count"] == len(rejected), "Rejected count mismatch")
    require(rejected_ids <= missing_ids, "Rejected finding is not a report MISSING finding")
    artifacts = response["artifacts"]
    require(len({a["artifact_id"] for a in artifacts}) == len(artifacts), "Duplicate artifact ID")
    require(sorted(a["type"] for a in artifacts) == ["GIT_PATCH"], "Expected one GIT_PATCH artifact")
    by_id = {a["artifact_id"]: a for a in artifacts}
    for patch in output["patches"]:
        require(patch["target_finding_id"] in missing_ids, "Patch targets a non-MISSING finding")
        require(patch["target_finding_id"] not in rejected_ids, "Patched and rejected the same finding")
        artifact = by_id.get(patch["artifact_ref"])
        require(artifact is not None, "Patch references a missing artifact")
        require(artifact["type"] == "GIT_PATCH", "Patch artifact_ref must point to a GIT_PATCH")
    require(output["summary"]["fixed_count"] == len(output["patches"]), "Fixed count does not match patch list")
    require(len(missing) - output["summary"]["fixed_count"] == output["verification"]["recheck"]["remaining_missing"], "Recheck remaining_missing mismatch")
    for artifact in artifacts:
        require(artifact["producer_job_id"] == response["job_id"], "Artifact producer mismatch")
        common_artifact_validator.validate(artifact)
        require(artifact["media_type"] == "text/x-diff", "Patch media type must be text/x-diff")
        diff = read_text(resolve_artifact(artifact["uri"]))
        require("Makefile" in diff, "Patch must touch the Makefile")
        require("config.h" in diff, "Patch must add the missing config.h dependency")
    return report


if __name__ == "__main__":
    common = read(HERE.parent / "task.schema.json")
    service = read(HERE / "contract.schema.json")
    for schema in [common, service]:
        Draft202012Validator.check_schema(schema)
    registry = Registry().with_resources([
        (schema["$id"], Resource.from_contents(schema)) for schema in [common, service]
    ])
    common_validator = Draft202012Validator(common, registry=registry, format_checker=FormatChecker())
    validator = Draft202012Validator(service, registry=registry, format_checker=FormatChecker())
    common_artifact_validator = Draft202012Validator(
        {"$ref": common["$id"] + "#/$defs/artifact"}, registry=registry
    )
    request, response = read(HERE / "request.json"), read(HERE / "response.json")
    accepted = {key: response[key] for key in ["schema_version", "job_id", "trace_id", "job_type"]}
    accepted["status"] = "QUEUED"
    valid = [("submission", request), ("completed record with patch", response), ("accepted", accepted)]
    for status, code in [("FAILED", "ENV_3002"), ("TIMED_OUT", "EXEC_4002")]:
        record = copy.deepcopy(response)
        record.update(status=status, output=None, error={"code": code, "message": "Offline error example", "retriable": False}, artifacts=[])
        valid.append((status, record))
    rejected = copy.deepcopy(response)
    rejected["output"] = {
        "sample_origin": "MANUAL_FIXTURE",
        "summary": {"consumed_finding_ids": ["g16-md-001"], "fixed_count": 0, "rejected_count": 1},
        "patches": [],
        "rejected": [{"finding_id": "g16-md-001", "reason": "candidate patch failed the clean build during verification"}],
        "verification": {"build": "FAIL", "test": "SKIPPED", "recheck": {"status": "FAIL", "remaining_missing": 1}},
    }
    rejected["artifacts"] = []
    valid.append(("rejected candidate", rejected))
    for label, document in valid:
        common_validator.validate(document)
        validator.validate(document)
        print(f"PASS: {label} (common + service schemas)")
    check_handoff(request, response)
    print("PASS: report read, MISSING-only consumption, patch artifact read")
    invalid = []
    for label, path, value in [
        ("unknown job type", ["job_type"], "ABC"),
        ("wrong service", ["job_type"], "FULL_CHECK"),
        ("short commit", ["input", "repository", "commit"], "1111111"),
        ("unpinned image", ["input", "environment", "image"], "demo:latest"),
        ("nonpositive timeout", ["input", "timeout_seconds"], 0),
        ("client-generated job ID", ["job_id"], "invalid-client-id"),
        ("non-repo report URI", ["input", "error_report_uri"], "https://example.invalid/report.json"),
    ]:
        bad = copy.deepcopy(request)
        parent = bad
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
        invalid.append((label, bad))
    bad = copy.deepcopy(request)
    del bad["input"]["environment"]
    invalid.append(("missing environment", bad))
    bad = copy.deepcopy(request)
    del bad["input"]["error_report_uri"]
    invalid.append(("missing error report URI", bad))
    bad = copy.deepcopy(response)
    bad["output"] = None
    invalid.append(("success without output", bad))
    for status in ["FAILED", "TIMED_OUT"]:
        bad = copy.deepcopy(response)
        bad.update(status=status, output=None, error=None)
        invalid.append((f"{status} without error", bad))
    for label, document in invalid:
        require(not validator.is_valid(document), f"Invalid example accepted: {label}")
        print(f"PASS: reject {label}")
    for label, mutate in [
        ("consume redundant finding", lambda r: r["output"]["summary"].update(consumed_finding_ids=["g16-rd-001"])),
        ("patch references missing artifact", lambda r: r["output"]["patches"][0].update(artifact_ref="no-such-artifact")),
        ("patch producer mismatch", lambda r: r["artifacts"][0].update(producer_job_id="wrong-job")),
        ("artifact path traversal", lambda r: r["artifacts"][0].update(uri="repo://../outside.patch")),
    ]:
        bad = copy.deepcopy(response)
        mutate(bad)
        try:
            check_handoff(request, bad)
        except ValueError:
            print(f"PASS: reject {label}")
        else:
            raise ValueError(f"Invalid handoff accepted: {label}")
    bad_request = copy.deepcopy(request)
    bad_response = copy.deepcopy(response)
    bad_request["input"]["repository"]["commit"] = "3" * 40
    bad_response["input"]["repository"]["commit"] = "3" * 40
    try:
        check_handoff(bad_request, bad_response)
    except ValueError:
        print("PASS: reject report commit mismatch")
    else:
        raise ValueError("Invalid handoff accepted: report commit mismatch")
    print("PASS: B2 offline contract validation complete; no service executed")
