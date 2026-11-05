> Historical working draft. Superseded by the current documents under `docs/`. Relative evidence links have been adjusted for this archive location; recorded versions and outcomes have not been rewritten.

# Defects and Next Steps — Versioned Local Review

## Current strict-target result

Tool/prompt-v0.9.7: 50/50 cases meet the stricter **AI-applied** case threshold, mean 4.31/5; genuine human review and release acceptance remain pending. [Detailed evidence and limitations](../../verification/ai-quality-review-v0.9.7/REPORT.md). The fixed 50-case dataset was actively used for tuning, so this is not holdout evidence.

All local requests now use program-authored evidence-bound reference copy edited by a real local LLM (98/150 raw bodies unchanged from reference). Greetings/products/events receive source frames; all local successes receive audited exact-address restoration, necessary policy/prior-offer context and narrow pronoun/typo normalization before grounding checks. Failed inference has no reference fallback. Every reference, raw provider output and transformation is retained. Source framing derives from fields, not case IDs. The same shared service powers UI and batch. Current freeze, full review and strict CLI replace the old deferred-work status.

Earlier sections below describe historical implementation/results and retain their recorded versions. Their thresholds and outcomes are not retroactively rewritten.


Status: **versioned assistant/source observations; human quality acceptance pending**. Current scope includes the complete v0.8.2 measurement and earlier selected smoke/repair populations. No human quality scores or overall quality pass rate are recorded. Existing-case repair/reruns/scoring are deferred by user direction.

**How to read this register:** sections 1–3 preserve the initial smoke-stage evidence and plan. Later numbered updates describe the superseding versions; section 8 states the current v0.8.2 result and unresolved findings. “Latest” in a historical table refers to that stage, not necessarily the current runtime. For current measured scope, see the [evaluation report](../../evaluation-report.md).

## 1. Versioned evidence

| Iteration | Tool / prompt | Model setup | Evidence |
| --- | --- | --- | --- |
| Initial local smoke | tool-v0.3 / prompt-v0.1 | Official Qwen3 4B GGUF imported; default generic template | `runs/local-smoke-v0.3/` |
| Explicit Chinese rules | tool-v0.3.1 / prompt-v0.2 | Same generic template; shorter Chinese system rules | `runs/local-smoke-v0.3.1/` |
| Chat template repair | tool-v0.3.2 / prompt-v0.2 | Added explicit Qwen ChatML role boundaries and no-thinking assistant prefix | `runs/local-smoke-v0.3.2/` |
| Scenario routing | tool-v0.3.3 / prompt-v0.3 | Corrected template; shared Chinese rules plus only the active scenario's instructions | `runs/local-smoke-v0.3.3/` |

The default imported template was confirmed as `TEMPLATE {{ .Prompt }}`. Repairing it alone did not eliminate scene confusion; further improvement appeared after explicit scenario routing. Do not claim the template was the sole cause of all poor outputs. Preserve the separate interventions and runs.

## 2. Historical observations and changes — through v0.3.3

| Defect | Evidence before change | Action / latest observation | Status |
| --- | --- | --- | --- |
| L-01: sales in birthday greetings | Initial S1-01 candidate 1: “如您有需要推荐的皮革制品，我随时为您服务。” This conflicts with BR-09 and the greeting purpose. | prompt-v0.3 makes greeting the sole task and excludes unrelated client/product facts from this prompt. Latest S1-01 contains three birthday wishes without the earlier product/service pitch. | Improved in this sample; needs full greeting-case evaluation. |
| L-02: implied stock/reservation | tool-v0.3.1 S2-01 candidate 1: “轻步斜挎包已为您准备好”. No inventory/reservation evidence was supplied. | Explicit task routing distinguishes catalogue facts from completed external actions. Latest S2-01 no longer says the product is ready/reserved. | Improved in this sample; not a global guarantee. |
| L-03: arrival and care assumptions | Baseline v0.3.3 S3-01 candidates say “已到手” or “已收到”, but the purchase record does not establish delivery/receipt. Earlier output also invented dust-bag instructions or “如新” guarantees. | Earlier unsupported instruction/guarantee wording is absent in the latest sample, but arrival assumptions remain. | Open: avoid delivery assertions unless separately verified. |
| L-04: unsupported alternative/price rationale | Baseline v0.3.3 S6-01 candidate 3: “也不存在其他尺寸或价格替代方案”. The input does not justify this broad negative claim. Other candidates infer why the brand set its price. | General discount policy is clearer, but factual grounding still needs improvement. | Open: state only the known price/policy; don't invent pricing rationale or assert absence of all alternatives. |
| L-05: weak diversity / formal invitations | Event invitation candidates repeat nearly the same logistics with small wording changes and formal closings. | They now invite to the correct event with supplied timing/venue, rather than merely asking unrelated questions. | Open: evaluate set-level diversity and naturalness with eval-v0.1. |
| L-06: missing chat template after GGUF import | `ollama show --modelfile` returned a generic `.Prompt` template, without explicit role boundaries. | Added a task-appropriate ChatML template and stop marker in `models/Modelfile`; imported the same verified weights again. | Configuration repaired; model semantic quality still requires evaluation. |

