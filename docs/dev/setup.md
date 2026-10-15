# Developer setup

This guide describes repository setup and validation commands for the current
prototype.

## Prerequisites

- Python 3.13.
- `uv` for the Python workspace.
- Node.js and npm for the frontend package.
- Docker Desktop only if using the optional local observability stack.

## Python workspace

The root `pyproject.toml` defines a `uv` workspace with `backend` and
`evaluation` members. Install Python dependencies from the repository root:

```bash
uv sync --all-packages --all-groups
```

Run the backend:

```bash
uv run --all-packages --directory backend uvicorn e3sm_ai_platform.api.app:app --reload
```

Run backend tests:

```bash
make backend-test
```

Run the deterministic integration evaluation against the packaged backend
adapter:

```bash
make evaluation-test
```

The Makefile expands that target to:

```bash
E3SM_COMPASS_EVALUATOR=e3sm_ai_platform.evaluation:evaluate uv run --all-packages pytest evaluation
```

## Frontend package

Install frontend dependencies:

```bash
npm --prefix frontend ci
```

Start the Vite development server:

```bash
npm --prefix frontend run dev
```

Frontend validation targets are available through Make:

```bash
make frontend-test frontend-lint frontend-typecheck frontend-build
```

The package scripts are `test`, `lint`, `typecheck`, and `build`.

## Local configuration

Backend settings are read from environment variables and optional `backend/.env`.
Common local settings are:

- `CORS_ALLOW_ORIGINS`: comma-separated browser origins allowed by
  FastAPI CORS; defaults to `http://localhost:5173`.
- `INFERENCE_BACKEND`: `deterministic` by default; set to `openai_compatible`,
  `argo`, or `ollama` only when that provider's required settings below are present. A
  named provider with a blank required setting logs a startup warning and stays
  deterministic.
- `OPENAI_COMPATIBLE_API_KEY`, `OPENAI_COMPATIBLE_MODEL`,
  `OPENAI_COMPATIBLE_BASE_URL`: backend-only settings for any gateway speaking
  the OpenAI chat completions API (LivAI, GitHub Copilot, Azure OpenAI, vLLM).
  The key is a secret. There is no default base URL; the value is used verbatim,
  so include `/v1` only where the gateway expects it.
- `OPENAI_COMPATIBLE_TEMPERATURE`: defaults to `0.0`. Set it to `omit` to drop
  the field from requests entirely, which some reasoning models require because
  they reject any temperature value.
  Blank also uses `0.0`; it does not omit the field. If the provider explicitly
  rejects temperature, `/query` returns HTTP 503 with
  `detail.code=unsupported_temperature` instead of a deterministic fallback.
  Compass displays the configuration error. Set
  `OPENAI_COMPATIBLE_TEMPERATURE=omit` in `backend/.env` and restart the backend
  to stop sending the parameter. Detection happens on a provider request, not
  at startup; other provider failures still use the deterministic fallback.
- `ARGO_USER`, `ARGO_MODEL`, `ARGO_BASE_URL`, `ARGO_TEMPERATURE`: backend-only
  Argo (ANL) settings. `ARGO_USER` is an ANL username sent in the request body,
  not a secret; access depends on the ANL network. `ARGO_MODEL` is the
  gateway's `internal_id` (default `claudesonnet5`). `ARGO_TEMPERATURE` is
  omitted from requests when blank; some models reject it. `ARGO_API_KEY` is
  read as a fallback for `ARGO_USER` because existing ANL tooling exports it.
- `OTLP_ENDPOINT`, `SERVICE_NAME`, `DEPLOYMENT_ENVIRONMENT`, `OTLP_HEADERS`: optional
  backend observability settings.
- `RETRIEVAL_MODE`: `lexical` (default), `semantic`, or `hybrid`.
  Lexical mode is offline-safe and never loads an embedding model.
