# Test Design and Requirement Coverage

Version: **test-v0.1**. Dependencies: brand-v0.1, io-v0.1, eval-v0.1. This plan is fixed before model-output evaluation. Inputs and outcomes must remain distinguishable: authoring requests does not complete the 50-case submission.

## 1. Test populations

| Population | Count | Purpose | Expected result |
| --- | ---: | --- | --- |
| Required generation cases | 50 | Cover all six scenarios with normal and answerable difficult inputs. | Three actual Chinese model outputs per case; quality assessed by eval-v0.1. |
| Additional guardrail cases | At least 18 | Invalid structures, missing essentials, contact restrictions, source/date conflicts. | Documented non-success state and zero candidates, usually no model call. |
| Implementation regression tests | As needed | Provider errors, retries, persistence, idempotency, UI behavior. | Deterministic assertions using labelled fakes; not counted as model-quality cases. |
| Live smoke run | Initially 1–6 | Verify credentials, endpoint, model, JSON parsing, storage, and UI/backend integration. | Real preserved run evidence; not a full quality acceptance claim. |

## 2. Fifty-case allocation

Each scenario uses six base themes below, with variants to reach the stated count. Each manifest row records case ID, request, expected status, focus, applicable rule IDs, and expected/forbidden behaviors. Exact example output text is not prescribed, to avoid optimizing for one answer.

| Scenario | Count | Planned themes and variants | Key rules / rubric |
| --- | ---: | --- | --- |
| Greeting | 8 | Birthday with known/unknown date; festival; no preferred address; new/existing relationship; sparse profile; no-sales preference. | BR-09–BR-11; grounded date, naturalness, respectful greetings. |
| Product recommendation | 9 | Known use/color; budget boundary; crossbody need; tote need; multiple candidates with one mismatch; sparse preference; owned item avoidance; unsupported fit question handled cautiously. | BR-01–BR-03/BR-10; factual grounding, fit, personalization. |
| Post-purchase care | 8 | General care; usage check; reported concern; unknown purchase date; assessment used/unused; expired/anniversary boundary. | BR-05–BR-07; no diagnosis or unauthorized service entitlement. |
| Reactivation | 8 | Known/unknown last contact; sparse history; preference update; neutral check-in; product rejection without global opt-out; explicit no-pressure preference. | BR-10–BR-11; no guilt, invented absence reason, or intrusive metrics. |
| Event invitation | 8 | Boutique event/private preview; product preview; known interests; new/existing relationship; optional RSVP deadline; understated invitation; no invented gifts/exclusivity. | BR-03/BR-08/BR-10; correct logistics and choice. |
| Price objection | 9 | Too expensive; budget concern; discount request; comparison with/without quoted price; alleged prior discount; aggressive tone; time to decide; cheaper but unsuitable alternative avoided. | BR-01–BR-04; acknowledge concern without policy exceptions or competitor accusations. |

At least 18 of the 50 should be answerable boundary/difficult cases, identified in the manifest, rather than merely renamed happy paths. All client names/IDs/histories, products, events, and transactions are fictional. Use fixed reference timestamps for reproducible date logic. Birthday/festival dates are supplied fixtures rather than assumed calendar facts.

## 3. Additional guardrail matrix

| Guardrail | Expected state | Requirement |
| --- | --- | --- |
| Structured proactive opt-out / restricted topic / explicit history opt-out | `blocked` | No outbound candidates or provider call. |
| Unknown proactive permission / ambiguous contact scope | `needs_clarification` | Ask CA to establish permitted scope. |
| Missing event venue / unknown eligibility / past event / closed RSVP | `needs_clarification` | No invented invitation details. |
| Ineligible event client | `blocked` | No invitation drafts. |
| Unknown product / no supplied products / no fitting product | `needs_clarification` | Do not invent a catalogue item or force a mismatch. |
| Missing price-objection content / client-role reference unavailable | Clarification for empty history; invalid for dangling/wrong-role reference | Respect contract distinction between missing essential content and bad references. |
| Future purchase / inverted event interval / future history | `invalid_input` | Correct chronology before generation. |
| Unknown field / wrong type / duplicate ID / wrong source kind / unsupported version | `invalid_input` | Strict structural/reference validation. |
| Conflicting client preference or trusted facts | `needs_clarification` | Do not silently pick one. |
| Unknown inventory / stale inventory / unknown care eligibility | Successful generation may omit claims | Include answerable variants among the 50; do not classify all missing optional facts as failures. |

