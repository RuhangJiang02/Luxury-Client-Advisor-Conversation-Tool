> Historical working draft; superseded by current project documents. Relative evidence links adjusted for this location.

# Local Setup, Demonstration and Saved Evidence

Runbook revision: **November 5, 2026 (Asia/Shanghai)**. Current runtime **tool-v0.8.2 / prompt-v0.8.2**; architecture arch-v0.3. Start with the [six-scenario walkthrough](../../ui-demo-walkthrough.md) after setup.

The active provider is **local Ollama / qwen3:4b**. No API key or paid credit purchase is required for this route. The user has deferred further repair/reruns/scoring of the existing 50 cases. The default steps below do not run them or invoke inference automatically.

## 1. Choose the Python environment

Run commands from the project/package root, where `app.py`, `requirements.txt`, `client_advisor/` and `docs/` are siblings.

**Existing workspace:** dependencies are already installed in `.venv`.

```bash
CHENGXU_PY=.venv/bin/python
"$CHENGXU_PY" -m streamlit --version
```

**Fresh unpacked package:** use an installed Python 3.11+ interpreter to create a separate environment. Substitute its actual executable path if `python3.11` is not on PATH.

```bash
python3.11 -m venv .venv-demo
CHENGXU_PY=.venv-demo/bin/python
"$CHENGXU_PY" -m pip install -r requirements.txt
```

Do not overwrite an existing environment. The recorded workspace uses Python 3.9 and emits an urllib3/LibreSSL warning; local HTTP and isolated checks have worked in that environment. This is not evidence of remote HTTPS compatibility. Requirements pin direct dependencies, not a fully locked transitive environment.

## 2. Configure local mode without exposing credentials

For a fresh package, copy the example only if `.env` does not already exist:

```bash
cp -n .env.example .env
```

Existing workspace configuration should be preserved. Local settings are:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://127.0.0.1:11434
LLM_TIMEOUT=180
LLM_MAX_ATTEMPTS=2
LLM_TEMPERATURE=0.7
```

Environment variables override `.env`. Inspect only the allowlisted public configuration:

```bash
"$CHENGXU_PY" -c 'from client_advisor.config import Config; print(Config.load().public())'
```

Confirm `provider` is `ollama`. Do not print `.env` or credential values. The local adapter clears the runtime remote key and sends no Authorization header or environment proxy. The retained optional remote adapter is outside this default walkthrough and needs separate explicit configuration/verification.

## 3. Start Ollama and confirm the model

Ollama must already be installed. First check whether a local service is running:

```bash
curl --fail --silent --max-time 5 http://127.0.0.1:11434/api/tags
```

If unavailable, start it in a separate terminal and leave that terminal running:

```bash
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 ollama serve
```

Check the model list again. It must contain the configured `qwen3:4b` tag. This GET request reads metadata and does not generate text. If the service is already running, reuse it rather than start another process on the same port.

### Fresh model installation only

Weights are deliberately excluded from the package. The recorded baseline used the official Qwen GGUF at revision `bc640142c66e1fdd12af0bd68f40445458f3869b`, imported with the supplied `models/Modelfile`. If the working installed model already exists, skip this section.

```bash
mkdir -p .models
curl --fail --location --output .models/Qwen3-4B-Q4_K_M.gguf 'https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/bc640142c66e1fdd12af0bd68f40445458f3869b/Qwen3-4B-Q4_K_M.gguf?download=true'
shasum -a 256 .models/Qwen3-4B-Q4_K_M.gguf
```

Recorded size: **2,497,280,256 bytes**. Expected SHA-256:

```text
7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5
```

Only after matching the source/checksum, import the model from the project root:

```bash
ollama create qwen3:4b -f models/Modelfile
```

This is a roughly 2.5 GB initial download, not a step required for every demo. A fresh setup/model or different installed runtime must be recorded separately rather than assumed identical to the historical measurement. See [local-model notes](../../local-model.md) and [recorded model/source identity](../../verification/evaluation-freeze-v0.8.2.json).

## 4. Start Streamlit

In the project terminal with `CHENGXU_PY` set:

```bash
"$CHENGXU_PY" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501) on the same computer. Leave the terminal running. In another terminal, this health check should return `ok`:

```bash
curl --fail --silent --max-time 5 http://127.0.0.1:8501/_stcore/health
```

Default mode is the labelled template preview. Switching to “本地模型真实生成” prepares the live path but does not call the model; only an explicit live form submission does. Candidate selection, result inspection and download controls do not regenerate. If restarting an owned foreground process, use Ctrl+C in its terminal; do not terminate unrelated processes or delete run storage.

The address binds to loopback. It is not a public reviewer link, hosted deployment or claim of account-free external access. A remote reviewer can instead run the unpacked source locally with the documented prerequisites.

## 5. Rehearse without real model calls

Follow [the walkthrough](../../ui-demo-walkthrough.md), using the separate [demo request manifest](../../../examples/ui-demo/manifest.json). Template mode shows layout/interaction but does not exercise all live validation. For reproducible UI/service checks without inference:

```bash
"$CHENGXU_PY" scripts/verify_ui_demo.py --output /tmp/chengxu-ui-demo-verification.json
```

The script runs Streamlit `AppTest`, uses clearly labelled test-double responses and a temporary SQLite database, and blocks real provider POST calls. It verifies six preview paths, six explicit live success paths, selection/no-auto-generation and non-success routes. It neither touches the preserved 50-case outputs nor adds human scores. Reported fake calls are not actual local/cloud inference.

