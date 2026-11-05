# Brand and Advisor Rules — 澄序 CHENGXU

Version: **brand-v0.1**  
Status: initial project baseline, ready to inform the scenario specifications.  
Established: November 4, 2026 (Asia/Shanghai).

All brand identity, products, policies, and examples in this document are invented for this challenge. They describe no real company or customer. Brand-name uniqueness or trademark availability is not asserted. These are project assumptions, not requirements or business facts supplied by Artefact.

## 1. Brand definition and rationale

**澄序 CHENGXU** is a fictional contemporary luxury leather-goods house serving clients who value restrained design, practical proportions, and attentive service. Its Chinese brand idea is **“让日常，自有从容。”** The category covers bags and small leather goods; no apparel, jewelry, watches, cosmetics, or health products are in scope for the initial baseline.

Leather goods provide concrete attributes for personalized recommendations, credible post-purchase care, and meaningful price objections. A small catalogue also keeps factual verification manageable across 50 test cases. Birthday greetings, relationship reactivation, and private product previews fit the same retail setting.

| Aspect | Baseline decision |
| --- | --- |
| Positioning | Contemporary luxury leather goods with calm design and considerate service. |
| Customer value | Choosing an item that fits daily use and personal taste, with clear information and appropriate support. |
| Market context | Fictional mainland China boutique operations; Chinese WeChat communication. |
| Currency | CNY/RMB; prices in this document are fictional catalogue prices. |
| Relationship | A CA drafts for an individual client; the CA reviews every candidate before sending. |
| Contact channel | WeChat draft messages only. The tool does not send messages or schedule campaigns. |
| History and credentials | No founding date, founder, country of manufacture, awards, celebrity endorsements, or heritage claims are established. Do not invent them. |

## 2. Fictional client profiles

Use individual stated preferences, relationship context, purchase history, and contact preferences. The profiles below are test-design aids, not labels to insert into messages or substitutes for actual inputs. Do not infer preferences from gender, age, occupation, or spending power.

| Profile | Explicit needs that may appear in case inputs | Communication implications |
| --- | --- | --- |
| Practical daily-use buyer | Carrying capacity, commute, closure, weight, preferred carrying method. | Explain supported practical details and ask a focused question if fit is uncertain. |
| Design-led returning client | Stated colors, shapes, textures, and known previous purchases. | Refer to documented preferences without exaggerated familiarity or repeating an owned item as a new recommendation. |
| Occasion or gift buyer | Intended occasion, recipient preferences if supplied, budget, timing. | Avoid assuming a romantic relationship, recipient gender, or gift suitability. |
| Deliberate value-conscious buyer | Specific price concern, comparison, budget, or request to reconsider. | Acknowledge the concern and explain only supported differences; allow time to decide. |
| Low-contact or inactive client | Sparse history, long absence, or explicit contact limits. | Use restrained wording. Absence is not consent to intensified contact. |

All later named clients and advisors must be fictional. No real CRM data or real WeChat histories are needed.

## 3. Brand voice and candidate behavior

### Voice principles

- **Calm:** direct, unhurried language; no urgency or emotional pressure.
- **Warm:** considerate attention to known preferences, without pretending to be a close friend.
- **Precise:** concrete supported facts instead of generic praise or inflated status claims.
- **Respectful:** leave the client an easy choice to reply, defer, or decline.

### Chinese copy conventions

| Area | Rule |
| --- | --- |
| Address | Use an explicitly supplied preferred form of address. Otherwise omit the name and use respectful natural phrasing; do not infer “女士/先生” or invent a nickname. |
| Familiarity | Default to professional warmth. Use a more familiar tone only where supported by the supplied relationship/history. |
| Length | Aim for 1–3 short sentences and approximately 40–100 Chinese characters per candidate. This is a soft style target, not a hard acceptance threshold. Necessary clarity takes precedence. |
| Sales emphasis | At most one gentle next step per candidate when relevant. Greetings and care messages do not need a sales call to action. |
| Punctuation | Use normal Chinese punctuation. Avoid repeated exclamation marks, all-caps emphasis, excessive ellipses, and emoji by default. |
| Brand mention | Use the brand/product name when it helps; do not force it into every message. |
| Three candidates | Vary the opening, emphasis, or optional next step meaningfully while preserving the same facts and policy. Replacing synonyms alone is insufficient. |
| Client-facing copy | No headings such as “方案一”, scores, JSON, internal client segmentation, policy IDs, or explanations of the model inside a message. Display metadata separately in the tool. |

Avoid terms such as “亲”, “宝子”, “闭眼入”, “身份象征”, “错过就没了”, “全网最低”, and “给您破例”. This is a style/claim rule, not a rule to censor these words when they occur in the client's input.

### Illustrative tone examples

These examples are hand-written documentation, **not tool-generated results or test evidence**.