Provider timeout, authentication failure, rejected JSON, truncated output, exact duplication, and exhausted retry budget are tested separately with a fake HTTP response or adapter. Injection attempts must appear in dedicated adversarial regression cases and answerable generation cases where appropriate. Semantic protection is assessed by actual outputs, not inferred from a prompt instruction.

## 4. Execution and evidence procedure

1. Freeze datasets and record hashes; keep six original contract examples as design fixtures.
2. Run deterministic tests before paid generation. Fix implementation errors before measuring message quality.
3. Run a small real smoke batch; record provider/model/configuration and any errors.
4. Run all 50 required cases under a fixed version/configuration. Preserve failures, attempts, and original outputs.
5. Run additional guardrail cases separately. Record expected/actual state and provider attempt count.
6. Export exact-column case CSV plus provenance. Collect human ratings and evidence using eval-v0.1.
7. Evaluate all three candidates, record defects, prioritize fixes, and preserve before/after run IDs. A full final acceptance claim requires a frozen full 50-case run and complete ratings.

Do not replace a failed case with an easier case after observing output. Clarify a defective input as a documented dataset revision with a new request ID. Keep initial and final results separate; report scenario-level denominators, overall score, quality pass rate, hard failures, incomplete reviews, latency, and token usage.

## Targeted quality regression — November 4

The 47-test suite includes positive/negative/conditional receipt claims, message-versus-product receipt, price causality, unsupported alternative offers, event title aliases and wrong minutes, candidate repetition, internal labels, and preservation of rejected output during repair. See `docs/verification/quality-fix-regression-results.txt`. Five additional authored inputs cover confirmed receipt, explicit non-receipt, competitor-price comparison, time to consider, and different event logistics. They were new at the start of this repair cycle and subsequently used for iteration; they are no longer an untouched holdout. The 11-case validation set combines these with six unchanged smoke inputs. It does not replace the fixed 50-case dataset.

## Editorial routing regressions — tool-v0.5.1

53 tests pass (docs/verification/naturalness-regression-results.txt). New cases verify that comparison and requests for time do not force a material pitch, explicit discount requests still receive the policy, formal language remains a soft review flag, unknown/confirmed receipt cannot become non-receipt, and client consideration of price is not misclassified as a price-setting explanation. Actual generation quality is separately reviewed at candidate and set level.

## Full measurement execution — v0.6.1

58 deterministic tests passed. Known 11-case regression and six previously untuned fixed -02 cases generated; current 20 guardrails matched with zero calls. The full baseline produced 48/50 generated cases in 52 provider attempts. A single extra request per failed case added two provider calls and recovered both; total measurement inference attempts are 54. The mapped recovery view contains 50 cases/150 messages and preserves all source artifacts. Its apparent 50 retained attempts are reused source evidence, not 50 additional network calls. Human scoring remains pending for all cases; metrics and source map are in docs/verification/full-50-*.

## Major source-defect repair — v0.7.1

70 tests pass: new coverage distinguishes birthday/festival source frames, wrong-occasion/date bodies, no fallback on clarification, unknown material properties versus non-promises, client claims versus advisor records, unsupported carrying modes, and four recovery-provenance boundaries. The 17-case unchanged-input repair population generated 51 drafts, all pending human ratings; it is not a holdout. A fresh full fixed-50 run is measured under evaluation-freeze-v0.7.1.json. Twenty current guardrails match with zero calls. Earlier test/measurement records remain historical evidence.

## Broader product-claim regression — v0.8.0

v0.7.1 full execution reached 50/50 generation without recovery, but source inspection found scratch-protection assertions not present in catalogue data. Recommendation composition therefore separates source facts from model-authored preference questions. Five additional tests verify that the selected item is preflight-eligible, all nine fixed recommendation inputs yield complete source frames, assertions/numeric/guarantee bodies are rejected, non-success does not create output and raw question provenance remains intact. Current suite: 75 tests passed. The reused 23-case validation set is a tuning population, not a holdout.

## Current completed measurement — v0.8.2

76 deterministic tests pass. The reused 23-case tuning set generated 69 drafts; current guardrails matched 20/20 with zero calls. A fresh fixed-50 measurement generated 50/50 cases and 150 drafts without additional recovery. There were 51 within-run provider attempts: S4-01 required one configured repair after an invalid candidate-count response. All raw attempts remain saved.

The complete CSV matches original candidate strings in all 150 cells, frozen code/input hashes remain unchanged, and all 25 source-composed records (8 greeting, 9 recommendation, 8 invitation) reconstruct exactly from raw model bodies and trusted facts. All 50 human assessments remain pending; remaining care/price/context/style findings are documented. A blank 150-row review worksheet is supplemental, not a direct evaluator format.
