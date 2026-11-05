> Historical working draft. Superseded by the current documents under `docs/`. Relative evidence links have been adjusted for this archive location; recorded versions and outcomes have not been rewritten.

# Evaluation Report — Source-Bound Revision v0.8.2

## Current measured revision — v0.9.7

Tool/prompt-v0.9.7: 50/50 cases meet the stricter **AI-applied** case threshold, mean 4.31/5; genuine human review and release acceptance remain pending. [Detailed evidence and limitations](../../verification/ai-quality-review-v0.9.7/REPORT.md). The fixed 50-case dataset was actively used for tuning, so this is not holdout evidence.

All local requests now use program-authored evidence-bound reference copy edited by a real local LLM (98/150 raw bodies unchanged from reference). Greetings/products/events receive source frames; all local successes receive audited exact-address restoration, necessary policy/prior-offer context and narrow pronoun/typo normalization before grounding checks. Failed inference has no reference fallback. Every reference, raw provider output and transformation is retained. Source framing derives from fields, not case IDs. The same shared service powers UI and batch. Current freeze, full review and strict CLI replace the old deferred-work status.

Earlier sections below describe historical implementation/results and retain their recorded versions. Their thresholds and outcomes are not retroactively rewritten.


**Status: complete measured output set; human quality acceptance pending.** This is not a release recommendation. The historical v0.6.1 package and all intermediate artifacts remain preserved.

## November 5 AI-assisted review supplement

[Complete source-based review](../../verification/ai-quality-review-v0.8.2/REPORT.md) covers 150/150 candidates: **16/50 cases meet the AI-applied threshold; mean raw score 3.6767/5; overall target fails**. One tentative HF-02 is pending human adjudication (conservative mean 3.6137). These are AI-authored editorial scores, not human acceptance or independent holdout results. All human ratings remain pending; original evaluation artifacts and archives are preserved.

## Current run and evidence

Tool/prompt-v0.8.2, brand-v0.1, io-v0.1 and eval-v0.1; local Ollama qwen3:4b. The model weights/template and business baseline are unchanged. [Freeze and source hashes](../../verification/evaluation-freeze-v0.8.2.json) · [Integrity checks](../../verification/full-50-integrity-v0.8.2.json).

- **50/50 cases generated, 150 retained drafts**, from a fresh full fixed-dataset batch; no extra recovery requests or mixed-version replacements.
- **51 provider attempts**, including the service's configured bounded repair within the full batch. This is not a claim of 50 first-attempt successes.
- **76 deterministic tests passed**; **20/20 guardrails matched with zero model calls**. The 23-case reused target set generated 69 drafts and is explicitly a tuning population, not a holdout.
- **All 50 human assessments remain pending.** No human mean quality score, human quality pass rate or zero-hard-failure claim is supported; the separate AI review above must not be interpreted as human acceptance.

[50-row / 150-output CSV](../../verification/full-50-cases-v0.8.2.csv) · [Saved evaluation](../../verification/full-50-evaluation-v0.8.2.json) · [Source map](../../verification/full-50-source-map-v0.8.2.json) · [Metrics](../../verification/full-50-summary-v0.8.2.json) · [Blank JSON rating template](../../verification/human-ratings-v0.8.2.json).

The original case allocation remains 8 greetings, 9 recommendations, 8 care, 8 reactivation, 8 invitations and 9 price objections. All exact CSV cells were checked against raw candidate text. Source hashes and frozen runtime/input hashes match, with one configuration identity.

## What was authored by the model

25 cases use explicitly disclosed hybrid composition: eight greeting cases bind the actual occasion/address to model-written wishes; nine recommendation cases combine catalogue facts with model-written preference questions; eight event cases add confirmed logistics to model-written invitation bodies. The other 25 cases contain model-authored full messages. All 50 involve actual local model calls, but the 150 final messages are not described as wholly model-authored prose.

Recommendation selection is deterministic: the first preflight-eligible product, not LLM ranking. Colour/price, a structure clause and dimensions come from the catalogue. The model receives the use requirement and one structure fact, then writes three questions within a checked scope. This limits invented product properties at the cost of predictable, question-heavy messages. Some model questions reuse the supplied style examples. Their usefulness and diversity still need human review.

Each composed case retains raw provider content, model body texts, verified frame(s), source fields, selection metadata and final messages. All 25 composition records were reconstructed and compared with saved outputs. No failed inference is replaced with a fabricated template result.

## Versioned results and iteration

| Version / population | Generated cases | Candidates | Interpretation |
| --- | ---: | ---: | --- |
| v0.6.1 initial full run | 48/50 | 144 | Two failures preserved |
| v0.6.1 same-version recovery | 2/2 | 6 | One additional request for each failed case; mapped view has 150 drafts, not a second independent run |
| v0.7.1 fresh full run | 50/50 | 150 | Birthday/history examples improved, but new scratch-protection assertions appeared |
| v0.8.0 target validation | 21/23 | 63 | Two rejected numeric question bodies |
| v0.8.1 target validation | 23/23 | 69 | Generation success hid copied writing instructions; retrospective v0.8.2 checks identify 9 leakage cases |
| v0.8.2 target validation | 23/23 | 69 | All generated; quality review still pending |
| **v0.8.2 fresh full run** | **50/50** | **150** | **Current measured set; no extra recovery; all human scores pending** |

