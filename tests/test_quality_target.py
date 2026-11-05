"""Context-sensitive repairs protect real concerns rather than known case IDs."""
import copy
import json
import unittest
from client_advisor.config import ROOT
from client_advisor.editorial import brief, recommendation_angles
from client_advisor.event_composition import compose_event
from client_advisor.greeting_composition import compose_greeting
from client_advisor.recommendation_composition import compose_recommendation
from client_advisor.source_checks import check_sources
from client_advisor.rules import preflight
from client_advisor.context import resolved_products

CASES={r['case_id']:r['request'] for r in json.loads((ROOT/'data/generation-cases.json').read_text())['cases']}
class StrictQualityTargetTests(unittest.TestCase):
    def test_unmeasured_laptop_and_waterproof_question_survives_composition(self):
        r=copy.deepcopy(CASES['S2-09']);r['case_id']='unseen-laptop';_,d,_=preflight(r)
        questions=['您方便量一下电脑的长宽厚吗？','您会连保护套一起携带吗？','您通勤还要带哪些物品？']
        out,meta,errors=compose_recommendation({'status':'generated','messages':questions},r,d)
        self.assertEqual(errors,[])
        self.assertTrue(all('不能保证防水' in t and '核对' in t for t in out['messages']))
        self.assertTrue(any('电脑' in a for a in recommendation_angles(r,resolved_products(d['eligible_product_ids'])[0])))
        self.assertEqual(meta['model_authored_bodies'],questions)

    def test_event_without_product_has_no_unsupported_design_in_brief(self):
        from client_advisor.editorial import build_editorial_messages
        r=CASES['S5-05'];_,d,_=preflight(r)
        m=build_editorial_messages(r,d)
        self.assertNotIn('这个设计',m[1]['content'])
        self.assertIn('您那天方便参加吗',m[1]['content'])

    def test_event_deadline_and_advance_greeting_use_verified_dates(self):
        r=CASES['S5-06'];out,meta,errors=compose_event({'status':'generated','messages':['欢迎来参加，有兴趣直接回复我。','如果想看看旋锁设计，您可以来参加。','您按自己的安排考虑，不必特意调整时间。']},r)
        self.assertFalse(errors)
        self.assertTrue(all('报名截止为11月7日18:00' in t for t in out['messages']))
        out,_,errors=compose_greeting({'status':'generated','messages':['愿您顺心自在。','愿您留些时间做喜欢的事。','愿您轻松开心。']},CASES['S1-08'])
        self.assertFalse(errors);self.assertTrue(all('提前祝您生日快乐' in t for t in out['messages']))

    def test_no_pressure_and_current_issue_take_priority(self):
        for case,term in [('S4-06','不再推介'),('S3-06','不保证'),('S6-03','预算'),('S6-05','结构')]:
            r=copy.deepcopy(CASES[case]);r['case_id']='unseen-case';_,d,_=preflight(r)
            self.assertIn(term,' '.join(brief(r,d)),case)

    def test_present_discount_injection_is_not_a_prior_promise(self):
        from client_advisor.reference_drafts import references
        for case,expected in [('S6-06',True),('S6-07',False)]:
            r=CASES[case];_,d,_=preflight(r);drafts=references(r,d)
            self.assertEqual(any('旧优惠' in s or '先前优惠' in s for s in drafts),expected)
        self.assertTrue(check_sources({'status':'generated','messages':['您提到的之前优惠还需要核实。','您提到的旧优惠需核实。','您对先前优惠的疑问还需核实。']},CASES['S6-07']))
        self.assertTrue(check_sources({'status':'generated','messages':['您，近来一切顺心吗？','最近还好吗？','不用特意回复。']},CASES['S4-04']))

    def test_chinese_copy_rejects_english_insertion_but_allows_given_name(self):
        r=copy.deepcopy(CASES['S3-04'])
        self.assertTrue(any('EDITORIAL_LANGUAGE' in e for e in check_sources({'status':'generated','messages':['please保持干燥。','可以用干布轻拭。','避免长时间日晒。']},r)))
        r['client']['preferred_address']='Alex'
        self.assertEqual(check_sources({'status':'generated','messages':['Alex，您可以用干布轻拭。','Alex，暂不使用时保持干燥。','Alex，有问题可以告诉我。']},r),[])

    def test_pricing_challenge_gets_unknown_rationale_boundary_not_past_offer(self):
        from client_advisor.reference_drafts import references
        r=copy.deepcopy(CASES['S6-07']);r['case_id']='unseen-pricing-challenge';_,d,_=preflight(r)
        drafts=references(r,d)
        self.assertTrue(any('定价依据' in s for s in drafts))
        self.assertFalse(any('旧优惠' in s for s in drafts))
        self.assertEqual(check_sources({'status':'generated','messages':drafts},r),[])
        self.assertTrue(any('EDITORIAL_FORMALITY' in e for e in check_sources({'status':'generated','messages':['您可以酌情考虑。','关于折扣事宜，不提供议价折扣。','不必急于做出决定。']},r)))

    def test_internal_message_labels_and_unintended_pronoun_are_rejected(self):
        from client_advisor.output_checks import parse_output
        for label in ['消息一：','文案二：','回复3:']:
            _,errors=parse_output(json.dumps({'status':'generated','messages':[label+'您好。','您可以慢慢考虑。','您方便时再联系。']}))
            self.assertTrue(any('HF-06' in e for e in errors))
        self.assertTrue(any('EDITORIAL_PRONOUN_OR_TYPO' in e for e in check_sources({'status':'generated','messages':['你可以先看看。','您可以慢慢考虑。','您方便时再联系。']},CASES['S6-05'])))

    def test_unverified_exclusivity_and_literal_branch_are_rejected(self):
        for case,text in [('S6-06','这是目前我们唯一可提供的材质。'),('S3-06','收到后/以后保持干燥。')]:
            self.assertTrue(check_sources({'status':'generated','messages':[text,'您可以慢慢考虑。','如有问题可以告诉我。']},CASES[case]))

if __name__=='__main__':unittest.main()
