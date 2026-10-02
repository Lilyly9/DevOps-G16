"""Run A2's EChecker increment baseline over the frozen C0/C1/C2 fixtures.

The script never modifies Git. For every version it verifies that the snapshot
under ``e3/fixtures/commits/<tag>/`` is byte-identical to the tagged commit
(the snapshot bytes must reproduce the blob id recorded by the commit), then
runs the real GNU Make behaviour in isolated runtime copies and keeps the raw
logs, exit codes and file fingerprints under ``e3/work/<run-id>/``.

    python e3/scripts/a2_run_echecker_baseline.py --make <make> --cc <cc> --python <python>

Expected observations (see e3/expected/echecker-c0-c1-c2.md):
    C0 clean build                          -> 10
    C1 incremental on top of C0 artifacts   -> 12
    C1, only feature.h edited afterwards    -> still 12 (missing dependency: no rebuild)
    C1 clean rebuild after that edit        -> 13 (proves the value was stale)
    C2 incremental on top of C1 artifacts   -> 12 (only CFLAGS changed)
    C2 clean build                          -> 19
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid

E3 = Path(__file__).resolve().parents[1]
REPO = E3.parent
FIXTURES = E3 / "fixtures" / "commits"
TAGS = ["C0", "C1", "C2"]
LAB = "e3/fixtures/commits/lab"
SOURCE_FILES = ["main.c", "config.h", "feature.h", "Makefile"]


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def blob_id(data):
    """Git object id of a blob, i.e. sha1("blob <len>\\0" + content)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def fingerprint(path):
    data = Path(path).read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "mtime_ns": Path(path).stat().st_mtime_ns}


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--make", default=shutil.which("make") or shutil.which("mingw32-make"))
    parser.add_argument("--cc", default=shutil.which("cc") or shutil.which("gcc"))
    parser.add_argument("--python", default=shutil.which("python3") or shutil.which("python"))
    args = parser.parse_args()
    if not (args.make and args.cc and args.python):
        parser.error("GNU Make, a C compiler and Python are required; use --make/--cc/--python")

    # The snapshot must describe the commit that is being tested.
    metadata = json.loads((FIXTURES / "versions.json").read_text(encoding="utf-8"))
    versions, commits = {}, {}
    for tag in TAGS:
        commit = git("rev-parse", tag + "^{commit}")
        commits[tag] = commit
        if metadata["tags"][tag]["commit"] != commit:
            raise RuntimeError("%s moved: fixture metadata says %s, Git says %s"
                               % (tag, metadata["tags"][tag]["commit"], commit))
        versions[tag] = {}
        for name, info in metadata["tags"][tag]["files"].items():
            data = (FIXTURES / tag / name).read_bytes()
            if blob_id(data) != info["git_blob_sha1"]:
                raise RuntimeError("%s/%s does not match tag %s" % (tag, name, tag))
            if git("rev-parse", "%s:%s/%s" % (tag, LAB, name)) != info["git_blob_sha1"]:
                raise RuntimeError("%s/%s blob differs from Git" % (tag, name))
            versions[tag][name] = data

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-A2-" + uuid.uuid4().hex[:6]
    work = E3 / "work" / run_id
    work.mkdir(parents=True, exist_ok=False)
    (work / ".gitignore").write_text("/runtime/\n", encoding="utf-8")
    (work / ".gitattributes").write_text("* -text\n", encoding="utf-8")
    logs = work / "logs"
    logs.mkdir()
    runtime = work / "runtime"
    runtime.mkdir()

    commands, failures = [], []
    observations = {"member": "A2", "run_id": run_id, "observation_type": "ACTUAL_RUN",
                    "task": "EChecker C0/C1/C2 increment baseline",
                    "status": "RUNNING", "fixture": "e3/fixtures/commits",
                    "commits": commits, "failures": failures}

    def record(label, argv, cwd, required=True):
        """Run one command, keep both streams and the real exit code."""
        tic = time.monotonic()
        result = subprocess.run([str(a) for a in argv], cwd=str(cwd), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=180)
        out_path, err_path = logs / (label + ".stdout.log"), logs / (label + ".stderr.log")
        out_path.write_bytes(result.stdout)
        err_path.write_bytes(result.stderr)
        commands.append({"id": label, "argv": [str(a) for a in argv], "cwd": str(cwd),
                         "started_at": datetime.now(timezone.utc).isoformat(),
                         "duration_seconds": round(time.monotonic() - tic, 4),
                         "exit_code": result.returncode,
                         "stdout": out_path.relative_to(work).as_posix(),
                         "stderr": err_path.relative_to(work).as_posix()})
        dump(work / "commands.json", commands)
        if required and result.returncode:
            raise RuntimeError("%s exited %d; see %s" % (label, result.returncode, err_path))
        return result.stdout.decode("utf-8", errors="replace")

    def check(condition, message):
        if not condition:
            failures.append(message)
            raise RuntimeError(message)

    def snapshot(label, folder):
        target = work / "snapshots" / label
        target.mkdir(parents=True, exist_ok=True)
        state = {}
        for item in sorted(Path(folder).iterdir()):
            if item.is_file():
                state[item.name] = fingerprint(item)
        for name in SOURCE_FILES:
            if name in state:
                shutil.copy2(Path(folder) / name, target / name)
        states[label] = state
        dump(work / "snapshots" / label / "state.json", state)
        return state

    states = {}
    app_name = "app.exe" if os.name == "nt" else "app"

    # Forward slashes keep the command line usable from sh on Windows.
    make = [args.make, "CC=" + Path(args.cc).as_posix(), "PYTHON=" + Path(args.python).as_posix()]
    versions_dir = runtime

    def fresh(tag):
        folder = versions_dir / tag
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        for name, data in versions[tag].items():
            (folder / name).write_bytes(data)
        return folder

    def overlay(folder, tag, names):
        """Apply only the files a real `git checkout` would change for that tag."""
        for name in names:
            (folder / name).write_bytes(versions[tag][name])

    def changed_files(old, new):
        out = git("diff", "--name-only", old, new, "--", LAB)
        return sorted(Path(line).name for line in out.splitlines() if line)

    def declared(folder, label):
        text = record(label, make + ["-pn"], folder)
        kept = [line for line in text.splitlines() if line.startswith("main.o:")]
        (logs / (label + ".declared.txt")).write_text("\n".join(kept) + "\n", encoding="utf-8")
        return "\n".join(kept)

    def version_of(label, argv):
        record("env-" + label, argv, REPO, required=False)
        entry = commands[-1]
        parts = [(work / entry["stdout"]).read_text(encoding="utf-8", errors="replace"),
                 (work / entry["stderr"]).read_text(encoding="utf-8", errors="replace")]
        return "".join(p for p in parts if p).strip()

    try:
        toolchain = {}
        for label, argv in [("git", ["git", "--version"]), ("make", [args.make, "--version"]),
                            ("cc", [args.cc, "--version"]), ("python", [args.python, "--version"])]:
            toolchain[label] = version_of(label, argv)
        toolchain["make_path"], toolchain["cc_path"], toolchain["python_path"] = \
            args.make, args.cc, args.python
        dump(work / "environment.json", {
            "member": "A2", "run_id": run_id, "system": platform.system(),
            "os": platform.platform(), "architecture": platform.machine(),
            "versions": toolchain, "configuration_id": "a2-" + platform.system().lower() + "-gcc-default",
            "scope": "main.o and project headers of e3/fixtures/commits/lab"})
        (E3 / "env").mkdir(exist_ok=True)
        (E3 / "env" / "toolchain-A2.txt").write_text(json.dumps({
            "member": "A2", "run_id": run_id, "system": platform.system(),
            "os": platform.platform(), "architecture": platform.machine(),
            "versions": toolchain, "compile_flags": "-O0 (C0/C1), -O0 -DMODE=7 (C2)",
            "configuration_id": "a2-" + platform.system().lower() + "-gcc-default",
            "scope": "main.o and project headers of e3/fixtures/commits/lab"},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # ---- C0: declared correctly, clean build must print 10 --------------
        c0 = fresh("C0")
        record("c0-clean", make + ["clean"], c0)
        record("c0-build", make, c0)
        out = record("c0-run", [c0 / app_name], c0).strip()
        check(out == "10", "C0 clean build output must be 10, got %r" % out)
        c0_initial = fingerprint(c0 / "main.o")
        snapshot("01-C0-clean", c0)
        c0_command = record("c0-main-o-command", make + ["-n", "-B", "main.o"], c0)
        declared(c0, "c0-make-pn")
        check("-O0" in c0_command and "DMODE" not in c0_command,
              "C0 command snapshot must compile with -O0 only")

        # ---- C1 incremental: main.c changed, so this version rebuilds ------
        c0_to_c1 = changed_files("C0", "C1")
        check(c0_to_c1 == ["feature.h", "main.c"],
              "C0 -> C1 must only add feature.h and change main.c, got %r" % c0_to_c1)
        time.sleep(1.1)
        overlay(c0, "C1", c0_to_c1)
        c1_log = record("c1-incremental", make, c0)
        out = record("c1-incremental-run", [c0 / app_name], c0).strip()
        check(out == "12", "C1 incremental output must be 12, got %r" % out)
        check("-c main.c" in c1_log, "C1 incremental must recompile main.o because main.c changed")
        check(fingerprint(c0 / "main.o")["mtime_ns"] > c0_initial["mtime_ns"],
              "C1 incremental must regenerate main.o")
        snapshot("02-C1-incremental-from-C0", c0)
        c1_command = record("c1-main-o-command", make + ["-n", "-B", "main.o"], c0)
        check(c1_command == c0_command, "C0 and C1 compile commands must be identical")
        c1_declared = declared(c0, "c1-make-pn")
        check("main.o: main.c config.h" in c1_declared,
              "C1 declaration must still be main.o: main.c config.h (feature.h is missing)")

        # ---- C1 missing dependency: edit only feature.h ---------------------
        time.sleep(1.1)
        feature = c0 / "feature.h"
        feature.write_bytes(feature.read_bytes().replace(b"#define FEATURE 2", b"#define FEATURE 3"))
        check(feature.stat().st_mtime_ns > (c0 / "main.o").stat().st_mtime_ns,
              "feature.h must be newer than the stale main.o")
        object_before = fingerprint(c0 / "main.o")
        stale_log = record("c1-touch-feature", make, c0)
        out = record("c1-touch-feature-run", [c0 / app_name], c0).strip()
        check("-c main.c" not in stale_log,
              "missing dependency: editing feature.h must NOT recompile main.o")
        check(fingerprint(c0 / "main.o") == object_before,
              "missing dependency: main.o must stay untouched")
        check(out == "12", "stale program must keep printing the old value 12, got %r" % out)
        snapshot("03-C1-stale-after-feature-edit", c0)
        record("c1-clean-rebuild-clean", make + ["clean"], c0)
        record("c1-clean-rebuild", make, c0)
        out = record("c1-clean-rebuild-run", [c0 / app_name], c0).strip()
        check(out == "13", "C1 clean rebuild must pick up FEATURE 3 and print 13, got %r" % out)
        snapshot("04-C1-clean-rebuild-feature3", c0)

        # ---- C2 incremental: only the compile command changed ---------------
        c2 = fresh("C1")
        record("c2-c1-baseline-clean", make + ["clean"], c2)
        record("c2-c1-baseline-build", make, c2)
        out = record("c2-c1-baseline-run", [c2 / app_name], c2).strip()
        check(out == "12", "C1 baseline inside the C2 runtime must print 12, got %r" % out)
        object_before = fingerprint(c2 / "main.o")
        c1_to_c2 = changed_files("C1", "C2")
        check(c1_to_c2 == ["Makefile"], "C2 must only change the Makefile, got %r" % c1_to_c2)
        time.sleep(1.1)
        overlay(c2, "C2", c1_to_c2)
        c2_log = record("c2-incremental", make, c2)
        out = record("c2-incremental-run", [c2 / app_name], c2).strip()
        check(out == "12", "C2 incremental output must stay 12, got %r" % out)
        check(fingerprint(c2 / "main.o") == object_before and "-c main.c" not in c2_log,
              "C2 incremental must not rebuild main.o although the command changed")
        snapshot("05-C2-incremental-reusing-C1", c2)
        c2_command = record("c2-main-o-command", make + ["-n", "-B", "main.o"], c2)
        check("DMODE=7" in c2_command and c2_command != c1_command,
              "C2 command snapshot must show -DMODE=7 and differ from C1")
        declared(c2, "c2-make-pn")
        record("c2-clean-rebuild-clean", make + ["clean"], c2)
        record("c2-clean-rebuild", make, c2)
        out = record("c2-clean-rebuild-run", [c2 / app_name], c2).strip()
        check(out == "19", "C2 clean build must print BASE+FEATURE+MODE = 19, got %r" % out)
        snapshot("06-C2-clean", c2)

        observations.update({
            "status": "PASSED",
            "c0_clean_output": "10",
            "c1_incremental_output": "12",
            "c1_stale_output_after_feature_edit": "12",
            "c1_clean_rebuild_output": "13",
            "c2_incremental_output": "12",
            "c2_clean_output": "19",
            "expected_findings": [
                {"version": "C0", "finding": "none in this project scope",
                 "basis": "main.o declares main.c and config.h, the only project header main.c reads"},
                {"version": "C1", "finding": "MISSING main.o -> feature.h",
                 "basis": "main.c line 4 includes feature.h but the rule stays 'main.o: main.c config.h'; "
                          "editing feature.h does not recompile (12) while a clean build prints 13"},
                {"version": "C2", "finding": "MISSING main.o -> feature.h still present",
                 "basis": "C2 only changes CFLAGS; incremental build reuses the C1 object and prints 12, "
                          "clean build prints 19"}],
            "command_change": {"c0_equals_c1": True, "c2_differs": True,
                               "c1_command": c1_command.strip().splitlines()[-1],
                               "c2_command": c2_command.strip().splitlines()[-1],
                               "conclusion": "the compile command change is invisible to plain make; "
                                             "only `make -n -B main.o` and the clean build expose it"},
            "snapshots": sorted(states),
        })
        print("STATUS=" + observations["status"])
        print("EVIDENCE_DIR=" + str(work))
        return 0
    except Exception as error:
        if "status" in observations and observations["status"] == "RUNNING":
            observations["status"] = "FAILED"
        dump(work / "observations.json", observations)
        print("EVIDENCE_DIR=" + str(work))
        raise
    finally:
        dump(work / "commands.json", commands)
        dump(work / "observations.json", observations)


if __name__ == "__main__":
    sys.exit(main())
