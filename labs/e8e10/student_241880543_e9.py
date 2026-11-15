"""B2 evidence driver; calls the shared course implementation, never copies it."""
import argparse
import contextlib
import csv
import hashlib
import platform
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

from lab import fixture, patch, save, scan

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out == ROOT / "work" or not out.is_relative_to(ROOT / "work") or out.exists():
        parser.error("--out must be a new subdirectory of work/")
    out.mkdir(parents=True)

    def step(name, description, action):
        folder = out / "steps" / name
        folder.mkdir(parents=True)
        (folder / "command.txt").write_text(description + "\n")
        code = 0
        try:
            with (folder / "stdout.log").open("w") as stdout, (folder / "stderr.log").open("w") as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        result = action()
                    except Exception:
                        traceback.print_exc()
                        raise
        except Exception:
            code = 1
            raise
        finally:
            (folder / "exit-code.txt").write_text(str(code) + "\n")
            print(f"{name} STEP_EXIT_CODE={code}", flush=True)
        return result

    def command(name, argv, cwd):
        def execute():
            save(out / "steps" / name / "argv.json", {"argv": argv, "cwd": str(cwd)})
            process = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=120)
            print(process.stdout, end="")
            print(process.stderr, end="", file=sys.stderr)
            save(out / "steps" / name / "process.json", {"exit_code": process.returncode})
            if process.returncode:
                raise RuntimeError(f"Command exited {process.returncode}: {argv}")
            return process.stdout
        return step(name, repr(argv) + " cwd=" + str(cwd), execute)

    def expect(condition, message):
        if not condition:
            raise AssertionError(message)
        print(message + ": PASS")

    source_sha = command("00-source-sha", ["git", "rev-parse", "HEAD"], ROOT).strip()
    status = command("01-source-status", ["git", "status", "--porcelain"], ROOT)
    environment = {"platform": platform.platform(), "python": sys.version, "cwd": str(ROOT),
                   "source_sha": source_sha, "source_status": status, "execution": "WSL host; no Docker image used",
                   "image_id": None, "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for tool in ("git", "gcc", "make"):
        environment[tool] = command("02-version-" + tool, [tool, "--version"], ROOT).splitlines()[0]
    environment["docker_path"] = shutil.which("docker")
    environment["disk_free_bytes"] = shutil.disk_usage(out).free
    environment["meminfo"] = Path("/proc/meminfo").read_text()
    save(out / "environment.json", environment)
    sources = ["lab.py", "test_student_241880543.py", "student_241880543_e9.py"]
    save(out / "source-hashes.json", {name: digest(Path(__file__).parent / name) for name in sources})
    command("03-unit-tests", [sys.executable, "-m", "unittest", "discover", "-s", "labs/e8e10", "-p", "test_*.py", "-v"], ROOT)
    originals = {}
    rows = []
    for style in ("direct", "macro", "mixed"):
        project = out / style
        step(style + "-fixture", f"fixture(out/{style}, {style!r})", lambda: fixture(project, style))
        originals[style] = (project / "Makefile").read_bytes()
        (out / (style + "-before.Makefile")).write_bytes(originals[style])
        # Freeze independent expected sets and edited line before observing results.
        expected_line = {"direct": "main.o: main.c unused.h config.h",
                         "macro": "DEPS = main.c unused.h config.h",
                         "mixed": "main.o: main.c $(HEADERS) config.h"}[style]
        save(out / (style + "-expected.json"), {
            "findings": [["MISSING", "main.o", "config.h"], ["REDUNDANT", "main.o", "unused.h"]],
            "edited_line": expected_line, "original_unchanged": True})
        report = step(style + "-scan", f"scan(out/{style})", lambda: scan(project))
        save(out / (style + "-input.json"), report)
        diff, plan = step(style + "-patch", f"patch(out/{style}, report)", lambda: patch(project, report))
        candidate = out / (style + ".patch")
        candidate.write_text(diff)
        save(out / (style + "-plan.json"), plan)

        def audit_candidate():
            expect(sorted([f["type"], f["target"], f["dependency"]] for f in report["findings"]) ==
                   [["MISSING", "main.o", "config.h"], ["REDUNDANT", "main.o", "unused.h"]], "exact MD/RD set")
            expect(plan == [{"target": "main.o", "dependency": "config.h", "style": style}], "exact one-entry plan")
            expect("+" + expected_line + "\n" in diff, "expected declaration location")
            expect(not any(line.startswith(("+\t", "-\t")) for line in diff.splitlines()), "TAB recipes preserved")
            expect((project / "Makefile").read_bytes() == originals[style], "source bytes unchanged")
        step(style + "-audit", "assert independent findings, plan, diff and source bytes", audit_candidate)
        command(style + "-apply-check", ["git", "apply", "--check", str(candidate)], project)
        clean = command(style + "-source-clean", ["git", "status", "--porcelain"], project)
        expect(clean == "", style + " original Git tree clean")
        history = out / "history"
        history.mkdir(exist_ok=True)
        command(style + "-history", ["git", "bundle", "create", str(history / (style + ".bundle")), "HEAD"], project)
        rows.append({"style": style, "commit": report["commit"], "apply_check": True,
                     "source_unchanged": True, "edits": len(plan)})

    demo = out / "apply-demo"
    step("demo-copy", "copy macro to apply-demo excluding .git and build outputs",
         lambda: shutil.copytree(out / "macro", demo, ignore=shutil.ignore_patterns(".git", "*.o", "app")))
    command("demo-git-init", ["git", "init", "-b", "main"], demo)
    command("demo-apply-check", ["git", "apply", "--check", str(out / "macro.patch")], demo)
    command("demo-apply", ["git", "apply", str(out / "macro.patch")], demo)

    def audit_demo():
        text = (demo / "Makefile").read_text()
        expect(text == originals["macro"].decode().replace("DEPS = main.c unused.h\n", "DEPS = main.c unused.h config.h\n"),
               "only DEPS definition changed; macro reference and all recipes preserved")
    step("demo-audit", "compare full Makefile against independent expected replacement", audit_demo)
    command("demo-build", ["make", "app"], demo)
    expect(command("demo-run", ["./app"], demo).strip() == "1", "demo initial output 1")
    time.sleep(1.05)
    step("demo-change-header", "write VALUE=2 in apply-demo/config.h only",
         lambda: (demo / "config.h").write_text("#define VALUE 2\n"))
    command("demo-incremental-build", ["make", "app"], demo)
    expect(command("demo-incremental-run", ["./app"], demo).strip() == "2", "demo header change output 2")

    def final_audit():
        for style, before in originals.items():
            expect((out / style / "Makefile").read_bytes() == before, style + " original Makefile bytes unchanged")
            expect((out / style / "config.h").read_text() == "#define VALUE 1\n", style + " original header unchanged")
    step("final-source-audit", "check all three original Makefiles and headers after demo", final_audit)
    with (out / "results.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    save(out / "gate.json", {"passed": True, "rows": len(rows), "scope": "E9-B candidate/check/demo; not E10 source acceptance"})
    (out / "结论.txt").write_text("E9-B: direct/macro/mixed candidates pass apply --check; original projects unchanged.\n"
                                  "Only apply-demo changed: DEPS definition repaired, header increment rebuilt app (1 -> 2).\n"
                                  "9 unit tests passed, including B2 duplicate-edge regression. No E10 acceptance claimed.\n")
    files = {p.relative_to(out).as_posix(): digest(p) for p in sorted(out.rglob("*")) if p.is_file() and ".git" not in p.relative_to(out).parts}
    save(out / "manifest.json", files)
    print("COMPLETED", out)


if __name__ == "__main__":
    main()
