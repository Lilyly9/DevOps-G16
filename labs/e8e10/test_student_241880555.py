import tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch

# B1 郭德林(241880555) 自主扩展：未知目标显式拒绝；纯RD报告不产生删除操作。
class StudentB1_241880555(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/"sample";fixture(self.p)

    def test_unknown_target_rejected_and_source_intact(self):
        # 独立预期：MISSING 条目指向 Makefile 中不存在的目标 phantom.o 时，
        # patch 显式拒绝(UNSUPPORTED_TARGET)，且 Makefile 逐字节保持不变。
        r=scan(self.p)
        r["findings"]=[{"type":"MISSING","target":"phantom.o","dependency":"config.h"}]
        before=(self.p/"Makefile").read_bytes()
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_TARGET"):
            patch(self.p,r)
        self.assertEqual((self.p/"Makefile").read_bytes(),before)

    def test_redundant_only_report_generates_no_deletion(self):
        # 独立预期：报告仅含 REDUNDANT(unused.h) 时，patch 返回空 diff 与空编辑列表，
        # 不产生任何删除操作，unused.h 仍保留在 Makefile 中。
        r=scan(self.p)
        r["findings"]=[f for f in r["findings"] if f["type"]=="REDUNDANT"]
        diff,edits=patch(self.p,r)
        self.assertEqual(diff,"")
        self.assertEqual(edits,[])
        self.assertIn("unused.h",(self.p/"Makefile").read_text())

if __name__=="__main__":unittest.main()
