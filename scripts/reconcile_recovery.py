"""Create a provenance-preserving view using every failed-case recovery, never best-of selection."""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

IDENTITY_FIELDS=('tool','prompt','config','rules_hash','catalogue_hash','execution_kind')


def reconcile(initial, recovery, output):
    initial,recovery,output=map(Path,(initial,recovery,output))
    manifest=json.loads((initial/'manifest.json').read_text())
    recovery_manifest=json.loads((recovery/'manifest.json').read_text())
    originals={c['case_id']:json.loads((initial/(c['case_id']+'.json')).read_text()) for c in manifest['cases']}
    failed={c for c,a in originals.items() if a['response']['status']!='generated'}
    recovery_ids=[c['case_id'] for c in recovery_manifest['cases']]
    if len(set(recovery_ids))!=len(recovery_ids) or set(recovery_ids)!=failed:
        raise ValueError('Recovery must contain exactly every initially non-generated case, with no generated-case reruns.')
    selections=[]
    for row in manifest['cases']:
        case=row['case_id'];source=(recovery if case in failed else initial)/(case+'.json');artifact=json.loads(source.read_text());original=originals[case]
        if artifact['response']['case_id']!=case:raise ValueError('Artifact case identity mismatch.')
        if any(artifact.get(k)!=original.get(k) for k in IDENTITY_FIELDS):raise ValueError('Recovery changed runtime version, configuration or evidence kind.')
        original_request=copy.deepcopy(original['request']);recovered_request=copy.deepcopy(artifact['request'])
        original_request.pop('request_id',None);recovered_request.pop('request_id',None)
        if original_request!=recovered_request:raise ValueError('Recovery changed input facts.')
        selections.append((case,source,artifact))
    output.mkdir(parents=True,exist_ok=False)
    sources=[]
    for case,source,artifact in selections:
        shutil.copyfile(source,output/(case+'.json'))
        sources.append({'case_id':case,'origin':'same-version recovery' if case in failed else 'initial full baseline','source_artifact':str(source),'initial_artifact':str(initial/(case+'.json')),'run_id':artifact['response']['metadata']['run_id'],'request_id':artifact['response']['request_id'],'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    manifest.update({'batch_id':output.name,'assembly_note':'Source-preserving view of one full run plus one request per initially non-generated case, not a second independent full run. All recovery results retained, including failures.','initial_batch':str(initial),'recovery_batch':str(recovery),'source_map':'source-map.json'})
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (output/'source-map.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
    return sources


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--initial',type=Path,required=True);p.add_argument('--recovery',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();rows=reconcile(a.initial,a.recovery,a.output);print('Saved',len(rows),'source-preserving cases to',a.output)

if __name__=='__main__':main()
