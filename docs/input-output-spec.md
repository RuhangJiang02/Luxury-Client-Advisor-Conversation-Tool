# Input and Output Specification

Contract version: **io-v0.1**  
Brand dependency: **brand-v0.1**, [Brand and Advisor Rules](brand-and-rules.md).  
Status: P1 design baseline, implemented through a strict request schema and shared Python generation service in tool-v0.2. Semantic policy screening is partial and requires human review; live API verification remains deferred. See [running and evaluation](running-and-evaluation.md).

The brief requires client information, scenario, conversation history, relevant product information, and three Chinese WeChat candidate messages. Field names, states, and validation behavior below are project design decisions. Examples are invented, hand-written fixtures, not generated outputs or completed test cases.

## 1. Contract boundaries

Use one request envelope for all six scenarios, with a scenario-specific `scenario_context` object. Use one response envelope to separate client-facing copy from advisor notices and technical metadata.

- A successful request returns **exactly three non-empty Chinese message candidates**.
- Missing essential facts, applicable contact restrictions, invalid requests, and technical failures do not produce sendable placeholders. They return an explicit non-success state and zero candidates.
- The CA reviews and chooses a candidate. This contract never sends messages or performs reservations, purchases, or bookings.
- Optional unknown values are `null` or omitted. Required nullable fields must be present, even when unknown. An empty array means no known records were supplied, not proof that none exist.
- Dates use `YYYY-MM-DD`; timestamps use ISO 8601 with an explicit offset. `timezone` is `Asia/Shanghai` in the initial scope. Currency is `CNY`. Use the supplied reference time, not the execution machine's clock.
- Unknown fields, unsupported enum values, inappropriate types, duplicate record IDs, and scenario-context mismatches are rejected. Do not silently strip them.

## 2. Common request envelope

| Field | Type | Presence | Definition |
| --- | --- | --- | --- |
| `contract_version` | string | Required | Literal `io-v0.1`. |
| `request_id` | non-empty string | Required | Unique identifier for this attempt; a corrected request gets a new ID. |
| `case_id` | string or null | Optional | Stable evaluation-case ID, if applicable. |
| `scenario` | enum | Required | One of the six identifiers in section 4. |
| `reference_time` | timestamp | Required | Evaluation/drafting reference time, including UTC offset. |
| `timezone` | string | Required | Literal `Asia/Shanghai` for this baseline. |
| `interaction` | object | Required | Draft purpose and contact direction; see below. |
| `client` | object | Required | Fictional client information and documented contact preferences. |
| `conversation_history` | array of message objects | Required | Chronological messages; `[]` is allowed for proactive scenarios. |
| `product_ids` | array of distinct strings | Required | Relevant catalogue IDs; `[]` when not needed. Resolves product information from the pinned brand catalogue, not from client claims. |
| `scenario_context` | object | Required | Exactly the fields applicable to the chosen scenario. |
| `trusted_context` | object | Required | Versioned brand/catalogue references and source-backed case facts, assembled by the application or controlled fixtures. |

### Interaction object

| Field | Type | Presence | Meaning |
| --- | --- | --- | --- |
| `mode` | `proactive` or `reply` | Required | Initiating contact versus responding to an inbound client message. |
| `channel` | string | Required | Literal `wechat`. |
| `reply_to_message_id` | string or null | Required | Must reference a client message in history when mode is `reply`; must be null when proactive. |

`price_objection` requires `reply`. Other scenarios may use either mode when the history supports it. A reply must address a current inbound request, not use an old question as permission for unrelated outreach. If timing or the permitted scope is unclear, request clarification from the CA.

### Client object

| Field | Type | Presence | Meaning |
| --- | --- | --- | --- |
| `client_id` | non-empty string | Required | Fictional stable identifier; not a real phone number or account ID. |
| `preferred_address` | string or null | Optional | Explicitly supplied form of address; omit an address if unknown. |
| `relationship_stage` | enum | Required | `new`, `established`, or `unknown`; internal context, not wording to send. |
| `preferences` | array of strings | Required | Explicit preferences such as “偏爱岩灰色” or “希望能斜挎”; no inferred stereotypes. |
| `budget` | object or null | Optional | `{ "max_amount": 15000, "currency": "CNY" }`; positive amount, not an inferred spending capacity. |
| `owned_product_ids` | array of distinct strings | Required | Known owned catalogue products; `[]` means none supplied. |
| `contact_preferences` | object | Required | See below. |