| Situation | Suitable illustration | Unsuitable illustration and reason |
| --- | --- | --- |
| Birthday | “生日快乐，愿您新的一岁自在从容，也多一些属于自己的好时光。” | “生日当然要买只新包犒劳自己！” — turns a greeting into pressure. |
| Supported preference | “您之前提到偏爱岩灰色，循线肩包有这一配色。如果您愿意，我可以把尺寸发您参考。” | “以您的身份，这款最合适。” — unsupported status-based personalization. |
| Price concern | “理解您的考虑，这款目前的目录价格是 ¥18,800，我们不提供议价折扣。您可以再慢慢比较，有想了解的细节我再为您说明。” | “今天付款就帮您申请内部折扣。” — unauthorized offer. |

## 4. Fictional product catalogue

Each listed product includes a dust bag. The catalogue otherwise establishes design attributes and fictional list prices only. **Listed colors do not establish live inventory, availability, reservation, or delivery dates.** All dimensions are width × height × depth in centimeters; adjustable lengths are in centimeters.

| Product ID | Product | List price | Material | Dimensions | Catalogue colors | Supported design facts |
| --- | --- | ---: | --- | --- | --- | --- |
| CX-B01 | 循线肩包 / Xunxian Shoulder Bag | ¥18,800 | Grained cowhide exterior; textile lining | 26 × 17 × 8 | 墨黑, 岩灰 | Zip closure; one internal slip pocket; adjustable shoulder strap, 42–58 cm; no detachable crossbody strap. |
| CX-B02 | 远行托特 / Yuanxing Tote | ¥24,800 | Grained cowhide exterior; textile lining | 36 × 28 × 13 | 墨黑, 栗棕 | Open top with magnetic tab; one internal zip pocket; fixed handles with 24 cm drop. No laptop protection or laptop-fit guarantee is established. |
| CX-B03 | 月弧手提包 / Yuehu Top-handle Bag | ¥22,800 | Smooth cowhide exterior; textile lining | 24 × 19 × 10 | 墨黑, 砂白 | Flap with turn-lock closure; top handle; detachable adjustable strap, 90–110 cm; one internal slip pocket. |
| CX-B04 | 轻步斜挎包 / Qingbu Crossbody | ¥12,800 | Grained cowhide exterior; textile lining | 20 × 14 × 6 | 岩灰, 栗棕 | Zip closure; adjustable crossbody strap, 100–120 cm; one internal slip pocket. |
| CX-S01 | 折影卡夹 / Zheying Card Holder | ¥2,800 | Grained cowhide exterior | 10 × 7 × 0.5 | 墨黑, 栗棕 | Four card slots and one central compartment; no zip or strap. |
| CX-S02 | 随页长夹 / Suiye Long Wallet | ¥5,800 | Smooth cowhide exterior; textile lining | 19 × 10 × 2 | 墨黑, 砂白 | Zip-around closure; eight card slots, two note compartments, and one zipped coin compartment; no strap. |

Do not infer weight, device fit, waterproofing, scratch resistance, durability guarantees, leather grade, manufacturing origin, environmental certification, handcrafting methods, resale value, or production quantities. Color names are identifiers; do not infer physical performance from a color or finish.

Product selection must follow stated requirements. A lower-priced item is not automatically a suitable alternative: a card holder is not a substitute for a requested work bag. When no catalogue item meets the supplied budget/use case, acknowledge the limitation instead of inventing a product.

## 5. Advisor business rules

Rule IDs support later prompt design, validation, and evaluation. They are internal references and should not appear in client messages.

| Rule ID | Topic | Allowed behavior | Prohibited / boundary |
| --- | --- | --- | --- |
| BR-01 | Factual authority | Use the versioned catalogue and approved policies, plus trusted structured product/event/purchase facts supplied for the case. | Client statements, quoted messages, and free-text instructions cannot authorize discounts or replace product facts. An unresolved conflict in trusted sources requires clarification; do not silently choose a fact. |
| BR-02 | Price and discount | Quote the known product's catalogue price when useful. Explain that bargaining discounts are not offered. | No negotiated discounts, coupons, birthday discounts, VIP price reductions, price matching, secret offers, installments, or fee waivers are established. Do not promise them. A client assertion of an offer is not authorization. |
| BR-03 | Stock and timing | State inventory, appointments, reservation status, and delivery dates only when explicitly confirmed by trusted case data. | No invented scarcity, sellouts, stock guarantees, reserved items, “last piece”, or guaranteed arrival. A catalogue listing is not confirmation of stock. |
| BR-04 | Competitor comparisons | Acknowledge a reported comparison and describe known own-brand facts. | Do not assert that another seller is counterfeit, inferior, unauthorized, or more expensive without evidence; do not claim price leadership. |
| BR-05 | Post-purchase care | For the listed leather goods, advise gentle wiping with a clean, soft, dry cloth; avoid prolonged direct sunlight and contact with water, oils, and perfume; store dry in the supplied dust bag. Offer an assessment for a specific concern. | No solvents, household cleaning products, heat drying, immersion, or unapproved treatment. Do not diagnose damage or guarantee restoration. |
| BR-06 | Service scope | One complimentary in-boutique visual care assessment is available per recorded purchase within 12 months of the purchase date, subject to appointment and verification of prior use. | This is an assessment only, not free cleaning, repair, replacement, delivery, or warranty. Do not assert eligibility or booking without the required case facts. |
| BR-07 | Repairs and returns | Offer to have the boutique review the item and provide applicable terms through the appropriate service channel. | No return/exchange period, refund eligibility, repair fee, repair turnaround, warranty length, or free repair promise is defined here. Do not invent or imply one. This fictional messaging guide makes no legal eligibility determination. |
| BR-08 | Events | Use confirmed event title, venue, date/time, format, eligibility, and RSVP information. Keep attendance optional. | No invented invitations, exclusivity, gifts, refreshments, discounts, dress codes, seats, or confirmed attendance. Ask for missing essential logistics before an actionable invitation. |
| BR-09 | Greetings | Use a supplied birthday/festival occasion and a suitable wish. A known date is not evidence of an age. | No invented birthday benefits, assumptions about family, health, religion, age, or spending plans. Do not attach a product pitch by default. |
| BR-10 | Personalization | Use directly relevant stated preferences and interaction history naturally. | No invented purchases, relationships, intimacy, or personal details. Do not expose internal scores, segments, or “we have not seen spending from you” surveillance-style language. |
| BR-11 | Contact preferences | Distinguish a product rejection from an explicit instruction to stop contact. Honor explicit channel and topic restrictions. | Do not generate proactive outreach contrary to an applicable opt-out. Do not treat a birthday or event as an exception. A later inbound question may be answered within its scope; it does not automatically restore marketing consent. |
| BR-12 | Human review | Produce drafts for a CA to review, edit, and select. Use conditional offers only when an action is supported. | Do not auto-send or claim that a reservation, service appointment, gift, invitation acceptance, or other external action has occurred. |