The recorded [workspace verification](../../verification/ui-demo-verification-2026-11-05.json) has 44 passing checks; the [portable check](../../verification/ui-demo-portable-check-2026-11-05.json) repeats those UI checks from copied package source. [Service readiness](../../verification/ui-demo-environment-2026-11-05.json) is based on actual local GET health/model-list responses, not model inference.

The script checks that a JSON download control exists; it does not perform a browser-native download or visual inspection. Actual local model output quality is not part of this wiring check. The recorded 76-test implementation suite is historical evidence; this demo script's assertion count is reported separately, not added to it.

## 6. Preserve and inspect evidence

Real UI submissions use `runs/runs.sqlite3`. Batch generation also writes JSON artifacts under its batch directory. Both use the same backend and preserve attempts; the directory is Git-ignored. Keep it intact for provenance. UI preview templates are not real run evidence. The verification script uses temporary test storage instead.

Current measured evidence in the workspace is `runs/full-50-v0.8.2`. In the synchronized review package, its portable copy is `evidence/full-50`; original path mappings are in `evidence/ORIGINAL_PATHS.json`. The already exported [CSV](../../verification/full-50-cases-v0.8.2.csv), [evaluation](../../verification/full-50-evaluation-v0.8.2.json) and [source map](../../verification/full-50-source-map-v0.8.2.json) can be opened without any model call.

All 50 human assessments remain pending. Further case execution, scoring and repair are deferred. This runbook does not execute the complete generation dataset as part of installation or demonstration.

### Optional later saved-run recheck

Only when that deferred work is resumed, the evaluator can read preserved evidence without inference:

```bash
"$CHENGXU_PY" scripts/evaluate_cases.py --batch evidence/full-50 --output /tmp/chengxu-saved-evaluation.json
```

Use the workspace batch path instead when not inside a package. This is a retrospective check under the executing source version; it may create a blank rating template if absent. Never treat missing ratings as pass. Exporting with `scripts/export_submission.py --batch <batch>` writes CSV/provenance but does not fix weak messages. Preserve existing exports when rerunning tools.

Any future full generation uses explicit `scripts/generate_cases.py --execute` and new batch IDs under a recorded version; it is intentionally not part of this demonstration checklist. The [test design](../../test-design.md), [acceptance rules](../../acceptance-criteria.md) and [evaluation report](../../evaluation-report.md) describe the deferred quality workflow.

## 7. Troubleshooting

| Symptom | Check / action |
| --- | --- |
| Browser cannot connect | Check Streamlit health, correct terminal/root and port 8501; start the server if absent |
| Ollama tags request fails | Start/reuse the local Ollama service on port 11434; a health failure is not a model-output verdict |
| `OLLAMA_MODEL_MISSING` | Match the configured tag to installed models; complete the pinned import only if needed |
| UI shows remote mode or missing key | Confirm `.env` exists and `LLM_PROVIDER=ollama`; inspect public config and overriding environment variables |
| Configuration error before submission | Fix local endpoint/model/value format; no service result is created by that UI error path |
| `needs_clarification` or `blocked` | Read the notice; correct missing facts or respect contact constraints rather than force generation |
| `invalid_input` after advanced edit | Use a whole request with matching scenario, valid references and no extra fields; select the advanced checkbox |
| Old cards remain after edits | Cards belong to the last submitted request; explicitly resubmit only if a new run is intended |
| `generation_failed` | Inspect safe codes/attempts; there is no automatic template/provider fallback |
| `REQUEST_IN_PROGRESS` in scripts | Preserve the pending record; an intentional new run needs a new request/batch ID |

The simple form's history box is one client-message block, event times are fixed and care controls are limited; advanced JSON exposes the full contract. Legacy help/care captions do not define backend capabilities. No model-quality pass rate, completed human evaluation, visual browser review, hosted demo or native download test is implied by a successful local health/UI check.

## 8. Rebuild a private review package

The synchronized documentation/UI package has a distinct name, `CHENGXU-review-draft-v0.8.2-docs-20261105.zip`, preserving earlier archives. To make another copy, use a new unused name:

```bash
"$CHENGXU_PY" scripts/build_review_package.py --name CHENGXU-review-local-copy
```

The builder copies allowlisted source/docs and selected saved evidence, checks relative links, source/evidence bytes, original frozen files and sensitive-file patterns, then writes a ZIP plus SHA-256 sidecar. It does not call a provider, score cases, upload or send anything. Existing ZIPs are never overwritten. A source/evidence hash manifest is included in `PACKAGE_MANIFEST.json`; its self-hash is explicitly omitted. The source path map preserves original case identities in portable locations.

For a staged workflow, use `--stage-only` first and `--finalize` with the same name after logging/document reconciliation. Use `--refresh-stage` to resynchronize and recheck a marked staging directory without creating the ZIP. Finalization is allowed only for this builder's marked staging directory. A newly unpacked package can use its portable evidence map rather than needing the original workspace's `runs/` paths. A successful package check certifies packaging consistency, not human quality acceptance.

## Current strict-target run — v0.9.7

Use local Ollama qwen3:4b with `LLM_TEMPERATURE=0`; restart Streamlit after source changes. Local generation is reference-bound editing, with all program/model contributions retained. [Current outputs, scores and authorship](../../verification/ai-quality-review-v0.9.7/REPORT.md). Run `python scripts/verify_quality_run.py --version v0.9.7` to verify saved evidence without inference. Use `--strict-all` with `scripts/evaluate_cases.py` for the user-required 50/50 human gate; omitted ratings remain pending. Previous commands referencing v0.8.2 reproduce historical evidence only.
