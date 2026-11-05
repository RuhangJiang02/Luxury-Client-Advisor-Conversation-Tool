"""Prevent content-routing regressions exposed by the 33-candidate review."""
import copy
import json
import unittest
from client_advisor.config import ROOT
from client_advisor.grounding import check_grounding, grounding_context
from client_advisor.output_checks import quality_flags, parse_output
from client_advisor.prompts import build_messages
from client_advisor.rules import preflight

CASES={r['case_id']:r['request'] for r in json.loads((ROOT/'data/quality-fix-validation-cases.json').read_text())['cases']}

class EditorialRoutingTests(unittest.TestCase):
    def test_client_request_for_space_does_not_require_product_pitch(self):
        r=CASES['QF-P02']
        texts=['好的，您慢慢考虑，不用急着决定。','明白，先不打扰您了，按自己的节奏就好。','之后有想了解的地方，方便时再给我留言就好。']
        self.assertEqual(check_grounding({'status':'generated','messages':texts},r)[0],[])
        _,derived,_=preflight(r);derived['writing_constraints']=grounding_context(r)
        payload=json.loads(build_messages(r,derived,local=True)[1]['content'].split('\n')[1])
        self.assertIn('客户要考虑时间',payload['核心请求'])
        self.assertNotIn('第二条专用资料',payload)

    def test_comparison_can_explain_unknown_conditions_without_material_pitch(self):
        r=CASES['QF-P01']
        texts=['您提到的16000元报价条件尚未核实，这里的价格是18800元。','目前还不了解对方报价的具体条件，我无法确认价差原因。','您可以慢慢比较，不急着决定；目前无法确认两边条件是否一致。']
        self.assertEqual(check_grounding({'status':'generated','messages':texts},r)[0],[])
        _,derived,_=preflight(r);derived['writing_constraints']=grounding_context(r)
        payload=json.loads(build_messages(r,derived,local=True)[1]['content'].split('\n')[1])
        self.assertEqual(payload['客户报告的比价']['reported_amount'],16000)
        self.assertNotIn('第二条专用资料',payload)

    def test_unknown_or_confirmed_receipt_cannot_be_rewritten_as_non_receipt(self):
        texts=['这只包目前还未收到。','日常清洁可用干净柔软的干布。','暂时不用可放入随附防尘袋。']
        for case in ['S3-01','QF-C01']:
            self.assertTrue(any('GROUNDING_NON_RECEIPT' in e for e in check_grounding({'status':'generated','messages':texts},CASES[case])[0]))
        self.assertFalse(any('GROUNDING_NON_RECEIPT' in e for e in check_grounding({'status':'generated','messages':texts},CASES['QF-C02'])[0]))
        texts[0]='如果这只包还未收到，可以先了解养护建议。'
        self.assertFalse(any('GROUNDING_NON_RECEIPT' in e for e in check_grounding({'status':'generated','messages':texts},CASES['S3-01'])[0]))

    def test_client_consideration_is_not_a_pricing_rationale(self):
        r=CASES['QF-P02']
        for text in ['价格方面您再考虑一下，我们尊重您的节奏。','您说的我理解，价格方面确实需要您再考虑。']:
            errors=check_grounding({'status':'generated','messages':[text,'您不用急着决定。','方便时再联系即可。']},r)[0]
            self.assertFalse(any('GROUNDING_PRICE_RATIONALE' in e for e in errors))

    def test_explicit_non_offer_of_sizes_is_not_an_offer(self):
        r=CASES['QF-P01']
        texts=['目前不涉及其他尺寸或替代方案。','报价条件尚未核实，无法确认原因。','您可以慢慢比较，不急着决定。']
        self.assertFalse(any('GROUNDING_UNVERIFIED_SIZE' in e for e in check_grounding({'status':'generated','messages':texts},r)[0]))

    def test_discount_request_still_requires_policy_in_each_candidate(self):
        r=CASES['S6-01']
        errors=check_grounding({'status':'generated','messages':['您慢慢考虑就好。','这款采用粒面牛皮。','不急着决定。']},r)[0]
        self.assertEqual(sum('POLICY_DISCOUNT_REPLY' in e for e in errors),3)

    def test_formal_language_is_a_review_flag_not_a_parser_rejection(self):
        texts=['诚邀您参加这次预览。','欢迎来看看这款包的设计。','您方便时再考虑是否参加即可。']
        self.assertIsNotNone(parse_output(json.dumps({'status':'generated','messages':texts}))[0])
        self.assertTrue(any(f['code']=='NATURALNESS_REVIEW' for f in quality_flags(texts)))

if __name__=='__main__':unittest.main()
