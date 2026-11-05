# AI-assisted quality review — v0.8.2

**Decision: current version does not meet the quality threshold. This is an AI-authored review, not completed human acceptance.**

## Scope and method

Reviewed all 50 original cases and all 150 final candidates against their saved requests, conversation context, trusted catalogue, business rules and eval-v0.1. Codex assistant directly assigned integer scores and explanatory comments; no inference API, new generation, case repair or replacement was used. This is a subjective editorial assessment of the development dataset, not an independent human study or holdout evaluation. Source hashes and run IDs bind each score to unchanged outputs. Hybrid composition provenance remains as recorded in the main evaluation report.

Each candidate has six scores: personalization 15%, brand 15%, naturalness 15%, scenario fit 15%, grounding 20%, respect 10%; case diversity adds 10%. Case scores average the three candidates per dimension. A case needs score >=4, every dimension/diversity >=3 and no hard failure. Overall target: >=45/50, mean >=4, each scenario >=75%, zero hard failures. Short responses or sparse inputs are not automatically penalized. Required repeated facts alone do not establish inadequate diversity.

## Results

- **16/50 cases (32%) meet the AI-applied case threshold**, versus target 45/50.
- **Mean raw score: 3.6767/5.** Conservative mean is 3.6137 when the one tentative hard-failure case is assigned zero. The overall conclusion fails even without that tentative finding.
- **One AI-suggested HF-02 requires human adjudication.** No verified human hard-failure count or zero-hard-failure claim is made.
- **Human acceptance: pending; release accepted: false.** Human rating records were not filled by the assistant.

| Scenario | AI threshold met | Required |
| --- | ---: | ---: |
| greeting | 7/8 | 6 |
| product_recommendation | 6/9 | 7 |
| post_purchase_care | 1/8 | 6 |
| reactivation | 0/8 | 6 |
| event_invitation | 0/8 | 6 |
| price_objection | 2/9 | 7 |

## Prioritized findings and acceptance checks

| Priority | Evidence | Finding | Check for a future revised version |
| --- | --- | --- | --- |
| P0 | S6-06 candidate 2: “这是目前我们唯一可提供的材质” | Catalogue describes one material but does not establish exclusive availability; inventory is unknown. Tentative HF-02, medium confidence. | Remove unsupported exclusivity/availability assertions; human reviewer adjudicates the original wording. |
| P1 | S3-06 candidates 1–2: “收到后/以后” | Unedited branching language and future-receipt framing do not address a bag that is wet now; impact uncertainty is not adequately answered. | Respond to the current incident with clear supported care and no outcome guarantee. |
| P1 | S2-09 | Laptop-fit question is not answered; alternatives ask about unrelated preferences. Injection is not followed, but relevance fails. | State dimensions and fit uncertainty; ask for laptop dimensions. |
| P1 | S5-05; S5-06; S5-07 | Unspecified “这个设计”; RSVP deadline unused; known interest in structure is weakly used. Correct event prefixes do not repair weak bodies. | Give one practical attendance/RSVP next step grounded in event and client context. |
| P1 | S4-03, S4-04, S4-06 | Truncated address, intimate “等你”, and shopping nudges despite a request not to be pushed. These are quality/respect findings, not automatically proven contact-policy hard failures. | Preserve address and relationship boundaries; make contact purpose specific and low pressure. |
| P1 | S6-03, S6-05, S6-09 | Budget cap, request for product information and shoulder-bag function are replaced by repeated discount policy. | Address the actual objection and function/budget constraints without inventing offers. |
| P2 | S2-05 candidate 2; recurring generic CTA wording | Technical “挂载”, vague references and shallow variation reduce naturalness/diversity. | Read each candidate independently as a sendable message; provide meaningfully different useful approaches. |

These checks are proposed next work, not implemented repairs. No model/prompt version changed during review. Ambiguous wording was not automatically treated as an established hard failure; unsupported positive availability is explicitly queued for adjudication.

## Review artifacts and next action

- [150 candidate rows with original text, scores and comments](candidate-scores.csv)
- [50 case totals and failing conditions](case-scores.csv)
- [Full source-linked ratings](ratings.json) and [machine-readable summary](summary.json)
- [Human adjudication queue](human-adjudication-queue.json): 34 cases below the AI threshold, with blank human decision fields. A genuine human must also assess the other 16 cases; they are not exempt.
- [Reproducible aggregation script](../../../scripts/summarize_ai_review.py)

Before claiming human acceptance, a real reviewer must inspect all 150 candidates, record independent scores and adjudicate hard failures in the existing human-review workflow. Any repaired runtime/prompt requires a separately versioned full measurement and review; original results and immutable draft ZIPs remain preserved. This supplement does not retroactively update their contents.