- `EMBEDDING_MODEL`: Hugging Face model used for semantic and hybrid
  retrieval; defaults to `BAAI/bge-small-en-v1.5`. Starting either mode may
  download the model and its dependencies on first use, so provision network
  access, cache storage, and suitable CPU or accelerator memory for the chosen
  model.
- `RETRIEVAL_SEMANTIC_MIN_SCORE`: dense cosine-similarity gate for
  semantic evidence; defaults to `0.7`. It is a model-calibration threshold,
  not a confidence percentage.
- `RETRIEVAL_LEXICAL_MIN_COVERAGE` and `RETRIEVAL_LEXICAL_MIN_SCORE`: lexical acceptance gates, defaulting
  to `0.18` and `0.11` respectively.
- `RETRIEVAL_LEXICAL_WEIGHT` and `RETRIEVAL_SEMANTIC_WEIGHT`: non-negative hybrid weights, each
  defaulting to `0.5`. Hybrid ranking uses their normalized weighted average of
  lexical relevance (clamped lexical score) and non-negative semantic cosine
  similarity. Set at least one weight above zero.

For example, enable semantic retrieval locally with:

```bash
RETRIEVAL_MODE=semantic \
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 \
RETRIEVAL_SEMANTIC_MIN_SCORE=0.7 \
uv run --all-packages --directory backend uvicorn e3sm_ai_platform.api.app:app --reload
```

Semantic and hybrid candidates still require official source authority and are
rejected for unsupported intents. They retain citations and produce the same
explicit insufficient-evidence response when no acceptable evidence is found.

Frontend local settings are documented in `frontend/.env.example`:

- `VITE_API_BASE_URL`: leave empty for local development through the Vite proxy.
- `VITE_DEV_API_PROXY_TARGET`: backend target for proxied `/query` calls;
  defaults to `http://localhost:8000`.

Do not expose backend secrets through `VITE_` variables.

## Local Ollama inference

Use native macOS Ollama on the 16 GB M2 MacBook Air for Apple GPU acceleration,
not Ollama inside Docker Desktop. Installation and model downloads are explicit
operator steps; the backend never downloads weights. No OpenAI-compatible or Argo credentials
are needed. Keep Ollama bound to loopback and disable its cloud features with
`OLLAMA_NO_CLOUD=1` in the Ollama server environment. Do not select cloud models
or sign the local server into cloud inference.

Before downloading or deploying, obtain institutional approval for the exact
provider, artifact provenance, origin, and license. Exclude Chinese-based models
and other institution-prohibited origins. Google Gemma and Meta Llama are only
candidates pending approval; both have custom licenses. Prefer permissive licenses
only among approved candidates.

After approval, install native Ollama and pull the initial Gemma 3 4B baseline:

```bash
ollama pull gemma3:4b
ollama show gemma3:4b
```

Verify the actual quantization is 4-bit and record the artifact digest and license;
a mutable tag does not establish artifact provenance. Create a local `Modelfile`
outside the repository with:

```text
FROM gemma3:4b
PARAMETER num_ctx 4096
```

