# Using ALCF Inference Service with E3SM Compass

The [ALCF Inference Service](https://docs.alcf.anl.gov/services/inference-endpoints/) speaks the standard OpenAI chat completions API and works out of the box with E3SM Compass using the `openai_compatible` backend.

## 1. Setup and Quickstart

### Step 1: Install dependencies and initialize local config

From the repository root:

```bash
make sync
make backend-env
```

### Step 2: Obtain an ALCF access token

You need an active [ALCF user account](https://accounts.alcf.anl.gov/). Download the official ALCF authentication helper, authenticate once in your browser via Globus, and print your access token:

```bash
curl -sO https://raw.githubusercontent.com/argonne-lcf/inference-endpoints/main/inference_auth_token.py
uv run --with globus-sdk python inference_auth_token.py authenticate
uv run --with globus-sdk python inference_auth_token.py get_access_token
```

> [!NOTE]
> ALCF Globus access tokens remain valid for 48 hours. When a token expires, run `get_access_token` again to refresh it from your local `~/.globus` cache without re-running browser login.

### Step 3: Configure `backend/.env`

Edit `backend/.env` and set the `openai_compatible` provider variables using the ALCF base URL, your chosen model, and the token from Step 2:

```env
INFERENCE_BACKEND=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1
OPENAI_COMPATIBLE_MODEL=openai/gpt-oss-120b
OPENAI_COMPATIBLE_API_KEY=<paste-your-alcf-access-token>
```

### Step 4: Start E3SM Compass

Start the backend API in one terminal:

```bash
make backend-start
```

Start the frontend UI in a second terminal:

```bash
make frontend-start
```

Open `http://localhost:5173` in your browser, or test the API directly:

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"How do I choose an E3SM compset?"}'
```

---

## 2. Local Verification Snapshot (2026-11-10)

The models hosted on the ALCF Inference Service evolve over time as new open-weight models are deployed. Refer to the [ALCF Inference Endpoints documentation](https://docs.alcf.anl.gov/services/inference-endpoints/) for the current list.

As of **2026-11-10**, the following models were listed on the primary ALCF vLLM endpoint (`https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1`):

- `openai/gpt-oss-120b`, `openai/gpt-oss-20b`
- `google/gemma-4-31B-it`, `google/gemma-4-26B-A4B-it`, `google/gemma-4-E4B-it`, `google/gemma-3-27b-it`
- `meta-llama/Llama-4-Scout-17B-16E-Instruct`, `meta-llama/Llama-4-Maverick-17B-128E-Instruct`, `meta-llama/Llama-3.3-70B-Instruct`, `meta-llama/Meta-Llama-3.1-405B-Instruct`, `meta-llama/Meta-Llama-3.1-70B-Instruct`, `meta-llama/Meta-Llama-3.1-8B-Instruct`, `meta-llama/Llama-3.2-90B-Vision-Instruct`
- `nvidia/nemotron-3-super-120b`
- `mistralai/Devstral-2-123B-Instruct-2512`, `mistralai/Mistral-Large-Instruct-2407`, `mistralai/Mixtral-8x22B-Instruct-v0.1`
- `arcee-ai/Trinity-Large-Thinking-W4A16`, `AstroMLab/AstroSage-70B-20251009`
- `argonne/AuroraGPT-DPO-UFB-0225`, `argonne/AuroraGPT-IT-v4-0125`, `argonne/AuroraGPT-KTO-UFB-0325`, `argonne/AuroraGPT-Tulu3-SFT-0125`

### Local E3SM Compass Query Results (2026-11-10)

Tested locally through `POST /query` on representative curated E3SM questions (*"How do I choose an E3SM compset?"* and *"How do I configure EAMxx YAML diagnostics output?"*):

| Model | Generation Mode | Citations Returned | End-to-End Latency | Notes |
| --- | --- | --- | --- | --- |
| `google/gemma-4-31B-it` | `llm` | 4 | 1.17s – 1.49s | Grounded E3SM answer with server citations preserved |
| `openai/gpt-oss-120b` | `llm` | 4 | 3.63s – 4.07s | Grounded E3SM answer with server citations preserved |
| `meta-llama/Llama-3.3-70B-Instruct` | `deterministic_fallback` | 4 | >15s (cold queue) | Model was not warm on an active node; cleanly fell back to deterministic response |
