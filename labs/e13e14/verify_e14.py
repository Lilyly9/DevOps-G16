"""Verify an archived four-service run against its request and stage evidence."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(folder):
    result = read(folder / "result.json")
    request = read(folder / "request.json")
    job, trace = result["job_id"], result["trace_id"]
    require(job and trace and result["schema_version"] == "e14-compose-1", "run identity")
    require(result["status"] == "SUCCEEDED", "run status")
    for field in ("base", "target"):
        require(result[field + "_commit"] == request[field], field)
    names = ["draft", "full-check", "incremental-check", "repair", "recheck"]
    require([item["name"] for item in result["stages"]] == names, "stage sequence")
    artifacts = {}
    for item in result["artifacts"]:
        uri = item["uri"]
        path = folder / uri
        require(path.resolve().is_relative_to(folder.resolve()) and uri not in artifacts, "artifact path")
        raw = path.read_bytes()
        require(len(raw) == item["bytes"] and hashlib.sha256(raw).hexdigest() == item["sha256"], uri)
        artifacts[uri] = item["sha256"]

    stages = {}
    for item in result["stages"]:
        name = item["name"]
        expected = name + ".json"
        require(item["artifact"]["uri"] == expected, expected)
        require(artifacts.get(expected) == item["artifact"]["sha256"], expected)
        stage = read(folder / expected)
        revision = request["base" if name == "full-check" else "target"]
        require((stage["name"], stage["commit"], stage["job_id"], stage["trace_id"], stage["status"])
                == (name, revision, job, trace, "SUCCEEDED"), name + " identity")
        stages[name] = stage["data"]
    report = (folder / "incremental/incremental-check.json").read_bytes()
    sha = hashlib.sha256(report).hexdigest()
    require(sha == stages["incremental-check"]["sha256"], "report digest")
    envelope = json.loads(report)
    require((envelope["job_id"], envelope["trace_id"], envelope["commit"], envelope["data"]["commit"])
            == (job, trace, request["target"], request["target"]), "report identity")
    patch = (folder / "repair-work/candidate.patch").read_bytes()
    require(hashlib.sha256(patch).hexdigest() == stages["repair"]["sha256"], "patch digest")
    require(stages["repair"]["validation"]["accepted"] is True, "patch rejected")
    final = stages["recheck"]
    require(final["remaining_missing"] == 0 and all(item["type"] != "MISSING"
            for item in final["result"]["result"]["findings"]), "recheck findings")
    return dict(job_id=job, trace_id=trace, target=request["target"], report_sha256=sha, artifact_count=len(artifacts), stages=names)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    print(json.dumps(verify(parser.parse_args().folder), indent=2))
