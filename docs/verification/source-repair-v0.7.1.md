# Source-defect repair — v0.7.1

**Scope:** 17 unchanged-input iteration cases: six scenario smoke inputs, five extra repair cases, and six fixed cases selected for birthday/material/history defects. All 17 generated 51 candidate messages; all remain pending human ratings. These are not untouched holdout inputs.

[Exact same-input comparison](source-repair-comparison-v0.7.1.json) · [Current targeted CSV](source-repair-cases-v0.7.1.csv) · [Current regression record](source-repair-regression-results.txt) (the historical 70-pass result is recorded in Work Log step 060)

## Changes and observations

| Defect | Change | Observed current sample | Limits |
| --- | --- | --- | --- |
| L-07 birthday/festival mismatch | Program binds actual occasion and known address; model writes three wish bodies. Body and final message are both retained. | Every selected birthday candidate has the birthday frame; S1-03 uses the exact fictional festival. Unknown/future dates do not add today/tomorrow. | This is disclosed hybrid composition, not entirely model-authored framing. Some wishes remain generic and very short. |
| L-08 unsupported performance | Shorter recommendation prompt; observed material-property checks; catalogue carrying methods added. | Selected recommendations omit the previous wear-resistance/sunlight-sheen assertions. | Checks only cover observed claim classes; usefulness, sizing and fit implications still need human review. |
| L-12 attributed discount history | Treat customer assertion as unverified; only advisor-role evidence can support recalling an advisor statement. | S6-06 says the customer mentioned a discount, then states current no-discount policy, without claiming the advisor promised it. | Customer wording is not policy authority; genuine advisor history also cannot authorize a prohibited discount. |
| Carry-method regression | The initial v0.7.0 S2-01 invented backpack carrying. v0.7.1 checks it against the selected catalogue. | Current target output no longer claims backpack carrying. | It is a narrow observed-class check, not complete semantic understanding of carrying. |
| Event cross-candidate reference | v0.7.0 S5-01 was rejected for using “上述”. Event-body repair now starts fresh with grounded facts, preserving prior raw attempt only in evidence. | v0.7.1 target invitations generated with complete composed logistics. | Event interest assumptions and weak attendance wording remain; one successful batch does not establish reliability. |

## Preserved unsuccessful evidence

v0.7.0 generated 16/17 cases and rejected S5-01. It also generated the unsupported backpack claim before that check existed. The raw output/attempt files are retained. An initial over-literal birthday phrase check caused six existing unit-test failures; the checker was corrected to accept explicit birthday blessings without requiring one exact sentence. That correction did not remove detection of festival wording in a birthday case.

## Reproducibility

`scripts/reconcile_recovery.py` now enforces recovery for exactly the initially non-generated cases, unchanged input facts and runtime identity, byte-preserving copies, all selected recovery outcomes retained and no generated-case style reruns. Four regression tests cover these provenance boundaries. Evaluator reports now identify the evaluation implementation and source hashes, so retrospective checks do not masquerade as historical original scores.

Full v0.7.1 measurement is a new independent run of the fixed 50 inputs, under the [new freeze](evaluation-freeze-v0.7.1.json). It must be assessed separately from v0.6.1. The existing v0.6.1 draft archive remains unchanged. No human scores or release pass rate are claimed.
