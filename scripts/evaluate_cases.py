"""Evaluate preserved artifacts; never generates messages or invents human ratings."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from client_advisor.evaluation import evaluate, rating_template, summarize
from client_advisor import TOOL_VERSION, PROMPT_VERSION


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',type=Path,required=True);parser.add_argument('--ratings',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--strict-all',action='store_true',help='Require all 50 cases rather than historical 45/50 minimum')
    args=parser.parse_args();manifest=json.loads((args.batch/'manifest.json').read_text())
    ratings=json.loads(args.ratings.read_text()) if args.ratings else []
    if len({r['run_id'] for r in ratings})!=len(ratings):parser.error('Duplicate rating run IDs.')
    by_run={r['run_id']:r for r in ratings};results=[];templates=[];identities=set()
    guardrails=all(c['expected_status']!='generated' for c in manifest['cases'])
    if not guardrails and any(c['expected_status']!='generated' for c in manifest['cases']):parser.error('Evaluate generation and guardrail populations separately.')
    for case in manifest['cases']:
        p=args.batch/(case['case_id']+'.json')
        if not p.exists():
            if guardrails:
                results.append({'case_id':case['case_id'],'expected':case['expected_status'],'actual':'missing_artifact','passed':False,'attempts':0})
            else:
                results.append({'case_id':case['case_id'],'run_id':None,'scenario':case.get('scenario'),'status':'fail','effective_score':0,'raw_score':None,'hard_failures':[],'reason':'Missing run artifact'})
            continue
        artifact=json.loads(p.read_text());rid=artifact['response']['metadata']['run_id']
        if artifact['response']['case_id']!=case['case_id']:parser.error('Artifact case ID does not match its manifest entry.')
        identities.add(json.dumps({k:artifact.get(k) for k in ['config','tool','prompt','rules_hash','catalogue_hash']},sort_keys=True))
        if case['expected_status']!='generated':
            results.append({'case_id':case['case_id'],'actual':artifact['response']['status'],'expected':case['expected_status'],'passed':artifact['response']['status']==case['expected_status'] and not artifact['response']['candidates'],'attempts':artifact['response']['metadata']['generation_attempts']})
        else:
            results.append(evaluate(artifact,by_run.get(rid)));templates.append(rating_template(artifact))
    report={'guardrail_results':results} if guardrails else {'results':results,'summary':summarize(results)}
    if not guardrails:
        if args.strict_all:
            summary=report['summary']
            summary['historical_quality_targets_met']=summary['quality_targets_met']
            summary['required_pass_cases']=50
            for rates in summary['per_scenario'].values():rates['required_passes']=rates['total']
            summary['quality_targets_met']=bool(summary['complete_50_case_human_review'] and summary['counts'].get('pass',0)==50 and summary['mean_effective_score']>=4 and not any(r['hard_failures'] for r in results))
        report['summary']['single_frozen_configuration']=len(identities)==1
        if len(identities)!=1:report['summary']['quality_targets_met']=False
    report['evaluation_implementation']={'tool_version':TOOL_VERSION,'prompt_version':PROMPT_VERSION,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'client_advisor/evaluation.py',ROOT/'client_advisor/grounding.py',ROOT/'client_advisor/source_checks.py',ROOT/'client_advisor/output_checks.py']}}
    output=args.output or args.batch/'evaluation.json';output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    template=args.batch/'human-ratings-template.json'
    if templates and not template.exists():template.write_text(json.dumps(templates,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report.get('summary',{'guardrail_cases':len(results)}),ensure_ascii=False,indent=2));print('Saved:',output)


if __name__=='__main__':main()