Old results were not overwritten. Evaluator outputs now record the checker implementation/hash; later checks on older artifacts are retrospective rather than the original historical evaluation. `scripts/reconcile_recovery.py` enforces exact failed-case selection, unchanged facts/runtime and byte-preserving sources when needed; it was not needed for the current full run.

## Source-defect before/after examples

The complete [same-case version comparison](../../verification/source-fix-full-comparison-v0.8.2.json) retains v0.6.1/v0.7.1/v0.8.2 texts and run IDs. The following are assistant-selected source examples, not numerical human ratings or an exhaustive review of 150 candidates.

| Case | Historical problem | Current change and limit |
| --- | --- | --- |
| S1-01 / S1-03 / S1-08 | Birthday replies included generic festival wording or unsupported relative-date phrasing. | Exact occasion/address frames are source-bound. All eight current greeting records reproduce the correct source frame; wishes remain sparse/generic. |
| S2-02 | Catalogue material became a wear-resistance claim. | Product statements now use source-backed facts; model contributes questions, not free-form performance statements. |
| S2-06 / S2-07 | v0.7.1 invented protection from scratching after narrower keyword checks had passed. | All nine recommendation frames reconstruct from catalogue/eligibility data. Selected current card/wallet examples omit protection claims. Scope checks are still not full semantic verification of question implications. |
| S6-06 | Customer's claimed discount was attributed to a confirmed past advisor discussion. | Current opening attributes the claim to the customer; explicit advisor-history assertion is removed. Other wording still needs review, including a new unsupported absolute material-availability statement. |

## Remaining source-linked findings

| Case / candidate | Actual current excerpt | Assistant finding |
| --- | --- | --- |
| S3-06 / 2 | 收到后/以后，记得避免长时间日晒和水、油、香水的接触，保持干燥并放入随附防尘袋。 | Copies the template-like phrase received-after/later into a response about an already reported water issue; scenario fit and naturalness remain poor. |
| S6-06 / 2 | 循线肩包采用粒面牛皮制作，这是目前我们唯一可提供的材质。关于价格和折扣政策，我们再次说明不提供议价折扣。 | The absolute claim that this is the only material that can be offered is not established as an offer/availability policy. |
| S4-05 / 3 | 方便的时候再聊，我这边随时待命。 | Generic availability and repetitive contact intent still need semantic diversity review. |
| S5-01 / 2 | 顾客甲，11月8日14:00想邀请您参加澄序皮具私享预览，地点是澄序虚构示范精品店·二层会客区。如果您想查看光面牛皮、旋锁开合以及可拆卸肩带的设计细节，这里为您准备了相关信息。 | Claim that related information has been prepared and informational wording should be reviewed against the event record; model body remains more about design information than attendance. |

[Structured findings and source references](../../verification/full-50-assistant-findings-v0.8.2.json). These are not human adjudications; known unresolved issues prevent a claim that material quality problems have all been eliminated. Greeting brevity, recommendation question repetition, care context, invitation purpose and price phrasing remain review items.

## Metrics and acceptance

The measured sum of per-attempt inference durations is **142.245 seconds**, with **2.275 seconds median per attempt**; these are not end-to-end benchmark guarantees. The provider reported 40,809 prompt tokens and 3,099 completion tokens across 51 attempts. No paid API calls were used; token usage is not a billing estimate. Full detail is in the metrics JSON.

Project-authored eval-v0.1 targets remain unchanged: at least 45/50 accepted, mean effective score at least 4/5, at least 75% accepted per scenario, zero verified hard failures, complete output evidence and all guardrails passing. A generated response, a zero automatic-error list or a source-composed frame is not human quality acceptance. Existing ratings are all pending, not 0% or 100% quality scores.

Human assessment must review all three candidates against exact client history/catalogue/policy, enter real six-dimension scores and set diversity, cite any hard failures, and identify assessor/time. The optional CSV worksheet has empty score cells and is an aid; the evaluator consumes the JSON template. Do not copy assistant suggestions or retrospective observations into fabricated human scores.

## Decision and next steps

The three prioritized source-defect classes have concrete improvements and source-bound controls, with a complete new measurement and transparent failed iterations. **No release acceptance is claimed.** Next: adjudicate remaining care/event/price findings, repair confirmed major issues under a new version, and complete genuine human scoring before final conclusions. A changed implementation needs a separate measurement. Those quality gates are currently deferred by user direction. Current document/delivery preparation does not rerun or score cases, waive the outstanding assessment, or imply quality acceptance. The local review ZIP is a draft; nothing was sent, uploaded or published.
