"""Local inference boundary tests; no actual model or external calls."""

import json
import os
import unittest
from unittest.mock import patch

from client_advisor.config import Config
from client_advisor.llm import OllamaAdapter, ProviderError


class OllamaTests(unittest.TestCase):
    def test_local_config_excludes_openai_key(self):
        with patch.dict(os.environ, {'LLM_PROVIDER':'ollama','OPENAI_API_KEY':'fake-private-value'}, clear=True):
            config=Config.load()
        self.assertEqual(config.provider,'ollama')
        self.assertEqual(config.api_key,'')
        self.assertNotIn('fake-private-value',json.dumps(config.public()))

    def test_nonlocal_endpoint_and_cloud_tag_are_rejected(self):
        for settings in [{'OLLAMA_BASE_URL':'http://example.com:11434'}, {'OLLAMA_MODEL':'qwen3:cloud'}, {'OLLAMA_BASE_URL':'http://user:pass@127.0.0.1:11434'}]:
            with self.subTest(settings=settings), patch.dict(os.environ,{'LLM_PROVIDER':'ollama',**settings},clear=True):
                with self.assertRaises(ValueError):Config.load()

    def test_native_request_has_no_auth_and_ignores_thinking(self):
        class Response:
            status_code=200
            def json(self):return {'message':{'content':'{"status":"generated","messages":["一","二","三"]}','thinking':'do not store'},'done':True,'done_reason':'stop','model':'qwen3:4b','prompt_eval_count':10,'eval_count':12}
        class Transport:
            def post(self,url,**kwargs):
                self.url,self.kwargs=url,kwargs
                return Response()
        transport=Transport()
        config=Config(provider='ollama',base_url='http://127.0.0.1:11434',model='qwen3:4b',api_key='must-not-be-forwarded')
        output=OllamaAdapter(config,transport).complete([])
        self.assertEqual(transport.url,'http://127.0.0.1:11434/api/chat')
        self.assertNotIn('headers',transport.kwargs)
        self.assertFalse(transport.kwargs['json']['think'])
        self.assertEqual(transport.kwargs['json']['options']['num_ctx'],16384)
        self.assertNotIn('do not store',json.dumps(output))
        self.assertNotIn('must-not-be-forwarded',json.dumps(transport.kwargs))
        self.assertEqual(output['usage']['total_tokens'],22)

    def test_missing_model_is_terminal(self):
        class Response:status_code=404
        class Transport:
            def post(self,*args,**kwargs):return Response()
        with self.assertRaises(ProviderError) as error:
            OllamaAdapter(Config(provider='ollama'),Transport()).complete([])
        self.assertEqual(error.exception.code,'OLLAMA_MODEL_MISSING')
        self.assertFalse(error.exception.retryable)

    def test_loopback_session_disables_environment_proxy(self):
        adapter=OllamaAdapter(Config(provider='ollama'))
        self.assertFalse(adapter.transport.trust_env)


if __name__=='__main__':unittest.main()
