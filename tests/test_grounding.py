"""Evidence-bound regression cases, including negations and permitted descriptions."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from client_advisor.config import Config, ROOT
from client_advisor.grounding import check_grounding, receipt_evidence
from client_advisor.run_store import RunStore
from client_advisor.service import GenerationService
from client_advisor.output_checks import parse_output

BASES = json.loads((ROOT/'examples/io-v0.1/examples.json').read_text())['scenario_requests']


class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.care = copy.deepcopy(BASES[2])
        self.price = copy.deepcopy(BASES[5])

    def errors(self, request, text):
        return check_grounding({'status':'generated','messages':[text,'理解您的想法，您可以慢慢考虑。','如果您有具体问题，我可以为您说明。']},request)[0]

    def test_purchase_date_is_not_receipt_evidence(self):
        self.assertFalse(receipt_evidence(self.care)['confirmed'])
        self.assertTrue(any('GROUNDING_RECEIPT' in e for e in self.errors(self.care,'您的包已到手，感谢选择。')))

    def test_explicit_client_receipt_is_supported(self):
        self.care['conversation_history']=[{'message_id':'receipt','role':'client','text':'我的肩包已经收到了，谢谢。','sent_at':None}]
        self.assertTrue(receipt_evidence(self.care)['confirmed'])
        self.assertFalse(any('GROUNDING_RECEIPT' in e for e in self.errors(self.care,'您的包已收到，想了解用得是否顺手。')))

    def test_advisor_question_does_not_confirm_receipt(self):
        self.care['conversation_history']=[{'message_id':'q','role':'advisor','text':'您的包已经收到了吗？','sent_at':None}]
        self.assertFalse(receipt_evidence(self.care)['confirmed'])

    def test_negation_and_conditional_do_not_confirm_receipt(self):
        for text in ['包还没收到。','如果包已经收到，我再告诉您。','我没有确认包已收到。']:
            self.care['conversation_history']=[{'message_id':'q','role':'client','text':text,'sent_at':None}]
            self.assertFalse(receipt_evidence(self.care)['confirmed'],text)

    def test_receipt_of_message_is_not_receipt_of_product(self):
        self.care['conversation_history']=[{'message_id':'q','role':'client','text':'我已收到关于肩包的通知消息。','sent_at':None}]
        self.assertFalse(receipt_evidence(self.care)['confirmed'])

    def test_conditional_care_language_is_not_an_arrival_assertion(self):
        self.assertFalse(any('GROUNDING_RECEIPT' in e for e in self.errors(self.care,'如果您已收到这只包，可以告诉我有无养护问题。')))

    def test_acknowledging_feedback_does_not_claim_product_receipt(self):
        self.assertFalse(any('GROUNDING_RECEIPT' in e for e in self.errors(self.care,'已收到您的反馈，关于这只包的养护我可以进一步说明。')))

    def test_unknown_receipt_does_not_justify_recent_usage_assumption(self):
        self.assertTrue(any('GROUNDING_USAGE' in e for e in self.errors(self.care,'您最近在使用这只包时有什么感受？')))
        self.assertFalse(any('GROUNDING_USAGE' in e for e in self.errors(self.care,'如果您最近在使用这只包，可以告诉我需要了解哪些细节。')))

    def test_known_price_and_material_can_be_stated_without_causal_story(self):
        text='理解您的顾虑，这款采用粒面牛皮，目录价为18800元，不提供议价折扣。'
        errors=self.errors(self.price,text)
        self.assertFalse(any('GROUNDING_PRICE_RATIONALE' in e for e in errors))

    def test_unsupported_pricing_rationale_is_rejected(self):
        for text in ['这是基于其材质和设计的官方定价，不提供折扣。','循线肩包的定价已考虑了其粒面牛皮材质和工艺，不议价。']:
            self.assertTrue(any('GROUNDING_PRICE_RATIONALE' in e for e in self.errors(self.price,text)),text)

    def test_comparison_cause_is_not_known_from_a_reported_price(self):
        request=copy.deepcopy(self.price);request['scenario_context']['objection_type']='comparison'
        for text in ['价格差异可能源于渠道不同。','价差可能与材质有关。','价格是基于其品质确定的。']:
            self.assertTrue(any('GROUNDING_PRICE_RATIONALE' in e for e in self.errors(request,text)),text)
        self.assertFalse(any('GROUNDING_PRICE_RATIONALE' in e for e in self.errors(request,'目前无法核实价差是否来自渠道，我只能说明已知目录价。')))

    def test_enum_and_planning_labels_are_not_client_copy(self):
        for text in ['请按reply_to_advisor回复。','活动名称：皮具私享预览。','以可自由安排时间为开头，请来参加活动。']:
            parsed, errors=parse_output(json.dumps({'status':'generated','messages':[text,'欢迎您按自己的安排考虑参加。','有兴趣的话直接回复这条微信即可。']}))
            self.assertIsNone(parsed)
            self.assertTrue(any('HF-06' in e for e in errors))

    def test_blanket_absence_is_rejected_but_missing_information_is_not(self):
        self.assertTrue(any('GROUNDING_ALTERNATIVE_ABSENCE' in e for e in self.errors(self.price,'不提供议价折扣，也不存在其他尺寸或价格替代方案。')))
        self.assertFalse(any('GROUNDING_ALTERNATIVE_ABSENCE' in e for e in self.errors(self.price,'不提供议价折扣，目前资料中没有其他尺寸信息。')))

    def test_discount_request_requires_an_explicit_policy_reply(self):
        self.assertTrue(any('POLICY_DISCOUNT_REPLY' in e for e in self.errors(self.price,'您可以慢慢考虑，有具体问题再告诉我。')))
        self.assertFalse(any('POLICY_DISCOUNT_REPLY 候选1' in e for e in self.errors(self.price,'理解您的顾虑，这款不提供议价折扣。')))
        self.assertFalse(any('POLICY_DISCOUNT_REPLY 候选1' in e for e in self.errors(self.price,'理解您的顾虑，我们无法提供议价折扣。')))

    def test_client_color_preference_is_not_product_color_evidence(self):
        request=copy.deepcopy(BASES[4])
        self.assertTrue(any('GROUNDING_PRODUCT_COLOR' in e for e in self.errors(request,'邀请您看看这款岩灰色皮具。')))
        self.assertFalse(any('GROUNDING_PRODUCT_COLOR' in e for e in self.errors(request,'您偏爱岩灰色，这款的目录配色是墨黑和砂白。')))

    def test_near_copies_trigger_correction(self):
        parsed={'status':'generated','messages':['您可以慢慢考虑，不必急着决定，有具体问题再告诉我。','您可以慢慢考虑，不必急着决定，有具体问题再告诉我！','理解您的顾虑，这款不提供议价折扣。']}
        self.assertTrue(any('DIVERSITY_NEAR_COPY' in e for e in check_grounding(parsed,self.price)[0]))

    def test_shared_event_logistics_do_not_alone_establish_duplication(self):
        request=copy.deepcopy(BASES[4]);ctx=request['scenario_context']
        shared=f"{ctx['title']}，2026年11月8日14:00，{ctx['venue']}。"
        parsed={'status':'generated','messages':[shared+'想邀请您来看看包型，您方便时回复即可。',shared+'如果您想了解手提设计，可以现场看看，是否参与按您的安排就好。',shared+'您可以慢慢安排时间，有兴趣的话回复我了解详情。']}
        self.assertFalse(any('DIVERSITY_NEAR_COPY' in e for e in check_grounding(parsed,request)[0]))

    def test_event_omissions_and_wrong_minutes_are_rejected(self):
        request=copy.deepcopy(BASES[4]);ctx=request['scenario_context']
        for text in [f"邀请您参加{ctx['title']}，11月8日14:30，{ctx['venue']}。",f"邀请您参加{ctx['title']}，11月8日14:00，请回复。"]:
            errors=self.errors(request,text)
            self.assertTrue(any('EVENT_TIME 候选1' in e or 'EVENT_LOGISTICS 候选1' in e for e in errors))

    def test_source_backed_short_event_name_is_allowed(self):
        request=copy.deepcopy(BASES[4]);ctx=request['scenario_context']
        text=f"邀请您参加私享预览，11月8日14:00在{ctx['venue']}举行。"
        self.assertFalse(any('EVENT_LOGISTICS 候选1' in e for e in self.errors(request,text)))
        self.assertTrue(any('EVENT_LOGISTICS 候选1' in e for e in self.errors(request,text.replace('私享预览','另一场活动'))))

    def test_price_candidates_need_distinct_fact_and_autonomy_approaches(self):
        texts=['理解您的顾虑，这款不提供议价折扣。','目录价18800元，不支持议价折扣。','谢谢您的理解，不提供议价折扣。']
        errors=check_grounding({'status':'generated','messages':texts},self.price)[0]
        self.assertTrue(any('DIVERSITY_PRICE_FACT' in e for e in errors))
        self.assertTrue(any('DIVERSITY_PRICE_SPACE' in e for e in errors))
        texts[1]='这款采用粒面牛皮，不提供议价折扣。';texts[2]='您可以慢慢考虑，这款不提供议价折扣。'
        errors=check_grounding({'status':'generated','messages':texts},self.price)[0]
        self.assertFalse(any('DIVERSITY_PRICE_' in e for e in errors))
        texts[0]+='采用粒面牛皮。'
        self.assertTrue(any('DIVERSITY_PRICE_OVERLOAD' in e for e in check_grounding({'status':'generated','messages':texts},self.price)[0]))

    def test_service_retries_grounding_failure_and_keeps_raw_attempt(self):
        unsafe=['您的包已到手，感谢选择。','您的包已经收到，可用干布轻拭。','您的包已收到，建议放入防尘袋。']
        safe=['关于这只包，您是否有想了解的使用细节？','日常清洁可用干净柔软的干布轻拭。','暂时不用时，保持干燥并放入随附防尘袋。']
        class Adapter:
            is_live=False;available=True;calls=0
            def complete(self,messages):
                self.calls+=1
                return {'content':json.dumps({'status':'generated','messages':unsafe if self.calls==1 else safe}),'finish_reason':'stop'}
        adapter=Adapter()
        with tempfile.TemporaryDirectory() as folder:
            artifact=GenerationService(config=Config(provider='ollama'),adapter=adapter,store=RunStore(Path(folder)/'runs.sqlite3')).generate(self.care)
        self.assertEqual(adapter.calls,2)
        self.assertEqual(artifact['response']['status'],'generated')
        self.assertTrue(any('GROUNDING_RECEIPT' in e for e in artifact['attempts'][0]['validation_errors']))
        self.assertIn('已到手',json.loads(artifact['attempts'][0]['content'])['messages'][0])
        self.assertEqual(artifact['response']['candidates'][0]['text'],self.care['client']['preferred_address']+'，'+safe[0])
        self.assertEqual(artifact['attempts'][1]['client_copy_composition']['original_messages'],safe)
        self.assertEqual(json.loads(artifact['attempts'][1]['content'])['messages'],safe)


if __name__=='__main__':unittest.main()
