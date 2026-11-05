"""Preflight by default; --execute explicitly enables real local or remote model calls."""

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from client_advisor.config import Config
from client_advisor.contracts import validate_request
from client_advisor.rules import preflight
from client_advisor.service import GenerationService


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=ROOT/'data/generation-cases.json')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1: parser.error('--limit must be positive')
    raw = args.dataset.read_bytes();dataset = json.loads(raw)
    cases = dataset['cases'][:args.limit] if args.limit else dataset['cases']
    if not args.execute:
        checks=[]
        for row in cases:
            errors=validate_request(row['request'])
            state='invalid_input' if errors else ((preflight(row['request'])[0] or {}).get('status','generation_eligible'))
            expected='generation_eligible' if row['expected_status']=='generated' else row['expected_status']
            checks.append({'case_id':row['case_id'],'expected_preflight':expected,'actual_preflight':state,'passed':state==expected})
        report={'mode':'preflight_only','model_calls':0,'cases':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks)}
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if all(c['passed'] for c in checks) else 1
    config=Config.load()
    if config.provider == 'openai' and not config.api_key:
        print('OPENAI_API_KEY is not configured. No model calls were made.',file=sys.stderr);return 2
    output=args.output or ROOT/'runs'/('batch-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid4().hex[:6])
    if args.resume:
        if not (output/'manifest.json').exists():parser.error('Resume requires an existing batch manifest.')
        manifest=json.loads((output/'manifest.json').read_text())
        if manifest['dataset_hash'] != hashlib.sha256(raw).hexdigest() or manifest['config'] != config.public():parser.error('Dataset/configuration changed; use a new batch directory.')
    else:
        output.mkdir(parents=True,exist_ok=False)
        manifest={'batch_id':output.name,'dataset_hash':hashlib.sha256(raw).hexdigest(),'dataset_version':dataset['dataset_version'],'config':config.public(),'dataset_path':str(args.dataset.resolve()),'cases':[{'case_id':r['case_id'],'scenario':r['scenario'],'expected_status':r['expected_status']} for r in cases]}
        (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    if [r['case_id'] for r in cases] != [r['case_id'] for r in manifest['cases']]:parser.error('Resume must use the original case selection/limit.')
    service=GenerationService(config=config);failed=0
    for row in cases:
        request=copy.deepcopy(row['request']);request['request_id']=f"{manifest['batch_id']}:{request['request_id']}"
        artifact=service.generate(request)
        if any(n['code'] in {'REQUEST_ID_CONFLICT','REQUEST_IN_PROGRESS'} for n in artifact['response']['notices']):
            print('Request identity conflict/in-progress; original artifacts preserved.',file=sys.stderr);return 2
        (output/(row['case_id']+'.json')).write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
        status=artifact['response']['status'];failed+=status!=row['expected_status'];print(row['case_id'],status)
    print('Batch artifacts:',output)
    return 1 if failed else 0


if __name__=='__main__':raise SystemExit(main())
