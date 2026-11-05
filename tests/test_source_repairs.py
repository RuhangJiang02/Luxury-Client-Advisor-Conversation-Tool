"""Source and composition regressions for the full-run major findings."""
import copy
import json
import unittest
from client_advisor.config import ROOT
from client_advisor.greeting_composition import compose_greeting
from client_advisor.grounding import check_grounding
from client_advisor.source_checks import check_sources
CASES={x['case_id']:x['request'] for x in json.loads((ROOT/'data/generation-cases.json').read_text())['cases']}

class SourceRepairTests(unittest.TestCase):
    def test_birthday_and_festival_frames_follow_exact_occasion(self):
        for case in ['S1-01','S1-03']:
            r=CASES[case];body=['愿您顺心自在。','愿您有时间做喜欢的事。','愿您轻松开心，常有欢喜。']
            result,meta,errors=compose_greeting({'status':'generated','messages':body},r)
            self.assertEqual(errors,[])
            self.assertEqual(check_sources(result,r),[])
            self.assertEqual(meta['model_authored_bodies'],body)
            target='生日快乐' if case=='S1-01' else r['scenario_context']['occasion_name']+'快乐'
            self.assertTrue(all(target in t for t in result['messages']))

    def test_wrong_occasion_body_or_unknown_relative_date_is_rejected(self):
        r=CASES['S1-02'];texts=['愿您顺心。','节日快乐。','愿您开心。']
        self.assertTrue(compose_greeting({'status':'generated','messages':texts},r)[2])
        self.assertTrue(check_sources({'status':'generated','messages':['生日快乐，今天愿您开心。','生日快乐。','生日快乐，愿您自在。']},r))

    def test_festival_body_does_not_invent_an_age_transition(self):
        parsed={'status':'generated','messages':['愿您新的一岁开心。','愿您从容。','愿您愉快。']}
        self.assertTrue(compose_greeting(parsed,CASES['S1-03'])[2])

    def test_compose_non_success_never_creates_wishes(self):
        result={'status':'needs_clarification','reason':'请确认场合。'}
        self.assertEqual(compose_greeting(result,CASES['S1-01']),(result,None,[]))

    def test_catalogue_material_does_not_prove_wear_or_optical_properties(self):
        for text in ['粒面牛皮耐磨。','牛皮在阳光下有柔和光泽。','材质触感细腻。']:
            self.assertTrue(check_sources({'status':'generated','messages':[text,'拉链开合。','您习惯怎样携带？']},CASES['S2-02']))
        self.assertEqual(check_sources({'status':'generated','messages':['采用粒面牛皮。','拉链开合。','无法确认是否耐磨，也不能保证防水。']},CASES['S2-02']),[])

    def test_selected_catalogue_does_not_support_backpack_claim(self):
        r=CASES['S2-01']
        self.assertTrue(any('GROUNDING_CARRY_METHOD' in e for e in check_sources({'status':'generated','messages':['可单肩或双肩携带。','配可调节斜挎肩带。','您平时怎样携带？']},r)))
        self.assertFalse(any('GROUNDING_CARRY_METHOD' in e for e in check_sources({'status':'generated','messages':['这款可以斜挎。','配可调节斜挎肩带。','您平时怎样携带？']},r)))

    def test_claimed_discount_is_not_an_advisor_promise(self):
        r=CASES['S6-06']
        self.assertTrue(check_sources({'status':'generated','messages':['我们上次提到的八折优惠，目前不再提供。','采用粒面牛皮。','您可慢慢考虑。']},r))
        self.assertEqual(check_sources({'status':'generated','messages':['您提到我们上次答应八折，这一点还未核实。','这款不提供议价折扣。','您可慢慢考虑。']},r),[])

    def test_actual_advisor_statement_is_distinct_from_client_claim(self):
        r=copy.deepcopy(CASES['S6-06']);r['conversation_history'].append({'message_id':'advisor-record','role':'advisor','text':'我们上次提到八折优惠。','sent_at':None})
        self.assertFalse(any('GROUNDING_DISCOUNT_HISTORY' in e for e in check_sources({'status':'generated','messages':['我们上次提到的八折优惠需要纠正，目前不提供议价折扣。','目前政策不支持议价。','您可以慢慢考虑。']},r)))

if __name__=='__main__':unittest.main()