Run `ollama create compass-gemma3:4b -f /path/to/Modelfile`. Ollama's
[OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility#setting-the-local-context-size)
cannot set `num_ctx` per request. The derived model sets the runtime context;
`OLLAMA_CONTEXT_TOKENS` sets the backend budget and must match that context.
A mismatch can cause silent server-side truncation rather than backend fallback.
Custom templates must fit the reserved 512 template tokens. Validate custom
tokenizers before use: the budget conservatively counts UTF-8 bytes as text
tokens for the baseline Gemma/Llama byte-fallback tokenizers, not arbitrary models.

Set these backend values in `backend/.env`, then restart the backend:

```bash
INFERENCE_BACKEND=ollama
OLLAMA_MODEL=compass-gemma3:4b
OLLAMA_BASE_URL=http://localhost:11434/v1/
OLLAMA_TIMEOUT_SECONDS=120
OLLAMA_CONTEXT_TOKENS=4096
OLLAMA_MAX_OUTPUT_TOKENS=512
```

The timeout must be finite, greater than zero, and at most 300 seconds. Context
must be between 1024 and 32768 tokens; output must be positive and leave more
than 512 tokens for instructions and input. Larger contexts increase memory use.
Invalid numeric limits or a blank model fail configuration loading, even when
another inference backend is selected; fix these values before restarting.
Prompts include the full question, instructions, and as many complete evidence
chunks as fit, in retrieval order. If no complete chunk fits, generation falls
back rather than silently truncating the question or evidence text.

Only HTTP(S) loopback endpoints are supported. Root URLs and `/v1/` URLs normalize
to one `/v1/chat/completions` endpoint. `localhost` maps to `127.0.0.1`; IPv4 and
IPv6 loopback literals are accepted. Remote hosts, embedded credentials, queries,
fragments, and other paths are rejected. Redirects and environment proxies are
disabled. Never expose unauthenticated Ollama publicly. OpenAI-compatible and Argo
endpoints still require HTTPS.

Run one backend worker and one Ollama generation slot (`OLLAMA_NUM_PARALLEL=1`
in the Ollama server environment). The backend allows one generation per process;
excess requests immediately fall back without queuing. Multiple workers or other
Ollama callers are outside this capacity bound. The deadline covers the provider
call, including model loading and response parsing, with SDK/agent retries disabled.
Answers cut off at the output limit also fall back rather than returning partial
claims. Timeout cancels the client request; it does not guarantee the server immediately
stops inference. Unavailable servers/models, invalid responses, empty output, busy
capacity, invalid endpoints, and context overflow return a cited deterministic
fallback. `/health` does not probe Ollama.

Rollback: set `INFERENCE_BACKEND=deterministic` and restart the backend. Installed
models may remain on disk without enabling inference.

### Opt-in laptop validation

After model approval, query `/query` with representative supported E3SM questions,
unsupported questions, and unavailable-model/server cases. Compare the Gemma
baseline with approved quantized `llama3.1:8b`, using a separate derived model
with the same `num_ctx 4096` and output budget. Record exact model/digest,
quantization, context/output limits, cold/warm latency, memory pressure, thermal
effects, claim-by-claim faithfulness to accepted evidence, and abstention behavior.
The project owner must set acceptable latency and quality thresholds before a
final recommendation. Do not use a 12B model as the laptop default. Citations and
prompt instructions do not prove generated claims are faithful.

Offline regression tests need no server or downloads:

```bash
uv run --all-packages pytest backend/tests/test_ollama.py backend/tests/test_openai_compatible.py backend/tests/test_argo.py backend/tests/test_observability.py
```

### Future private hosting

NERSC Spin deployment is not included. First obtain NERSC workload and resource
approval, then plan a private Ollama container with persistent model storage,
explicit CPU/memory limits, restricted networking, authentication boundaries,
and failure recovery. Do not assume Spin GPUs exist. Remote endpoint support
requires a separately designed and tested security policy; this adapter rejects
non-loopback hosts. Compass on Spin with approved, job-backed Perlmutter GPU
inference is a separate option requiring scheduling, endpoint-lifetime,
connectivity, and authentication design.

## Validation commands

Repository guidance requires Ruff and ty for Python validation:

```bash
uv run --all-packages ruff format backend evaluation
uv run --all-packages ruff check backend evaluation
uv run --all-packages ty check
```

The Makefile also provides ty type-check targets:

```bash
make backend-typecheck
make evaluation-typecheck
```

`make check` currently runs backend tests, backend Ruff lint, backend ty,
evaluation tests, evaluation Ruff lint, and evaluation ty. It does not run the
frontend checks.

Optional full pre-commit validation from repository guidance:

```bash
uv run --all-packages pre-commit run --all-files
```

## Observability stack

The local Docker Collector and Jaeger stack is optional and developer-only:

```bash
make observability-up
make observability-status
make observability-logs
make observability-down
```

Configuration details and telemetry payload rules are canonical in
[observability.md](observability.md).