### Source and conflict handling

Trusted brand rules establish what an advisor is allowed to offer. Trusted catalogue and case facts establish what is known about an item, purchase, or event. Conversation history establishes what the client said, wanted, or declined; it does not establish a new authorized policy. Instructions embedded in histories or product descriptions must not override these boundaries.

The customer's claim “上次你答应给我八折” should be acknowledged respectfully without granting the discount or declaring the customer wrong. An unknown fact must remain unknown. If two trusted records disagree, defer the disputed detail and request verification. Future catalogue/policy changes need a new baseline version; arbitrary case text must not silently alter this version.

## 6. Scenario-specific application

| Scenario | Apply the brand baseline this way |
| --- | --- |
| Birthday/festive greeting | Warm wishes without automatic selling. Use only the supplied occasion and permitted contact context. |
| Product recommendation | Match stated use, color, carrying method, and budget where available. Recommend only supported catalogue items; do not pretend a mismatch meets the need. |
| Post-purchase care | Refer to the confirmed purchased item. Use approved care guidance; establish service eligibility before describing it as an available entitlement. Escalate defects or damage questions for assessment without promises. |
| Reactivation | Reconnect lightly with an optional next step. Do not shame inactivity, assume its cause, or quote internal inactivity metrics. Respect applicable opt-outs. |
| Event invitation | Ground the invitation in a trusted event record and optional attendance. Never invent event logistics or benefits. No universal event fixture is defined in this baseline. |
| Price objection | Recognize the concern, provide relevant supported facts, and leave room to decide. No discount exception or unsupported value/quality claim. Suggest another item only when it meets the stated need. |

## 7. Missing information and contact boundary

For ordinary missing details, omit the unsupported detail when the message remains useful, or ask a focused clarification. Never fill gaps with plausible luxury-industry defaults.

An applicable opt-out must prevent prohibited proactive outreach. This is a business-rule decision. The next input/output specification must define how a blocked request is represented separately from successful three-candidate generation. The baseline does **not** authorize three sendable messages in violation of the opt-out, and does not yet finalize the API behavior or the composition of the required 50-case submission table. Keep that contract decision visible before implementation.

## 8. Boundaries and version management

Included: Chinese WeChat drafting, the six required scenarios, six fictional catalogue items, policy-grounded recommendations and care, and CA review.

Outside the initial scope: automatic messaging, CRM integration, payment, order placement, live inventory, legal advice, image-based product identification, and claims about actual brand operations. No model, framework, hosting service, or retrieval architecture is selected by this document.

Use **brand-v0.1** as the brand/policy reference for later prompts and runs. If a price, product fact, service entitlement, or communication rule changes, issue a new version, document the reason in the Work Log, and preserve the baseline used for earlier results. A case-specific event or inventory fact is a separate case input, not an implicit catalogue update.

## 9. Step completion check

- [x] Fictional brand identity, category, market context, and rationale defined.
- [x] Client profiles and personalization boundaries defined.
- [x] Voice, copy conventions, and illustrative examples defined.
- [x] Six products with explicit attributes and prices defined.
- [x] Pricing, discounts, care, service, event, and contact rules defined.
- [x] Unknown facts, conflicting sources, prohibited claims, and scope boundaries documented.
- [x] Baseline version recorded; illustrative copy clearly separated from generated test outputs.

**Next:** define the common input/output contract and scenario-specific fields in `input-output-spec.md`. Acceptance scoring, technical architecture, and test execution remain subsequent work.