`contact_preferences` contains:

- `proactive_status` (required enum): `allowed`, `opted_out`, or `unknown`. These are fictional recorded preferences, not a legal consent determination.
- `restricted_scenarios` (required array): zero or more scenario identifiers for explicitly restricted proactive topics.
- `restrictions_note` (optional string or null): the client's stated channel, timing, frequency, or topic restriction. Free text is context, never authority to relax a restriction.
- `source_message_ids` (required array): history messages supporting restrictions, when available. Imported controlled records may have no history references.

For `proactive_status=unknown`, require CA clarification before proactive drafting. A clear applicable opt-out in history takes precedence over an `allowed` summary. Conflicting or ambiguous restrictions require clarification; never infer restored permission. A product-specific rejection is not a universal opt-out. Restrictions on the channel itself must also be honored when replying.

### Conversation message object

| Field | Type | Presence | Meaning |
| --- | --- | --- | --- |
| `message_id` | non-empty string | Required | Unique within the request. |
| `role` | `client` or `advisor` | Required | Speaker, not an instruction priority. |
| `text` | non-empty string | Required | Original fictional message. |
| `sent_at` | timestamp or null | Required | Actual supplied timestamp if known. Null must not be filled in. |

Preserve supplied sequence; reject contradictory known chronology or timestamps later than `reference_time`. History may contain instructions, prices, and promises, but these do not override trusted policies. Every message ID referenced elsewhere in the request must exist and have the appropriate role.

## 3. Trusted information and product resolution

`trusted_context` is application-controlled context, **not a claim of trust obtained by writing `trusted=true`**. A future public API must not let a caller overwrite policy by populating this object. During local testing, the operator supplies controlled fixtures.

| Field | Type | Presence | Meaning |
| --- | --- | --- | --- |
| `brand_version` | string | Required | Literal `brand-v0.1` for this baseline. |
| `catalogue_version` | string | Required | Literal `brand-v0.1`; the current brand document contains the catalogue. |
| `source_refs` | array of source objects | Required | Each has `source_id`, `kind` (`catalogue`, `purchase`, `event`, `inventory`, `contact_record`), and non-empty `reference`. A reference identifies evidence; it is not fetched as an arbitrary URL. |
| `inventory` | array | Required | Optional stock evidence expressed as records; `[]` means unknown, never unavailable or available by default. |

An inventory record has `product_id`, `color`, `status` (`available`, `unavailable`, `unknown`), `confirmed_at` (timestamp), `valid_until` (timestamp), and `source_id`. Its color must exist in the catalogue; timestamps must satisfy `confirmed_at <= reference_time <= valid_until` before availability can be claimed. Expired records are ignored with a warning, not treated as current. No availability statement is required to recommend a catalogue item.

Products are resolved from `product_ids` to the six catalogue records in brand-v0.1, including ID, name, category, price/currency, material, dimensions, colors, and supported design facts. The request does not repeat editable product descriptions or prices. Each request that resolves products must include a `catalogue` source reference. The run record stores the **resolved product snapshot**, so the exported test case contains readable product information, not just IDs. Unsupported product IDs require clarification rather than an invented product; malformed ID types are invalid input.

Purchase/event contexts reference `source_id` entries of matching kinds. An ID match establishes referential consistency; source authenticity depends on the controlled application boundary. If trusted sources disagree with the pinned baseline, request clarification. A different policy or catalogue needs an explicit version change.

## 4. Six scenario-specific contracts

### S1 — `greeting`

| `scenario_context` field | Type | Presence / behavior |
| --- | --- | --- |
| `occasion_type` | `birthday` or `festival` | Required. |
| `occasion_name` | string or null | Required non-empty string for a festival, e.g. “中秋节”; null for birthday. |
| `occasion_date` | date or null | Required field. Confirmed occurrence date, not birth year; unknown is allowed if wording omits timing claims. |

