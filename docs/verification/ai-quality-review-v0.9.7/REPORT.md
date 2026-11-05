# AI-assisted quality review — v0.9.7

**All 50 cases meet the stricter AI-applied case threshold. Genuine human acceptance remains pending.**

## Results and scope

- Original fixed dataset: **50 cases / 150 final candidates**, one frozen tool/prompt version, local Ollama qwen3:4b, temperature 0.
- **50/50 cases meet the AI threshold; mean 4.3097/5; minimum 4.1333/5.** Every candidate dimension and every case diversity score is at least 3; every weighted case score is at least 4.
- AI source review found **no hard-failure finding in this final set**. This is not a verified human zero-hard-failure claim.
- **50 actual provider attempts**, no within-run retry and no extra recovery or substituted historical candidates in this final batch. Prior iterations are separate and retained.
- **87 unit/regression tests pass, 20/20 guardrails match with zero model attempts, 44 isolated UI checks pass** using explicit test doubles. These counts are not additional model-quality cases.
- Human ratings are unfilled; **human acceptance and release acceptance remain false**.

| Scenario | AI threshold met | Current requirement |
| --- | ---: | ---: |
| greeting | 8/8 | 8 |
| product_recommendation | 9/9 | 9 |
| post_purchase_care | 8/8 | 8 |
| reactivation | 8/8 | 8 |
| event_invitation | 8/8 | 8 |
| price_objection | 9/9 | 9 |

## Assessment method

Codex assistant read each saved request and all three final candidates against the catalogue, contact/history context and eval-v0.1, then assigned six integer candidate scores and one diversity score per case. Scores are recorded with individual comments, run IDs, timestamps and immutable source hashes. No paid API judge was used and no human assessor was invented. The same assistant implemented and reviewed the repair: this is **self-review on an actively tuned development dataset**, not independent assessment, inter-rater reliability or a holdout test.

Weights remain personalization 15%, brand 15%, naturalness 15%, scenario fit 15%, grounding 20%, respect 10%, plus case diversity 10%. Candidate dimensions and diversity must each be >=3; weighted case score must be >=4; any verified hard failure rejects the entire case. The user's November 5 requirement raises overall case coverage from the historical 45/50 minimum to **50/50**. No candidate score or weight was relaxed to force the result. Short messages, long necessary event logistics and sparse inputs remain soft/contextual issues.

## Authorship and limitations

All local requests use **program-authored, evidence-bound reference drafts**, edited by a real local LLM. Greeting/recommendation/event outputs also receive source frames. Every successful local result receives an audited client-copy step: exact known address; any missing mandatory discount refusal or reported prior-offer context; polite-pronoun and observed-typo normalization. This step does not run on provider failure and does not supply replacement messages for failed inference.

Of the 150 raw provider message bodies, **98 exactly match the reference body supplied to the model**; the other 52 differ. This is controlled drafting/editing, not evidence that the small model can freely invent 150 equally good messages. The audit recorded **75 final candidate transformations** in client-copy composition, primarily exact address restoration. All source references, raw provider text, model edits, trusted frames and final transformations are retained. Product choice remains the first preflight-eligible item, not model ranking.

The outputs still have minor style limitations: segmented recommendation openings (S2-01–07), a dense policy explanation (S3-06), formal price-challenge wording (S6-07), and closely related time/closure alternatives (S6-08). These receive 3s where appropriate rather than perfect scores. Cross-case copy is often similar, especially greetings and general care. The case diversity rubric does not test cross-client stylistic breadth. Results support this frozen set only; arbitrary future inputs can fail and still require advisor review.

## Repair evidence

| Version | Observed outcome | Disposition |
| --- | --- | --- |
| v0.8.2 | 16/50 AI thresholds; raw mean 3.6767 | Original assessment preserved. |
| v0.9.0 / v0.9.1 targets | Instruction copying, generic advice and a bounded question rejection | Targeted tuning, not final measurement. |
| v0.9.2 | 50 generated, but current discount request misread as historical offer | Rejected; source triage and snapshot retained. |
| v0.9.3 | 50 generated, accidental English in care | Rejected; original text retained. |
| v0.9.4 | 49/50 AI thresholds; raw mean 4.3047 | Preserved failed strict-target assessment; no score inflation. |
| v0.9.5 | Leaked message headings and informal pronouns | Rejected; partial scores explicitly labelled. |
| v0.9.6 | Two generation failures after bounded rejection; missing known addresses | Rejected; failed outputs remain empty. |
| v0.9.7 | Fresh 50/50 AI thresholds, 150 outputs | Current tool-output result; human gate still pending. |

The architecture and configuration changed during repair, so the before/after difference measures the whole tool and review process, not a causal improvement in the unchanged Qwen model. Failed target/full runs remain available; only the final single-version run is used for the 50/50 result.

## Reviewable artifacts

- [50-case exact eight-column output CSV](full-50-cases.csv)
- [150 candidate texts, dimension scores and comments](candidate-scores.csv)
- [50 case totals and threshold conditions](case-scores.csv)
- [Full AI score records](ratings.json), [summary](summary.json), [below-threshold adjudication queue](human-adjudication-queue.json)
- [Freeze](../evaluation-freeze-v0.9.7.json), [raw-to-export integrity audit](../full-50-integrity-v0.9.7.json), [human evaluation status](../full-50-evaluation-v0.9.7.json)
- [UI verification](../ui-demo-verification-v0.9.7.json), [guardrails](../guardrails-v0.9.7.json)

An empty below-threshold queue does **not** exempt any case from human assessment: all 50 remain in the actual human-rating template under `runs/full-50-v0.9.7/human-ratings-template.json`.

## Reproduction

From the project root, with the existing Python dependencies installed:

```sh
python scripts/summarize_ai_review.py --review-dir docs/verification/ai-quality-review-v0.9.7
python scripts/verify_quality_run.py --version v0.9.7
python scripts/evaluate_cases.py --batch runs/full-50-v0.9.7 --strict-all
```

The first command aggregates existing **AI-authored** scores; the second verifies frozen sources, actual run evidence, composition, CSV linkage and review hashes. The third keeps human results pending unless genuine human ratings are supplied with `--ratings`. None of these commands calls a model. A new generation run must use a new directory/request identity and should not overwrite the frozen final artifacts.
