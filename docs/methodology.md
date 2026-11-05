# B — Methodology

**Submission narrative for tool-v0.9.7 / prompt-v0.9.7.** Business baseline: brand-v0.1; contract: io-v0.1; quality rubric: eval-v0.1. This document describes the measured local implementation. [D — Evaluation](evaluation-report.md) reports results; [E — Defects](defects-and-next-steps.md) explains changes; the [architecture](architecture.md) shows the runtime and evidence flow.

## 1. Problem and assumptions

The user is a luxury Client Advisor who needs three alternative Chinese WeChat messages for one client and one situation. Each candidate must stand alone. The advisor reviews, edits and chooses a message; selecting one in the UI does not send it.

The fictional house **澄序 CHENGXU** sells six leather-goods products. A small explicit catalogue makes names, prices, colours, dimensions and carrying methods auditable. All customers, purchases, events, prices and policies are fictional assumptions. No real customer data, CRM or live inventory is used. The [brand baseline](brand-and-rules.md) defines a warm, precise and restrained voice, no negotiated discounts, and limited care advice. An eligible purchase can include one unused free in-boutique visual assessment within 12 months, by appointment; this is not free cleaning or repair.

| Required scenario | Useful response | Main boundary |
| --- | --- | --- |
| Birthday / festival | A wish tied to the supplied occasion | Do not infer age, relationship or an unsupported relative date |
| Recommendation | An eligible product plus relevant needs questions | Respect budget and hard uses; catalogue colour is not stock |
| Post-purchase care | Address the actual problem or offer concise care help | Purchase does not establish receipt; do not guarantee an outcome |
| Reactivation | Light contact with an easy option not to reply | Respect contact restrictions; no inactivity shaming |
| Event invitation | An invitation with known logistics and optional participation | Do not invent gifts, launch status, stock or confirmed attendance |
| Price objection | Address the stated budget, comparison or discount concern | No discount promise, invented pricing cause or false prior-offer attribution |

## 2. What “good” and “not acceptable” mean

A good message selects useful known context, reads naturally in Chinese, fits the current purpose, stays within brand rules and leaves the client control over whether to respond or buy. The three alternatives should differ in useful emphasis or next step while sharing consistent facts. Sparse inputs should lead to restraint or a useful question, not invented personalization. Approximately 40–100 Chinese characters is a soft target.

Unacceptable output includes fabricated facts or entitlements, unauthorized discounts or completed actions, contact-policy violations, offensive or intrusive assumptions, successful prompt injection, internal labels, exact duplicate alternatives or invalid structure. Known material alone does not establish waterproofing, wear resistance or pricing rationale. A client's report of an old discount promise is not verified advisor evidence or authorization.

These definitions come from the project [acceptance criteria](acceptance-criteria.md), not a scoring scheme supplied by Artefact. The later **50/50 target** is an internal project requirement; the brief requires 50 cases and an evaluation, without prescribing a pass rate or human signoff.

## 3. Design and division of responsibility

Streamlit and the batch CLI call one Python `GenerationService`. It reserves a request identity, validates the contract, applies business preflight, resolves eligible products, creates reference drafts, invokes the local LLM, composes approved facts, checks output, persists all attempts and returns a contract response. [Architecture](architecture.md) maps these stages to code.

The measured local path is **controlled reference editing**. The program builds three scenario-appropriate reference texts from known fields. Qwen3 edits those texts; it is not asked to invent unknown facts. References are supplied on the normal successful path, never as a replacement for a failed provider call.

| Scenario | Text sent for local model editing | Program contribution after inference |
| --- | --- | --- |
| Greeting | Three wish bodies | Known address, exact occasion, and advance framing when the supplied date is future |
| Recommendation | Three needs questions | First eligible product, known colour/price, structure, external dimensions and applicable fit/claim boundaries |
| Invitation | Three invitation bodies | Exact event title, local start date/time, venue, and supplied RSVP deadline |
| Care / reactivation / price | Three complete reference drafts | Client-copy step described below; there is no additional occasion/product/event frame |

Every successful local draft passes through `client_copy.py`: restore the known exact address; add a missing mandatory discount refusal or source-supported reported-prior-offer context where applicable; normalize singular informal pronouns and one observed repeated-character typo. Every original/final string and transformation is saved. This is a narrow deterministic correction, not a semantic verifier.

