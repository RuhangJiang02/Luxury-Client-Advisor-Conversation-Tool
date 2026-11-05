# Luxury Client Advisor Conversation Tool

Planning and delivery guide for Artefact's **Applied AI Engineer: Written Challenge**.

**Current measured version: tool-v0.9.7 / prompt-v0.9.7. All 50 cases meet the stricter AI-applied quality threshold**, with **150 candidates, mean 4.31/5**, and no hard-failure finding in the final AI source review. The final run used 50 actual local-model calls, no retry or extra recovery. **Genuine human acceptance and release acceptance remain pending.**

[Current 50-case CSV](docs/verification/ai-quality-review-v0.9.7/full-50-cases.csv) · [Detailed review](docs/verification/ai-quality-review-v0.9.7/REPORT.md) · [150 scored candidates](docs/verification/ai-quality-review-v0.9.7/candidate-scores.csv) · [Integrity audit](docs/verification/full-50-integrity-v0.9.7.json) · [Freeze](docs/verification/evaluation-freeze-v0.9.7.json) · [Reviewer entry](START_HERE.md)

**Authorship:** source-bound program references are edited by local Qwen3 4B. Of 150 raw model bodies, 98 match their reference exactly. Greetings, recommendations and invitations also use trusted frames; all successful local outputs have audited address/policy framing and narrow normalization. Raw references, actual provider content and every transformation are preserved. This is a controlled drafting/editing tool; outputs are not claimed to be wholly model-authored. Product selection is the first preflight-eligible item, not LLM ranking. Failed inference returns failure with no template fallback.

