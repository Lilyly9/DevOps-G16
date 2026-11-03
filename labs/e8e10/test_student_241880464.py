"""A3 241880464：独立配置失效测试，保留课程原七项测试。"""
import tempfile
import unittest
from pathlib import Path
from lab import scan
from student_241880464 import prepare, enable, check
from lab import fixture
from student_241880464_followup import add_shared_header, check_shared, prepare_chain, remove_indirect_include, check_removed

class Student241880464Tests(unittest.TestCase):
    def test_e8_shared_header_keeps_object_job_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)/'sample'
            fixture(project)
            baseline = scan(project)
            add_shared_header(project)
            check_shared(scan(project, baseline), scan(project))

    def test_e9_removed_indirect_include_resolves_exact_missing_edge(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)/'sample'
            baseline = prepare_chain(project)
            self.assertEqual(baseline['actual']['main.o'], ['branch.h','config.h','leaf.h','main.c'])
            remove_indirect_include(project)
            check_removed(scan(project, baseline), scan(project))

    def test_conditional_macro_adds_exact_missing_edge(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)/'sample'
            previous = prepare(project)
            self.assertEqual(previous['actual'], {'main.o':['config.h','main.c'], 'helper.o':['helper.c']})
            enable(project)
            check(scan(project, previous), scan(project))

if __name__ == '__main__':
    unittest.main()
