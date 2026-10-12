# E3SM Compass usage guide

E3SM Compass is a local prototype assistant for questions supported by a curated
E3SM documentation corpus. It answers from accepted curated evidence when
available, otherwise it returns an explicit insufficient-evidence response for
current web, live operational/tool, or unsupported requests.

## Start the backend

From the repository root:

```bash
uv sync --all-packages --all-groups
uv run --all-packages --directory backend uvicorn e3sm_ai_platform.api.app:app --reload
```

The backend starts the FastAPI application `e3sm_ai_platform.api.app:app`. Useful local
endpoints are:

- `GET http://localhost:8000/health`
- `POST http://localhost:8000/query`

Example direct query:

```bash
curl -s http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"How do I use E3SM-Unified?"}'
```

## Start the frontend

In another terminal from the repository root:

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

The Vite development server proxies relative `/query` calls to
`VITE_DEV_API_PROXY_TARGET`, defaulting to `http://localhost:8000`. Leave
`VITE_API_BASE_URL` empty for the local proxy. Set `VITE_API_BASE_URL` only when
the frontend must call a full backend URL directly; the backend CORS setting must
allow that origin.

## Query behavior

`POST /query` accepts:

```json
{
  "question": "How do I create an E3SM case?",
  "top_k": 4,
  "include_evidence": true
}
```

The response includes an answer, route, route alias, citations, evidence fields,
an `insufficient_evidence` flag, and debug metadata. Current route values are:

- `curated`: accepted curated documentation evidence supports the answer.
- `web`: the question appears to require current web information; no live web
  provider is configured in this prototype.
- `future_operational`: the question appears to require live operational,
  GitHub, SimBoard, scheduler, or tool data; only provider-independent
  interfaces exist today.
- `insufficient_evidence`: the curated corpus does not provide enough support or
  the request is unsupported.

Curated answers include citation provenance and avoid adding claims beyond the
accepted evidence. Non-curated routes return no accepted evidence or citations.

## Answer process

E3SM Compass uses retrieval-augmented generation (RAG) to:

1. Search the curated E3SM documentation corpus for relevant passages.
2. Rank top candidates with the configured retrieval mode. The default
   offline-safe `lexical` mode uses lexical similarity, query-term coverage,
   metadata matches, and E3SM-specific phrase boosts. Optional `semantic` mode
   uses Hugging Face embeddings, and `hybrid` mode deterministically combines
   lexical relevance with semantic similarity.
3. Filter candidates to official, sufficiently relevant, and mutually coherent
   evidence. Semantic matches must meet the configured semantic threshold;
   unsupported requests are rejected in every mode.
4. Pass accepted evidence to the deterministic generator or optional LLM before
   producing a cited answer. If no evidence passes the safeguards, return an
   explicit insufficient-evidence response.

Retrieval scores and semantic similarity values are relevance signals, not
confidence percentages. See [developer setup](../dev/setup.md) for retrieval
mode, model, weight, and threshold configuration.

## Optional LLM generation

Deterministic generation is the default. Two providers can be enabled for
answers that already have curated supporting evidence. Set `INFERENCE_BACKEND`
to exactly one of them in the backend environment only. Both are optional, and
either provider's errors fall back to deterministic, evidence-constrained output
without enabling live web retrieval.

### LivAI (LLNL)

```bash
INFERENCE_BACKEND=livai
LIVAI_API_KEY=your-secret-key
LIVAI_MODEL=gpt-5.5
LIVAI_BASE_URL=https://livai-api.llnl.gov/
```

Inject secrets through an untracked backend environment, `backend/.env`, or a
deployment secret manager. Do not use `VITE_` names for backend secrets and never
commit API keys.

### Argo (ANL)

```bash
INFERENCE_BACKEND=argo
ARGO_USER=your-anl-username
ARGO_MODEL=claudesonnet5
ARGO_BASE_URL=https://apps.inside.anl.gov/argoapi
```

Argo is reachable only from the Argonne network or VPN. It authenticates with an
ANL username sent in the request body rather than an API key, so `ARGO_USER` is
an identifier, not a secret. `ARGO_MODEL` takes the `internal_id` reported by the
gateway's `/api/v1/models/` endpoint (for example `claudesonnet5`, `gpt4o`,
`gemini25pro`), not the display name. Leave `ARGO_TEMPERATURE` blank unless the
selected model accepts it; Claude Sonnet 5 rejects the parameter.

If `INFERENCE_BACKEND` names a provider whose required setting is blank, the
backend logs a warning at startup and runs deterministic generation.

## Observability

The backend returns an `X-Request-ID` header and emits bounded request-completion
logs. For local OpenTelemetry Collector and Jaeger setup, see the canonical
[observability guide](../dev/observability.md).
