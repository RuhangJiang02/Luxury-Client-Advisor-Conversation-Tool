import copy
import json
import unittest
from client_advisor.client_copy import compose_client_copy
from client_advisor.config import ROOT
CASES={r['case_id']:r['request'] for r in json.loads((ROOT/'data/generation-cases.json').read_text())['cases']}
class ClientCopyTests(unittest.TestCase):
    def test_exact_address_and_polite_pronoun_are_source_bound(self):
        r=copy.deepcopy(CASES['S4-07']);r['case_id']='unseen'
        raw={'status':'generated','messages':['愿你一切顺心。','你喜欢什么颜色？','你方便时再联系。']}
        out,meta,errors=compose_client_copy(raw,r)
        self.assertFalse(errors);self.assertTrue(all(t.startswith('顾客甸，') and '你' not in t for t in out['messages']))
        self.assertEqual(meta['original_messages'],raw['messages']);self.assertEqual(len(meta['transformations']),3)
        r['client']['preferred_address']=None;out,_,_=compose_client_copy(raw,r)
        self.assertTrue(all('顾客' not in s for s in out['messages']))
    def test_required_policy_and_prior_context_are_not_provider_fallbacks(self):
        r=CASES['S6-06'];raw={'status':'generated','messages':['目录价18800元。','采用粒面牛皮。','您可以慢慢考虑。']}
        out,meta,errors=compose_client_copy(raw,r)
        self.assertFalse(errors);self.assertTrue(all('不提供议价折扣' in s and '先前优惠' in s for s in out['messages']))
        self.assertFalse(meta['provider_failure_fallback'])
        failure={'status':'needs_clarification','reason':'请核实资料。'}
        self.assertEqual(compose_client_copy(failure,r),(failure,None,[]))
        r=CASES['S6-07'];out,_,_=compose_client_copy(raw,r)
        self.assertTrue(all('先前优惠' not in s for s in out['messages']))
if __name__=='__main__':unittest.main()
