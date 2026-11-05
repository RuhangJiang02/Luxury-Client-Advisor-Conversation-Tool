# D — Evaluation Report

**Evaluated output set: tool-v0.9.7 / prompt-v0.9.7.** The final tool outputs meet the internal **50/50 AI-applied case threshold**, with mean **4.3097/5** and minimum **4.1333/5**. This is AI-authored self-review of an actively tuned development set. Genuine human assessment and release acceptance remain pending. The challenge brief itself does not prescribe a numerical pass rate or human signoff.

## 1. Evaluated population and configuration

| Item | Recorded value |
| --- | --- |
| Population | Original fixed 50 fictional cases; all six required scenarios |
| Final outputs | 150 candidates, three per case |
| Tool / prompt | tool-v0.9.7 / prompt-v0.9.7 |
| Business / contract / rubric | brand-v0.1 / io-v0.1 / eval-v0.1 |
| Local provider / model | Ollama, qwen3:4b, temperature 0 |
| Actual provider attempts | 50 in the final batch |
| Within-run retries / extra recovery | 0 / 0 |
| Version/configuration integrity | One frozen configuration; original dataset and frozen source hashes match |
| Reviewer | Codex assistant, AI-authored source-based self-review |
| Actual human assessment | 0 completed; 50 pending |

[Freeze and model digest](verification/evaluation-freeze-v0.9.7.json) · [raw-to-export integrity audit](verification/full-50-integrity-v0.9.7.json) · [exact eight-column case CSV](verification/ai-quality-review-v0.9.7/full-50-cases.csv).

The final batch does not substitute nicer older candidates or assemble a mixed-version result. Earlier experiments are retained separately. No new inference or re-scoring was performed to consolidate this report.

## 2. Method and threshold

All three candidates were read against each case's exact input, known catalogue/policy facts and conversation context. Six integer 1–5 scores were assigned per candidate: personalization 15%, brand consistency 15%, naturalness 15%, scenario fit 15%, factual grounding 20% and respect/autonomy 10%. Diversity is a single 1–5 case score weighted 10%.

The case score averages each candidate dimension across the three alternatives, applies its weight, then adds weighted diversity. A case meets the AI-applied threshold when every dimension and diversity is >=3, its unrounded weighted score is >=4, and the AI review records no hard-failure finding. Verified hard failures would set effective score to zero. The strict project target is 50/50, superseding the historical 45/50 project minimum without changing weights or per-case thresholds.

A complete genuine human review is a separate internal acceptance gate. The [human evaluator output](verification/full-50-evaluation-v0.9.7.json) correctly reports all 50 as pending. The AI result below must not be read as 50 human passes or proof of release readiness.

## 3. Final quality results

| Scenario | Cases | AI threshold met | Mean case score |
| --- | ---: | ---: | ---: |
| Birthday / festival | 8 | 8/8 | 4.2750 |
| Recommendation | 9 | 9/9 | 4.2889 |
| Post-purchase care | 8 | 8/8 | 4.2542 |
| Reactivation | 8 | 8/8 | 4.2938 |
| Event invitation | 8 | 8/8 | 4.3250 |
| Price objection | 9 | 9/9 | 4.4111 |

All 150 candidates have every scored dimension >=3; all 50 diversity scores are >=3. All weighted case scores are >=4. “50/50” is a **case-level result**, not a claim that every candidate is excellent or scored 5. There is no AI hard-failure finding in the final set; a verified human zero-hard-failure result is not established.

[All 150 candidate scores, comments and texts](verification/ai-quality-review-v0.9.7/candidate-scores.csv) · [50 case scores](verification/ai-quality-review-v0.9.7/case-scores.csv) · [full source-linked AI ratings](verification/ai-quality-review-v0.9.7/ratings.json) · [summary](verification/ai-quality-review-v0.9.7/summary.json).

## 4. Engineering and evidence checks

| Check population | Recorded result | What it supports |
| --- | --- | --- |
| Unit/regression suite | 87 passed | Tested contracts, rules, providers, bounded failures, persistence, UI and composition behavior |
| Separate guardrails | 20/20 matched; zero model attempts | Expected blocked/clarification/invalid-input behavior on those cases |
| Isolated Streamlit checks | 44 passed; zero real model calls | UI/service wiring with explicit test doubles; not browser visuals or language quality |
| Final artifact reconstruction | All 150 messages match the raw → frame → client-copy → export chain | Traceability and copy integrity, not complete semantic correctness |
| Historical evidence | Old output hashes and archives preserved | Poor/intermediate results were not silently overwritten |

