# E — Defects and Next Steps

**Current measured version: tool-v0.9.7 / prompt-v0.9.7.** This register distinguishes observed repairs in the fixed development cases from unresolved language and validation limits. The current AI self-review meets 50/50 case thresholds; it does not establish independent human acceptance. [D — Evaluation](evaluation-report.md) defines the measurement scope.

## 1. Defects addressed in the current version

“Observed repair” means the selected final outputs and relevant checks address the recorded example. It is not a guarantee for every possible input. The [same-input before/after evidence](verification/final-before-after-v0.9.7.json) records exact text, case/candidate IDs, run IDs, source hashes and versions. No comparison text is an assistant-written replacement for a saved output.

| Defect | Before: actual evidence | Change | v0.9.7 observation / status |
| --- | --- | --- | --- |
| L-13 — Care reply misses current issue | v0.8.2 S3-06 candidate 2 says “收到后/以后” despite a current water incident | Reported-issue references prioritize immediate approved care, uncertainty and applicable assessment eligibility | Addresses the incident now; no outcome guarantee. Observed repair; dense wording remains |
| L-16 — Unsupported material availability | v0.8.2 S6-06 candidate 2 says “这是目前我们唯一可提供的材质” | Source-bound reference wording and explicit exclusivity checks | Material stated without unsupported exclusivity; old offer remains an unverified client claim. Observed repair |
| Q-01 — Recommendation ignores hard question | v0.8.2 S2-09 candidate 1 asks generally about carried items while laptop fit is the immediate issue | Laptop-aware question/reference route and source-supplied dimensions/uncertainty | Asks for measurements; cannot guarantee fit or waterproofing. Observed repair |
| Q-02 — Current discount request becomes past-offer dispute | v0.9.2 S6-07 candidate 1 invents a “previous offer” context | Prior-offer branch requires temporal evidence; source checker rejects unsupported context | Replies to current pricing challenge without an invented earlier offer. Observed repair |
| Q-03 — English insertion and message labels | v0.9.3 S3-04 contains “please”; v0.9.5 S6-04 starts “消息一：” | Language checks and broader internal-label rejection | Neither defect found in final scored outputs. Observed repair; markers are still a limited list |
| Q-04 — Dropped full address / required policy, informal pronoun | v0.9.6 loses known addresses; S4-07 and S6-06 exhaust bounded attempts | Audited client-copy composition restores the known address and missing required policy/context, normalizes singular pronouns and the observed typo | All final cases generated; 75 candidates record transformations. This is explicit program contribution, not improved raw-model reliability |
| Q-05 — Wrong occasion / omitted invitation logistics | Earlier source reviews exposed occasion confusion and incomplete event information | Trusted occasion/event frames; future-date framing and supplied deadline retained | Current framing reconstructs exactly from supplied facts. Generic body language still needs review |

## 2. Selected exact before/after examples

### Current water incident — S3-06, candidate 2

**Before, v0.8.2:** “收到后/以后，记得避免长时间日晒和水、油、香水的接触，保持干燥并放入随附防尘袋。”

**After, v0.9.7:** “顾客男，仅凭描述还不能保证没有影响。如想进一步确认，您这次购买尚有一次免费在店目视评估可用，需预约；不包含清洗或维修。”

The revised candidate answers the reported concern and the known entitlement instead of implying future receipt. It still has a dense policy explanation. Other candidates provide immediate approved care and a current-state question; no assessment is booked or repair guaranteed.

### Unsupported exclusivity — S6-06, candidate 2

**Before, v0.8.2:** “循线肩包采用粒面牛皮制作，这是目前我们唯一可提供的材质。关于价格和折扣政策，我们再次说明不提供议价折扣。”

**After, v0.9.7:** “顾客男，您提到的旧优惠需要先核对记录，目前不提供议价折扣。供您了解，循线肩包采用粒面牛皮。”

