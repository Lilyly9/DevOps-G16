"""Validate A1's offline examples, including cross-file handoff consistency."""

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


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
    findings = response["output"]["findings"]
    require(len({f["finding_id"] for f in findings}) == len(findings), "Duplicate finding ID")
    for finding in findings:
        require(finding["commit"] == request["input"]["repository"]["commit"], "Finding commit mismatch")
        require(finding["configuration_id"] == request["input"]["configuration_id"], "Finding configuration mismatch")
        require(finding["detector"] == "MANUAL_FIXTURE", "Manual sample must identify its source")
    for kind, key in [("MISSING", "missing_count"), ("REDUNDANT", "redundant_count")]:
        require(response["output"]["summary"][key] == sum(f["type"] == kind for f in findings), "Summary count mismatch")
    artifacts = response["artifacts"]
    require(len({a["artifact_id"] for a in artifacts}) == len(artifacts), "Duplicate artifact ID")
    require(sorted(a["type"] for a in artifacts) == ["ACTUAL_GRAPH", "DECLARED_GRAPH", "ERROR_REPORT"], "Expected three handoff artifacts")
    contents = {}
    for artifact in artifacts:
        require(artifact["producer_job_id"] == response["job_id"], "Artifact producer mismatch")
        common_artifact_validator.validate(artifact)
        data = read(resolve_artifact(artifact["uri"]))
        for key, value in {
            "schema_version": response["schema_version"],
            "sample_origin": "MANUAL_FIXTURE",
            "producer_job_id": response["job_id"],
            "repository": request["input"]["repository"],
            "configuration_id": request["input"]["configuration_id"],
        }.items():
            require(data.get(key) == value, f"Artifact {key} mismatch")
        contents[artifact["type"]] = data
    require(contents["ERROR_REPORT"]["findings"] == findings, "File report differs from inline findings")
    graphs = {}
    for kind in ["ACTUAL_GRAPH", "DECLARED_GRAPH"]:
        graph = contents[kind]
        nodes = set(graph["nodes"])
        require(len(nodes) == len(graph["nodes"]), "Duplicate graph node")
        edges = {(e["target"], e["dependency"]) for e in graph["edges"]}
        require(len(edges) == len(graph["edges"]), "Duplicate graph edge")
        require(all(t in nodes and d in nodes for t, d in edges), "Edge references a missing node")
        graphs[kind] = edges
    for finding in findings:
        edge = (finding["target"], finding["dependency"])
        expected = (True, False) if finding["type"] == "MISSING" else (False, True)
        require((edge in graphs["ACTUAL_GRAPH"], edge in graphs["DECLARED_GRAPH"]) == expected, "Finding contradicts fixture graphs")
    return contents


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
    valid = [("submission", request), ("completed record with MD/RD", response), ("accepted", accepted)]
    for status, code in [("FAILED", "ANALYSIS_5001"), ("TIMED_OUT", "EXEC_4002")]:
        record = copy.deepcopy(response)
        record.update(status=status, output=None, error={"code": code, "message": "Offline error example", "retriable": False}, artifacts=[])
        valid.append((status, record))
    for label, document in valid:
        common_validator.validate(document)
        validator.validate(document)
        print(f"PASS: {label} (common + service schemas)")
    check_handoff(request, response)
    print("PASS: artifact reads, provenance, report/graph consistency")
    invalid = []
    for label, path, value in [
        ("unknown job type", ["job_type"], "ABC"),
        ("wrong service", ["job_type"], "REPAIR"),
        ("short commit", ["input", "repository", "commit"], "1111111"),
        ("unpinned image", ["input", "environment", "image"], "demo:latest"),
        ("nonpositive timeout", ["input", "timeout_seconds"], 0),
        ("client-generated job ID", ["job_id"], "invalid-client-id"),
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
        ("finding commit mismatch", lambda r: r["output"]["findings"][0].update(commit="3" * 40)),
        ("artifact producer mismatch", lambda r: r["artifacts"][0].update(producer_job_id="wrong-job")),
        ("incorrect summary", lambda r: r["output"]["summary"].update(missing_count=0)),
        ("artifact path traversal", lambda r: r["artifacts"][0].update(uri="repo://../outside.json")),
    ]:
        bad = copy.deepcopy(response)
        mutate(bad)
        try:
            check_handoff(request, bad)
        except ValueError:
            print(f"PASS: reject {label}")
        else:
            raise ValueError(f"Invalid handoff accepted: {label}")
    print("PASS: A1 offline contract validation complete; no service executed")
