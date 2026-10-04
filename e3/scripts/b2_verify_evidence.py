"""Verify B2 frozen inputs, patch transformations and saved behavior evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

STYLES = ("target", "macro", "hybrid", "implicit")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run", help="A B2 run directory name; defaults to all saved B2 runs")
    args = parser.parse_args()
    root = args.root.resolve()
    fixture = root / "e3/fixtures/mdfixer"
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)
        return bool(condition)

    def read(path):
        return json.loads(path.read_text(encoding="utf-8"))

    def local(folder, relative):
        require(isinstance(relative, str) and bool(relative), "Missing file reference")
        path = (folder / relative).resolve()
        if not path.is_relative_to(folder.resolve()) or not path.is_file():
            raise ValueError(f"Missing/unsafe path: {path}")
        return path

    def apply(before, patch):
        with tempfile.TemporaryDirectory(prefix="e3-b2-check-") as name:
            folder = Path(name)
            (folder / ".gitattributes").write_bytes(b"* text eol=lf\n")
            (folder / "Makefile").write_bytes(before.read_bytes())
            for argv in (["git", "init", "--quiet", "."],
                         ["git", "apply", "--check", str(patch.resolve())],
                         ["git", "apply", str(patch.resolve())]):
                result = subprocess.run(argv, cwd=folder, capture_output=True)
                if result.returncode:
                    raise ValueError("Patch check failed: " + result.stderr.decode(errors="replace"))
            return (folder / "Makefile").read_bytes()

    def verify_inputs(folder):
        require((folder / "Makefile").read_bytes() == (folder / "Makefile.before").read_bytes(), "Root Makefile must be original")
        for name in ("Makefile.before", "reference.patch", "md-report.json"):
            require((folder / name).read_bytes() == (folder / "styles/target" / name).read_bytes(), f"Root target mismatch: {name}")
        for style in STYLES:
            directory = folder / "styles" / style
            report = read(directory / "md-report.json")
            require(report["provenance"] == "MANUAL_EXPECTED" and bool(report["source"]), f"{style}: invalid provenance")
            require(report["configuration_id"] == "b2-gcc-O0-project-headers" and report["style"] == style, f"{style}: report context mismatch")
            require([(f["type"], f["target"], f["dependency"]) for f in report["findings"]] == [("MISSING", "main.o", "config.h")], f"{style}: must consume only the fixed MD")
            require(set(report["input_sha256"]) == {"main.c", "config.h", "unused.h", "Makefile.before"}, f"{style}: incomplete input hashes")
            for name, expected in report["input_sha256"].items():
                require(sha(local(directory if name == "Makefile.before" else folder, name)) == expected, f"{style}: fixed report/hash mismatch: {name}")
            require(apply(directory / "Makefile.before", directory / "reference.patch") == (directory / "Makefile.reference").read_bytes(), f"{style}: patch/reference mismatch")
            require(b"unused.h" in (directory / "Makefile.reference").read_bytes(), f"{style}: RD declaration was removed")
        return apply(folder / "Makefile.before", folder / "invalid-candidate.patch")

    try:
        invalid_makefile = verify_inputs(fixture)
        for name in ("main.c", "config.h", "unused.h"):
            report = read(fixture / "md-report.json")
            imported = report["imported_source"]
            result = subprocess.run(["git", "-C", str(root), "show", f"{imported['commit']}:{imported['path']}/{name}"], capture_output=True)
            require(result.returncode == 0 and result.stdout == (fixture / name).read_bytes(), f"Imported source differs from real A1 commit: {name}")
        expected = root / "e3/expected/mdfixer-reference.md"
        require(expected.is_file() and "MANUAL_EXPECTED" in expected.read_text(encoding="utf-8"), "Missing labeled reference answer")
        work = root / "e3/work"
        if args.run:
            require(Path(args.run).name == args.run, "--run must be a directory name")
            runs = [work / args.run]
        else:
            runs = sorted(p for p in work.glob("*-B2-*") if p.is_dir())
        require(bool(runs), "No B2 actual runs")
        for run in runs:
            obs = read(run / "observations.json")
            env = read(run / "environment.json")
            manifest = read(run / "source-manifest.json")
            require(obs["member"] == env["member"] == "B2" and obs["run_id"] == env["run_id"] == run.name, f"{run.name}: identity mismatch")
            require(obs["observation_type"] == "ACTUAL_RUN" and obs["status"] == "PASSED" and obs["failures"] == [], f"{run.name}: run did not pass")
            require(set(obs["styles"]) == set(STYLES), f"{run.name}: missing styles")
            require(env["configuration_id"] == "b2-gcc-O0-project-headers" and all(env.get(k) for k in ("os", "architecture", "versions")), f"{run.name}: missing environment/configuration")
            require(set(env["versions"]) == {"git", "make", "cc", "python"}, f"{run.name}: missing tool versions")
            require(manifest["fixture_version"] in ("WORKING_TREE_SNAPSHOT", "COMMITTED_FIXTURE"), f"{run.name}: invalid source version label")
            require(obs["source_commit"] == manifest["base_commit"], f"{run.name}: source context mismatch")
            require(subprocess.run(["git", "-C", str(root), "cat-file", "-e", manifest["base_commit"] + "^{commit}"], capture_output=True).returncode == 0, f"{run.name}: base commit not available")
            frozen = run / "inputs"
            require(set(manifest["sha256"]) == {p.relative_to(frozen).as_posix() for p in frozen.rglob("*") if p.is_file()}, f"{run.name}: incomplete frozen input manifest")
            for name, expected_hash in manifest["sha256"].items():
                require(sha(local(frozen, name)) == expected_hash, f"{run.name}: input bytes changed: {name}")
            frozen_invalid = verify_inputs(frozen)
            require(frozen_invalid == invalid_makefile, f"{run.name}: frozen rejection candidate differs")
            commands = read(run / "commands.json")
            ids = {}
            for command in commands:
                label = command["id"]
                require(label not in ids, f"{run.name}: duplicate command {label}")
                ids[label] = command
                require(isinstance(command["argv"], list) and bool(command["argv"]) and bool(command["cwd"]), f"{label}: missing command")
                require(command["source_commit"] == obs["source_commit"] and type(command["exit_code"]) is int, f"{label}: missing version/exit code")
                for stream in ("stdout", "stderr"):
                    require(sha(local(run, command[stream])) == command[stream + "_sha256"], f"{label}: raw log hash mismatch")
                require(command["exit_code"] != 0 if label == "rejection-candidate-build" else command["exit_code"] == 0, f"{label}: unexpected exit code")

            def log(label, stream="stdout"):
                return local(run, ids[label][stream]).read_text(encoding="utf-8", errors="replace")

            def snapshot(label, require_object=True):
                folder = run / "snapshots" / label
                state = read(folder / "state.json")
                for path in folder.iterdir():
                    if path.name != "state.json":
                        require(path.name in state and sha(path) == state[path.name]["sha256"] and path.stat().st_size == state[path.name]["bytes"], f"{label}: snapshot/hash mismatch: {path.name}")
                required = ("main.c", "config.h", "unused.h", "Makefile") + (("main.o",) if require_object else ())
                require(all(k in state for k in required), f"{label}: incomplete snapshot")
                for name in ("main.c", "unused.h"):
                    require(state[name]["sha256"] == sha(frozen / name), f"{label}: unrelated source changed: {name}")
                return state

            for style in STYLES:
                result = obs["styles"][style]
                for suffix, field, value in (("initial", "initial_output", "1"), ("stale", "stale_output", "1"),
                                             ("patched", "patched_clean_output", "2"), ("incremental3", "incremental3_output", "3"),
                                             ("incremental4", "incremental4_output", "4")):
                    require(result[field] == value and log(style + "-" + suffix + "-run").strip() == value, f"{style}/{suffix}: raw output mismatch")
                require(result["status"] == "PASSED", f"{style}: failed")
                for suffix in ("patch-check", "patch-apply"):
                    argv = ids[style + "-" + suffix]["argv"]
                    require(argv[0:2] == ["git", "apply"] and ("--check" in argv) == (suffix == "patch-check"), f"{style}: patch application not recorded")
                initial, stale, fixed, third, fourth, noop = [snapshot(style + "-" + suffix) for suffix in ("initial", "stale", "patched", "incremental3", "incremental4", "noop")]
                require(initial["main.o"] == stale["main.o"], f"{style}: MD did not retain original object")
                require(stale["config.h"]["sha256"] == fixed["config.h"]["sha256"], f"{style}: clean comparison used different source")
                for phase, previous, current, value in (("incremental3", fixed, third, "3"), ("incremental4", third, fourth, "4")):
                    edited = snapshot(style + "-header" + value + "-before-make")
                    require(edited["config.h"]["mtime_ns"] > previous["main.o"]["mtime_ns"], f"{style}/{phase}: header not newer")
                    require(current["main.o"]["mtime_ns"] > previous["main.o"]["mtime_ns"] and current["main.o"]["sha256"] != previous["main.o"]["sha256"], f"{style}/{phase}: object not regenerated")
                    require("-c main.c -o main.o" in log(style + "-" + phase + "-build"), f"{style}/{phase}: no compile recipe")
                    require(edited["config.h"]["sha256"] == current["config.h"]["sha256"], f"{style}/{phase}: edited source changed during build")
                require(noop["main.o"] == fourth["main.o"] and log(style + "-noop-run").strip() == "4", f"{style}: unchanged build recompiled")
                for phase in ("initial", "stale"):
                    require((run / "snapshots" / (style + "-" + phase) / "Makefile").read_bytes() == (frozen / "styles" / style / "Makefile.before").read_bytes(), f"{style}: original Makefile changed")
                for phase in ("patched", "incremental3", "incremental4", "noop"):
                    require((run / "snapshots" / (style + "-" + phase) / "Makefile").read_bytes() == (frozen / "styles" / style / "Makefile.reference").read_bytes(), f"{style}: patched Makefile changed")
            depfile = (run / "implicit-main.d").read_bytes()
            require(b"main.o: main.c config.h" in depfile and b"config.h:" in depfile, "Missing generated implicit dependency edge")
            require("main.d" not in read(run / "snapshots/implicit-initial/state.json"), "Initial .d should be absent")
            require(depfile == (run / "snapshots/implicit-patched/main.d").read_bytes(), "Generated .d differs from retained sample")
            rejected = obs["rejection"]
            require(rejected["candidate_accepted"] is False and rejected["restored_exact_bytes"] is True and rejected["restored_output"] == "1", "Candidate rejection/recovery mismatch")
            require(rejected["candidate_exit_code"] == ids["rejection-candidate-build"]["exit_code"] and "B2_INVALID_CANDIDATE" in log("rejection-candidate-build", "stderr"), "Candidate did not fail for injected command")
            require(log("rejection-original-run").strip() == log("rejection-restored-run").strip() == "1", "Recovery program output mismatch")
            for phase in ("original", "failed", "restored"):
                state = snapshot("rejection-" + phase, require_object=phase != "failed")
                if phase == "failed":
                    require("main.o" not in state, "Failed compile must not leave a new object")
                actual = (run / "snapshots" / ("rejection-" + phase) / "Makefile").read_bytes()
                require(actual == (frozen_invalid if phase == "failed" else (frozen / "Makefile.before").read_bytes()), f"Rejection {phase}: Makefile differs")
            require(rejected["restored_makefile_sha256"] == sha(frozen / "Makefile.before"), "Recovery hash mismatch")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        errors.append(str(exc))
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print(f"PASS: B2 fixed MD inputs, four reference patches, {len(runs)} runs, incremental rebuilds, .d and candidate recovery")
    print("Scope: manual baseline behavior; no detector accuracy or service recheck claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
