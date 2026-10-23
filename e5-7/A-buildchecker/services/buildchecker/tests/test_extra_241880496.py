"""Extra boundary tests added by A2 (241880496).

The shipped suite checks the trace-side boundaries but not how the Make
database parser and the MD/RD comparison interact. Two behaviours are pinned
here:

1. The `# Not a target:` section of `make -p` output is skipped instead of
   being treated as a declared target.
2. An order-only prerequisite that the recipe actually reads is reported as
   MISSING (it never triggers a rebuild), and is never reported as REDUNDANT.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import analyze, declaration_graph

ROOT = "/course/project"


class TestExtraBoundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text):
        path = self.folder / name
        path.write_text(text, encoding="utf-8")
        return path

    def traces(self):
        self.write("t.10", 'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 11\n')
        self.write("t.11", 'execve("/usr/bin/cc", ["cc", "-c", "unit.c", "-o", "unit.o"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 12\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 13\n')
        self.write("t.12", 'execve("/usr/bin/cc1", ["cc1", "unit.c"], []) = 0\n'
                   'openat(AT_FDCWD, "unit.c", O_RDONLY) = 3\n'
                   'openat(AT_FDCWD, "needed.h", O_RDONLY) = 4\n')
        self.write("t.13", 'execve("/usr/bin/as", ["as", "-o", "unit.o"], []) = 0\n'
                   'openat(AT_FDCWD, "unit.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 3\n')

    def test_not_a_target_section_is_skipped(self):
        db = self.write("db.txt", "# Files\n# Not a target:\nhelper-target: hidden.h\n"
                        "unit.o: unit.c needed.h\n# files hash-table stats:\n")
        declared = declaration_graph(db, ROOT)
        self.assertNotIn("helper-target", declared)
        self.assertEqual(set(declared["unit.o"]["dependencies"]), {"unit.c", "needed.h"})

    def test_order_only_prerequisite_read_by_recipe_is_missing_not_redundant(self):
        self.traces()
        db = self.write("db.txt", "# Files\nunit.o: unit.c | needed.h\n"
                        "# files hash-table stats:\n")
        declared = declaration_graph(db, ROOT)
        self.assertEqual(declared["unit.o"]["order_only"], ["needed.h"])
        result = analyze(self.folder, db, ROOT)
        self.assertEqual([(f["type"], f["target"], f["dependency"]) for f in result["findings"]],
                         [("MISSING", "unit.o", "needed.h")])


if __name__ == "__main__":
    unittest.main()
