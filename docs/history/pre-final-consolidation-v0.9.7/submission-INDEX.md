> Historical working draft; superseded by current project documents. Relative evidence links adjusted for this location.

# Current review revision — v0.9.7

[Current reviewer entry](../../../START_HERE.md) · [50/50 AI quality report](../../verification/ai-quality-review-v0.9.7/REPORT.md). Current package name: `CHENGXU-review-draft-v0.9.7-20261105.zip`; private review draft, not human accepted or sent. Earlier package details below are historical and their ZIPs remain unchanged.

# Submission Review Package — v0.8.2 Draft

**Status: 50-case measurement complete; further case work is deferred at the user's direction, with human scoring and known quality issues still pending. This is not an accepted final release.**

**Delivery-document revision — November 5, 2026:** the latest prepared local attachment is `CHENGXU-review-draft-v0.8.2-delivery-20261105.zip`, with an external SHA-256 sidecar and a root [START_HERE](../../../START_HERE.md). It incorporates the prior documentation/UI work plus a [delivery plan](../../delivery-plan.md) and [local email draft](../../submission-email-draft.md). Earlier ZIPs are preserved. Runtime generation version remains v0.8.2; no measured case is rerun or scored by this revision.

**Route and limits:** a private attachment workflow is prepared, not transmitted. No hosted share link or account-free external URL test is claimed. Identity placeholders remain in the email draft. Local artifact/access checks and human quality acceptance are separate.

Start with the [six-scenario walkthrough](../../ui-demo-walkthrough.md) and [setup/run guide](../../running-and-evaluation.md). The 44 AppTest checks use labelled test doubles, block provider POST calls and use temporary storage; they are not 44 new language-quality cases. Real local health/model-list checks are separate from inference. Native browser download, visual review and actual model quality were not tested in this revision.

| Required item | File | State |
| --- | --- | --- |
| A — Work Log | WORK_LOG.md and docs/conversations/ | Active project record, including failed iterations |
| B — Methodology | docs/methodology.md | Consolidated design/testing/grounding narrative |
| C — 50 cases | evidence/full-50/test-cases.csv and provenance/source map | Fresh 50 cases / 150 drafts, no extra recovery or mixed-version substitution |
| D — Evaluation | docs/evaluation-report.md; evidence/full-50/evaluation.json | Full metrics/comparison; all 50 human ratings pending |
| E — Defects | docs/defects-and-next-steps.md and source comparison | Open care/price/context/style findings retained |
| Supporting source | client_advisor/, scripts/, app.py, requirements.txt | Shared local UI/backend and reproducible evaluation/reconciliation |

**Composition is disclosed:** 25 greeting/recommendation/event cases use actual model bodies plus known source frames, while 25 cases retain model-authored full messages. Product recommendation uses the first preflight-eligible item, not LLM ranking. No failed model call is substituted with a template. Source frames and bodies are saved per attempt.

Current run: 50/50 generated, 150 drafts, 51 bounded provider attempts and no extra recovery. 76 tests pass; 20/20 guardrails match with zero inference. Historical v0.6.1 initial failures/recovery and the v0.7.1 run remain separate; intermediate copying/failure artifacts are included as selected iteration evidence. Original artifact paths are mapped into the package by evidence/ORIGINAL_PATHS.json.

After installing requirements, evaluate the saved current set from the package root with `python scripts/evaluate_cases.py --batch evidence/full-50`. Copy the blank human-ratings template to a separate file, fill only actual assessor ratings and pass `--ratings <completed-file.json>`. The 150-row review worksheet is a note-taking aid; the evaluator consumes JSON. All present score fields are empty/pending.

The package excludes private challenge PDF, .env/credentials, model weights, SQLite, virtual environment and server logs. Local model setup is documented; weights are not bundled. All clients/products are fictional. Nothing has been uploaded, published or emailed. Local UI access is not external hosting; final account-free delivery links must be checked separately if used.
