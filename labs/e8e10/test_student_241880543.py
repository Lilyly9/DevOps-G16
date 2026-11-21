"""B2: repeated MD records must describe one edit per target/dependency."""
import tempfile
import unittest
from pathlib import Path

from lab import declarations, fixture, patch, run, scan


class Student241880543PatchTests(unittest.TestCase):
    def test_same_header_on_two_targets_is_not_globally_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "two-targets"
            fixture(project)
            # Both translation units now really use config.h.
            (project / "helper.c").write_text('#include "config.h"\nint helper(void){return VALUE;}\n')
            from lab import commit
            commit(project, "helper also includes config.h")
            report = scan(project)
            report["findings"] *= 2
            diff, plan = patch(project, report)
            self.assertEqual(plan, [
                {"target": "main.o", "dependency": "config.h", "style": "direct"},
                {"target": "helper.o", "dependency": "config.h", "style": "direct"},
            ])
            candidate = Path(tmp) / "candidate.patch"
            candidate.write_text(diff)
            run(["git", "apply", str(candidate)], project)
            self.assertEqual(declarations(project)[0], {
                "main.o": ["config.h", "main.c", "unused.h"],
                "helper.o": ["config.h", "helper.c"],
            })

    def test_duplicate_missing_records_preserve_all_three_styles(self):
        for style in ("direct", "macro", "mixed"):
            with self.subTest(style=style), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp) / style
                fixture(project, style)
                before = (project / "Makefile").read_bytes()
                report = scan(project)
                missing = {"type": "MISSING", "target": "main.o", "dependency": "config.h"}
                # Independent input: two duplicate MD records around the real RD.
                report["findings"] = [missing.copy(), report["findings"][1], missing.copy(), missing.copy()]
                diff, plan = patch(project, report)

                self.assertEqual(plan, [{"target": "main.o", "dependency": "config.h", "style": style}])
                self.assertEqual((project / "Makefile").read_bytes(), before)
                candidate = Path(tmp) / "candidate.patch"
                candidate.write_text(diff)
                run(["git", "apply", "--check", str(candidate)], project)
                run(["git", "apply", str(candidate)], project)
                after = (project / "Makefile").read_text()
                expected = {
                    "direct": "main.o: main.c unused.h config.h",
                    "macro": "DEPS = main.c unused.h config.h",
                    "mixed": "main.o: main.c $(HEADERS) config.h",
                }[style]
                self.assertIn(expected + "\n", after)
                self.assertEqual(after.count("config.h"), 1)
                self.assertEqual(declarations(project)[0], {
                    "main.o": ["config.h", "main.c", "unused.h"],
                    "helper.o": ["helper.c"],
                })
                self.assertEqual(
                    [line for line in after.splitlines() if line.startswith("\t")],
                    [line for line in before.decode().splitlines() if line.startswith("\t")],
                )
                if style == "macro":
                    self.assertIn("main.o: $(DEPS)\n", after)
                if style == "mixed":
                    self.assertIn("HEADERS = unused.h\n", after)


if __name__ == "__main__":
    unittest.main()