These observations identify likely rubric failures and review priorities. They do not replace complete human ratings. Automated `status=generated` means the response passed configured structural checks; it does not certify factual or brand compliance.

## 3. Historical next-step plan after the first smoke review

1. Review the six latest cases and adjudicate factual issues against the exact request snapshots and brand rules. Preserve edits separately from generated text.
2. Improve receipt-state grounding, pricing-rationale restraint, and candidate diversity; test targeted changes with new version/run IDs.
3. Freeze model digest, Modelfile, prompt, catalogue, and configuration for a complete 50-case run. Do not mix the four smoke versions into a 150-output final table.
4. Execute all 50 cases plus the extra guardrails, complete human scoring, and report defects and all unsuccessful runs honestly.
5. Consolidate the final methodology/evaluation/defect report and private submission package. Local hosting and file access are separate from external reviewer access.

The paid OpenAI credit issue remains historical. Local generation neither fixes the account balance nor needs it. No API purchase is necessary for the active route.

## 4. Targeted repair update — tool/prompt-v0.4.6

The earlier table preserves baseline observations. Current superseding evidence is [the repair comparison](../../verification/quality-fix-comparison.md), with exact before/after text, versioned failures and limits. 47 tests pass; 11/11 latest local cases generated 33 candidates (six required cases plus five extras). All await human ratings.

- **L-03:** targeted receipt checks implemented; improved in sampled inputs, not globally resolved.
- **L-04:** targeted price-rationale and blanket-alternative checks implemented; sampled causal claims removed. Vague alternative-support phrasing and formal replies remain review items.
- **L-05:** event logistics improved; **open** for formal tone and semantic duplication. Lexical diversity is not human diversity acceptance.

Next: review the 11-case CSV, improve justified residual issues, validate untouched inputs, freeze a version, then execute all 50 and complete human evaluation. The complete 50-case final run and final B/D/E consolidation remain pending.

## 5. Completed editorial review and mixed rerun — v0.5.2

[All 33 candidates reviewed](../../verification/naturalness-review.md), with original text, specific issue and separately labelled assistant-edited alternative for each. Review found unsupported personality/design-intent claims, formal voice, care context mismatch, comparison evasion and continued selling after requests for space. These are assistant findings, not completed human scoring.

Context-sensitive pricing prompts and soft naturalness flags were added; 53 tests pass. Latest local batch generates nine cases (27 messages), while both invitations fail independent logistics checks. This is a generation-completeness regression from v0.4.6. No final 50-case freeze is recommended. L-05 stays open; new residual issues include uneven 您/你/address use, copied phrasing, vague support offers and generic endings. Negative receipt assumptions and a consideration-language regex false positive were fixed during iteration. Preserve all v0.5.0–v0.5.2 outputs. See exact rerun comparison and remaining actions in the linked review.

## 6. Full frozen measurement — tool/prompt-v0.6.1

All 50 cases were executed. Initial result: 48 generated / 2 generation_failed (144 messages). One same-version recovery request for every failed case produced both remaining sets; the separately mapped recovery view has 150 messages across the original 50 cases. Original failures remain intact. See [evaluation report](../../evaluation-report.md), [freeze](../../verification/evaluation-freeze-v0.6.1.json) and [case/run mapping](../../verification/full-50-source-map-v0.6.1.json). This is generation completeness, not quality acceptance. All 50 human ratings remain pending.

