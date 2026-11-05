"""UI mode and submit regression tests without provider credentials or calls."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from client_advisor.config import Config, ROOT
from client_advisor.run_store import RunStore
from client_advisor.service import GenerationService


class UITests(unittest.TestCase):
    def test_local_ui_mode_is_labelled_and_does_not_auto_generate(self):
        config=Config(provider='ollama',model='qwen3:4b',base_url='http://127.0.0.1:11434',api_key='')
        with patch.object(Config,'load',return_value=config), patch.object(GenerationService,'generate',side_effect=AssertionError('No automatic model call')):
            app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
            app.radio(key='generation-mode').set_value('live').run()
            self.assertFalse(app.exception)
            self.assertIn('本地模型真实生成',app.radio(key='generation-mode').options)
            self.assertNotIn('result-live-greeting',app.session_state)

    def test_preview_scenarios_and_explicit_live_submit(self):
        with patch.object(Config, 'load', return_value=Config(api_key='')):
            app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=20).run()
            self.assertFalse(app.exception)
            for scenario in ['greeting','product_recommendation','post_purchase_care','reactivation','event_invitation','price_objection']:
                app.selectbox(key='scenario-selector').set_value(scenario).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.session_state[f'result-preview-{scenario}']['response']['candidates']),3)
            app.radio(key='generation-mode').set_value('live').run()
            self.assertFalse(app.exception)
            self.assertNotIn('result-live-price_objection', app.session_state)
            app.selectbox(key='scenario-selector').set_value('greeting').run()
            with tempfile.TemporaryDirectory() as directory:
                service=GenerationService(config=Config(api_key=''), store=RunStore(Path(directory)/'ui.sqlite3'))
                generate=GenerationService.generate
                with patch.object(GenerationService, 'generate', lambda _,request:generate(service,request)):
                    next(b for b in app.button if b.label=='生成三条候选消息 →').click().run()
                self.assertFalse(app.exception)
                response=app.session_state['result-live-greeting']['response']
                self.assertEqual(response['status'],'generation_failed')
                self.assertEqual(response['notices'][0]['code'],'CONFIG_MISSING')
                self.assertEqual(response['metadata']['generation_attempts'],0)


if __name__=='__main__':unittest.main()
