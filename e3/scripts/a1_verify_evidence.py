"""Independently verify A1's saved source, command logs and trace evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

E3 = Path(__file__).resolve().parents[1]
REPO = E3.parent

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def verify(folder):
    observations = read(folder / "observations.json")
    source = read(folder / "source-manifest.json")
    environment = read(folder / "environment.json")
    commit = source["commit"]
    require(observations["member"] == "A1", "Expected A1 evidence")
    require(observations["source_commit"] == environment["source_commit"] == commit, "Source versions differ")
    require(re.fullmatch(r"[a-fA-F0-9]{40}", commit), "Expected full commit SHA")
    for name, digest in source["sha256"].items():
        committed = subprocess.check_output(["git", "-C", str(REPO), "show", commit + ":e3/fixtures/md-rd/" + name])
        require(hashlib.sha256(committed).hexdigest() == digest, "Source differs from committed fixture: " + name)
    commands = {entry["id"]: entry for entry in read(folder / "commands.json")}
    for entry in commands.values():
        require(entry["exit_code"] == 0, "Unexpected failed command: " + entry["id"])
        require(entry["source_commit"] == commit, "Command source mismatch")
        for key in ["stdout", "stderr"]:
            path = (folder / entry[key]).resolve()
            require(path.is_relative_to(folder.resolve()) and path.is_file(), "Missing or unsafe log path")
    for label, expected in [("md-rd-clean-run", "1"), ("md-rd-touch-header-run", "1"),
                            ("md-rd-clean-rebuild-run", "2"), ("md-rd-redundant-run", "2")]:
        actual = (folder / commands[label]["stdout"]).read_text(encoding="utf-8").strip()
        require(actual == expected, "Program output mismatch: " + label)
    snapshot_names = [
        "01-initial-value1", "02-header-value2-before-make", "03-stale-after-incremental",
        "04-clean-value2", "05-unused-comment-before-make", "06-redundant-after-make"]
    states = [read(folder / "snapshots" / name / "state.json") for name in snapshot_names]
    for snapshot_name, state in zip(snapshot_names, states):
        for name in source["sha256"]:
            data = (folder / "snapshots" / snapshot_name / name).read_bytes()
            require(hashlib.sha256(data).hexdigest() == state[name]["sha256"] and len(data) == state[name]["size"],
                    "Snapshot bytes differ from recorded metadata: " + snapshot_name + "/" + name)
    for name, digest in source["sha256"].items():
        require(states[0][name]["sha256"] == digest, "Initial snapshot differs from fixture")
        if name != "config.h":
            require(states[0][name]["sha256"] == states[1][name]["sha256"], "MD changed a file besides config.h")
        if name != "unused.h":
            require(states[3][name]["sha256"] == states[4][name]["sha256"], "RD changed a file besides unused.h")
    require(states[0]["config.h"]["sha256"] != states[1]["config.h"]["sha256"], "MD header did not change")
    require(states[3]["unused.h"]["sha256"] != states[4]["unused.h"]["sha256"], "RD header did not change")
    require(states[1]["config.h"]["mtime_ns"] > states[0]["main.o"]["mtime_ns"], "Header is not newer than object")
    require(states[0]["main.o"] == states[2]["main.o"], "MD did not retain the old object")
    for name in source["sha256"]:
        require(states[2][name]["sha256"] == states[3][name]["sha256"], "Incremental/clean source differs")
    require(states[4]["unused.h"]["mtime_ns"] > states[3]["main.o"]["mtime_ns"], "RD header is not newer")
    require(states[5]["main.o"]["mtime_ns"] > states[3]["main.o"]["mtime_ns"], "RD did not rebuild object")
    rd_log = (folder / commands["md-rd-redundant"]["stdout"]).read_text(encoding="utf-8")
    require("-c main.c -o main.o" in rd_log and "main.o -o app" in rd_log, "Missing compile/link evidence")
    require(observations["behavior_status"] == "PASSED" and not observations["failures"], "Baseline not successful")
    if observations["linux_trace_status"] == "PASSED":
        trace_dir = (REPO / observations["linux_evidence"]).resolve()
        require(trace_dir.is_relative_to(E3 / "evidence" / "linux-verified"), "Invalid Linux evidence path")
        require(environment["system"] == "Linux", "Trace must originate in Linux")
        trace_source = read(trace_dir / "source-manifest.json")
        require(trace_source["commit"] == commit and trace_source["sha256"] == source["sha256"], "Trace source mismatch")
        compiler_reads = []
        for path in trace_dir.glob("trace.log.*"):
            text = path.read_text(encoding="utf-8")
            if re.search(r'execve\("[^"\n]*/cc1(?:plus)?"', text) and re.search(r'openat\([^\n]*"config.h"[^\n]*= \d+', text):
                compiler_reads.append(path.name)
        require(compiler_reads, "Missing compiler-specific config.h read")
        parsed = (trace_dir / "make-pn.txt").read_text(encoding="utf-8")
        require("main.o: main.c unused.h" in parsed, "Missing parsed faulty declaration")
        for label in ["linux-trace-clean", "linux-strace-build", "linux-make-pn"]:
            require(label in commands, "Missing Linux command record")
        print("PASS: Linux compiler reads config.h: " + ", ".join(compiler_reads))
    else:
        print("NOTE: this run has no Linux trace; consult the separate Linux run")
    print("PASS: " + folder.name + " source SHA, logs, MD/RD outputs, source equality and timestamps")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", help="A1 run directory name (repeatable)")
    args = parser.parse_args()
    runs = [E3 / "work" / name for name in args.run] if args.run else sorted(p for p in (E3 / "work").glob("*-A1-*") if (p / "observations.json").exists())
    require(bool(runs), "No A1 runs found")
    oracle = read(E3 / "expected" / "buildchecker-md-rd.json")
    require(oracle["provenance"] == "MANUAL_EXPECTED", "Artificial oracle must identify its source")
    require({(f["type"], f["target"], f["dependency"]) for f in oracle["findings"]} == {
        ("MISSING", "main.o", "config.h"), ("REDUNDANT", "main.o", "unused.h")}, "Oracle differs from fixture")
    for run in runs:
        require(run.resolve().is_relative_to((E3 / "work").resolve()), "Invalid run path")
        verify(run)
    print("PASS: A1 saved-evidence verification complete")
