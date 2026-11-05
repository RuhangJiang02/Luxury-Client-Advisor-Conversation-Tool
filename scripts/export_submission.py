"""Export actual preserved outputs to the brief's exact eight-column CSV."""

import argparse
import csv
import json
from pathlib import Path

COLUMNS=['Case ID','Scenario','Client information','Conversation history','Product information','Output 1','Output 2','Output 3']


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',type=Path,required=True);args=parser.parse_args()
    manifest=json.loads((args.batch/'manifest.json').read_text());provenance=[]
    for case in manifest['cases']:
        path=args.batch/(case['case_id']+'.json')
        if case['expected_status']=='generated' and path.exists():
            if json.loads(path.read_text()).get('execution_kind')!='live':
                raise ValueError('Refusing to export test doubles as actual outputs.')
    with (args.batch/'test-cases.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.writer(stream);writer.writerow(COLUMNS)
        for case in manifest['cases']:
            p=args.batch/(case['case_id']+'.json')
            if case['expected_status']!='generated':continue
            if not p.exists():
                writer.writerow([case['case_id'],'','','','','','','']);provenance.append({'case_id':case['case_id'],'status':'missing_artifact'});continue
            a=json.loads(p.read_text());r=a['request'];response=a['response']
            if a.get('execution_kind')!='live':raise ValueError('Refusing to export test doubles as actual outputs.')
            messages=[c['text'] for c in response['candidates']] if response['status']=='generated' else []
            messages=(messages+['','',''])[:3]
            writer.writerow([case['case_id'],r['scenario'],json.dumps({'client':r['client'],'interaction':r['interaction'],'scenario_context':r['scenario_context'],'reference_time':r['reference_time']},ensure_ascii=False),json.dumps(r['conversation_history'],ensure_ascii=False),json.dumps(a['resolved_products'],ensure_ascii=False) if a['resolved_products'] else 'Not applicable',*messages])
            provenance.append({'case_id':case['case_id'],'status':response['status'],'metadata':response['metadata'],'identity':a['identity']})
    (args.batch/'test-case-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n');print(args.batch/'test-cases.csv')


if __name__=='__main__':main()
