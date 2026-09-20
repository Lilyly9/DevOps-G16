"""Validate A2's offline EChecker examples, including the baseline handoff to A1's BuildChecker artifacts."""

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


def warn(message):
    print(f"WARN: {message}")


def resolve_artifact(uri):
    require(uri.startswith("repo://"), "Expected a repo:// fixture URI")
    relative = uri[len("repo://"):]
    require(relative and not Path(relative).is_absolute(), "Expected a relative artifact path")
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), "Artifact escapes repository root")
    return path


def edge_set(graph):
    return {(edge["target"], edge["dependency"]) for edge in graph["edges"]}


def finding_key(item):
    return (item["type"], item["target"], item["dependency"])


def check_handoff(request, response):
    require(request["input"] == response["input"], "Request/response inputs differ")
    require(request["trace_id"] == response["trace_id"], "Trace IDs differ")
    require(request["schema_version"] == response["schema_version"], "Schema versions differ")
    require(request["job_type"] == response["job_type"] == "INCREMENTAL_CHECK", "Unexpected job type")
    payload = request["input"]
    baseline = payload["baseline"]
    if payload["base_commit"] != baseline["commit"]:
        warn("base_commit and baseline.commit differ; the course template repeats this value, so A2 reports it as a hint instead of rejecting the request")
    require(baseline["configuration_id"] == payload["configuration_id"], "Baseline configuration differs from the requested configuration")
    require(payload["base_commit"] != payload["repository"]["commit"], "Incremental check needs a head commit different from the base commit")
    baseline_graph = read(resolve_artifact(baseline["actual_graph_uri"]))
    baseline_report = read(resolve_artifact(baseline["error_report_uri"]))
    for label, artifact in [("graph", baseline_graph), ("report", baseline_report)]:
        require(artifact.get("schema_version") == request["schema_version"], f"Baseline {label} schema version mismatch")
        require(artifact.get("sample_origin") == "MANUAL_FIXTURE", f"Baseline {label} must identify its manual origin")
        require(artifact.get("producer_job_id") == baseline["producer_job_id"], f"Baseline {label} producer mismatch")
        require(artifact.get("repository", {}).get("url") == payload["repository"]["url"], f"Baseline {label} repository mismatch")
        require(artifact.get("repository", {}).get("commit") == baseline["commit"], f"Baseline {label} base commit mismatch")
        require(artifact.get("configuration_id") == baseline["configuration_id"], f"Baseline {label} configuration mismatch")
    output = response["output"]
    scope = output["scope"]
    require(set(payload.get("changed_paths", [])) <= set(scope["changed_paths"]), "Reported changed paths do not cover the caller hint")
    require(scope["checked_targets"], "No checked target was reported")
    require(len(set(scope["checked_targets"])) == len(scope["checked_targets"]), "Duplicate checked target")
    require(len(set(scope["reused_targets"])) == len(scope["reused_targets"]), "Duplicate reused target")
    require(not set(scope["checked_targets"]) & set(scope["reused_targets"]), "A target cannot be both checked and reused")
    baseline_findings = baseline_report["findings"]
    baseline_keys = {finding_key(item) for item in baseline_findings}
    require(len(baseline_keys) == len(baseline_findings), "Duplicate baseline finding")
    for item in baseline_findings:
        require(item["detector"] == "MANUAL_FIXTURE", "Baseline sample must identify its source")
    findings = output["findings"]
    require(len({item["finding_id"] for item in findings}) == len(findings), "Duplicate finding ID")
    head_keys, new_keys, carried_keys = set(), set(), set()
    for finding in findings:
        require(finding["commit"] == payload["repository"]["commit"], "Finding commit mismatch")
        require(finding["configuration_id"] == payload["configuration_id"], "Finding configuration mismatch")
        require(finding["detector"] == "MANUAL_FIXTURE", "Manual sample must identify its source")
        key = finding_key(finding)
        require(key not in head_keys, "Duplicate finding")
        head_keys.add(key)
        if finding["status"] == "NEW":
            require(key not in baseline_keys, "NEW finding already existed in the baseline")
            new_keys.add(key)
        else:
            require(key in baseline_keys, "CARRIED_OVER finding is missing from the baseline")
            carried_keys.add(key)
    resolved = output["resolved_findings"]
    require(len({item["finding_id"] for item in resolved}) == len(resolved), "Duplicate resolved finding ID")
    resolved_keys = set()
    for item in resolved:
        require(item["baseline_commit"] == baseline["commit"], "Resolved finding baseline commit mismatch")
        key = finding_key(item)
        require(key in baseline_keys, "Resolved finding is missing from the baseline")
        require(key not in head_keys, "A resolved finding still exists in this run")
        require(key not in resolved_keys, "Duplicate resolved finding")
        resolved_keys.add(key)
    require(carried_keys == head_keys - new_keys, "Findings are not fully classified as NEW or CARRIED_OVER")
    require(baseline_keys == carried_keys | resolved_keys, "Baseline delta is not closed: every baseline finding must be carried over or resolved")
    summary = output["summary"]
    for name, computed in [
        ("missing_count", sum(item["type"] == "MISSING" for item in findings)),
        ("redundant_count", sum(item["type"] == "REDUNDANT" for item in findings)),
        ("new_count", sum(item["status"] == "NEW" for item in findings)),
        ("carried_over_count", sum(item["status"] == "CARRIED_OVER" for item in findings)),
        ("resolved_count", len(resolved)),
        ("checked_target_count", len(scope["checked_targets"])),
    ]:
        require(summary[name] == computed, f"Summary {name} mismatch")
    require(summary["new_count"] + summary["carried_over_count"] == len(findings), "Findings are not fully classified as NEW or CARRIED_OVER")
    artifacts = response["artifacts"]
    require(len({item["artifact_id"] for item in artifacts}) == len(artifacts), "Duplicate artifact ID")
    require(sorted(item["type"] for item in artifacts) == ["ACTUAL_GRAPH", "DECLARED_GRAPH", "ERROR_REPORT"], "Expected three handoff artifacts")
    contents = {}
    for artifact in artifacts:
        require(artifact["producer_job_id"] == response["job_id"], "Artifact producer mismatch")
        common_artifact_validator.validate(artifact)
        data = read(resolve_artifact(artifact["uri"]))
        for key, value in {
            "schema_version": response["schema_version"],
            "sample_origin": "MANUAL_FIXTURE",
            "producer_job_id": response["job_id"],
            "repository": payload["repository"],
            "configuration_id": payload["configuration_id"],
        }.items():
            require(data.get(key) == value, f"Artifact {key} mismatch")
        contents[artifact["type"]] = data
    require(contents["ERROR_REPORT"]["findings"] == findings, "File report differs from inline findings")
    require(contents["ERROR_REPORT"]["resolved_findings"] == resolved, "File report differs from inline resolved findings")
    graphs = {}
    for kind in ["ACTUAL_GRAPH", "DECLARED_GRAPH"]:
        graph = contents[kind]
        nodes = set(graph["nodes"])
        require(len(nodes) == len(graph["nodes"]), "Duplicate graph node")
        edges = edge_set(graph)
        require(len(edges) == len(graph["edges"]), "Duplicate graph edge")
        require(all(target in nodes and dependency in nodes for target, dependency in edges), "Edge references a missing node")
        graphs[kind] = edges
    merged = contents["ACTUAL_GRAPH"]
    for key, value in {
        "commit": baseline["commit"],
        "configuration_id": baseline["configuration_id"],
        "producer_job_id": baseline["producer_job_id"],
        "actual_graph_uri": baseline["actual_graph_uri"],
    }.items():
        require(merged.get("baseline", {}).get(key) == value, f"ACTUAL_GRAPH baseline reference mismatch: {key}")
    checked = set(scope["checked_targets"])
    for target in {edge[0] for edge in edge_set(baseline_graph)} | {edge[0] for edge in graphs["ACTUAL_GRAPH"]}:
        if target in checked:
            continue
        require(
            {dependency for weight, dependency in graphs["ACTUAL_GRAPH"] if weight == target}
            == {dependency for weight, dependency in edge_set(baseline_graph) if weight == target},
            f"ACTUAL_GRAPH changed an unchecked target: {target}",
        )
    for finding in findings:
        edge = (finding["target"], finding["dependency"])
        expected = (True, False) if finding["type"] == "MISSING" else (False, True)
        require((edge in graphs["ACTUAL_GRAPH"], edge in graphs["DECLARED_GRAPH"]) == expected, "Finding contradicts fixture graphs")
    return contents


