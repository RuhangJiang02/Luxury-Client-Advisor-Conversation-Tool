# Local Model Mode — No Paid API Required

Setup originally recorded at **tool-v0.3.3**; current measured implementation is **tool-v0.8.2**. Provider: **local Ollama**. Initial model: **qwen3:4b**.

The user requested an alternative to paid OpenAI API credits. Local inference preserves the Streamlit UI, shared generation service, io-v0.1 contracts, run storage, 50-case inputs, evaluation rubric, and export workflow. Genuine model outputs count as model runs; template previews remain excluded.

## 1. Runtime choice

The inspected Mac is Apple Silicon with 24 GiB RAM. Qwen3 4B is an initial small-model choice to validate local generation; its Ollama model page lists a roughly 2.5 GB Q4_K_M download. Actual runtime memory, speed, and language quality must be measured on this machine. [Official model page](https://ollama.com/library/qwen3:4b).

Ollama is installed locally and serves only the loopback address. Model download requires internet access, but generation uses the installed model rather than an external paid service. Local hardware, storage, and electricity are still used. No claim of cloud-model-equivalent quality is made.

## 2. Start and configure

Install/start Ollama and download the model if not already present:

```bash
brew install --cask ollama
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 ollama serve
```

In a separate terminal:

```bash
ollama pull qwen3:4b
```

In the recorded setup, the Ollama registry pull failed a redirect-address check under the current network. That protection was not disabled. The alternative official-source workflow downloads `Qwen/Qwen3-4B-GGUF` at revision `bc640142c66e1fdd12af0bd68f40445458f3869b` from Hugging Face into `.models/Qwen3-4B-Q4_K_M.gguf`, verifies size **2497280256 bytes** and SHA-256 **7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5**, then imports it:

```bash
ollama create qwen3:4b -f models/Modelfile
```

The weights are ignored by Git; the small Modelfile is reproducible source. Importing the same fixed GGUF does not require a paid account. [Official Qwen GGUF repository](https://huggingface.co/Qwen/Qwen3-4B-GGUF), [Ollama GGUF import guide](https://docs.ollama.com/import).

The current project `.env` is configured with:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://127.0.0.1:11434
LLM_TIMEOUT=180
LLM_MAX_ATTEMPTS=2
LLM_TEMPERATURE=0.7
```

An existing OpenAI key may remain privately in `.env`, but the local configuration deliberately sets the runtime key to empty. The Ollama adapter sends no Authorization header and disables environment proxy use for loopback requests. No OpenAI request is made when `LLM_PROVIDER=ollama`.

Launch Streamlit with the normal command and choose **本地模型真实生成** in the sidebar. The separate **离线模板预览** mode still uses hand-written copy and does not contribute to the submission's 150 model outputs.

## 3. Adapter and provenance

The adapter calls native `POST /api/chat` with `stream=false`, `format=json`, and `think=false`. Runtime options set `num_ctx=16384`, `num_predict=1800`, and the configured temperature. Hidden thinking is not requested or recorded. Only final content and basic token/finish metadata are retained. Application-level JSON/cardinality/policy checks still apply. [Official chat API](https://docs.ollama.com/api/chat), [JSON output guide](https://docs.ollama.com/capabilities/structured-outputs).

Only loopback HTTP endpoints are accepted for local mode, and `:cloud` model tags are rejected. The server is started with cloud functionality disabled. Missing server/model responses are explicit failures, not triggers to call OpenAI or fall back to templates.

Public configuration and run identity include provider, model, endpoint, context length, generation token limit, thinking mode, temperature, and retry/time limits. Local model execution is recorded as `execution_kind=live`, meaning a real model call, not specifically a paid cloud call. Deterministic fake adapters retain `test_double` and cannot be exported as real output evidence.

Preserve Ollama version and model digest in the verification summary before reporting a final evaluated version; model tags alone can change upstream. Keep the downloaded model fixed for comparisons. Do not mix OpenAI and Ollama outputs into a single-version final acceptance claim.

## 4. Verification and evaluation commands

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/generate_cases.py --execute --limit 1
```

`--execute` means real model execution; in local mode it does not incur API charges. After a successful smoke run and inspection, run the frozen 50-case batch, evaluate saved results with human ratings, and export CSV using the same scripts described in [the run guide](running-and-evaluation.md).

The acceptance thresholds remain eval-v0.1. A successful local HTTP/JSON response is not proof of factual grounding, personalization, or appropriate brand tone. Small-model limitations must be reflected in the evaluation and defects report.

## Historical measurement status — v0.6.1

See [full evaluation report](evaluation-report.md): 58 tests pass and current guardrails match 20/20 with no model calls. Initial complete 50-case measurement generated 48 cases; one same-version recovery request for each failure produced the remaining two. Source-mapped view: 50 cases/150 messages, all pending human ratings. Known semantic defects remain. Local event drafts now combine real model bodies with source-derived logistics, preserving both. The historical setup/smoke evidence above is not the latest quality acceptance result.

## Latest source-bound revision

The v0.8.2 fresh run generated all 50 cases/150 drafts without extra recovery (51 within-run provider attempts). 76 tests pass and current 20/20 guardrails match with zero calls. Greeting, recommendation and invitation frames are source-bound with real model bodies; recommendation selection is the first preflight-eligible item, not model ranking. All 50 human ratings remain pending; care/price/context issues are open. See the current evaluation report and freeze. Earlier setup and measurements remain historical evidence.
