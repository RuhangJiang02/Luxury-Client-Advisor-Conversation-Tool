> Historical working draft. Superseded by the current documents under `docs/`. Relative evidence links have been adjusted for this archive location; recorded versions and outcomes have not been rewritten.

# Methodology — CHENGXU Client Advisor Conversation Tool

## Current local reference-editing revision

Tool/prompt-v0.9.7: 50/50 cases meet the stricter **AI-applied** case threshold, mean 4.31/5; genuine human review and release acceptance remain pending. [Detailed evidence and limitations](../../verification/ai-quality-review-v0.9.7/REPORT.md). The fixed 50-case dataset was actively used for tuning, so this is not holdout evidence.

All local requests now use program-authored evidence-bound reference copy edited by a real local LLM (98/150 raw bodies unchanged from reference). Greetings/products/events receive source frames; all local successes receive audited exact-address restoration, necessary policy/prior-offer context and narrow pronoun/typo normalization before grounding checks. Failed inference has no reference fallback. Every reference, raw provider output and transformation is retained. Source framing derives from fields, not case IDs. The same shared service powers UI and batch. Current freeze, full review and strict CLI replace the old deferred-work status.

Earlier sections below describe historical implementation/results and retain their recorded versions. Their thresholds and outcomes are not retroactively rewritten.


Deliverable **B — Methodology**. Documentation revision: **November 5, 2026, Asia/Shanghai**. Implementation reference: **tool-v0.8.2 / prompt-v0.8.2**; brand-v0.1, io-v0.1 and eval-v0.1.

This document explains the final implemented design and its tradeoffs for a reviewer who has not followed the project conversations. Detailed results belong in the [evaluation report](../../evaluation-report.md), implementation boundaries in the [architecture](../../architecture.md), and historical changes in the [Work Log](../../../WORK_LOG.md). The original challenge brief is private and is not reproduced.

**Review status:** the implementation and saved measurement evidence exist, but human quality acceptance is incomplete. At the user's direction, further work on the existing 50 cases is deferred while documentation, demonstration and packaging are completed. This documentation revision neither changes the runtime nor certifies its outputs.

## 1. Problem, users and scope

A client advisor needs suitable Chinese WeChat drafts for an individual client. The tool accepts a client profile, one scenario, relevant conversation history and any applicable product/purchase/event facts. A successful request returns exactly three independently usable alternatives for the advisor to review, edit and select. Selection does not send a message.

The fictional brand, **澄序 CHENGXU**, is a contemporary luxury leather-goods house with a six-item catalogue. This small, explicit product domain makes price, colour, dimensions and carrying-method claims auditable. All clients, products, prices, events and policies are fictional project assumptions, not facts provided by Artefact or records about real customers. See the [brand and rules](../../brand-and-rules.md).

| Scenario | Intended communication | Important boundary |
| --- | --- | --- |
| Birthday or festive greeting | A warm wish tied to the supplied occasion | No invented age, benefits or automatic sales pitch |
| Product recommendation | A supported eligible item and useful questions about needs | No assumed stock, unsupported properties or budget/use mismatch |
| Post-purchase care | Respond to the actual concern using approved care guidance | Purchase is not proof of receipt; assessment is not free repair |
| Reactivation | Reconnect lightly and leave room to respond | No shaming inactivity or overriding contact restrictions |
| Event invitation | Invite to a confirmed event with optional attendance | Exact logistics; no invented gifts, exclusivity or reservations |
| Price objection | Address the particular concern without pressure | No negotiated discount, invented price rationale or assumed past promise |

The implemented application drafts text only. CRM integration, live stock, transactions, automated outreach and hosted multi-user operation are outside the current implementation.

## 2. What good and unacceptable mean

A good set contains relevant, readable, restrained Chinese messages grounded in the supplied facts. Alternatives should offer useful differences in emphasis or next step while keeping policies and facts consistent. Sparse input is a reason to avoid assumptions, not to invent personalization.

Unacceptable behavior includes fabricated facts or entitlements, unauthorized discounts or completed actions, prohibited contact, instruction leakage and duplicate or structurally invalid output. For example, a known leather material does not establish wear resistance; a customer's statement that an advisor promised a discount does not establish an advisor record or authorize that discount.

The target length of approximately 40–100 Chinese characters is a soft preference. A concise, appropriate wish may be shorter. Quality thresholds are project-authored and were defined before recorded model-output evaluation; they are not Artefact's scoring scheme. The full definitions and exceptions are in [acceptance criteria](../../acceptance-criteria.md).