The revised candidate removes the availability/exclusivity inference and does not confirm the disputed old discount. Full provenance and four additional comparisons are in the [comparison artifact](verification/final-before-after-v0.9.7.json).

## 3. Iteration outcomes retained

| Version / population | Recorded outcome | Interpretation |
| --- | --- | --- |
| v0.8.2, full 50 | 50 generated; 16/50 AI quality thresholds; mean 3.6767 | Baseline defects preserved, not relabelled accepted |
| v0.9.0 / v0.9.1, targeted cases | Instruction copying, generic advice and rejected question bodies | Tuning populations, not full-run proof |
| v0.9.2, full 50 | 50 generated; false historical-offer context | Rejected after source triage |
| v0.9.3, full 50 | 50 generated; accidental English | Rejected after source triage |
| v0.9.4, full 50 | 49/50 AI thresholds; mean 4.3047 | Failed stricter target; scores preserved |
| v0.9.5, full 50 | Heading/pronoun defects | Rejected; its 25-case score record is explicitly partial |
| v0.9.6, full 50 | 48 generated; 2 explicit failures | No preview/reference fallback and no accepted claim |
| v0.9.7, fresh full 50 | 50 generated in 50 calls; 50/50 AI thresholds | Final single-version result; not a mixture of earlier candidates |

The final result belongs to the whole revised tool. Reference logic, prompts, source composition and configuration changed; unchanged model weights do not make this a controlled experiment on model capability alone. [Earlier working narrative](history/pre-final-consolidation-v0.9.7/defects-and-next-steps.md) retains the longer historical register.

## 4. Remaining defects and improvements

| Priority | Remaining issue / evidence | Next change or check | Completion condition |
| --- | --- | --- | --- |
| High | Scripted feel and limited cross-client variety; 98/150 raw bodies match references exactly | Independent Chinese-language review across different clients; assess repetitions before broadening language generation | Reviewer judges contextual voice/naturalness; any new runtime/config is measured separately |
| High | Development-set self-review; no independent or unseen-input result | Human assessment and a separate new-input evaluation population | Report assessor/scope and all misses without reusing the old 50/50 as new evidence |
| High | Pattern-based history, contact and claim interpretation is incomplete | Add contrasting temporal/negation/quotation cases, plus unsupported implication checks | Preserve expected blocked/clarification cases; report new false positives and misses |
| Medium | Fragmented recommendation opening, S2-01–07 | Simplify the source frame while retaining relevant budget/use facts | New version improves readability without losing constraints; new full measurement if changed |
| Medium | Dense care eligibility statement, S3-06; formal price reply, S6-07 | Reviewer-led wording revision against the same policy/source boundaries | Current raw text retained; newly generated outputs independently scored |
| Medium | Closely related alternatives, S6-08; diversity is measured within a case only | Evaluate distinct conversational purposes and cross-case variety separately | Distinct usefulness without forcing extra sales pressure or unsupported facts |
| Medium | First-eligible product selection is not ranking | Add explicit preference scoring only if the product set and evidence justify it | Explain selection and validate hard constraints; do not call current behavior LLM ranking |
| Before submission | Required screenshot evidence is absent | User-managed screenshot inclusion | A/D references point to actual supplied evidence; no text-only substitute claimed |
| Before submission | Identity fields and transmission are incomplete | Complete the private email/attachment handoff when explicitly instructed | Correct attachment/identity and actual sending recorded by the sender; no invented receipt |

The production backlog is separate: authentication, CRM authorization, retention rules, live inventory, multi-user isolation and monitoring are not implemented features or current challenge acceptance claims. Hosted demo, repository publication and recording remain optional.

## 5. Preservation and version rule

This consolidation changes documentation only. Runtime/prompt remain v0.9.7; raw outputs, references, scores, freeze, human templates and older archives are preserved. Historical docs are now separate from the current narrative. Any future behavioral change needs a new identified configuration/run and new evaluation; a prettier manual rewrite must not replace an original candidate silently. No AI score is a human signature, and no package integrity check is a language-quality pass.