Products are not needed: `product_ids=[]`. Do not infer a birthday age, lunar date, festival date, gift, or privilege. If the date is unknown, avoid “今天/明天”; if supplied and different from the reference date, avoid a false same-day greeting. Soft date-neutral wording may still be generated. No product pitch by default.

Candidate variation: a concise wish, a warmer relationship-appropriate wish, and a restrained occasion-focused wish. All remain greetings, not invented benefits.

### S2 — `product_recommendation`

| `scenario_context` field | Type | Presence / behavior |
| --- | --- | --- |
| `use_case` | string or null | Required field; may be unknown. |
| `must_have` | array of strings | Required; hard client requirements, e.g. “可斜挎”. |
| `preferred_color` | string or null | Optional; supplements known client preferences without overriding an unresolved conflict. |

Require one or more `product_ids`. If none are supplied, ask the CA to select candidate products; do not silently search outside the catalogue. Sparse preference data may produce cautious wording or a client-facing preference question, with a warning. Hard budget/use constraints must not be represented as met when unsupported. When no supplied product fits, return `needs_clarification` to the CA for revised selection/requirements rather than pretend a match.

Candidate variation: supported use-case fit, supported design details, or a low-pressure preference question. Do not invent fit, weight, stock, or product performance.

### S3 — `post_purchase_care`

| `scenario_context` field | Type | Presence / behavior |
| --- | --- | --- |
| `purchase` | object | Required. See purchase fields below. |
| `care_topic` | `general`, `usage_check`, or `reported_issue` | Required. |
| `issue_message_id` | string or null | Required client-message reference for `reported_issue`; otherwise null. |

Purchase fields: `purchase_id` (non-empty string), `product_id` (catalogue ID), `purchased_on` (date or null), `source_id` (purchase source reference), and `assessment_used` (boolean or null). Exactly one product is in scope per request and `product_ids` must equal `[purchase.product_id]`. The purchase is verified by its controlled source; a client statement alone is not proof of a transaction.

Unknown purchase date permits general care without timing claims; a future purchase date is invalid for this scenario. Complimentary assessment eligibility requires a known date, `assessment_used=false`, and reference local date within the inclusive period from purchase to its 12-calendar-month anniversary. If the anniversary day does not exist, use that month's last day. Unknown or expired eligibility must not be promised. Even when eligible, an appointment is required and no booking is implied.

Candidate variation: a brief usage check-in, approved care guidance, or a cautious offer of assessment where supported. A reported problem takes priority over cheerful selling; do not diagnose, guarantee repair, or promise refunds.

### S4 — `reactivation`

| `scenario_context` field | Type | Presence / behavior |
| --- | --- | --- |
| `last_contact_on` | date or null | Required field; unknown allowed. |
| `last_purchase_on` | date or null | Required field; unknown allowed. |
| `reconnect_purpose` | `relationship_check_in` or `preference_update` | Required. |

No arbitrary “inactive for N days” business threshold is introduced. The CA's scenario selection supplies the intent; timestamps provide context only. Reject future last-contact/purchase dates. Unknown history permits a general reconnection without claiming a previous meeting, purchase, or exact absence duration. `product_ids=[]`; a specific product recommendation belongs to S2, and an event invitation belongs to S5.

Candidate variation: a gentle check-in, a preference-update offer, or an invitation to reach out when convenient. Do not quote internal inactivity metrics or assume why the client was absent.

### S5 — `event_invitation`

| `scenario_context` field | Type | Presence / behavior |
| --- | --- | --- |
| `event_id` | non-empty string | Required. |
| `title` | string or null | Required field; non-empty to generate. |
| `format` | `boutique_event`, `private_preview`, or null | Required field; known to generate. |
| `starts_at`, `ends_at` | timestamp or null | Required fields; known, future start and strictly later end to generate. |
| `venue` | string or null | Required field; confirmed venue to generate. |
| `eligibility` | `eligible`, `ineligible`, or `unknown` | Required; must be eligible to generate. |
| `rsvp_method` | `reply_to_advisor` or null | Required field; known to generate. |
| `rsvp_deadline` | timestamp or null | Optional; if supplied, reference time must precede it and it must not follow event start. |
| `source_id` | non-empty string | Required event-source reference. |

