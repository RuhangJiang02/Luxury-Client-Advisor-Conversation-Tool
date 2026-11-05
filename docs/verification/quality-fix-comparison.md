# Targeted quality repair — November 4, 2026

Tool/prompt: **v0.4.6**. Provider: local Ollama, qwen3:4b; no paid API calls.

- 47 deterministic regression tests passed. These validate implementation behaviour, not overall language quality.
- Latest real batch: 11/11 generated, 33 candidates, each on its first attempt. Six are unchanged required-dataset smoke inputs; five are additional iteration cases. This is still only 6/50 required cases.
- Saved-run evaluation: all 11 pending human ratings; no acceptance score or pass rate claimed.
- Separate v0.4.4 guardrail evidence: 20/20 matched, zero model calls. No preflight logic changed in v0.4.5–v0.4.6; this is explicitly historical evidence.

## Before and after

See [exact per-case original and updated text](quality-fix-comparison.json) and [latest 11-case CSV](quality-fix-latest.csv). Baseline is tool-v0.3.3, latest tool-v0.4.6.

| Defect | Intervention and observation | Remaining limitation |
| --- | --- | --- |
| L-03 receipt assumptions | Client receipt evidence, conditional/negation handling, focused care context and output rejection. Latest S3-01 avoids asserting receipt; explicit received/not-received inputs also generated. | Heuristic chat parsing does not verify delivery or resolve all contradictory history. Care wording still needs review. |
| L-04 price rationale / alternatives | Reject observed unsupported causal explanations and blanket absence of alternatives; separate policy, a known material fact and time-to-consider angles. Latest S6-01 and QF-P01 omit the earlier causal claims. | Regex checks are incomplete; QF-P01 still vaguely offers a more suitable solution. Formal policy phrasing and unnecessary repeated prices remain. |
| L-05 diversity / invitation tone | Different candidate angles; strip shared logistics before lexical similarity scoring; require independent title, date, start and venue. v0.4.6 repaired both v0.4.5 rejected invitations. | Still open: invitations remain formal and candidates 1/3 can be semantically similar despite passing lexical checks. Recommendation wording also exposes catalogue-oriented reasoning; human review required. |

## Preserved unsuccessful iterations

Runs v0.4–v0.4.5 remain under runs/. v0.4.4 generated all 11 but review identified guessed channel-price reasons and writing labels. v0.4.5 generated 9 and rejected 2 invitations after bounded retries. A source-backed short event title initially triggered a false positive; the title-alias rule was corrected. v0.4.6 explicitly supplies required details per candidate and separates the start time from end time. Failed outputs were never substituted into the successful CSV.

These five new cases were used repeatedly during repair and are no longer an untouched holdout. Next: independent unseen-input review, tone/diversity adjudication, freeze configuration, then run all 50 and complete human scoring. Do not combine iterations into a claimed final 150-output dataset.
