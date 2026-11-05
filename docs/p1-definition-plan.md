# P1 — Problem Definition and Acceptance Criteria

Status: all five P1 design artifacts remain complete: brand-v0.1, io-v0.1, eval-v0.1, arch-v0.2, and test-v0.1. Tool-v0.3 extends the implementation with **key-free local Ollama inference**, selected after the user declined paid API credits. Local six-scenario smoke generation is verified; design completion is not model-quality acceptance.

The user requested a visible UI preview before the remaining P1 work. An [offline Streamlit prototype](ui-preview.md) is now available; this does not complete acceptance criteria, architecture, or evaluation.

## Execution order and artifacts

| Order | Decision | Expected artifact | Completion condition |
| --- | --- | --- | --- |
| 1 | Define the fictional brand and business boundaries. | [`brand-and-rules.md`](brand-and-rules.md) — completed, brand-v0.1 | Category, audience, voice, fictional product facts, pricing/discount policies, service rules, and prohibited claims are explicit. |
| 2 | Define a common input/output contract and scenario-specific context. | [`input-output-spec.md`](input-output-spec.md) — completed design, io-v0.1 | All six scenarios have input requirements, missing-information handling, and three-candidate output expectations. |
| 3 | Define acceptance and evaluation criteria. | [`acceptance-criteria.md`](acceptance-criteria.md) — complete, eval-v0.1 | Hard failures, quality dimensions, scoring anchors, case-level aggregation, and proposed pass thresholds are specified before final evaluation. |
| 4 | Design the minimum sufficient architecture. | [`architecture.md`](architecture.md) — complete, arch-v0.2 | Components, data flow, failure handling, versioned run records, and evaluation flow are explained. Provider and stack selection may follow during P2. |
| 5 | Map requirements to tests. | [`test-design.md`](test-design.md) — complete, test-v0.1 | A 50-case coverage plan maps scenarios, normal inputs, boundary conditions, and expected behavior to criteria. Actual outputs belong to P3. |

P0 setup is established, but logging continues throughout P1–P6. An initial architecture sketch belongs in P1; the final bonus diagram must reflect the implementation.

## Proposed common contract

Inputs: scenario, fictional client profile, conversation history, relevant product/event/purchase context, and trusted brand rules. Distinguish unknown data from empty history. Avoid requiring information a scenario does not need.

Successful business output: exactly three Chinese WeChat candidate messages with consistent facts and meaningful variation. Record technical metadata separately: tool/prompt/model configuration, run identifier, validation results, and versions. Do not expose technical metadata inside client-facing message copy.

## Scenario-specific decisions to resolve

| Scenario | Additional context to define | Acceptance focus |
| --- | --- | --- |
| Birthday/festive greeting | Occasion, relevant date, relationship and contact preferences | Appropriate greeting without assuming age or unwanted sales pressure. |
| Product recommendation | Product facts, preferences, relevant purchase history | Grounded product fit; no invented inventory or benefits. |
| Post-purchase care | Purchased item, purchase timing, approved care/service guidance | Helpful follow-up grounded in known purchase and care facts. |
| Reactivation | Last known contact/purchase, relationship context, contact preferences | Respectful reconnection; no guilt or invented reasons for absence. |
| Event invitation | Event date, venue, format, eligibility and RSVP details | Accurate invitation with no invented privileges or availability. |
| Price objection | Exact objection, referenced item/price, trusted discount and service policies | Acknowledge concern; avoid unauthorized discounts or unsupported competitor claims. |

Missing facts lead to conservative wording or clarification as specified in io-v0.1. Applicable contact restrictions produce a blocked response with zero candidates. The required 50 cases remain generation-eligible cases with three outputs each; separate guardrail cases cover blocked, clarification, invalid-input, and technical-failure states.

## Proposed architecture scope

CA input → input validation → trusted brand/scenario context assembly → model generation → output validation → three candidates for CA review.

Add versioned run records and a separate batch evaluation path. Define behavior for invalid input, missing facts, malformed model output, provider failures, and any bounded retry. Treat conversation history as context rather than authority to override brand policies. Architecture choices must serve these requirements; the Web UI direction is Streamlit with a shared Python service, LLM adapter, and batch evaluation scripts (see [technical direction](technical-direction.md)). Local Ollama is selected with qwen3:4b; OpenAI remains optional; direct dependencies are pinned. Detailed component/retry/storage decisions are in [architecture.md](architecture.md). Hosting is undecided; retrieval and agent orchestration are not required for the initial fixed catalogue.

## P1 completion gate

P1 is complete when the five artifacts above agree, all six scenarios are specified, acceptance rules are testable, open product decisions are resolved or explicitly bounded, and P2 can implement without guessing the intended behavior. No pass rate, performance metric, or completed implementation is claimed at this stage.

P1 completion evidence: [acceptance criteria](acceptance-criteria.md), [architecture](architecture.md), [test design](test-design.md), and authored 50-generation/20-guardrail datasets under `data/`. See [implementation verification](verification/implementation-checks.json) and [run guide](running-and-evaluation.md).
