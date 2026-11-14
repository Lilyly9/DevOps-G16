"""A1 checks for running BuildChecker in the DRAFT image."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest.mock import patch

from draft_fullcheck import DraftExecutor


IMAGE_ID = "sha256:" + "b" * 64
CONTAINER_ID = "c" * 64


class FakeDocker:
    """Offer a created container, its observation, and the traced Make output."""

    def __init__(self, inspected_image=IMAGE_ID):
        self.inspected_image = inspected_image
        self.commands = []

    def __call__(self, argv, **kwargs):
        argv = [str(arg) for arg in argv]
        self.commands.append(argv)
        verb = argv[1]
        err = ""
        if verb == "create":
            out = CONTAINER_ID + "\n"
        elif verb == "start":
            out = "# Files\nmain.o: main.c\n"
            err = "compiler diagnostic\n"
        elif argv[1:3] == ["container", "inspect"]:
            if argv[-1] != CONTAINER_ID:
                raise AssertionError("Executor did not inspect its created container")
            fields = argv[argv.index("--format") + 1]
            if fields == "{{.Image}}":
                out = self.inspected_image + "\n"
            elif ".State.Status" in fields and ".State.ExitCode" in fields:
                out = "exited 0\n"
            else:
                raise AssertionError("Unexpected inspection fields: " + fields)
        elif verb == "rm":
            out = CONTAINER_ID + "\n"
        else:
            raise AssertionError("Unexpected Docker command: " + repr(argv))
        for key, data in (("stdout", out), ("stderr", err)):
            sink = kwargs.get(key)
            if hasattr(sink, "write"):
                try:
                    sink.write(data)
                except TypeError:
                    sink.write(data.encode())
        return subprocess.CompletedProcess(argv, 0, out, err)


class DraftExecutorTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name).resolve()
        self.course = root / "course"
        self.host = PurePosixPath("/docker-host/host checkout")
        self.stage = self.course / "work" / "a1" / "baseline-full"
        self.project = self.stage / "project"
        self.traces = self.stage / "trace"
        self.project.mkdir(parents=True)
        self.traces.mkdir()
        self.outside_project = root / "outside"
        self.outside_project.mkdir()

    def executor(self, image=IMAGE_ID):
        return DraftExecutor(image, self.host, course_root=self.course)

    def test_rejects_mutable_or_incomplete_image_reference(self):
        for invalid in ("draft:candidate", "sha256:" + "b" * 12):
            with self.subTest(image=invalid), self.assertRaises(ValueError):
                self.executor(invalid)

    def test_rejects_project_outside_course_root_before_docker(self):
        with patch("draft_fullcheck.subprocess.run") as docker:
            executor = self.executor()
            with self.assertRaises(ValueError):
                executor(
                    ["make", "clean"],
                    self.outside_project,
                    self.stage / "clean.log",
                    self.stage / "clean-stderr.log",
                    3,
                )
            docker.assert_not_called()

    def traced_build(self, docker):
        with (
            patch("draft_fullcheck.subprocess.run", side_effect=docker),
            patch("draft_fullcheck.os.getuid", return_value=123, create=True),
            patch("draft_fullcheck.os.getgid", return_value=456, create=True),
        ):
            return self.executor()(
                [
                    "strace", "-ff", "-s", "4096", "-o", str(self.traces / "t"),
                    "-e", "trace=%file,%process", "make", "-p", "app",
                ],
                self.project,
                self.stage / "make-db.txt",
                self.stage / "build-stderr.log",
                3,
            )

    def test_traced_make_uses_image_id_and_host_paths_and_preserves_logs(self):
        docker = FakeDocker()
        self.assertEqual(self.traced_build(docker), 0)
        create = next(argv for argv in docker.commands if argv[1] == "create")
        image_index = create.index(IMAGE_ID)
        self.assertEqual(create[image_index + 1 :][-3:], ["make", "-p", "app"])
        self.assertEqual(create[create.index("--entrypoint") + 1], "strace")
        self.assertEqual(create[create.index("--workdir") + 1], self.project.as_posix())
        self.assertEqual(create[create.index("--network") + 1], "none")
        for path in (self.project, self.traces):
            host_path = self.host / path.relative_to(self.course).as_posix()
            self.assertIn(f"type=bind,source={host_path},target={path.as_posix()}", create)
        self.assertEqual(create.count("--mount"), 2)
        self.assertEqual((self.stage / "make-db.txt").read_text(), "# Files\nmain.o: main.c\n")
        self.assertEqual((self.stage / "build-stderr.log").read_text(), "compiler diagnostic\n")
        record = json.loads((self.stage / "build-execution.json").read_text(encoding="utf-8"))
        self.assertEqual(record["actual_image_id"], IMAGE_ID)
        self.assertEqual(record["container_exit_code"], 0)

    def test_refuses_inspected_container_with_different_image(self):
        docker = FakeDocker(inspected_image="sha256:" + "d" * 64)
        with self.assertRaisesRegex(ValueError, "image differs"):
            self.traced_build(docker)
        self.assertFalse(any(argv[1] == "start" for argv in docker.commands))
        self.assertTrue(any(argv[1] == "rm" for argv in docker.commands))


if __name__ == "__main__":
    unittest.main()
