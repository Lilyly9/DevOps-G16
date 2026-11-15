"""A1 independent E8-A case: an include added inside an existing header."""

import tempfile
import unittest
from pathlib import Path

from lab import commit, fixture, scan


class A1IndirectIncludeTests(unittest.TestCase):
    def test_header_include_invalidates_previous_dependency_graph(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir) / "sample"
            fixture(project)
            baseline = scan(project)

            # Independent expectation from the edited input: main.c still
            # includes config.h, while config.h newly includes extra.h.
            (project / "config.h").write_text(
                '#include "extra.h"\n#define VALUE 1\n'
            )
            updated_commit = commit(project, "A1 indirect header include")
            incremental = scan(project, baseline)

            self.assertNotEqual(updated_commit, baseline["commit"])
            self.assertEqual(incremental["commit"], updated_commit)
            self.assertEqual(
                incremental["actual"],
                {
                    "main.o": ["config.h", "extra.h", "main.c"],
                    "helper.o": ["helper.c"],
                },
            )
            self.assertEqual(
                {
                    (finding["type"], finding["target"], finding["dependency"])
                    for finding in incremental["findings"]
                },
                {
                    ("MISSING", "main.o", "config.h"),
                    ("MISSING", "main.o", "extra.h"),
                    ("REDUNDANT", "main.o", "unused.h"),
                },
            )
            self.assertEqual(
                incremental["added"], [["MISSING", "main.o", "extra.h"]]
            )
            self.assertEqual(incremental["resolved"], [])
            self.assertEqual(incremental["refreshed"], ["main.o", "helper.o"])
            self.assertEqual(incremental["reused"], [])

            full = scan(project)
            for field in ("actual", "declared", "findings"):
                with self.subTest(field=field):
                    self.assertEqual(incremental[field], full[field])


if __name__ == "__main__":
    unittest.main()
