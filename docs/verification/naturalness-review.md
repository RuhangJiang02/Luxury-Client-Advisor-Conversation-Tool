# Naturalness and diversity editorial review

Scope: all 33 saved candidates, tool/prompt-v0.4.6, 11 iteration cases. Reviewer: Codex assistant. This is qualitative editorial evidence, not completed human eval-v0.1 scoring. Proposed alternatives are **assistant-authored examples**, never exported as local-model results. Original artifacts remain unchanged. Chinese source text and suggested copy are preserved verbatim in the linked CSV/JSON.

[All 33 original texts, observations and edited examples](naturalness-review-v0.4.6.csv) · [Structured review](naturalness-review-v0.4.6.json)

## Set-level findings

| Case | Primary distinct angles for improvement | Main defect |
| --- | --- | --- |
| S1-01 | Simple blessing / personal time / light everyday wish | Unsupported personality and brand accompaniment; no explicit birthday greeting in candidates 2/3 |
| S2-01 | Known use and budget / one design fact / unanswered carrying preference | Superlatives, invented intent, and redundant known preference |
| S3-01 | Support question / cleaning / storage | Unsupplied restrictions, lifespan benefit and unnecessary assessment |
| S4-01 | Greeting / changed preference / space to reconnect | First two are similar questions; third is generic service copy |
| S5-01 | Direct invitation / one supplied design detail / optional attendance | First and third have the same purpose; formal openings and endings |
| S6-01 | Price/policy / one material fact / time to consider | Rigid tone and unsupported unique craftsmanship |
| QF-C01 | Use question / cleaning / storage | Soften bureaucracy and remove unsolicited assessment |
| QF-C02 | Acknowledge non-receipt / future cleaning / future storage | Present-tense care advice ignores non-receipt |
| QF-P01 | Price boundary / explain lack of verified comparison / comparison autonomy | All three largely evade the actual why-price-differs question |
| QF-P02 | Acknowledge / stop pushing / client-initiated later contact | Forced material and policy are inappropriate after request for space |
| QF-E01 | Direct invitation / design detail / optional attendance | Near-equivalent opening and confirmation, vague display description |

All 33 receive an editorial suggestion (26 substantive revisions, 7 light edits). This is not a measured quality pass/fail rate. Low-pressure responses can be short; adding sales facts merely to meet 40 characters damages fit. Shared logistics/policy are necessary repetition, while meaningful diversity concerns the client's choice of conversational purpose.

## Implementation response

Tool/prompt-v0.5.0 adds conversational style rules, focused recommendation/reconnection context, comparison-specific responses and consideration-space routing. It removes the blanket requirement to sell a material fact in every price scenario, retaining the existing fact/policy/space approach for discount requests. Formal-copy indicators are soft review flags. No subjective word blacklist becomes an automatic rejection. The fixed 50-case dataset, 11-case inputs, model weights, catalogue and acceptance rubric are unchanged.

## Preserved rerun observations

- v0.5.0: 7 generated / 4 generation_failed. Saved-run evaluation under the corrected v0.5.1 checks also flags two generated care cases for unsupported non-receipt, leaving 5 pending / 6 fail. Generation status and retrospective validation are different measurements. Original outputs remain unchanged.
- v0.5.1: 9 generated / 2 generation_failed, both invitations. Sentence-level style examples improved brevity but were copied verbatim in several cases and omitted personalization/logistics. They were removed in v0.5.2 in favour of a phrase-level hint and explicit per-message facts. This is an observed prompt-example copying limitation, not evidence that a reusable template meets quality acceptance.
- v0.5.1 also corrected a pricing-check false positive: client consideration of the price is not a factual explanation of price-setting. Non-receipt checking now prevents inventing a negative receipt state where receipt is unknown or positive. Conditional examples remain allowed.

The latest deterministic record contains 53 passing implementation tests. No human scores were filled. Human review must cover relevance, grounded details, brand voice, naturalness and semantic diversity, even when an output is generated and short.

## Latest result — tool/prompt-v0.5.2

**Editorial review completed for all 33 original candidates. Automatic generation quality remains unresolved.** Latest unchanged-input rerun: **9 generated cases / 27 messages, 2 generation_failed** (both invitations). Evaluator: **9 pending human ratings / 2 fail**. This regresses from v0.4.6's 11 generated cases. No failed invitation was replaced with an editorial example or a prior version. Do not freeze this version for the final 50-case execution.

[Latest actual-output CSV, with failed rows empty](naturalness-latest.csv) · [Saved evaluation](naturalness-evaluation.json) · [Exact versioned comparison](naturalness-rerun-comparison.json)

| Case | Assistant observation | Remaining action |
| --- | --- | --- |
| S1-01 | Mixed: Removed brand accompaniment and personality claims. Still poetic; switches 您/你, and candidate 2 does not explicitly say happy birthday. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| S2-01 | Mixed: More use-oriented recommendation and one concrete question. Still subjective quality adjectives and a redundant broad use-case question. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| S3-01 | Mixed: No unsupported receipt statement or unsolicited assessment. Storage wording is stiff and the offered further detail is vague. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| S4-01 | Mixed: Different greeting/preference/space purposes, but overly abrupt and the copied interest closing lacks a clear subject. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| S5-01 | Regression: Rejected after two attempts: candidate 2 lacks independent event identity/logistics. No final messages exported. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| S6-01 | Mixed: Policy/material/time angles are distinct. Internal phrases about discount requests and giving choice-space remain in customer copy. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| QF-C01 | Mixed: No explicit invented non-receipt assertion, but future receipt phrasing ignores confirmed receipt; unsupported maintaining softness claim and interest closing remain. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| QF-C02 | Mixed: Acknowledges non-receipt and gives future cleaning advice. Third candidate still gives present storage advice; uneven address and generic help. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| QF-P01 | Improved with residual issues: Directly acknowledges reported price and inability to verify terms. Repeats list price in all three and unnecessarily mentions authenticity. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| QF-P02 | Improved with residual issues: No material pitch or forced discount policy; acknowledges time request. Candidate 2 may imply advisor-initiated contact; use client-initiated closing instead. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |
| QF-E01 | Regression: Rejected after two attempts: candidate 3 omits event name/logistics. No final messages exported. | Use original candidate-level editorial notes for revision; do not claim human acceptance. |

The strongest sampled improvement is content selection for comparisons and requests for time. No global naturalness/diversity improvement rate is claimed. Shared factual content is expected; semantics, response fit, and consistency must still be assessed. The 33 assistant-authored alternatives are the concrete editorial deliverable for this review, not a substitute for actual provider output evidence.

## Next implementation decision

Resolve independent invitation completeness without weakening factual checks; investigate smaller per-candidate generation requests if joint three-message prompting keeps dropping context. Recheck every revised sentence against the exact request, especially confirmed/non-received care and no-pressure follow-up. Test on untouched inputs before freezing. Sentence-level style examples are not retained in v0.5.2 because they induced copying. Screenshots remain outside assistant scope.
