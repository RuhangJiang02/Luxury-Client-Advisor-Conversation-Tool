"""Verify product evidence, eligibility and bounded model question bodies."""
import json
import tempfile
import unittest
from pathlib import Path
from client_advisor.config import ROOT,Config
from client_advisor.recommendation_composition import compose_recommendation
from client_advisor.rules import preflight
from client_advisor.run_store import RunStore
from client_advisor.service import GenerationService
CASES={x['case_id']:x['request'] for x in json.loads((ROOT/'data/generation-cases.json').read_text())['cases']}
QUESTIONS=['您平时会携带哪些随身物品？','您对于开合方式有什么偏好？','您通常怎样安排随身物品的收纳？']

class RecommendationCompositionTests(unittest.TestCase):
    def test_only_preflight_eligible_product_is_used(self):
        r=CASES['S2-05'];_,derived,_=preflight(r)
        parsed,meta,errors=compose_recommendation({'status':'generated','messages':QUESTIONS},r,derived)
        self.assertEqual(errors,[]);self.assertEqual(meta['product_id'],'CX-B04')
        self.assertTrue(all('循线肩包' not in t for t in parsed['messages']))
        self.assertEqual(meta['model_authored_bodies'],QUESTIONS)
        self.assertIn('12800',parsed['messages'][0]);self.assertIn('20 × 14 × 6',parsed['messages'][2])

    def test_assertions_cross_references_and_guarantees_are_not_question_bodies(self):
        r=CASES['S2-01'];_,derived,_=preflight(r)
        for body in ['这款耐磨，可以保护物品。','您知道它可以保护卡片吗？','您需要20个卡位吗？']:
            self.assertTrue(compose_recommendation({'status':'generated','messages':[body,*QUESTIONS[1:]]},r,derived)[2])

    def test_instruction_copying_is_not_a_customer_question(self):
        r=CASES['S2-01'];_,derived,_=preflight(r)
        self.assertTrue(compose_recommendation({'status':'generated','messages':[QUESTIONS[0],QUESTIONS[1],'您是否有空间偏好，不写具体数字？']},r,derived)[2])

    def test_all_nine_fixed_recommendation_inputs_have_complete_supported_frames(self):
        for case,r in CASES.items():
            if r['scenario']!='product_recommendation':continue
            _,derived,_=preflight(r);parsed,meta,errors=compose_recommendation({'status':'generated','messages':QUESTIONS},r,derived)
            self.assertEqual(errors,[],case);self.assertEqual(len(parsed['messages']),3)
            self.assertTrue(all(t.endswith(q) for t,q in zip(parsed['messages'],QUESTIONS)))
            self.assertIn('catalogue.detail',meta['source_fields'])

    def test_no_fallback_on_non_success(self):
        r=CASES['S2-01'];_,derived,_=preflight(r);parsed={'status':'needs_clarification','reason':'请确认需求。'}
        self.assertEqual(compose_recommendation(parsed,r,derived),(parsed,None,[]))

    def test_service_keeps_model_questions_and_final_fact_composition(self):
        raw=json.dumps({'status':'generated','messages':QUESTIONS},ensure_ascii=False)
        class Adapter:
            is_live=False;available=True
            def complete(self,messages):return {'content':raw,'finish_reason':'stop'}
        with tempfile.TemporaryDirectory() as d:
            a=GenerationService(config=Config(provider='ollama'),adapter=Adapter(),store=RunStore(Path(d)/'runs.sqlite3')).generate(CASES['S2-01'])
        self.assertEqual(a['response']['status'],'generated');self.assertEqual(a['attempts'][0]['content'],raw)
        self.assertEqual(a['attempts'][0]['structured_composition']['model_authored_bodies'],QUESTIONS)

if __name__=='__main__':unittest.main()
