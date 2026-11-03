"""A3 241880464：独立配置失效测试，保留课程原七项测试。"""
import tempfile
import unittest
from pathlib import Path
from lab import scan
from student_241880464 import prepare, enable, check

class Student241880464Tests(unittest.TestCase):
    def test_conditional_macro_adds_exact_missing_edge(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)/'sample'
            previous = prepare(project)
            self.assertEqual(previous['actual'], {'main.o':['config.h','main.c'], 'helper.o':['helper.c']})
            enable(project)
            check(scan(project, previous), scan(project))

if __name__ == '__main__':
    unittest.main()