**Run the app:** `.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true`, then open [http://127.0.0.1:8501](http://127.0.0.1:8501). Restart an existing process to load repaired modules. Use local Ollama qwen3:4b with `LLM_TEMPERATURE=0`, as measured. See [runbook](docs/running-and-evaluation.md) and [six-scenario walkthrough](docs/ui-demo-walkthrough.md). No paid API is needed. Private `.env` and the original brief are excluded from packages.

## Progress review — November 5, 2026

| Priority | Current state | Remaining gate |
| --- | --- | --- |
| P0 | Existing work and conversation evidence retained | Preserve the recorded evidence |
| P1 | Brand, contracts, acceptance, architecture and test design defined | Current delivery target is 50/50, superseding the historical 45/50 minimum |
| P2 | Shared Streamlit/Python service repaired; 87 regression tests pass | Arbitrary new inputs still require advisor review |
| P3 | Fresh v0.9.7 full run: 50 cases, 150 outputs, 50 actual attempts | Preserve frozen evidence; new code/config needs new measurement |
| P4 | All 150 candidates scored by AI; all 50 case thresholds met; 20/20 zero-call guardrails; 44 isolated UI checks | Genuine human scores/adjudication for all 50 |
| P5 | A–E documents, CSVs, source provenance and historical ZIPs retained | Human signoff and actual transmission remain separate gates; the current private review package is synchronized |
| P6 | Six-scenario demo/runbook and local architecture | Hosting/recording optional |

## Core deliverables

| Item | Current artifact |
| --- | --- |
| A — Work Log | [WORK_LOG.md](WORK_LOG.md) and [conversation records](docs/conversations/2026-11-05-session-02.md) |
| B — Methodology | [Methodology](docs/methodology.md) and [current architecture](docs/architecture.md) |
| C — 50 cases | [Exact eight-column final output table](docs/verification/ai-quality-review-v0.9.7/full-50-cases.csv) |
| D — Evaluation | [Final evaluation narrative](docs/evaluation-report.md), [detailed AI scores](docs/verification/ai-quality-review-v0.9.7/REPORT.md) and [pending human status](docs/verification/full-50-evaluation-v0.9.7.json) |
| E — Defects / next steps | [Versioned findings](docs/defects-and-next-steps.md); intermediate failures and source snapshots preserved |

The earlier v0.8.2 review (16/50) and v0.9.4 review (49/50) remain unchanged. The final 50/50 is a self-review on an actively tuned development set, not independent human or holdout validation. Minor style scores of 3 remain visible. Older `submission/` ZIPs predate this repair and are historical review drafts; the new private review package is `CHENGXU-review-draft-v0.9.7-final-docs-20261105.zip`. No archive has been overwritten or sent. Screenshots remain user-managed and outside assistant scope.

## 1. Objective

Build a tool that helps Client Advisors (CAs) at a fictional luxury house draft personal, brand-consistent WeChat messages. For each request, the tool must produce **exactly three candidate messages in Chinese** for the CA to choose from.

The submission should demonstrate how the tool was designed, built, tested, evaluated, and improved. This is an implementation and evidence task, rather than a proposal-only exercise.

Source of truth: the privately supplied Written Challenge Brief (private brief excluded from package), pages 1–2. Requirements labelled **Required**, **Optional**, or **Bonus** below reflect the brief. Implementation choices and suggested acceptance criteria are labelled as recommendations and may be revised.

## 2. Required product behavior

### Inputs and outputs

| Item | Requirement |
| --- | --- |
| Client information | Accept fictional client information relevant to the message. The brief does not prescribe a schema. |
| Scenario | Support all six scenarios listed below. |
| Conversation history | Use the supplied history to maintain context. |
| Product information | Use product information when the scenario calls for it. |
| Output | Return three Chinese candidate messages written for WeChat. |
| Brand assumptions | Invent a luxury house in any category; explain its voice, clients, products, and advisor communication rules. No brand guidelines or data are supplied. |
| Further demonstration | Be prepared to run the tool on a new input during a later discussion with Artefact. |

### Six mandatory scenarios

| ID | Scenario | Expected purpose |
| --- | --- | --- |
| S1 | Birthday and festive greetings | Greet a client on a birthday or festival. |
| S2 | Product recommendation | Suggest a product using what is known about the client. |
| S3 | Post-purchase care | Follow up after a purchase. |
| S4 | Reactivation | Reconnect with someone who has not visited or purchased for a long time. |
| S5 | Event invitation | Invite a client to a boutique event or private preview. |
| S6 | Price objection | Reply when a client considers a price too high, compares prices elsewhere, or asks for a discount. |

The desired communication should feel personal, recognizably on-brand, and appropriate to the moment. It should avoid sounding scripted, pushy, or intrusive.

## 3. Task priorities and execution order

The priorities below retain the original execution plan, not an additional scoring rubric from Artefact. Current measured status is shown at the top of this README. **P0 continues throughout the project. P1–P5 establish the core submission; P6 adds supporting material.**

| Priority | Task | Concrete output | Completion gate / dependency |
| --- | --- | --- | --- |
| **P0 — Start immediately; maintain continuously** | Capture the work process and AI assistance. | Work Log, conversation transcripts, screenshots, and evidence references. | Every substantive step records its action, input, output, tools/agents, and available screenshots. Record missing evidence honestly. |
| **P1 — Define the problem and acceptance criteria** | Choose the fictional brand; define assumptions, communication rules, input/output structure, and evaluation criteria. | Brand and rules document; proposed schemas; definitions of “good” and “not acceptable”; test coverage plan. | All six scenarios have clear intended behavior. Separate brief requirements from project decisions. |
| **P2 — Build the core tool** | Implement generation for all scenarios and make it runnable on unseen input. | Working generation flow, prompts/configuration, basic execution instructions, version identification. | A new input can produce three Chinese candidates. Preserve the configuration used for each recorded run. Depends on P1. |
| **P3 — Produce the required test evidence** | Create 50 fictional cases, execute the tool, and save actual outputs. | Required case table with 50 inputs and 150 generated candidate messages. | All six scenarios are covered. Each row has the specified fields and traceable run/version information. Test design begins in P1; execution depends on P2. |
| **P4 — Evaluate and iterate** | Assess outputs, capture evidence, identify defects, and make justified improvements. | Evaluation report, screenshots, defect register, and before/after comparisons where changes are made. | Results are linked to cases and versions. Re-run affected cases after changes and clearly label the scope of any re-evaluation. Depends on an initial P3 run. |
| **P5 — Assemble and verify delivery** | Complete the methodology and required A–E materials; review consistency and access. | Final report, Work Log, case workbook, evaluation, defects/next steps, and submission index. | Every required element is present, readable, and supported by evidence. Links must work without an account if used for submission. |
| **P6 — Add supporting material** | Draw architecture and optionally provide a demo, source package, or recording. | Architecture diagram; optional runnable demo/repository/recording. | Core A–E materials are complete first. The architecture diagram is the brief's bonus question; other supporting material is optional. |

### Recommended time allocation

- **November 4, 2026:** establish logging, requirements, brand assumptions, and evaluation design.
- **November 5–6:** implement the core tool; design the full test set; validate all six scenario paths.
- **November 7:** execute the 50 cases and conduct the initial evaluation.
- **November 8:** fix priority defects, run justified re-evaluations, and assemble reports and screenshots.
- **November 9:** check the package and access permissions, then submit before the deadline.

This schedule is a planning recommendation using Asia/Shanghai dates, not a schedule specified by the company. Adjust it to actual progress while preserving the mandatory deliverables.

## 4. Core deliverables

**The central result is a functioning tool supported by a complete, traceable A–E evidence package.** A hosted demo and a repository are optional submission formats; the brief still asks for a tool and may require a later run on new input.

| Deliverable | Status in brief | Required content | Recommended artifact |
| --- | --- | --- | --- |
| **A. Work log** | Required | Walk through the process from receiving the brief to the final result. Use one row per step with: Step, What you did, Input, Output, Tool or agent used, Screenshots. Include screenshots of AI chats when used at each step. | `WORK_LOG.md` with linked transcripts and screenshots; optionally export to PDF or XLSX. |
| **B. Methodology** | Required | Explain tool design, test-set design, evaluation method, and what “good” and “not acceptable” mean. | Methodology section in a final report, or a separate document. |
| **C. 50 test cases** | Required | For every case, supply client information, scenario, conversation history, product information if applicable, and three outputs generated by the tool. | XLSX/CSV containing the exact requested columns. |
| **D. Evaluation report** | Required | Evaluate the generated outputs and include screenshots. | Report with case references, results, examples, and screenshot links. |
| **E. Defects and next steps** | Required | Describe defects found, changes made in response, before/after evidence if changes were made, and remaining work. If the tool changes after testing, mark which version each result comes from. | Defect register and report section with versioned comparisons. |
| **Architecture diagram** | Bonus | Draw the tool architecture; any format is acceptable. | Mermaid, exported diagram, or a photographed sketch. |
| **Demo, repository, recording, other material** | Optional | Additional material that helps the reviewer understand the work. | Demo link, source archive, or short recording. |

### Evidence and submission checklist

These checks distinguish completed evidence from quality acceptance. The original requirements remain listed above; user-managed capture is described in section 6. The current package contains the consolidated v0.9.7 narrative; earlier ZIP snapshots remain unchanged.

- [x] Fictional brand, six-product catalogue, client inputs/history and business rules documented.
- [x] Shared UI/backend supports all six scenarios and explicit generation/non-success paths; real-run evidence and separate isolated UI verification exist.
- [x] The current v0.9.7 full generation population contains three Chinese drafts per case: 50 cases / 150 outputs. Historical failed requests remain preserved with zero candidates.
- [x] “Good” and “not acceptable” were defined in eval-v0.1 before recorded output evaluation.
- [x] Evaluation population, versions, criteria and assessment provenance are explicit; missing human ratings remain pending.
- [x] The measurement report contains specific source-linked findings and version comparisons; assistant observations are distinguished from human scores.
- [x] Defects, changes and remaining limitations are reported, with reproducible source/run mappings.
- [x] Existing Work Log and visible conversation evidence are preserved.
- [x] Current source/evidence integrity and isolated UI checks are recorded; the documentation package is validated separately and no upload/publication/email is claimed.
- [ ] Complete genuine human assessment if pursuing the additional internal acceptance gate; the brief does not specifically require human signoff.
- [ ] Review remaining naturalness and cross-client repetition; any changed implementation needs a separately identified measurement.
- [ ] Finalize acceptance conclusions and the actual delivery/access check. A localhost URL is not an external reviewer link.

## 5. Test-set and evaluation plan

### Required case table

Preserve these columns from the brief:

| Case ID | Scenario | Client information | Conversation history | Product information | Output 1 | Output 2 | Output 3 |
| --- | --- | --- | --- | --- | --- | --- | --- |

Use an explicit value such as `Not applicable` when product information is unnecessary. Store traceability fields such as tool version, prompt version, run identifier, and generation time in extra columns or a linked metadata sheet. These extra fields are project recommendations, not prescribed columns.

### Recommended coverage

| Scenario | Planned number of cases |
| --- | ---: |
| Birthday and festive greetings | 8 |
| Product recommendation | 9 |
| Post-purchase care | 8 |
| Reactivation | 8 |
| Event invitation | 8 |
| Price objection | 9 |
| **Total** | **50** |

The brief does not prescribe this distribution. Cover both ordinary and difficult situations, including missing information, sparse history, explicit rejection, complaints, mismatched preferences, unsupported product claims, and discount requests that conflict with fictional brand policy. Record the expected handling of each difficult case.

### Recommended evaluation dimensions

| Dimension | What to assess |
| --- | --- |
| Personalization | Uses relevant supplied information without inventing personal details. |
| Brand consistency | Matches the documented tone and advisor rules. |
| Chinese and WeChat suitability | Natural, clear, appropriately concise language suitable for the conversation. |
| Scenario fit | Responds to the actual purpose and conversation context. |
| Candidate diversity | Offers meaningfully different choices while keeping facts and policy consistent. |
| Factual grounding | Product, price, event, and policy statements are supported by the input or documented rules. |
| Respect for the client | Avoids pressure, intrusive references, and disregard for explicit preferences. |

Hard-failure definitions, the scoring scale and aggregation rules were established in P1 in [eval-v0.1](docs/acceptance-criteria.md). They cover unsupported facts/policies, contact violations, offensive wording, leakage and invalid candidate structure. Defined criteria are not measured quality results; all current human ratings remain pending.

Keep original generated outputs intact. Store any human-edited copy separately and label it. After a tool change, preserve earlier outputs and identify which cases were re-run; do not combine results from different versions without disclosure.

## 6. Existing process and conversation evidence

The retained [Work Log](WORK_LOG.md) and [conversation evidence](docs/conversations/2026-11-04-session-01.md) describe the recorded development process, failures and AI assistance. The current B/D/E documents summarize the measured design and results; historical working narratives are kept in [the documentation archive](docs/history/pre-final-consolidation-v0.9.7/README.md). Existing process records are preserved rather than rewritten as new evidence.

The brief requests screenshots for A and D. They are not currently included; transcripts and structured run artifacts are supplemental and do not replace screenshots. Screenshot handling remains user-managed and outside the assistant's scope.

## 7. Suggested final package

Current source and existing draft-delivery layout (final acceptance remains pending):

```text
README.md / WORK_LOG.md / AGENTS.md
app.py / preview_service.py                 # implemented UI + offline mode
requirements.txt / .env.example             # direct dependency pins + blank config
client_advisor/                            # shared backend + local/optional-cloud adapters + scoring
scripts/                                   # case authoring / batch / evaluate / export
data/
  catalogue.json / request.schema.json      # shared catalogue + strict schema
  generation-cases.json                    # 50 authored inputs; no outputs
  guardrail-cases.json                     # 20 additional cases
docs/
  conversations/                           # ongoing conversation records
  brand-and-rules.md / input-output-spec.md
  acceptance-criteria.md / architecture.md / test-design.md
  running-and-evaluation.md
  verification/                            # deterministic check evidence
  methodology.md                           # consolidated methodology narrative
  evaluation-report.md                     # measured results; human quality review pending
  defects-and-next-steps.md                 # versioned defects and unresolved findings
tests/                                     # deterministic backend/UI regression tests
runs/                                      # ignored local DB, batches, ratings, CSVs
submission/                                # checked draft ZIPs/index; final acceptance pending
```

The source PDF must remain private. If a public repository is used for optional supporting code, exclude the brief and review the repository contents before publishing. A private email attachment or account-free submission link can carry the required materials without publishing the brief.

## 8. Submission details

| Item | Detail from the brief |
| --- | --- |
| Recipient | `campus-recruit-china@artefact.com` |
| Deadline | By the end of **November 9, 2026**. The brief does not specify a timezone; plan to submit early using Asia/Shanghai local time. |
| Link access | Any submitted link must be accessible without an account. |
| Fictional content | Everything created for the challenge should be fictional; do not include real personal data about real people. |
| Confidentiality | Keep the challenge brief private and do not publish it. |
| Follow-up | Artefact may ask for a live run using a new input. |
| Expected response | The brief says every submission will be read and everyone will receive a reply by November 16, 2026. |

## 9. Current decisions and open choices

**Established:** the six mandatory scenarios, three Chinese outputs per request, required A–E materials, 50-case evidence requirement, and continuous process logging.

**Brand baseline established:** 澄序 CHENGXU, a fictional luxury leather-goods house, with six catalogue products and versioned advisor rules.

**Input/output baseline established:** io-v0.1 defines shared client/history/product context, all six scenario-specific contracts, three-candidate success output, and separate non-success states. The 50 generation cases are supplemented by separate guardrail tests. Strict request schema/reference checks and selected policy checks are implemented. Semantic interpretation remains partial and needs model/human evaluation.

**Technical direction established:** [Streamlit Web UI with shared Python services](docs/technical-direction.md), an LLM API adapter, and independent Python batch-generation/evaluation scripts. UI live mode and batch execution now call the same generation service. The offline template mode remains separate. Local model generation, six-scenario integration, evaluation-script execution, and export are verified. The current frozen v0.9.7 run contains 50 cases / 150 outputs with no additional recovery; AI self-review and pending human status are reported separately. Historical recovery views remain retained evidence. Optional OpenAI credit is outside the active local path.

**Selected:** local Ollama provider with qwen3:4b; optional OpenAI adapter retained; pinned direct dependencies; eval-v0.1; SQLite evidence store. Architecture has been extended for local inference; see the local-model guide.

**Current handoff:** v0.9.7 has 50/50 cases meeting the AI-applied threshold, with raw evidence, full scoring and strict-target verification. Genuine human assessment and actual delivery remain pending. The current consolidated documentation archive is `CHENGXU-review-draft-v0.9.7-final-docs-20261105.zip`; earlier ZIPs are historical and unchanged. No material has been transmitted. OpenAI credit is not needed for the local path.
