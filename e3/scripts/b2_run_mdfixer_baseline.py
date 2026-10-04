"""Run B2's manual MDFixer baseline in isolated copies and retain raw evidence."""

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import uuid

E3 = Path(__file__).resolve().parents[1]
REPO = E3.parent
FIXTURE = E3 / "fixtures" / "mdfixer"
STYLES = ("target", "macro", "hybrid", "implicit")
SOURCE = ("main.c", "config.h", "unused.h")


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def fingerprint(path):
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "mtime_ns": path.stat().st_mtime_ns}


def architecture():
    value = platform.machine()
    if not value and os.name == "nt":
        # A minimal process environment may omit PROCESSOR_ARCHITECTURE.
        # SYSTEM_INFO starts with a WORD architecture; the native API supplies
        # the OS architecture independently of those environment variables.
        import ctypes
        info = ctypes.create_string_buffer(64)
        ctypes.windll.kernel32.GetNativeSystemInfo(ctypes.byref(info))
        value = {0: "x86", 9: "AMD64", 12: "ARM64"}.get(ctypes.c_ushort.from_buffer(info).value, "UNKNOWN")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--make", default=shutil.which("make") or shutil.which("mingw32-make"))
    parser.add_argument("--cc", default=shutil.which("cc") or shutil.which("gcc"))
    args = parser.parse_args()
    if not args.make or not args.cc:
        parser.error("GNU Make and GCC/Clang are required; use --make and --cc")
    base_commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    # HEAD is contextual, not a claim that new/uncommitted fixture bytes exist in it.
    dirty = subprocess.check_output(["git", "-C", str(REPO), "status", "--porcelain", "--",
                                     "e3/fixtures/mdfixer"], text=True).strip()
    run_id = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S") + "-B2-" + uuid.uuid4().hex[:6]
    work = E3 / "work" / run_id
    work.mkdir(parents=True, exist_ok=False)
    (work / ".gitignore").write_bytes(b"/runtime/\n")
    (work / ".gitattributes").write_bytes(b"* -text\n")
    logs = work / "logs"
    logs.mkdir()
    frozen = work / "inputs"
    shutil.copytree(FIXTURE, frozen)
    manifest = {p.relative_to(frozen).as_posix(): fingerprint(p)["sha256"]
                for p in sorted(frozen.rglob("*")) if p.is_file()}
    dump(work / "source-manifest.json", {"base_commit": base_commit,
         "fixture_version": "WORKING_TREE_SNAPSHOT" if dirty else "COMMITTED_FIXTURE",
         "fixture_git_status": dirty, "sha256": manifest,
         "note": "Input hashes identify exact bytes; base_commit alone does not identify an uncommitted fixture."})
    commands = []
    obs = {"member": "B2", "run_id": run_id, "source_commit": base_commit,
           "observation_type": "ACTUAL_RUN", "status": "RUNNING", "styles": {}, "failures": [],
           "scope": "Manual reference-patch behavior only; no MDFixer service or detector executed."}
    environment = {"member": "B2", "run_id": run_id, "os": platform.platform(),
                   "system": platform.system(), "architecture": architecture(),
                   "configuration_id": "b2-gcc-O0-project-headers", "versions": {},
                   "make": args.make, "cc": args.cc, "cflags": "-O0 -Wall -Wextra"}
    make = [args.make, "CC=" + Path(args.cc).as_posix(), "PYTHON=" + Path(sys.executable).as_posix()]

    def check(condition, message):
        if not condition:
            raise RuntimeError(message)

    def run(label, argv, cwd=REPO, allow_failure=False):
        start = datetime.now(timezone.utc).isoformat()
        tic = time.monotonic()
        argv = [str(a) for a in argv]
        try:
            result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=120)
            stdout, stderr, code = result.stdout, result.stderr, result.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            stdout = getattr(exc, "stdout", None) or b""
            stderr = (getattr(exc, "stderr", None) or b"") + str(exc).encode()
            code = 124 if isinstance(exc, subprocess.TimeoutExpired) else 127
        out, err = logs / (label + ".stdout.log"), logs / (label + ".stderr.log")
        out.write_bytes(stdout)
        err.write_bytes(stderr)
        commands.append({"id": label, "argv": argv, "cwd": str(cwd), "source_commit": base_commit,
                         "started_at": start, "duration_seconds": round(time.monotonic() - tic, 4),
                         "exit_code": code, "stdout": out.relative_to(work).as_posix(),
                         "stderr": err.relative_to(work).as_posix(),
                         "stdout_sha256": fingerprint(out)["sha256"], "stderr_sha256": fingerprint(err)["sha256"]})
        dump(work / "commands.json", commands)
        check(allow_failure or code == 0, f"{label}: exit {code}; see logs")
        return stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace"), code

    def prepare(style, name=None):
        folder = work / "runtime" / (name or style)
        folder.mkdir(parents=True)
        (folder / ".gitattributes").write_bytes(b"* text eol=lf\n")
        for file in SOURCE:
            shutil.copy2(frozen / file, folder / file)
        for source, destination in (("Makefile.before", "Makefile"), ("reference.patch", "reference.patch")):
            shutil.copy2(frozen / "styles" / style / source, folder / destination)
        # A private Git root prevents git apply from prefixing paths with runtime's
        # location inside the outer project. No project index is changed.
        run((name or style) + "-git-init", ["git", "init", "--quiet", "."], folder)
        return folder

    def snapshot(folder, label):
        dest = work / "snapshots" / label
        dest.mkdir(parents=True)
        names = [*SOURCE, "Makefile", "reference.patch", "main.d", "invalid-candidate.patch"]
        state = {}
        for file in [*names, "main.o", "app", "app.exe"]:
            path = folder / file
            if path.is_file():
                state[file] = fingerprint(path)
                if file in names:
                    shutil.copy2(path, dest / file)
        dump(dest / "state.json", state)
        return state

    def header(folder, value):
        obj = folder / "main.o"
        # Let real time advance before writing; do not leave future timestamps
        # that would make every subsequent Make invocation rebuild.
        time.sleep(1.1)
        path = folder / "config.h"
        path.write_bytes(("#ifndef CONFIG_H\n#define CONFIG_H\n#define VALUE " + str(value) + "\n#endif\n").encode())
        check(path.stat().st_mtime_ns > obj.stat().st_mtime_ns, "Header must be newer than main.o")

    def output(label, folder, expected):
        app = folder / ("app.exe" if os.name == "nt" else "app")
        value, _, _ = run(label, [app], folder)
        check(value.strip() == expected, f"{label}: expected {expected!r}, got {value!r}")
        return value.strip()

    def verify_rebuild(label, folder, expected, old_state):
        text, _, _ = run(label + "-build", make, folder)
        value = output(label + "-run", folder, expected)
        state = snapshot(folder, label)
        check("-c main.c -o main.o" in text, f"{label}: compiler recipe did not run")
        check(state["main.o"]["mtime_ns"] > old_state["main.o"]["mtime_ns"], f"{label}: object not regenerated")
        check(state["main.o"]["sha256"] != old_state["main.o"]["sha256"], f"{label}: object bytes not changed")
        return value, state

    try:
        for name, argv in (("git", ["git", "--version"]), ("make", [args.make, "--version"]),
                           ("cc", [args.cc, "--version"]), ("python", [sys.executable, "--version"])):
            environment["versions"][name], _, _ = run("env-" + name, argv)
        dump(work / "environment.json", environment)
        for style in STYLES:
            folder = prepare(style)
            report = json.loads((frozen / "styles" / style / "md-report.json").read_text(encoding="utf-8"))
            check({f["type"] for f in report["findings"]} == {"MISSING"}, "Only MISSING findings may be consumed")
            for name, sha in report["input_sha256"].items():
                path = frozen / name if name in SOURCE else frozen / "styles" / style / name
                check(fingerprint(path)["sha256"] == sha, f"{style}: report input mismatch: {name}")
            check(not (folder / "main.d").exists(), "Initial .d must be absent")
            run(style + "-initial-build", make, folder)
            first = output(style + "-initial-run", folder, "1")
            initial = snapshot(folder, style + "-initial")
            header(folder, 2)
            snapshot(folder, style + "-header2-before-make")
            run(style + "-stale-build", make, folder)
            stale = output(style + "-stale-run", folder, "1")
            stale_state = snapshot(folder, style + "-stale")
            check(stale_state["main.o"] == initial["main.o"], "Original Makefile must leave the object unchanged")
            run(style + "-before-patch-clean", make + ["clean"], folder)
            run(style + "-patch-check", ["git", "apply", "--check", "reference.patch"], folder)
            run(style + "-patch-apply", ["git", "apply", "reference.patch"], folder)
            check((folder / "Makefile").read_bytes() == (frozen / "styles" / style / "Makefile.reference").read_bytes(), "Patch differs from reference Makefile")
            run(style + "-patched-clean", make + ["clean"], folder)
            check(not (folder / "main.d").exists(), "Clean must remove .d")
            run(style + "-patched-build", make, folder)
            clean_value = output(style + "-patched-run", folder, "2")
            fixed = snapshot(folder, style + "-patched")
            check(fixed["config.h"]["sha256"] == stale_state["config.h"]["sha256"], "Clean comparison changed the source")
            if style == "implicit":
                depfile = (folder / "main.d").read_bytes()
                check(b"main.o: main.c config.h" in depfile and b"config.h:" in depfile, "Unexpected generated .d")
                (work / "implicit-main.d").write_bytes(depfile)
            header(folder, 3)
            snapshot(folder, style + "-header3-before-make")
            incremental, next_state = verify_rebuild(style + "-incremental3", folder, "3", fixed)
            # A second edit and an unchanged rebuild guard against one-time or
            # unconditional rebuilding masquerading as a dependency repair.
            header(folder, 4)
            snapshot(folder, style + "-header4-before-make")
            second, last = verify_rebuild(style + "-incremental4", folder, "4", next_state)
            run(style + "-noop-build", make, folder)
            output(style + "-noop-run", folder, "4")
            noop = snapshot(folder, style + "-noop")
            check(noop["main.o"] == last["main.o"], "Unchanged build must not recompile")
            obs["styles"][style] = {"status": "PASSED", "initial_output": first, "stale_output": stale,
                "patched_clean_output": clean_value, "incremental3_output": incremental,
                "incremental4_output": second, "stale_object_unchanged": True, "incremental_recompiled": True,
                "noop_object_unchanged": True, "redundant_declaration_preserved": "unused.h"}
            dump(work / "observations.json", obs)

        folder = prepare("target", "rejection")
        original = (folder / "Makefile").read_bytes()
        run("rejection-original-build", make, folder)
        output("rejection-original-run", folder, "1")
        snapshot(folder, "rejection-original")
        shutil.copy2(frozen / "invalid-candidate.patch", folder / "invalid-candidate.patch")
        accepted = False
        try:
            run("rejection-patch-check", ["git", "apply", "--check", "invalid-candidate.patch"], folder)
            run("rejection-patch-apply", ["git", "apply", "invalid-candidate.patch"], folder)
            run("rejection-candidate-clean", make + ["clean"], folder)
            _, failure, exit_code = run("rejection-candidate-build", make, folder, allow_failure=True)
            snapshot(folder, "rejection-failed")
            check(exit_code != 0 and "B2_INVALID_CANDIDATE" in failure, "Candidate must fail for the injected reason")
        finally:
            # Restore exact bytes even if validation unexpectedly fails.
            (folder / "Makefile").write_bytes(original)
            run("rejection-restored-clean", make + ["clean"], folder)
            run("rejection-restored-build", make, folder)
            restored_output = output("rejection-restored-run", folder, "1")
            restored = snapshot(folder, "rejection-restored")
            check((folder / "Makefile").read_bytes() == original, "Recovery must restore the original Makefile")
        obs["rejection"] = {"candidate_accepted": accepted, "candidate_exit_code": exit_code,
                            "reason": "B2_INVALID_CANDIDATE", "restored_exact_bytes": True,
                            "restored_output": restored_output,
                            "restored_makefile_sha256": restored["Makefile"]["sha256"],
                            "note": "Restored baseline is buildable; its original MD is intentionally retained."}
        obs["status"] = "PASSED"
    except Exception as exc:
        obs["status"] = "FAILED"
        obs["failures"].append(str(exc))
        print(str(exc), file=sys.stderr)
    finally:
        dump(work / "observations.json", obs)
        dump(work / "environment.json", environment)
        dump(E3 / "env" / "toolchain-B2.txt", environment)
    print("EVIDENCE_DIR=" + work.relative_to(REPO).as_posix())
    print("STATUS=" + obs["status"])
    return 0 if obs["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
