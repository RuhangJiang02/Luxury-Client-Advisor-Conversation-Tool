"""Deterministic regression tests. Fake outputs never count as quality evidence."""

import copy
import json
import tempfile
import unittest
import contextlib
import io
from pathlib import Path
from unittest.mock import patch

from client_advisor.config import Config, ROOT
from client_advisor.contracts import validate_request
from client_advisor.evaluation import evaluate, rating_template
from client_advisor.llm import OpenAIAdapter, ProviderError
from client_advisor.output_checks import parse_output
from client_advisor.rules import preflight
from client_advisor.run_store import RunStore
from client_advisor.service import GenerationService

VALID = json.dumps({"status": "generated", "messages": ["生日快乐，愿您新的一岁从容自在，日常里常有小欢喜。", "送上一份生日祝福，愿您在忙碌之余也有属于自己的轻松时光。", "祝您生日快乐，愿生活中有喜欢的风景，也有享受当下的好心情。"]}, ensure_ascii=False)


class FakeAdapter:
    is_live = False
    available = True

    def __init__(self, outcomes=None):
        self.outcomes = list(outcomes or [VALID])
        self.calls = 0

    def complete(self, messages):
        self.calls += 1
        value = self.outcomes[min(self.calls - 1, len(self.outcomes) - 1)]
        if isinstance(value, Exception):
            raise value
        return {"content": value, "finish_reason": "stop", "usage": {"total_tokens": 20}}


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = RunStore(Path(self.temp.name) / "runs.sqlite3")
        self.request = copy.deepcopy(json.loads((ROOT / 'examples/io-v0.1/examples.json').read_text())['scenario_requests'][0])

    def tearDown(self):
        self.temp.cleanup()

    def service(self, adapter=None):
        return GenerationService(config=Config(), adapter=adapter or FakeAdapter(), store=self.store)

    def test_fifty_generation_inputs_are_preflight_eligible(self):
        rows = json.loads((ROOT/'data/generation-cases.json').read_text())['cases']
        self.assertEqual(len(rows), 50)
        for row in rows:
            with self.subTest(case=row['case_id']):
                self.assertEqual(validate_request(row['request']), [])
                self.assertIsNone(preflight(row['request'])[0])

    def test_twenty_guardrails_do_not_call_provider(self):
        fake = FakeAdapter(); service = self.service(fake)
        rows = json.loads((ROOT/'data/guardrail-cases.json').read_text())['cases']
        for row in rows:
            with self.subTest(case=row['case_id']):
                result = service.generate(row['request'])['response']
                self.assertEqual(result['status'], row['expected_status'])
                self.assertEqual(result['candidates'], [])
                self.assertEqual(result['metadata']['generation_attempts'], 0)
        self.assertEqual(fake.calls, 0)

    def test_generated_run_is_durable_and_idempotent(self):
        fake = FakeAdapter(); service = self.service(fake)
        first = service.generate(self.request)
        second = service.generate(self.request)
        self.assertEqual(fake.calls, 1)
        self.assertEqual(first, second)
        self.assertEqual(len(self.store.artifacts()), 1)
        self.assertEqual(first['execution_kind'], 'test_double')

    def test_request_id_cannot_be_reused_for_other_content(self):
        fake = FakeAdapter(); service = self.service(fake)
        service.generate(self.request)
        self.request['client']['preferred_address'] = '另一位虚构客户'
        result = service.generate(self.request)['response']
        self.assertEqual(result['status'], 'invalid_input')
        self.assertEqual(fake.calls, 1)

    def test_bad_output_is_retried_once_and_original_preserved(self):
        fake = FakeAdapter(['not JSON', VALID])
        result = self.service(fake).generate(self.request)
        self.assertEqual(result['response']['status'], 'generated')
        self.assertEqual(len(result['attempts']), 2)
        self.assertEqual(result['attempts'][0]['content'], 'not JSON')
        self.assertIn('previous attempt failed', result['attempts'][1]['messages'][-1]['content'])

    def test_exhausted_output_never_falls_back_to_templates(self):
        result = self.service(FakeAdapter(['bad JSON'])).generate(self.request)
        self.assertEqual(result['response']['status'], 'generation_failed')
        self.assertEqual(result['response']['candidates'], [])
        self.assertEqual(result['response']['metadata']['generation_attempts'], 2)

    def test_auth_error_is_terminal_and_transient_error_is_bounded(self):
        fake = FakeAdapter([ProviderError('HTTP_401'), VALID])
        self.assertEqual(self.service(fake).generate(self.request)['response']['status'], 'generation_failed')
        self.assertEqual(fake.calls, 1)
        self.request['request_id'] = 'transient-error'
        fake = FakeAdapter([ProviderError('HTTP_429', True), VALID])
        self.assertEqual(self.service(fake).generate(self.request)['response']['status'], 'generated')
        self.assertEqual(fake.calls, 2)

    def test_missing_key_returns_explicit_failure_without_attempt(self):
        result = self.service(OpenAIAdapter(Config(api_key=''))).generate(self.request)['response']
        self.assertEqual(result['status'], 'generation_failed')
        self.assertEqual(result['notices'][0]['code'], 'CONFIG_MISSING')
        self.assertEqual(result['metadata']['generation_attempts'], 0)

    def test_unknown_fields_wrong_types_and_scenario_mismatch_are_invalid(self):
        for change in [lambda r:r.update(extra=True), lambda r:r['client'].update(preferences='wrong'), lambda r:r.update(scenario='event_invitation')]:
            r = copy.deepcopy(self.request);change(r)
            self.assertTrue(validate_request(r))

    def test_duplicate_and_internal_output_are_rejected(self):
        for texts in [['您好']*3, ['您好','BR-02 政策','生日快乐']]:
            _, errors = parse_output(json.dumps({'status':'generated','messages':texts}))
            self.assertTrue(errors)

    def test_model_clarification_remains_non_sendable(self):
        fake = FakeAdapter([json.dumps({'status':'needs_clarification','reason':'请确认客户是否希望继续联系。'})])
        result = self.service(fake).generate(self.request)['response']
        self.assertEqual(result['status'], 'needs_clarification')
        self.assertTrue(result['clarifications'])
        self.assertEqual(result['candidates'], [])

    def test_calendar_anniversary_and_unknown_eligibility(self):
        request = copy.deepcopy(json.loads((ROOT/'examples/io-v0.1/examples.json').read_text())['scenario_requests'][2])
        request['scenario_context']['purchase']['purchased_on'] = '2025-11-04'
        self.assertTrue(preflight(request)[1]['assessment_eligible'])
        request['reference_time'] = '2026-11-05T00:00:00+08:00'
        self.assertFalse(preflight(request)[1]['assessment_eligible'])
        request['scenario_context']['purchase']['purchased_on'] = None
        self.assertIsNone(preflight(request)[1]['assessment_eligible'])

    def test_recorded_key_is_not_in_artifact(self):
        secret = 'test-secret-not-a-real-key'
        config = Config(api_key=secret)
        artifact = GenerationService(config=config, adapter=FakeAdapter(), store=self.store).generate(self.request)
        self.assertNotIn(secret, json.dumps(artifact))
        self.assertNotIn(secret, repr(config))

    def test_http_adapter_uses_json_mode_and_sanitizes_auth_body(self):
        class Response:
            status_code = 401
            text = 'sensitive provider body should never be logged'
        class Transport:
            def post(self, url, **kwargs):
                self.url, self.kwargs = url, kwargs
                return Response()
        transport = Transport(); adapter = OpenAIAdapter(Config(api_key='test-key'), transport)
        with self.assertRaises(ProviderError) as cm:adapter.complete([{'role':'user','content':'JSON please'}])
        self.assertEqual(str(cm.exception), 'HTTP_401')
        self.assertEqual(transport.kwargs['json']['response_format'], {'type':'json_object'})
        self.assertEqual(transport.url,'https://api.openai.com/v1/chat/completions')

    def test_evaluation_excludes_fake_outputs_and_keeps_unreviewed_live_pending(self):
        artifact = self.service().generate(self.request)
        self.assertEqual(evaluate(artifact)['status'],'excluded')
        artifact['execution_kind']='live'  # Scoring fixture only, not real provider evidence.
        self.assertEqual(evaluate(artifact)['status'],'pending')
        rating=rating_template(artifact)
        rating.update(assessor='fictional-test-reviewer',assessed_at='2026-11-04T21:00:00+08:00',review_complete=True,diversity=4)
        for scores in rating['candidate_scores']:
            for key in ['personalization','brand','naturalness','scenario_fit','grounding','respect']:scores[key]=4
        self.assertEqual(evaluate(artifact,rating)['status'],'pass')
        rating['hard_failures']=[{'id':'HF-02','evidence':'test fixture excerpt','source':'test fixture source'}]
        self.assertEqual(evaluate(artifact,rating)['effective_score'],0)

    def test_saved_fake_batch_is_excluded_and_cannot_be_exported_as_real(self):
        from scripts.evaluate_cases import main as evaluate_main
        from scripts.export_submission import main as export_main
        self.request['case_id']='S1-01'
        artifact=self.service().generate(self.request)
        directory=Path(self.temp.name)/'batch';directory.mkdir()
        (directory/'manifest.json').write_text(json.dumps({'cases':[{'case_id':'S1-01','scenario':'greeting','expected_status':'generated'}]}))
        (directory/'S1-01.json').write_text(json.dumps(artifact))
        with patch('sys.argv',['evaluate_cases.py','--batch',str(directory)]), contextlib.redirect_stdout(io.StringIO()):
            evaluate_main()
        report=json.loads((directory/'evaluation.json').read_text())
        self.assertEqual(report['summary']['counts'],{'excluded':1})
        self.assertFalse(report['summary']['quality_targets_met'])
        with patch('sys.argv',['export_submission.py','--batch',str(directory)]):
            with self.assertRaises(ValueError):export_main()
        self.assertFalse((directory/'test-cases.csv').exists())

    def test_pending_request_does_not_trigger_another_call(self):
        fake=FakeAdapter();service=self.service(fake)
        service.generate(self.request)
        with self.store.connect() as db:
            db.execute("UPDATE runs SET state='pending' WHERE request_id=?",(self.request['request_id'],))
        result=service.generate(self.request)['response']
        self.assertEqual(result['notices'][0]['code'],'REQUEST_IN_PROGRESS')
        self.assertEqual(fake.calls,1)

    def test_successful_http_adapter_preserves_only_needed_response_fields(self):
        class Response:
            status_code=200
            def json(self):return {'id':'fixture-response','model':'fixture-model','choices':[{'finish_reason':'stop','message':{'content':VALID,'reasoning_content':'not stored'}}],'usage':{'total_tokens':12}}
        class Transport:
            def post(self,*args,**kwargs):return Response()
        result=OpenAIAdapter(Config(api_key='fake'),Transport()).complete([])
        self.assertEqual(result['content'],VALID)
        self.assertEqual(result['usage']['total_tokens'],12)
        self.assertNotIn('reasoning_content',result)

    def test_quota_error_is_not_retried_and_body_is_not_exposed(self):
        class Response:
            status_code=429
            def json(self):return {'error':{'code':'insufficient_quota','message':'sensitive diagnostic body'}}
        class Transport:
            calls=0
            def post(self,*args,**kwargs):
                self.calls+=1
                return Response()
        transport=Transport()
        artifact=self.service(OpenAIAdapter(Config(api_key='fake'),transport)).generate(self.request)
        self.assertEqual(transport.calls,1)
        self.assertEqual(artifact['response']['status'],'generation_failed')
        self.assertEqual(artifact['attempts'][0]['error_code'],'QUOTA_INSUFFICIENT_QUOTA')
        self.assertNotIn('sensitive diagnostic body',json.dumps(artifact))


if __name__ == '__main__':unittest.main()
