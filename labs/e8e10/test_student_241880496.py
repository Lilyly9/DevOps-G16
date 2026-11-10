import tempfile, unittest
from pathlib import Path
from lab import fixture, scan, commit

class StudentE8E10A2(unittest.TestCase):
    def test_transitive_header_include_extends_actual_set(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            (p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
            (p/'extra.h').write_text('#include "leaf.h"\n#define EXTRA 0\n')
            (p/'leaf.h').write_text('#define LEAF 7\n')
            commit(p,'student: transitive include')
            incremental=scan(p,old)
            full=scan(p)
            self.assertEqual(incremental['actual']['main.o'],['config.h','extra.h','leaf.h','main.c'])
            missing={x['dependency'] for x in incremental['findings'] if x['type']=='MISSING'}
            self.assertEqual(missing,{'config.h','extra.h','leaf.h'})
            for key in ['actual','declared','findings']:
                self.assertEqual(incremental[key],full[key])

    def test_helper_source_invalidation_keeps_conservative_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            (p/'helper.c').write_text('#include "extra.h"\nint helper(void){return EXTRA;}\n')
            commit(p,'student: helper includes extra')
            incremental=scan(p,old)
            full=scan(p)
            self.assertEqual(incremental['invalidation'],['helper.c'])
            self.assertEqual(incremental['actual']['main.o'],old['actual']['main.o'])
            self.assertEqual(incremental['refreshed'],['main.o','helper.o'])
            self.assertEqual(incremental['reused'],[])
            for key in ['actual','declared','findings']:
                self.assertEqual(incremental[key],full[key])

    def test_body_change_records_no_invalidation_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            (p/'helper.c').write_text('int helper(void){return 0+0;}\n')
            commit(p,'student: body only')
            result=scan(p,old)
            self.assertEqual(result['invalidation'],[])
            self.assertEqual(result['reused'],['main.o','helper.o'])
            self.assertEqual(result['refreshed'],[])
            self.assertEqual(result['findings'],old['findings'])

if __name__=='__main__':unittest.main()