## 3. End-to-end approach

1. **Capture a structured request.** Streamlit provides six scenario forms and an advanced JSON path. The batch runner uses the same contract and generation service.
2. **Validate before inference.** JSON Schema and reference/date checks reject malformed requests. Business preflight screens contact restrictions, missing essential information, product eligibility and applicable service conditions.
3. **Assemble relevant context.** The service resolves the versioned catalogue and rules, derives facts such as eligibility, and chooses a scenario-specific model task. Client text remains quoted data rather than authority to change policy.
4. **Invoke the selected provider explicitly.** The active route is local Ollama/Qwen3 4B. Provider calls occur on submitted requests or explicit batch execution, not each input edit.
5. **Compose and check drafts.** Three local scenarios use source-bound composition; the others retain full model-authored messages. Parsed/composed text passes count, source, leakage and diversity checks.
6. **Persist and return the result.** The service keeps the request, raw attempts, versions, source snapshots, diagnostic codes and final response. The UI displays successful candidates or an actionable non-success state.
7. **Evaluate saved outputs separately.** Evaluation and export consume preserved artifacts; they do not silently generate replacement text or rewrite poor candidates.

There are five contract outcomes: `generated`, `needs_clarification`, `blocked`, `invalid_input` and `generation_failed`. Only `generated` contains three candidate messages; the other states contain zero sendable candidates and an explanation or clarification. See the [I/O specification](../../input-output-spec.md).

## 4. Division of responsibility: facts and language

Repeated experiments showed that prompt instructions alone did not reliably keep a small model from mixing occasions, omitting event logistics or embellishing product properties. The implemented local route therefore constrains the model's job where verified facts can be stated directly.

| Local scenario | Model-authored content | Program-supplied content |
| --- | --- | --- |
| Greeting | Three wish bodies | Known address and the exact birthday/festival opening |
| Recommendation | Three short preference questions | Eligible product facts: colour/price, one structure detail and dimensions |
| Invitation | Three invitation bodies | Known address, confirmed event title, start date/time and venue |
| Care, reactivation, price objection | Three full draft messages | No text frame; the service supplies context and validates the output |

Recommendation selection is deterministic: **the first preflight-eligible product**, not LLM ranking. The model asks about unknown needs rather than inventing a product's performance. This is useful for factual control, but does not claim sophisticated product optimization.

The hybrid messages are not described as entirely model-authored prose. Each attempt records raw provider content and, when applicable, `structured_composition`: model bodies, verified frame(s), source fields, the selection rule and final messages. Failed inference or invalid bodies do not trigger a fabricated template replacement. The separate preview mode remains explicitly labelled and does not count as real generation evidence.

The tradeoff is less free-form language and more predictable, question-heavy recommendations. Supplied question examples can also lead to repeated phrasing. Source-bound facts do not establish that a message is natural, relevant or meaningfully different; those judgments remain part of quality review.

## 5. Engineering choices and alternatives

| Choice | Reason in this challenge | Cost or limit |
| --- | --- | --- |
| Streamlit with a shared Python service | A working advisor interface and scriptable backend without separate frontend/server stacks | Current scope is a local demonstration, not a multi-user production service |
| Local Ollama / Qwen3 4B | Reproducible inference on installed weights without paid API credits | Quantization and small model capacity have shown semantic/style weaknesses; local compute still has a cost |
| Explicit JSON catalogue and rules | Six products fit in inspectable structured data and direct context | Updates are manual/versioned; no live CRM or inventory connection |
| Deterministic preflight plus generation | Enforce known eligibility/contact boundaries before asking the model to write | Pattern-based language interpretation is incomplete |
| Source-bound composition | Preserve known facts while asking the model for language | Less expressive structure; requires explicit authorship/provenance disclosure |
| SQLite plus JSON artifacts | Request reservations, replay protection and traceable evaluation inputs | Local durability only; no provider-side exactly-once execution guarantee |
| Bounded retries and explicit failure | Keep failed attempts visible and prevent unbounded repair loops | Some requests can legitimately exhaust the budget |
| Saved-run evaluation | Separate generation, review and export; avoid changing evidence during scoring | Human semantic assessment remains necessary |

A vector database, retrieval framework and autonomous agent orchestration were not implemented: the small fixed catalogue can be resolved directly. A retained optional remote adapter is an extension point, not evidence that the local route and every remote model have equivalent behavior or quality.

## 6. Test-set design and measurement discipline

