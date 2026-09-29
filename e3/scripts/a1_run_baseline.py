"""Run A1's isolated MD/RD baseline and retain real command evidence."""

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
FIXTURE = E3 / "fixtures" / "md-rd"
SOURCE_FILES = ["main.c", "config.h", "unused.h", "Makefile", "Makefile.before"]


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fingerprint(path):
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns}


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--make", default=shutil.which("make") or shutil.which("mingw32-make"))
    parser.add_argument("--cc", default=shutil.which("cc") or shutil.which("gcc"))
    parser.add_argument("--source-commit", help="Commit of a verified exported fixture; otherwise use local Git HEAD")
    parser.add_argument("--require-linux-trace", action="store_true")
    args = parser.parse_args()
    if not args.make or not args.cc:
        parser.error("GNU Make and a C compiler are required; use --make and --cc")
    commit = args.source_commit or git("rev-parse", "HEAD")
    if not re.fullmatch(r"[a-fA-F0-9]{40}", commit):
        parser.error("A complete 40-character source commit is required")
    if not args.source_commit and git("diff", "--", "e3/fixtures/md-rd"):
        parser.error("Commit the frozen fixture before recording a new run")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-A1-" + uuid.uuid4().hex[:6]
    work = E3 / "work" / run_id
    work.mkdir(parents=True, exist_ok=False)
    (work / ".gitignore").write_text("/runtime/\n/trace-runtime/\n", encoding="utf-8")
    logs = work / "logs"
    logs.mkdir()
    runtime = work / "runtime"
    shutil.copytree(FIXTURE, runtime)
    commands = []
    observations = {"member": "A1", "run_id": run_id, "source_commit": commit,
                    "observation_type": "ACTUAL_RUN", "behavior_status": "RUNNING",
                    "linux_trace_status": "NOT_RUN", "failures": []}
    source_hashes = {name: fingerprint(FIXTURE / name)["sha256"] for name in SOURCE_FILES}
    dump(work / "source-manifest.json", {"commit": commit, "fixture": "e3/fixtures/md-rd",
                                         "sha256": source_hashes})

    def run(label, argv, cwd=runtime, required=True):
        start = datetime.now(timezone.utc).isoformat()
        tic = time.monotonic()
        result = subprocess.run([str(a) for a in argv], cwd=cwd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=120)
        stdout_path = logs / (label + ".stdout.log")
        stderr_path = logs / (label + ".stderr.log")
        stdout_path.write_bytes(result.stdout)
        stderr_path.write_bytes(result.stderr)
        record = {"id": label, "argv": [str(a) for a in argv], "cwd": str(cwd),
                  "source_commit": commit, "started_at": start,
                  "duration_seconds": round(time.monotonic() - tic, 4),
                  "exit_code": result.returncode,
                  "stdout": stdout_path.relative_to(work).as_posix(),
                  "stderr": stderr_path.relative_to(work).as_posix()}
        commands.append(record)
        dump(work / "commands.json", commands)
        if required and result.returncode:
            raise RuntimeError(f"{label} exited {result.returncode}; see {stderr_path}")
        return result.stdout.decode("utf-8", errors="replace"), result.returncode

    def check(condition, message):
        if not condition:
            raise RuntimeError(message)

    def snapshot(label):
        folder = work / "snapshots" / label
        folder.mkdir(parents=True)
        for name in SOURCE_FILES:
            shutil.copy2(runtime / name, folder / name)
        state = {name: fingerprint(runtime / name) for name in SOURCE_FILES}
        for name in ["main.o", "app", "app.exe"]:
            if (runtime / name).is_file():
                state[name] = fingerprint(runtime / name)
        dump(folder / "state.json", state)
        return state

    # Forward slashes keep command-line make variables usable on Windows.
    make = [args.make, "CC=" + Path(args.cc).as_posix(), "PYTHON=" + Path(sys.executable).as_posix()]
    app = runtime / ("app.exe" if os.name == "nt" else "app")
    try:
        versions = {}
        for label, argv in [("git", ["git", "--version"]), ("make", [args.make, "--version"]),
                            ("cc", [args.cc, "--version"]), ("python", [sys.executable, "--version"])]:
            versions[label], _ = run("env-" + label, argv, cwd=REPO)
        trace_executable = shutil.which("strace")
        if platform.system() == "Linux" and trace_executable:
            versions["strace"], _ = run("env-strace", [trace_executable, "--version"], cwd=REPO)
        else:
            versions["strace"] = "NOT_AVAILABLE: Linux strace must be run in a Linux environment"
        environment = {"member": "A1", "run_id": run_id, "source_commit": commit,
                       "system": platform.system(), "os": platform.platform(),
                       "architecture": platform.machine(), "versions": versions,
                       "make": args.make, "cc": args.cc, "cflags": "-O0 -Wall -Wextra",
                       "configuration_id": "a1-" + platform.system().lower() + "-gcc-default",
                       "scope": "main.o, project headers only"}
        dump(work / "environment.json", environment)
        env_dir = E3 / "env"
        env_dir.mkdir(exist_ok=True)
        (env_dir / "toolchain-A1.txt").write_text(json.dumps(environment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        run("md-rd-clean", make)
        initial_output, _ = run("md-rd-clean-run", [app])
        check(initial_output.strip() == "1", "Initial program output must be 1")
        initial = snapshot("01-initial-value1")
        original_object = fingerprint(runtime / "main.o")

        time.sleep(1.1)
        config = runtime / "config.h"
        config.write_text(config.read_text(encoding="utf-8").replace("VALUE 1", "VALUE 2"), encoding="utf-8")
        check(config.stat().st_mtime_ns > (runtime / "main.o").stat().st_mtime_ns, "Header mtime must be newer than object")
        before_md = snapshot("02-header-value2-before-make")
        run("md-rd-touch-header", make)
        stale_output, _ = run("md-rd-touch-header-run", [app])
        stale = snapshot("03-stale-after-incremental")
        check(stale_output.strip() == "1", "MD incremental output must remain 1")
        check(original_object == fingerprint(runtime / "main.o"), "MD should leave main.o unchanged")

        run("md-rd-clean-rebuild-clean", make + ["clean"])
        run("md-rd-clean-rebuild", make)
        fresh_output, _ = run("md-rd-clean-rebuild-run", [app])
        fresh = snapshot("04-clean-value2")
        check(fresh_output.strip() == "2", "Clean rebuild output must be 2")
        check(stale["config.h"]["sha256"] == fresh["config.h"]["sha256"], "MD comparison must keep source identical")

        object_before_rd = fingerprint(runtime / "main.o")
        time.sleep(1.1)
        (runtime / "unused.h").write_text("/* still unused: comment changed only */\n", encoding="utf-8")
        check((runtime / "unused.h").stat().st_mtime_ns > (runtime / "main.o").stat().st_mtime_ns, "unused.h must be newer than object")
        snapshot("05-unused-comment-before-make")
        rd_log, _ = run("md-rd-redundant", make)
        rd_output, _ = run("md-rd-redundant-run", [app])
        rd = snapshot("06-redundant-after-make")
        check("-c main.c -o main.o" in rd_log, "RD must execute compile recipe")
        check("main.o -o app" in rd_log, "RD must execute link recipe")
        check((runtime / "main.o").stat().st_mtime_ns > object_before_rd["mtime_ns"], "RD must regenerate main.o")
        check(rd_output.strip() == "2", "RD must preserve functional output 2")
        observations.update(behavior_status="PASSED", initial_output=initial_output.strip(),
                            md_incremental_output=stale_output.strip(), clean_rebuild_output=fresh_output.strip(),
                            rd_output=rd_output.strip(), md_object_unchanged=True, rd_recompiled=True,
                            source_comparison="Same VALUE=2 sources before and after clean build")

        if platform.system() == "Linux" and trace_executable:
            trace_dir = E3 / "evidence" / "linux-verified" / run_id
            trace_dir.mkdir(parents=True, exist_ok=False)
            trace_runtime = work / "trace-runtime"
            shutil.copytree(FIXTURE, trace_runtime)
            run("linux-trace-clean", make + ["clean"], cwd=trace_runtime)
            run("linux-strace-build", [trace_executable, "-ff", "-o", trace_dir / "trace.log",
                                      "-e", "trace=%file,%process", *make], cwd=trace_runtime)
            parsed, _ = run("linux-make-pn", make + ["-pn"], cwd=trace_runtime)
            (trace_dir / "make-pn.txt").write_text(parsed, encoding="utf-8")
            excerpts = []
            processes = []
            for trace in sorted(trace_dir.glob("trace.log.*")):
                for line in trace.read_text(encoding="utf-8", errors="replace").splitlines():
                    if "config.h" in line or "unused.h" in line:
                        excerpts.append(trace.name + ": " + line)
                    if "execve(" in line or "clone(" in line or "vfork(" in line:
                        processes.append(trace.name + ": " + line)
            check(any('"config.h"' in line and "openat(" in line for line in excerpts), "Trace must include config.h openat")
            check("main.o: main.c unused.h" in parsed, "Parsed declaration must show missing config.h")
            (trace_dir / "config-h-access.txt").write_text("\n".join(excerpts) + "\n", encoding="utf-8")
            (trace_dir / "processes.txt").write_text("\n".join(processes) + "\n", encoding="utf-8")
            dump(trace_dir / "source-manifest.json", {"commit": commit, "sha256": source_hashes})
            dump(trace_dir / "environment.json", environment)
            dump(trace_dir / "command-links.json", {"work": "e3/work/" + run_id,
                                                       "commands": ["linux-trace-clean", "linux-strace-build", "linux-make-pn"]})
            (trace_dir / "README.md").write_text(
                "# A1 Linux 原始跟踪\n\n实测命令与退出码见本轮 work/commands.json。\n"
                "config-h-access.txt 提供带进程文件名的摘录，processes.txt 提供进程身份线索。\n"
                "只看到 openat 还不足以直接判 MD；本阶段保留原始证据，构图与归一化留给后续 BuildChecker。\n",
                encoding="utf-8")
            observations.update(linux_trace_status="PASSED", linux_evidence=trace_dir.relative_to(REPO).as_posix())
        else:
            observations["linux_trace_reason"] = "Linux/strace unavailable in this run; not replaced by Windows evidence"
        print("BEHAVIOR_STATUS=" + observations["behavior_status"])
        print("LINUX_TRACE_STATUS=" + observations["linux_trace_status"])
        print("EVIDENCE_DIR=" + str(work))
    except Exception as error:
        observations["failures"].append(str(error))
        if observations["behavior_status"] == "RUNNING":
            observations["behavior_status"] = "FAILED"
        dump(work / "observations.json", observations)
        print("EVIDENCE_DIR=" + str(work))
        raise
    finally:
        dump(work / "commands.json", commands)
        dump(work / "observations.json", observations)
    return 0 if not args.require_linux_trace or observations["linux_trace_status"] == "PASSED" else 3


if __name__ == "__main__":
    sys.exit(main())