[Guardrails](verification/guardrails-v0.9.7.json) · [UI verification](verification/ui-demo-verification-v0.9.7.json) · [schema/threshold/source checks](verification/ai-quality-review-v0.9.7/validation.json). The 87-test result is a recorded earlier execution; documentation consolidation does not count as a new test run.

## 5. Findings across the six scenarios

| Case | Score | Source-based finding |
| --- | ---: | --- |
| S1-08 | 4.5000 | Uses advance birthday framing for a supplied future date; does not invent age or add a sales pitch |
| S2-09 | 4.3500 | Gives actual external dimensions, asks for laptop measurements and does not guarantee fit or waterproofing |
| S3-06 | 4.4333 | Responds to water contact now, retains outcome uncertainty and distinguishes eligible visual assessment from cleaning/repair |
| S4-06 | 4.5000 | Acknowledges the request not to be pushed and leaves further contact to the client |
| S5-06 | 4.2333 | Retains full event logistics and RSVP deadline; the resulting messages are long and less fluid |
| S6-07 | 4.1833 | Refuses discount and makes unknown pricing rationale explicit; formal wording remains a limitation |

These examples illustrate the review; the CSV includes all candidates, including lower style scores. [E — Defects and next steps](defects-and-next-steps.md) links the actual before/after outputs and separates observed repairs from remaining issues.

## 6. Authorship and validity limits

The measured system uses program-authored evidence-bound references, actual local-model editing, conditional source frames and audited client-copy correction. **98/150 raw message bodies exactly equal their supplied reference bodies**; 52 differ. **75 final candidates have recorded client-copy transformations**, primarily exact address restoration. These counts describe different stages and are not interchangeable. Product choice is the first preflight-eligible item, not an LLM ranking decision.

The result therefore evaluates the **whole controlled tool**, not unconstrained language generation by Qwen3. Changed reference logic, composition and configuration contribute to improvements; they are not evidence of a causal improvement in the unchanged model. The same assistant developed and scored the repair, and all 50 cases were available during tuning. No independent reviewer, holdout population, inter-rater agreement or generalization rate is claimed.

The brief asks for personal, on-brand language that avoids sounding scripted. Repeated cross-client phrasing remains a real concern: the rubric scores diversity within a three-candidate case, not stylistic breadth across customers. Passing this threshold does not establish that every future advisor interaction will feel personal. [B — Methodology](methodology.md) explains the deliberate control/variety tradeoff.

## 7. Screenshots and remaining evaluation work

The brief requests screenshots in the evaluation report. **No screenshots are currently attached.** Linked text/JSON/CSV evidence is inspectable but does not replace that requirement. Screenshot capture and inclusion remain user-managed; this document does not claim they exist.

Recommended evaluation work is a genuine Chinese-language reviewer assessment, followed by a new unseen-input set spanning all scenarios, with explicit attention to cross-case repetition and less common history/issue wording. These steps are not included in the 50/50 result. The empty AI below-threshold queue does not remove the need for human review if that internal gate is pursued.

## 8. Reproduction and historical evidence

The following commands read saved artifacts and do not call a model. The standard evaluator may write a new evaluation JSON; preserve existing reports when selecting output paths.

```sh
python scripts/summarize_ai_review.py --review-dir docs/verification/ai-quality-review-v0.9.7
python scripts/verify_quality_run.py --version v0.9.7
python scripts/evaluate_cases.py --batch runs/full-50-v0.9.7 --strict-all --output /tmp/chengxu-human-status.json
```

AI aggregation reproduces the recorded scores, not an independent reassessment. Human ratings may be supplied separately with `--ratings`; missing ones remain pending. [Detailed AI report](verification/ai-quality-review-v0.9.7/REPORT.md), [selected before/after sources](verification/final-before-after-v0.9.7.json) and the [historical documentation archive](history/pre-final-consolidation-v0.9.7/README.md) preserve supporting detail without mixing earlier outcomes into the current result.