def with_mutated_request(request, response, mutate):
    bad_request, bad_response = copy.deepcopy(request), copy.deepcopy(response)
    mutate(bad_request)
    bad_response["input"] = copy.deepcopy(bad_request["input"])
    return bad_request, bad_response


def require_rejected(label, request, response):
    try:
        check_handoff(request, response)
    except ValueError:
        print(f"PASS: reject {label}")
    else:
        raise ValueError(f"Invalid handoff accepted: {label}")


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
    running = copy.deepcopy(response)
    running.update(status="RUNNING", output=None, error=None)
    running.pop("artifacts")
    valid = [("submission", request), ("completed record with incremental findings", response), ("accepted", accepted), ("running", running)]
    for status, code in [("FAILED", "ANALYSIS_5001"), ("TIMED_OUT", "EXEC_4002")]:
        record = copy.deepcopy(response)
        record.update(status=status, output=None, error={"code": code, "message": "Offline error example", "retriable": False}, artifacts=[])
        valid.append((status, record))
    for label, document in valid:
        common_validator.validate(document)
        validator.validate(document)
        print(f"PASS: {label} (common + service schemas)")
    check_handoff(request, response)
    print("PASS: baseline reads, provenance, delta closure and graph merge consistency")
    tolerated_request, tolerated_response = with_mutated_request(
        request, response, lambda document: document["input"].update(base_commit="2" * 40)
    )
    check_handoff(tolerated_request, tolerated_response)
    print("PASS: tolerate a base_commit/baseline.commit mismatch with a warning instead of rejecting it")
    def edited(base, path, value=None, remove=False):
        document = copy.deepcopy(base)
        parent = document
        for key in path[:-1]:
            parent = parent[key]
        if remove:
            del parent[path[-1]]
        else:
            parent[path[-1]] = value
        return document

    invalid = []
    for label, path, value in [
        ("unknown job type", ["job_type"], "ABC"),
        ("wrong service", ["job_type"], "FULL_CHECK"),
        ("short head commit", ["input", "repository", "commit"], "3333333"),
        ("short base commit", ["input", "base_commit"], "1111111"),
        ("short baseline commit", ["input", "baseline", "commit"], "1111111"),
        ("nonpositive timeout", ["input", "timeout_seconds"], 0),
        ("unpinned image", ["input", "environment", "image"], "demo:latest"),
        ("client-generated job ID", ["job_id"], "invalid-client-id"),
        ("unknown finding status", ["output", "findings", 0, "status"], "UNKNOWN"),
        ("missing resolved finding resolution", ["output", "resolved_findings", 0, "resolution"], "DONE"),
    ]:
        invalid.append((label, edited(response if path[0] == "output" else request, path, value)))
    for label, path in [
        ("missing baseline", ["input", "baseline"]),
        ("missing base commit", ["input", "base_commit"]),
        ("baseline without actual graph uri", ["input", "baseline", "actual_graph_uri"]),
        ("baseline without error report uri", ["input", "baseline", "error_report_uri"]),
        ("baseline without commit", ["input", "baseline", "commit"]),
        ("baseline without configuration", ["input", "baseline", "configuration_id"]),
        ("baseline without producer job", ["input", "baseline", "producer_job_id"]),
        ("missing environment", ["input", "environment"]),
        ("missing build command", ["input", "build", "command"]),
        ("missing scope", ["output", "scope"]),
        ("missing summary", ["output", "summary"]),
        ("missing resolved findings", ["output", "resolved_findings"]),
    ]:
        base = response if path[0] == "output" else request
        invalid.append((label, edited(base, path, remove=True)))
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

    cases = [
        ("baseline configuration mismatch", (lambda document: document["input"]["baseline"].update(configuration_id="gcc-o2-v2"))),
        ("head commit equals base commit", (lambda document: document["input"]["repository"].update(commit="1" * 40))),
        ("baseline producer mismatch", (lambda document: document["input"]["baseline"].update(producer_job_id="wrong-job"))),
        ("changed path hint not covered", (lambda document: document["input"].update(changed_paths=["util.c"]))),
    ]
    for label, mutate in cases:
        require_rejected(label, *with_mutated_request(request, response, mutate))

    def response_only(mutate):
        bad = copy.deepcopy(response)
        mutate(bad)
        return request, bad

    require_rejected("delta not closed", *response_only(lambda document: document["output"]["resolved_findings"].pop(0)))
    require_rejected("NEW finding already in the baseline", *response_only(lambda document: document["output"]["findings"][0].update(target="main.o", dependency="config.h", status="NEW")))
    require_rejected("CARRIED_OVER finding missing from the baseline", *response_only(lambda document: document["output"]["findings"][0].update(status="CARRIED_OVER")))
    require_rejected("incorrect summary", *response_only(lambda document: document["output"]["summary"].update(missing_count=0)))
    require_rejected("artifact producer mismatch", *response_only(lambda document: document["artifacts"][0].update(producer_job_id="wrong-job")))
    require_rejected("artifact path traversal", *response_only(lambda document: document["artifacts"][0].update(uri="repo://../outside.json")))
    require_rejected("inline findings differ from the file report", *response_only(lambda document: document["output"]["findings"][0].update(finding_id="g16-inc-md-999")))

    def claim_unchecked(document):
        document["output"]["scope"].update(checked_targets=["util.o"], reused_targets=["main.o"])
        document["output"]["summary"].update(checked_target_count=1)

    require_rejected("unchecked target changed against the baseline", *response_only(claim_unchecked))
    print("PASS: A2 offline contract validation complete; no service executed, no image built")