Missing logistics, unknown eligibility, past events, or closed RSVP return `needs_clarification` for a valid current invitation. Known ineligibility returns `blocked`. Contradictory event interval types/order return `invalid_input`. Product IDs are optional for an actual product preview; no gift, exclusive privilege, seat, or discount is implied by the event format.

Candidate variation: clear logistics, relevance based on stated interests, or an easy RSVP invitation. All must preserve the same dates, venue, and optional attendance.

### S6 — `price_objection`

| `scenario_context` field | Type | Presence / behavior |
| --- | --- | --- |
| `objection_type` | `too_expensive`, `comparison`, or `discount_request` | Required. |
| `objection_message_id` | non-empty string | Required client-message reference; must equal `interaction.reply_to_message_id`. |
| `comparison` | object or null | Optional; object permitted only for `comparison`. |

Require `interaction.mode=reply` and exactly one relevant `product_id`. No editable discount-policy field is accepted. `comparison`, if supplied, contains `reported_seller` (string or null), `reported_amount` (positive number or null), and `currency` (`CNY` or null; required when amount is known). These are **client-reported claims**, not verified competitor facts; they must be supported by the referenced message, otherwise clarify the conflict. Compare only what is known and never infer authenticity or price leadership.

Candidate variation: empathy plus clear policy, relevant supported product facts, or room to defer and ask a focused question. Do not suggest an unrelated lower-priced item or invent discounts, installment plans, quality superiority, or resale value.

## 5. Response envelope

| Field | Type | Required behavior |
| --- | --- | --- |
| `contract_version` | string | `io-v0.1`. |
| `request_id` | string or null | Echo a recoverable request ID; null if an invalid request has none. |
| `case_id` | string or null | Echo the case ID if available. |
| `scenario` | string or null | Valid scenario if recoverable; otherwise null. |
| `status` | enum | `generated`, `needs_clarification`, `blocked`, `invalid_input`, or `generation_failed`. |
| `candidates` | array | Exactly three objects when generated; `[]` otherwise. Each object has only `candidate_id` (`1`, `2`, `3`, integer) and `text` (non-empty Chinese message). IDs are ordered and unique. |
| `notices` | array | CA-facing objects with `code`, `field` (JSON-style path or null), and `message`. Never include notices in client copy. |
| `clarifications` | array | Objects with `field` and `question`, addressed to the CA, not automatically to the client. Non-empty only for `needs_clarification`; at least one in that state. |
| `metadata` | object | System-created provenance and run details below; never client-facing. |

`metadata` contains `run_id`, `brand_version`, `catalogue_version`, `tool_version`, `prompt_version`, `model_id`, `started_at`, `finished_at`, `generation_attempts`, and `resolved_product_ids`. Versions/model may be null when not reached; attempts is a non-negative integer and is zero when preflight prevents generation. The exact model invocation record and resolved product snapshot belong in the stored run artifact. Do not store API keys or hidden model reasoning.

`generated` asserts structural and configured output checks passed, not that every semantic fact has been proven correct. Human evaluation remains necessary. Soft length/style deviations may be warnings; non-empty Chinese copy and three-candidate cardinality are mandatory. If provider failure or rejected output persists after the configured bounded retry, return `generation_failed`, never a partial candidate set or an unlabelled fallback. Retry count and semantic checks are subsequent implementation decisions.

### Preflight and outcome rules

Apply in this order: (1) request shape/types/versions/references; (2) contact and eligibility restrictions; (3) essential facts and source conflicts; (4) generation and output checks. Do not invoke the model for a known blocked request. Multiple notices may be recorded, but one primary status is returned.

