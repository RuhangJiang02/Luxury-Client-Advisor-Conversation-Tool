"""Verify six Streamlit flows with explicit test doubles; no real provider calls.

Results are UI wiring evidence, never actual LLM outputs or human scores.
"""
import argparse
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from streamlit.testing.v1 import AppTest
from client_advisor import TOOL_VERSION,PROMPT_VERSION
from client_advisor.config import Config
from client_advisor.llm import ProviderError
from client_advisor.run_store import RunStore
from client_advisor.service import GenerationService

SCENARIOS=['greeting','product_recommendation','post_purchase_care','reactivation','event_invitation','price_objection']
BODIES={
 'greeting':['愿您顺心自在。','愿您有时间做喜欢的事。','愿您轻松开心，常有欢喜。'],
 'product_recommendation':['您平时主要带哪些随身物品？','您更习惯怎样整理这些物品？','您有没有特别在意的空间需求？'],
 'post_purchase_care':['关于这只包，您有想了解的养护问题吗？','日常清洁可用干净柔软的干布轻拭。','暂时不用时，保持干燥并放入随附防尘袋。'],
 'reactivation':['您好，最近还好吗？','您最近喜欢的颜色有变化吗？','您方便的时候再聊就好。'],
 'event_invitation':['想邀请您来看看，有兴趣可回复我。','如果想了解旋锁设计，您可以来现场看看。','您按自己的安排考虑，不必特意调整时间。'],
 'price_objection':['理解您的顾虑，这款不提供议价折扣。','这款采用粒面牛皮，不提供议价折扣。','您可以慢慢考虑，不急着决定；这款不提供议价折扣。'],
}


