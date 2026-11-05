"""eval-v0.1 scoring. Missing human ratings are pending, never passes."""

import json
from datetime import datetime
from collections import Counter, defaultdict
from math import ceil

from .output_checks import parse_output, quality_flags
from .grounding import check_grounding

WEIGHTS = {"personalization": .15, "brand": .15, "naturalness": .15, "scenario_fit": .15, "grounding": .20, "respect": .10}


def rating_template(artifact):
    response = artifact["response"]
    return {"run_id": response["metadata"]["run_id"], "case_id": response["case_id"], "rubric_version": "eval-v0.1", "assessor": None, "assessed_at": None, "candidate_scores": [{"candidate_id": i, **{k: None for k in WEIGHTS}} for i in [1, 2, 3]], "diversity": None, "hard_failures": [], "review_complete": False, "notes": "Provide source-grounded evidence for findings; do not auto-fill ratings."}


def evaluate(artifact, rating=None):
    response = artifact["response"]
    base = {"case_id": response["case_id"], "run_id": response["metadata"]["run_id"], "scenario": response["scenario"], "status": "pending", "raw_score": None, "effective_score": None, "hard_failures": [], "flags": []}
    if artifact.get("execution_kind") != "live":
        return {**base, "status": "excluded", "reason": "Not an actual provider run."}
    if response["status"] != "generated":
        return {**base, "status": "fail", "effective_score": 0, "reason": response["status"]}
    messages = [c["text"] for c in response["candidates"]]
    _, errors = parse_output(json.dumps({"status": "generated", "messages": messages}))
    if not errors:
        grounding_errors, diversity = check_grounding({"status": "generated", "messages": messages}, artifact["request"])
        errors.extend(grounding_errors)
        base["diversity_checks"] = diversity
    if [c["candidate_id"] for c in response["candidates"]] != [1, 2, 3]:
        errors.append("HF-01: invalid candidate IDs")
    if errors:
        return {**base, "status": "fail", "effective_score": 0, "hard_failures": errors}
    base["flags"] = quality_flags(messages)
    if not rating or not rating.get("review_complete"):
        return base
    if rating.get("run_id") != base["run_id"] or rating.get("case_id") != base["case_id"] or rating.get("rubric_version") != "eval-v0.1":
        raise ValueError("Rating is linked to a different case/run/rubric.")
    if not rating.get("assessor") or not rating.get("assessed_at"):
        raise ValueError("Completed human review requires assessor and timestamp.")
    try:
        assessed_at = datetime.fromisoformat(rating["assessed_at"].replace("Z", "+00:00"))
        if assessed_at.tzinfo is None: raise ValueError("Missing timezone")
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Assessment time must be an ISO timestamp with timezone.") from None
    scores = rating.get("candidate_scores", [])
    if len(scores) != 3 or [s.get("candidate_id") for s in scores] != [1, 2, 3]:
        raise ValueError("Three candidate score records are required.")
    values = [s.get(k) for s in scores for k in WEIGHTS] + [rating.get("diversity")]
    if any(type(v) is not int or not 1 <= v <= 5 for v in values):
        raise ValueError("All scores must be integer values 1–5.")
    failures = rating.get("hard_failures", [])
    if not isinstance(failures, list) or any(not isinstance(f, dict) or not all(f.get(k) for k in ['id','evidence','source']) or f.get('id') not in {f'HF-{i:02}' for i in range(1,7)} for f in failures):
        raise ValueError("Hard failures require id, evidence and source.")
    raw = sum(weight * sum(s[k] for s in scores) / 3 for k, weight in WEIGHTS.items()) + .10 * rating["diversity"]
    passed = not failures and min(values) >= 3 and raw >= 4
    return {**base, "status": "pass" if passed else "fail", "raw_score": raw, "effective_score": 0 if failures else raw, "hard_failures": failures}


def summarize(results):
    counts = Counter(r["status"] for r in results)
    by_scenario = defaultdict(list)
    for row in results:
        by_scenario[row["scenario"]].append(row)
    target_counts = {'greeting':8,'product_recommendation':9,'post_purchase_care':8,'reactivation':8,'event_invitation':8,'price_objection':9}
    complete = len(results) == 50 and len({r['case_id'] for r in results}) == 50 and Counter(r['scenario'] for r in results) == Counter(target_counts) and not counts['pending'] and not counts['excluded']
    mean = sum(r['effective_score'] or 0 for r in results) / len(results) if complete else None
    scenario_rates = {s:{'total':len(rows),'passed':sum(r['status']=='pass' for r in rows),'required_passes':ceil(.75*len(rows))} for s,rows in by_scenario.items()}
    quality_acceptance = complete and counts['pass'] >= 45 and mean >= 4 and not any(r['hard_failures'] for r in results) and all(v['passed']>=v['required_passes'] for v in scenario_rates.values())
    return {'rubric_version':'eval-v0.1','counts':dict(counts),'total':len(results),'complete_50_case_human_review':bool(complete),'mean_effective_score':mean,'per_scenario':scenario_rates,'quality_targets_met':bool(quality_acceptance),'release_accepted':False,'release_note':'Quality targets alone do not establish release acceptance; guardrail results and a single frozen configuration must also be verified.'}
