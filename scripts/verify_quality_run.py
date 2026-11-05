"""Verify raw inference, source composition, export and strict AI-review linkage."""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from client_advisor.output_checks import parse_output
from client_advisor.grounding import check_grounding
from client_advisor.rules import preflight
from client_advisor.reference_drafts import references
from client_advisor.greeting_composition import compose_greeting
from client_advisor.recommendation_composition import compose_recommendation
from client_advisor.event_composition import compose_event
from client_advisor.client_copy import compose_client_copy

def verify(version):
 batch=ROOT/'runs'/('full-50-'+version);freeze=json.loads((ROOT/'docs/verification'/('evaluation-freeze-'+version+'.json')).read_text())
 assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in freeze['source_hashes'].items()),'Frozen source changed'
 dataset=ROOT/'data/generation-cases.json';expected=json.loads(dataset.read_text())['cases'];manifest=json.loads((batch/'manifest.json').read_text())
 assert manifest['dataset_hash']==hashlib.sha256(dataset.read_bytes()).hexdigest()
 assert [c['case_id'] for c in manifest['cases']]==[c['case_id'] for c in expected] and len(expected)==50
 configs=set();hashes={};attempts=0;tokens=0;refmatches=0;transforms=0;retry_cases=[];results=[]
 for row in expected:
  p=batch/(row['case_id']+'.json');a=json.loads(p.read_text());q=a['request'];response=a['response'];configs.add(json.dumps(a['config'],sort_keys=True))
  stripped=dict(q);stripped['request_id']=row['request']['request_id'];assert stripped==row['request'],'Changed input'
  assert a['execution_kind']=='live' and response['status']=='generated' and len(response['candidates'])==3
  assert a['tool']=='tool-'+version and a['prompt']=='prompt-'+version
  assert a['config']['provider']=='ollama' and a['config']['model']=='qwen3:4b' and a['config']['temperature']==0
  assert response['metadata']['generation_attempts']==len(a['attempts'])
  attempts+=len(a['attempts']);tokens+=sum(t.get('usage',{}).get('total_tokens',0) for t in a['attempts'])
  if len(a['attempts'])>1:retry_cases.append(row['case_id'])
  last=a['attempts'][-1];raw,errors=parse_output(last['content']);assert not errors and raw['status']=='generated'
  _,derived,_=preflight(q)
  refs=references(q,derived);assert last['editorial_reference']['program_authored_references']==refs
  address=q['client'].get('preferred_address')
  passed_refs=[s[len(address):].lstrip('，,：: ') if address and s.startswith(address) else s for s in refs]
  refmatches+=sum(s==r for s,r in zip(raw['messages'],passed_refs))
  if q['scenario']=='greeting':raw,meta,errors=compose_greeting(raw,q)
  elif q['scenario']=='product_recommendation':raw,meta,errors=compose_recommendation(raw,q,derived)
  elif q['scenario']=='event_invitation':raw,meta,errors=compose_event(raw,q)
  else:meta=None;errors=[]
  assert not errors
  if meta:assert meta==last['structured_composition']
  raw,copy_meta,errors=compose_client_copy(raw,q);assert not errors and copy_meta==last['client_copy_composition']
  transforms+=len(copy_meta['transformations'])
  assert not check_grounding(raw,q)[0]
  assert raw['messages']==[c['text'] for c in response['candidates']]
  hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();results.append(a)
 assert len(configs)==1
 with (batch/'test-cases.csv').open(encoding='utf-8-sig',newline='') as f:
  rows=list(csv.DictReader(f));assert len(rows)==50 and len(rows[0])==8
  for r,a in zip(rows,results):
   assert r['Case ID']==a['request']['case_id']
   assert [r[f'Output {i}'] for i in [1,2,3]]==[c['text'] for c in a['response']['candidates']]
 review=ROOT/'docs/verification'/('ai-quality-review-'+version)
 scores=json.loads((review/'ratings.json').read_text());summary=json.loads((review/'summary.json').read_text())
 assert len(scores['ratings'])==50 and summary['required_pass_cases']==50
 for r in scores['ratings']:assert hashes[r['source_artifact']]==r['source_sha256']
 assert summary['human_acceptance_complete'] is False and summary['release_accepted'] is False
 human=ROOT/'docs/verification/human-ratings-v0.8.2.json'
 assert hashlib.sha256(human.read_bytes()).hexdigest()=='5737d9d9d1ef232439af8eb0ebd6671a6434b7856c62d9015e04270c4a76dc24'
 return dict(version=version,verified_at=datetime.now().astimezone().isoformat(),cases=50,candidates=150,provider_attempts=attempts,within_run_retry_cases=retry_cases,extra_recovery_requests=0,single_frozen_configuration=True,frozen_source_hashes_match=True,original_dataset_preserved=True,raw_to_composition_to_export_verified=True,reference_body_exact_matches=refmatches,reference_body_total=150,client_copy_transformed_candidates=transforms,reported_total_tokens=tokens,ai_threshold_met_cases=summary['ai_threshold_met_cases'],strict_ai_target_met=summary['ai_overall_threshold_met'],human_acceptance_complete=False,release_accepted=False,original_human_template_unchanged=True,source_hashes=hashes)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--version',default='v0.9.7');a=p.parse_args();report=verify(a.version)
 out=ROOT/'docs/verification'/('full-50-integrity-'+a.version+'.json');out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='source_hashes'},indent=2))
if __name__=='__main__':main()
