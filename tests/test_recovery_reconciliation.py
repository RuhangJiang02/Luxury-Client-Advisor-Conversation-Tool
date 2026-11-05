"""Recovery provenance must not hide generated-case selection or input changes."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.reconcile_recovery import reconcile

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.initial=self.root/'initial';self.recovery=self.root/'recovery'
        for p in [self.initial,self.recovery]:p.mkdir()
        for p,cases in [(self.initial,['A','B']),(self.recovery,['B'])]:
            (p/'manifest.json').write_text(json.dumps({'cases':[{'case_id':c,'expected_status':'generated'} for c in cases]}))
        self.write(self.initial,'A','generated');self.write(self.initial,'B','generation_failed');self.write(self.recovery,'B','generated')
    def tearDown(self):self.tmp.cleanup()
    def write(self,folder,case,status):
        a={'tool':'test-version','prompt':'test-prompt','config':{},'rules_hash':'r','catalogue_hash':'c','execution_kind':'test_double','request':{'case_id':case,'request_id':str(folder)+case,'fact':'fixed'},'response':{'case_id':case,'request_id':str(folder)+case,'status':status,'metadata':{'run_id':str(folder)+case}}}
        (folder/(case+'.json')).write_text(json.dumps(a))
    def test_recovery_view_keeps_source_bytes_and_every_selected_case(self):
        out=self.root/'view';rows=reconcile(self.initial,self.recovery,out)
        self.assertEqual(len(rows),2);self.assertEqual((out/'A.json').read_bytes(),(self.initial/'A.json').read_bytes());self.assertEqual((out/'B.json').read_bytes(),(self.recovery/'B.json').read_bytes())
    def test_generated_case_recovery_is_rejected(self):
        (self.recovery/'manifest.json').write_text(json.dumps({'cases':[{'case_id':'A'},{'case_id':'B'}]}))
        with self.assertRaises(ValueError):reconcile(self.initial,self.recovery,self.root/'view')
    def test_changed_facts_are_rejected_before_writing(self):
        p=self.recovery/'B.json';a=json.loads(p.read_text());a['request']['fact']='changed';p.write_text(json.dumps(a))
        with self.assertRaises(ValueError):reconcile(self.initial,self.recovery,self.root/'view')
        self.assertFalse((self.root/'view').exists())
    def test_failed_recovery_remains_a_failure_in_view(self):
        self.write(self.recovery,'B','generation_failed');out=self.root/'view';reconcile(self.initial,self.recovery,out)
        self.assertEqual(json.loads((out/'B.json').read_text())['response']['status'],'generation_failed')

if __name__=='__main__':unittest.main()
