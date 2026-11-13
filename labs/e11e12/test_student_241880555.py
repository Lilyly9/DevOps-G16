"""B1 241880555 extension tests: DRAFT build success vs run-output conclusions.

The CI test container has no Docker socket, so draft.autobuild.execute is
replaced by a scriptable fake that replays docker build / image inspect /
run exit codes and logs. What is verified:

1. A candidate whose build succeeds AND whose program prints the expected
   output must be recorded as SUCCEEDED with an explicit image_id (the field
   B1 hands over to A1/A2/B2 for same-image checks).
2. A candidate whose build succeeds but whose program prints a different
   output must fail verification - with the built image still recorded, so
   "build succeeded, output wrong" stays distinguishable from "build broke".
3. A candidate whose build itself fails must fail with a different message
   and must not record any image_id.
4. The first iteration must reproduce MISSING_MAKE before the candidate is
   even considered.
5. classify_failure separates MISSING_MAKE from infrastructure errors.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parent / "vendor")]

import draft.autobuild as autobuild

IMAGE_ID = "sha256:" + "b" * 64

CANDIDATE = (
    "FROM python:3.13-slim@sha256:" + "a" * 64 + "\n"
    "WORKDIR /work\n"
    "COPY main.c helper.c config.h ./\n"
    "RUN apt-get update && apt-get install -y --no-install-recommends build-essential\n"
    "RUN make app\n"
    'CMD ["./app"]\n'
)

BROKEN = (
    "FROM python:3.13-slim\n"
    "WORKDIR /work\n"
    "COPY main.c helper.c config.h ./\n"
    "RUN make app\n"
    'CMD ["./app"]\n'
)


class FakeDocker:
    """Replay the docker client commands auto_build issues, with scripted outcomes."""

    def __init__(self, build1_exit=1, build2_exit=0, run_exit=0, run_output="1\n"):
        self.build1_exit = build1_exit
        self.build2_exit = build2_exit
        self.run_exit = run_exit
        self.run_output = run_output

    def __call__(self, argv, stdout, stderr, timeout):
        stdout, stderr = Path(stdout), Path(stderr)
        verb = argv[1]
        if verb == "build":
            first = "iter-01" in str(argv[argv.index("-f") + 1])
            code = self.build1_exit if first else self.build2_exit
            stdout.write_text("", encoding="utf-8")
            stderr.write_text("", encoding="utf-8")
            if first and code:
                stderr.write_text(
                    "ERROR: failed to build: process \"/bin/sh -c make app\" did not "
                    "complete successfully: exit code: 127\n/bin/sh: 1: make: not found\n",
                    encoding="utf-8",
                )
            elif not first and code:
                stderr.write_text("ERROR: candidate build broke\n", encoding="utf-8")
            return code
        if verb == "image":
            stdout.write_text(json.dumps([{"Id": IMAGE_ID}]), encoding="utf-8")
            return 0
        if verb == "run":
            if "--cidfile" in argv:
                Path(argv[argv.index("--cidfile") + 1]).write_text("c" * 64, encoding="utf-8")
            stdout.write_text(self.run_output, encoding="utf-8")
            return self.run_exit
        return 0


def write_fixture(root):
    root.mkdir(parents=True)
    (root / "Dockerfile.broken").write_text(BROKEN, encoding="utf-8")
    for name in ("main.c", "helper.c", "config.h"):
        (root / name).write_text("#include \"config.h\"\n", encoding="utf-8")
    (root / "Makefile").write_text("app: main.o helper.o\n\tgcc main.o helper.o -o app\n", encoding="utf-8")
    candidate = root.parent / "candidate.Dockerfile"
    candidate.write_text(CANDIDATE, encoding="utf-8")
    return root, candidate


def run_auto_build(tmp, fake, expected_output="1"):
    fixture, candidate = write_fixture(tmp / "fixture")
    output = tmp / "draft-out"
    with patch.object(autobuild, "execute", fake):
        return autobuild.auto_build(fixture, candidate, output, expected_output)


class B1DraftConclusions(unittest.TestCase):
    def test_build_ok_output_matches_records_image_id(self):
        with tempfile.TemporaryDirectory() as d:
            report = run_auto_build(Path(d), FakeDocker())
            self.assertEqual(report["status"], "SUCCEEDED")
            second = report["attempts"][1]
            self.assertEqual(second["build_exit_code"], 0)
            self.assertEqual(second["image_id"], IMAGE_ID)
            self.assertTrue(report["verification"]["output_matches"])
            self.assertEqual(report["verification"]["actual_output"], "1\n")

    def test_build_ok_but_wrong_output_fails_verification(self):
        with tempfile.TemporaryDirectory() as d:
            report = run_auto_build(Path(d), FakeDocker(run_output="2\n"))
            self.assertEqual(report["status"], "FAILED")
            self.assertIn("Program verification failed", report["error"])
            second = report["attempts"][1]
            self.assertEqual(second["build_exit_code"], 0)
            self.assertEqual(second["image_id"], IMAGE_ID)
            self.assertFalse(report["verification"]["output_matches"])

    def test_repair_build_failure_is_a_different_conclusion(self):
        with tempfile.TemporaryDirectory() as d:
            report = run_auto_build(Path(d), FakeDocker(build2_exit=1))
            self.assertEqual(report["status"], "FAILED")
            self.assertIn("Repair candidate build failed", report["error"])
            self.assertNotIn("image_id", report["attempts"][1])
            self.assertNotIn("verification", report)

    def test_first_iteration_must_reproduce_missing_make(self):
        with tempfile.TemporaryDirectory() as d:
            report = run_auto_build(Path(d), FakeDocker(build1_exit=0))
            self.assertEqual(report["status"], "FAILED")
            self.assertIn("Baseline did not reproduce missing make", report["error"])
            self.assertEqual(report["attempts"][0]["failure_class"], "OTHER_BUILD_ERROR")

    def test_classify_failure_separates_make_from_infrastructure(self):
        self.assertEqual(autobuild.classify_failure("/bin/sh: 1: make: not found"), "MISSING_MAKE")
        self.assertEqual(autobuild.classify_failure("failed to resolve source metadata"), "INFRASTRUCTURE")
        self.assertEqual(autobuild.classify_failure("gcc: fatal error: no such file"), "OTHER_BUILD_ERROR")


if __name__ == "__main__":
    unittest.main()
