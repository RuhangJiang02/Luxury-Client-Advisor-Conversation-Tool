"""Aggregate explicitly AI-authored reviews; never populate human acceptance records."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/verification/ai-quality-review-v0.8.2'
WEIGHTS = dict(personalization=15, brand=15, naturalness=15, scenario_fit=15, grounding=20, respect=10)
EXPECTED = dict(greeting=8, product_recommendation=9, post_purchase_care=8, reactivation=8, event_invitation=8, price_objection=9)


def aggregate(data):
    if data['assessor']['kind'] != 'ai' or data['human_review_complete'] is not False:
        raise ValueError('Only explicitly AI-authored, non-human reviews accepted')
    rows = data['ratings']
    source_batch = ROOT / data.get('source_batch', 'runs/full-50-v0.8.2')
    required_pass_cases = data.get('required_pass_cases', 45)
    if required_pass_cases not in {45, 50}: raise ValueError('Unsupported target')
    if len(rows) != 50 or len({r['case_id'] for r in rows}) != 50 or Counter(r['scenario'] for r in rows) != Counter(EXPECTED):
        raise ValueError('Expected fixed 50-case allocation')
    results, candidates = [], []
    for r in rows:
        source = ROOT / r['source_artifact']
        if source.resolve().parent != source_batch.resolve():
            raise ValueError('Unexpected source path')
        if hashlib.sha256(source.read_bytes()).hexdigest() != r['source_sha256']:
            raise ValueError('Source hash mismatch')
        a = json.loads(source.read_text())
        if a['response']['metadata']['run_id'] != r['run_id'] or a['request']['case_id'] != r['case_id'] or a['request']['scenario'] != r['scenario']:
            raise ValueError('Case/run/scenario mismatch')
        scores = r['candidate_scores']
        if [s['candidate_id'] for s in scores] != [1, 2, 3] or r['human_adjudication_complete'] is not False:
            raise ValueError('Invalid candidate IDs or human attribution')
        values = [s[k] for s in scores for k in WEIGHTS] + [r['diversity']]
        if any(type(v) is not int or not 1 <= v <= 5 for v in values):
            raise ValueError('Scores must be integer 1–5')
        hf = r['hard_failures_suggested_by_ai']
        for f in hf:
            if f['rule_id'] not in {f'HF-{i:02}' for i in range(1, 7)} or f['candidate_id'] not in [1, 2, 3] or not f.get('evidence') or not f.get('excerpt') or f.get('human_adjudication_required') is not True:
                raise ValueError('AI hard-failure finding needs evidence and human adjudication')
        raw = sum(Fraction(w * sum(s[k] for s in scores), 300) for k, w in WEIGHTS.items()) + Fraction(r['diversity'], 10)
        effective = Fraction(0) if hf else raw
        reasons = []
        if min(values) < 3: reasons.append('dimension_or_diversity_below_3')
        if raw < 4: reasons.append('weighted_score_below_4')
        if hf: reasons.append('AI_suggested_hard_failure_pending_adjudication')
        results.append(dict(case_id=r['case_id'], scenario=r['scenario'], raw_score=float(raw), conservative_effective_score=float(effective), ai_threshold_met=not reasons, reasons='; '.join(reasons), diversity=r['diversity'], run_id=r['run_id'], source_sha256=r['source_sha256']))
        for s, c in zip(scores, a['response']['candidates']):
            if s['candidate_id'] != c['candidate_id']: raise ValueError('Candidate linkage mismatch')
            candidates.append(dict(case_id=r['case_id'], scenario=r['scenario'], **s, text=c['text'], diversity=r['diversity'], source_artifact=r['source_artifact'], source_sha256=r['source_sha256'], run_id=r['run_id']))
    groups = defaultdict(list)
    for r in results: groups[r['scenario']].append(r)
    summary = dict(assessment_kind=data['assessment_kind'], ai_review_complete=True, human_acceptance_complete=False, release_accepted=False, cases=50, candidates=150, ai_threshold_met_cases=sum(r['ai_threshold_met'] for r in results), mean_raw_score=sum(r['raw_score'] for r in results)/50, mean_conservative_effective_score=sum(r['conservative_effective_score'] for r in results)/50, suggested_hard_failure_cases=sum(bool(r['hard_failures_suggested_by_ai']) for r in rows), scenario_results={k:dict(total=len(v), ai_threshold_met=sum(r['ai_threshold_met'] for r in v), required=len(v) if required_pass_cases == 50 else (3*len(v)+3)//4) for k,v in groups.items()})
    summary['required_pass_cases'] = required_pass_cases
    summary['source_batch'] = str(source_batch.relative_to(ROOT))
    summary['ai_overall_threshold_met'] = summary['ai_threshold_met_cases'] >= required_pass_cases and summary['mean_conservative_effective_score'] >= 4 and not summary['suggested_hard_failure_cases'] and all(v['ai_threshold_met'] >= v['required'] for v in summary['scenario_results'].values())
    return summary, results, candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-dir', type=Path, default=OUT)
    args=parser.parse_args()
    output=args.review_dir
    summary, cases, candidates = aggregate(json.loads((output/'ratings.json').read_text()))
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    for name, rows in [('case-scores.csv',cases), ('candidate-scores.csv',candidates)]:
        with (output/name).open('w', newline='') as f:
            w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    queue=[dict(case_id=r['case_id'], priority='P0' if 'hard_failure' in r['reasons'] else 'P1', ai_findings=r['reasons'], human_assessor=None, human_decision=None, human_evidence=None) for r in cases if not r['ai_threshold_met']]
    queue.sort(key=lambda r:(r['priority'],r['case_id']))
    (output/'human-adjudication-queue.json').write_text(json.dumps(queue,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__': main()
