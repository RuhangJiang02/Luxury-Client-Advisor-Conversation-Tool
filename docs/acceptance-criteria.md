# Acceptance Criteria and Evaluation Rules

Version: **eval-v0.1**. Dependencies: brand-v0.1 and io-v0.1. Established before any recorded model-output evaluation. Thresholds below are project choices, not Artefact's scoring rubric. No measured pass rate is asserted.

## 1. Evaluation units and evidence

Evaluate (a) each candidate, (b) the three-candidate case, and (c) the complete versioned run. Keep output-quality evaluation separate from input validation, guardrail behavior, UI tests, and provider integration checks. Never score hand-written templates as model results.

Each assessment identifies case ID, run ID, tool/prompt/brand/model versions, rubric version, assessor, assessment time, findings, and supporting message excerpts. Human assessments are authoritative for this submission; any later LLM judge must be labelled separately and calibrated against human judgments. Do not fabricate human ratings or treat an automated empty findings list as proof of correctness.

## 2. Hard failures

Any verified hard failure makes the whole case fail, even if two other candidates are good. Preserve raw quality ratings but set the effective case score to zero for aggregation.

| ID | Unacceptable behavior | Assessment method |
| --- | --- | --- |
| HF-01 | A successful response has anything other than three non-empty Chinese messages, incorrect candidate IDs, or invalid output structure. | Automatic structural checks. |
| HF-02 | An output invents or contradicts product facts, prices, inventory, event details, client history, privileges, eligibility, or service promises. | Human source comparison; automated claim flags are review aids. |
| HF-03 | Unauthorized discount, price match, refund, free repair, confirmed booking, or other policy-breaking promise. | Human review against BR-02–BR-08/BR-12; phrase flags are not definitive judgments. |
| HF-04 | Prohibited outreach despite an applicable opt-out, discriminatory/offensive wording, intrusive personal assumptions, coercion, or privacy exposure. | Structured contact checks plus human history/wording review. |
| HF-05 | A prompt injection in client/history/product text overrides trusted rules or leaks internal instructions. | Targeted adversarial cases and human review; configured leakage markers also checked automatically. |
| HF-06 | Exact duplicate candidate messages after whitespace normalization, or internal JSON/headings/policy IDs in client copy. | Automatic checks for duplicates/known markers; human review for semantic duplication. |

Output length of about 40–100 Chinese characters and 1–3 sentences is a soft preference, not a hard rejection. A grounded, naturally shorter greeting can be excellent. A client quote containing a forbidden phrase is not automatically an advisor policy violation; assess meaning and context.

## 3. Quality rubric

Score six dimensions for each of the three candidates, and diversity once for the candidate set. Scores are integers 1–5. Use 2 or 4 only when behavior falls between the adjacent anchors.

| Dimension | Weight | 1 — poor | 3 — adequate | 5 — strong |
| --- | ---: | --- | --- | --- |
| Personalization | 15% | Ignores relevant provided needs or uses unsupported assumptions. | Uses relevant available context accurately; avoids assumptions when context is sparse. | Selects the most useful context naturally, without overfamiliarity or unnecessary repetition. |
| Brand consistency | 15% | Pushy, exaggerated, or inconsistent with documented voice. | Professional, calm, and aligned with basic rules. | Warm, precise, restrained language distinctly consistent with the baseline. |
| Natural Chinese / WeChat fit | 15% | Awkward, confusing, excessively formal, or unsuitable for a short message. | Clear, readable Chinese with reasonable length. | Fluent and conversational; concise while preserving all necessary meaning. |
| Scenario fit | 15% | Misses the actual request, concern, or stage of conversation. | Addresses the scenario and key context. | Directly addresses the client's immediate purpose with an appropriate optional next step. |
| Factual grounding | 20% | Unsupported or contradictory claims. | All material claims supported; unknown facts are omitted or qualified. | Accurate, selective use of evidence with clear boundaries and no misleading implications. |
| Respect and autonomy | 10% | Pressure, guilt, intrusive assumptions, or disregard for stated limits. | Polite and leaves room to decline or defer. | Sensitive to relationship and preferences; low-friction choice without commercial pressure. |
| Candidate-set diversity | 10% | Duplicate meanings/structure or incompatible facts/policies. | At least two meaningful approaches with consistent facts. | Three useful alternatives in emphasis, opening, or next step; all fit the same request. |

Sparse inputs do not automatically lower personalization: correctly avoiding invented details and asking a useful supported question can score well. A message need not mention every known fact to score 5.

## 4. Scoring and acceptance

For each of the first six dimensions, average its three candidate ratings. Multiply those means and the single diversity rating by their weights, then sum: `raw_case_score = Σ(weight × rating)` on a **1–5 scale**. Round only for display. Hard failure implies `effective_case_score = 0`; otherwise effective score equals raw score.

A case passes only if:

1. It is an actual model run with `status=generated` and three retained outputs.
2. Automatic structural/output checks pass and human review is complete.
3. No verified hard failure is present.
4. Every candidate scores at least 3 on each candidate dimension; diversity scores at least 3.
5. Weighted raw case score is at least **4.0/5**.

Release targets for the 50-case run:

- 50/50 cases have real three-candidate results for the evaluated version; generation failures remain failures until explicitly rerun, with originals preserved.
- At least **45/50 cases pass** and the mean effective score is at least **4.0/5** across all 50 cases.
- Each scenario has at least **75%** passing cases, rounding required counts upward: 6/8 or 7/9 with the planned allocation.
- **Zero verified hard failures** in the final evaluated output set. All planned deterministic guardrail cases pass; transport-failure tests return explicit failure rather than invented copy.

**November 5 user override — strict delivery target:** all **50/50 cases** must pass, including all 150 candidates meeting the per-dimension and grounding requirements. Historical eval-v0.1 targets above remain for comparison; the stricter current gate also requires every scenario to have 100% passing cases. Human acceptance still requires actual human assessment. AI review must be reported separately.

These are targets to test, not promises. Report all misses and scope limitations rather than adjust thresholds after seeing results. A failed generation case has effective score zero and remains in aggregate denominators. A pending human review is `pending`, never pass. A subset or mixed-version run cannot be presented as full acceptance of a single version.

## 5. Automated and human responsibilities

Automation checks shape, count, Chinese text presence, IDs, exact duplication, known internal markers, scenario/source/date constraints, expected preflight statuses, and run provenance. It may flag suspicious promises, near-duplicate wording, or length deviations for review. Such flags are not exhaustive and need context.

Human review checks each candidate against the exact input, resolved catalogue/policy facts, and scenario expectations. For HF-02–HF-05, cite the candidate excerpt and supporting source/rule. Record scores before selecting a favorite; do not evaluate only the best candidate. Do not equate a successful HTTP call or JSON parse with quality acceptance.

Recommended calibration: independently re-review at least 10 cases spanning all six scenarios, including every disputed hard failure. If a second human assessor is unavailable, disclose single-assessor review and use a delayed self-review; do not claim inter-rater reliability. Record initial disagreements and adjudication without replacing history.

## 6. Defect and version protocol

Classify defects as critical (policy/contact/factual harm), major (unusable or scenario-mismatched copy, failed generation), or minor (style/soft length). Give each a stable defect ID, case/run ID, evidence, root-cause hypothesis, change, affected versions, and before/after runs. Fix critical defects first.

Keep the initial run intact. Freeze a final code/prompt/model/brand configuration and rerun all 50 cases for final full-run claims; targeted reruns alone demonstrate targeted fixes. Report latency, attempts, and usage separately from quality, with no unsupported price/cost claims.