Product choice is the **first preflight-eligible product**, not LLM ranking. Composition is field-driven, with no case-ID lookup. There is no vector database, agent orchestration, live CRM, transaction flow or automatic outreach. The retained remote adapter uses a different prompt path and is not covered by the local quality result.

The authorship tradeoff is material: **98/150 raw provider message bodies exactly match their supplied reference bodies**. The other 52 differ. All 150 involve actual local inference, but they are not 150 wholly model-authored messages. The design improves control over observed errors while limiting expressive variety and evidence of open-ended generation.

## 4. Failure handling and evidence

The service returns `generated` with three candidates, or `needs_clarification`, `blocked`, `invalid_input` or `generation_failed` with no sendable candidates. Known permission, fact or product mismatches can stop execution before inference. Parsing, body-scope and grounding failures have a bounded repair budget; terminal or exhausted failures remain explicit. Neither provider nor failed output is silently replaced with preview/reference text.

SQLite reserves request identities and keeps artifacts. A completed identical request can be replayed without another call; a conflicting or pending identity does not launch duplicate work. This does not guarantee provider-side exactly-once execution after a timeout. Raw model responses, prompts, references, public configuration, source hashes, timings, validation errors, composition and final outputs remain traceable. Preview and fake-backed tests are labelled separately from actual inference.

## 5. Test-set design

The fixed generation set has 50 fictional inputs: **8 greetings, 9 recommendations, 8 care, 8 reactivations, 8 invitations and 9 price objections**. Variation covers unknown addresses/dates, sparse context, budgets and carrying constraints, laptop-fit uncertainty, care eligibility and a water incident, event details/deadlines, prior contact preferences, comparison quotes and discount requests. Twenty additional guardrails cover non-success behavior, including invalid inputs, unclear permissions and missing essential facts.

The generation cases were repeatedly used for tuning. This is a development set, **not an untouched holdout**. The [test design](test-design.md) supplies coverage detail; [E](defects-and-next-steps.md) links intermediate failures. Code tests use labelled fake adapters; they test engineering behavior, not language quality. UI tests likewise do not enlarge the 50-case quality population.

## 6. Evaluation procedure

The evaluation keeps engineering checks, source integrity and language review separate:

1. Freeze runtime/prompt versions, actual provider configuration, model digest, business baseline and original inputs.
2. Run the complete 50-case set and preserve successful and failed attempts. Additional requests must remain separately identified.
3. Check structure and selected source/policy constraints; reconstruct raw output through composition and exact CSV export.
4. Read all 150 final candidates against their inputs and source facts. Assign six candidate dimension scores and one case diversity score, with comments and run/hash linkage.
5. Aggregate using unchanged weights; report quality results separately from test/guardrail counts and actual human-review status.

Weights are personalization 15%, brand 15%, naturalness 15%, scenario fit 15%, grounding 20%, respect 10%, and case diversity 10%. For each candidate dimension, average its three ratings before weighting. A case requires every dimension/diversity >=3, weighted score >=4, and no hard failure; a verified hard failure makes its effective score zero. The current project target requires all 50 cases to meet those conditions.

**The recorded quality scores are AI-authored self-review.** The same assistant implemented the repair and assessed the outputs. No independent human assessor, calibrated judge or inter-rater result is claimed. Actual human-rating records remain pending and do not become passes through AI aggregation. [D](evaluation-report.md) reports both statuses explicitly.

## 7. Reproducibility and limits

Use the [freeze](verification/evaluation-freeze-v0.9.7.json), [integrity audit](verification/full-50-integrity-v0.9.7.json), [scores](verification/ai-quality-review-v0.9.7/ratings.json) and exact [case table](verification/ai-quality-review-v0.9.7/full-50-cases.csv). The [runbook](running-and-evaluation.md) explains local setup; the [review report](verification/ai-quality-review-v0.9.7/REPORT.md) gives commands for saved-output aggregation and verification without inference. Keep new generations in new directories rather than overwriting evidence.

The method does not prove semantic correctness on arbitrary future inputs. Contact-language and claim checks are incomplete; reference-driven phrases repeat across clients, and several messages remain formal or dense. Human review and an unseen-input exercise would strengthen confidence. Authentication, CRM authorization, retention policy, production monitoring and hosted multi-user use are outside the local demonstration. Screenshots required by the brief are not present in the current materials; no screenshot evidence is claimed here.