def verify():
 config=Config(provider='ollama',model='ui-demo-test-double',base_url='http://127.0.0.1:11434')
 checks=[];invocations=[];provider_calls=[];simulate_failure=[False]
 original_generate=GenerationService.generate
 default_db=ROOT/'runs/runs.sqlite3'
 default_db_before=hashlib.sha256(default_db.read_bytes()).hexdigest() if default_db.exists() else None
 def require(condition,name):
  if not condition:raise AssertionError(name)
  checks.append({'check':name,'passed':True})
 with tempfile.TemporaryDirectory(prefix='chengxu-ui-demo-') as temp:
  store=RunStore(Path(temp)/'ui.sqlite3')
  class Adapter:
   is_live=False;available=True
   def __init__(self,scenario):self.scenario=scenario
   def complete(self,messages):
    provider_calls.append(self.scenario)
    if simulate_failure[0]:raise ProviderError('OLLAMA_UNREACHABLE')
    return {'content':json.dumps({'status':'generated','messages':BODIES[self.scenario]},ensure_ascii=False),'finish_reason':'stop','reported_model':'ui-demo-test-double'}
  def generate(_service,request):
   scenario=request.get('scenario','greeting') if isinstance(request,dict) else 'greeting'
   artifact=original_generate(GenerationService(config=config,adapter=Adapter(scenario),store=store),request)
   invocations.append({'scenario':scenario,'status':artifact['response']['status'],'execution_kind':artifact['execution_kind'],'attempts':len(artifact['attempts'])})
   return artifact
  with patch.object(Config,'load',return_value=config),patch.object(GenerationService,'generate',generate),patch('client_advisor.service.RunStore',return_value=store),patch('client_advisor.llm.requests.Session.post',side_effect=AssertionError('Unexpected real network call')),patch('client_advisor.llm.requests.post',side_effect=AssertionError('Unexpected real network call')):
   app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=25).run()
   require(not app.exception,'initial render')
   for scenario in SCENARIOS:
    app.selectbox(key='scenario-selector').set_value(scenario).run()
    require(not app.exception and len(app.session_state[f'result-preview-{scenario}']['response']['candidates'])==3,f'{scenario}: preview shows three labelled template candidates')
   require(len(provider_calls)==0 and len(invocations)==0,'preview and scenario switching make no service/provider calls')
   app.radio(key='generation-mode').set_value('live').run()
   require('本地模型真实生成' in app.radio(key='generation-mode').options,'local mode label')
   require(len(invocations)==0,'switch to live does not generate')
   for scenario in SCENARIOS:
    app.selectbox(key='scenario-selector').set_value(scenario).run()
    require(f'result-live-{scenario}' not in app.session_state,f'{scenario}: live waits for explicit submit')
    next(b for b in app.button if b.label=='生成三条候选消息 →').click().run()
    response=app.session_state[f'result-live-{scenario}']['response']
    require(not app.exception and response['status']=='generated' and len(response['candidates'])==3,f'{scenario}: explicit submit succeeds with test double')
    count=len(provider_calls);rid=response['metadata']['run_id']
    app.button(key=f'choose-{scenario}-1').click().run()
    require(len(provider_calls)==count and app.session_state[f'selection-{scenario}']['run_id']==rid,f'{scenario}: selection does not regenerate')
    require(len(app.get('download_button'))==1,f'{scenario}: JSON download control present')
   app.selectbox(key='scenario-selector').set_value('greeting').run()
   prior=app.session_state['result-live-greeting']['response']['metadata']['run_id'];count=len(provider_calls)
   app.text_input(key='greeting-address').set_value('演示客户').run()
   require(app.session_state['result-live-greeting']['response']['metadata']['run_id']==prior and len(provider_calls)==count,'unsubmitted field edits preserve prior submitted result and do not generate')
   for name,expected in [('blocked-contact','blocked'),('unknown-permission','needs_clarification'),('missing-venue','needs_clarification'),('over-budget','needs_clarification'),('invalid-unknown-field','invalid_input')]:
    request=json.loads((ROOT/'examples/ui-demo'/f'{name}.json').read_text());scenario=request['scenario'];app.selectbox(key='scenario-selector').set_value(scenario).run()
    app.checkbox(key=f'{scenario}-use-json').set_value(True)
    app.text_area(key=f'{scenario}-json').set_value(json.dumps(request,ensure_ascii=False))
    count=len(provider_calls);next(b for b in app.button if b.label=='生成三条候选消息 →').click().run()
    response=app.session_state[f'result-live-{scenario}']['response']
    require(not app.exception and response['status']==expected and not response['candidates'] and len(provider_calls)==count,f'{name}: {expected}, zero provider calls')
   app.selectbox(key='scenario-selector').set_value('greeting').run();app.checkbox(key='greeting-use-json').set_value(True);app.text_area(key='greeting-json').set_value('{broken')
   count=len(provider_calls);next(b for b in app.button if b.label=='生成三条候选消息 →').click().run()
   response=app.session_state['result-live-greeting']['response'];require(response['status']=='invalid_input' and len(provider_calls)==count,'malformed editor JSON returns invalid_input without provider call')
   request=json.loads((ROOT/'examples/ui-demo/greeting.json').read_text());app.text_area(key='greeting-json').set_value(json.dumps(request,ensure_ascii=False));simulate_failure[0]=True
   count=len(provider_calls);next(b for b in app.button if b.label=='生成三条候选消息 →').click().run()
   response=app.session_state['result-live-greeting']['response'];require(not app.exception and response['status']=='generation_failed' and not response['candidates'] and len(provider_calls)==count+1,'simulated unavailable model returns explicit failure with no fallback')
   require(all(i['execution_kind']=='test_double' for i in invocations),'all saved demo service artifacts are labelled test_double')
   after=hashlib.sha256(default_db.read_bytes()).hexdigest() if default_db.exists() else None
   require(after==default_db_before,'default app database remains absent or byte-identical')
 return {'verification_version':'ui-demo-verification-v0.1','tool_version':TOOL_VERSION,'prompt_version':PROMPT_VERSION,'verified_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'timezone':'Asia/Shanghai','app_sha256':hashlib.sha256((ROOT/'app.py').read_bytes()).hexdigest(),'verification_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'AppTest UI/service wiring only; no real LLM calls or quality scores','checks':checks,'passed':len(checks),'fake_provider_calls':len(provider_calls),'actual_model_calls':0,'fixed_50_cases_rerun':False,'human_scores_added':False,'service_invocations':invocations,'storage':'temporary test database removed after verification','default_run_database_unchanged':True,'not_verified':['native browser file download','browser visual appearance','actual model quality']}


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args();report=verify()
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'actual_model_calls':0,'fake_provider_calls':report['fake_provider_calls'],'fixed_50_cases_rerun':False},indent=2))

if __name__=='__main__':main()
