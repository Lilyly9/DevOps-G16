"""Validate B1's offline examples, including cross-file handoff consistency."""

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
    output = response["output"]
    require(output["configuration_id"] == request["input"]["configuration_id"], "Output configuration mismatch")
    artifacts = response["artifacts"]
    require(len({a["artifact_id"] for a in artifacts}) == len(artifacts), "Duplicate artifact ID")
    require(sorted(a["type"] for a in artifacts) == ["BUILD_LOG", "BUILD_LOG", "DOCKERFILE"], "Expected two BUILD_LOG and one DOCKERFILE artifact")
    by_id = {a["artifact_id"]: a for a in artifacts}
    for artifact in artifacts:
        require(artifact["producer_job_id"] == response["job_id"], "Artifact producer mismatch")
        common_artifact_validator.validate(artifact)
        require(artifact["media_type"] == "text/plain", "DRAFT artifact media type must be text/plain")
    dockerfile = by_id.get(output["dockerfile_artifact_ref"])
    require(dockerfile is not None, "dockerfile_artifact_ref points to a missing artifact")
    require(dockerfile["type"] == "DOCKERFILE", "dockerfile_artifact_ref must point to a DOCKERFILE")
    dockerfile_text = read_text(resolve_artifact(dockerfile["uri"]))
    require("MANUAL_FIXTURE" in dockerfile_text, "Dockerfile must identify manual origin")
    require("FROM" in dockerfile_text, "Dockerfile must contain a FROM instruction")
    iterations = [a["iteration"] for a in output["attempts"]]
    require(iterations == list(range(1, len(iterations) + 1)), "Attempt iterations must be consecutive starting at 1")
    for attempt in output["attempts"]:
        log = by_id.get(attempt["log_artifact_ref"])
        require(log is not None, "Attempt references a missing log artifact")
        require(log["type"] == "BUILD_LOG", "log_artifact_ref must point to a BUILD_LOG")
        log_text = read_text(resolve_artifact(log["uri"]))
        require("MANUAL_FIXTURE" in log_text, "Log must identify manual origin")
    last = output["attempts"][-1]
    require(last["outcome"] == "SUCCESS", "Final attempt must be SUCCESS for a SUCCEEDED environment job")
    require(output["verification"] == {"build": "PASS", "verify": "PASS"}, "Final verification must pass for the delivered image")
    final_log = read_text(resolve_artifact(by_id[last["log_artifact_ref"]]["uri"]))
    require(request["input"]["repository"]["commit"] in final_log, "Final log does not reference the requested commit")
    require("build.command PASS" in final_log and "verify_command PASS" in final_log, "Final log must record build and verify success")
    for consumer in ["buildchecker", "echecker", "mdfixer"]:
        downstream = read(ROOT / "contracts" / consumer / "request.json")
        require(downstream["input"]["environment"]["producer_job_id"] == response["job_id"], f"{consumer} references a different DRAFT job")
        require(downstream["input"]["environment"]["image"] == output["image"], f"{consumer} image does not match DRAFT output")
        require(downstream["input"]["configuration_id"] == output["configuration_id"], f"{consumer} configuration does not match DRAFT output")
    return output


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
    valid = [("submission", request), ("completed record", response), ("accepted", accepted)]
    for status, code in [("FAILED", "ENV_3002"), ("TIMED_OUT", "EXEC_4002")]:
        record = copy.deepcopy(response)
        record.update(status=status, output=None, error={"code": code, "message": "Offline error example", "retriable": False}, artifacts=[])
        valid.append((status, record))
    for label, document in valid:
        common_validator.validate(document)
        validator.validate(document)
        print(f"PASS: {label} (common + service schemas)")
    check_handoff(request, response)
    print("PASS: artifacts read, image and configuration handoff to A1/A2/B2 consistent")
    invalid = []
    for label, path, value in [
        ("unknown job type", ["job_type"], "ABC"),
        ("wrong service", ["job_type"], "FULL_CHECK"),
        ("short commit", ["input", "repository", "commit"], "1111111"),
        ("empty verify command", ["input", "build", "verify_command"], ""),
        ("zero max iterations", ["input", "max_iterations"], 0),
        ("nonpositive timeout", ["input", "timeout_seconds"], 0),
        ("client-generated job ID", ["job_id"], "invalid-client-id"),
        ("unpinned output image", ["output", "image"], "demo:latest"),
    ]:
        bad = copy.deepcopy(request if "output" not in path else response)
        parent = bad
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
        invalid.append((label, bad))
    bad = copy.deepcopy(request)
    del bad["input"]["max_iterations"]
    invalid.append(("missing max iterations", bad))
    bad = copy.deepcopy(request)
    del bad["input"]["build"]
    invalid.append(("missing build requirements", bad))
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
        ("output configuration mismatch", lambda r: r["output"].update(configuration_id="clang-default-v1")),
        ("dockerfile reference missing artifact", lambda r: r["output"].update(dockerfile_artifact_ref="no-such-artifact")),
        ("log reference points to wrong type", lambda r: r["output"]["attempts"][0].update(log_artifact_ref="g16-dockerfile-001")),
        ("non-consecutive iterations", lambda r: r["output"]["attempts"][1].update(iteration=3)),
        ("final attempt not SUCCESS", lambda r: r["output"]["attempts"][1].update(outcome="BUILD_FAILED")),
        ("artifact producer mismatch", lambda r: r["artifacts"][0].update(producer_job_id="wrong-job")),
        ("artifact path traversal", lambda r: r["artifacts"][0].update(uri="repo://../outside.txt")),
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
        print("PASS: reject request/response commit mismatch")
    else:
        raise ValueError("Invalid handoff accepted: request/response commit mismatch")
    bad = copy.deepcopy(response)
    bad["output"]["image"] = "registry.example.invalid/g16/build-demo@sha256:" + "3" * 64
    try:
        check_handoff(request, bad)
    except ValueError:
        print("PASS: reject downstream image mismatch")
    else:
        raise ValueError("Invalid handoff accepted: downstream image mismatch")
    print("PASS: B1 offline contract validation complete; no service executed")