- **L-05 event completeness:** repaired by explicit verified logistics composition; model bodies and source-derived frame are preserved. Naturalness/diversity still open.
- **L-07 birthday/festival mismatch:** open; birthday candidates can contain festival language.
- **L-08 unsupported material properties:** open; e.g. S2-02 adds wear resistance without catalogue support.
- **L-09 internal process wording:** open; client copy references ending a sales push.
- **L-10 assumed event interest:** open; generated bodies may infer interest despite accurate logistics.
- **L-11 invalid structured output:** initial S3-03 failed; recovered on the single extra request. This does not prove robustness.
- **L-12 attributed discount history:** open; S6-06 speaks as if an unverified customer claim is confirmed advisor history.
- **L-13 care-response context:** open; future receipt language can distract from a reported water issue.
- **L-14 semantic repetition:** open; some reconnection alternatives duplicate availability despite different words.

Next priorities: human/source adjudication of factual and policy findings, targeted repair of confirmed major issues, then a separately versioned full rerun if code/prompt changes. Do not relabel pending ratings as pass or alter the rubric. B methodology and D measurement report now exist; the local submission review package is a draft until quality review and final consistency/access checks are complete.

## 7. Source-defect repair sequence — v0.7.1 to v0.8.2

v0.7.1 completed a fresh 50/50 generated run, improving occasion binding and observed property/history checks. Full source review still found scratch-protection claims in S2-06/S2-07, so those checks were not called a complete solution. Recommendation generation was narrowed in v0.8: source-bound catalogue facts plus actual model preference questions, with deterministic first-eligible selection disclosed.

Intermediate evidence remains: v0.8.0 generated 21/23 target cases and rejected two for numeric question bodies; v0.8.1 generated all 23 but copied a writing instruction into nine recommendation cases. Retrospective v0.8.2 evaluation separately records 14 pending/9 instruction-leakage failures, not a changed historical generation status. v0.8.2 simplified the question prompt and added explicit leakage rejection; all 23 target cases generated with 76 tests passing and 20 current guardrails matching.

- **L-07 occasion mismatch:** source-bound frame implemented and verified on birthday/festival/unknown-date targets. Generic short wishes remain a style limitation.
- **L-08 invented material/protection:** recommendation statement fields now come from the catalogue; model only supplies questions. Other scenario claims and implied benefits still require review.
- **L-12 discount-history attribution:** targeted source-aware check/prompt added; customer assertion is not advisor evidence or policy authorization. The full output set still needs human source review.
- **L-15 instruction-copying in questions:** v0.8.1 evidence retained; parser/composer reject known writing-instruction leakage in v0.8.2.

This architecture trades free-form recommendation prose for grounded facts and more predictable, question-heavy drafts. It does not rank products with the LLM. Human acceptance and semantic diversity remain open; event interest, care issue fit and generic reconnection language remain priorities after these source defects.

## 8. Current full result — v0.8.2

A fresh fixed-50 run generated 50/50 cases and 150 drafts with 51 provider attempts (one bounded within-run repair), no additional recovery. 76 tests pass; current 20/20 guardrails match with zero calls. All 25 greeting/recommendation/invitation compositions reconstruct exactly from raw model bodies and known source facts. [Current evaluation](../../evaluation-report.md), [case table](../../verification/full-50-cases-v0.8.2.csv), [integrity](../../verification/full-50-integrity-v0.8.2.json) and [version comparison](../../verification/source-fix-full-comparison-v0.8.2.json) preserve evidence.

L-07 source framing and L-08 recommendation fact binding improve the selected defect classes; L-12 explicit advisor-history attribution is removed in the selected current example. These are not blanket semantic-quality guarantees. **L-13 remains open:** S3-06 uses “收到后/以后” despite a reported water issue. **L-16 remains open:** S6-06 says the material is the only one available, without supporting offer/availability evidence. Event bodies and reconnection copy also need relevance/naturalness/diversity review. All 50 human score records remain pending.

Next priorities are care issue fit and unsupported absolute claims in price responses, then semantic/style review and actual human assessment. The new review package is a draft; do not present 50/50 generation as the quality pass rate or claim all messages were wholly LLM-authored.
