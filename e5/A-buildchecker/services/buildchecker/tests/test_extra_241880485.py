"""A1 (241880485): keep Make's own reads out of compiler dependencies.

These independent synthetic transcripts are unit-test inputs, not collected
E5 evidence. A header opened only by Make must not produce a false MD finding
for the object compiled by a descendant recipe process.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import analyze


class TestMakeProcessIsolation(unittest.TestCase):
    def test_make_only_header_open_is_not_a_recipe_dependency(self):
        transcripts = {
            "t.100": (
                'execve("/usr/bin/make", ["make", "main.o"], []) = 0\n'
                'openat(AT_FDCWD, "Makefile", O_RDONLY) = 3\n'
                'openat(AT_FDCWD, "config.h", O_RDONLY) = 4\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 110\n'
            ),
            "t.110": (
                'execve("/usr/bin/cc", ["cc", "-c", "main.c", "-o", "main.o"], []) = 0\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 111\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 112\n'
            ),
            "t.111": (
                'execve("/usr/bin/cc1", ["cc1", "main.c"], []) = 0\n'
                'openat(AT_FDCWD, "main.c", O_RDONLY) = 3\n'
                'openat(AT_FDCWD, "required.h", O_RDONLY) = 4\n'
            ),
            "t.112": (
                'execve("/usr/bin/as", ["as", "-o", "main.o"], []) = 0\n'
                'openat(AT_FDCWD, "main.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 3\n'
            ),
        }
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            trace = folder / "trace"
            trace.mkdir()
            for filename, text in transcripts.items():
                (trace / filename).write_text(text, encoding="utf-8")
            database = folder / "make-db.txt"
            database.write_text(
                "# Files\nmain.o: main.c required.h\n# files hash-table stats:\n",
                encoding="utf-8",
            )

            result = analyze(trace, database, "/course/project")

        # The compiler's reads belong to main.o; the Make-only reads do not.
        self.assertEqual(
            {(edge["target"], edge["dependency"]) for edge in result["actual_graph"]},
            {("main.o", "main.c"), ("main.o", "required.h")},
        )
        self.assertEqual(result["findings"], [])


if __name__ == "__main__":
    unittest.main()
