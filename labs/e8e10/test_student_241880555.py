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

# B1 郭德林(241880555) E9-B 自主扩展：共享变量影响范围（macro 修复的跨目标效果）。
class StudentE9B_SharedDeps_241880555(unittest.TestCase):
    def test_macro_patch_shared_variable_expands_helper_declaration(self):
        # 独立预期：让 helper.o 也引用 $(DEPS) 后，helper.o 展开声明丢失 helper.c，
        # scan 产生两条 MISSING：main.o→config.h 与 helper.o→helper.c。patch 对每条
        # MISSING 依次追加到共享变量定义，最终 DEPS = main.c unused.h config.h helper.c；
        # 两个目标行均保持 $(DEPS) 字节不变，而 helper.o 的声明集合被动扩大。
        # 这证明共享变量的修复影响所有引用目标，不能假设影响只限报告中的 target。
        # （初版预期只写一条 edit，实测第二条 MISSING(helper.o,helper.c) 后修正——
        #   声明改为引用变量时，原字面依赖 helper.c 从展开结果中消失。）
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p,'macro')
            makefile=p/'Makefile'
            makefile.write_text(makefile.read_text().replace('helper.o: helper.c\n','helper.o: $(DEPS)\n'))
            run(['git','add','.'],p); run(['git','commit','-m','student: helper.o shares DEPS'],p)
            r=scan(p)
            self.assertIn({'type':'MISSING','target':'main.o','dependency':'config.h'},r['findings'])
            diff,edits=patch(p,r)
            self.assertEqual(edits,[
                {'target':'main.o','dependency':'config.h','style':'macro'},
                {'target':'helper.o','dependency':'helper.c','style':'macro'}])
            candidate=Path(directory)/'candidate.patch'; candidate.write_text(diff)
            run(['git','apply',str(candidate.resolve())],p)
            text=makefile.read_text()
            self.assertIn('DEPS = main.c unused.h config.h helper.c',text)
            self.assertIn('main.o: $(DEPS)',text)
            self.assertIn('helper.o: $(DEPS)',text)
            after=scan(p)
            self.assertIn('config.h',after['declared']['helper.o'])
            self.assertIn('config.h',after['declared']['main.o'])
            self.assertFalse(any(x['type']=='MISSING' for x in after['findings']))

# B1 郭德林(241880555) E10-B 自主扩展：错位修复（能构建但MD残留）的拒绝。
class StudentE10B_MisplacedFix_241880555(unittest.TestCase):
    def test_misplaced_fix_buildable_but_rejected_no_source_write(self):
        # 独立预期：候选把 config.h 加到 helper.o 的依赖行（错位修复）而非 main.o：
        # patch_applies/build/test 三项通过，但 no_missing=False——main.o 的
        # MISSING(config.h) 残留；且 header_change=False——main.o 声明缺 config.h，
        # 头文件改 VALUE=2 后 make 不会重编 main.o，程序仍输出 1。五项检查未全过，
        # accepted=False、rollback=True，源 Makefile 逐字节保持。
        import difflib,json
        from lab import validate
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            p=root/'sample'
            fixture(p)
            original=(p/'Makefile').read_text()
            changed=original.replace('helper.o: helper.c\n','helper.o: helper.c config.h\n')
            candidate=root/'misplaced.patch'
            candidate.write_text(''.join(difflib.unified_diff(original.splitlines(True),changed.splitlines(True),fromfile='a/Makefile',tofile='b/Makefile')))
            before=(p/'Makefile').read_bytes()
            r=validate(p,candidate,root/'validation')
            self.assertTrue(r['checks']['patch_applies'])
            self.assertTrue(r['checks']['build'])
            self.assertTrue(r['checks']['test'])
            self.assertFalse(r['checks']['header_change'])
            self.assertFalse(r['checks']['no_missing'])
            self.assertFalse(r['accepted'])
            self.assertTrue(r['rollback'])
            self.assertTrue(r['source_unchanged'])
            self.assertEqual((p/'Makefile').read_bytes(),before)
            recheck=json.loads((root/'validation'/'recheck.json').read_text())
            self.assertIn(('MISSING','main.o','config.h'),
                [(f['type'],f['target'],f['dependency']) for f in recheck['findings']])

if __name__=="__main__":unittest.main()