| Situation | Status / code | Candidates |
| --- | --- | --- |
| Valid supported request and accepted output | `generated`; optional warnings | Exactly 3 |
| Missing required key, wrong type, bad date/order, unknown field, mismatched scenario context, dangling source/history reference, unsupported contract/brand version | `invalid_input` / `INPUT_INVALID` or `VERSION_UNSUPPORTED` | 0 |
| Applicable opt-out/topic/channel restriction | `blocked` / `CONTACT_RESTRICTED` | 0 |
| Known event ineligibility | `blocked` / `EVENT_INELIGIBLE` | 0 |
| Unknown proactive contact permission | `needs_clarification` / `CONTACT_PERMISSION_UNKNOWN` | 0 |
| Correctly shaped but insufficient essential facts | `needs_clarification` / `ESSENTIAL_FACT_MISSING` | 0 |
| Unknown catalogue item or no suitable selected product | `needs_clarification` / `PRODUCT_UNRESOLVED` or `NO_PRODUCT_FIT` | 0 |
| Conflicting trusted facts or unsupported client-claim extraction | `needs_clarification` / `SOURCE_CONFLICT` | 0 |
| Nonessential facts absent, unknown care entitlement, stale inventory | `generated` with `DETAIL_OMITTED`, `ELIGIBILITY_UNCONFIRMED`, or `INVENTORY_STALE`, if all other checks pass | Exactly 3; omit unsupported assertions |
| Provider error or output fails checks after retry budget | `generation_failed` / `MODEL_ERROR` or `OUTPUT_REJECTED` | 0 |

For inbound replies after an opt-out, verify that the referenced client message requests the response, the channel is permitted, and candidates stay within that request. This does not authorize new marketing. Ambiguous scope returns clarification; a clear prohibition blocks. Free-text history restrictions cannot be ignored merely because a structured summary says allowed.

## 6. Fixtures and implementation handoff

[The contract examples](../examples/io-v0.1/examples.json) contain one request per scenario and illustrative response envelopes. They are hand-written design fixtures, **not the required 50-case dataset and not evidence of a working tool**. They are intended to become implementation fixtures after a validator exists. The executable [request schema](../data/request.schema.json) now enforces object shape, enums, required fields, and scenario-specific context. Python checks handle references and business rules. Semantic interpretation remains limited as documented in the run guide.

The application must validate at two levels:

1. Structural checks: types, required fields, enums, conditional fields, timestamp formats, and prohibited extra fields.
2. Business checks: source resolution, date relationships, known contact restrictions, essential facts, catalogue fit, and grounded output behavior.

History interpretation and message grounding involve semantic judgment; documenting them does not make them deterministic validators. Specify practical checks and their limitations during acceptance/architecture design.

## 7. Mapping to the required 50-case submission

Export these exact brief columns: `Case ID`, `Scenario`, `Client information`, `Conversation history`, `Product information`, `Output 1`, `Output 2`, `Output 3`.

- Client information includes the fictional client plus relevant interaction and scenario context so dates, purchases, event facts, and preferences remain reconstructable.
- Product information contains the resolved snapshot, or `Not applicable`; the scenario name remains human-readable.
- Only `generated` cases populate Output 1–3 with actual tool messages. Preserve raw outputs, versions, request snapshots, and run IDs in linked artifacts/additional metadata.
- Plan **50 generation-eligible cases with three outputs each**, spanning all six scenarios and answerable difficult inputs. If a required case initially fails, record the failure and any correction/versioned rerun; do not fabricate messages or conceal it.
- Maintain additional guardrail/validation cases for opt-outs, missing essential facts, invalid input, and provider failures, with expected status and zero candidates. Report their coverage and results separately. They do not replace any of the 50 three-output cases.

This is the project decision resolving the opt-out/three-output tension: the brief's successful generation contract remains intact, and prohibited outreach is tested separately without producing sendable drafts.

## 8. Completion and next step

P1 step 2 is specified at design level: common fields, all six scenario contracts, conditional requirements, missing-information handling, output states, evidence metadata, and test-export mapping are documented. Structural checks and selected business rules are now implemented; live integration and message-quality evaluation remain unverified.

**Related completed designs:** [acceptance criteria](acceptance-criteria.md), [architecture](architecture.md), and [test design](test-design.md). Next verify a real provider call after local key configuration.