The required generation population has 50 fictional, preflight-eligible inputs: **8 greetings, 9 recommendations, 8 care cases, 8 reactivations, 8 invitations and 9 price objections**. Case variation includes sparse context, address/occasion differences, budget and carrying constraints, care eligibility and reported issues, event logistics, contact context and different price concerns. The [test design](../../test-design.md) describes the coverage and execution procedure.

Twenty additional guardrails exercise non-success behavior such as contact blocks, missing facts and invalid input. Their denominator remains separate from generation quality. Deterministic tests use labelled fake adapters to verify service boundaries, persistence, provider handling, composition and export behavior; they are not real language-quality results.

Smoke inputs and the later 17-/23-case repair populations were reused during tuning. Earlier first-time live checks on selected fixed cases overlap the required set and are not an independent external benchmark. Repeatedly observed cases are not presented as untouched holdout data.

A measurement freeze identifies tool/prompt versions, provider configuration, installed model digest, source/input hashes and the brand/catalogue/rubric baseline. Failed runs remain intact. Where a bounded recovery view is assembled, it identifies every source run and cannot replace already-generated cases based on stylistic preference. The current full measurement and historical results are reported separately.

## 7. Evaluation method

Review has four distinct layers:

| Layer | What it establishes | What it does not establish |
| --- | --- | --- |
| Request/preflight checks | Defined inputs and supported business decisions | Quality of generated text |
| Deterministic implementation tests | Tested code/error/provenance behavior | Human-level language or factual understanding |
| Saved-output automatic checks | Structure, selected source/date constraints, leakage and lexical warnings | Complete semantic grounding or true diversity |
| Source-based human review | Candidate quality, contextual hard failures and set-level usefulness | Robustness beyond the measured population |

Human scoring uses six dimensions per candidate: personalization **15%**, brand **15%**, naturalness **15%**, scenario fit **15%**, grounding **20%** and respect **10%**. Candidate-set diversity contributes **10%**. Candidate dimensions are averaged over the three outputs before weighting. A verified hard failure sets the effective case score to zero.

A case requires every candidate dimension and diversity at least 3/5, weighted score at least 4/5, no verified hard failure and completed human review. The full targets remain at least 45/50 accepted, mean effective score at least 4/5, at least 75% in every scenario, zero verified hard failures and passing guardrails. These are targets, not measured claims.

Assessors must consider all three messages, cite the exact source/excerpt for hard failures and identify assessor/time. Assistant editorial notes, suggested rewrites, model outputs and human scores remain distinct. Missing human ratings stay `pending`; a successful JSON response does not imply quality acceptance.

## 8. Evidence and reproducibility

| Evidence | Location / purpose |
| --- | --- |
| Runtime and source identity | [Current freeze](../../verification/evaluation-freeze-v0.8.2.json) |
| Full measured outputs and evaluation status | [Evaluation report](../../evaluation-report.md) |
| Model/source authorship and text integrity | [Integrity record](../../verification/full-50-integrity-v0.8.2.json) and per-attempt composition records |
| Failures, changes and unresolved defects | [Defect report](../../defects-and-next-steps.md), with versioned comparisons |
| Actions, inputs, outputs and tools | [Work Log](../../../WORK_LOG.md) and linked conversation records |
| Setup, explicit execution and saved-run evaluation | [Running guide](../../running-and-evaluation.md) |

The export uses the brief's exact eight columns and separate provenance. Neither a manual edit nor a nicer previous-version candidate is silently substituted into the current output cells. Credentials, the private brief, weights, database and server logs are excluded from the review archive. Source text and raw model responses may contain fictional client history and are kept in the private local project.

## 9. Limitations and priorities

The method controls known source fields but does not prove every implication in model bodies. Small-model replies still show generic phrasing, weak semantic diversity and context errors. Current open examples include a care response that misfits a reported issue and an unsupported absolute availability statement in a price reply. Exact source-bound frames, regex checks and lexical similarity cannot replace semantic review.

Human scoring has not been completed; it is deferred, not waived. Final quality acceptance therefore remains open. The local UI is not externally hosted, and production features such as authenticated multi-user access, CRM integration, retention management and operational monitoring have not been implemented.

The [six-scenario UI demonstration](../../ui-demo-walkthrough.md), [runbook](../../running-and-evaluation.md) and separate documentation/UI review package are now completed. The 44 isolated UI checks use test doubles and do not add model-quality evidence. If later implementation changes address the deferred findings, they require a separately versioned measurement. Existing outputs and the current runtime baseline remain preserved during this documentation step.
