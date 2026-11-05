"""Verify composition, rejection, and raw model provenance, not copy style."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from client_advisor.config import ROOT, Config
from client_advisor.event_composition import compose_event
from client_advisor.grounding import check_grounding
from client_advisor.run_store import RunStore
from client_advisor.service import GenerationService

BASE=json.loads((ROOT/'examples/io-v0.1/examples.json').read_text())['scenario_requests'][4]
BODIES=['想邀请您来看看，有兴趣回复我就好。','如果想了解旋锁设计，您可以来现场看看。','您按自己的安排考虑，不必特意调整时间。']

class EventCompositionTests(unittest.TestCase):
    def test_complete_source_facts_and_distinct_bodies_are_retained(self):
        request=copy.deepcopy(BASE)
        parsed,meta,errors=compose_event({'status':'generated','messages':BODIES},request)
        self.assertEqual(errors,[])
        self.assertEqual(check_grounding(parsed,request)[0],[])
        for i,text in enumerate(parsed['messages']):
            self.assertIn(request['scenario_context']['title'],text)
            self.assertIn(request['scenario_context']['venue'],text)
            self.assertTrue(text.endswith(BODIES[i]))
        self.assertEqual(meta['model_authored_bodies'],BODIES)
        self.assertEqual(meta['source_id'],request['scenario_context']['source_id'])

    def test_wrong_model_date_and_cross_candidate_reference_are_rejected(self):
        for text in ['活动在11月9日15:00开始。','请按如上地点前往。']:
            _,meta,errors=compose_event({'status':'generated','messages':[text,*BODIES[1:]]},BASE)
            self.assertIsNone(meta)
            self.assertTrue(errors)

    def test_non_success_is_not_replaced_with_composed_output(self):
        parsed={'status':'needs_clarification','reason':'请确认参与资格。'}
        self.assertEqual(compose_event(parsed,BASE),(parsed,None,[]))

    def test_service_preserves_raw_body_and_composition_without_fallback(self):
        raw=json.dumps({'status':'generated','messages':BODIES},ensure_ascii=False)
        class Adapter:
            is_live=False;available=True
            def complete(self,messages):return {'content':raw,'finish_reason':'stop'}
        with tempfile.TemporaryDirectory() as folder:
            a=GenerationService(config=Config(provider='ollama'),adapter=Adapter(),store=RunStore(Path(folder)/'runs.sqlite3')).generate(BASE)
        self.assertEqual(a['response']['status'],'generated')
        self.assertEqual(a['attempts'][0]['content'],raw)
        self.assertIn('structured_composition',a['attempts'][0])
        self.assertNotEqual(a['response']['candidates'][0]['text'],BODIES[0])

if __name__=='__main__':unittest.main()
